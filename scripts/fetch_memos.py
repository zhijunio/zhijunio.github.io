#!/usr/bin/env python3
"""从 Memos 拉公开说说，写成 public/data/memos.json。"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin

import requests

TZ_SH = timezone(timedelta(hours=8))
DEFAULT_BASE = "https://memos.zhijun.io"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def _iso(value: str) -> str:
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_SH).isoformat(timespec="seconds")


def _uid(memo: dict) -> str:
    uid = str(memo.get("uid") or "").strip()
    if uid:
        return uid
    name = str(memo.get("name") or "")
    return name.rsplit("/", 1)[-1].strip()


def _image_url(att: dict, base: str) -> str:
    mime = str(att.get("type") or "")
    filename = str(att.get("filename") or "").strip()
    if not mime.startswith("image/") and not re.search(
        r"\.(?:jpe?g|png|gif|webp|avif)$", filename, re.I
    ):
        return ""
    external = str(att.get("externalLink") or att.get("external_link") or "").strip()
    name = str(att.get("name") or "").strip().strip("/")
    if name and filename:
        parts = "/".join(quote(part) for part in name.split("/") if part)
        return urljoin(base.rstrip("/") + "/", f"file/{parts}/{quote(filename)}")
    return external


def _images(memo: dict, base: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for att in memo.get("attachments") or memo.get("resources") or []:
        if not isinstance(att, dict):
            continue
        url = _image_url(att, base)
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def _item(memo: dict, base: str) -> dict | None:
    vis = str(memo.get("visibility") or "").upper()
    state = str(memo.get("state") or memo.get("rowStatus") or "NORMAL").upper()
    if vis and vis != "PUBLIC":
        return None
    if state in {"ARCHIVED", "STATE_ARCHIVED"}:
        return None
    content = str(memo.get("content") or "").strip()
    images = _images(memo, base)
    if not content and not images:
        return None
    time_raw = (
        memo.get("displayTime") or memo.get("createTime") or memo.get("create_time")
    )
    if not time_raw:
        return None
    try:
        time_iso = _iso(str(time_raw))
    except ValueError:
        return None
    uid = _uid(memo)
    item: dict[str, Any] = {
        "type": "memo",
        "time": time_iso,
        "text": content,
    }
    if uid:
        item["url"] = urljoin(base.rstrip("/") + "/", f"memos/{uid}")
    tags = [str(t).strip() for t in (memo.get("tags") or []) if str(t).strip()]
    if tags:
        item["tags"] = tags
    if images:
        item["images"] = images
    return item


def _list_page(
    session: requests.Session, base: str, headers: dict, page_size: int
) -> list[dict]:
    rows: list[dict] = []
    page_token = ""
    while True:
        params = {
            "pageSize": str(page_size),
            "filter": 'visibility == "PUBLIC"',
        }
        if page_token:
            params["pageToken"] = page_token
        url = f"{base.rstrip('/')}/api/v1/memos"
        r = session.get(url, headers=headers, params=params, timeout=20)
        if r.status_code == 401:
            log.error("Memos 需要认证。设置 Secret MEMOS_TOKEN（Bearer PAT）")
            sys.exit(1)
        if not r.ok:
            log.error("List memos failed: HTTP %s", r.status_code)
            sys.exit(1)
        data = r.json() if r.content else {}
        memos = data.get("memos") or []
        for memo in memos:
            if isinstance(memo, dict):
                item = _item(memo, base)
                if item:
                    rows.append(item)
        page_token = str(data.get("nextPageToken") or "")
        log.info("page: %d so far, next=%s", len(rows), bool(page_token))
        if not page_token:
            break
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(root / "public" / "data" / "memos.json"))
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()

    base = os.environ.get("MEMOS_URL", DEFAULT_BASE).strip() or DEFAULT_BASE
    token = os.environ.get("MEMOS_TOKEN", "").strip()
    if not token:
        log.error("Set MEMOS_TOKEN")
        sys.exit(1)

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    session = requests.Session()
    rows = _list_page(session, base, headers, args.page_size)
    by_time: dict[str, dict] = {}
    for item in rows:
        key = f"{item['time']}|{item.get('url') or item.get('text','')[:40]}"
        by_time[key] = item
    out_rows = sorted(
        by_time.values(), key=lambda x: str(x.get("time")), reverse=True
    )
    out = Path(args.output)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(out_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log.info("Wrote %d memos -> %s", len(out_rows), out)


if __name__ == "__main__":
    main()

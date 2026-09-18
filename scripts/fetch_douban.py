#!/usr/bin/env python3
"""从豆瓣公开「看过 / 读过 / 听过」写成 public/data/douban.json。"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import requests

TZ_SH = timezone(timedelta(hours=8))
DEFAULT_USER = "266559066"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
STAR_WORDS = {"力荐": 5, "推荐": 4, "还行": 3, "较差": 2, "很差": 1}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def _title(raw: str) -> str:
    text = _clean(re.sub(r"<[^>]+>", "", raw))
    return text.split(" / ", 1)[0].strip()


def _time(day: str) -> str:
    return (
        datetime.strptime(day, "%Y-%m-%d")
        .replace(hour=12, tzinfo=TZ_SH)
        .isoformat(timespec="seconds")
    )


def _star_class(block: str) -> int | None:
    m = re.search(r"rating([1-5])-t", block)
    return int(m.group(1)) if m else None


def _get(session: requests.Session, url: str) -> str:
    r = session.get(url, timeout=20)
    if r.status_code == 403:
        raise RuntimeError(f"豆瓣拒绝访问 {url} HTTP 403")
    r.raise_for_status()
    return r.text


def _collect_items(page: str, kind: str) -> list[dict[str, Any]]:
    host = {"movie": "movie", "music": "music"}[kind]
    rows: list[dict[str, Any]] = []
    for block in page.split('class="item comment-item"')[1:]:
        link = re.search(
            rf'href="(https://{host}\.douban\.com/subject/\d+/)"', block
        )
        title = re.search(r"<em>(.*?)</em>", block, re.S)
        day = re.search(r'class="date">\s*(\d{4}-\d{2}-\d{2})', block)
        if not link or not title or not day:
            continue
        item: dict[str, Any] = {
            "type": kind,
            "time": _time(day.group(1)),
            "title": _title(title.group(1)),
            "url": link.group(1),
        }
        if kind == "music":
            intro = re.search(r'class="intro">(.*?)</li>', block, re.S)
            artist = _clean(intro.group(1)).split(" / ", 1)[0] if intro else ""
            if artist:
                item["artist"] = artist
        star = _star_class(block)
        if star:
            item["star"] = star
        comment = re.search(r'class="comment"[^>]*>(.*?)</span>', block, re.S)
        text = _clean(comment.group(1)) if comment else ""
        if text:
            item["text"] = text
        rows.append(item)
    return rows


def _movie_items(page: str) -> list[dict[str, Any]]:
    return _collect_items(page, "movie")


def _music_items(page: str) -> list[dict[str, Any]]:
    return _collect_items(page, "music")


def _book_items(page: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for block in page.split('class="subject-item"')[1:]:
        link = re.search(
            r'href="(https://book\.douban\.com/subject/\d+/)"[^>]*title="([^"]+)"',
            block,
        )
        day = re.search(r'class="date">\s*(\d{4}-\d{2}-\d{2})', block)
        if not link or not day:
            continue
        item: dict[str, Any] = {
            "type": "book",
            "time": _time(day.group(1)),
            "title": _clean(link.group(2)),
            "url": link.group(1),
        }
        star = _star_class(block)
        if star:
            item["star"] = star
        comment = re.search(
            r'class="comment[^"]*"[^>]*>(.*?)</p>', block, re.S
        )
        text = _clean(comment.group(1)) if comment else ""
        if text:
            item["text"] = text
        rows.append(item)
    return rows


def _rss_items(xml: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.S):
        title_el = re.search(r"<title>(.*?)</title>", block, re.S)
        link_el = re.search(r"<link>(.*?)</link>", block, re.S)
        date_el = re.search(r"<pubDate>(.*?)</pubDate>", block, re.S)
        if not title_el or not link_el or not date_el:
            continue
        raw = _clean(title_el.group(1))
        url = _clean(link_el.group(1))
        if raw.startswith("看过") and "movie.douban.com" in url:
            kind = "movie"
            title = raw[2:].strip()
        elif raw.startswith("读过") and "book.douban.com" in url:
            kind = "book"
            title = raw[2:].strip()
        elif raw.startswith("听过") and "music.douban.com" in url:
            kind = "music"
            title = raw[2:].strip()
        else:
            continue
        pub = parsedate_to_datetime(date_el.group(1).strip())
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        item: dict[str, Any] = {
            "type": kind,
            "time": pub.astimezone(TZ_SH).isoformat(timespec="seconds"),
            "title": title,
            "url": url,
        }
        desc = re.search(r"<description>(.*?)</description>", block, re.S)
        blob = html_lib.unescape(desc.group(1)) if desc else ""
        rec = re.search(r"推荐:\s*(\S+)", blob)
        if rec and rec.group(1) in STAR_WORDS:
            item["star"] = STAR_WORDS[rec.group(1)]
        note = re.search(r"备注:\s*(.+?)(?:</p>|$)", blob, re.S)
        text = _clean(note.group(1)) if note else ""
        if text:
            item["text"] = text
        rows.append(item)
    return rows


def _paged(
    session: requests.Session,
    user: str,
    host: str,
    parse,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = 0
    while True:
        url = (
            f"https://{host}/people/{user}/collect"
            f"?sort=time&start={start}&mode=grid&filter=all"
        )
        page = _get(session, url)
        batch = parse(page)
        if not batch:
            break
        rows.extend(batch)
        log.info("%s start=%s got %d (total %d)", host, start, len(batch), len(rows))
        if len(batch) < 15:
            break
        start += 15
        time.sleep(0.35)
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default=str(root / "public" / "data" / "douban.json")
    )
    args = parser.parse_args()
    user = os.environ.get("DOUBAN_USER", DEFAULT_USER).strip() or DEFAULT_USER

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": UA,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": f"https://www.douban.com/people/{user}/",
        }
    )

    by_url: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for host, parse in (
        ("movie.douban.com", _movie_items),
        ("book.douban.com", _book_items),
        ("music.douban.com", _music_items),
    ):
        try:
            for item in _paged(session, user, host, parse):
                by_url[item["url"]] = item
        except Exception as exc:
            errors.append(f"{host}: {exc}")
            log.warning("%s", errors[-1])

    try:
        rss = _get(
            session,
            f"https://www.douban.com/feed/people/{user}/interests",
        )
        for item in _rss_items(rss):
            by_url.setdefault(item["url"], item)
    except Exception as exc:
        errors.append(f"rss: {exc}")
        log.warning("RSS: %s", exc)

    rows = sorted(by_url.values(), key=lambda x: str(x.get("time")), reverse=True)
    if not rows:
        log.error("没有抓到豆瓣条目。%s", "；".join(errors) or "检查 DOUBAN_USER")
        sys.exit(1)

    out = Path(args.output)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    movies = sum(1 for x in rows if x["type"] == "movie")
    books = sum(1 for x in rows if x["type"] == "book")
    music = sum(1 for x in rows if x["type"] == "music")
    log.info(
        "Wrote %d items (movie %d, book %d, music %d) -> %s",
        len(rows),
        movies,
        books,
        music,
        out,
    )


if __name__ == "__main__":
    main()

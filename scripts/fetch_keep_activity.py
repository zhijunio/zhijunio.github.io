#!/usr/bin/env python3
"""从 Keep Open API 拉跑步记录，写成 public/data/keep.json。"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import requests

TZ_SH = timezone(timedelta(hours=8))
LOGIN_API = "https://api.gotokeep.com/v1.1/users/login"
RUN_DATA_API = (
    "https://api.gotokeep.com/pd/v3/stats/detail"
    "?dateUnit=all&type={sport_type}&lastDate={last_date}"
)
RUN_LOG_API = "https://api.gotokeep.com/pd/v3/{sport_type}log/{run_id}"
USER_AGENT = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) "
    "Gecko/20100101 Firefox/78.0"
)
SPORTS = ("outdoorRunning", "indoorRunning")
TITLES = {
    "outdoorRunning": "户外跑",
    "indoorRunning": "室内跑",
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def _n(val: Any) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _f(val: Any) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _km(val: float) -> float:
    return float(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _login(session: requests.Session, mobile: str, password: str):
    log.info("Logging in to Keep API...")
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    r = session.post(
        LOGIN_API,
        headers=headers,
        data={"mobile": mobile, "password": password},
        timeout=10,
    )
    if not r.ok:
        log.error("Login failed: HTTP %s", r.status_code)
        sys.exit(1)
    token = r.json().get("data", {}).get("token")
    if not token:
        log.error("No token in response")
        sys.exit(1)
    headers["Authorization"] = f"Bearer {token}"
    log.info("Login OK")
    return headers


def _get(session: requests.Session, url: str, headers: dict) -> requests.Response:
    for attempt in range(3):
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code == 429:
            wait = 2**attempt
            log.warning("Rate limited, retry in %ss", wait)
            time.sleep(wait)
            continue
        return r
    return r


def _hr(stats: dict, detail: dict | None = None) -> int:
    for src in (stats, detail or {}):
        heart = src.get("heartRate")
        if isinstance(heart, dict):
            value = _n(heart.get("averageHeartRate"))
            if value > 0:
                return value
        value = _n(src.get("averageHeartRate"))
        if value > 0:
            return value
    return 0


def _place(stats: dict, detail: dict | None = None) -> str:
    """Keep 详情里 region 常为字符串，见 running_page keep_sync.location_country。"""
    for src in (detail, stats):
        if not src:
            continue
        region = src.get("region")
        if isinstance(region, str) and region.strip():
            return region.strip()
        if isinstance(region, dict):
            text = "".join(
                str(region.get(key) or "").strip()
                for key in ("province", "city", "district")
            )
            if text:
                return text
            for key in ("name", "address", "desc"):
                value = str(region.get(key) or "").strip()
                if value:
                    return value
        for key in ("location", "city", "regionName"):
            value = src.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _item_from_stats(stats: dict, detail: dict | None = None) -> dict | None:
    if stats.get("isDoubtful") or not stats.get("id"):
        return None
    start_ms = _n(stats.get("startTime"))
    if start_ms <= 0:
        return None
    raw_m = _f(stats.get("accurateDistance")) or _f(stats.get("distance"))
    km = _f(stats.get("kmDistance")) or (raw_m / 1000.0 if raw_m > 0 else 0.0)
    dur_s = _n(stats.get("duration"))
    if km <= 0 and dur_s <= 0:
        return None
    data_type = str(stats.get("dataType") or "outdoorRunning")
    if data_type not in TITLES:
        return None
    time_iso = (
        datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        .astimezone(TZ_SH)
        .isoformat(timespec="seconds")
    )
    item: dict[str, Any] = {
        "type": "run",
        "time": time_iso,
        "title": TITLES[data_type],
    }
    if km > 0:
        item["km"] = _km(km)
    if dur_s > 0:
        item["minutes"] = round(dur_s / 60)
    hr = _hr(stats, detail)
    if hr > 0:
        item["hr"] = hr
    place = _place(stats, detail)
    if place:
        item["place"] = place
    return item


def _detail(
    session: requests.Session, headers: dict, sport: str, run_id: str
) -> dict | None:
    r = _get(session, RUN_LOG_API.format(sport_type=sport, run_id=run_id), headers)
    if not r.ok:
        return None
    data = r.json().get("data")
    return data if isinstance(data, dict) else None


def _complete(item: dict) -> bool:
    if item.get("title") == "室内跑":
        return bool(item.get("hr"))
    return bool(item.get("hr") and item.get("place"))


def _fetch_sport(
    session: requests.Session,
    headers: dict,
    sport: str,
    existing: dict[str, dict],
    full: bool,
    limit: int | None,
) -> list[dict]:
    rows: list[dict] = []
    last_date = 0
    while True:
        r = _get(
            session,
            RUN_DATA_API.format(sport_type=sport, last_date=last_date),
            headers,
        )
        if not r.ok:
            log.warning("%s page failed HTTP %s", sport, r.status_code)
            break
        data = r.json().get("data") or {}
        stop = False
        for group in data.get("records") or []:
            for entry in group.get("logs") or []:
                if not isinstance(entry, dict):
                    continue
                stats = entry.get("stats")
                if not isinstance(stats, dict):
                    continue
                prev = None
                start_ms = _n(stats.get("startTime"))
                if start_ms > 0:
                    key = (
                        datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
                        .astimezone(TZ_SH)
                        .isoformat(timespec="seconds")
                    )
                    prev = existing.get(key)
                if not full and prev and _complete(prev):
                    stop = True
                    break
                detail = None
                if full or not prev or not _complete(prev):
                    run_id = str(stats.get("id") or "")
                    if run_id:
                        detail = _detail(session, headers, sport, run_id)
                        time.sleep(0.25)
                item = _item_from_stats(stats, detail)
                if item is None:
                    continue
                if prev and not item.get("hr") and prev.get("hr"):
                    item["hr"] = prev["hr"]
                if prev and not item.get("place") and prev.get("place"):
                    item["place"] = prev["place"]
                rows.append(item)
                if limit and len(rows) >= limit:
                    return rows
            if stop:
                break
        if stop or not data.get("lastTimestamp"):
            break
        last_date = data.get("lastTimestamp")
        time.sleep(1)
    log.info("%s: %d rows", sport, len(rows))
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(root / "public" / "data" / "keep.json"),
        help="absolute or repo-relative path",
    )
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    mobile = os.environ.get("KEEP_MOBILE", "").strip()
    password = os.environ.get("KEEP_PASSWORD", "").strip()
    if not mobile or not password:
        log.error("Set KEEP_MOBILE and KEEP_PASSWORD")
        sys.exit(1)

    out = Path(args.output)
    if not out.is_absolute():
        out = root / out
    existing_list: list[dict] = []
    if out.exists() and not args.full:
        try:
            loaded = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            loaded = []
        if isinstance(loaded, list):
            existing_list = [
                x
                for x in loaded
                if isinstance(x, dict) and x.get("title") in TITLES.values()
            ]
    existing = {
        str(item.get("time")): item for item in existing_list if item.get("time")
    }

    session = requests.Session()
    headers = _login(session, mobile, password)
    cap = args.limit or None
    fresh: list[dict] = []
    for sport in SPORTS:
        left = None if cap is None else max(0, cap - len(fresh))
        if cap is not None and left == 0:
            break
        fresh.extend(_fetch_sport(session, headers, sport, existing, args.full, left))

    fetched_times = {str(item.get("time")) for item in fresh}
    merged = (
        fresh
        if args.full
        else fresh + [item for key, item in existing.items() if key not in fetched_times]
    )
    by_time: dict[str, dict] = {}
    for item in merged:
        key = str(item.get("time") or "")
        if key and key not in by_time:
            by_time[key] = item
    rows = sorted(by_time.values(), key=lambda x: str(x.get("time")), reverse=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log.info("Wrote %d rows (%d fetched) -> %s", len(rows), len(fresh), out)


if __name__ == "__main__":
    main()

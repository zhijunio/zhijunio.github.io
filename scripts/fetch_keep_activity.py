#!/usr/bin/env python3
"""从 Keep Open API 拉跑步记录，写成 public/data/keep.json。

列表、详情与 running_page keep_sync 一致：type=running，runninglog/{id}。
地点取详情 region。跑力、心率区间、负荷本地计算，不拉轨迹。
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterator

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
LIST_SPORTS = ("running", "outdoorRunning", "indoorRunning")
TITLES = {
    "outdoorRunning": "户外跑",
    "indoorRunning": "室内跑",
}
HR_ZONE_THRESHOLDS = ((60, 1), (70, 2), (80, 3), (90, 4), (100, 5))
MAX_HR = int(os.environ.get("MAX_HR", "180"))
PAGE_PAUSE = 1.0
DETAIL_PAUSE = 0.2
# 增量同步每次最多补这么多缺地点的旧记录，避免把 Actions 拖满。
BACKFILL = 40

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


def _time_key(start_ms: int) -> str:
    return (
        datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        .astimezone(TZ_SH)
        .isoformat(timespec="seconds")
    )


def _login(session: requests.Session, mobile: str, password: str) -> dict:
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


def _positive_hr(value: Any) -> int:
    n = _n(value)
    return n if n > 0 else 0


def _hr(stats: dict, detail: dict | None = None) -> int:
    for src in (detail or {}, stats):
        heart = src.get("heartRate")
        if isinstance(heart, dict):
            value = _positive_hr(heart.get("averageHeartRate"))
            if value:
                return value
        value = _positive_hr(src.get("averageHeartRate"))
        if value:
            return value
    return 0


def _pace_seconds(km: float, dur_s: int, stats: dict) -> int:
    pace = _n(stats.get("averagePace"))
    if pace > 0:
        return pace
    if km <= 0 or dur_s <= 0:
        return 0
    return round(dur_s / km)


def _vdot(dist_m: float, dur_s: int) -> float:
    if dur_s <= 0 or dist_m <= 0:
        return 0.0
    dur_min = dur_s / 60
    vpm = dist_m / dur_min
    if vpm <= 0:
        return 0.0
    vo2 = -4.60 + 0.182258 * vpm + 0.000104 * vpm**2
    pct = (
        0.8
        + 0.1894393 * math.exp(-0.012778 * dur_min)
        + 0.2989558 * math.exp(-0.1932605 * dur_min)
    )
    if pct <= 0 or pct > 1:
        return 0.0
    vdot = vo2 / pct
    if not 20 <= vdot <= 85:
        return 0.0
    return float(Decimal(str(vdot)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def _zone(avg_hr: int) -> int:
    if avg_hr <= 0 or MAX_HR <= 0:
        return 0
    pct = avg_hr / MAX_HR * 100
    for thresh, zone in HR_ZONE_THRESHOLDS:
        if pct <= thresh:
            return zone
    return 5


def _load(stats: dict, dur_s: int) -> int:
    score = _n(stats.get("trainingLoadScore"))
    if score > 0:
        return score
    if dur_s <= 0:
        return 0
    return round(dur_s / 3600 * 100)


def _place(stats: dict, detail: dict | None = None) -> str:
    for src in (detail, stats):
        if not src:
            continue
        region = src.get("region")
        if isinstance(region, str) and region.strip():
            return region.strip()
        if isinstance(region, dict):
            address = str(region.get("address") or "").strip()
            if address:
                return address
            parts: list[str] = []
            for key in (
                "province",
                "city",
                "district",
                "county",
                "township",
                "town",
                "street",
                "road",
                "streetNumber",
                "village",
                "poiName",
                "name",
            ):
                value = str(region.get(key) or "").strip()
                if value and value not in parts:
                    parts.append(value)
            if parts:
                return "".join(parts)
        for key in ("location", "city", "regionName", "address"):
            value = src.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _item_from_stats(stats: dict, detail: dict | None = None) -> dict | None:
    if stats.get("isDoubtful") or not stats.get("id"):
        return None
    start_ms = _n(stats.get("startTime")) or _n((detail or {}).get("startTime"))
    if start_ms <= 0:
        return None
    src = detail or {}
    raw_m = (
        _f(src.get("accurateDistance"))
        or _f(src.get("distance"))
        or _f(stats.get("accurateDistance"))
        or _f(stats.get("distance"))
    )
    km = (
        _f(src.get("kmDistance"))
        or _f(stats.get("kmDistance"))
        or (raw_m / 1000.0 if raw_m > 0 else 0.0)
    )
    dur_s = (
        _n(src.get("movingDuration"))
        or _n(src.get("duration"))
        or _n(stats.get("duration"))
    )
    if km <= 0 and dur_s <= 0:
        return None
    data_type = str(src.get("dataType") or stats.get("dataType") or "outdoorRunning")
    if data_type not in TITLES:
        return None
    item: dict[str, Any] = {
        "type": "run",
        "time": _time_key(start_ms),
        "title": TITLES[data_type],
    }
    run_id = str(stats.get("id") or src.get("id") or "")
    if run_id:
        item["id"] = run_id
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
    pace_src = src if src.get("averagePace") else stats
    pace = _pace_seconds(km, dur_s, pace_src)
    if pace > 0:
        item["pace"] = pace
    vdot = _vdot(raw_m, dur_s)
    if vdot > 0:
        item["vdot"] = vdot
    zone = _zone(hr)
    if zone > 0:
        item["zone"] = zone
    load_src = src if src.get("trainingLoadScore") else stats
    load = _load(load_src, dur_s)
    if load > 0:
        item["load"] = load
    return item


def _reuse(item: dict, prev: dict | None) -> dict:
    if not prev:
        return item
    if not item.get("place") and prev.get("place"):
        item["place"] = prev["place"]
    if not item.get("hr") and prev.get("hr"):
        item["hr"] = prev["hr"]
        if not item.get("zone"):
            item["zone"] = prev.get("zone") or _zone(_n(item["hr"]))
    if not item.get("id") and prev.get("id"):
        item["id"] = prev["id"]
    return item


def _needs_detail(item: dict | None) -> bool:
    if item is None:
        return True
    if item.get("title") == "室内跑":
        return not item.get("hr")
    return not item.get("place")


class LogApi:
    kind = "running"


def _detail(
    session: requests.Session, headers: dict, run_id: str, sport: str
) -> dict | None:
    for kind in (LogApi.kind, "running", sport):
        if not kind:
            continue
        r = _get(
            session,
            RUN_LOG_API.format(sport_type=kind, run_id=run_id),
            headers,
        )
        if not r.ok:
            log.warning("GET failed HTTP %s %s", r.status_code, url.split("?", 1)[0])
            continue
        data = r.json().get("data")
        if isinstance(data, dict):
            LogApi.kind = kind
            return data
    return None


def _derived(item: dict) -> dict:
    km = _f(item.get("km"))
    minutes = _n(item.get("minutes"))
    hr = _n(item.get("hr"))
    dur_s = minutes * 60
    if not item.get("pace"):
        pace = _pace_seconds(km, dur_s, {})
        if pace > 0:
            item["pace"] = pace
    if not item.get("vdot"):
        vdot = _vdot(km * 1000, dur_s)
        if vdot > 0:
            item["vdot"] = vdot
    if hr > 0 and not item.get("zone"):
        zone = _zone(hr)
        if zone > 0:
            item["zone"] = zone
    if not item.get("load") and dur_s > 0:
        item["load"] = _load({}, dur_s)
    return item


def _iter_stats(
    session: requests.Session, headers: dict, sport: str
) -> Iterator[dict]:
    last_date = 0
    pages = 0
    while True:
        r = _get(
            session,
            RUN_DATA_API.format(sport_type=sport, last_date=last_date),
            headers,
        )
        if not r.ok:
            log.warning("%s page failed HTTP %s", sport, r.status_code)
            return
        data = r.json().get("data") or {}
        pages += 1
        count = 0
        for group in data.get("records") or []:
            for entry in group.get("logs") or []:
                if not isinstance(entry, dict):
                    continue
                stats = entry.get("stats")
                if isinstance(stats, dict):
                    count += 1
                    yield stats
        last_date = data.get("lastTimestamp") or 0
        log.info("%s page %d: %d logs", sport, pages, count)
        if not last_date:
            return
        time.sleep(PAGE_PAUSE)


def _fill_detail(
    session: requests.Session,
    headers: dict,
    stats: dict,
    item: dict | None,
    sport: str,
    details: list[int],
) -> dict | None:
    run_id = str(stats.get("id") or "")
    if not run_id:
        return item
    if details[0]:
        time.sleep(DETAIL_PAUSE)
    details[0] += 1
    n = details[0]
    if n == 1 or n % 10 == 0:
        log.info("detail %d  …%s", n, run_id[-16:])
    detail = _detail(session, headers, run_id, sport)
    if detail is None:
        log.warning("detail empty  …%s", run_id[-16:])
    return _item_from_stats(stats, detail) or item


def _fetch_sport(
    session: requests.Session,
    headers: dict,
    sport: str,
    existing: dict[str, dict],
    full: bool,
    limit: int | None,
) -> tuple[list[dict], int]:
    rows: list[dict] = []
    details = [0]
    seen = 0
    kept = 0
    skipped = 0
    backfill = 0 if full else BACKFILL
    log.info(
        "%s: start (%s, existing=%d%s)",
        sport,
        "full" if full else "incremental",
        len(existing),
        f", limit={limit}" if limit else "",
    )
    for stats in _iter_stats(session, headers, sport):
        seen += 1
        start_ms = _n(stats.get("startTime"))
        key = _time_key(start_ms) if start_ms > 0 else ""
        prev = existing.get(key) if key else None
        item = _item_from_stats(stats, None)
        if item is None:
            skipped += 1
            continue
        item = _reuse(item, prev)
        if not full and prev:
            if backfill > 0 and _needs_detail(item):
                filled = _fill_detail(session, headers, stats, item, sport, details)
                if filled:
                    rows.append(_reuse(filled, prev))
                    backfill -= 1
                    kept += 1
                    log.info(
                        "backfill %d/%d  %s  %s",
                        BACKFILL - backfill,
                        BACKFILL,
                        filled.get("time"),
                        filled.get("place") or "(no place)",
                    )
                if limit and len(rows) >= limit:
                    log.info("%s: hit limit %d", sport, limit)
                    break
                continue
            log.info("%s: incremental stop at %s", sport, key or "?")
            break
        if _needs_detail(item):
            filled = _fill_detail(session, headers, stats, item, sport, details)
            item = _reuse(filled, prev) if filled else item
        rows.append(item)
        kept += 1
        if kept == 1 or kept % 20 == 0:
            log.info(
                "%s: kept %d  latest %s  %s %.2fkm",
                sport,
                kept,
                item.get("time"),
                item.get("title"),
                _f(item.get("km")),
            )
        if limit and len(rows) >= limit:
            log.info("%s: hit limit %d", sport, limit)
            break
    log.info(
        "%s: done  logs=%d kept=%d skip=%d details=%d",
        sport,
        seen,
        len(rows),
        skipped,
        details[0],
    )
    return rows, seen


def _load_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not isinstance(loaded, list):
        return []
    return [x for x in loaded if isinstance(x, dict) and x.get("type") == "run"]


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
    existing_list = _load_existing(out)
    existing = {
        str(item.get("time")): item for item in existing_list if item.get("time")
    }
    log.info(
        "sync %s  existing=%d  output=%s%s",
        "full" if args.full else "incremental",
        len(existing),
        out,
        f"  limit={args.limit}" if args.limit else "",
    )

    session = requests.Session()
    headers = _login(session, mobile, password)
    cap = args.limit or None
    fresh: list[dict] = []
    listed = False
    for sport in LIST_SPORTS:
        left = None if cap is None else max(0, cap - len(fresh))
        if cap is not None and left == 0:
            log.info("limit reached, skip remaining lists")
            break
        if listed:
            log.info("skip %s, already listed", sport)
            break
        log.info("list %s", sport)
        batch, seen = _fetch_sport(
            session, headers, sport, existing, args.full, left
        )
        if seen:
            listed = True
        elif sport != LIST_SPORTS[-1]:
            log.info("%s empty, try next list", sport)
        fresh.extend(batch)

    fetched_times = {str(item.get("time")) for item in fresh}
    merged = fresh + [
        item for key, item in existing.items() if key not in fetched_times
    ]
    by_time: dict[str, dict] = {}
    for item in merged:
        key = str(item.get("time") or "")
        if key and key not in by_time:
            by_time[key] = item
    rows = [
        _derived(item)
        for item in sorted(by_time.values(), key=lambda x: str(x.get("time")), reverse=True)
    ]
    with_place = sum(1 for item in rows if item.get("place"))
    log.info("merge %d rows (%d with place, %d fetched)", len(rows), with_place, len(fresh))
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    if out.exists() and out.read_text(encoding="utf-8") == text:
        log.info("Unchanged %d rows", len(rows))
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    log.info("Wrote %d rows (%d fetched) -> %s", len(rows), len(fresh), out)


if __name__ == "__main__":
    main()

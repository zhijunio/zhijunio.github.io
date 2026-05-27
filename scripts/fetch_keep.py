"""
从 Keep 拉取运动记录，写入 scripts/assets/keep_activities.json、keep_stats.json。

凭证：KEEP_TOKEN 或 KEEP_MOBILE + KEEP_PASSWORD
可选：KEEP_SYNC_TYPES、SYNC_LIMIT、AI_ENABLED、AI_PROVIDER / OpenAI / CF
依赖：requests；轨迹可选 pycryptodome、polyline
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import zlib
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from activity_sync_common import (  # noqa: E402
    SyncPaths,
    apply_ai_to_record,
    assets_path,
    build_activity_record,
    cap_sync_batch,
    create_sync_http_session,
    cutoff_timestamp,
    debug,
    err,
    finalize_sync,
    info,
    item,
    known_run_ids,
    load_activities,
    log_sync_startup,
    merge_records,
    ok,
    parse_positive_int,
    parse_time,
    request_with_retries,
    section,
    set_log_scope,
    warn,
)

try:
    from Crypto.Cipher import AES

    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False

try:
    import polyline as polyline_lib

    _HAS_POLYLINE = True
except ImportError:
    _HAS_POLYLINE = False

PATHS = SyncPaths(
    activities=assets_path("keep_activities.json"),
    stats=assets_path("keep_stats.json"),
)

KEEP_MOBILE = os.getenv("KEEP_MOBILE")
KEEP_PASSWORD = os.getenv("KEEP_PASSWORD")
KEEP_TOKEN = os.getenv("KEEP_TOKEN")
KEEP_SYNC_TYPES = [
    t.strip()
    for t in (os.getenv("KEEP_SYNC_TYPES") or "running").split(",")
    if t.strip()
]
SYNC_LIMIT = parse_positive_int(os.getenv("SYNC_LIMIT"))
VALID_SPORT_TYPES = frozenset({"running", "cycling", "hiking"})

KEEP2STRAVA = {
    "outdoorWalking": "Walk",
    "outdoorRunning": "Run",
    "outdoorCycling": "Ride",
    "indoorRunning": "VirtualRun",
    "mountaineering": "Hiking",
}

KEEP_TYPE_CN = {
    "outdoorWalking": "户外步行",
    "outdoorRunning": "户外跑步",
    "outdoorCycling": "户外骑行",
    "indoorRunning": "室内跑步",
    "mountaineering": "登山",
}

KEEP_TZ = ZoneInfo("Asia/Shanghai")
LOGIN_API = "https://api.gotokeep.com/v1.1/users/login"
RUN_DATA_API = (
    "https://api.gotokeep.com/pd/v3/stats/detail?dateUnit=all&type={sport_type}&lastDate={last_date}"
)
RUN_LOG_API = "https://api.gotokeep.com/pd/v3/{sport_type}log/{run_id}"
AES_KEY = base64.b64decode("NTZmZTU5OzgyZzpkODczYw==")
AES_IV = base64.b64decode("MjM0Njg5MjQzMjkyMDMwMA==")


def extract_keep_id(stats_id: str) -> str | None:
    if not stats_id:
        return None
    parts = stats_id.split("_")
    return parts[1] if len(parts) >= 2 else stats_id


def _is_new_keep_summary(
    stats: dict, known_ids: set[str], cutoff_ts: int
) -> bool:
    keep_id = extract_keep_id(stats.get("id") or "")
    if not keep_id or f"keep_{keep_id}" in known_ids:
        return False
    ts = keep_time_to_timestamp(stats.get("doneDate"))
    return ts is None or ts >= cutoff_ts


def build_keep_session() -> tuple[requests.Session, dict[str, str]]:
    if not KEEP_TOKEN and not (KEEP_MOBILE and KEEP_PASSWORD):
        raise RuntimeError("缺少凭证：KEEP_TOKEN 或 KEEP_MOBILE + KEEP_PASSWORD")

    session = create_sync_http_session("Keep")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }

    if KEEP_TOKEN:
        token = KEEP_TOKEN
        headers["Authorization"] = (
            token if token.startswith("Bearer ") else f"Bearer {token}"
        )
        info("使用 KEEP_TOKEN 认证")
        return session, headers

    info("手机号登录 Keep…")
    try:
        response = request_with_retries(
            session,
            "POST",
            LOGIN_API,
            headers=headers,
            data={"mobile": KEEP_MOBILE, "password": KEEP_PASSWORD},
            timeout=30,
        )
    except Exception as exc:
        raise RuntimeError(f"登录异常: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(f"登录失败: {response.text[:120]}")

    token = response.json().get("data", {}).get("token")
    if not token:
        raise RuntimeError("登录响应无 token")

    headers["Authorization"] = f"Bearer {token}"
    ok("登录成功")
    return session, headers


def get_keep_json(
    session: requests.Session,
    headers: dict[str, str],
    url: str,
    *,
    error_label: str,
    use_err: bool = False,
) -> dict | None:
    log_fail = err if use_err else warn
    try:
        response = request_with_retries(
            session,
            "GET",
            url,
            headers=headers,
            timeout=30,
        )
        if response.status_code != 200:
            log_fail(f"{error_label} HTTP {response.status_code}")
            return None
        return response.json()
    except Exception as exc:
        log_fail(f"{error_label}: {exc}")
        return None


def fetch_keep_run_detail(
    session: requests.Session,
    headers: dict[str, str],
    sport_type: str,
    stats_id: str,
) -> dict | None:
    keep_id = extract_keep_id(stats_id)
    if not keep_id:
        return None
    url = RUN_LOG_API.format(sport_type=sport_type, run_id=stats_id)
    return get_keep_json(session, headers, url, error_label=f"详情失败 {keep_id}")


def fetch_keep_stats_pages(
    session: requests.Session,
    headers: dict[str, str],
    sport_type: str,
    *,
    known_ids: set[str],
    cutoff_ts: int,
    max_pending: int | None,
) -> list[tuple[str, dict]]:
    last_date = 0
    collected: list[tuple[str, dict]] = []
    pages = 0

    def pending_count() -> int:
        return sum(
            1 for _, stats in collected if _is_new_keep_summary(stats, known_ids, cutoff_ts)
        )

    while True:
        url = RUN_DATA_API.format(sport_type=sport_type, last_date=last_date)
        debug(f"列表 {sport_type} lastDate={last_date}")
        payload_root = get_keep_json(
            session,
            headers,
            url,
            error_label=f"列表拉取失败 {sport_type}",
            use_err=True,
        )
        if payload_root is None:
            break

        payload = payload_root.get("data") or {}
        records = payload.get("records") or []
        if not records:
            break

        pages += 1
        for group in records:
            for entry in group.get("logs") or []:
                stats = entry.get("stats")
                if stats and not stats.get("isDoubtful"):
                    collected.append((sport_type, stats))

        last_date = payload.get("lastTimestamp") or 0
        if not last_date:
            break
        if max_pending and pending_count() >= max_pending:
            debug(f"{sport_type} 待同步已达 {max_pending}，停止翻页")
            break
        time.sleep(0.5)

    info(f"{sport_type} 摘要 {len(collected)} 条（{pages} 页）")
    return collected


def fetch_all_keep_summaries(
    session: requests.Session,
    headers: dict[str, str],
    local_data: list[dict],
    *,
    sync_limit: int | None = None,
) -> list[tuple[str, dict]]:
    known = known_run_ids(local_data)
    cutoff_ts = cutoff_timestamp(local_data)
    all_summaries: list[tuple[str, dict]] = []

    for sport_type in KEEP_SYNC_TYPES:
        if sport_type not in VALID_SPORT_TYPES:
            warn(f"忽略未知类型: {sport_type}")
            continue
        all_summaries.extend(
            fetch_keep_stats_pages(
                session,
                headers,
                sport_type,
                known_ids=known,
                cutoff_ts=cutoff_ts,
                max_pending=sync_limit,
            )
        )
    return all_summaries


def filter_keep_pending(
    local_data: list[dict],
    summaries: list[tuple[str, dict]],
) -> list[tuple[str, dict]]:
    known_ids = known_run_ids(local_data)
    cutoff_ts = cutoff_timestamp(local_data)
    summaries.sort(
        key=lambda pair: parse_time(keep_time_to_local_str(pair[1].get("doneDate")) or "")
    )
    return [
        (sport_type, stats)
        for sport_type, stats in summaries
        if _is_new_keep_summary(stats, known_ids, cutoff_ts)
    ]


def sync_keep_records(
    session: requests.Session,
    headers: dict[str, str],
    local_data: list[dict],
    summaries: list[tuple[str, dict]],
):
    pending = filter_keep_pending(local_data, summaries)
    pending = cap_sync_batch(
        pending,
        SYNC_LIMIT,
        env_name="SYNC_LIMIT",
        keep_newest_at_end=True,
    )
    history = list(local_data)
    formatted: list[dict] = []
    total = len(pending)

    for n, (sport_type, stats) in enumerate(pending, start=1):
        safe_time = keep_time_to_local_str(stats.get("doneDate"))
        keep_id = extract_keep_id(stats.get("id") or "")
        fallback = f"keep_{keep_id}" if keep_id else "?"
        item(n, total, f"{sport_type} {safe_time or fallback}")
        detail = fetch_keep_run_detail(session, headers, sport_type, stats.get("id") or "")
        record = format_keep_record(sport_type, stats, detail)
        if not record:
            continue
        llm_used = apply_ai_to_record(record, history)
        if llm_used:
            time.sleep(1)
        formatted.append(record)
        history.insert(0, record)
        time.sleep(0.3)

    return merge_records(local_data, formatted)


def decode_geo_polyline(geo_points_b64: str) -> list[tuple[float, float]]:
    if not geo_points_b64 or not _HAS_CRYPTO:
        return []
    try:
        raw = base64.b64decode(geo_points_b64)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        decrypted = cipher.decrypt(raw)
        decompressed = zlib.decompress(decrypted, 16 + zlib.MAX_WBITS)
        points = json.loads(decompressed)
        return [
            (float(p["latitude"]), float(p["longitude"]))
            for p in points
            if p.get("latitude") is not None and p.get("longitude") is not None
        ]
    except Exception as exc:
        debug(f"轨迹解码失败: {exc}")
        return []


def encode_summary_polyline(coords: list[tuple[float, float]]) -> str:
    if not coords or not _HAS_POLYLINE:
        return ""
    try:
        return polyline_lib.encode(coords)
    except Exception:
        return ""


def _as_keep_tz(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=KEEP_TZ)
    return dt.astimezone(KEEP_TZ)


def _parse_keep_datetime_from_str(text: str) -> datetime | None:
    if text.isdigit():
        return parse_keep_datetime(int(text))
    iso = text.replace("Z", "+00:00")
    try:
        return _as_keep_tz(datetime.fromisoformat(iso))
    except ValueError:
        pass
    try:
        return datetime.strptime(text[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=KEEP_TZ
        )
    except ValueError:
        return None


def parse_keep_datetime(value) -> datetime | None:
    if value is None or value == "" or value == 0:
        return None
    if isinstance(value, datetime):
        return _as_keep_tz(value)
    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 1e12:
            ts /= 1000
        return datetime.fromtimestamp(ts, tz=KEEP_TZ)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        return _parse_keep_datetime_from_str(text)
    return None


def keep_time_to_local_str(value) -> str:
    dt = parse_keep_datetime(value)
    return dt.astimezone(KEEP_TZ).strftime("%Y-%m-%dT%H:%M:%S") if dt else ""


def keep_time_to_timestamp(value) -> int | None:
    dt = parse_keep_datetime(value)
    return int(dt.timestamp()) if dt else None


def _keep_avg_heartrate(detail_data: dict, stats: dict) -> float | int | None:
    hr_block = detail_data.get("heartRate") or {}
    avg_hr = None
    if isinstance(hr_block, dict):
        avg_hr = hr_block.get("averageHeartRate") or stats.get("averageHeartRate")
    if avg_hr is not None and avg_hr < 0:
        return None
    return avg_hr


def _keep_calories(detail_data: dict, stats: dict) -> float | None:
    cal = detail_data.get("calorie") or stats.get("calorie")
    return float(cal) if cal and cal > 0 else None


def _keep_cadence(detail_data: dict, stats: dict) -> float | None:
    cad = (
        detail_data.get("cadence")
        or detail_data.get("averageCadence")
        or stats.get("cadence")
        or stats.get("averageCadence")
    )
    return float(cad) if cad and cad > 0 else None


def _keep_location(detail_data: dict, stats: dict) -> str | None:
    loc = (
        detail_data.get("region")
        or detail_data.get("location")
        or detail_data.get("city")
        or stats.get("region")
        or stats.get("location")
        or stats.get("city")
    )
    if isinstance(loc, str) and loc.strip():
        return loc.strip()
    if isinstance(loc, dict):
        return loc.get("city") or loc.get("name") or loc.get("region") or None
    return None


def format_keep_record(
    sport_type: str,
    stats: dict,
    detail: dict | None,
) -> dict | None:
    stats_id = stats.get("id") or ""
    keep_id = extract_keep_id(stats_id)
    if not keep_id:
        return None

    detail_data = (detail or {}).get("data") or {}
    data_type = detail_data.get("dataType") or stats.get("subtype") or ""
    strava_type = KEEP2STRAVA.get(data_type, "Workout")

    duration_sec = detail_data.get("duration") or stats.get("duration") or 0
    if not duration_sec:
        return None

    distance_m = int(
        round(float(detail_data.get("distance") or stats.get("distance") or 0))
    )
    start_ms = detail_data.get("startTime") or stats.get("doneDate") or 0
    avg_hr = _keep_avg_heartrate(detail_data, stats)
    avg_speed_ms = distance_m / duration_sec if duration_sec > 0 else 0
    coords = decode_geo_polyline(detail_data.get("geoPoints") or "")
    name = detail_data.get("name") or KEEP_TYPE_CN.get(data_type) or stats.get("statsName") or f"Keep {strava_type}"

    return build_activity_record(
        run_id=f"keep_{keep_id}",
        name=name,
        activity_type=strava_type,
        distance_m=distance_m,
        duration_sec=int(duration_sec),
        start_date_local=keep_time_to_local_str(start_ms),
        average_heartrate=round(avg_hr) if avg_hr else None,
        average_speed_ms=avg_speed_ms,
        total_elevation_gain=detail_data.get("elevationGain")
        or stats.get("elevationGain")
        or 0,
        summary_polyline=encode_summary_polyline(coords),
        calories=_keep_calories(detail_data, stats),
        average_cadence=_keep_cadence(detail_data, stats),
        location_city=_keep_location(detail_data, stats),
    )


def main() -> int:
    set_log_scope("Keep")
    section("Keep 运动同步")
    try:
        log_sync_startup(PATHS)
        if not _HAS_CRYPTO or not _HAS_POLYLINE:
            info("未装 pycryptodome/polyline，轨迹折线将为空")

        local_data = load_activities(PATHS.activities)
        info(f"本地 {len(local_data)} 条")
        if SYNC_LIMIT:
            info(f"单次上限 SYNC_LIMIT={SYNC_LIMIT}")

        session, headers = build_keep_session()
        summaries = fetch_all_keep_summaries(
            session, headers, local_data, sync_limit=SYNC_LIMIT
        )
        info(f"摘要合计 {len(summaries)} 条")

        final_data, fetched_count, added_count = sync_keep_records(
            session, headers, local_data, summaries
        )
        finalize_sync(
            PATHS,
            local_data,
            final_data,
            fetched_count=fetched_count,
            added_count=added_count,
        )
        return 0
    except Exception as exc:
        err(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())

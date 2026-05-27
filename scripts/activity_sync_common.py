"""
运动数据同步共用模块（Strava / Keep）。

- 日志、JSON 读写、合并、AI 文案、月度统计
- 统一活动记录结构与同步流水线
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, TypeVar

import requests

T = TypeVar("T")

VERBOSE = os.getenv("SYNC_VERBOSE", "").lower() in ("1", "true", "yes")


class SyncLogger:
    """同步脚本统一日志：默认简洁，SYNC_VERBOSE=1 输出调试信息。"""

    def __init__(self, scope: str = "sync") -> None:
        self.scope = scope

    def _emit(self, icon: str, msg: str, *, file=None) -> None:
        print(f"{icon} [{self.scope}] {msg}", file=file, flush=True)

    def section(self, title: str) -> None:
        self._emit("▸", title)

    def info(self, msg: str) -> None:
        self._emit("ℹ️", msg)

    def ok(self, msg: str) -> None:
        self._emit("✅", msg)

    def warn(self, msg: str) -> None:
        self._emit("⚠️", msg)

    def err(self, msg: str) -> None:
        self._emit("❌", msg, file=sys.stderr)

    def debug(self, msg: str) -> None:
        if VERBOSE:
            self._emit("·", msg)

    def item(self, index: int, total: int, msg: str) -> None:
        if total <= 1:
            self.info(msg)
        else:
            self.info(f"({index}/{total}) {msg}")


log = SyncLogger("sync")


def set_log_scope(scope: str) -> SyncLogger:
    global log
    log = SyncLogger(scope)
    return log


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def assets_path(filename: str) -> str:
    return os.path.join(ASSETS_DIR, filename)


@dataclass(frozen=True)
class SyncPaths:
    activities: str
    stats: str


CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_AI_TOKEN = os.getenv("CF_AI_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_RAW_AI_PROVIDER = (os.getenv("AI_PROVIDER") or "openai").strip().lower()
if _RAW_AI_PROVIDER in ("cf", "cloudflare"):
    AI_PROVIDER = "cf"
elif _RAW_AI_PROVIDER in ("openai", "oai", "gpt"):
    AI_PROVIDER = "openai"
else:
    AI_PROVIDER = "openai"

AI_ENABLED = os.getenv("AI_ENABLED", "1").lower() in ("1", "true", "yes")

ACTIVITY_TYPE_CN = {
    "Run": "跑步",
    "Ride": "骑行",
    "VirtualRide": "室内骑行",
    "EBikeRide": "电助力骑行",
    "Walk": "徒步",
    "Hike": "远足",
    "Swim": "游泳",
}

RUN_LIKE_TYPES = frozenset(
    {"Run", "TrailRun", "VirtualRun", "Walk", "Hike", "Workout"}
)
RIDE_LIKE_TYPES = frozenset({"Ride", "VirtualRide", "EBikeRide"})
_LONGEST_RUN_TYPES = frozenset({"Run", "TrailRun"})


def get_ai_provider() -> str:
    return AI_PROVIDER


def has_ai_credentials() -> bool:
    if not AI_ENABLED:
        return False
    if get_ai_provider() == "cf":
        return bool(CF_ACCOUNT_ID and CF_AI_TOKEN)
    return bool(OPENAI_API_KEY)


def ai_provider_label() -> str:
    if get_ai_provider() == "cf":
        return "Cloudflare AI"
    return f"OpenAI ({OPENAI_MODEL})"


def log_ai_startup_status() -> None:
    max_hr = _user_max_hr()
    hr_note = f"HRmax={max_hr}" if max_hr else "HRmax=固定阈值"
    min_km = _ai_min_km_for_llm()
    if has_ai_credentials():
        log.info(f"AI 已启用 ({ai_provider_label()}) · {hr_note} · AI_MIN_KM={min_km}")
        return
    provider = get_ai_provider()
    if provider == "openai":
        log.warn(
            f"AI 未启用：未设置 OPENAI_API_KEY · {hr_note} · "
            f"<{min_km}km 仍可用模板"
        )
    else:
        log.warn(
            f"AI 未启用：未设置 CF 凭证 · {hr_note} · <{min_km}km 仍可用模板"
        )


_SYNC_PROXY_OFF = frozenset({"0", "false", "no", "off", "direct"})


def _explicit_sync_proxies() -> tuple[str | None, str | None] | None:
    http_proxy = os.getenv("SYNC_HTTP_PROXY")
    https_proxy = os.getenv("SYNC_HTTPS_PROXY")
    if not http_proxy and not https_proxy:
        return None
    return http_proxy, https_proxy


def sync_use_proxy() -> bool:
    """是否走代理。SYNC_USE_PROXY=0/off 全部直连；未设或其它值则沿用系统 HTTP_PROXY。"""
    raw = (os.getenv("SYNC_USE_PROXY") or "").strip().lower()
    return raw not in _SYNC_PROXY_OFF


def sync_proxy_hint() -> str:
    return "若需全部直连请 export SYNC_USE_PROXY=0"


def log_sync_proxy_status() -> None:
    if not sync_use_proxy():
        log.info("网络：直连（SYNC_USE_PROXY=off）")
        return
    explicit = _explicit_sync_proxies()
    if explicit:
        http_proxy, https_proxy = explicit
        log.info(f"网络：代理 {https_proxy or http_proxy}（SYNC_HTTP_PROXY）")
        return
    sys_proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    if sys_proxy:
        log.info(f"网络：系统代理 {sys_proxy}")
    else:
        log.info("网络：直连（未配置代理）")


def parse_positive_int(raw: str | None) -> int | None:
    if not raw or not str(raw).strip().isdigit():
        return None
    value = int(raw)
    return value if value > 0 else None


def parse_time(time_str: str) -> datetime:
    try:
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return datetime.min


def _sort_activities_newest_first(records: list[dict]) -> None:
    records.sort(
        key=lambda item: parse_time(item.get("start_date_local", "")),
        reverse=True,
    )


def log_sync_startup(paths: SyncPaths) -> None:
    log.info(f"活动 → {paths.activities}")
    log.info(f"统计 → {paths.stats}")
    log_sync_proxy_status()
    log_ai_startup_status()


def format_time(seconds: int | float | None) -> str:
    if not seconds:
        return "--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def get_distance_km(record: dict) -> float:
    if "distance_km" in record:
        return float(record.get("distance_km") or 0)
    return float(record.get("distance") or 0)


def calculate_pace(activity_type: str, average_speed_ms: float) -> tuple[str, str]:
    if not average_speed_ms or average_speed_ms <= 0:
        return "--", ""

    if activity_type in ["Ride", "VirtualRide", "EBikeRide"]:
        kmh = average_speed_ms * 3.6
        return f"{kmh:.2f}", "km/h"
    if activity_type in ["Swim", "WaterSport"]:
        sec_per_100m = 100 / average_speed_ms
        mins, secs = divmod(sec_per_100m, 60)
        return f"{int(mins)}'{int(secs):02d}''", "100m"

    sec_per_km = 1000 / average_speed_ms
    mins, secs = divmod(sec_per_km, 60)
    return f"{int(mins)}'{int(secs):02d}''", "km"


def build_activity_record(
    *,
    run_id: str,
    name: str,
    activity_type: str,
    distance_m: int,
    duration_sec: int,
    start_date_local: str,
    average_heartrate: int | None,
    average_speed_ms: float,
    total_elevation_gain: float | int = 0,
    summary_polyline: str = "",
    calories: float | int | None = None,
    average_cadence: float | int | None = None,
    location_city: str | None = None,
    source: str | None = None,
) -> dict:
    """统一活动 JSON 结构（Strava / Keep 共用）。"""
    pace_num, pace_unit = calculate_pace(activity_type, average_speed_ms)
    distance_km = round(distance_m / 1000, 2)
    record = {
        "run_id": run_id,
        "name": name,
        "ai_comment": None,
        "type": activity_type,
        "distance": distance_m,
        "distance_km": distance_km,
        "moving_time": format_time(duration_sec),
        "start_date_local": start_date_local,
        "average_heartrate": average_heartrate,
        "average_speed": round(average_speed_ms * 3.6, 2) if average_speed_ms else 0,
        "pace_num": pace_num,
        "pace_unit": pace_unit,
        "total_elevation_gain": total_elevation_gain,
        "summary_polyline": summary_polyline or "",
    }
    if calories is not None:
        record["calories"] = calories
    if average_cadence is not None:
        record["average_cadence"] = average_cadence
    if location_city:
        record["location_city"] = location_city
    if source:
        record["source"] = source
    return record


def format_strava_activity(item: dict) -> dict:
    start_date = item.get("start_date_local", "")
    safe_time = start_date.replace("Z", "") if start_date else ""
    hr = item.get("average_heartrate", 0)
    distance_m = int(item.get("distance", 0) or 0)
    return build_activity_record(
        run_id=str(item.get("id")),
        name=item.get("name", "未命名运动"),
        activity_type=item.get("type", "Workout"),
        distance_m=distance_m,
        duration_sec=int(item.get("moving_time", 0) or 0),
        start_date_local=safe_time,
        average_heartrate=round(hr) if hr else None,
        average_speed_ms=float(item.get("average_speed", 0) or 0),
        total_elevation_gain=item.get("total_elevation_gain", 0),
        summary_polyline=item.get("map", {}).get("summary_polyline") or "",
        calories=item.get("calories") or None,
        average_cadence=item.get("average_cadence") or None,
        location_city=item.get("location_city") or None,
    )


def known_run_ids(local_data: list[dict]) -> set[str]:
    return {str(item["run_id"]) for item in local_data if item.get("run_id") is not None}


def cutoff_timestamp(local_data: list[dict]) -> int:
    """有本地数据时返回最新 start_date_local 的时间戳，否则 0（不截断）。"""
    if not local_data:
        return 0
    latest = local_data[0].get("start_date_local", "")
    dt = parse_time(latest)
    if dt == datetime.min:
        return 0
    return int(dt.timestamp())


def cap_sync_batch(
    items: list[T],
    limit: int | None,
    *,
    env_name: str,
    keep_newest_at_end: bool,
) -> list[T]:
    """按 SYNC_LIMIT 截断待处理列表并打日志。"""
    if not limit or len(items) <= limit:
        return items
    skipped = len(items) - limit
    if keep_newest_at_end:
        capped = items[-limit:]
        hint = "（列表按时间升序，保留末尾最新）"
    else:
        capped = items[:limit]
        hint = "（API 最新在前，保留头部最新）"
    log.info(
        f"{env_name}={limit}，仅处理最新 {limit} 条"
        f"（另有 {skipped} 条待下次同步）{hint}"
    )
    return capped


def ingest_records(
    local_data: list[dict],
    pending: list[T],
    *,
    label: Callable[[T], str],
    build: Callable[[T], dict | None],
    item_delay: float = 0.0,
) -> tuple[list[dict], int, int]:
    """格式化待同步项、可选 AI、合并进本地列表。"""
    history = list(local_data)
    formatted: list[dict] = []
    total = len(pending)

    for n, item in enumerate(pending, start=1):
        log.item(n, total, label(item))
        record = build(item)
        if not record:
            continue
        llm_used = apply_ai_to_record(record, history)
        if llm_used:
            time.sleep(1)
        formatted.append(record)
        history.insert(0, record)
        if item_delay > 0:
            time.sleep(item_delay)

    return merge_records(local_data, formatted)


def _load_json_file(file_path: str, default):
    if not os.path.exists(file_path):
        return default
    with open(file_path, "r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return default


def _save_json_file(file_path: str, data, *, atomic: bool = False) -> None:
    target = file_path
    if atomic:
        target = file_path + ".tmp"
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    if atomic:
        os.replace(target, file_path)


def load_activities(file_path: str) -> list[dict]:
    data = _load_json_file(file_path, []) or []
    _sort_activities_newest_first(data)
    return data


def save_activities(file_path: str, data: list[dict]) -> None:
    _sort_activities_newest_first(data)
    _save_json_file(file_path, data, atomic=True)


def merge_records(
    local_data: list[dict], new_records: list[dict]
) -> tuple[list[dict], int, int]:
    if not new_records:
        return local_data, 0, 0

    merged = {item["run_id"]: item for item in local_data if item.get("run_id")}
    initial_count = len(merged)
    for item in new_records:
        run_id = item.get("run_id")
        if run_id:
            merged[run_id] = item

    final_list = list(merged.values())
    _sort_activities_newest_first(final_list)
    return final_list, len(new_records), len(final_list) - initial_count


def finalize_sync(
    paths: SyncPaths,
    local_data: list[dict],
    final_data: list[dict],
    *,
    fetched_count: int,
    added_count: int,
) -> list[dict]:
    """merge 完成后在 final_data 上补全 AI，再按需写入活动 JSON 与月报。"""
    ai_changed = heal_missing_ai(final_data)
    needs_save = ai_changed or fetched_count > 0
    if needs_save:
        save_activities(paths.activities, final_data)
        log.ok(
            f"已保存：处理 {fetched_count} 条，新增 {added_count} 条，共 {len(final_data)} 条"
        )
    else:
        log.info("无变更，跳过写入")
        final_data = local_data

    if final_data:
        log.section("月度统计")
        update_stats(final_data, paths.stats)
    return final_data


def extract_ai_context(
    history_newest_first: list[dict],
    current_start: str,
    activity_type: str,
) -> dict:
    global_prev = history_newest_first[0] if history_newest_first else None
    same_prev = next(
        (x for x in history_newest_first if x.get("type") == activity_type),
        None,
    )

    def gap_days(previous: dict | None) -> int | None:
        if not previous:
            return None
        return (parse_time(current_start) - parse_time(previous["start_date_local"])).days

    if same_prev:
        prior = {
            "old_dist": get_distance_km(same_prev),
            "old_pace": f"{same_prev.get('pace_num', '')}{same_prev.get('pace_unit', '')}",
            "old_pace_num": same_prev.get("pace_num"),
            "old_pace_unit": same_prev.get("pace_unit"),
            "old_speed_kmh": same_prev.get("average_speed"),
            "old_hr": same_prev.get("average_heartrate"),
        }
    else:
        prior = {
            "old_dist": None,
            "old_pace": None,
            "old_pace_num": None,
            "old_pace_unit": None,
            "old_speed_kmh": None,
            "old_hr": None,
        }

    return {
        "global_gap_days": gap_days(global_prev),
        "last_type": global_prev.get("type") if global_prev else None,
        "same_gap_days": gap_days(same_prev),
        **prior,
    }


def parse_cf_ai_json_response(response_payload) -> dict | None:
    if response_payload is None:
        return None

    if isinstance(response_payload, dict):
        if "comment" in response_payload:
            return response_payload
        for key in ("content", "text", "message"):
            nested = response_payload.get(key)
            if isinstance(nested, str):
                parsed = parse_cf_ai_json_response(nested)
                if parsed:
                    return parsed
        return response_payload

    text_str = str(response_payload).strip()
    if not text_str:
        return None

    start_idx = text_str.find("{")
    end_idx = text_str.rfind("}")
    candidates = []
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        candidates.append(text_str[start_idx : end_idx + 1])
    clean_text = text_str.replace("```json", "").replace("```", "").strip()
    clean_text = clean_text.replace("\n", " ").replace("\r", "")
    candidates.append(clean_text)

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    return None


def _user_max_hr() -> int | None:
    raw = os.getenv("USER_MAX_HR", "").strip()
    if raw.isdigit() and int(raw) > 100:
        return int(raw)
    age = os.getenv("USER_AGE", "40").strip()
    if age.isdigit() and int(age) > 0:
        return max(100, 220 - int(age))
    return None


def get_hr_zone_info(bpm: int | float | None) -> str:
    if not bpm or bpm <= 0:
        return "未知区间"
    max_hr = _user_max_hr()
    if max_hr:
        pct = float(bpm) / max_hr
        if pct < 0.60:
            return "舒缓有氧 (Z1)"
        if pct < 0.70:
            return "稳态燃脂 (Z2)"
        if pct < 0.80:
            return "有氧强化 (Z3)"
        if pct < 0.90:
            return "乳酸阈值 (Z4)"
        return "无氧极限 (Z5)"
    if bpm < 115:
        return "舒缓有氧 (Z1)"
    if bpm <= 129:
        return "稳态燃脂 (Z2)"
    if bpm <= 144:
        return "有氧强化 (Z3)"
    if bpm <= 159:
        return "乳酸阈值 (Z4)"
    return "无氧极限 (Z5)"


def _ai_min_km_for_llm() -> float:
    raw = os.getenv("AI_MIN_KM", "3").strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 3.0


def _duration_label(time_str: str) -> str:
    sec = _parse_moving_time_sec(time_str)
    if not sec:
        return "时长未知"
    if sec < 1200:
        return "时长偏短"
    if sec < 3600:
        return "时长适中"
    return "时长较长"


def render_template_comment(insights: list[str]) -> str:
    """无 LLM 或 API 失败时，将预计算结论拼成可读短评。"""
    if not insights:
        return "本场训练数据不足，暂无法生成分析。"

    sentences: list[str] = []
    head = insights[0]
    if head.startswith("项目："):
        head = head[len("项目：") :]
    sentences.append(head.rstrip("。") + "。")

    tip = ""
    priority: list[str] = []
    regular: list[str] = []
    compare_kw = ("效率", "进步", "相近", "同距离", "放缓", "强度", "恢复", "爬升")

    for line in insights[1:]:
        if line.startswith("建议方向："):
            tip = line[len("建议方向：") :].rstrip("。")
            continue
        if line.startswith("配速/均速：") or re.search(r"\d", line):
            continue
        if any(kw in line for kw in compare_kw):
            priority.append(line)
        else:
            regular.append(line)

    for line in (priority + regular)[:2]:
        sentences.append(line.rstrip("。") + "。")

    if tip:
        sentences.append(f"建议{tip}。")

    text = "".join(sentences)
    return text[:200] if len(text) > 200 else text


def _needs_ai_refresh(record: dict) -> bool:
    return not record.get("ai_comment")


def _parse_moving_time_sec(time_str: str) -> int | None:
    if not time_str or time_str == "--":
        return None
    parts = [int(p) for p in str(time_str).split(":") if p.isdigit()]
    if not parts:
        return None
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return None


def _hr_pace_balance_insight(
    hr: float, pace_sec: float, activity_type: str
) -> str | None:
    max_hr = _user_max_hr() or 180
    hr_pct = hr / max_hr
    if activity_type not in RUN_LIKE_TYPES:
        return None
    if hr_pct >= 0.85 and pace_sec >= 360:
        return "心率已达较高区间而配速偏慢，留意恢复、补水或疲劳累积"
    if hr_pct <= 0.72 and pace_sec <= 330:
        return "配速较快且心率仍在有氧区间，效率运用较好"
    if hr_pct >= 0.90:
        return "心率接近上限区间，注意控制强度与恢复"
    return None


def _parse_run_pace_sec(pace_num: str) -> float | None:
    if not pace_num or pace_num == "--":
        return None
    match = re.match(r"(\d+)'(\d+)''?", str(pace_num).strip())
    if not match:
        return None
    return int(match.group(1)) * 60 + int(match.group(2))


def _distance_training_label(km: float) -> str:
    if km < 3:
        return "短距离（偏恢复或热身）"
    if km < 10:
        return "日常训练距离"
    if km < 21:
        return "中长距离"
    return "长距离"


def _intensity_from_hr_zone(zone: str) -> str:
    if "Z1" in zone or "Z2" in zone:
        return "整体偏轻松有氧"
    if "Z3" in zone:
        return "有氧强化/节奏训练强度"
    if "Z4" in zone:
        return "强度偏高，接近阈值"
    if "Z5" in zone:
        return "高强度，需注意恢复"
    return "强度待评估"


def _recovery_gap_insight(days: int | None) -> str | None:
    if days is None:
        return None
    if days <= 1:
        return "连续训练，注意恢复"
    if days <= 7:
        return "距上次运动间隔正常"
    return "久未训练，宜控制强度"


def _elevation_insight(km: float, gain: float | int) -> str | None:
    gain_f = float(gain or 0)
    if gain_f <= 0 or km <= 0:
        return None
    per_km = gain_f / km
    if per_km >= 30:
        return "爬升较大，心率偏高可能与爬坡有关"
    if per_km >= 15:
        return "路线有一定起伏"
    return None


def _compare_run_efficiency(
    cur_pace_sec: float,
    cur_hr: float,
    cur_km: float,
    old_pace_sec: float,
    old_hr: float,
    old_km: float,
) -> list[str]:
    lines: list[str] = []
    pace_diff = cur_pace_sec - old_pace_sec
    hr_diff = cur_hr - old_hr

    if abs(pace_diff) <= 15:
        if hr_diff <= -3:
            lines.append("配速相近但心率更低，有氧效率提升")
        elif hr_diff >= 3:
            lines.append("配速相近但心率更高，可能疲劳或环境偏热")
        else:
            lines.append("配速与心率与上次同类相近，状态稳定")
    elif pace_diff < -15:
        if hr_diff <= 0:
            lines.append("配速更快且心率未升高，表现进步")
        else:
            lines.append("配速更快且心率升高，强度明显增加")
    elif hr_diff <= -3:
        lines.append("配速放缓且心率更低，符合恢复跑特征")
    else:
        lines.append("配速较上次放缓，需结合目标判断是否刻意降强度")
    return lines


def _compare_ride_efficiency(
    cur_speed: float,
    cur_hr: float,
    old_speed: float,
    old_hr: float,
) -> list[str]:
    speed_diff = cur_speed - old_speed
    hr_diff = cur_hr - old_hr
    if abs(speed_diff) < 1:
        if hr_diff <= -3:
            return ["均速相近但心率更低，骑行效率提升"]
        if hr_diff >= 3:
            return ["均速相近但心率更高，强度或疲劳上升"]
        return ["均速与心率与上次同类相近"]
    if speed_diff > 1 and hr_diff <= 0:
        return ["均速更快且心率未升，表现进步"]
    if speed_diff > 1:
        return ["均速更快且心率升高，强度增加"]
    return ["均速较上次放缓，可能为恢复骑或路况影响"]


def compute_activity_insights(record: dict, ctx: dict) -> list[str]:
    """规则预计算训练结论，供 LLM 润色（避免编造数据）。"""
    activity_type = record.get("type", "Workout")
    type_cn = ACTIVITY_TYPE_CN.get(activity_type, "运动")
    km = get_distance_km(record)
    hr = record.get("average_heartrate")
    time_str = record.get("moving_time", "--")

    insights: list[str] = [
        f"项目：{type_cn}，{_distance_training_label(km)}，{_duration_label(time_str)}",
    ]

    if hr:
        hr_zone = get_hr_zone_info(hr)
        insights.append(f"心率处于{hr_zone}，{_intensity_from_hr_zone(hr_zone)}")
        pace_sec = _parse_run_pace_sec(record.get("pace_num", ""))
        balance = _hr_pace_balance_insight(float(hr), pace_sec, activity_type) if pace_sec else None
        if balance:
            insights.append(balance)
    else:
        insights.append("无心率数据，仅能依据配速/均速与距离评估")

    duration_sec = _parse_moving_time_sec(time_str)
    if duration_sec and duration_sec < 1200 and km >= _ai_min_km_for_llm():
        insights.append("时长偏短，更像速度课或时间有限的训练")

    elev = _elevation_insight(km, record.get("total_elevation_gain", 0))
    if elev:
        insights.append(elev)

    gap = _recovery_gap_insight(ctx.get("global_gap_days"))
    if gap:
        insights.append(gap)

    same_gap = ctx.get("same_gap_days")
    if same_gap is not None and same_gap != ctx.get("global_gap_days"):
        insights.append(f"距上次{type_cn}不久，中间有其他项目训练")

    old_hr = ctx.get("old_hr")
    old_dist = ctx.get("old_dist")
    old_pace_num = ctx.get("old_pace_num")
    old_speed = ctx.get("old_speed_kmh")

    if old_dist is not None and old_hr and hr:
        cur_pace_sec = _parse_run_pace_sec(record.get("pace_num", ""))
        old_pace_sec = _parse_run_pace_sec(old_pace_num or "")

        if activity_type in RIDE_LIKE_TYPES and record.get("average_speed") and old_speed:
            insights.extend(
                _compare_ride_efficiency(
                    float(record["average_speed"]),
                    float(hr),
                    float(old_speed),
                    float(old_hr),
                )
            )
        elif cur_pace_sec and old_pace_sec:
            insights.extend(
                _compare_run_efficiency(
                    cur_pace_sec,
                    float(hr),
                    km,
                    old_pace_sec,
                    float(old_hr),
                    float(old_dist),
                )
            )
        elif old_dist and abs(km - old_dist) / max(old_dist, 0.1) < 0.15:
            hr_diff = float(hr) - float(old_hr)
            if hr_diff <= -3:
                insights.append("同距离心率更低，效率提升")
            elif hr_diff >= 3:
                insights.append("同距离心率更高，强度或状态偏重")
            else:
                insights.append("同距离心率与上次接近")

    if hr:
        zone = get_hr_zone_info(hr)
        if "Z4" in zone or "Z5" in zone:
            insights.append("建议方向：次日轻松恢复或降强度")
        elif "Z1" in zone or "Z2" in zone:
            if km < 5:
                insights.append("建议方向：强度适中，可维持或略增距离")
            else:
                insights.append("建议方向：有氧基础训练，可保持当前强度区间")
        elif "Z3" in zone:
            insights.append("建议方向：注意配速稳定，避免后半程心率继续攀升")
    else:
        insights.append("建议方向：若有条件佩戴心率带，便于评估强度")

    return insights


_METRIC_IN_COMMENT = re.compile(
    r"\d+[\d.]*\s*(?:km|公里|bpm|次/分|kph|km/h)"
    r"|\d+'\d+''?"
    r"|\d{1,2}:\d{2}(?::\d{2})?"
    r"|心率\s*\d+"
    r"|\d+[\d.]*%"
    r"|\d+\s*m(?:/km)?"
)


def _scrub_comment_metrics(comment: str) -> str:
    """去掉 comment 里残留的公里、配速、心率等数字片段。"""
    text = _METRIC_IN_COMMENT.sub("", comment)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _build_activity_ai_prompt(record: dict, insights: list[str]) -> str:
    type_cn = ACTIVITY_TYPE_CN.get(record.get("type", "Workout"), "运动")
    insights_block = "\n".join(f"- {line}" for line in insights)

    return f"""你是运动教练，将下列【系统结论】改写成 100–150 字训练分析。

【系统结论】（必须全部体现，不得矛盾；禁止编造分段、步频、后程掉速等未提供的数据）
{insights_block}

【输出】仅返回一行 JSON：{{"comment":"..."}}
- 结构：一句总结 → 一句依据 → 一句建议
- 只讨论{type_cn}；用区间、快慢、强弱、长短等概括，禁止出现任何阿拉伯数字及单位（公里、km、配速、分钟、bpm、心率数值、爬升、百分比、天数等）
- JSON 内勿用英文双引号；comment 单行无换行"""


def generate_ai_content(
    record: dict,
    ctx: dict,
    *,
    insights: list[str] | None = None,
) -> tuple[str | None, bool]:
    """返回 (comment, 是否调用了 LLM)。"""
    insights = insights or compute_activity_insights(record, ctx)
    km = get_distance_km(record)

    if km < _ai_min_km_for_llm():
        log.debug(f"距离 {km} km < AI_MIN_KM，使用模板")
        return _scrub_comment_metrics(render_template_comment(insights)), False

    if not has_ai_credentials():
        return None, False

    log.debug(f"AI 预计算 {len(insights)} 条结论")
    prompt = _build_activity_ai_prompt(record, insights)
    ai_result = _call_ai(prompt, temperature=0.65, max_tokens=350)
    if ai_result:
        comment = ai_result.get("comment")
        if comment:
            return _scrub_comment_metrics(comment), True

    log.warn("LLM 未返回有效结果，回退模板")
    return _scrub_comment_metrics(render_template_comment(insights)), True


def create_sync_http_session(scope: str) -> requests.Session:
    """同步脚本 HTTP Session。由 SYNC_USE_PROXY 统一控制是否走代理。"""
    session = requests.Session()
    if not sync_use_proxy():
        session.trust_env = False
        log.debug(f"{scope} 请求已禁用系统代理")
        return session
    explicit = _explicit_sync_proxies()
    if explicit:
        http_proxy, https_proxy = explicit
        session.trust_env = False
        session.proxies = {
            "http": http_proxy,
            "https": https_proxy or http_proxy,
        }
        log.debug(f"{scope} 请求使用 SYNC_HTTP(S)_PROXY")
    return session


_RETRYABLE_REQUEST_ERRORS = (
    requests.exceptions.ProxyError,
    requests.exceptions.SSLError,
    requests.exceptions.ConnectionError,
)


def request_with_retries(
    session: requests.Session,
    method: str,
    url: str,
    *,
    retries: int = 3,
    retry_delay: float = 1.0,
    **kwargs,
) -> requests.Response:
    delay = retry_delay
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return session.request(method, url, **kwargs)
        except _RETRYABLE_REQUEST_ERRORS as exc:
            last_exc = exc
            if attempt >= retries:
                break
            log.warn(f"请求失败 ({attempt}/{retries})，{delay:.0f}s 后重试…")
            time.sleep(delay)
            delay = min(delay * 2, 8)
    assert last_exc is not None
    raise last_exc


_AI_SESSION: requests.Session | None = None


def _get_ai_session() -> requests.Session:
    global _AI_SESSION
    if _AI_SESSION is None:
        _AI_SESSION = create_sync_http_session("AI")
    return _AI_SESSION


def _log_ai_request_error(provider: str, exc: Exception) -> None:
    if isinstance(exc, requests.exceptions.ProxyError):
        log.warn(
            f"{provider} 代理连接失败: {exc}。"
            f"{sync_proxy_hint()}；"
            "或检查 HTTP_PROXY/HTTPS_PROXY、SYNC_HTTP(S)_PROXY"
        )
        return
    if isinstance(exc, requests.exceptions.SSLError):
        log.warn(f"{provider} SSL 连接失败: {exc}。{sync_proxy_hint()}")
        return
    log.warn(f"{provider} 异常: {exc}")


def _post_llm_chat(
    provider: str,
    url: str,
    headers: dict[str, str],
    payload: dict,
    *,
    timeout: int,
    extract_content: Callable[[requests.Response], object],
    on_error_status: Callable[[requests.Response], None] | None = None,
) -> dict | None:
    try:
        response = _get_ai_session().post(
            url, headers=headers, json=payload, timeout=timeout
        )
        if response.status_code == 200:
            content = extract_content(response)
            result_json = parse_cf_ai_json_response(content)
            if result_json:
                return result_json
            log.warn(f"{provider} 返回 200 但无法解析 JSON")
        if on_error_status:
            on_error_status(response)
        else:
            log.warn(
                f"{provider} 失败 HTTP {response.status_code}: {response.text[:200]}"
            )
    except Exception as exc:
        _log_ai_request_error(provider, exc)
    return None


def _call_ai(
    prompt: str, *, temperature: float = 0.9, max_tokens: int = 1000
) -> dict | None:
    if get_ai_provider() == "openai":
        return _call_openai(prompt, temperature=temperature, max_tokens=max_tokens)
    return _call_cf(prompt, temperature=temperature, max_tokens=max_tokens)


def _call_cf(
    prompt: str, *, temperature: float = 0.9, max_tokens: int = 1000
) -> dict | None:
    if not (CF_ACCOUNT_ID and CF_AI_TOKEN):
        log.warn("AI_PROVIDER=cf 但未配置 CF_ACCOUNT_ID / CF_AI_TOKEN")
        return None

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}"
        "/ai/run/@cf/meta/llama-4-scout-17b-16e-instruct"
    )
    headers = {"Authorization": f"Bearer {CF_AI_TOKEN}"}
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    def on_cf_error(response: requests.Response) -> None:
        if response.status_code == 429:
            log.warn("CF AI 配额已用尽 (HTTP 429)，可改用 AI_PROVIDER=openai")
        else:
            log.warn(f"CF AI 失败 HTTP {response.status_code}: {response.text[:160]}")

    return _post_llm_chat(
        "CF AI",
        url,
        headers,
        payload,
        timeout=45,
        extract_content=lambda response: response.json()["result"]["response"],
        on_error_status=on_cf_error,
    )


def _call_openai(
    prompt: str, *, temperature: float = 0.9, max_tokens: int = 1000
) -> dict | None:
    if not OPENAI_API_KEY:
        log.warn("AI_PROVIDER=openai 但未配置 OPENAI_API_KEY")
        return None

    url = f"{OPENAI_BASE_URL}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    def extract_openai_content(response: requests.Response) -> object:
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    return _post_llm_chat(
        "OpenAI",
        url,
        headers,
        payload,
        timeout=120,
        extract_content=extract_openai_content,
    )


def apply_ai_to_record(record: dict, history_newest_first: list[dict]) -> bool:
    """写入 ai_comment；返回是否调用了 LLM（用于节流 sleep）。"""
    safe_time = record.get("start_date_local", "")
    ctx = extract_ai_context(
        history_newest_first, safe_time, record.get("type", "Workout")
    )
    insights = compute_activity_insights(record, ctx)

    if not _needs_ai_refresh(record):
        log.debug(
            f"AI 已有分析 {record.get('start_date_local', '') or record.get('run_id', '?')}"
        )
        return False

    gap = ctx["global_gap_days"]
    if gap is not None:
        log.debug(
            f"AI {safe_time} 距上次 {gap} 天，距上次同类 {ctx['same_gap_days']} 天"
        )

    km = get_distance_km(record)
    if not has_ai_credentials() and km >= _ai_min_km_for_llm():
        return False

    comment, llm_used = generate_ai_content(record, ctx, insights=insights)
    if comment:
        record["ai_comment"] = comment
    else:
        log.warn(
            f"AI 分析未生成 {record.get('start_date_local', '') or record.get('run_id', '?')}"
        )
    return llm_used


def heal_missing_ai(local_data: list[dict]) -> bool:
    missing = [
        (index, item)
        for index, item in enumerate(local_data)
        if _needs_ai_refresh(item)
    ]
    if not missing:
        return False
    if not has_ai_credentials():
        missing = [
            (index, item)
            for index, item in missing
            if get_distance_km(item) < _ai_min_km_for_llm()
        ]
        if not missing:
            return False

    label = ai_provider_label() if has_ai_credentials() else "模板"
    log.info(f"补全 AI 分析 {len(missing)} 条（{label}）")
    filled = 0
    for n, (index, item) in enumerate(missing, start=1):
        log.item(
            n,
            len(missing),
            item.get("start_date_local", "") or item.get("run_id", "?"),
        )
        before = item.get("ai_comment")
        llm_used = apply_ai_to_record(item, local_data[index + 1 :])
        if item.get("ai_comment") and item.get("ai_comment") != before:
            filled += 1
        if llm_used:
            time.sleep(1)

    if filled:
        log.ok(f"AI 分析已补全 {filled}/{len(missing)} 条")
    else:
        log.warn(f"AI 分析补全失败（0/{len(missing)}），请检查 CF/OpenAI 配置与配额")
    return filled > 0


def get_time_of_day(hour: int) -> str:
    time_zones = ["午夜", "破晓", "清晨", "上午", "正午", "午后", "暮色", "暗夜"]
    return time_zones[hour // 3]


def calculate_monthly_stats(month_activities: list[dict]) -> dict:
    stats: dict = {
        "total_count": len(month_activities),
        "total_distance_km": 0.0,
        "sports_count": defaultdict(int),
        "time_preferences": defaultdict(int),
        "longest_ride_km": 0.0,
        "longest_run_km": 0.0,
        "hardest_session": {"date": None, "type": None, "hr": 0, "zone": "未知"},
        "hr_sums": defaultdict(list),
        "active_days": set(),
    }

    for act in month_activities:
        raw_type = act.get("type", "Unknown")
        sport_type_cn = ACTIVITY_TYPE_CN.get(raw_type, "运动")
        dist = get_distance_km(act)
        hr = act.get("average_heartrate", 0)
        start_date = act.get("start_date_local", "")

        stats["total_distance_km"] += dist
        stats["sports_count"][sport_type_cn] += 1

        if start_date:
            dt = parse_time(start_date)
            if dt != datetime.min:
                stats["active_days"].add(dt.date())
                stats["time_preferences"][get_time_of_day(dt.hour)] += 1

        if raw_type in RIDE_LIKE_TYPES and dist > stats["longest_ride_km"]:
            stats["longest_ride_km"] = dist
        elif raw_type in _LONGEST_RUN_TYPES and dist > stats["longest_run_km"]:
            stats["longest_run_km"] = dist

        if hr and hr > stats["hardest_session"]["hr"]:
            day_str = f"{int(start_date[8:10])}号" if len(start_date) >= 10 else "未知"
            stats["hardest_session"] = {
                "date": day_str,
                "type": sport_type_cn,
                "hr": round(hr),
                "zone": get_hr_zone_info(hr),
            }

        if hr:
            stats["hr_sums"][sport_type_cn].append(hr)

    stats["total_distance_km"] = round(stats["total_distance_km"], 2)
    stats["sports_count"] = dict(stats["sports_count"])
    stats["favorite_time"] = (
        max(stats["time_preferences"], key=stats["time_preferences"].get)
        if stats["time_preferences"]
        else "未知"
    )

    stats["avg_hr"] = {}
    for stype_cn, hrs in stats["hr_sums"].items():
        avg_bpm = round(sum(hrs) / len(hrs))
        stats["avg_hr"][stype_cn] = f"{avg_bpm}bpm ({get_hr_zone_info(avg_bpm)})"

    sorted_days = sorted(stats["active_days"])
    max_streak = 0
    if sorted_days:
        max_streak = 1
        current_streak = 1
        for i in range(1, len(sorted_days)):
            if sorted_days[i] == sorted_days[i - 1] + timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
    stats["max_streak_days"] = max_streak

    del stats["active_days"]
    del stats["time_preferences"]
    del stats["hr_sums"]
    return stats


def _monthly_phase_brief(current_day: int) -> tuple[str, list[str], str]:
    """返回 (阶段名, 写作要点, 行动指令指向)。"""
    if current_day <= 10:
        return (
            f"月初（第 {current_day} 天）",
            [
                "样本少属正常，重单次质量与状态，勿因总次数/总里程低而批评",
                "语气积极，顺带提醒本月中下旬保持节奏、防懈怠",
            ],
            "本月中下旬",
        )
    if current_day <= 22:
        return (
            f"月中（第 {current_day} 天）",
            [
                "综合看出勤频率、心率强度、项目偏好与时段习惯",
                "指出 1 个最可能影响目标的隐患，语气直接但不刻薄",
            ],
            "本月剩余时间",
        )
    return (
        f"月末（第 {current_day} 天）",
        [
            "作月度复盘：容量、强度、连续性；有上月数据则对比趋势",
            "点出本月最明显短板，并给出可执行的下月改进方向",
        ],
        "下个自然月",
    )


def _build_monthly_stats_block(
    month_str: str, stats: dict, prev_stats: dict | None
) -> str:
    lines = [
        f"- 月份：{month_str}",
        f"- 合计：{stats['total_count']} 次 · {stats['total_distance_km']} km · "
        f"最长连续 {stats['max_streak_days']} 天",
        f"- 偏好：{stats['sports_count']} · 常练时段 {stats['favorite_time']}",
        f"- 平均心率：{stats['avg_hr']}",
    ]
    hardest = stats.get("hardest_session") or {}
    if hardest.get("hr", 0) > 0:
        lines.append(
            f"- 强度峰值：{hardest.get('date')} {hardest.get('type')} "
            f"{hardest.get('hr')} bpm（{hardest.get('zone')}）"
        )
    if prev_stats:
        lines.append(
            f"- 上月对比：{prev_stats['total_count']} 次 · "
            f"{prev_stats['total_distance_km']} km"
        )
    return "\n".join(lines)


def _build_monthly_ai_prompt(
    *,
    month_str: str,
    stats: dict,
    prev_stats: dict | None,
    current_day: int,
) -> str:
    phase_label, focus_lines, action_target = _monthly_phase_brief(current_day)
    stats_block = _build_monthly_stats_block(month_str, stats, prev_stats)
    focus_block = "\n".join(f"- {line}" for line in focus_lines)

    return f"""你是运动私教，写月度训练小结。文风克制、有判断力，像私教月报而非数据朗读。

【阶段】{phase_label}
【数据摘要】
{stats_block}

【写作要点】
{focus_block}

【输出】仅返回一行 JSON：{{"comment":"..."}}
- comment：100–150 字（约 2–3 句）；结构：先肯定亮点 → 点出问题/风险 → 对「{action_target}」给 1 条可执行建议
- 可概括趋势与习惯，勿逐条复读上面的次数、公里、心率数字；表达新颖、避免空话套话
- JSON 字符串内勿使用英文双引号，强调用单引号；comment 单行无换行"""


def generate_monthly_ai_report(
    month_str: str, stats: dict, prev_stats: dict | None, current_day: int
) -> str | None:
    if not has_ai_credentials():
        return None

    prompt = _build_monthly_ai_prompt(
        month_str=month_str,
        stats=stats,
        prev_stats=prev_stats,
        current_day=current_day,
    )
    result = _call_ai(prompt, temperature=0.85, max_tokens=500)
    if result:
        return result.get("comment")
    return None


def update_stats(local_data: list[dict], stats_path: str) -> None:
    if not local_data:
        return

    insights = _load_json_file(stats_path, {})
    months_data: dict[str, list[dict]] = defaultdict(list)
    for act in local_data:
        date_str = act.get("start_date_local", "")
        if len(date_str) >= 7:
            months_data[date_str[0:7]].append(act)

    sorted_months = sorted(months_data.keys(), reverse=True)
    if not sorted_months:
        return

    for i, current_month_key in enumerate(sorted_months):
        current_stats = calculate_monthly_stats(months_data[current_month_key])
        prev_month_key = sorted_months[i + 1] if i + 1 < len(sorted_months) else None
        prev_stats = (
            calculate_monthly_stats(months_data[prev_month_key])
            if prev_month_key
            else None
        )

        existing = insights.get(current_month_key)
        old_stats = (existing or {}).get("stats", {})
        if existing and (
            old_stats.get("total_count") == current_stats["total_count"]
            and old_stats.get("total_distance_km") == current_stats["total_distance_km"]
        ):
            continue

        log.info(f"更新月报 {current_month_key}")
        latest_act_date = months_data[current_month_key][0].get("start_date_local", "")
        current_day = (
            int(latest_act_date[8:10]) if len(latest_act_date) >= 10 else 15
        )
        comment = generate_monthly_ai_report(
            current_month_key, current_stats, prev_stats, current_day
        )

        if comment:
            insights[current_month_key] = {
                "month_str": current_month_key,
                "last_update": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "stats": current_stats,
                "ai_comment": comment,
            }
            _save_json_file(stats_path, insights)
            log.ok(f"统计 {current_month_key} 已写入 {os.path.basename(stats_path)}")
            time.sleep(2)

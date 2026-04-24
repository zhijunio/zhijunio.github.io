#!/usr/bin/env python3
"""
从 Keep 读取跑步数据并生成 running.json。
通过 Keep API 拉取数据，包含 VDOT 跑力、训练负荷与周期统计。
"""

import argparse
import json
import logging
import math
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

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

DATATYPE_NAME = {
    "outdoorRunning": "户外跑步",
    "indoorRunning": "跑步机",
    "outdoorWalking": "步行",
    "outdoorCycling": "户外骑行",
    "mountaineering": "越野",
}

# 心率区间 (最大心率%阈值 -> zone)
HR_ZONE_THRESHOLDS: List[Tuple[int, int]] = [
    (84, 1), (89, 2), (94, 3), (99, 4),
    (102, 5), (105, 6), (106, 7),
]

MAX_HR = int(os.environ.get("MAX_HR", "180"))
RUNNER_WEIGHT_KG = float(os.environ.get("RUNNER_WEIGHT_KG", "70"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _n(val: Any) -> int:
    """安全转 int，无效返回 0。"""
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _f(val: Any) -> float:
    """安全转 float，无效返回 0.0。"""
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _time_label(hour: int) -> str:
    """根据小时数返回时段名称。"""
    if hour <= 5:
        return "凌晨"
    if hour <= 8:
        return "清晨"
    if hour <= 11:
        return "上午"
    if hour <= 13:
        return "中午"
    if hour <= 17:
        return "下午"
    if hour <= 19:
        return "傍晚"
    return "夜晚"


def _extract_weather(info: Any) -> str:
    """从 weatherInfo 中提取温度和湿度字符串。"""
    if isinstance(info, str):
        return info.strip()
    if isinstance(info, dict):
        temp = info.get("temperature", "").strip()
        humidity = info.get("humidity", "").strip()
        return f"{temp} {humidity}".strip()
    return ""


def _pick(obj: Dict, *keys: str, default: Any = None) -> Any:
    """从字典中按顺序取第一个存在的 key。"""
    for k in keys:
        v = obj.get(k)
        if v is not None:
            return v
    return default


def _login(session: requests.Session, mobile: str, password: str):
    """Keep 登录，返回 (session, headers) 或退出。"""
    logger.info("正在登录 Keep API...")
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    r = session.post(LOGIN_API, headers=headers, data={
        "mobile": mobile, "password": password,
    }, timeout=10)
    if not r.ok:
        logger.error("登录失败: HTTP %s, 响应: %s", r.status_code, r.text[:500])
        sys.exit(1)
    token = r.json().get("data", {}).get("token")
    if not token:
        logger.error("未获取到 token")
        sys.exit(1)
    headers["Authorization"] = f"Bearer {token}"
    logger.info("登录成功")
    return session, headers


def _fetch_with_retry(session, url: str, headers: Dict, max_retries: int = 3) -> requests.Response:
    """发送 GET 请求，遇到 429 时指数退避重试。"""
    for attempt in range(max_retries):
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code == 429:
            wait = 2 ** attempt
            logger.warning("请求被限流 (429), %d 秒后重试 (%d/%d)", wait, attempt + 1, max_retries)
            time.sleep(wait)
            continue
        if not r.ok:
            break
        return r
    return r


def _fetch_run_stats(
    session,
    headers,
    sport_type: str,
    last_date: int = 0,
    limit: Optional[int] = None,
    existing_keys: Optional[set] = None,
) -> List[Dict]:
    """分页获取跑步 stats 列表。

    Args:
        last_date: 分页起始时间戳 (毫秒)。0 = 从最新记录开始。
        limit: 客户端安全上限，超过后停止翻页。
        existing_keys: 已有记录的 startTime 集合。遇到已存在的记录时提前停止翻页。
    """
    result: List[Dict] = []
    page = 0
    hit_existing = False
    while True:
        page += 1
        r = _fetch_with_retry(
            session,
            RUN_DATA_API.format(sport_type=sport_type, last_date=last_date),
            headers,
        )
        if not r.ok:
            logger.warning("分页请求失败 (第 %d 页), HTTP %d", page, r.status_code)
            break
        data = r.json().get("data") or {}
        for group in data.get("records") or []:
            for entry in group.get("logs") or []:
                if isinstance(entry, dict):
                    stats = entry.get("stats")
                    if isinstance(stats, dict) and not stats.get("isDoubtful") and stats.get("id"):
                        result.append(stats)
                        # 增量检查：遇到已有记录 → 标记停止
                        if existing_keys:
                            start_ms = stats.get("startTime")
                            if isinstance(start_ms, (int, float)):
                                key = datetime.fromtimestamp(
                                    start_ms / 1000, tz=timezone.utc
                                ).astimezone(TZ_SH).strftime("%Y-%m-%d %H:%M:%S")
                                if key in existing_keys:
                                    hit_existing = True
                                    logger.info(
                                        "第 %d 页遇到已有记录 %s，增量数据已全部覆盖",
                                        page, key,
                                    )
                                    break
                        if limit and len(result) >= limit:
                            logger.info(
                                "第 %d 页后触发 limit(%d)，提前返回 %d 条",
                                page, limit, len(result),
                            )
                            return result
            if hit_existing:
                break
        page_count = len(result)
        last_date = data.get("lastTimestamp") or 0
        time.sleep(1)  # spider rule
        if not last_date or hit_existing:
            reason = "(末页)" if not last_date else "(遇到已有记录)"
            logger.info("第 %d 页获取 %d 条，共 %d 条 %s", page, len(data.get("records", [])), page_count, reason)
            break
        logger.info("第 %d 页获取 %d 条，共 %d 条", page, len(data.get("records", [])), len(result))
    return result


def _fetch_detail(session, headers, sport_type: str, run_id: str) -> Optional[Dict]:
    """获取单条跑步详情（含 429 重试）。"""
    r = _fetch_with_retry(
        session,
        RUN_LOG_API.format(sport_type=sport_type, run_id=run_id),
        headers,
    )
    return r.json().get("data") if r.ok else None


class VDCCalculator:
    """VDOT 跑力计算器 (Jack Daniels' Running Formula)。"""

    def __init__(self, max_hr: int = MAX_HR):
        self.max_hr = max_hr

    def hr_zone(self, avg_hr: float) -> int:
        """根据最大心率百分比获取心率区间 (1-7)。"""
        if avg_hr <= 0:
            return 0
        pct = (avg_hr / self.max_hr) * 100
        for thresh, zone in HR_ZONE_THRESHOLDS:
            if pct <= thresh:
                return zone
        return 7

    def calc_vdot(self, dist_m: float, dur_s: float) -> Optional[float]:
        """计算 VDOT。"""
        if dur_s <= 0 or dist_m <= 0:
            return None
        dur_min = dur_s / 60
        vpm = dist_m / dur_min
        if vpm <= 0:
            return None

        vo2 = -4.60 + 0.182258 * vpm + 0.000104 * vpm ** 2
        pct = (
            0.8
            + 0.1894393 * math.exp(-0.012778 * dur_min)
            + 0.2989558 * math.exp(-0.1932605 * dur_min)
        )
        if pct <= 0 or pct > 1.0:
            return None
        vdot = vo2 / pct
        return round(vdot, 1) if 20 <= vdot <= 100 else None


def _build_segments_from_cross_km(data: Dict, vc: VDCCalculator) -> List[Dict]:
    """从 crossKmPoints 构建每公里分段。"""
    points = data.get("crossKmPoints")
    if not isinstance(points, list):
        return []
    segs = []
    for i, pt in enumerate(points):
        if not isinstance(pt, dict):
            continue
        km = _n(_pick(pt, "km", "index", default=i + 1))
        pace = _n(_pick(pt, "kmPace", "pace", "paceSeconds"))
        speed = round(3600 / pace, 2) if pace > 0 else 0
        hr = _n(pt.get("averageHeartRate"))
        segs.append({
            "km": km,
            "averagePace": pace,
            "averageSpeed": speed,
            "averageHeartRate": hr,
            "heartRateZone": vc.hr_zone(hr),
            "stepFrequency": _n(pt.get("stepFrequency")),
        })
    return segs


def _estimate_power(
    dist_m: float, dur_s: float, elev_m: float = 0, cross_km: Optional[List] = None
) -> Tuple[Optional[int], Optional[int]]:
    """本地估算跑步功率（瓦特）。"""
    if dur_s <= 0 or dist_m <= 0:
        return None, None
    v = dist_m / dur_s
    avg_pwr = int(round(1.03 * RUNNER_WEIGHT_KG * v))
    if elev_m > 0:
        avg_pwr += int(round(RUNNER_WEIGHT_KG * 9.81 * elev_m / dur_s))

    max_pwr = avg_pwr
    if isinstance(cross_km, list):
        paces = [_f(_pick(pt, "kmPace", "pace", "paceSeconds")) for pt in cross_km if isinstance(pt, dict)]
        valid = [p for p in paces if p > 0]
        if valid:
            v_max = 1000.0 / min(valid)
            max_pwr = int(round(1.03 * RUNNER_WEIGHT_KG * v_max))
            if elev_m > 0:
                max_pwr += int(round(RUNNER_WEIGHT_KG * 9.81 * elev_m / dur_s))

    return avg_pwr or None, max_pwr or None


def _build_record(stats: Dict, vc: VDCCalculator, detail: Optional[Dict] = None) -> Optional[Dict]:
    """将 stats + detail API 数据转为 running.json 记录。"""
    # 距离: kmDistance (km) > accurateDistance (m) > distance (m)
    if stats.get("kmDistance"):
        dist_km = _f(stats["kmDistance"])
    elif stats.get("accurateDistance"):
        dist_km = _f(stats["accurateDistance"]) / 1000.0
    else:
        dist_km = _f(stats.get("distance", 0)) / 1000.0
    dist_m = dist_km * 1000.0

    # 时长: movingDuration (detail, 不含暂停) > duration (含暂停)
    dur_s = _n(stats.get("duration"))
    if detail:
        md = _n(detail.get("movingDuration"))
        if md > 0:
            dur_s = md

    if dur_s <= 0 or dist_m <= 0:
        return None
    dist_km = round(dist_km, 2)

    # 配速 (秒/km)
    pace = _n(stats.get("averagePace"))
    if pace <= 0:
        pace = round(dur_s / (dist_m / 1000))

    # 速度 (km/h)
    speed = _f(stats.get("averageSpeed"))
    if speed <= 0:
        speed = round(dist_km / (dur_s / 3600), 2)

    # 心率
    hr_data = stats.get("heartRate") or {}
    avg_hr = _n(hr_data.get("averageHeartRate"))
    max_hr_val = _n(hr_data.get("maxHeartRate"))

    # 时间
    start_ms = _n(stats.get("startTime"))
    start_local = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc).astimezone(TZ_SH).strftime("%Y-%m-%d %H:%M:%S")
    end_local = datetime.fromtimestamp((start_ms + dur_s * 1000) / 1000, tz=timezone.utc).astimezone(TZ_SH).strftime("%Y-%m-%d %H:%M:%S")

    # 数据类型
    dataType = DATATYPE_NAME.get(stats.get("dataType", ""), "户外跑步")

    # 名称
    name = f"{_time_label(datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc).hour)}{dataType}"

    # 天气 & 路线
    weather = ""
    route = "未知路线"
    if detail:
        region = detail.get("region") or {}
        route = f"{region.get('province','')}{region.get('city','')}{region.get('district','')}" or route
        weather = _extract_weather(detail.get("weatherInfo"))

    # 分段
    segs = []
    if detail:
        segs = _build_segments_from_cross_km(detail, vc) or _build_segments_from_cross_km(stats, vc)

    # 步频（优先从 detail 获取）
    step_freq = _n(_pick(detail, "averageStepFrequency", "stepFrequency")) if detail else 0
    if step_freq == 0:
        step_freq = _n(_pick(stats, "averageStepFrequency"))

    # 总步数（从 detail 获取）
    total_steps = _n(detail.get("totalSteps")) if detail else 0

    # 步幅（从 detail 补充）
    stride = _f(_pick(stats, "strideLength", "avgStrideLength", "averageStrideLength"))
    if stride == 0 and detail:
        stride = _f(_pick(detail, "strideLength", "avgStrideLength", "averageStrideLength"))

    # 爬升
    elev = _f(stats.get("accumulativeUpliftedHeight"))

    # 功率
    avg_pwr = _n(_pick(stats, "avgPower", "averagePower"))
    max_pwr = _n(_pick(stats, "maxPower", "peakPower"))
    if avg_pwr == 0 and max_pwr == 0:
        cross_km = stats.get("crossKmPoints") if isinstance(stats.get("crossKmPoints"), list) else None
        est_avg, est_max = _estimate_power(dist_m, dur_s, elev, cross_km)
        avg_pwr = est_avg or 0
        max_pwr = est_max or 0

    # VDOT / 心率区间
    vdot = vc.calc_vdot(dist_m, dur_s)
    hr_zone = vc.hr_zone(avg_hr) if avg_hr > 0 else 0

    # 训练负荷
    tl = _n(stats.get("trainingLoadScore"))
    if tl == 0:
        tl = round(dur_s / 3600 * 100)

    return {
        "startTime": start_local,
        "endTime": end_local,
        "type": stats.get("type", ""),
        "distance": dist_km,
        "duration": dur_s,
        "averagePace": pace,
        "averageSpeed": speed,
        "averageHeartRate": avg_hr,
        "maxHeartRate": max_hr_val,
        "calorie": _n(stats.get("calorie")),
        "elevationGain": round(elev, 1),
        "region": route,
        "weatherInfo": weather,
        "dataType": dataType,
        "name": name,
        "stepFrequency": step_freq,
        "totalSteps": total_steps,
        "strideLength": round(stride, 2),
        "averagePower": avg_pwr,
        "maxPower": max_pwr,
        "vDOT": vdot,
        "trainingLoadScore": tl,
        "heartRateZone": hr_zone,
        "segments": segs,
    }


_EMPTY_PERIOD = {
    "totalActivities": 0,
    "totalDistance": 0,
    "totalDuration": 0,
    "averagePace": 0,
    "averageHeartRate": None,
    "averageVdot": None,
    "bestVdot": None,
    "longestDistance": 0,
    "totalTrainingLoadScore": 0,
    "totalCalorie": 0,
}


def _period_stats(runs: List[Dict], start: datetime, end: datetime) -> Dict:
    """计算单个周期统计。"""
    period = []
    for r in runs:
        try:
            d = datetime.strptime(r["startTime"].split(" ")[0], "%Y-%m-%d")
            if start <= d <= end:
                period.append(r)
        except (ValueError, IndexError):
            continue

    if not period:
        return dict(_EMPTY_PERIOD)

    total_dist = sum(r["distance"] for r in period)
    total_s = sum(r.get("duration", 0) for r in period)
    total_tl = sum(r.get("trainingLoadScore", 0) for r in period)
    total_cal = sum(r.get("calorie", 0) for r in period)
    longest = max(r["distance"] for r in period)

    hr_sum = hr_cnt = vdot_sum = vdot_cnt = 0
    best_vdot = 0.0
    for r in period:
        hr = r.get("averageHeartRate") or 0
        if hr > 0:
            hr_sum += hr
            hr_cnt += 1
        vd = r.get("vDOT") or 0
        if vd > 0:
            vdot_sum += vd
            vdot_cnt += 1
            best_vdot = max(best_vdot, vd)

    return {
        "totalActivities": len(period),
        "totalDistance": round(total_dist, 2),
        "totalDuration": round(total_s / 3600, 2),
        "averagePace": round(total_s / total_dist) if total_dist > 0 else 0,
        "averageHeartRate": round(hr_sum / hr_cnt) if hr_cnt > 0 else None,
        "averageVdot": round(vdot_sum / vdot_cnt, 1) if vdot_cnt > 0 else None,
        "bestVdot": round(best_vdot, 1) if vdot_cnt > 0 else None,
        "longestDistance": longest,
        "totalTrainingLoadScore": total_tl,
        "totalCalorie": total_cal,
    }


def _calculate_stats(runs: List[Dict]) -> Dict:
    """计算各周期统计（昨日/今日/周/月/年/总）。"""
    now = datetime.now(TZ_SH).replace(tzinfo=None)
    yesterday = (datetime.now(TZ_SH) - timedelta(days=1)).date()
    y_start = datetime.combine(yesterday, datetime.min.time())
    y_end = datetime.combine(yesterday, datetime.max.time())

    monday = now - timedelta(days=now.isoweekday() - 1)
    w_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    return {
        "yesterday": _period_stats(runs, y_start, y_end),
        "today": _period_stats(runs, today_start, now),
        "week": _period_stats(runs, w_start, now),
        "month": _period_stats(runs, datetime(now.year, now.month, 1), now),
        "year": _period_stats(runs, datetime(now.year, 1, 1), now),
        "total": _period_stats(runs, datetime.min, now),
    }


def fetch_runs(
    mobile: str,
    password: str = "",
    sport_type: str = "running",
    last_date: int = 0,
    limit: Optional[int] = None,
    debug: bool = False,
    full: bool = False,
    existing_keys: Optional[set] = None,
) -> List[Dict]:
    """从 Keep API 拉取跑步数据（登录入口）。"""
    session, headers = _login(requests.Session(), mobile, password)
    return _fetch_runs_with_session(
        session, headers, sport_type=sport_type,
        last_date=last_date, limit=limit, debug=debug,
        full=full, existing_keys=existing_keys,
    )


def _fetch_runs_with_session(
    session,
    headers,
    sport_type: str = "running",
    last_date: int = 0,
    limit: Optional[int] = None,
    debug: bool = False,
    full: bool = False,
    existing_keys: Optional[set] = None,
) -> List[Dict]:
    """从 Keep API 拉取跑步数据（使用已有 session）。

    阶段 1: 分页获取 stats（列表 API 已包含大部分字段）
    阶段 2: 逐条获取详情（仅补充 region/weatherInfo/totalSteps）
    """
    if full:
        logger.info("全量模式: 将获取所有记录")

    run_stats = _fetch_run_stats(
        session, headers, sport_type,
        last_date=last_date, limit=limit,
        existing_keys=(existing_keys if (not full) and existing_keys else None),
    )
    if not run_stats:
        logger.error("Keep API 未返回任何记录")
        sys.exit(1)
    logger.info("获取 %d 条记录", len(run_stats))

    logger.info("开始获取 %d 条跑步详情 (间隔 1s/条)", len(run_stats))

    vc = VDCCalculator()
    records = []
    for i, stats in enumerate(run_stats):
        if i > 0:
            time.sleep(1.0)
        run_id = stats.get("id", "")
        detail = _fetch_detail(session, headers, sport_type, run_id)
        rec = _build_record(stats, vc, detail)
        if debug and rec:
            print("\n" + "=" * 60)
            print("【stats】")
            print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
            if detail:
                print("\n【detail】")
                print(json.dumps(detail, ensure_ascii=False, indent=2, default=str))
            print("\n【output】")
            print(json.dumps(rec, ensure_ascii=False, indent=2, default=str))
        if rec:
            records.append(rec)
        if (i + 1) % 20 == 0:
            logger.info("已解析 %d/%d (有效 %d 条)", i + 1, len(run_stats), len(records))

    logger.info("解析完成: %d/%d 条有效 (%d 条被丢弃)", len(records), len(run_stats), len(run_stats) - len(records))
    return records


def main():
    p = argparse.ArgumentParser(description="从 Keep API 拉取跑步数据并生成 running.json")
    p.add_argument("--output", default="../public/data/running.json")
    p.add_argument("--mobile", default=os.environ.get("KEEP_MOBILE", ""))
    p.add_argument("--password", default=os.environ.get("KEEP_PASSWORD", ""))
    p.add_argument("--limit", type=int, default=None, metavar="N",
                   help="客户端限制: 最多获取 N 条记录 (可选, 仅作为安全上限)")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--full", action="store_true",
                   help="全量模式: 获取所有记录，忽略已有数据，重新拉取全部")
    args = p.parse_args()

    mobile = (args.mobile or "").strip()
    if not mobile:
        logger.error("未提供手机号：设置 KEEP_MOBILE 环境变量或使用 --mobile")
        sys.exit(1)
    password = (args.password or "").strip()
    if not password:
        logger.error("未提供密码：设置 KEEP_PASSWORD 环境变量或使用 --password")
        sys.exit(1)

    # 先登录
    session, headers = _login(requests.Session(), mobile, password)

    # 登录后再加载已有数据
    existing_records: List[Dict] = []
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    if os.path.exists(out_path):
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            existing_records = old_data.get("runs", [])
            logger.info("加载已有 %d 条记录", len(existing_records))
        except json.JSONDecodeError as e:
            logger.warning("已有 running.json 解析失败 (%s)，从空记录开始", e)
    else:
        logger.info("running.json 不存在，仅使用新数据")

    # 计算 last_date (基于已有数据中最新记录的 startTime)
    # API 的 last_date 参数表示 "获取比这个时间更早的记录"
    # last_date=0 表示从最新记录开始（全量模式）
    last_date = 0
    if existing_records:
        newest = max(existing_records, key=lambda r: r.get("startTime", ""))
        try:
            dt = datetime.strptime(newest["startTime"], "%Y-%m-%d %H:%M:%S")
            ts_ms = int(dt.replace(tzinfo=timezone.utc).timestamp()) * 1000
            last_date = ts_ms
            logger.info("基于最新记录 %s 计算 last_date=%d 毫秒", newest["startTime"], last_date)
        except (ValueError, KeyError) as e:
            logger.warning("无法计算 last_date: %s, 使用全量模式", e)

    # 构建已有记录的 startTime 集合（用于增量检测）
    existing_keys = {r["startTime"] for r in existing_records}

    # 获取新数据（使用 last_date 作为分页起点 + 增量检测）
    new_records = _fetch_runs_with_session(
        session, headers,
        sport_type="running",
        last_date=last_date, limit=args.limit,
        debug=args.debug,
        full=args.full,
        existing_keys=existing_keys,
    )
    logger.info("获取 %d 条新记录", len(new_records))

    if not new_records and not existing_records:
        logger.error("没有读取到任何记录")
        sys.exit(1)

    # 合并并去重（按 startTime 去重，新数据优先）
    merged: Dict[str, Dict] = {r["startTime"]: r for r in existing_records}
    before = len(merged)
    merged.update({r["startTime"]: r for r in new_records})
    added = len(merged) - before
    logger.info("合并完成: %d (新增 %d 条)", len(merged), added)

    records = sorted(merged.values(), key=lambda x: x["startTime"], reverse=True)

    logger.info("写入 %s", out_path)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    output = {
        "statistics_time": datetime.now(TZ_SH).strftime("%Y-%m-%d %H:%M:%S"),
        "stats": _calculate_stats(records),
        "runs": records,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")
    logger.info("已保存到文件")

if __name__ == "__main__":
    main()

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

# ─── 常量 ───────────────────────────────────────────────────────────────
TZ_SH = timezone(timedelta(hours=8))

LOGIN_API = "https://api.gotokeep.com/v1.1/users/login"
RUN_DATA_API = (
    "https://api.gotokeep.com/pd/v3/stats/detail"
    "?dateUnit=all&type={sport_type}&last_date={last_date}"
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


# ═══════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════

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
    """从 weatherInfo 中提取温度字符串。"""
    if isinstance(info, str):
        return info.strip()
    if isinstance(info, dict):
        temp = info.get("temperature")
        if temp is not None:
            return str(temp).strip()
    return ""


def _pick(obj: Dict, *keys: str, default: Any = None) -> Any:
    """从字典中按顺序取第一个存在的 key。"""
    for k in keys:
        v = obj.get(k)
        if v is not None:
            return v
    return default



# ═══════════════════════════════════════════════════════════════════════
# Keep API 交互
# ═══════════════════════════════════════════════════════════════════════

def _login(session: requests.Session, mobile: str, password: str):
    """Keep 登录，返回 (session, headers) 或退出。"""
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
    return session, headers


def _fetch_run_ids(session, headers, sport_type: str, limit: Optional[int] = None) -> List[Dict]:
    """分页获取跑步记录列表。"""
    result = []
    last_ts = 0
    while True:
        r = session.get(
            RUN_DATA_API.format(sport_type=sport_type, last_date=last_ts),
            headers=headers,
            timeout=10,
        )
        if not r.ok:
            break
        data = r.json().get("data") or {}
        for group in data.get("records") or []:
            for entry in group.get("logs") or []:
                if isinstance(entry, dict):
                    stats = entry.get("stats")
                    if isinstance(stats, dict) and not stats.get("isDoubtful"):
                        if stats.get("id"):
                            result.append(stats)
                            if limit and len(result) >= limit:
                                return result
        last_ts = data.get("lastTimestamp") or 0
        if not last_ts:
            break
    return result


def _fetch_detail(session, headers, sport_type: str, run_id: str) -> Optional[Dict]:
    """获取单条跑步详情。"""
    r = session.get(
        RUN_LOG_API.format(sport_type=sport_type, run_id=run_id),
        headers=headers,
        timeout=10,
    )
    return r.json().get("data") if r.ok else None


# ═══════════════════════════════════════════════════════════════════════
# VDOT / 训练负荷计算
# ═══════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════
# 分段数据构建
# ═══════════════════════════════════════════════════════════════════════

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


def _build_segments(data: Dict, vc: VDCCalculator) -> List[Dict]:
    """从 crossKmPoints 构建分段。"""
    return _build_segments_from_cross_km(data, vc)


# ═══════════════════════════════════════════════════════════════════════
# 估算功率
# ═══════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════
# API 数据 -> 记录转换
# ═══════════════════════════════════════════════════════════════════════

def _build_record(stats: Dict, vc: VDCCalculator, detail: Optional[Dict] = None) -> Optional[Dict]:
    """将 stats + detail API 数据转为 running.json 记录。"""
    dur_s = _n(stats.get("duration"))
    dist_m = _f(stats.get("distance"))
    if dur_s <= 0 or dist_m <= 0:
        return None
    dist_km = round(dist_m / 1000.0, 2)

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

    # 名称
    name = (stats.get("name") or "").strip()
    if not name:
        dtype = (stats.get("dataType") or "").strip()
        type_short = (
            "户外跑步" if "outdoor" in dtype.lower()
            else "跑步机" if "indoor" in dtype.lower()
            else "跑步"
        )
        name = f"{_time_label(datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc).hour)}{type_short}"

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
        segs = _build_segments(detail, vc) or _build_segments(stats, vc)

    # 步频（从 detail 补充）
    step_freq = _n(_pick(stats, "averageStepFrequency"))
    if step_freq == 0 and detail:
        step_freq = _n(_pick(detail, "averageStepFrequency", "stepFrequency"))

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
        "type": stats.get("dataType", ""),
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
        "activityType": DATATYPE_NAME.get(stats.get("dataType", ""), "户外跑步"),
        "name": name,
        "stepFrequency": step_freq,
        "strideLength": round(stride, 2),
        "averagePower": avg_pwr,
        "maxPower": max_pwr,
        "vDOT": vdot,
        "trainingLoadScore": tl,
        "heartRateZone": hr_zone,
        "segments": segs,
    }


# ═══════════════════════════════════════════════════════════════════════
# 周期统计
# ═══════════════════════════════════════════════════════════════════════

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
        hr = r.get("averageHeartRate", 0)
        if hr > 0:
            hr_sum += hr
            hr_cnt += 1
        vd = r.get("vDOT", 0)
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
    """计算各周期统计（昨日/周/月/年/总）。"""
    now = datetime.now(TZ_SH).replace(tzinfo=None)
    yesterday = (datetime.now(TZ_SH) - timedelta(days=1)).date()
    y_start = datetime.combine(yesterday, datetime.min.time())
    y_end = datetime.combine(yesterday, datetime.max.time())

    monday = now - timedelta(days=now.isoweekday() - 1)
    w_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = now
    return {
        "yesterday": _period_stats(runs, y_start, y_end),
        "today": _period_stats(runs, today_start, today_end),
        "week": _period_stats(runs, w_start, now),
        "month": _period_stats(runs, datetime(now.year, now.month, 1), now),
        "year": _period_stats(runs, datetime(now.year, 1, 1), now),
        "total": _period_stats(runs, datetime.min, now),
    }


# ═══════════════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════════════

def fetch_runs(
    mobile: str,
    password: str = "",
    sport_type: str = "running",
    limit: Optional[int] = None,
    debug: bool = False,
) -> List[Dict]:
    """从 Keep API 拉取跑步数据。"""
    session, headers = _login(requests.Session(), mobile, password)
    ids = _fetch_run_ids(session, headers, sport_type, limit=limit)
    if not ids:
        logger.error("Keep API 未返回任何记录")
        sys.exit(1)

    logger.info("获取 %d 条跑步 ID", len(ids))

    vc = VDCCalculator()
    records = []
    for i, stat in enumerate(ids):
        if i > 0:
            time.sleep(0.5)
        detail = _fetch_detail(session, headers, sport_type, stat.get("id", ""))
        rec = _build_record(stat, vc, detail)
        if debug and rec:
            print("\n" + "=" * 60)
            print("【stats】")
            print(json.dumps(stat, ensure_ascii=False, indent=2, default=str))
            if detail:
                print("\n【detail】")
                print(json.dumps(detail, ensure_ascii=False, indent=2, default=str))
            print("\n【output】")
            print(json.dumps(rec, ensure_ascii=False, indent=2, default=str))
        if rec:
            records.append(rec)
        if (i + 1) % 20 == 0 and not debug:
            logger.info("已解析 %d/%d", i + 1, len(ids))

    logger.info("有效记录 %d 条", len(records))
    return records


def main():
    p = argparse.ArgumentParser(description="从 Keep API 拉取跑步数据并生成 running.json")
    p.add_argument("--output", default="../public/data/running.json")
    p.add_argument("--mobile", default=os.environ.get("KEEP_MOBILE", ""))
    p.add_argument("--password", default=os.environ.get("KEEP_PASSWORD", ""))
    p.add_argument("--limit", type=int, default=None, metavar="N")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    mobile = (args.mobile or "").strip()
    if not mobile:
        logger.error("未提供手机号：设置 KEEP_MOBILE 环境变量或使用 --mobile")
        sys.exit(1)
    password = (args.password or "").strip()
    if not password:
        logger.error("未提供密码：设置 KEEP_PASSWORD 环境变量或使用 --password")
        sys.exit(1)

    records = fetch_runs(mobile, password, limit=args.limit, debug=args.debug)
    if not records:
        logger.error("没有读取到任何记录")
        sys.exit(1)

    # 按时间倒序
    records.sort(key=lambda x: x["startTime"], reverse=True)

    output = {
        "statistics_time": datetime.now(TZ_SH).strftime("%Y-%m-%d %H:%M:%S"),
        "stats": _calculate_stats(records),
        "runs": records,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")
    logger.info("已保存到 %s", out_path)
    print("跑步数据已生成并保存。")


if __name__ == "__main__":
    main()

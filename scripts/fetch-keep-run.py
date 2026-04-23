#!/usr/bin/env python3
"""
从 Keep 读取跑步数据并生成与 Garmin 脚本兼容的 running.json，默认保存到当前脚本目录下的 data/running.json。
通过 Keep API 拉取数据，包含 VDOT 跑力与训练负荷、周期统计。
"""

import argparse
import base64
import json
import logging
import math
import os
import re
import time
import zlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

LOGIN_API = "https://api.gotokeep.com/v1.1/users/login"
RUN_DATA_API = "https://api.gotokeep.com/pd/v3/stats/detail?dateUnit=all&type={sport_type}&lastDate={last_date}"
RUN_LOG_API = "https://api.gotokeep.com/pd/v3/{sport_type}log/{run_id}"
HR_FRAME_THRESHOLD_DECISEC = 100
TIMESTAMP_THRESHOLD_DECISEC = 3_600_000

# running.json 内所有时间统一用上海时区显示
TZ_SHANGHAI = timezone(timedelta(hours=8))


def _decode_runmap_data(text: str, is_geo: bool = False) -> Any:
    """解码 Keep runmap 数据（来自 keep_sync.decode_runmap_data）。"""
    _bytes = base64.b64decode(text)
    key_b = base64.b64decode("NTZmZTU5OzgyZzpkODczYw==")
    iv_b = base64.b64decode("MjM0Njg5MjQzMjkyMDMwMA==")
    if is_geo:
        from Crypto.Cipher import AES
        cipher = AES.new(key_b, AES.MODE_CBC, iv_b)
        _bytes = cipher.decrypt(_bytes)
    raw = zlib.decompress(_bytes, 16 + zlib.MAX_WBITS)
    return json.loads(raw)


def _find_nearest_hr(
    hr_data_list: List[Dict],
    target_time: int,
    start_time_ms: int,
    threshold: int = HR_FRAME_THRESHOLD_DECISEC,
) -> Optional[int]:
    """找与 target_time 最近的心率点（来自 keep_sync.find_nearest_hr）。target_time/start_time 单位：分秒/毫秒。"""
    closest = None
    min_diff = float("inf")
    if target_time > TIMESTAMP_THRESHOLD_DECISEC:
        target_time = target_time - start_time_ms // 100
    for item in hr_data_list:
        ts = item.get("timestamp")
        if ts is None:
            continue
        diff = abs(ts - target_time)
        if diff <= threshold and diff < min_diff:
            closest = item
            min_diff = diff
    if closest:
        hr = closest.get("beatsPerMinute")
        if hr and hr > 0:
            return int(hr)
    return None


def _keep_login(session: Any, mobile: str, password: str) -> Optional[tuple]:
    """Keep 登录，返回 (session, headers) 或 None。"""
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    data = {"mobile": mobile, "password": password}
    r = session.post(LOGIN_API, headers=headers, data=data)
    if r.ok:
        token = r.json().get("data", {}).get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            return (session, headers)
    return None


def _keep_get_run_ids(session: Any, headers: Dict[str, str], sport_type: str) -> List[str]:
    """获取待下载的跑步 ID 列表。"""
    result = []
    last_date = 0
    while True:
        r = session.get(
            RUN_DATA_API.format(sport_type=sport_type, last_date=last_date),
            headers=headers,
        )
        if not r.ok:
            break
        data = r.json().get("data") or {}
        records = data.get("records") or []
        print(records)
        for i in records:
            logs = [j.get("stats") for j in (i.get("logs") or []) if isinstance(j, dict)]
            for k in logs:
                if isinstance(k, dict) and not k.get("isDoubtful"):
                    rid = k.get("id")
                    if rid:
                        result.append(rid)
        last_date = data.get("lastTimestamp") or 0
        time.sleep(1)
        if not last_date:
            break
    return result


def _keep_get_single_run(session: Any, headers: Dict[str, str], run_id: str, sport_type: str) -> Optional[Dict]:
    """拉取单条跑步详情。"""
    r = session.get(
        RUN_LOG_API.format(sport_type=sport_type, run_id=run_id),
        headers=headers,
    )
    if r.ok:
        return r.json()
    return None


# 心率区间配置（用于 VDOT/训练负荷）
MAX_HR = int(os.environ.get("MAX_HR", 180))
RESTING_HR = int(os.environ.get("RESTING_HR", 55))
# 体重 kg，用于本地功率估算（环境变量 RUNNER_WEIGHT_KG，默认 70）
RUNNER_WEIGHT_KG = float(os.environ.get("RUNNER_WEIGHT_KG", "70"))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class VDOTCalculator:
    """VDOT 跑力计算器，基于 Jack Daniels' Running Formula"""

    def __init__(self, max_hr: int = MAX_HR, resting_hr: int = RESTING_HR):
        self.max_hr = max_hr
        self.resting_hr = resting_hr
        self.hr_reserve = max_hr - resting_hr

    def get_hr_zone(self, avg_hr: float) -> int:
        """根据最大心率百分比获取心率区间 (1-5)"""
        if avg_hr <= 0:
            return 0
        hr_percent = (avg_hr / self.max_hr) * 100
        if hr_percent < 60:
            return 1
        if hr_percent < 70:
            return 2
        if hr_percent < 80:
            return 3
        if hr_percent < 90:
            return 4
        return 5

    def calculate_vdot(
        self,
        distance_meters: float,
        duration_seconds: float,
        avg_hr: Optional[float] = None,
    ) -> Optional[float]:
        if duration_seconds <= 0 or distance_meters <= 0:
            return None
        duration_minutes = duration_seconds / 60
        velocity_m_per_min = distance_meters / duration_minutes
        if velocity_m_per_min <= 0:
            return None
        vo2 = -4.60 + 0.182258 * velocity_m_per_min + 0.000104 * (velocity_m_per_min**2)
        t = duration_minutes
        percent_vo2max = (
            0.8
            + 0.1894393 * math.exp(-0.012778 * t)
            + 0.2989558 * math.exp(-0.1932605 * t)
        )
        if percent_vo2max <= 0 or percent_vo2max > 1.0:
            return None
        vdot = vo2 / percent_vo2max
        if avg_hr and avg_hr > 0:
            hr_zone = self.get_hr_zone(avg_hr)
            zone_multipliers = {1: 0.97, 2: 0.99, 3: 1.00, 4: 1.00, 5: 1.00}
            vdot *= zone_multipliers.get(hr_zone, 1.0)
        if vdot < 20 or vdot > 100:
            return None
        return round(vdot, 1)

    def calculate_training_load(
        self, duration_seconds: float, avg_hr: Optional[float] = None
    ) -> int:
        if duration_seconds <= 0:
            return 0
        duration_hours = duration_seconds / 3600
        base_load = duration_hours * 100
        if avg_hr and avg_hr > 0:
            hr_zone = self.get_hr_zone(avg_hr)
            zone_factors = {1: 0.6, 2: 0.8, 3: 1.0, 4: 1.3, 5: 1.5}
            base_load *= zone_factors.get(hr_zone, 1.0)
        return round(base_load)


def parse_pace_cn(pace_str: str) -> str:
    """将 'X分Y秒/公里' 转为 "X'YY\"" 格式"""
    if not pace_str or pace_str == "0":
        return "0'00\""
    m = re.match(r"(\d+)\s*分\s*(\d+)\s*秒\s*/\s*公里", pace_str)
    if m:
        return f"{int(m.group(1))}'{int(m.group(2)):02d}\""
    return pace_str


def parse_duration_to_seconds(duration_str: str) -> int:
    """'HH:MM:SS' -> 秒"""
    if not duration_str:
        return 0
    parts = duration_str.strip().split(":")
    if len(parts) == 3:
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        return h * 3600 + m * 60 + s
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    if len(parts) == 1:
        return int(parts[0])
    return 0


def duration_seconds_to_str(seconds: int) -> str:
    """秒 -> 'X小时Y分钟' 或 'Y分钟'"""
    if seconds <= 0:
        return "0分钟"
    minutes = int(seconds // 60)
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}小时{mins}分钟"
    return f"{mins}分钟"


def parse_location_route(location_country: str) -> str:
    """从 location_country 的 dict 字符串中提取省/市/区作为路线名"""
    if not location_country or not location_country.strip():
        return "未知路线"
    s = location_country.strip()
    if s.startswith("{"):
        try:
            # 兼容单引号 Python dict
            s = s.replace("'", '"')
            obj = json.loads(s)
            parts = [
                obj.get("province"),
                obj.get("city"),
                obj.get("district"),
            ]
            name = "".join(p for p in parts if p)
            return name or "未知路线"
        except Exception:
            pass
    return location_country[:50] if len(s) > 50 else s


def _safe_number(val: Any, kind: str = "int") -> Optional[float]:
    """安全转为 int/float，无效则返回 None。"""
    if val is None:
        return None
    try:
        return int(val) if kind == "int" else float(val)
    except (TypeError, ValueError):
        return None


def _estimate_running_power(
    distance_m: float,
    duration_sec: float,
    elevation_gain: float = 0,
    cross_km_points: Optional[List[Dict[str, Any]]] = None,
    weight_kg: Optional[float] = None,
) -> tuple[Optional[int], Optional[int]]:
    """本地估算跑步功率（瓦特）。

    公式（简化）：平路功率 ≈ 1.03 * 体重 * 速度(m/s)；爬升功率 = 体重 * 9.81 * (爬升米/时长秒)。
    平均功率 = 平路 + 爬升；最大功率：若有 crossKmPoints 取最快一公里的配速估算，否则与平均相同。
    体重可通过环境变量 RUNNER_WEIGHT_KG 设置，默认 70 kg。
    """
    if duration_sec <= 0 or distance_m <= 0:
        return None, None
    m = weight_kg if weight_kg is not None and weight_kg > 0 else RUNNER_WEIGHT_KG
    v_avg = distance_m / duration_sec  # m/s
    # 平路功率近似 1.03 * m * v（常见经验系数）
    p_flat = 1.03 * m * v_avg
    p_elev = 0.0
    if elevation_gain and elevation_gain > 0:
        p_elev = m * 9.81 * (float(elevation_gain) / duration_sec)
    avg_power = int(round(p_flat + p_elev))
    if avg_power <= 0:
        avg_power = None

    max_power: Optional[int] = None
    if cross_km_points and isinstance(cross_km_points, list):
        km_paces_sec = []
        for pt in cross_km_points:
            if not isinstance(pt, dict):
                continue
            pace_sec = _safe_number(
                pt.get("kmPace") or pt.get("pace") or pt.get("paceSeconds"), "float"
            )
            if pace_sec and pace_sec > 0:
                km_paces_sec.append(pace_sec)
        if km_paces_sec:
            min_pace_sec = min(km_paces_sec)
            v_max_km = 1000.0 / min_pace_sec  # 最快一公里对应的速度 m/s
            max_power = int(round(1.03 * m * v_max_km + p_elev))
    if max_power is None or max_power <= 0:
        max_power = avg_power

    return avg_power, max_power


# dataType -> 活动类型中文（与 keep_sync 一致）
KEEP_DATATYPE_TO_ACTIVITY = {
    "outdoorRunning": "室外跑步",
    "indoorRunning": "跑步机",
    "outdoorWalking": "步行",
    "outdoorCycling": "户外骑行",
    "mountaineering": "越野",
}


def _pace_to_display(pace_val: Any) -> str:
    """将配速转为 "X'YY\"" 格式。pace_val 可为秒数（int/float）或中文配速字符串。"""
    if pace_val is None:
        return "0'00\""
    if isinstance(pace_val, (int, float)):
        sec = int(round(float(pace_val)))
        if sec <= 0:
            return "0'00\""
        return f"{sec // 60}'{sec % 60:02d}\""
    s = str(pace_val).strip()
    if not s:
        return "0'00\""
    if "'" in s or '"' in s:
        return s
    return parse_pace_cn(s)


def _build_segments_from_cross_km_points(
    api_data: Dict[str, Any], vdot_calculator: VDOTCalculator
) -> List[Dict[str, Any]]:
    """从 Keep API 的 crossKmPoints 构建每公里分段，与 reference running.json 的 segments 格式一致。"""
    points = api_data.get("crossKmPoints")
    if not points or not isinstance(points, list):
        return []
    segments_out = []
    for i, pt in enumerate(points):
        if not isinstance(pt, dict):
            continue
        km = pt.get("km") or pt.get("index") or (i + 1)
        km = int(km) if km is not None else (i + 1)
        pace_val = pt.get("kmPace")
        pace_str = _pace_to_display(pace_val)
        hr_val = pt.get("averageHeartRate")
        heart_rate = int(hr_val) if hr_val is not None else 0
        hr_zone = vdot_calculator.get_hr_zone(heart_rate) if heart_rate else 0
        cadence = _safe_number(pt.get("stepFrequency"), "int")
        cadence = int(cadence) if cadence is not None else 0
        segments_out.append(
            {
                "km": km,
                "pace": pace_str,
                "gap": pace_str,
                "heart_rate": heart_rate,
                "hr_zone": hr_zone,
                "cadence": cadence,
            }
        )
    return segments_out


def _build_segments_from_keep_api(
    api_data: Dict[str, Any], vdot_calculator: VDOTCalculator
) -> List[Dict[str, Any]]:
    """从 Keep API 单条记录构建每公里分段：优先 crossKmPoints，否则用 geoPoints + 心率计算。"""
    segments = _build_segments_from_cross_km_points(api_data, vdot_calculator)
    if segments:
        return segments

    geo_points_raw = api_data.get("geoPoints")
    if not geo_points_raw:
        return []
    try:
        from haversine import haversine
    except ImportError as e:
        logger.debug("无法加载 haversine，跳过 segments: %s", e)
        return []

    try:
        points = _decode_runmap_data(geo_points_raw, True)
    except Exception as e:
        logger.debug("解码 geoPoints 失败，跳过 segments: %s", e)
        return []
    if not points or len(points) < 2:
        return []

    start_time_ms = int(api_data.get("startTime") or 0)
    decoded_hr_data = []
    heart_rate_data = (api_data.get("heartRate") or {}).get("heartRates")
    if heart_rate_data:
        try:
            decoded_hr_data = _decode_runmap_data(heart_rate_data)
        except Exception:
            pass

    for p in points:
        ts = p.get("timestamp") or p.get("unixTimestamp") or 0
        p["_ts"] = int(ts)
        if decoded_hr_data:
            hr = _find_nearest_hr(decoded_hr_data, p["_ts"], start_time_ms)
            p["_hr"] = hr
        else:
            p["_hr"] = None

    cum_dist_m = 0.0
    dist_series = [0.0]
    for i in range(1, len(points)):
        a, b = points[i - 1], points[i]
        lat_a, lon_a = a.get("latitude"), a.get("longitude")
        lat_b, lon_b = b.get("latitude"), b.get("longitude")
        if None in (lat_a, lon_a, lat_b, lon_b):
            dist_series.append(cum_dist_m)
            continue
        d_km = haversine((lat_a, lon_a), (lat_b, lon_b))
        cum_dist_m += d_km * 1000
        dist_series.append(cum_dist_m)

    total_m = dist_series[-1] if dist_series else 0
    if total_m < 100:
        return []

    segments_out = []
    seg_start_idx = 0
    seg_start_dist = 0.0
    seg_start_ts = points[0].get("_ts", 0)
    k = 1
    while True:
        target_m = k * 1000.0
        if target_m > total_m:
            break
        seg_end_idx = None
        for i in range(seg_start_idx + 1, len(points)):
            if dist_series[i] >= target_m:
                seg_end_idx = i
                break
        if seg_end_idx is None:
            break
        seg_end_dist = dist_series[seg_end_idx]
        seg_end_ts = points[seg_end_idx].get("_ts", seg_start_ts)
        seg_dist_m = seg_end_dist - seg_start_dist
        seg_duration_sec = (
            (seg_end_ts - seg_start_ts) / 10.0 if (seg_end_ts - seg_start_ts) > 0 else 1
        )
        if seg_duration_sec <= 0:
            seg_duration_sec = 1
        seg_pace_sec_per_km = (
            (seg_duration_sec / seg_dist_m) * 1000 if seg_dist_m > 0 else 0
        )
        pace_min = int(seg_pace_sec_per_km // 60)
        pace_sec = int(seg_pace_sec_per_km % 60)
        pace_str = f"{pace_min}'{pace_sec:02d}\""

        hrs = [
            points[j].get("_hr")
            for j in range(seg_start_idx, seg_end_idx + 1)
            if points[j].get("_hr") is not None
        ]
        avg_hr = int(round(sum(hrs) / len(hrs))) if hrs else 0
        hr_zone = vdot_calculator.get_hr_zone(avg_hr) if avg_hr else 0

        segments_out.append(
            {
                "km": k,
                "pace": pace_str,
                "gap": pace_str,
                "heart_rate": avg_hr,
                "hr_zone": hr_zone,
                "cadence": 0,
            }
        )
        seg_start_idx = seg_end_idx
        seg_start_dist = seg_end_dist
        seg_start_ts = seg_end_ts
        k += 1

    return segments_out


def _get_time_of_day(hour: int) -> str:
    """根据小时数返回时段名称：凌晨 (0-5)/清晨 (6-8)/上午 (9-11)/中午 (12-13)/下午 (14-17)/傍晚 (18-19)/夜晚 (20-23)"""
    if 0 <= hour <= 5:
        return "凌晨"
    elif 6 <= hour <= 8:
        return "清晨"
    elif 9 <= hour <= 11:
        return "上午"
    elif 12 <= hour <= 13:
        return "中午"
    elif 14 <= hour <= 17:
        return "下午"
    elif 18 <= hour <= 19:
        return "傍晚"
    else:  # 20-23
        return "夜晚"


def _keep_api_run_to_row(
    api_data: Dict[str, Any],
    vdot_calculator: Optional[VDOTCalculator] = None,
) -> Optional[Dict[str, Any]]:
    """将 Keep API 单条跑步详情转为行字典，便于复用 format_running_data。
    能拿到的 API 字段：distance, duration, startTime/endTime, heartRate(平均/最大),
    region, timezone, dataType, calorie；步频/步幅/功率/爬升等若接口有则一并提取。
    """
    try:
        duration_sec = int(api_data.get("duration") or 0)
        distance_m = float(api_data.get("distance") or 0)
    except (TypeError, ValueError):
        return None
    if duration_sec <= 0 or distance_m <= 0:
        return None

    # 配速：秒/公里 -> "X分Y秒/公里"
    sec_per_km = duration_sec / (distance_m / 1000)
    pace_min = int(sec_per_km // 60)
    pace_sec = int(sec_per_km % 60)
    average_speed = f"{pace_min}分{pace_sec}秒/公里"

    # 时长 "H:MM:SS"
    h, remainder = divmod(duration_sec, 3600)
    m, s = divmod(remainder, 60)
    moving_time = f"{h}:{m:02d}:{s:02d}"

    # 本地开始时间：统一转为上海时区写入 running.json（run["date"]、周期统计一致）
    start_time_ms = api_data.get("startTime") or 0
    start_date_utc = datetime.fromtimestamp(
        start_time_ms / 1000, tz=timezone.utc
    )
    start_date_local = start_date_utc.astimezone(TZ_SHANGHAI).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    heart_rate_data = api_data.get("heartRate") or {}
    avg_hr = heart_rate_data.get("averageHeartRate")
    if avg_hr is not None and avg_hr < 0:
        avg_hr = None
    average_heartrate = int(avg_hr) if avg_hr else None
    max_heart_rate = _safe_number(
        heart_rate_data.get("maxHeartRate") or heart_rate_data.get("max"),
        "int",
    )

    region = api_data.get("region") or ""
    if isinstance(region, dict):
        region = json.dumps(region, ensure_ascii=False)
    location_country = str(region) if region else ""

    # 卡路里
    calorie = api_data.get("calorie") or api_data.get("calories")
    calories = _safe_number(calorie, "int")

    # 活动类型：dataType -> 室外跑步/跑步机 等
    data_type = (api_data.get("dataType") or "").strip()
    activity_type = KEEP_DATATYPE_TO_ACTIVITY.get(
        data_type, "室外跑步" if "run" in data_type.lower() else "跑步机"
    )

    # 爬升：若 API 顶层有则用（无则 0；精确爬升需解码 geoPoints 算高程）
    elevation_gain = _safe_number(
        api_data.get("accumulativeUpliftedHeight"),
        "float",
    )
    if elevation_gain is None:
        elevation_gain = 0

    # 步频（平均步频）：从 averageStepFrequency 获取
    cadence = _safe_number(
        api_data.get("averageStepFrequency"),
        "int",
    )
    # 步幅：由 totalSteps 与 distance 计算（距离/步数），单位米
    total_steps = _safe_number(api_data.get("totalSteps"), "float")
    if total_steps and total_steps > 0 and distance_m > 0:
        stride_length = distance_m / total_steps
    else:
        stride_length = _safe_number(
            api_data.get("strideLength")
            or api_data.get("avgStrideLength")
            or api_data.get("averageStrideLength"),
            "float",
        )
    if stride_length is None:
        stride_length = 0
    stride_length = round(float(stride_length), 2)
    # 平均功率、最大功率：优先用 API，缺省时用本地估算
    avg_power = _safe_number(
        api_data.get("avgPower") or api_data.get("averagePower"), "int"
    )
    max_power = _safe_number(
        api_data.get("maxPower") or api_data.get("peakPower"), "int"
    )
    if avg_power is None and max_power is None:
        est_avg, est_max = _estimate_running_power(
            distance_m,
            duration_sec,
            elevation_gain=elevation_gain or 0,
            cross_km_points=(
                api_data.get("crossKmPoints")
                if isinstance(api_data.get("crossKmPoints"), list)
                else None
            ),
        )
        avg_power = est_avg
        max_power = est_max
    if avg_power is None:
        avg_power = 0
    if max_power is None:
        max_power = 0

    # 天气：从 weatherInfo 取（可为字符串或对象 description/weather/condition，可选温度）
    weather_str = ""
    weather_info = api_data.get("weatherInfo")
    if weather_info is not None:
        if isinstance(weather_info, str) and weather_info.strip():
            weather_str = weather_info.strip()
        elif isinstance(weather_info, dict):
            # weatherTypeIcon
            temperature = weather_info.get("temperature")
            if temperature is not None and str(temperature).strip():
                weather_str = f"{temperature}".strip()

    # workout_name: 根据开始时间的时段 + data_type 生成，如"清晨室外跑步"、"夜晚跑步机"
    start_hour = start_date_utc.hour
    time_of_day = _get_time_of_day(start_hour)
    # data_type 映射为简短类型名
    type_short_name = "室外跑步" if "outdoor" in data_type.lower() else "跑步机" if "indoor" in data_type.lower() else "跑步"
    workout_name = f"{time_of_day}{type_short_name}"

    row = {
        "distance": distance_m,
        "moving_time": moving_time,
        "elapsed_time": moving_time,
        "start_date_local": start_date_local,
        "start_date": datetime.fromtimestamp(
            start_time_ms / 1000, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "average_speed": average_speed,
        "average_heartrate": average_heartrate,
        "location_country": location_country,
        "elevation_gain": elevation_gain,
        "name": workout_name,
        "calories": calories,
        "max_heart_rate": max_heart_rate,
        "activity_type": activity_type,
        "cadence": cadence,
        "stride_length": stride_length,
        "avg_power": avg_power,
        "max_power": max_power,
        "weather": weather_str,
    }
    if vdot_calculator and (api_data.get("crossKmPoints") or api_data.get("geoPoints")):
        row["segments"] = _build_segments_from_keep_api(api_data, vdot_calculator)
    else:
        row["segments"] = []
    return row


def _debug_json(obj: Any) -> str:
    """序列化为可打印的 JSON，支持 datetime 等类型。"""

    def _default(o: Any) -> Any:
        if hasattr(o, "isoformat"):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    return json.dumps(obj, ensure_ascii=False, indent=2, default=_default)


def fetch_keep_runs_via_api(
    mobile: str,
    password: str,
    sport_type: str = "running",
    limit: Optional[int] = None,
    debug: bool = False,
) -> List[Dict[str, Any]]:
    """通过 Keep API 拉取跑步列表并逐条拉取详情，返回行格式列表。"""
    import requests

    session = requests.Session()
    login_result = _keep_login(session, mobile, password)
    if login_result is None:
        logger.error("Keep 登录失败，请检查手机号与密码")
        return []
    session, headers = login_result

    all_run_ids = _keep_get_run_ids(session, headers, sport_type)
    if limit is not None and limit > 0:
        run_ids = all_run_ids[:limit]
        logger.info(
            "Keep API 共 %d 条跑步 ID，仅拉取前 %d 条（调试）", len(all_run_ids), limit
        )
    else:
        run_ids = all_run_ids
        logger.info("Keep API 共获取 %d 条跑步 ID", len(run_ids))

    vdot_calculator = VDOTCalculator()
    rows = []
    for i, run_id in enumerate(run_ids):
        try:
            raw = _keep_get_single_run(session, headers, run_id, sport_type)
            if not raw or "data" not in raw:
                continue
            api_data = raw["data"]
            row = _keep_api_run_to_row(api_data, vdot_calculator)
            if debug and row:
                print("\n" + "=" * 60 + "\n【Keep API 原始 data】\n" + "=" * 60)
                print(_debug_json(api_data))
                print("\n" + "=" * 60 + "\n【转换后 row】\n" + "=" * 60)
                print(_debug_json(row))
                print()
            if row:
                rows.append(row)
            if (i + 1) % 20 == 0 and not debug:
                logger.info("已拉取 %d/%d 条", i + 1, len(run_ids))
            time.sleep(0.3)
        except Exception as e:
            logger.warning("拉取 run_id=%s 失败: %s", run_id, e)
    logger.info("从 Keep API 解析出 %d 条有效记录", len(rows))
    return rows


def format_running_data(
    rows: List[Dict[str, Any]],
    vdot_calculator: Optional[VDOTCalculator] = None,
) -> Dict[str, Any]:
    """将行列表格式化为新的 stats + runs 结构。"""
    if vdot_calculator is None:
        vdot_calculator = VDOTCalculator()

    stats = {
        "total_runs": 0,
        "total_distance": 0,
        "total_duration": "--",
        "avg_pace": "0'00\"",
        "longest_run": 0,
        "avg_vdot": 0,
        "total_training_load": 0,
        "period_stats": {},
    }
    if vdot_calculator is None:
        vdot_calculator = VDOTCalculator()

    total_seconds = 0
    total_vdot = 0
    vdot_count = 0
    formatted_runs = []

    for row in rows:
        try:
            distance_m = float(row.get("distance", 0) or 0)
            distance_km = distance_m / 1000.0
        except (TypeError, ValueError):
            distance_km = 0
        if distance_km <= 0:
            continue

        moving_time = row.get("moving_time", "") or row.get("elapsed_time", "")
        duration_seconds = parse_duration_to_seconds(moving_time)
        if duration_seconds <= 0:
            continue

        pace_str_raw = row.get("average_speed", "") or ""
        pace = parse_pace_cn(pace_str_raw)
        duration_str = duration_seconds_to_str(duration_seconds)

        try:
            avg_hr = float(row.get("average_heartrate", 0) or 0)
        except (TypeError, ValueError):
            avg_hr = 0

        try:
            elevation_gain = float(row.get("elevation_gain", 0) or 0)
        except (TypeError, ValueError):
            elevation_gain = 0

        start_local = row.get("start_date_local", "").strip()
        if not start_local:
            start_local = row.get("start_date", "").strip()

        vdot = vdot_calculator.calculate_vdot(
            distance_m, duration_seconds, avg_hr if avg_hr > 0 else None
        )
        training_load = vdot_calculator.calculate_training_load(
            duration_seconds, avg_hr if avg_hr > 0 else None
        )
        hr_zone = vdot_calculator.get_hr_zone(avg_hr) if avg_hr and avg_hr > 0 else 0

        route = parse_location_route(row.get("location_country", "") or "")
        name = (row.get("name") or "").strip() or ""

        # 卡路里：Keep API 的 calorie 字段
        raw_cal = row.get("calories") or row.get("calorie")
        try:
            calories = int(raw_cal) if raw_cal is not None else 0
        except (TypeError, ValueError):
            calories = 0

        # 以下字段 Keep API 若有则从 row 带入，否则默认 0 或占位
        def _row_num(key: str, default: float = 0) -> float:
            v = row.get(key)
            if v is None:
                return default
            try:
                return (
                    int(v) if isinstance(v, (int, float)) and v == int(v) else float(v)
                )
            except (TypeError, ValueError):
                return default

        max_hr = _row_num("max_heart_rate", 0)
        cadence = _row_num("cadence", 0)
        stride_length = _row_num("stride_length", 0)
        avg_power = _row_num("avg_power", 0)
        max_power = _row_num("max_power", 0)
        activity_type = (row.get("activity_type") or "").strip() or "室外跑步"

        run_data = {
            "date": start_local,
            "distance": round(distance_km * 100 / 100,2),
            "duration": duration_str,
            "pace": pace,
            "heart_rate": round(avg_hr, 1) if avg_hr else 0,
            "max_heart_rate": int(max_hr),
            "cadence": int(cadence),
            "stride_length": round(stride_length, 2) if stride_length else 0,
            "avg_power": int(avg_power),
            "max_power": int(max_power),
            "calories": calories,
            "elevation_gain": round(elevation_gain, 1),
            "route": route,
            "weather": row.get("weather", "未知天气"),
            "activity_type": activity_type,
            "workout_name": name,
            "vdot": vdot,
            "training_load": training_load,
            "hr_zone": hr_zone,
            "segments": row.get("segments", []),
        }
        formatted_runs.append(run_data)

    # 按日期倒序
    formatted_runs.sort(key=lambda x: x["date"], reverse=True)

    # 周期统计
    period_stats = _calculate_period_stats(formatted_runs, vdot_calculator)
    return {
        "statistics_time": datetime.now(TZ_SHANGHAI).strftime("%Y-%m-%d %H:%M:%S"),
        "stats": period_stats,
        "runs": formatted_runs,
    }


def _calculate_period_stats(
    runs: List[Dict[str, Any]],
    vdot_calculator: VDOTCalculator,
) -> Dict[str, Any]:
    now = datetime.now(TZ_SHANGHAI)
    # 昨日：上海时间昨天 00:00 至昨天 23:59:59
    yesterday_date = (now - timedelta(days=1)).date()
    yesterday_start = datetime.combine(yesterday_date, datetime.min.time())
    yesterday_end = datetime.combine(yesterday_date, datetime.max.time())
    # 当前周：周一 00:00 至今天（ISO 周：周一为第 1 天，上海时区）
    days_since_monday = now.isoweekday() - 1
    week_start = (now - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # 当月：本月 1 日 00:00 至今天
    month_start = datetime(now.year, now.month, 1)
    # 当年：1 月 1 日 00:00 至今天
    year_start = datetime(now.year, 1, 1)
    # 使用 naive datetime 与 run["date"] 解析出的日期比较
    now_naive = now.replace(tzinfo=None)
    week_start_naive = week_start.replace(tzinfo=None)
    month_start_naive = month_start.replace(tzinfo=None)
    year_start_naive = year_start.replace(tzinfo=None)
    period_ranges = {
        "yesterday": {"start": yesterday_start, "end": yesterday_end},
        "week": {"start": week_start_naive, "end": now_naive},
        "month": {"start": month_start_naive, "end": now_naive},
        "year": {"start": year_start_naive, "end": now_naive},
        "total": {"start": datetime.min, "end": now_naive},
    }
    result = {}
    for period_name, rng in period_ranges.items():
        result[period_name] = _stats_for_period(
            runs, rng["start"], rng["end"], vdot_calculator
        )
    return result


def _stats_for_period(
    runs: List[Dict[str, Any]],
    start_date: datetime,
    end_date: datetime,
    vdot_calculator: VDOTCalculator,
) -> Dict[str, Any]:
    """按日期区间筛选 runs。run["date"] 为本地时间字符串（与 TZ_SHANGHAI 一致），此处只比较日期部分。"""
    period_runs = []
    for run in runs:
        try:
            dt_str = run["date"].split(" ")[0]
            run_date = datetime.strptime(dt_str, "%Y-%m-%d")  # naive，仅日期 00:00:00
            if start_date <= run_date <= end_date:
                period_runs.append(run)
        except (ValueError, IndexError):
            continue
    if not period_runs:
        return {
            "total_activities": 0,
            "total_distance": 0,
            "total_duration_hours": 0,
            "avg_pace": "--",
            "avg_heart_rate": None,
            "avg_vdot": None,
            "best_vdot": None,
            "total_training_load": 0,
            "total_calories": 0,
        }
    total_distance = sum(r["distance"] for r in period_runs)
    total_activities = len(period_runs)
    total_training_load = sum(r.get("training_load", 0) for r in period_runs)
    longest_run = max(r["distance"] for r in period_runs)
    total_calories = sum(r.get("calories", 0) for r in period_runs)
    total_seconds = 0
    total_hr = 0
    hr_count = 0
    total_vdot = 0
    vdot_count = 0
    best_vdot = 0
    for run in period_runs:
        duration_str = run["duration"]
        parts = duration_str.replace("小时", ":").replace("分钟", "").split(":")
        if len(parts) == 2:
            total_seconds += int(parts[0]) * 3600 + int(parts[1]) * 60
        else:
            total_seconds += int(parts[0]) * 60
        if run.get("heart_rate") and run["heart_rate"] > 0:
            total_hr += run["heart_rate"]
            hr_count += 1
        if run.get("vdot") and run["vdot"] > 0:
            total_vdot += run["vdot"]
            vdot_count += 1
            best_vdot = max(best_vdot, run["vdot"])
    if total_distance > 0:
        avg_pace_sec = total_seconds / total_distance
        avg_pace = f"{int(avg_pace_sec // 60)}'{int(avg_pace_sec % 60):02d}\""
    else:
        avg_pace = "--"
    total_duration_hours = round(total_seconds / 3600, 1)
    return {
        "total_activities": total_activities,
        "total_distance": int(total_distance * 100) / 100,
        "total_duration_hours": total_duration_hours,
        "avg_pace": avg_pace,
        "avg_heart_rate": round(total_hr / hr_count) if hr_count > 0 else None,
        "avg_vdot": round(total_vdot / vdot_count, 1) if vdot_count > 0 else None,
        "best_vdot": round(best_vdot, 1) if vdot_count > 0 else None,
        "longest_run": longest_run,
        "total_training_load": total_training_load,
        "total_calories": total_calories,
    }


def save_running_json(
    data: Dict[str, Any],
    output_path: str,
    merge: bool = False,
    vdot_calculator: Optional[VDOTCalculator] = None,
) -> bool:
    """保存到 JSON；merge=True 时与已有 running.json 按日期合并并重算 stats。"""
    if vdot_calculator is None:
        vdot_calculator = VDOTCalculator()
    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        if merge and os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                data = _merge_running_data(existing, data, vdot_calculator)
                logger.info("已与现有数据合并，共 %d 条跑步记录", len(data["runs"]))
            except Exception as e:
                logger.warning("合并现有数据失败，将覆盖: %s", e)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        logger.info("已保存到 %s", output_path)
        return True
    except Exception as e:
        logger.error("保存失败: %s", e)
        return False


def _merge_running_data(
    existing: Dict[str, Any],
    new_data: Dict[str, Any],
    vdot_calculator: VDOTCalculator,
) -> Dict[str, Any]:
    by_date = {r["date"]: r for r in existing.get("runs", [])}
    for run in new_data.get("runs", []):
        if run["date"] in by_date:
            for k, v in run.items():
                if k != "date" and (v or v == 0):
                    by_date[run["date"]][k] = v
        else:
            by_date[run["date"]] = run
    existing["runs"] = sorted(by_date.values(), key=lambda x: x["date"], reverse=True)
    existing["stats"] = _recalculate_stats(existing["runs"], vdot_calculator)
    return existing


def _recalculate_stats(
    runs: List[Dict[str, Any]], vdot_calculator: VDOTCalculator
) -> Dict[str, Any]:
    stats = {
        "total_runs": len(runs),
        "total_distance": 0,
        "total_duration": "0小时0分钟",
        "avg_pace": "0'00\"",
        "longest_run": 0,
        "avg_vdot": 0,
        "total_training_load": 0,
        "period_stats": {},
    }
    total_seconds = 0
    total_vdot = 0
    vdot_count = 0
    for run in runs:
        stats["total_distance"] += run["distance"]
        stats["longest_run"] = max(stats["longest_run"], run["distance"])
        stats["total_training_load"] += run.get("training_load", 0)
        if run.get("vdot"):
            total_vdot += run["vdot"]
            vdot_count += 1
        parts = run["duration"].replace("小时", ":").replace("分钟", "").split(":")
        if len(parts) == 2:
            total_seconds += int(parts[0]) * 3600 + int(parts[1]) * 60
        else:
            total_seconds += int(parts[0]) * 60
    if stats["total_distance"] > 0:
        avg_sec = total_seconds / stats["total_distance"]
        stats["avg_pace"] = f"{int(avg_sec // 60)}'{int(avg_sec % 60):02d}\""
    if vdot_count > 0:
        stats["avg_vdot"] = round(total_vdot / vdot_count, 1)
    stats["total_duration"] = duration_seconds_to_str(total_seconds)
    stats["total_distance"] = int(stats["total_distance"] * 100) / 100
    stats["longest_run"] = stats["longest_run"]
    stats["period_stats"] = _calculate_period_stats(runs, vdot_calculator)
    stats["statistics_time"] = datetime.now(TZ_SHANGHAI).strftime("%Y-%m-%d %H:%M:%S")
    return stats


def parse_args():
    p = argparse.ArgumentParser(
        description="从 Keep API 拉取跑步数据并生成 running.json"
    )
    p.add_argument(
        "--output",
        default="../public/data/running.json",
        help="相对脚本目录的输出路径 (默认: ../public/data/running.json)",
    )
    p.add_argument(
        "--mobile",
        default=os.environ.get("KEEP_MOBILE", ""),
        help="Keep 登录手机号（环境变量 KEEP_MOBILE）",
    )
    p.add_argument(
        "--password",
        default=os.environ.get("KEEP_PASSWORD", ""),
        help="Keep 登录密码（环境变量 KEEP_PASSWORD）",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="仅拉取前 N 条记录（调试用，如 --limit 1）",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="打印每条记录的 Keep API 原始 data 与转换后的 row，便于对比",
    )
    return p.parse_args()


def main():
    args = parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, args.output)

    mobile = (args.mobile or "").strip()
    password = (args.password or "").strip()
    if not mobile or not password:
        print(
            "请提供 --mobile 和 --password，或设置环境变量 KEEP_MOBILE、KEEP_PASSWORD"
        )
        return
    vdot_calculator = VDOTCalculator()
    rows = fetch_keep_runs_via_api(mobile, password, limit=args.limit, debug=args.debug)

    if not rows:
        print("没有读取到任何记录。")
        return

    data = format_running_data(rows, vdot_calculator)
    if save_running_json(
        data, output_path, merge=False, vdot_calculator=vdot_calculator
    ):
        stats = data["stats"]
        total = stats.get("total", {})
        print("跑步数据已生成并保存。")
        print(f"  跑步次数：{total.get('total_activities', 0)}")
        print(f"  总距离：{total.get('total_distance', 0)} 公里")
        print(f"  最长距离：{total.get('longest_run', 0)} 公里")
        print(f"  总时长：{total.get('total_duration_hours', 0)} 小时")
        print(f"  平均配速：{total.get('avg_pace', '--')}")
        print(f"  昨日距离：{(stats.get('yesterday') or {}).get('total_distance', 0)} 公里")
        print(f"  本周距离：{(stats.get('week') or {}).get('total_distance', 0)} 公里")
        print(f"  本月距离：{(stats.get('month') or {}).get('total_distance', 0)} 公里")
        print(f"  本年距离：{(stats.get('year') or {}).get('total_distance', 0)} 公里")
        if total.get("avg_vdot"):
            print(f"  平均 VDOT: {total['avg_vdot']}")
        if total.get("total_training_load"):
            print(f"  总训练负荷：{total['total_training_load']}")
    else:
        print("保存失败。")


if __name__ == "__main__":
    main()

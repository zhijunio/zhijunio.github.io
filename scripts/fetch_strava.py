"""
从 Strava 拉取运动记录，写入 scripts/assets/strava_activities.json、strava_stats.json。

凭证：STRAVA_CLIENT_ID、STRAVA_CLIENT_SECRET、STRAVA_REFRESH_TOKEN
可选：SYNC_LIMIT、SYNC_USE_PROXY、SYNC_HTTP(S)_PROXY、AI 相关环境变量
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from activity_sync_common import (  # noqa: E402
    SyncPaths,
    assets_path,
    cap_sync_batch,
    create_sync_http_session,
    cutoff_timestamp,
    finalize_sync,
    format_strava_activity,
    ingest_records,
    known_run_ids,
    load_activities,
    log,
    log_sync_startup,
    parse_positive_int,
    parse_time,
    request_with_retries,
    set_log_scope,
    sync_proxy_hint,
)

PATHS = SyncPaths(
    activities=assets_path("strava_activities.json"),
    stats=assets_path("strava_stats.json"),
)

SYNC_LIMIT = parse_positive_int(os.getenv("SYNC_LIMIT"))

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
TOKEN_URL = "https://www.strava.com/oauth/token"


def _require_credentials() -> None:
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        log.err("缺少 Strava 凭证 (CLIENT_ID / SECRET / REFRESH_TOKEN)")
        sys.exit(1)


class StravaClient:
    def __init__(self) -> None:
        self._token: str | None = None
        self._session = create_sync_http_session("Strava")

    def access_token(self) -> str | None:
        if self._token:
            return self._token
        log.info("刷新 Strava Token…")
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
            "f": "json",
        }
        try:
            response = request_with_retries(
                self._session, "POST", TOKEN_URL, data=payload, verify=True, timeout=30
            )
            if response.status_code == 200:
                self._token = response.json().get("access_token")
                return self._token
            log.err(f"认证失败: {response.text[:120]}")
        except Exception as exc:
            log.err(f"认证异常: {exc}")
            log.warn(sync_proxy_hint())
        return None

    def fetch_activities(
        self,
        after_timestamp: int | None,
        *,
        known_ids: set[str],
        max_new: int | None,
    ) -> list[dict]:
        if not self._token:
            return []
        headers = {"Authorization": f"Bearer {self._token}"}
        all_activities: list[dict] = []
        page = 1

        while True:
            params: dict = {"per_page": 200, "page": page}
            if after_timestamp:
                params["after"] = after_timestamp
            log.debug(f"拉取第 {page} 页")
            try:
                response = request_with_retries(
                    self._session,
                    "GET",
                    ACTIVITIES_URL,
                    headers=headers,
                    params=params,
                    timeout=30,
                )
                if response.status_code != 200:
                    log.err(f"拉取失败 HTTP {response.status_code}")
                    break
                data = response.json()
                if not data:
                    break
                all_activities.extend(data)
                page += 1
                if max_new:
                    new_count = sum(
                        1
                        for item in all_activities
                        if str(item.get("id")) not in known_ids
                    )
                    if new_count >= max_new:
                        log.debug(f"已收集足够新活动 ({new_count})，停止翻页")
                        break
                time.sleep(0.5)
            except Exception as exc:
                log.err(f"拉取异常: {exc}")
                log.warn(sync_proxy_hint())
                break

        log.info(f"API 返回 {len(all_activities)} 条（{page - 1} 页）")
        return all_activities

    @staticmethod
    def filter_pending(
        local_data: list[dict], raw_activities: list[dict]
    ) -> list[dict]:
        known = known_run_ids(local_data)
        pending = [
            item for item in raw_activities if str(item.get("id")) not in known
        ]
        return cap_sync_batch(
            pending,
            SYNC_LIMIT,
            env_name="SYNC_LIMIT",
            keep_newest_at_end=False,
        )

    @staticmethod
    def process_and_merge(local_data: list[dict], raw_new: list[dict]):
        raw_new.sort(
            key=lambda item: parse_time(item.get("start_date_local", ""))
        )

        def label(item: dict) -> str:
            return item.get("start_date_local") or str(item.get("id", "?"))

        return ingest_records(
            local_data,
            raw_new,
            label=label,
            build=format_strava_activity,
        )

    @staticmethod
    def incremental_after_ts(local_data: list[dict]) -> int | None:
        if not local_data:
            return None
        return cutoff_timestamp(local_data)


def main() -> None:
    set_log_scope("Strava")
    log.section("Strava 运动同步")
    _require_credentials()
    log_sync_startup(PATHS)

    local_data = load_activities(PATHS.activities)
    log.info(f"本地 {len(local_data)} 条")
    if SYNC_LIMIT:
        log.info(f"单次上限 SYNC_LIMIT={SYNC_LIMIT}")

    client = StravaClient()
    after_ts = client.incremental_after_ts(local_data)
    if after_ts is not None:
        log.info(f"增量自 {datetime.fromtimestamp(after_ts):%Y-%m-%d %H:%M}")
    else:
        log.info("全量拉取 Strava 历史")

    token = client.access_token()
    if not token:
        sys.exit(1)
    log.ok("Token 就绪")

    raw = client.fetch_activities(
        after_ts,
        known_ids=known_run_ids(local_data),
        max_new=SYNC_LIMIT,
    )
    pending = client.filter_pending(local_data, raw)
    final_data, fetched_count, added_count = client.process_and_merge(
        local_data, pending
    )
    finalize_sync(
        PATHS,
        local_data,
        final_data,
        fetched_count=fetched_count,
        added_count=added_count,
    )


if __name__ == "__main__":
    main()

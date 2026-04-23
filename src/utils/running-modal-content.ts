/**
 * 跑步详情弹窗 HTML（由 running 页客户端脚本注入）
 */

export interface RunningSegment {
  km?: number;
  averagePace?: number;
  averageSpeed?: number;
  averageHeartRate?: number;
  heartRateZone?: number | null;
  stepFrequency?: number;
}

export interface RunningRecord {
  startTime: string;
  endTime?: string;
  type?: string;
  distance?: number;
  duration?: number;
  durationShort?: string;
  averagePace?: number;
  averageSpeed?: number;
  averageHeartRate?: number;
  maxHeartRate?: number;
  stepFrequency?: number;
  strideLength?: number;
  averagePower?: number;
  maxPower?: number;
  calorie?: number;
  elevationGain?: number;
  vDOT?: number;
  trainingLoadScore?: number;
  heartRateZone?: number;
  name?: string;
  activityType?: string;
  region?: string;
  weatherInfo?: string;
  segments?: RunningSegment[];
}

export interface HrZoneContext {
  hrZoneLabels: Record<number, string>;
  hrZoneColors: Record<number, string>;
}

const SVG_ATTR =
  'xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"';

const DETAIL_ICONS = {
  distance: `<svg ${SVG_ATTR}><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>`,
  duration: `<svg ${SVG_ATTR}><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
  pace: `<svg ${SVG_ATTR}><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg>`,
  heartRate: `<svg ${SVG_ATTR}><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>`,
  cadence: `<svg ${SVG_ATTR}><circle cx="12" cy="5" r="1"></circle><path d="M9 20l3-6 3 6"></path><path d="M6 8l6 2 6-2"></path><path d="M12 10V4"></path></svg>`,
  stride: `<svg ${SVG_ATTR}><path d="M2 12h20"></path><path d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-6"></path><path d="M12 2v10"></path></svg>`,
  power: `<svg ${SVG_ATTR}><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg>`,
  calories: `<svg ${SVG_ATTR}><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>`,
  elevation: `<svg ${SVG_ATTR}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
  vdot: `<svg ${SVG_ATTR}><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`,
  load: `<svg ${SVG_ATTR}><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"></path></svg>`,
} as const;

function _formatPaceDetail(sec: number): string {
  if (!sec || sec <= 0) return "0'00\"";
  return `${Math.floor(sec / 60)}'${Math.floor(sec % 60)
    .toString()
    .padStart(2, "0")}"`;
}

function formatDuration(seconds: number): string {
  if (seconds <= 0) return "0m";
  const minutes = Math.round(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours > 0 && mins > 0) {
    return `${hours}h${mins}m`;
  } else if (hours > 0) {
    return `${hours}h`;
  } else {
    return `${mins}m`;
  }
}

function getPaceBarWidthFromSec(sec: number, allSecs: number[]): number {
  if (sec <= 0) return 0;
  const valid = allSecs.filter((s: number) => s > 0);
  if (valid.length > 1) {
    const minPace = Math.min(...valid);
    const maxPace = Math.max(...valid);
    const range = maxPace - minPace;
    if (range > 0) {
      const ratio = (maxPace - sec) / range;
      return Math.max(30, Math.min(100, 30 + ratio * 70));
    }
  }
  const minSec = 240;
  const maxSec = 480;
  const ratio = (maxSec - sec) / (maxSec - minSec);
  return Math.max(20, Math.min(100, 20 + ratio * 80));
}

function getPaceBarClassFromSec(sec: number): "fast" | "medium" | "slow" {
  if (sec <= 0) return "medium";
  if (sec < 330) return "fast";
  if (sec > 420) return "slow";
  return "medium";
}

function hrZoneBadgeHtml(zone: number, ctx: HrZoneContext): string {
  const c = ctx.hrZoneColors[zone];
  const label = ctx.hrZoneLabels[zone];
  if (!c || !label) return "";
  return `<span class="detail-hr-zone" style="background-color: ${c}20; color: ${c}; border: 1px solid ${c}40;">${label}</span>`;
}

export function buildRunDetailModalHtml(
  run: RunningRecord,
  ctx: HrZoneContext
): string {
  const icons = DETAIL_ICONS;
  const hrZoneBadge =
    run.heartRateZone && run.heartRateZone > 0
      ? hrZoneBadgeHtml(run.heartRateZone, ctx)
      : "";

  const detailStats: { icon: string; label: string; value: string }[] = [];

  detailStats.push({
    icon: icons.distance,
    label: "距离",
    value: `${run.distance ?? ""} km`,
  });
  detailStats.push({
    icon: icons.duration,
    label: "移动时间",
    value: formatDuration(run.duration ?? 0),
  });
  detailStats.push({
    icon: icons.pace,
    label: "配速",
    value: `${_formatPaceDetail(run.averagePace ?? 0)} /km`,
  });

  if (run.averageHeartRate && run.averageHeartRate > 0) {
    detailStats.push({
      icon: icons.heartRate,
      label: "平均心率",
      value: `${Math.round(run.averageHeartRate)} bpm`,
    });
  }
  if (run.maxHeartRate && run.maxHeartRate > 0) {
    detailStats.push({
      icon: icons.heartRate,
      label: "最大心率",
      value: `${Math.round(run.maxHeartRate)} bpm`,
    });
  }
  if (run.stepFrequency && run.stepFrequency > 0) {
    detailStats.push({
      icon: icons.cadence,
      label: "平均步频",
      value: `${Math.round(run.stepFrequency)} spm`,
    });
  }
  if (run.strideLength && run.strideLength > 0) {
    detailStats.push({
      icon: icons.stride,
      label: "步幅",
      value: `${run.strideLength.toFixed(2)} m`,
    });
  }
  if (run.averagePower && run.averagePower > 0) {
    detailStats.push({
      icon: icons.power,
      label: "平均功率",
      value: `${Math.round(run.averagePower)} w`,
    });
  }
  if (run.maxPower && run.maxPower > 0) {
    detailStats.push({
      icon: icons.power,
      label: "最大功率",
      value: `${Math.round(run.maxPower)} w`,
    });
  }
  if (run.calorie && run.calorie > 0) {
    detailStats.push({
      icon: icons.calories,
      label: "热量消耗",
      value: `${Math.round(run.calorie)} kcal`,
    });
  }
  if (run.elevationGain && run.elevationGain > 0) {
    detailStats.push({
      icon: icons.elevation,
      label: "累计爬升",
      value: `${Math.round(run.elevationGain)} m`,
    });
  }
  if (run.vDOT && run.vDOT > 0) {
    detailStats.push({
      icon: icons.vdot,
      label: "VDOT",
      value: run.vDOT.toFixed(1),
    });
  }
  if (run.trainingLoadScore && run.trainingLoadScore > 0) {
    detailStats.push({
      icon: icons.load,
      label: "训练负荷",
      value: String(run.trainingLoadScore),
    });
  }

  let segmentsHtml = "";
  if (run.segments && run.segments.length > 0) {
    const allPaces = run.segments
      .map(s => s.averagePace ?? 0)
      .filter((p: number) => p > 0);

    const segmentRows = run.segments
      .map((seg, idx) => {
        const zoneClass =
          seg.heartRateZone != null ? `zone-${seg.heartRateZone}` : "";
        const zoneLabel =
          seg.heartRateZone != null
            ? (ctx.hrZoneLabels[seg.heartRateZone] || "").split(" ")[0]
            : "";
        const paceSec = seg.averagePace ?? 0;
        const paceStr = _formatPaceDetail(paceSec);
        const barWidth = getPaceBarWidthFromSec(paceSec, allPaces);
        const barClass = getPaceBarClassFromSec(paceSec);
        return `
          <tr>
            <td>${seg.km ?? idx + 1}</td>
            <td>
              <div class="pace-bar">
                <div class="pace-bar-fill ${barClass}" style="width: ${barWidth}%"></div>
                <span>${paceStr}</span>
              </div>
            </td>
            <td>${seg.stepFrequency ? seg.stepFrequency : "-"}</td>
            <td>
              <span class="hr-zone-tag ${zoneClass}">${seg.averageHeartRate ?? "-"} ${zoneLabel}</span>
            </td>
          </tr>`;
      })
      .join("");

    segmentsHtml = `
        <div class="detail-section">
          <h4 class="section-subtitle">分段数据</h4>
          <div class="segments-table-wrapper">
            <table class="segments-table">
              <thead>
                <tr>
                  <th>公里</th>
                  <th>配速</th>
                  <th>步频</th>
                  <th>心率</th>
                </tr>
              </thead>
              <tbody>
                ${segmentRows}
              </tbody>
            </table>
          </div>
        </div>`;
  }

  const detailMetaExtras = [
    run.region
      ? `<span class="detail-route" title="路线">${run.region}</span>`
      : "",
    run.weatherInfo
      ? `<span class="detail-weather" title="天气">${run.weatherInfo}</span>`
      : "",
  ]
    .filter(Boolean)
    .join("");

  const statsGrid = detailStats
    .map(
      stat => `
          <div class="detail-stat-item">
            <span class="detail-stat-icon">${stat.icon}</span>
            <span class="detail-stat-label">${stat.label}</span>
            <span class="detail-stat-value">${stat.value}</span>
          </div>`
    )
    .join("");

  return `
      <div class="detail-header">
        <h3 class="detail-title">${run.name || "户外跑步"}</h3>
        <div class="detail-meta">
          <span class="detail-date">${run.startTime}</span>
          ${hrZoneBadge}
          ${detailMetaExtras ? `<span class="detail-meta-sep" aria-hidden="true">·</span>${detailMetaExtras}` : ""}
        </div>
      </div>

      <div class="detail-stats-grid">
        ${statsGrid}
      </div>

      ${segmentsHtml}`;
}

/**
 * 跑步详情弹窗 HTML（由 running 页客户端脚本注入）
 */

export interface RunningSegment {
  km?: number;
  pace?: string;
  cadence?: number;
  heart_rate?: number;
  hr_zone?: number | null;
}

export interface RunningRecord {
  date: string;
  duration?: string;
  durationShort?: string;
  distance?: number;
  pace?: string;
  heart_rate?: number;
  max_heart_rate?: number;
  cadence?: number;
  stride_length?: number;
  avg_power?: number;
  max_power?: number;
  calories?: number;
  elevation_gain?: number;
  vdot?: number;
  training_load?: number;
  hr_zone?: number;
  workout_name?: string;
  activity_type?: string;
  route?: string;
  weather?: string;
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

function paceToSeconds(paceStr: string): number {
  if (!paceStr || paceStr === "0'00\"") return 0;
  const match = paceStr.match(/(\d+)'(\d+)/);
  if (match) {
    return parseInt(match[1], 10) * 60 + parseInt(match[2], 10);
  }
  return 0;
}

function getPaceBarWidth(paceStr: string, allPaces: string[]): number {
  const paceSeconds = paceToSeconds(paceStr);
  if (paceSeconds === 0) return 0;

  if (allPaces.length > 1) {
    const allSeconds = allPaces.map(p => paceToSeconds(p)).filter(s => s > 0);
    if (allSeconds.length > 1) {
      const minPace = Math.min(...allSeconds);
      const maxPace = Math.max(...allSeconds);
      const range = maxPace - minPace;
      if (range > 0) {
        const ratio = (maxPace - paceSeconds) / range;
        return Math.max(30, Math.min(100, 30 + ratio * 70));
      }
    }
  }

  const minSeconds = 240;
  const maxSeconds = 480;
  const ratio = (maxSeconds - paceSeconds) / (maxSeconds - minSeconds);
  return Math.max(20, Math.min(100, 20 + ratio * 80));
}

function getPaceBarClass(paceStr: string): "fast" | "medium" | "slow" {
  const paceSeconds = paceToSeconds(paceStr);
  if (paceSeconds === 0) return "medium";
  if (paceSeconds < 330) return "fast";
  if (paceSeconds > 420) return "slow";
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
    run.hr_zone && run.hr_zone > 0 ? hrZoneBadgeHtml(run.hr_zone, ctx) : "";

  const detailStats: { icon: string; label: string; value: string }[] = [];

  detailStats.push({
    icon: icons.distance,
    label: "距离",
    value: `${run.distance ?? ""} km`,
  });
  detailStats.push({
    icon: icons.duration,
    label: "移动时间",
    value: String(run.durationShort ?? ""),
  });
  detailStats.push({
    icon: icons.duration,
    label: "总时间",
    value: String(run.durationShort ?? ""),
  });
  detailStats.push({
    icon: icons.pace,
    label: "配速",
    value: `${run.pace ?? ""} /km`,
  });

  if (run.heart_rate && run.heart_rate > 0) {
    detailStats.push({
      icon: icons.heartRate,
      label: "平均心率",
      value: `${Math.round(run.heart_rate)} bpm`,
    });
  }
  if (run.max_heart_rate && run.max_heart_rate > 0) {
    detailStats.push({
      icon: icons.heartRate,
      label: "最大心率",
      value: `${Math.round(run.max_heart_rate)} bpm`,
    });
  }
  if (run.cadence && run.cadence > 0) {
    detailStats.push({
      icon: icons.cadence,
      label: "步频",
      value: `${Math.round(run.cadence)} spm`,
    });
  }
  if (run.stride_length && run.stride_length > 0) {
    detailStats.push({
      icon: icons.stride,
      label: "步幅",
      value: `${run.stride_length.toFixed(2)} m`,
    });
  }
  if (run.avg_power && run.avg_power > 0) {
    detailStats.push({
      icon: icons.power,
      label: "平均功率",
      value: `${Math.round(run.avg_power)} w`,
    });
  }
  if (run.max_power && run.max_power > 0) {
    detailStats.push({
      icon: icons.power,
      label: "最大功率",
      value: `${Math.round(run.max_power)} w`,
    });
  }
  if (run.calories && run.calories > 0) {
    detailStats.push({
      icon: icons.calories,
      label: "热量消耗",
      value: `${Math.round(run.calories)} kcal`,
    });
  }
  if (run.elevation_gain && run.elevation_gain > 0) {
    detailStats.push({
      icon: icons.elevation,
      label: "累计爬升",
      value: `${Math.round(run.elevation_gain)} m`,
    });
  }
  if (run.vdot && run.vdot > 0) {
    detailStats.push({
      icon: icons.vdot,
      label: "VDOT",
      value: run.vdot.toFixed(1),
    });
  }
  if (run.training_load && run.training_load > 0) {
    detailStats.push({
      icon: icons.load,
      label: "训练负荷",
      value: String(run.training_load),
    });
  }

  let segmentsHtml = "";
  if (run.segments && run.segments.length > 0) {
    const allSegmentPaces = run.segments
      .map(s => s.pace)
      .filter((p): p is string => Boolean(p && p !== "0'00\""));

    const segmentRows = run.segments
      .map((seg, idx) => {
        const zoneClass = seg.hr_zone != null ? `zone-${seg.hr_zone}` : "";
        const zoneLabel =
          seg.hr_zone != null
            ? (ctx.hrZoneLabels[seg.hr_zone] || "").split(" ")[0]
            : "";
        const barWidth = getPaceBarWidth(seg.pace ?? "", allSegmentPaces);
        const barClass = getPaceBarClass(seg.pace ?? "");
        return `
          <tr>
            <td>${seg.km ?? idx + 1}</td>
            <td>
              <div class="pace-bar">
                <div class="pace-bar-fill ${barClass}" style="width: ${barWidth}%"></div>
                <span>${seg.pace ?? ""}</span>
              </div>
            </td>
            <td>${seg.cadence ? seg.cadence : "-"}</td>
            <td>
              <span class="hr-zone-tag ${zoneClass}">${seg.heart_rate ?? "-"} ${zoneLabel}</span>
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
    run.route
      ? `<span class="detail-route" title="路线">${run.route}</span>`
      : "",
    run.weather
      ? `<span class="detail-weather" title="天气">${run.weather}</span>`
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
        <h3 class="detail-title">${run.workout_name || "室外跑步"}</h3>
        <div class="detail-meta">
          <span class="detail-date">${run.date}</span>
          ${hrZoneBadge}
          ${detailMetaExtras ? `<span class="detail-meta-sep" aria-hidden="true">·</span>${detailMetaExtras}` : ""}
        </div>
      </div>

      <div class="detail-stats-grid">
        ${statsGrid}
      </div>

      ${segmentsHtml}`;
}

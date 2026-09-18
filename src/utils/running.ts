/**
 * 跑步页读 public/data/keep.json。
 * 统计在构建时算，不另存一份 running.json。
 */

import keepData from "../../public/data/keep.json";

const TIME_ZONE = "Asia/Shanghai";
const PAGE_SIZE = 20;

export type RunRecord = {
  type: "run";
  time: string;
  title?: string;
  km?: number;
  minutes?: number;
  hr?: number;
  place?: string;
  /** 秒/公里 */
  pace?: number;
  vdot?: number;
  /** 1–5 */
  zone?: number;
  load?: number;
};

export type PeriodKey = "week" | "month" | "year" | "total";

export type PeriodStats = {
  count: number;
  km: number;
  hours: number;
  pace: string;
  hr: number | null;
  vdot: number | null;
  load: number;
};

export type HeatDay = {
  date: string;
  km: number;
  minutes: number;
  count: number;
  level: 0 | 1 | 2 | 3 | 4 | 5;
  inRange: boolean;
};

export type HeatWeek = HeatDay[];

export const ZONE_LABELS: Record<number, string> = {
  1: "Z1 恢复",
  2: "Z2 有氧",
  3: "Z3 节奏",
  4: "Z4 阈值",
  5: "Z5 最大",
};

export const PERIOD_LABELS: Record<PeriodKey, string> = {
  week: "周",
  month: "月",
  year: "年",
  total: "总",
};

function isRun(value: unknown): value is RunRecord {
  if (!value || typeof value !== "object") return false;
  const item = value as RunRecord;
  return item.type === "run" && !Number.isNaN(Date.parse(item.time));
}

export function loadRuns(): RunRecord[] {
  const rows = Array.isArray(keepData) ? keepData : [];
  const runs: RunRecord[] = [];
  for (const row of rows) {
    if (isRun(row)) runs.push(row);
  }
  return runs.sort((a, b) => Date.parse(b.time) - Date.parse(a.time));
}

export function dayKey(time: string): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(time));
}

function shanghaiParts(date: Date) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    weekday: "short",
    hourCycle: "h23",
  }).formatToParts(date);
  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find(part => part.type === type)?.value ?? "";
  return {
    year: Number(get("year")),
    month: Number(get("month")),
    day: Number(get("day")),
    weekday: get("weekday"),
  };
}

const WEEKDAY_INDEX: Record<string, number> = {
  Mon: 0,
  Tue: 1,
  Wed: 2,
  Thu: 3,
  Fri: 4,
  Sat: 5,
  Sun: 6,
};

export function runDateLabel(time: string): string {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date(time));
  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find(part => part.type === type)?.value ?? "";
  return `${get("year")}-${get("month")}-${get("day")} ${get("hour")}:${get("minute")}:${get("second")}`;
}

export function paceLabel(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds <= 0) return "--";
  const total = Math.round(seconds);
  const min = Math.floor(total / 60);
  const sec = total % 60;
  return `${min}'${String(sec).padStart(2, "0")}"`;
}

export function durationLabel(minutes: number): string {
  if (!Number.isFinite(minutes) || minutes <= 0) return "--";
  const total = Math.round(minutes);
  const hours = Math.floor(total / 60);
  const mins = total % 60;
  if (hours > 0 && mins > 0) return `${hours}h${mins}m`;
  if (hours > 0) return `${hours}h`;
  return `${mins}m`;
}

function intensity(km: number): HeatDay["level"] {
  if (km <= 0) return 0;
  if (km < 3) return 1;
  if (km < 5) return 2;
  if (km < 10) return 3;
  if (km < 15) return 4;
  return 5;
}

function addDays(year: number, month: number, day: number, delta: number) {
  const date = new Date(Date.UTC(year, month - 1, day + delta));
  return {
    year: date.getUTCFullYear(),
    month: date.getUTCMonth() + 1,
    day: date.getUTCDate(),
  };
}

function keyOf(year: number, month: number, day: number) {
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

/** 近 12 个自然月，列从周一开始。范围外的格子 inRange=false。 */
export function runHeatmap(runs: RunRecord[], months = 12): {
  weeks: HeatWeek[];
  labels: { label: string; weekIndex: number }[];
} {
  const today = shanghaiParts(new Date());
  const startIndex = today.year * 12 + (today.month - 1) - (months - 1);
  const startYear = Math.floor(startIndex / 12);
  const startMonth = (startIndex % 12) + 1;
  const startKey = keyOf(startYear, startMonth, 1);

  const byDay = new Map<string, { km: number; minutes: number; count: number }>();
  for (const run of runs) {
    const key = dayKey(run.time);
    const bucket = byDay.get(key) ?? { km: 0, minutes: 0, count: 0 };
    bucket.km += run.km ?? 0;
    bucket.minutes += run.minutes ?? 0;
    bucket.count += 1;
    byDay.set(key, bucket);
  }

  const first = shanghaiParts(new Date(`${startKey}T12:00:00+08:00`));
  const lead = WEEKDAY_INDEX[first.weekday] ?? 0;
  const origin = addDays(startYear, startMonth, 1, -lead);
  const lastDay = new Date(Date.UTC(today.year, today.month, 0)).getUTCDate();
  const rangeEnd = keyOf(today.year, today.month, lastDay);
  const span =
    Math.round(
      (Date.parse(`${rangeEnd}T00:00:00Z`) -
        Date.parse(keyOf(origin.year, origin.month, origin.day) + "T00:00:00Z")) /
        86400000
    ) + 1;
  const weekCount = Math.ceil(span / 7);

  const weeks: HeatWeek[] = [];
  for (let w = 0; w < weekCount; w++) {
    const week: HeatDay[] = [];
    for (let d = 0; d < 7; d++) {
      const date = addDays(origin.year, origin.month, origin.day, w * 7 + d);
      const dateStr = keyOf(date.year, date.month, date.day);
      const hit = byDay.get(dateStr);
      const inRange = dateStr >= startKey && dateStr <= rangeEnd;
      week.push({
        date: dateStr,
        km: hit?.km ?? 0,
        minutes: hit?.minutes ?? 0,
        count: hit?.count ?? 0,
        level: inRange ? intensity(hit?.km ?? 0) : 0,
        inRange,
      });
    }
    weeks.push(week);
  }

  const labels: { label: string; weekIndex: number }[] = [];
  for (let m = 0; m < months; m++) {
    const index = startIndex + m;
    const year = Math.floor(index / 12);
    const month = (index % 12) + 1;
    const key = keyOf(year, month, 1);
    const offset = Math.round(
      (Date.parse(`${key}T00:00:00Z`) -
        Date.parse(keyOf(origin.year, origin.month, origin.day) + "T00:00:00Z")) /
        86400000
    );
    const weekIndex = Math.floor(offset / 7);
    if (weekIndex >= 0 && weekIndex < weeks.length) {
      labels.push({ label: `${month}月`, weekIndex });
    }
  }

  return { weeks, labels };
}

function periodStart(key: PeriodKey, now: Date): number {
  if (key === "total") return 0;
  const parts = shanghaiParts(now);
  if (key === "year") return Date.parse(`${keyOf(parts.year, 1, 1)}T00:00:00+08:00`);
  if (key === "month") {
    return Date.parse(
      `${keyOf(parts.year, parts.month, 1)}T00:00:00+08:00`
    );
  }
  const weekday = WEEKDAY_INDEX[parts.weekday] ?? 0;
  const monday = addDays(parts.year, parts.month, parts.day, -weekday);
  return Date.parse(
    `${keyOf(monday.year, monday.month, monday.day)}T00:00:00+08:00`
  );
}

export function periodStats(runs: RunRecord[], key: PeriodKey, now = new Date()): PeriodStats {
  const start = periodStart(key, now);
  const picked = runs.filter(run => Date.parse(run.time) >= start);
  let km = 0;
  let minutes = 0;
  let hrSum = 0;
  let hrCount = 0;
  let vdotSum = 0;
  let vdotCount = 0;
  let load = 0;
  for (const run of picked) {
    km += run.km ?? 0;
    minutes += run.minutes ?? 0;
    load += run.load ?? 0;
    if (run.hr) {
      hrSum += run.hr;
      hrCount += 1;
    }
    if (run.vdot) {
      vdotSum += run.vdot;
      vdotCount += 1;
    }
  }
  const pace = km > 0 ? (minutes * 60) / km : 0;
  return {
    count: picked.length,
    km: Math.round(km),
    hours: Math.round((minutes / 60) * 10) / 10,
    pace: paceLabel(pace),
    hr: hrCount ? Math.round(hrSum / hrCount) : null,
    vdot: vdotCount ? Math.round((vdotSum / vdotCount) * 10) / 10 : null,
    load: Math.round(load),
  };
}

export type RunFeedItem = {
  time: string;
  date: string;
  title: string;
  place?: string;
  km?: number;
  minutes?: number;
  pace?: string;
  hr?: number;
  vdot?: number;
  zone?: number;
  zoneLabel?: string;
  load?: number;
};

export function toRunFeedItem(run: RunRecord): RunFeedItem {
  const item: RunFeedItem = {
    time: run.time,
    date: runDateLabel(run.time),
    title: run.title?.trim() || "跑步",
  };
  if (run.place) item.place = run.place;
  if (run.km != null) item.km = run.km;
  if (run.minutes != null) item.minutes = run.minutes;
  if (run.pace) item.pace = paceLabel(run.pace);
  if (run.hr) item.hr = run.hr;
  if (run.vdot) item.vdot = run.vdot;
  if (run.zone) {
    item.zone = run.zone;
    item.zoneLabel = ZONE_LABELS[run.zone];
  }
  if (run.load) item.load = run.load;
  return item;
}

export function runFeedPage(runs: RunRecord[], page: number) {
  const items = runs.map(toRunFeedItem);
  const total = Math.ceil(items.length / PAGE_SIZE);
  const safe = Math.min(Math.max(page, 1), Math.max(total, 1));
  const start = (safe - 1) * PAGE_SIZE;
  return {
    items: items.slice(start, start + PAGE_SIZE),
    nextPage: safe < total ? safe + 1 : null,
  };
}

export function getRunFeedStaticPaths() {
  const runs = loadRuns();
  const pages = Math.max(1, Math.ceil(runs.length / PAGE_SIZE));
  return Array.from({ length: pages }, (_, index) => {
    const page = index + 1;
    return {
      params: { page: String(page) },
      props: runFeedPage(runs, page),
    };
  });
}

/**
 * 动态页读内容集合文章（/data/post.json）、public/data/memos.json、
 * public/data/keep.json、public/data/douban.json。
 * type：post 文章、memo 说说、music 音乐、movie 电影、book 读书、food 美食、run 运动。
 */

import doubanData from "../../public/data/douban.json";
import keepData from "../../public/data/keep.json";
import memosData from "../../public/data/memos.json";
import {
  getEntryDescription,
  getEntryTags,
  getPostUrl,
  getPosts,
  sortPosts,
} from "@/utils/postUtils";
import { renderMemoMarkdown } from "@/utils/memoMarkdown";

export const ACTIVITY_TYPES = [
  "post",
  "memo",
  "music",
  "movie",
  "book",
  "food",
  "run",
] as const;

export type ActivityType = (typeof ACTIVITY_TYPES)[number];

export type Activity = {
  type: ActivityType;
  time: string;
  title?: string;
  text?: string;
  description?: string;
  url?: string;
  artist?: string;
  place?: string;
  km?: number;
  minutes?: number;
  hr?: number;
  /** 配速，秒/公里 */
  pace?: number;
  /** Jack Daniels 跑力 */
  vdot?: number;
  /** 1–5，相对最大心率的区间 */
  zone?: number;
  /** 训练负荷 */
  load?: number;
  star?: number;
  slug?: string;
  category?: string;
  tags?: string[];
  images?: string[];
  html?: string;
  cover?: string;
  updated?: string;
};

export const ACTIVITY_LABELS: Record<ActivityType, string> = {
  post: "文章",
  memo: "说说",
  music: "音乐",
  movie: "电影",
  book: "读书",
  food: "美食",
  run: "运动",
};

const TIME_ZONE = "Asia/Shanghai";
const typeSet = new Set<string>(ACTIVITY_TYPES);

function isActivity(value: unknown): value is Activity {
  if (!value || typeof value !== "object") return false;
  const item = value as Activity;
  return typeSet.has(item.type) && !Number.isNaN(Date.parse(item.time));
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function shanghaiIso(value: Date | string): string {
  const date = value instanceof Date ? value : new Date(value);
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).formatToParts(date);
  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find(part => part.type === type)?.value ?? "";
  return `${get("year")}-${get("month")}-${get("day")}T${get("hour")}:${get("minute")}:${get("second")}+08:00`;
}

export async function loadPostRecords(): Promise<Activity[]> {
  return sortPosts(await getPosts(), "date").map(post => {
    const cover = post.data.cover?.trim();
    const updated = post.data.updated
      ? shanghaiIso(post.data.updated)
      : undefined;
    const item: Activity = {
      type: "post",
      time: shanghaiIso(post.data.date),
      title: post.data.title,
      url: getPostUrl(post.data.slug),
      slug: post.data.slug,
      category: post.data.category,
      tags: getEntryTags(post),
      description: getEntryDescription(post),
    };
    if (cover) item.cover = cover;
    if (updated) item.updated = updated;
    return item;
  });
}

export async function loadActivities(): Promise<Activity[]> {
  const posts = await loadPostRecords();
  return [
    ...posts,
    ...asList(memosData),
    ...asList(keepData),
    ...asList(doubanData),
  ]
    .filter(isActivity)
    .sort((a, b) => Date.parse(b.time) - Date.parse(a.time));
}

export function dayKey(time: string): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(time));
}

function calendarDaysAgo(day: string, today: string): number {
  const from = Date.parse(`${day}T00:00:00+08:00`);
  const to = Date.parse(`${today}T00:00:00+08:00`);
  return Math.round((to - from) / 86_400_000);
}

export function activityDayLabel(time: string, now = Date.now()): string {
  const day = dayKey(time);
  const today = dayKey(new Date(now).toISOString());
  const ago = calendarDaysAgo(day, today);
  if (ago === 0) return "今天";
  if (ago === 1) return "昨天";
  if (ago === 2) return "前天";
  if (ago >= 3 && ago <= 30) return `${ago}天前`;
  return `${Number(day.slice(5, 7))}月${Number(day.slice(8, 10))}日`;
}

export function memoHeadline(text?: string): string {
  const line = (text ?? "").trim().split(/\r?\n/, 1)[0] ?? "";
  return line
    .replace(/^#{1,6}\s+/, "")
    .replace(/^\*\*(.+)\*\*$/, "$1")
    .replace(/^[\*_~]+|[\*_~]+$/g, "")
    .trim();
}

export function memoImages(item: Activity): string[] {
  const listed = (item.images ?? []).map(url => url.trim()).filter(Boolean);
  return [...new Set(listed)];
}

export function memoTags(item: Activity): string[] {
  if (item.tags?.length) {
    return item.tags.map(tag => tag.replace(/^#/, "").trim()).filter(Boolean);
  }
  const found = [...(item.text ?? "").matchAll(/(?:^|\s)#([^\s#]+)/g)].map(
    match => match[1]
  );
  return [...new Set(found)];
}

function runHour(time: string): number {
  const hour = new Intl.DateTimeFormat("en-GB", {
    timeZone: TIME_ZONE,
    hour: "2-digit",
    hourCycle: "h23",
  }).format(new Date(time));
  return Number(hour);
}

export function runPeriodTitle(item: Activity): string {
  const kind = item.title?.trim() || ACTIVITY_LABELS.run;
  const hour = runHour(item.time);
  const when =
    hour <= 5
      ? "凌晨"
      : hour <= 8
        ? "清晨"
        : hour <= 11
          ? "上午"
          : hour <= 13
            ? "中午"
            : hour <= 17
              ? "下午"
              : hour <= 19
                ? "傍晚"
                : "晚上";
  return `${when}${kind}`;
}

export function activityTitle(item: Activity): string {
  if (item.type === "memo")
    return item.title?.trim() || memoHeadline(item.text);
  if (item.type === "run") return runPeriodTitle(item);
  return item.title?.trim() || ACTIVITY_LABELS[item.type];
}

export function activityDetail(item: Activity): string {
  if (item.type === "music") return item.artist?.trim() ?? "";
  if (item.type === "movie") return item.text?.trim() ?? "";
  if (item.type === "food") {
    return [item.place, item.text].filter(Boolean).join(" · ");
  }
  if (item.type === "run") {
    const bits = [
      item.km != null ? `${item.km} km` : "",
      item.minutes != null ? `${item.minutes} 分钟` : "",
      item.hr != null ? `${item.hr} bpm` : "",
      item.place ?? "",
    ].filter(Boolean);
    return bits.join(" · ");
  }
  return "";
}

export type HeatCell = {
  date: string;
  count: number;
  level: 0 | 1 | 2 | 3 | 4;
  tone: ActivityType | "mixed" | "";
  counts: Partial<Record<ActivityType, number>>;
};

export type HeatMonth = {
  label: string;
  weeks: (HeatCell | null)[][];
};

function level(count: number): HeatCell["level"] {
  if (count <= 0) return 0;
  if (count === 1) return 1;
  if (count === 2) return 2;
  if (count <= 4) return 3;
  return 4;
}

function toneOf(
  counts: Partial<Record<ActivityType, number>>
): HeatCell["tone"] {
  const types = ACTIVITY_TYPES.filter(type => (counts[type] ?? 0) > 0);
  if (types.length === 0) return "";
  if (types.length === 1) return types[0];
  return "mixed";
}

function cellFrom(
  date: string,
  counts: Partial<Record<ActivityType, number>>
): HeatCell {
  const count = Object.values(counts).reduce((sum, n) => sum + (n ?? 0), 0);
  return { date, count, level: level(count), tone: toneOf(counts), counts };
}

/** 近若干个自然月，每月一块。列从周一开始，月初留空。 */
export function monthHeatmap(items: Activity[], months = 12): HeatMonth[] {
  const todayKey = dayKey(new Date().toISOString());
  const [ty, tm] = todayKey.split("-").map(Number);
  const startIndex = ty * 12 + (tm - 1) - (months - 1);

  const byDay = new Map<string, Partial<Record<ActivityType, number>>>();
  for (const item of items) {
    const key = dayKey(item.time);
    const bucket = byDay.get(key) ?? {};
    bucket[item.type] = (bucket[item.type] ?? 0) + 1;
    byDay.set(key, bucket);
  }

  const result: HeatMonth[] = [];
  for (let index = 0; index < months; index++) {
    const abs = startIndex + index;
    const year = Math.floor(abs / 12);
    const month = (abs % 12) + 1;
    const yearStr = String(year);
    const monthStr = String(month).padStart(2, "0");
    const first = new Date(`${yearStr}-${monthStr}-01T12:00:00+08:00`);
    const lead = (first.getUTCDay() + 6) % 7;
    const days = new Date(Date.UTC(year, month, 0)).getUTCDate();
    const slots: (HeatCell | null)[] = Array.from({ length: lead }, () => null);
    for (let day = 1; day <= days; day++) {
      const key = `${yearStr}-${monthStr}-${String(day).padStart(2, "0")}`;
      slots.push(key > todayKey ? null : cellFrom(key, byDay.get(key) ?? {}));
    }
    while (slots.length % 7 !== 0) slots.push(null);
    const weeks: (HeatCell | null)[][] = [];
    for (let offset = 0; offset < slots.length; offset += 7) {
      weeks.push(slots.slice(offset, offset + 7));
    }
    result.push({
      label: `${month}月`,
      weeks,
    });
  }
  return result;
}

export type ActivityRow = {
  item: Activity;
  label: string;
  hideTime: boolean;
  showYear: boolean;
  year: string;
};

export function activityRows(items: Activity[]): ActivityRow[] {
  let lastDay = "";
  let lastYear = "";
  return items.map(item => {
    const day = dayKey(item.time);
    const year = day.slice(0, 4);
    const row: ActivityRow = {
      item,
      label: activityDayLabel(item.time),
      hideTime: day === lastDay,
      showYear: year !== lastYear,
      year,
    };
    lastDay = day;
    lastYear = year;
    return row;
  });
}

export function starMarks(star: number | undefined): string {
  const n = Math.max(0, Math.min(5, Math.round(star ?? 0)));
  if (!n) return "";
  return "★".repeat(n) + "☆".repeat(5 - n);
}

export const ACTIVITY_PAGE_SIZE = 20;

export type ActivityFilter = "all" | ActivityType;

export type ActivityFeedItem = {
  type: ActivityType;
  time: string;
  label: string;
  hideTime: boolean;
  showYear: boolean;
  year: string;
  title: string;
  lead: string;
  url?: string;
  tags?: string[];
  images?: string[];
  html?: string;
  stars?: string;
  star?: number;
  place?: string;
  km?: number;
  minutes?: number;
  hr?: number;
  text?: string;
};

function activityLead(item: Activity): string {
  if (item.type === "post") return "发布了文章";
  if (item.type === "memo") return "发布了说说";
  if (item.type === "music") {
    return item.artist?.trim() ? `听过 ${item.artist.trim()} 的` : "听过";
  }
  if (item.type === "movie") return "看过电影";
  if (item.type === "book") return "读过";
  if (item.type === "food") return "点评了";
  return "";
}

export async function toActivityFeedItem(
  row: ActivityRow
): Promise<ActivityFeedItem> {
  const item = row.item;
  const stars = starMarks(item.star);
  const feed: ActivityFeedItem = {
    type: item.type,
    time: item.time,
    label: row.label,
    hideTime: row.hideTime,
    showYear: row.showYear,
    year: row.year,
    title: activityTitle(item),
    lead: activityLead(item),
  };
  if (item.url) feed.url = item.url;
  if (item.type === "memo") {
    const tags = memoTags(item);
    if (tags.length) feed.tags = tags;
    const images = memoImages(item);
    if (images.length) feed.images = images;
    if (item.text?.trim()) feed.html = await renderMemoMarkdown(item.text);
  }
  if (stars) {
    feed.stars = stars;
    if (item.star != null) feed.star = item.star;
  }
  if (item.place) feed.place = item.place;
  if (item.km != null) feed.km = item.km;
  if (item.minutes != null) feed.minutes = item.minutes;
  if (item.hr != null) feed.hr = item.hr;
  if (
    (item.type === "movie" ||
      item.type === "food" ||
      item.type === "book" ||
      item.type === "music") &&
    item.text?.trim()
  ) {
    feed.text = item.text.trim();
  }
  return feed;
}

export async function activityFeedPage(
  items: Activity[],
  filter: ActivityFilter,
  page: number
) {
  const source =
    filter === "all" ? items : items.filter(item => item.type === filter);
  const total = Math.ceil(source.length / ACTIVITY_PAGE_SIZE);
  const safe = Math.min(Math.max(page, 1), Math.max(total, 1));
  const start = (safe - 1) * ACTIVITY_PAGE_SIZE;
  const rows = await Promise.all(
    activityRows(source)
      .slice(start, start + ACTIVITY_PAGE_SIZE)
      .map(toActivityFeedItem)
  );
  return {
    items: rows,
    nextPage: safe < total ? safe + 1 : null,
  };
}

export async function getActivityFeedStaticPaths() {
  const items = await loadActivities();
  const filters: ActivityFilter[] = [
    "all",
    ...ACTIVITY_TYPES.filter(type => items.some(item => item.type === type)),
  ];
  const paths = await Promise.all(
    filters.map(async filter => {
      const count =
        filter === "all"
          ? items.length
          : items.filter(item => item.type === filter).length;
      const pages = Math.ceil(count / ACTIVITY_PAGE_SIZE);
      return Promise.all(
        Array.from({ length: pages }, async (_, index) => {
          const page = index + 1;
          return {
            params: { type: filter, page: String(page) },
            props: await activityFeedPage(items, filter, page),
          };
        })
      );
    })
  );
  return paths.flat();
}

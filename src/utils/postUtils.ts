/**
 * 文章过滤、排序、路径、摘要与首页 feed。
 */

import { getCollection } from "astro:content";
import type { CollectionEntry } from "astro:content";

import { SITE } from "@/config";

const SITE_TZ = SITE.timezone;
const SCHEDULED_POST_MARGIN_MS = 15 * 60 * 1000;
const DESC_MAX_LINES = 3;
const DESC_MAX_CHARS = 200;

export type BlogLikeCollection = "posts";
export type BlogLikeEntry = CollectionEntry<BlogLikeCollection>;

export async function getAllBlogLike(): Promise<BlogLikeEntry[]> {
  return getCollection("posts");
}

const tagMoreRegex = /^(.*?)<!--\s*more\s*-->/s;

const descriptionStrippers: [RegExp, string][] = [
  [/```[\s\S]*?```/g, ""],
  [/!\[[^\]]*\]\([^)]+\)/g, ""],
  [/\[([^\]]+)\]\([^)]+\)/g, "$1"],
  [/#{1,6}\s+/g, ""],
  [/`([^`]+)`/g, "$1"],
];

export function isHttpUrl(url: string): boolean {
  return url.startsWith("http://") || url.startsWith("https://");
}

function isPublished(post: BlogLikeEntry): boolean {
  const { data } = post;
  const ok =
    Date.now() > new Date(data.date).getTime() - SCHEDULED_POST_MARGIN_MS;
  return !data.draft && (import.meta.env.DEV || ok);
}

export function getPublishedPosts(posts: BlogLikeEntry[]): BlogLikeEntry[] {
  return posts.filter(isPublished);
}

/** 文章页 URL：`/{collection}/{slug}` */
export function getPostUrl(
  slug: string,
  collection: BlogLikeCollection = "posts"
): string {
  return `/${collection}/${slug.trim()}`;
}

/** 动态路由 `[...slug]` 的 param（无 leading slash） */
export function getPostSlugParam(slug: string): string {
  return slug.trim();
}

export function resolveBlogImageRef(
  raw: string | undefined | null,
  imageDir: string
): string | undefined {
  const t = typeof raw === "string" ? raw.trim() : "";
  if (!t) return undefined;
  if (isHttpUrl(t)) return t;
  if (t.startsWith("/")) return t;
  const rel = t.replace(/\\/g, "/").replace(/^(\.\/)+/, "");
  if (!rel || rel.split("/").some(s => s === ".." || s === "")) {
    return undefined;
  }
  const dir = imageDir.trim() || "post";
  return `/images/${dir}/${rel}`;
}

export function getEntryDescription(entry: BlogLikeEntry): string {
  return entry.data.description?.trim() || getDescription(entry.body ?? "");
}

export function getDescription(markdownContent: string): string {
  const lines = markdownContent.split(/\r?\n/).slice(0, DESC_MAX_LINES);
  const processedContent = lines.join("");
  const moreTagMatch = processedContent.match(tagMoreRegex);
  let short = moreTagMatch
    ? moreTagMatch[1]
    : processedContent.substring(0, DESC_MAX_CHARS) + " ...";
  for (const [pattern, replacement] of descriptionStrippers) {
    short = short.replace(pattern, replacement);
  }
  return short.replace(/\s+/g, " ").trim();
}

export function sortPosts(posts: BlogLikeEntry[]): BlogLikeEntry[] {
  return getPublishedPosts(posts).sort(
    (a, b) =>
      Math.floor(new Date(b.data.updated ?? b.data.date).getTime() / 1000) -
      Math.floor(new Date(a.data.updated ?? a.data.date).getTime() / 1000)
  );
}

export function sortPostsByDate(posts: BlogLikeEntry[]): BlogLikeEntry[] {
  return getPublishedPosts(posts).sort(
    (a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime()
  );
}

function parseInstant(value: Date | string): Date {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new Error(`Invalid date: ${String(value)}`);
  }
  return date;
}

export function formatFeedDate(
  pubDatetime: Date | string,
  modDatetime?: Date | string | null
): { display: string; iso: string } {
  const pub = parseInstant(pubDatetime);
  const mod = modDatetime != null ? parseInstant(modDatetime) : null;
  const latest = mod && mod.getTime() > pub.getTime() ? mod : pub;
  return {
    display: new Intl.DateTimeFormat("sv-SE", {
      timeZone: SITE_TZ,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(latest),
    iso: latest.toISOString(),
  };
}

export const HOME_FEED_PAGE_SIZE = SITE.postPerIndex;

export type HomeFeedItem = {
  title: string;
  href: string;
  dateDisplay: string;
  dateIso: string;
  description: string;
};

export function toHomeFeedItem(entry: BlogLikeEntry): HomeFeedItem {
  const date = formatFeedDate(entry.data.date, entry.data.updated);
  return {
    title: entry.data.title,
    href: getPostUrl(entry.data.slug, entry.collection),
    dateDisplay: date.display,
    dateIso: date.iso,
    description: getEntryDescription(entry),
  };
}

export async function getAllHomeFeedItems(): Promise<HomeFeedItem[]> {
  return sortPosts(await getAllBlogLike()).map(toHomeFeedItem);
}

export function paginateHomeFeedItems(
  items: HomeFeedItem[],
  page: number
): {
  items: HomeFeedItem[];
  page: number;
  totalPages: number;
  nextPage: number | null;
} {
  const totalPages = Math.max(1, Math.ceil(items.length / HOME_FEED_PAGE_SIZE));
  const safePage = Math.min(Math.max(page, 1), totalPages);
  const start = (safePage - 1) * HOME_FEED_PAGE_SIZE;
  return {
    items: items.slice(start, start + HOME_FEED_PAGE_SIZE),
    page: safePage,
    totalPages,
    nextPage: safePage < totalPages ? safePage + 1 : null,
  };
}

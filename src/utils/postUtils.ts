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

export type PostEntry = CollectionEntry<"posts">;

const HOME_FEED_PAGE_SIZE = SITE.postPerIndex;

const tagMoreRegex = /^(.*?)<!--\s*more\s*-->/s;

const descriptionStrippers: [RegExp, string][] = [
  [/```[\s\S]*?```/g, ""],
  [/!\[[^\]]*\]\([^)]+\)/g, ""],
  [/\[([^\]]+)\]\([^)]+\)/g, "$1"],
  [/#{1,6}\s+/g, ""],
  [/`([^`]+)`/g, "$1"],
];

export async function getPosts(): Promise<PostEntry[]> {
  return getCollection("posts");
}

function isHttpUrl(url: string): boolean {
  return url.startsWith("http://") || url.startsWith("https://");
}

function isPublished(post: PostEntry): boolean {
  const { data } = post;
  const ok =
    Date.now() > new Date(data.date).getTime() - SCHEDULED_POST_MARGIN_MS;
  return !data.draft && (import.meta.env.DEV || ok);
}

export function getPostUrl(slug: string): string {
  return `/posts/${slug.trim()}`;
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

export function getEntryDescription(entry: PostEntry): string {
  return entry.data.description?.trim() || excerptFromMarkdown(entry.body ?? "");
}

function excerptFromMarkdown(markdownContent: string): string {
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

/** `updated`：首页/站点图；`date`：RSS 按发布时间 */
export function sortPosts(
  posts: PostEntry[],
  by: "updated" | "date" = "updated"
): PostEntry[] {
  const published = posts.filter(isPublished);
  if (by === "date") {
    return published.sort(
      (a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime()
    );
  }
  return published.sort(
    (a, b) =>
      Math.floor(new Date(b.data.updated ?? b.data.date).getTime() / 1000) -
      Math.floor(new Date(a.data.updated ?? a.data.date).getTime() / 1000)
  );
}

function parseInstant(value: Date | string): Date {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) {
    throw new Error(`Invalid date: ${String(value)}`);
  }
  return date;
}

function formatFeedDate(
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

export type HomeFeedItem = {
  title: string;
  href: string;
  dateDisplay: string;
  dateIso: string;
  description: string;
};

function toHomeFeedItem(entry: PostEntry): HomeFeedItem {
  const date = formatFeedDate(entry.data.date, entry.data.updated);
  return {
    title: entry.data.title,
    href: getPostUrl(entry.data.slug),
    dateDisplay: date.display,
    dateIso: date.iso,
    description: getEntryDescription(entry),
  };
}

export async function getAllHomeFeedItems(): Promise<HomeFeedItem[]> {
  return sortPosts(await getPosts()).map(toHomeFeedItem);
}

function getFeedTotalPages(itemCount: number): number {
  return Math.max(1, Math.ceil(itemCount / HOME_FEED_PAGE_SIZE));
}

export function paginateHomeFeedItems(
  items: HomeFeedItem[],
  page: number
): { items: HomeFeedItem[]; nextPage: number | null } {
  const totalPages = getFeedTotalPages(items.length);
  const safePage = Math.min(Math.max(page, 1), totalPages);
  const start = (safePage - 1) * HOME_FEED_PAGE_SIZE;
  return {
    items: items.slice(start, start + HOME_FEED_PAGE_SIZE),
    nextPage: safePage < totalPages ? safePage + 1 : null,
  };
}

export function postModifiedIso(entry: PostEntry): string {
  return new Date(entry.data.updated ?? entry.data.date).toISOString();
}

export async function getFeedPaginationStaticPaths() {
  const all = await getAllHomeFeedItems();
  const totalPages = getFeedTotalPages(all.length);
  if (totalPages <= 1) return [];

  return Array.from({ length: totalPages - 1 }, (_, index) => {
    const page = index + 2;
    const { items, nextPage } = paginateHomeFeedItems(all, page);
    return {
      params: { page: String(page) },
      props: { items, nextPage },
    };
  });
}

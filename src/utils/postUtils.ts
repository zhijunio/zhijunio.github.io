/**
 * 博客与文章集合相关工具
 *
 * @fileoverview 文章过滤/排序/路径、描述提取、列表时间展示、LLMs 站点地图；content/about 等静态页 frontmatter
 */

import fs from "node:fs";
import path from "node:path";

import { getCollection } from "astro:content";
import type { CollectionEntry } from "astro:content";
import dayjs from "dayjs";
import type { Dayjs } from "dayjs";
import utc from "dayjs/plugin/utc";
import timezonePlugin from "dayjs/plugin/timezone";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/zh-cn";

import { SITE } from "@/config";

dayjs.extend(utc);
dayjs.extend(timezonePlugin);
dayjs.extend(relativeTime);
dayjs.locale("zh-cn");

const SITE_TZ = SITE.timezone || "Asia/Shanghai";

/** 与 `src/content.config.ts` 集合名一致 */
export type BlogLikeCollection = "posts";

export type BlogLikeEntry = CollectionEntry<BlogLikeCollection>;

export async function getAllBlogLike(): Promise<BlogLikeEntry[]> {
  return getCollection("posts");
}

// --- 描述提取（Markdown → 纯文本摘要）---

/** 匹配 `<!-- more -->` 之前的内容，捕获组 $1 为摘要 */
const tagMoreRegex = /^(.*?)<!--\s*more\s*-->/s;

/** Markdown 语法替换规则，按顺序应用 */
const regexReplacers: Record<string, [RegExp, string]> = {
  header: [/#{1,6} (.*?)/g, "$1 "],
  star: [/\*{1,3}(.*?)\*{1,3}/g, "$1"],
  underscore: [/_{1,3}(.*?)_{1,3}/g, "$1"],
  strikeout: [/~~~[\s\S]*?~~~/g, ""],
  horizontalRule: [/^(-{3,}|\*{3,})$/gm, ""],
  quote: [/> (.*?)/g, "$1"],
  codeInline: [/`(.*?)`/g, "$1"],
  codeBlock: [/```[\s\S]*?```/g, ""],
  latexInline: [/\$(.*?)\$/g, ""],
  latexBlock: [/\$\$[\s\S]*?\$\$/g, ""],
  image1: [/!\[(.*?)\]\((.*?)\)/g, ""],
  image2: [/!\[(.*?)\]\[(.*?)\]/g, ""],
  link1: [/\[(.*?)\]\((.*?)\)/g, "$1 "],
  link2: [/\[(.*?)\]\[(.*?)\]/g, "$1 "],
  linkRef: [/\[(.*?)\]: (.*?)/g, ""],
};

// --- PostUtils ---

export class PostUtils {
  /** `http://` 或 `https://` 开头 */
  static isHttpUrl(url: string): boolean {
    return url.startsWith("http://") || url.startsWith("https://");
  }

  static filter(post: BlogLikeEntry): boolean {
    const { data } = post;
    const isPublishTimePassed =
      Date.now() > new Date(data.date).getTime() - SITE.scheduledPostMargin;
    return !data.draft && (import.meta.env.DEV || isPublishTimePassed);
  }

  static getPublishedPosts(posts: BlogLikeEntry[]): BlogLikeEntry[] {
    return posts.filter(this.filter);
  }

  static sort(posts: BlogLikeEntry[]): BlogLikeEntry[] {
    return this.getPublishedPosts(posts).sort(
      (a, b) =>
        Math.floor(new Date(b.data.updated ?? b.data.date).getTime() / 1000) -
        Math.floor(new Date(a.data.updated ?? a.data.date).getTime() / 1000)
    );
  }

  /**
   * 按发布时间 `date` 降序（不使用 `updated`），与文章列表「最近更新」逻辑区分。
   * 用于 RSS 等需与 `pubDate` 一致的排序。
   */
  static sortByPublishedDate(posts: BlogLikeEntry[]): BlogLikeEntry[] {
    return this.getPublishedPosts(posts).sort(
      (a, b) =>
        new Date(b.data.date).getTime() - new Date(a.data.date).getTime()
    );
  }

  static getLocalDateString(
    date: Date,
    timeZone: string = SITE.timezone
  ): string {
    const f = new Intl.DateTimeFormat("en-CA", {
      timeZone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
    const parts = f.formatToParts(date);
    const y = parts.find(p => p.type === "year")!.value;
    const m = parts.find(p => p.type === "month")!.value;
    const d = parts.find(p => p.type === "day")!.value;
    return `${y}-${m}-${d}`;
  }

  /**
   * 文章 URL：`/{collection}/{slug}`（如 `/posts/...`）。frontmatter `slug` 按元数据原样使用（仅 trim）；未指定时由文件名去掉 `YYYY-MM-DD-` 前缀，整段再 trim（不作 kebab-case）。
   *
   * @param explicitSlug - frontmatter `slug`
   * @param _date - 保留参数（排序/展示仍用）；不再参与 URL，避免破坏既有调用签名
   * @param _timeZone - 同上
   * @param collection - 内容集合名，与 URL 首段一致
   */
  static getPath(
    id: string,
    _filePath: string | undefined,
    includeBase = true,
    _date?: Date,
    _timeZone?: string,
    explicitSlug?: string | null,
    collection: BlogLikeCollection = "posts"
  ): string {
    const basePath = includeBase ? `/${collection}` : "";
    const blogId = id.split("/");
    const fileName = blogId.length > 0 ? blogId.slice(-1)[0] : id;
    let slug = fileName.replace(/\.(md|mdx)$/, "").trim();
    const datePrefixMatch = slug.match(/^(\d{4}-\d{2}-\d{2})-(.+)$/);
    if (datePrefixMatch) {
      slug = datePrefixMatch[2].trim();
    }

    const fromFrontmatter = explicitSlug?.trim();
    if (fromFrontmatter) {
      slug = fromFrontmatter;
    }

    return [basePath, slug].filter(Boolean).join("/");
  }

  /**
   * 文章配图在 `public/images/{目录}/` 下的目录名（与 {@link PostUtils.getPath} 末段相同，即 `slug` 语义）。
   *
   * 对外 URL：`astro dev` 同源 `/images/...`，生产 CDN，见 `src/utils/blogImages/`。
   */
  static getPostImageDirName(
    id: string,
    filePath: string | undefined,
    date?: Date,
    timeZone?: string,
    explicitSlug?: string | null,
    collection: BlogLikeCollection = "posts"
  ): string {
    const pathNoPosts = PostUtils.getPath(
      id,
      filePath,
      false,
      date,
      timeZone,
      explicitSlug,
      collection
    );
    const segments = pathNoPosts.split("/").filter(Boolean);
    return segments[segments.length - 1] ?? "post";
  }

  /**
   * 将 frontmatter 中的图片引用解析为根相对 URL。
   *
   * - `http(s)://...`：原样返回
   * - 以 `/` 开头：根相对路径原样返回（旧式 `/images/foo/01.webp` 等）
   * - 否则视为相对文章配图目录的文件名（可含子路径段），解析为 `/images/{imageDirName}/{ref}`
   */
  static resolveBlogImageRef(
    raw: string | undefined | null,
    imageDirName: string
  ): string | undefined {
    const t = typeof raw === "string" ? raw.trim() : "";
    if (!t) return undefined;
    if (PostUtils.isHttpUrl(t)) return t;
    if (t.startsWith("/")) return t;
    const rel = t.replace(/\\/g, "/").replace(/^(\.\/)+/, "");
    if (!rel || rel.split("/").some(s => s === ".." || s === "")) {
      return undefined;
    }
    const dir = imageDirName.trim() || "post";
    return `/images/${dir}/${rel}`;
  }

  static getDescription(markdownContent: string): string {
    const lines = markdownContent
      .split(/\r?\n/)
      .slice(0, SITE.genDescriptionMaxLines);
    const processedContent = lines.join("");
    const moreTagMatch = processedContent.match(tagMoreRegex);
    let short = moreTagMatch
      ? moreTagMatch[1]
      : processedContent.substring(0, SITE.genDescriptionCount) + " ...";

    for (const patternKey in regexReplacers) {
      const [pattern, replacement] = regexReplacers[patternKey];
      short = short.replace(pattern, replacement);
    }
    return short;
  }

  /**
   * 获取纯文本描述（去除 HTML 标签）
   * 用于相关文章卡片等场景
   * @param markdownContent Markdown 内容
   * @param maxLength 最大字符数，默认 80
   */
  static getPlainTextDescription(
    markdownContent: string,
    maxLength: number = 80
  ): string {
    const lines = markdownContent
      .split(/\r?\n/)
      .slice(0, SITE.genDescriptionMaxLines);
    const processedContent = lines.join("");
    const moreTagMatch = processedContent.match(tagMoreRegex);
    let short = moreTagMatch
      ? moreTagMatch[1]
      : processedContent.substring(0, SITE.genDescriptionCount);

    // 移除 HTML 标签
    short = short.replace(/<[^>]+>/g, "");

    // 移除 Markdown 语法
    for (const patternKey in regexReplacers) {
      const [pattern, replacement] = regexReplacers[patternKey];
      short = short.replace(pattern, replacement);
    }

    // 清理多余空白
    short = short.replace(/\s+/g, " ").trim();

    // 截断
    if (short.length > maxLength) {
      short = short.slice(0, maxLength) + "…";
    }

    return short;
  }
}

// --- llms.txt ---

function toAbsoluteUrl(path: string): string {
  return new URL(path, SITE.website).toString();
}

function getPostMarkdownUrl(post: BlogLikeEntry): string {
  const slugPath = PostUtils.getPath(
    post.id,
    post.filePath,
    false,
    post.data.date,
    post.data.timezone,
    post.data.slug,
    post.collection
  );
  return toAbsoluteUrl(`/${post.collection}/${slugPath}.md`);
}

function getPostDescription(post: BlogLikeEntry): string {
  return (
    post.data.description?.trim() ||
    PostUtils.getDescription(post.body ?? "")
      .replace(/\s+/g, " ")
      .trim()
  );
}

function formatPostLine(post: BlogLikeEntry): string {
  return `- [${post.data.title}](${getPostMarkdownUrl(post)}): ${getPostDescription(post)}`;
}

function formatLinkLine(
  label: string,
  path: string,
  description?: string
): string {
  const link = `[${label}](${toAbsoluteUrl(path)})`;
  return description ? `- ${link}: ${description}` : `- ${link}`;
}

export function generateLlmsTxt(posts: BlogLikeEntry[]): string {
  const allPosts = PostUtils.sort(posts);

  const lines = [
    `# ${SITE.title}`,
    "",
    `> ${SITE.description}. Personal blog by ${SITE.author}.`,
    "",
    "## Site",
    formatLinkLine("Home", "/", "Main entry point"),
    formatLinkLine("About", "/about", "Author profile and site background"),
    formatLinkLine(
      "博客",
      "/posts",
      "博客和周报时间线（content/tech、content/weekly）"
    ),
    "",
    "## All entries",
    ...allPosts.map(formatPostLine),
    "",
    "## Feeds",
    formatLinkLine("RSS", "/rss.xml"),
    formatLinkLine("Sitemap", "/sitemap.xml"),
    formatLinkLine("Robots", "/robots.txt"),
    "",
    "## Notes For LLMs",
    "- Canonical article URLs use the /posts/ prefix. Weekly notes live under content/weekly/.",
    "- These pages are the primary source of truth; search is available at /search.",
  ];

  return `${lines.join("\n")}\n`;
}

// --- 列表时间展示 ---

/** 列表 `<time>`：展示文案、机器可读 ISO、悬浮提示（发布时刻） */
export interface ArticleTimeFields {
  display: string;
  iso: string;
  titleAttr: string;
}

function latestOf(pub: Dayjs, mod: Dayjs | null): Dayjs {
  return mod && mod.isAfter(pub) ? mod : pub;
}

function effectiveTimezone(timezoneProp: string | undefined): string {
  return timezoneProp || SITE_TZ;
}

/** 文章发布/更新时间在列表卡片中的展示（最新时间 + 时区；`titleAttr` 为发布时间） */
export class ArticleTime {
  static getDisplay(
    pubDatetime: Date | string,
    modDatetime: Date | string | null | undefined,
    timezoneProp: string | undefined,
    format: "relative" | "absolute"
  ): ArticleTimeFields {
    const pub = dayjs(pubDatetime);
    const mod = modDatetime ? dayjs(modDatetime) : null;
    const latest = latestOf(pub, mod);
    const iso = latest.toISOString();
    const tz = effectiveTimezone(timezoneProp);
    const latestInTz = dayjs.utc(latest.toDate()).tz(tz);
    const pubInTz = dayjs.utc(pub.toDate()).tz(tz);
    const titleAttr = pubInTz.format("YYYY-MM-DD HH:mm:ss");
    const display =
      format === "absolute"
        ? latestInTz.format("YYYY-MM-DD")
        : latest.fromNow();
    return { display, iso, titleAttr };
  }
}

// --- 首页 feed（博客 + 周报混排）---

export const HOME_FEED_PAGE_SIZE = 10;

export type HomeFeedItem = {
  title: string;
  href: string;
  dateDisplay: string;
  dateIso: string;
  dateTitle: string;
  description: string;
};

export function toHomeFeedItem(entry: BlogLikeEntry): HomeFeedItem {
  const date = ArticleTime.getDisplay(
    entry.data.date,
    entry.data.updated,
    entry.data.timezone,
    "absolute"
  );
  return {
    title: entry.data.title,
    href: PostUtils.getPath(
      entry.id,
      entry.filePath,
      true,
      entry.data.date,
      entry.data.timezone,
      entry.data.slug,
      entry.collection
    ),
    dateDisplay: date.display,
    dateIso: date.iso,
    dateTitle: date.titleAttr,
    description: (
      entry.data.description?.trim() ||
      PostUtils.getDescription(entry.body ?? "")
    ).trim(),
  };
}

export async function getAllHomeFeedItems(): Promise<HomeFeedItem[]> {
  return PostUtils.sort(await getAllBlogLike()).map(toHomeFeedItem);
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

// --- content/ 下静态 Markdown 页（about 等）---

export interface ContentPageData {
  frontmatter: Record<string, string>;
  content: string;
}

/** 读取 `content/{fileName}`，解析单行 `key: value` frontmatter（与 about 页约定一致） */
export function readContentPage(fileName: string): ContentPageData {
  const filePath = path.join(process.cwd(), "content", fileName);
  const fileContent = fs.readFileSync(filePath, "utf-8");
  const frontmatterMatch = fileContent.match(
    /^---\n([\s\S]*?)\n---\n([\s\S]*)$/
  );

  if (!frontmatterMatch) {
    throw new Error(`Invalid content page frontmatter: ${fileName}`);
  }

  const frontmatterStr = frontmatterMatch[1];
  const content = frontmatterMatch[2];
  const frontmatter: Record<string, string> = {};

  frontmatterStr.split("\n").forEach((line: string) => {
    const match = line.match(/^(\w+):\s*(.+)$/);
    if (!match) return;

    const key = match[1];
    let value = match[2].trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    frontmatter[key] = value;
  });

  return { frontmatter, content };
}

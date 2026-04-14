/**
 * 博客与文章集合相关工具（原多文件合并：摘要正则、slug、分类元数据、PostUtils、llms.txt 生成）
 *
 * @fileoverview 文章过滤/排序/路径、标签、描述提取、LLMs 站点地图文案；订阅卡片日期、content/pages 极简 frontmatter 读取
 */

import fs from "node:fs";
import path from "node:path";

import type {
  BlogLikeCollection,
  BlogLikeEntry,
} from "@/utils/contentCollections";

import { SITE } from "@/config";
import { siteImageHref } from "@/utils/blogImages";

// --- 描述提取（Markdown → 纯文本摘要）---

/** 列表 favicon 无分类或回退（`public/favicons/blank.svg`） */
const FAVICON_BLANK_PATH = "/favicons/blank.svg";

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

// --- Slug（URL 路径）---

/**
 * 标签/分类 URL 段、索引用键等：与 frontmatter 字面一致，仅 `trim`（不做 kebab-case 等变换）。
 */
export function trimUrlSegment(str: string): string {
  return String(str).trim();
}

const trimAll = (arr: string[]) => arr.map(s => trimUrlSegment(s));

// --- PostUtils ---

export interface Tag {
  tag: string;
  tagName: string;
  count: number;
}

type GroupKey = string | number | symbol;

interface GroupFunction<T> {
  (item: T, index?: number): GroupKey;
}

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

  static getUniqueTags(posts: BlogLikeEntry[]): Tag[] {
    const tagCountMap = new Map<string, Tag>();

    this.getPublishedPosts(posts)
      .flatMap(post => post.data.tags)
      .forEach(tag => {
        const tagKey = trimUrlSegment(tag).toLowerCase();

        // 跳过空字符串标签
        if (!tagKey) {
          return;
        }

        if (tagCountMap.has(tagKey)) {
          const existingTag = tagCountMap.get(tagKey)!;
          existingTag.count += 1;
        } else {
          tagCountMap.set(tagKey, {
            tag: tagKey,
            tagName: tag,
            count: 1,
          });
        }
      });

    return Array.from(tagCountMap.values()).sort((tagA, tagB) =>
      tagA.tag.localeCompare(tagB.tag)
    );
  }

  static getPostsByTag(posts: BlogLikeEntry[], tag: string): BlogLikeEntry[] {
    const tagLower = tag.toLowerCase();
    return this.sort(
      posts.filter(post =>
        trimAll(post.data.tags).some(t => t.toLowerCase() === tagLower)
      )
    );
  }

  static groupBy(
    posts: BlogLikeEntry[],
    groupFunction: GroupFunction<BlogLikeEntry>
  ): Record<GroupKey, BlogLikeEntry[]> {
    const result: Record<GroupKey, BlogLikeEntry[]> = {};

    for (let i = 0; i < posts.length; i++) {
      const item = posts[i];
      const groupKey = groupFunction(item, i);

      if (!result[groupKey]) {
        result[groupKey] = [];
      }

      result[groupKey].push(item);
    }

    return result;
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
   * 文章 URL：`/{collection}/{slug}`（如 `/posts/...`、`/briefs/...`）。frontmatter `slug` 按元数据原样使用（仅 trim）；未指定时由文件名去掉 `YYYY-MM-DD-` 前缀，整段再 trim（不作 kebab-case）。
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

  /**
   * 列表卡片用站点/分类图标：`public/favicons/`。
   *
   * - `http(s)://...`：原样
   * - 以 `/` 开头：根相对原样
   * - 否则视为 `favicons` 内文件名（可含子路径段），解析为 `/favicons/{ref}`
   */
  static resolveFaviconRef(raw: string | undefined | null): string | undefined {
    const t = typeof raw === "string" ? raw.trim() : "";
    if (!t) return undefined;
    if (PostUtils.isHttpUrl(t)) return t;
    if (t.startsWith("/")) {
      return t;
    }
    const rel = t.replace(/\\/g, "/").replace(/^(\.\/)+/, "");
    if (!rel || rel.split("/").some(s => s === ".." || s === "")) {
      return undefined;
    }
    return `/favicons/${rel}`;
  }

  /**
   * 根相对路径（如 `/favicons/x.svg`）是否在仓库 `public/` 下存在对应文件（构建时 `fs` 校验）。
   */
  static publicRootFileExists(rootRelative: string): boolean {
    const t = rootRelative.trim();
    if (!t.startsWith("/")) return false;
    const rel = t.replace(/^\/+/, "");
    if (!rel || rel.split("/").some(s => s === ".." || s === "")) {
      return false;
    }
    const abs = path.join(process.cwd(), "public", rel);
    try {
      return fs.existsSync(abs) && fs.statSync(abs).isFile();
    } catch {
      return false;
    }
  }

  /**
   * 文章列表/详情：`favicon` 优先（外链或站内且 `public/` 存在）；否则首个有效 `categories` 对应 `/favicons/{slug}.svg`；
   * **未设置分类或全部为空** → `/favicons/blank.svg`；分类 svg 不存在则回退 `blank.svg`。
   */
  static resolveArticleListFaviconPath(
    favicon: string | undefined | null,
    categories: string[] | undefined | null
  ): string {
    const raw = typeof favicon === "string" ? favicon.trim() : "";
    if (raw) {
      const resolved = PostUtils.resolveFaviconRef(raw);
      if (resolved) {
        if (PostUtils.isHttpUrl(resolved)) {
          return resolved;
        }
        if (
          resolved.startsWith("/") &&
          PostUtils.publicRootFileExists(resolved)
        ) {
          return resolved;
        }
      }
    }

    let slug: string | null = null;
    for (const c of categories ?? []) {
      const s = trimUrlSegment(c);
      if (s) {
        slug = s;
        break;
      }
    }
    if (!slug) {
      return FAVICON_BLANK_PATH;
    }

    const candidate = `/favicons/${slug}.svg`;
    return PostUtils.publicRootFileExists(candidate)
      ? candidate
      : FAVICON_BLANK_PATH;
  }

  /**
   * 列表 Card `<img src>`：外链原样，站内根相对经 {@link siteImageHref}。
   */
  static resolveArticleListFaviconImgSrc(
    favicon: string | undefined | null,
    categories: string[] | undefined | null
  ): string {
    const p = PostUtils.resolveArticleListFaviconPath(favicon, categories);
    return PostUtils.isHttpUrl(p) ? p : siteImageHref(p);
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
    formatLinkLine("博客", "/posts", "博客目录长文时间线（content/posts）"),
    formatLinkLine("周报", "/briefs", "Weekly notes listing"),
    formatLinkLine("Wiki", "/wiki", "Wiki notes listing"),
    formatLinkLine("Tags", "/tags", "Tag index"),
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
    "- Canonical article URLs use top-level prefixes: /posts/, /briefs/, /wiki/ (match content type).",
    "- These pages are the primary source of truth; tag, archive, feed, and search pages are navigational.",
    "- Use /tags/ for topical browsing; there is no separate category taxonomy.",
  ];

  return `${lines.join("\n")}\n`;
}

// --- 聚合条目日期（Card mode=feed 与 formatFeedDate；构建时相对「当前」时间）---

function formatDateYYYYMMDD(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** 今年内返回相对时间（中文），否则返回 YYYY-MM-DD */
export function formatFeedDate(
  value: string | number | null | undefined
): string {
  if (value == null || value === "") return "日期未知";
  const d = new Date(value);
  if (Number.isNaN(d.getTime()))
    return typeof value === "string" ? value : "日期未知";
  const now = new Date();
  if (d.getFullYear() !== now.getFullYear()) return formatDateYYYYMMDD(d);
  const diffMs = now.getTime() - d.getTime();
  if (diffMs < 0) return formatDateYYYYMMDD(d);
  if (diffMs < 60 * 1000) return "刚刚";
  if (diffMs < 60 * 60 * 1000)
    return `${Math.floor(diffMs / (60 * 1000))} 分钟前`;
  if (diffMs < 24 * 60 * 60 * 1000)
    return `${Math.floor(diffMs / (60 * 60 * 1000))} 小时前`;
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (
    d.getFullYear() === yesterday.getFullYear() &&
    d.getMonth() === yesterday.getMonth() &&
    d.getDate() === yesterday.getDate()
  ) {
    return "昨天";
  }
  return `${Math.floor(diffMs / (24 * 60 * 60 * 1000))} 天前`;
}

// --- content/pages（about 等静态 Markdown 页）---

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

  frontmatterStr.split("\n").forEach(line => {
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

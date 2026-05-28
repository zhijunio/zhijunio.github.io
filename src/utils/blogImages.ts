/**
 * 博客图片：CDN / 根相对 URL、remark 图片目录、rehype 正文 img 处理。
 */

import { CDN_IMAGES_BASE, CDN_ORIGIN } from "../config";

const isProd = import.meta.env.PROD;
const cdnRoot = CDN_ORIGIN.replace(/\/$/, "");

function normalizePath(ref: string): string {
  const t = ref.trim();
  if (!t || /^https?:\/\//i.test(t) || t.startsWith("//")) return t;
  return t.startsWith("/") ? t : `/${t}`;
}

export function getImagesAssetBase(): string {
  return isProd ? CDN_IMAGES_BASE : "/images";
}

export function devLocalImageRef(href: string): string {
  const t = href.trim();
  if (!t || isProd || !/^https?:\/\//i.test(t)) return t;
  try {
    const u = new URL(t);
    if (u.origin === new URL(CDN_ORIGIN).origin) {
      return `${u.pathname}${u.search}${u.hash}`;
    }
  } catch {
    /* ignore */
  }
  return t;
}

export function siteImageHref(pathOrUrl: string): string {
  const path = normalizePath(pathOrUrl);
  if (!path || /^https?:\/\//i.test(path)) return path;
  if (isProd && path.startsWith("/images/")) return `${cdnRoot}${path}`;
  return path;
}

export function publicImageAbsoluteUrl(
  ref: string,
  siteOrigin: string
): string {
  const path = normalizePath(ref);
  if (!path) return "";
  if (/^https?:\/\//i.test(path)) return path;
  if (path.startsWith("/images/")) {
    return isProd ? `${cdnRoot}${path}` : new URL(path, siteOrigin).href;
  }
  return new URL(path, siteOrigin).href;
}

type VfileLike = {
  data?: {
    astro?: { frontmatter?: Record<string, unknown> };
    frontmatter?: Record<string, unknown>;
  };
};

type MdastNode = { type?: string; url?: string; children?: unknown[] };

function frontmatterFromFile(
  file: VfileLike
): Record<string, unknown> | undefined {
  return (
    file.data?.astro?.frontmatter ??
    (file.data?.frontmatter as Record<string, unknown> | undefined)
  );
}

function imageDirFromFile(file: VfileLike): string {
  const fm = frontmatterFromFile(file);
  return typeof fm?.imageDir === "string" ? fm.imageDir.trim() : "";
}

/** 注入 `imageDir` 并去掉正文图片 URL 中与 slug 重复的前缀 */
export function remarkBlogImages() {
  return (tree: unknown, file: VfileLike) => {
    const fm = frontmatterFromFile(file);
    if (fm && typeof fm === "object") {
      const slug = typeof fm.slug === "string" ? fm.slug.trim() : "";
      if (slug) fm.imageDir = slug;
    }

    const dir = imageDirFromFile(file);
    if (!dir) return;

    const walk = (node: unknown): void => {
      if (!node || typeof node !== "object") return;
      const n = node as MdastNode;
      if (n.type === "image" && typeof n.url === "string") {
        let u = n.url.trim();
        if (
          u &&
          !u.startsWith("/") &&
          !/^https?:\/\//i.test(u) &&
          !u.startsWith("../")
        ) {
          u = u.replace(/^\.\//, "");
          const prefix = `${dir}/`;
          let guard = 0;
          while (u.startsWith(prefix) && guard++ < 16) {
            u = u.slice(prefix.length);
          }
          n.url = u;
        }
      }
      const kids = n.children;
      if (Array.isArray(kids)) for (const c of kids) walk(c);
    };
    walk(tree);
  };
}

type HastElement = {
  type: "element";
  tagName: string;
  properties?: Record<string, unknown>;
  children?: HastChild[];
};

type HastChild =
  | HastElement
  | { type: string; children?: HastChild[] }
  | unknown;

type HastRoot = { type: "root"; children?: HastChild[] };

function walkRehypeImg(
  node: HastChild | HastRoot | undefined,
  state: { first: boolean }
): void {
  if (!node || typeof node !== "object") return;
  const n = node as Record<string, unknown>;
  if (n.type === "element" && n.tagName === "img" && n.properties) {
    const propsEl = n as HastElement;
    const props: Record<string, unknown> = {
      ...(propsEl.properties as Record<string, unknown>),
      decoding: "async",
    };
    const srcRaw = props.src;
    if (typeof srcRaw === "string" && srcRaw.trim()) {
      props.src = siteImageHref(srcRaw.trim());
    }
    const altRaw = props.alt;
    const altMissing =
      altRaw === undefined || altRaw === null || String(altRaw).trim() === "";
    if (altMissing) {
      const src = String(props.src ?? "");
      const file =
        src
          .split("/")
          .pop()
          ?.replace(/\.(webp|png|jpe?g|gif)$/i, "") ?? "";
      props.alt = file.replace(/[-_]+/g, " ").trim() || "文章配图说明图";
    }
    if (state.first) {
      state.first = false;
      props.fetchpriority = "high";
      props.loading = "eager";
    } else {
      props.loading = "lazy";
    }
    propsEl.properties = props;
  }
  const kids = n.children as HastChild[] | undefined;
  if (Array.isArray(kids)) for (const c of kids) walkRehypeImg(c, state);
}

export function rehypeArticleContentImages() {
  return (tree: HastRoot) => {
    walkRehypeImg(tree, { first: true });
  };
}

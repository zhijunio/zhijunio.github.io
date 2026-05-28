/**
 * 博客图片：CDN / 根相对 URL、remark 注入与去重、rehype 正文 img 处理。
 */

import { CDN_IMAGES_BASE, CDN_ORIGIN } from "../config";

/** 生产构建：`/images/` 等资源使用 CDN；`astro dev` 为 false，走同源根相对 */
export function shouldUseCdnForPublicImagePaths(): boolean {
  return import.meta.env.PROD;
}

function normalizeCdnOrigin(): string {
  return CDN_ORIGIN.replace(/\/$/, "");
}

function imageCdnOrigin(): string {
  try {
    return new URL(CDN_ORIGIN).origin;
  } catch {
    return "";
  }
}

export const LOCAL_IMAGES_PUBLIC_BASE = "/images";

export function getImagesAssetBase(): string {
  return shouldUseCdnForPublicImagePaths()
    ? CDN_IMAGES_BASE
    : LOCAL_IMAGES_PUBLIC_BASE;
}

export function devLocalImageRef(href: string): string {
  const t = typeof href === "string" ? href.trim() : "";
  if (!t || shouldUseCdnForPublicImagePaths()) return t;
  if (!/^https?:\/\//i.test(t)) return t;
  const o = imageCdnOrigin();
  if (!o) return t;
  try {
    const u = new URL(t);
    if (u.origin === o) return `${u.pathname}${u.search}${u.hash}`;
  } catch {
    /* ignore */
  }
  return t;
}

export function siteImageHref(pathOrUrl: string): string {
  const t = (pathOrUrl ?? "").trim();
  if (!t) return t;
  if (/^https?:\/\//i.test(t) || t.startsWith("//")) return t;
  const path = t.startsWith("/") ? t : `/${t}`;
  if (!shouldUseCdnForPublicImagePaths()) {
    return path;
  }
  if (path.startsWith("/images/")) {
    return `${normalizeCdnOrigin()}${path}`;
  }
  return path;
}

export function publicImageAbsoluteUrl(
  ref: string,
  siteOrigin: string
): string {
  const t = (ref ?? "").trim();
  if (!t) return "";
  if (/^https?:\/\//i.test(t)) return t;
  const path = t.startsWith("/") ? t : `/${t}`;
  if (path.startsWith("/images/")) {
    if (!shouldUseCdnForPublicImagePaths()) {
      return new URL(path, siteOrigin).href;
    }
    return `${normalizeCdnOrigin()}${path}`;
  }
  return new URL(path, siteOrigin).href;
}

type VfileLike = {
  data?: {
    astro?: { frontmatter?: Record<string, unknown> };
    frontmatter?: Record<string, unknown>;
  };
};

export function remarkInjectImageDir() {
  return (_tree: unknown, file: VfileLike) => {
    const apply = (fm: Record<string, unknown> | undefined) => {
      if (!fm || typeof fm !== "object") return;
      const slug = typeof fm.slug === "string" ? fm.slug.trim() : "";
      if (!slug) return;
      fm.imageDir = slug;
    };
    apply(file.data?.astro?.frontmatter);
    apply(file.data?.frontmatter as Record<string, unknown> | undefined);
  };
}

type MdastNode = { type?: string; url?: string; children?: unknown[] };

function imageDirFromFile(file: VfileLike): string {
  const fm =
    file.data?.astro?.frontmatter ?? file.data?.frontmatter ?? undefined;
  return typeof fm?.imageDir === "string" ? fm.imageDir.trim() : "";
}

export function remarkStripLeadImageDirDup() {
  return (tree: unknown, file: VfileLike) => {
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

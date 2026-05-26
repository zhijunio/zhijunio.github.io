/**
 * 图片 CDN 开关与 URL 解析（Layout、PostDetails、Photosuite、rehype）。
 */

import { CDN_IMAGES_BASE, CDN_ORIGIN } from "../../config";

/** 生产构建：`/images/` 等资源使用 {@link CDN_ORIGIN}；`astro dev` 为 false，走同源根相对 */
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

/** 与 `public/images`、桶内 `images/` 对应的根路径（无末尾斜杠） */
export const LOCAL_IMAGES_PUBLIC_BASE = "/images";

/**
 * Photosuite `imageBase`：仅桶前缀；子目录由 remark 从 `slug` 注入的 `imageDir` + Photosuite `join`。
 */
export function getImagesAssetBase(): string {
  return shouldUseCdnForPublicImagePaths()
    ? CDN_IMAGES_BASE
    : LOCAL_IMAGES_PUBLIC_BASE;
}

/** 客户端脚本：生产为 CDN 主机前缀，dev 为空 */
export function getClientImagesHostPrefix(): string {
  return shouldUseCdnForPublicImagePaths() ? normalizeCdnOrigin() : "";
}

/**
 * `astro dev`：把指向 CDN 同源的绝对 URL 压成根相对，便于本地 `public/`。
 */
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

/** `<img src>` 等：外链原样；`/images/` 在生产改为 CDN 绝对 URL */
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

/** OG / JSON-LD：绝对 URL；`/images/...` 在 dev 用 siteOrigin，prod 用 CDN */
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

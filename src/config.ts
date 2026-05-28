/**
 * 站点配置。图片 CDN 见 `src/utils/blogImages.ts`。
 */
export const CDN_ORIGIN = "https://cos.zhijun.io";

export const CDN_IMAGES_BASE = `${CDN_ORIGIN}/images`;

export const SITE = {
  website: "https://blog.zhijun.io",
  author: "ZhiJun",
  description:
    "记录 AI、Java、MicroServices、Architecture、Kubernetes 的博客",
  title: "ZhiJun Blog",

  logo: "/images/avatar.webp",

  googleSiteVerification: "702mzR8WJvXKVdS3ergTkQEIWAMuwniGMAIeE6wPRhc",
  bingSiteVerification: "5995FAD202DE5A364D652266E4C4E0E0",

  postPerIndex: 10,

  lang: "zh-CN",
  timezone: "Asia/Shanghai",

  defaultOgImage: "/og.webp",

  /** 自托管 Umami；scriptUrl 为反广告拦截自定义脚本名 */
  umami: {
    enabled: true,
    websiteId: "2311be4b-ebe4-4a94-9c69-b2e841584d0d",
    scriptUrl: "https://umami.zhijun.io/random-string.js",
  },
} as const;

/** 浏览器标签页 `<title>`：首页仅站点名，其余为「页面标题 | 站点名」。 */
export function formatDocumentTitle(pageTitle?: string | null): string {
  const t = pageTitle?.trim();
  if (!t || t === SITE.title) return SITE.title;
  return `${t} | ${SITE.title}`;
}

/**
 * 站点配置。图片 CDN 见 `src/utils/blogImages.ts`。
 */
export const CDN_ORIGIN = "https://cos.zhijun.io";

export const CDN_IMAGES_BASE = `${CDN_ORIGIN}/images`;

export const SITE = {
  website: "https://blog.zhijun.io",
  author: "ZhiJun",
  description:
    "记录 Java、Spring、MicroServices、Architecture、Kubernetes、DevOps、AI 编码工具、架构与个人周报的博客",
  title: "ZhiJun Blog",

  logo: "/images/avatar.webp",

  googleSiteVerification: "702mzR8WJvXKVdS3ergTkQEIWAMuwniGMAIeE6wPRhc",
  bingSiteVerification: "5995FAD202DE5A364D652266E4C4E0E0",

  postPerIndex: 10,

  lang: "zh-CN",
  timezone: "Asia/Shanghai",

  defaultOgImage: "/og.webp",
} as const;

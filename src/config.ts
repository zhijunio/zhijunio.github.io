/**
 * 对象存储自定义域名（R2 / COS，无末尾斜杠）。
 * 图片 dev/prod 与 CDN 开关见 `src/utils/blogImages/`。
 */
export const CDN_ORIGIN = "https://cos.zhijun.io";

/** 桶内 `images/` 在 CDN 上的基址（与 Photosuite 生产环境 `imageBase` 一致） */
export const CDN_IMAGES_BASE = `${CDN_ORIGIN}/images`;

export const SITE = {
  website: "https://blog.zhijun.io",
  author: "ZhiJun",
  description:
    "记录 Java、Spring、MicroServices、Architecture、Kubernetes、DevOps、AI 编码工具、架构与个人周报的博客",
  title: "ZhiJun Blog",

  /** 顶栏标题左侧标识图（根相对路径，如 `/images/avatar.webp`）；留空则不显示 */
  logo: "/images/avatar.webp",

  googleSiteVerification: "702mzR8WJvXKVdS3ergTkQEIWAMuwniGMAIeE6wPRhc",
  bingSiteVerification: "5995FAD202DE5A364D652266E4C4E0E0",

  /** 首页与 /page/N 每页条目数 */
  postPerIndex: 10,

  /** 定时文章发布的时间容差（毫秒） */
  scheduledPostMargin: 15 * 60 * 1000,

  /** 自动生成描述：优先 <!--more-->，否则取前 N 行 */
  genDescriptionMaxLines: 3,
  genDescriptionCount: 200,

  /** 顶栏下方年度进度条 */
  showYearProgress: true,

  lang: "zh-CN",
  langOg: "zh_CN",
  timezone: "Asia/Shanghai",
  icp: "",

  /** Open Graph 分享图（静态 defaultImage，无构建期按路由生成） */
  og: {
    enabled: true,
    defaultImage: "/og.webp",
  },
} as const;

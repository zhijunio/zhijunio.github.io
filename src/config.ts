/**
 * 对象存储自定义域名（R2 / COS，无末尾斜杠）。
 * - **dist**：KaTeX、lazy-list 等 CSS/JS
 * - **图片**：dev/prod 与 CDN 开关见 `src/utils/blogImages/`（`shouldUseCdnForPublicImagePaths`、`siteImageHref` 等）
 */
export const CDN_ORIGIN = "https://cos.chensoul.cc";

/** 桶内 `images/` 在 CDN 上的基址（与 Photosuite 生产环境 `imageBase` 一致） */
export const CDN_IMAGES_BASE = `${CDN_ORIGIN}/images`;

/** KaTeX 与 `public/dist/katex` 同步上传后的样式表 URL */
export const CDN_KATEX_STYLESHEET = `${CDN_ORIGIN}/dist/katex/0.16.38/dist/katex.min.css`;

export const SITE = {
  website: "https://blog.chensoul.cc",
  author: "ChenSoul",
  description:
    "记录 Java、Spring、MicroServices、Architecture、Kubernetes、DevOps、AI 编码工具、架构与个人周报的博客",
  title: "ChenSoul Blog",

  googleSiteVerification: "702mzR8WJvXKVdS3ergTkQEIWAMuwniGMAIeE6wPRhc",
  bingSiteVerification: "5995FAD202DE5A364D652266E4C4E0E0",

  /** 是否启用浅色/深色模式切换功能 */
  lightAndDarkMode: true,

  /**
   * 首页各栏（博客 / 周报 ）展示的最近条目数
   */
  postPerIndex: 12,

  /**
   * 定时文章发布的时间容差（毫秒）
   *
   * 作用：判断一篇文章是否"即将发布"
   * - 如果当前时间 + 容差 > 文章发布时间，则显示该文章
   * - 默认 15 分钟，避免因服务器时间差异导致文章提前显示
   */
  scheduledPostMargin: 15 * 60 * 1000, // 15 minutes

  /**
   * 自动生成描述时处理的最大行数
   *
   * 用于从文章内容提取摘要：
   * - 优先查找 <!--more--> 标记
   * - 若未找到，则处理前 N 行内容
   */
  genDescriptionMaxLines: 3,

  /**
   * 当未找到 more 标记时，提取的字符数量
   *
   * 作为自动生成描述的备选方案
   */
  genDescriptionCount: 200,

  /** 是否在顶栏下方显示年度进度条 */
  showYearProgress: true,

  /**
   * HTML 页面的 lang 属性值
   *
   * 影响：
   * - 浏览器的翻译功能
   * - 屏幕阅读器的语言选择
   * - 搜索引擎的语言识别
   */
  lang: "zh-CN",

  /**
   * Open Graph 的 locale 标签
   *
   * 格式：language_TERRITORY（如 zh_CN、en_US）
   * 用于社交媒体分享时显示正确的语言环境
   * @see https://ogp.me/#optional
   */
  langOg: "zh_CN",

  /**
   * 全局默认时区
   *
   * 格式：IANA 时区标识符（如 Asia/Shanghai、Asia/Taipei）
   * 用于统一所有日期时间的显示格式
   * @see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
   */
  timezone: "Asia/Shanghai",

  /**
   * 中国大陆 ICP 备案号
   *
   * 根据中国法律，托管在大陆的网站必须显示备案号
   */
  icp: "",

  /**
   * Open Graph / Twitter 分享图
   *
   * - **enabled**：为 false 时不输出 og:image、twitter:image 及 JSON-LD 中的文章 image
   * - **dynamic**：为 true 时在构建阶段用 Satori 生成 `/og/` 下各路由 PNG，且未传 `ogImage` 时默认图按当前页 URL 指向 `/og/...`；为 false 时不生成 PNG，默认一律用 **defaultImage**
   * - **defaultImage**：根相对路径（如 `/images/og.webp`，对应 `public/images/og.webp`）；Layout 会结合站点 origin 生成 og 绝对 URL，开发环境用当前 dev 域名
   */
  og: {
    enabled: true,
    dynamic: false,
    defaultImage: "/images/og.webp",
  },

  /**
   * 页脚社交链接（图标 + 链接）
   *
   * icon 需与 SocialIcon 支持的 name 一致：github | rss | twitter | x | linkedin | facebook | mail | telegram | whatsapp | pinterest
   */
  socialLinks: [
    { name: "GitHub", url: "https://github.com/zhijunio", icon: "github" },
    { name: "Twitter", url: "https://twitter.com/zhijunio", icon: "twitter" },
    { name: "Telegram", url: "https://t.me/zhijunio", icon: "telegram" },
    { name: "Email", url: "mailto:zhijun.lab@gmail.com", icon: "mail" },
    { name: "RSS", url: "/rss.xml", icon: "rss" },
  ],

  giscus: {
    enabled: true,
  },

  umami: {
    enabled: true,
    websiteId: "2311be4b-ebe4-4a94-9c69-b2e841584d0d",
    scriptUrl: "https://umami.chensoul.cc/random-string.js",
  },

  lazyListJsUrl: `${CDN_ORIGIN}/dist/lazy-list.js`,

  /**
   * 聚合 / Feeds 页（友联博客最新文章聚合，非本站 RSS 订阅地址）。
   * 构建时读取 `public/data/feeds.json`，列表一次性输出全部条目。
   */
  feeds: {
    enabled: true,
    navLabel: "聚合",
    /** 聚合 JSON 路径（CI 写入；页面构建时读取） */
    dataSourceUrl: "/data/feeds.json",
    /** 无头像时使用的默认图（根相对，对应 `public/favicons/rss.svg`） */
    fallbackAvatarUrl: "/favicons/rss.svg",
  },
} as const;

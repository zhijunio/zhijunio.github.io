# ZhiJun Blog

**ZhiJun Blog** 是一个基于 **Astro 6 + Tailwind CSS 4** 构建的个人技术博客，面向中文技术内容（Java、Spring、微服务、架构、Kubernetes、DevOps）。

## 技术栈

| 类别     | 技术                            |
| -------- | ------------------------------- |
| 框架     | Astro 6.x                       |
| 样式     | Tailwind CSS 4（via Vite 插件） |
| 包管理   | pnpm                            |
| 语言     | TypeScript                      |
| 节点版本 | Node.js 22+                     |
| 构建输出 | 纯静态站点（SSG）               |

## 目录结构

```
zhijunio.github.io/
├── content/
│   ├── tech/                # 长文
│   ├── weekly/              # 周报
│   └── about.md             # 关于页内容
├── src/
│   ├── assets/              # 图标等构建内资源
│   ├── components/
│   ├── layouts/
│   ├── pages/               # 路由与端点
│   ├── styles/
│   ├── utils/               # postUtils、blogImages/ 等
│   ├── config.ts
│   ├── content.config.ts    # 集合与 Zod schema
│   └── (Cloudflare 重定向见 public/_redirects)
├── public/
│   ├── images/              # 文章配图等
│   ├── _headers
│   └── _redirects
├── scripts/                 # 辅助脚本（如 convert-to-webp）
├── .github/workflows/       # CI（build + CDN 发布）
├── astro.config.ts
└── package.json
```

## 核心集成与插件

### Astro 集成

- `@astrojs/mdx` — MDX 支持
- `@astrojs/rss` — RSS 订阅
- `astro-expressive-code` — 代码语法高亮（One Dark Pro + One Light 主题）
- `astro-mermaid` — Mermaid 图表
- `astro-compressor` — Gzip + Brotli 压缩
- `@zokki/astro-minify` — CSS/HTML 压缩
- `@critters-rs/astro` — CSS Critical Path 内联
- `photosuite` — 图片展示套件

### Markdown Pipeline

- `remark-math` + `rehype-katex` — LaTeX 数学公式
- `rehype-slug` + `rehype-autolink-headings` — 标题锚点
- `rehype-external-links` — 外链处理（`target="_blank"`）
- `rehype-wrap-all` — 响应式表格包裹
- `rehype-rewrite` — 图片懒加载

## 内容结构

### 文章 Frontmatter

```yaml
title: "文章标题" # 必填
slug: "custom-url-slug" # 必填，URL 路径片段（与 public/images/{slug}/ 对应）
description: "文章描述" # 可选，用于 meta description 和 SEO
date: 2026-02-26 08:00:00+08:00 # 必填
tags: [Java, Spring] # 默认 ["Others"]
draft: false # true 则排除构建
math: false # 启用 KaTeX
mermaid: false # 启用 Mermaid
comments: true # 需 SITE.giscus.enabled 为 true 才显示评论；设为 false 可关单篇
banner: "01.webp" # 可选，正文横幅图（拼到 public/images/{slug}/；有 banner 时用作 OG 图）
```

### 文章 URL 规则

```
/posts/{slug}
```

## 第三方服务

| 服务                      | 用途                                               |
| ------------------------- | -------------------------------------------------- |
| Giscus                    | 基于 GitHub Discussions 的评论系统                 |
| Umami (`umami.zhijun.io`) | 访问统计                                           |
| Pagefind                  | 本地全文搜索                                       |
| COS (`cos.zhijun.io`)     | 图片 CDN（生产环境 `/images/` 经 `siteImageHref`） |

在 [`src/config.ts`](./src/config.ts) 中可用 `SITE.giscus.enabled`、`SITE.umami.enabled` 全站开关。

## 静态资源

| 路径                | 说明                          |
| ------------------- | ----------------------------- |
| `public/images/`    | 文章配图等静态资源            |
| `public/_redirects` | Cloudflare 重定向（手动维护） |

## SEO 与机器入口

- 自定义 `sitemap.xml`：由 [src/pages/sitemap.xml.ts](./src/pages/sitemap.xml.ts) 动态生成，不依赖 `@astrojs/sitemap`
- `robots.txt`：由 [src/pages/robots.txt.ts](./src/pages/robots.txt.ts) 动态生成，默认指向 `https://blog.zhijun.io/sitemap.xml`
- `llms.txt`：由 [src/pages/llms.txt.ts](./src/pages/llms.txt.ts) 动态生成，提供简版机器入口
- 页面级索引控制：文章页、首页、列表页保持可索引
- 结构化数据：文章页输出 `BlogPosting`，首页输出 `WebSite`，其他页面按需输出 `CollectionPage` / `WebPage` / `AboutPage`

## 开发命令

```bash
pnpm dev              # 启动开发服务器（热重载，默认 --host 可局域网访问）
pnpm build            # 类型检查 + 构建 + Pagefind 索引
pnpm preview          # 预览生产构建（构建后本地看效果，通常比 dev 快）

pnpm lint             # ESLint 检查
pnpm format           # Prettier 格式化
pnpm format:check     # 检查格式（不写入）

pnpm md:check         # Markdown Lint 检查
pnpm md:fix           # Markdown 自动修复

pnpm convert-to-webp  # jpg/png → webp（rotate、长边≤1920 后编码，见 scripts/convert-to-webp.mjs）
pnpm images:sync      # rclone 同步 public/images 等到 R2 CDN
pnpm images:publish   # 本地手动 webp + rclone
```

## 功能亮点

- ✅ **深色/浅色模式**（持久化到 `localStorage`，系统偏好为 fallback）
- ✅ **OG 图片自动生成**（生产环境，Satori + Sharp 渲染）
- ✅ **计划发布支持**（15 分钟时间容差，避免时区误差）
- ✅ **全文搜索**（Pagefind，离线本地搜索）
- ✅ **数学公式**（KaTeX）
- ✅ **Mermaid 图表**
- ✅ **响应式表格**
- ✅ **返回顶部按钮**

## CI/CD

- `.github/workflows/ci.yml`：
  - **build**：每次 push/PR 运行 `lint → format:check → md:check → build`
  - **publish-cdn**：push 到 `main` 且 `public/images` 等变更时（或手动 `workflow_dispatch`）：
    1. `convert-to-webp` → 若有新 webp 则 bot commit（`[skip ci]`）
    2. `rclone sync` 到 R2 CDN

### CDN 发布（GitHub Actions）

在仓库 **Settings → Secrets and variables → Actions** 添加：

| Secret          | 说明                                                                                            |
| --------------- | ----------------------------------------------------------------------------------------------- |
| `RCLONE_CONFIG` | 本机 `~/.config/rclone/rclone.conf` 里 **`[r2]` remote 整段**（remote 名 `r2`，路径 `cos/...`） |

本地导出示例：

```bash
rclone config file   # 查看配置文件路径
# 复制 [r2] 段（含 type、access_key_id、secret_access_key、endpoint 等）到 Secret
```

也可在 Actions 页 **CI → Run workflow** 手动触发（会执行 publish-cdn 任务）。

遵循 **Conventional Commits** 规范：

```
feat(scope): ...
fix(scope): ...
chore(scope): ...
docs(scope): ...
```

## 许可证

[MIT](./LICENSE)

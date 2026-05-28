# ZhiJun Blog

基于 **Astro 6** 的静态技术博客（中文），文章在 `content/posts/`（`tech/`、`weekly/` 等子目录仅作分类，路由统一为 `/posts/{slug}`）。

## 技术栈

| 类别     | 技术                   |
| -------- | ---------------------- |
| 框架     | Astro 6.x              |
| 样式     | 手写 CSS（`base.css`） |
| 包管理   | pnpm                   |
| 语言     | TypeScript             |
| 构建输出 | 纯静态 SSG             |

## 目录结构

```
├── content/posts/            # 文章（子目录可选，仅分类）
├── content/pages/about.md    # 关于页（`/about` 由 `[slug].astro` 生成）
├── src/components/HomeFeed.astro # 首页列表（滚动加载更多）
├── src/pages/feed/[page].json.ts # 首页分页 JSON（构建期静态）
├── src/styles/feed|post|chrome.css  # 列表/文章/顶栏样式（按需引入）
├── src/components|layouts|pages|utils/
├── public/images/         # 配图（生产走 CDN）
├── scripts/               # 构建辅助与校验
└── astro.config.ts
```

## 文章能力

- **Markdown + Shiki**（`SHIKI_LANGS` 裁剪）
- **Mermaid**：正文含 ` ```mermaid ` 时按需加载
- **Photosuite**：正文含内联图时按需加载
- **代码复制**：正文含围栏代码时按需加载
- **全站**：年进度条、回到顶部、Umami 统计、RSS、sitemap、robots、OG/JSON-LD

列表页（`/`、`/about`）不加载 Mermaid / 复制 / Photosuite；首页向下滚动时请求 `/feed/N.json` 追加列表。

## Frontmatter（节选）

```yaml
title: "标题"
slug: "url-slug"
date: 2026-02-26 08:00:00+08:00
description: "可选"
draft: false
banner: "01.webp" # 相对 public/images/{slug}/
```

URL：`/{collection}/{slug}`（如 `/posts/my-slug`）。无全站 `/posts.html` 归档页。

## 常用命令

```bash
pnpm dev
pnpm build          # 构建并裁剪 dist/images
pnpm ci             # lint + format + check + build（与 CI 一致）
pnpm images:publish # 本地 webp + 同步 R2
```

## 部署与 CDN

- 站点：`SITE.website`（见 `src/config.ts`）
- 图片：`cos.zhijun.io` / `siteImageHref`
- Cloudflare：`public/_redirects`、`_headers`

## CI

`.github/workflows/ci.yml`：push/PR 跑 `pnpm ci`；图片变更时可选 CDN 同步 job。

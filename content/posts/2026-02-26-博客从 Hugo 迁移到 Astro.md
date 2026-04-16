---
title: "博客从 Hugo 迁移到 Astro"
date: 2026-02-26 06:00:00+08:00
slug: from-hugo-to-astro-blog
categories: [ "tech" ]
tags: [ "astro" ]
favicon: "astro.svg"
description: "记录博客从 Hugo 迁移到 Astro 的过程，以及基于 astro-lhasa 主题做过的结构与样式调整，方便后续复盘与参考。"
---

最近将博客从 Hugo 迁移到了 Astro，并选择了 [astro-lhasa](https://github.com/achuanya/astro-lhasa)
做为博客主题，我还对该主题做了一些修改（修改后的主题在 [chensoul/astro-lhasa](https://github.com/zhijunio/astro-lhasa)
）。此文主要记录修改了哪些内容，方便以后查询。

<!--more-->

## 如何统计

为了和 [achuanya/astro-lhasa]((https://github.com/achuanya/astro-lhasa)) 做对比总结修改了哪些内容，我实际执行过的命令是这些：

1. 看本仓库的远程和分支

```bash
cd astro-lhasa && git remote -v && git branch -a && git status --short
```

1. 看最近几次提交

```bash
git log --oneline -5
```

1. 添加上游并拉取

```bash
git remote add upstream https://github.com/achuanya/astro-lhasa.git 2>/dev/null
git fetch upstream main 2>&1
```

1. 和上游的差异统计（文件与行数）

```bash
git diff upstream/main --stat
```

1. 和上游的差异文件列表（含 A/M/D 状态）

```bash
git diff upstream/main --name-status
```

1. 看几个关键文件的 diff

```bash
git diff upstream/main -- src/content.config.ts | head -120
git diff upstream/main -- src/config.ts | head -150
git diff upstream/main -- astro.config.ts | head -80
git diff upstream/main -- src/utils/getPath.ts | head -100
git diff upstream/main -- src/pages/rss.xml.ts | head -80
git diff upstream/main --stat -- src/layouts/PostDetails.astro src/components/Header.astro
```

1. 确认当前页面结构

```bash
find src/pages -name "*.astro" -o -name "*.ts" -o -name "*.md" 2>/dev/null | sort
ls -la src/pages/posts 2>/dev/null || echo "No posts dir"
```

## 主题修改汇总

与上游 [achuanya/astro-lhasa](https://github.com/achuanya/astro-lhasa) 对比后的主题修改汇总（基于
`git diff upstream/main`）。

### 一、内容与路由

#### 1. 文章存放位置

- **上游**：文章在项目根目录 `posts/` 下，按子目录分类（如 `posts/life/`、`posts/technology/`）。
- **当前**：改为 Astro Content Collections，文章放在 **`content/posts/`**，并在 `content.config.ts` 中将 `BLOG_PATH` 设为
  `"content/posts"`。

#### 2. 文章 URL 格式

- **上游**：路径为 `/posts/分类/slug`（目录结构即 URL）。
- **当前**：支持 **带日期的 URL**：`/posts/YYYY/MM/DD/slug`。`getPath.ts` 增加 `date` 参数，若传入日期则生成该格式；文章 slug
  从文件名解析，不再对 slug 做 slugify（避免如 `langchain4j` 被改成 `langchain-4-j`）。

#### 3. 分类逻辑

- **上游**：使用 `config.ts` 中的 `categoryOrder` 对分类排序。
- **当前**：改为由 `postUtils.ts`（分类元数据 `CATEGORY_META`） 统一维护分类顺序、中文名称与分类卡片缩略图，分类页和归档页优先按该顺序显示。

#### 4. 已删除的页面与功能

- **删除页面**：
  - `src/pages/feeds/index.astro`（订阅/Feeds 页）
  - `src/pages/guestbook.astro`（留言板）
  - `src/pages/about.md`、`src/pages/favorites.md`（原 Markdown 页面）
- **新增/迁移**：
  - **关于**：`src/pages/about.astro` 从 `content/pages/about.md` 读取并渲染。
- **配置**：移除 `feedsPerIndex`、`feedsPerPage` 等 Feeds 相关配置。

#### 5. 新增页面与资源

- **`src/pages/running.astro`**：跑步/数据页，使用 `public/data/running.json`。
- **`content/pages/about.md`**：关于的正文内容。
- **`public/_headers`**：自定义响应头（如部署用）。
- **`public/data/running.json`**：跑步数据。

### 二、配置与构建

#### 1. 站点与作者信息（`src/config.ts`）

- **website**：`https://blog.lhasa.icu` → `https://blog.zhijun.io`
- **author**：`lhasa` → `chensoul`
- **profile**：`https://github.com/achuanya` → `https://github.com/zhijunio`
- **title**：`游钓四方` → `ChenSoul Blog`
- **description**：改为技术向描述（Java、Spring、MicroServices 等）。
- **timezone**：`Asia/Taipei` → `Asia/Shanghai`
- **icp**：移除备案号（设为空字符串）。
- **postPerIndex**：10 → 8。
- **genDescriptionMaxLines**：30 → 3。
- **Stats 链接**：指向 `stats.zhijun.io/blog.zhijun.io`。
- **imageConfig**：当前使用 `https://cos.zhijun.io` 作为图片 CDN；列表用 `favicon` 字段指向 `/favicons/`，与文章图同属 `/images/` 前缀、优先走站内同源路径。
- **移除**：`displayOptions`（如评论数等）、Feeds 相关配置。

#### 2. Astro 与集成（`astro.config.ts`）

- **图片与构建**：
  - 新增 **astro-mermaid**：支持 Mermaid 图表（`mermaid` frontmatter）。
  - 新增 **@critters-rs/astro**：关键 CSS 内联。
  - **minify**：启用 CSS minify 并开启 `errorRecovery: true`。
- **Expressive Code**：
  - `wrap`：false → true。
  - `overridesByLang` 增加 `gradle,java` 的 `frame: "none"`。
- **Vite**：当前 `optimizeDeps.include` 主要保留 `mermaid`、`dayjs`、`lodash.kebabcase`、`markdown-it` 等实际使用项。

#### 3. 内容 Schema（`src/content.config.ts`）

- **BLOG_PATH**：`"posts"` → `"content/posts"`。
- **categories**：分类显示名、排序与分类卡片缩略图由 `postUtils.ts`（分类元数据 `CATEGORY_META`） 统一控制。
- **新增 frontmatter**：`mermaid: z.boolean().default(false)`。

#### 4. 依赖与脚本（`package.json`、`pnpm-lock.yaml`）

- 依赖变更与上述集成一致（如 mermaid、critters 等加入）；`pnpm-lock.yaml` 有大量变更。

### 三、布局与组件

#### 1. 文章详情（`PostDetails.astro`）

- 文章标题与发布日期移出 `<main>`，放在 Header 与 main 之间的独立 `<section>`。
- 其余结构（正文、标签、上一篇/下一篇、评论）保留在 main 内。

#### 2. 主布局（`Layout.astro`）

- 结构、样式或脚本有调整（约 176 行变更），与上述页面和配置变更一致。

#### 3. 组件

- **Header.astro**：较大调整（约 354 行变更），与导航、leadingTitle、站点标题等逻辑相关。
- **Card.astro**、**Footer.astro**、**Tag.astro**、**YearProgress.astro**、**Artalk.astro**
  ：均有修改，以配合新路由、链接和样式。

### 四、样式

#### 1. 正文排版（`src/styles/typography.css`）

- **h3**：移除 `prose-h3:italic`，h3 不再斜体。
- **标题颜色**：移除 `prose-headings:!text-accent`，h1–h6 不单独设 color，继承正文颜色。
- **行高**：`.prose` 增加 `!leading-relaxed`，增大行间距。

#### 2. 全局样式（`src/styles/global.css`）

- 约 105 行变更，与布局、侧边栏、TOC、代码块等样式相关。

#### 3. 字体（`src/styles/fonts.css`）

- 小范围调整（约 3 行）。

### 五、RSS 与工具函数

#### 1. RSS（`src/pages/rss.xml.ts`）

- **内容**：输出摘要（优先 `<!-- more -->` 前内容，否则正文提要），使用 `getDescription(body)`。
- **实现**：移除 markdown-it、sanitize-html；`pubDate` 使用 `data.updated ?? data.date`；`link` 使用
  `getPath(..., true, data.date)`。
- **条数**：仅保留最近 20 篇；仅非草稿文章。

#### 2. 工具函数

- **getPath.ts**：重写以支持 `date` 参数及 `/posts/YYYY/MM/DD/slug`；slug 从文件名解析并支持去掉日期前缀。
- **getDescription.ts**：用于 RSS 摘要生成。
- **分类相关工具**：当前由 `PostUtils.getUniqueCategories()` 与同文件内的 `CATEGORY_META` / `getCategoryMeta` 协同处理显示名与排序。
- **getSortedPosts.ts**：有调整以配合新数据与路由。
- **categoryImages.ts**：分类图片 URL 等有小幅修改。
- **已删除**：`getBlogMetrics.ts`。

### 六、删除的仓库级文件与内容

- **.github**：删除 CODE_OF_CONDUCT、CONTRIBUTING、FUNDING、ISSUE_TEMPLATE、PULL_REQUEST_TEMPLATE；保留并修改了
  workflows/ci.yml。
- **.claude**：删除 settings.local.json。
- **.mcp.json**：删除。
- **docs**：删除 `redirect.conf`、`reverse-proxy.conf`。
- **posts/**：删除上游全部示例/原博客文章（约 120+ 篇，含 life、technology、outdoors、photo、book、startup、annual-reviews
  等），当前博客内容改为使用 `content/posts/`（可为空或自建）。
- **public**：删除 `feeds.js`、`dev.svg`、`astro-lhasa-lighthouse-score.svg`、`astro-lhasa-v1-thumbnail.svg`、
  `assets/forrest-gump-quote.webp`；修改 favicon、apple-touch-icon、`_redirects`、`lazy-list.js`、`tocbot`、`toggle-theme.js`
  等。

## 总结

总结一下，我的 [chensoul/astro-lhasa](https://github.com/zhijunio/astro-lhasa) 主题，对原主题做了以下改动：

- 删除订阅、留言、日志等页面；收藏页面改为链接页面
- 修改 css 样式，以适应宽屏（web 端，主体部分 960px）；修改文章主题色为蓝色；代码库支持自动换行；调整了导航菜单
- RSS 仅保留最近 20 篇非草稿文章；仅输出摘要，不输出全文 HTML
- 文章链接改为 `/posts/YYYY/MM/DD/slug` 格式
- 添加对 Mermaid 图表 的支持
- 参考[zdyxry.github.io](https://github.com/zdyxry/zdyxry.github.io)
  ，添加[跑步](/running)页面（该页面样式同样做了一些调整）。跑步数据使用 [get_keep_data.py](https://github.com/zhijunio/chensoul/blob/main/get_keep_data.py)
  从 Keep 读取跑步数据并生成与 Garmin 脚本兼容的 [running.json](https://github.com/zhijunio/chensoul/blob/main/data/running.json)。

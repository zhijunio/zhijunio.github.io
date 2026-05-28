# 博客减法与加载性能设计

**日期**：2026-05-28  
**状态**：已批准（2026-05-28 套餐 2 已落地部分见文末修订）  
**优先级**：读者首屏（A）> 构建/部署（B）> 维护（C）

## 背景

ZhiJun Blog 为 Astro 6 静态站，已完成一轮减法（搜索/Pagefind、主题、Footer、Giscus、MDX/KaTeX、Expressive Code、`/posts.html` 等）。本设计在**少动既有功能**前提下，进一步明确页面资源边界，并以构建校验保证**列表页不加载 Mermaid 与代码复制**。

## 目标

| 优先级 | 指标 | 目标 |
|--------|------|------|
| A | 列表页（`/`, `/page/*`, `/about`） | 无 Mermaid、无代码复制相关 JS；LCP 以 HTML + 顶栏为主 |
| A | 文章页 | 正文含 ` ```mermaid ` 才加载 Mermaid；含围栏代码才复制；有内联图才 Photosuite |
| B | `dist` | `_astro` 长期缓存；HTML 短期可再验证；`prune-dist-images` 减小部署体积 |
| C | 约定文档化 + 可选审计脚本 | 新能力默认不进入列表页 |

## 产品约束（已确认）

- **Mermaid**：正文含 ` ```mermaid ` 时启用（remark + `MermaidLoader`）。
- **Photosuite**：保留；仅文章且含内联图时加载。
- **无 `/posts.html`**：发现靠首页分页、RSS、单篇 URL `/{collection}/{slug}`。
- **优化路线**：方案 E — 不改为构建期 Mermaid 出图、不砍 Photosuite；优先 HTML/CSS/缓存/Shiki 体积。
- **首页**：不得加载 Mermaid、代码复制按钮（与 `/page/N`、`/about` 同属列表类页面）。

## 必要功能（保留）

- **页面**：首页分页、`/about`、404、文章详情。
- **订阅与 SEO**：`rss.xml`、`sitemap.xml`、`robots.txt`、canonical / OG / JSON-LD。
- **正文**：Markdown、Shiki（裁剪 `SHIKI_LANGS`）、`remarkPlainShortCode`、外链 `noopener`、表格 responsive wrap。
- **图片**：CDN + Photosuite（条件加载）。

## 架构：页面类型与资源边界

```text
列表页（index.astro, page/[page].astro, about.astro）
  └── Layout.astro
        ├── base.css（全局）
        ├── BackToTop、年进度条（全站）
        └── HomeFeed / 静态内容（无 Mermaid/复制/Photosuite）

文章页（[section]/[...slug]/index.astro → PostDetails.astro）
  └── Layout.astro（同上）
  └── PostDetails.astro
        ├── Photosuite?     hasInlineImages
        ├── MermaidLoader?  正文含 mermaid 围栏
        └── CodeCopyButton? 正文含 ``` 围栏
```

当前实现已满足上述边界；列表页未引用 `PostDetails`。本设计的重点是**防止回归**与**持续优化 HTML/Shiki 体积**。

## 方案选型

曾评估三条路线：

| 路线 | 说明 | 结论 |
|------|------|------|
| ① 保守打磨 | 仅手工优化 Shiki/缓存 | 收益有限 |
| ② 分层页面 + 构建校验 | 文档化边界 + `dist` 断言 | **采用** |
| ③ 双 Layout 硬隔离 | 物理拆分 List/Article Layout | 重构成本偏高，暂不采用 |

## 实现计划

### P0 — 列表页零文章脚本（防回归）

1. 新增 `scripts/assert-list-pages-lean.mjs`：
   - 扫描 `dist/index.html`、`dist/page/*.html`、`dist/about.html`。
   - 断言 HTML 中不包含：`mermaid`、`code-copy-btn`、`photosuite` 客户端特征（可按实际构建产物调整匹配串）。
   - 失败时以非零退出码终止构建。
2. 在 `package.json` 的 `build` 脚本末尾调用：`astro build && node scripts/prune-dist-images.mjs && node scripts/assert-list-pages-lean.mjs`。
3. 更新 `.cursor/rules/blog-product.mdc`：明确列表页不得引入 `PostDetails` 子组件或 Mermaid/CodeCopy。

### P1 — Shiki / HTML 体积（方案 E 主战场）

1. 维护 `SHIKI_LANGS`：用脚本扫描 `content/tech`、`content/weekly` 中围栏语言，与 `astro.config.ts` 同步。
2. 调优 `remarkPlainShortCode` 阈值（`MAX_LINES` / `MAX_CHARS`）在可读性与 HTML 体积间取舍。
3. 文章页：保持 `needsCodeCopy` / `needsMermaid` 与 frontmatter 门控一致，避免误加载。

### P2 — 部署与观测（可选）

1. 保持 `public/_headers`：`/_astro/*` immutable；`/*.html` 短期缓存。
2. 可选为 HTML 增加 `stale-while-revalidate`（需结合 Cloudflare 行为验证）。
3. 抽测 Lighthouse：首页 vs 典型长代码文 vs `mermaid: true` 文，记录 LCP/JS 体积基线。

## 明确不做（本轮）

- 运行时 Mermaid 改为构建期 SVG/PNG（除非后续 A 指标仍不达标）。
- 移除 Umami/Pagefind/Giscus/主题切换；**保留** Photosuite、BackToTop、年进度、代码复制（用户确认）。
- 恢复 `/posts.html`、站内搜索、评论、深色主题。

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 断言字符串过严导致误报 | 仅匹配列表页路径；特征串与 `dist` 实际产物对齐 |
| 未来在 `Layout` 误引文章组件 | 规则文档 + CI 断言 |
| 文章 HTML 过大拖慢 LCP | Shiki 语言裁剪 + 短代码 plain 化 |

## 验收标准

- [ ] `pnpm build` 通过后，列表页 HTML 无 Mermaid/CodeCopy/Photosuite 客户端引用。
- [ ] 文章 `mermaid: true` 仍正常渲染图表。
- [ ] 含内联图文章仍可使用 Photosuite。
- [ ] RSS、sitemap、文章 URL 行为不变。

## 后续（用户自行决定）

- 若需可测试增量计划：使用 **sdd-plan** 生成 `docs/sdd/plans/2026-05-28-blog-minimal-performance.md`。
- 实现由 **sdd-build** 按 P0 → P1 顺序执行。

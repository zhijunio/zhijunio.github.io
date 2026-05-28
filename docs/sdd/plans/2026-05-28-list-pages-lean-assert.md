# 2026-05-28 列表页构建期 lean 断言（P0）

## Intent

落实 brainstorm [2026-05-28-blog-minimal-performance-design.md](../brainstorm/2026-05-28-blog-minimal-performance-design.md) 的 **P0**：在 `pnpm build` 末尾自动检查列表页 HTML，确保 **首页、分页页、about** 不引入 Mermaid、代码复制、Photosuite 客户端资源，防止回归；并更新项目约定文档。

## Out of scope

- P1 Shiki 语言审计脚本、`SHIKI_LANGS` 自动同步（后续增量）
- P2 Lighthouse、`stale-while-revalidate` 调优
- 修改文章页加载逻辑（`PostDetails` 条件加载已符合设计）
- 移除 BackToTop、Umami、Photosuite 功能
- Mermaid 构建期出图或点击加载改造

## Acceptance

- [ ] 存在 `scripts/assert-list-pages-lean.mjs`，在 `dist` 存在时检查以下文件（缺失文件跳过并记 warn，零文件可检查时 exit 1）：
  - `dist/index.html`
  - `dist/about.html`
  - `dist/page/*.html`（若有分页）
- [ ] 上述列表页 HTML 正文**不得**包含下列任一特征（大小写按实现约定，优先匹配构建产物中的稳定串）：
  - Mermaid 客户端：`mermaid.core`、`MermaidLoader`、`pre class="mermaid"`（经 remark 输出的未渲染块）
  - 代码复制：`code-copy-btn`、`CodeCopyButton`
  - Photosuite 客户端：`photosuite/client`、`fancybox`（Photosuite 灯箱依赖）
- [ ] 违规时脚本向 stderr 输出文件路径与命中模式，并以退出码 `1` 结束。
- [ ] `package.json` 的 `build` 为：`astro build && node scripts/prune-dist-images.mjs && node scripts/assert-list-pages-lean.mjs`。
- [ ] `.cursor/rules/blog-product.mdc` 补充：列表页（`index` / `page/[page]` / `about`）不得引用 `PostDetails` 或上述文章专属客户端组件。
- [ ] 在当前仓库上执行 `pnpm build` **成功**（证明现状已 lean）。
- [ ] 文章页行为不变：含 `mermaid: true` 的文章构建产物仍可含 Mermaid 相关 chunk 引用（不在列表页扫描范围内）。

## Test-first checklist

- `scripts/assert-list-pages-lean.test.mjs`（`node:test`，与脚本同目录）
- `scripts/fixtures/list-pages-lean/ok.html`（应通过）
- `scripts/fixtures/list-pages-lean/bad-mermaid.html`（应失败并报告 mermaid 模式）
- `scripts/fixtures/list-pages-lean/bad-copy.html`（应失败并报告 code-copy 模式）

测试要求：在不跑完整 `astro build` 的前提下，对 fixture 调用断言模块/函数；至少覆盖通过、两种失败分支。

## Notes

- 上游设计：`docs/sdd/brainstorm/2026-05-28-blog-minimal-performance-design.md` § P0。
- 本仓库暂无 `test/` 根目录约定；脚本测试与 fixture 均放在 `scripts/` 下。
- 实现时若 `dist/page/` 不存在（文章不足一页），仅检查存在的列表页文件即可。
- 404 页不在本增量扫描范围（非列表/发现页核心路径）。

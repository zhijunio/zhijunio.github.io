# zhijunio.github.io

中文回复，言简意赅。

## 工作方式

- 减少 compile 和 build。优先做最小验证；需要检查时，优先 `pnpm exec astro check`。
- 不要为了小改动跑整站构建；只有在改动确实涉及构建产物或路由行为时才升级验证。
- 保守修改，尽量沿用现有 Astro、Photosuite、内容组织方式。

## 内容模型

- `content/posts/**/*.md` 只放真实文章。
- `content/posts` 下的 `tech/`、`review/` 等子目录仅用于本地整理，不影响文章 URL。
- 不要把 prompt、outline、草稿、生成记录、临时脚本放进 `content/posts`，否则会被内容集合误收录。

## 图片约定

- 文章封面 frontmatter 使用 `cover`，不要使用 `banner`。
- 文章正文图片默认使用相对路径文件名，例如 `![说明](01.webp)`。
- 文章图片资源放在 `public/images/{slug}/`。
- 博客里的文章封面图和正文插图默认都使用 `webp`。
- 生成类中间产物放在 `.baoyu-skills/.../artifacts/` 或其他非 `content/posts` 目录。

## 封面与正文图

- 文章页封面由 `src/layouts/PostDetails.astro` 渲染，DOM id 使用 `post-cover`。
- Photosuite 作用范围是 `#article`；只要文章有封面或正文图片，就应确保加载 Photosuite；列表页不加载。
- Mermaid 只在正文含 ```` ```mermaid ```` 时启用；列表页不加载。
- 代码复制按钮只在文章含围栏代码块时加载；列表页不加载。
- 如果新增图片相关能力，保持与 `src/utils/blogImages.ts` 和 Photosuite 路径解析一致。

## 风格与页面

- 当前博客已做减法，保留克制风格；不要随意加回搜索、主题切换、复杂页脚或重装饰模块。
- 保留年进度条。
- 样式调整优先小步修改现有变量和现有组件，不做无关重构。
- 首页使用首屏 SSR + `/feed/{n}.json` 向下滚动追加；不要恢复 `/page/N` HTML 分页。
- 不要引入 `/posts.html` 归档页；文章入口以首页、RSS、单篇 URL 为主。
- `index`、`about` 这类列表/静态页只加载必要资源，不要带正文增强脚本。
- 已移除并默认保持移除：页脚、TOC、相关文章推荐、社交分享按钮、文章上下篇导航、标签页、分类页、全站搜索、主题切换、Giscus。

## AI 生图技能

- `baoyu-cover-image`、`baoyu-article-illustrator` 在本仓库按项目约定产出 `webp`。
- 生成记录用于复现即可；最终文章只引用 `public/images/{slug}/` 下的资源。

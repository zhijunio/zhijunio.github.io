import { SITE } from "./src/config";
import { buildLegacyPostsRedirects } from "./src/legacyRedirects";
import {
  getImagesAssetBase,
  rehypeArticleContentImages,
  remarkInjectImageDir,
  remarkStripLeadImageDirDup,
} from "./src/utils/blogImages";
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import mdx from "@astrojs/mdx";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeSlug from "rehype-slug";
import rehypeWrapAll from "rehype-wrap-all";
import rehypeExternalLinks from "rehype-external-links";
import expressiveCode, {
  type AstroExpressiveCodeOptions,
} from "astro-expressive-code";
import { pluginLineNumbers } from "@expressive-code/plugin-line-numbers";
import { pluginCollapsibleSections } from "@expressive-code/plugin-collapsible-sections";
import compressor from "astro-compressor";
import { minify } from "@zokki/astro-minify";
import critters from "@critters-rs/astro";
import photosuite from "photosuite";
import mermaid from "./src/utils/quietAstroMermaid";

// Expressive Code syntax highlighting, https://expressive-code.com/reference/configuration/
const expressiveCodeOption: AstroExpressiveCodeOptions = {
  plugins: [pluginLineNumbers(), pluginCollapsibleSections()],
  themes: ["github-dark"],
  defaultProps: {
    wrap: true,
    showLineNumbers: false,
    // Disable wrapped line indentation for terminal languages
    overridesByLang: {
      "bash,ps,sh": { preserveIndent: false },
    },
  },
};

// https://astro.build/config
export default defineConfig({
  site: SITE.website,
  redirects: buildLegacyPostsRedirects(),
  integrations: [
    mermaid({
      theme: "base",
      autoTheme: true,
      mermaidConfig: {
        securityLevel: "loose",
      },
    }),
    photosuite({
      scope: "#article",
      /**
       * 桶前缀见 `getImagesAssetBase`（`blogImages/cdnUrls`）；子目录由 `remarkInjectImageDir` 从 frontmatter `slug` 注入
       */
      imageBase: getImagesAssetBase(),
      exif: false,
    }),
    expressiveCode(expressiveCodeOption),
    mdx(),
    minify({
      css: { minify: true, errorRecovery: true },
      // 关闭 SVG 压缩，避免 astro:build:done 时 public 尚未完全复制到 dist 导致 ENOENT
      svg: false,
    }),
    compressor({ gzip: true, brotli: true }),
    critters({
      publicPath: SITE.website,
      pruneSource: false,
      mergeStylesheets: true,
      // 禁用字体 preload，避免 "preloaded but not used within a few seconds" 警告
      preloadFonts: false,
      // 不将外部 CSS 转为 preload，避免按需样式 "preloaded but not used" 警告
      preload: "None",
    }),
  ],
  markdown: {
    /** `blogImages` remark → Photosuite `imageUrl`（integration 追加） */
    remarkPlugins: [
      remarkMath,
      remarkInjectImageDir,
      remarkStripLeadImageDirDup,
    ],
    rehypePlugins: [
      rehypeKatex,
      rehypeSlug,
      [rehypeAutolinkHeadings, { behavior: "append" }],
      [rehypeExternalLinks, { target: "_blank", rel: "noopener noreferrer" }],
      [
        rehypeWrapAll,
        {
          selector: "table",
          wrapper: "div.responsive-table",
        },
      ],
      rehypeArticleContentImages,
    ],
    // Use ExpressiveCode instead of shiki
    syntaxHighlight: false,
    // shikiConfig: {
    //   // For more themes, visit https://shiki.style/themes
    //   themes: { light: "min-light", dark: "night-owl" },
    //   wrap: true,
    // },
  },
  vite: {
    plugins: [tailwindcss()],
    build: {
      // 提高 chunk 大小警告阈值，避免大型库（如 pagefind）触发警告
      chunkSizeWarningLimit: 1000,
    },
    optimizeDeps: {
      include: ["mermaid", "dayjs", "markdown-it"],
      /**
       * photosuite/client 内部对 fancybox、imageGrid 等为相对路径的动态 import；
       * 打进 .vite/deps 后子 chunk 易在热更/重启后与 hash 失步，浏览器报 504 Outdated Optimize Dep。
       * 排除后主入口仍被正常转换，子模块从包内 dist 直连，避免过时预构建片段。
       */
      exclude: ["@resvg/resvg-js", "photosuite/client"],
    },
    // 开发时预编译常用模块，减轻首屏/热更延迟
    server: {
      warmup: {
        ssrFiles: [
          "./src/layouts/Layout.astro",
          "./src/utils/blogImages/index.ts",
          "./src/utils/postUtils.ts",
          "./src/config.ts",
        ],
      },
    },
  },
  trailingSlash: "ignore",
  build: {
    format: "file", // generate `page.html` instead of `page/index.html`
  },
  compressHTML: true,
  prefetch: false, // 禁用预取，链接点击为整页刷新
  // image: {
  //   // Used for all Markdown images; not configurable per-image
  //   // Used for all `<Image />` and `<Picture />` components unless overridden with a prop
  //   experimentalLayout: "constrained",
  // },
  // experimental: {
  //   responsiveImages: true,
  //   preserveScriptOrder: true,
  // },
});

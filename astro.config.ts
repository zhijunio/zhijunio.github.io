import { SITE } from "./src/config";
import {
  getImagesAssetBase,
  rehypeArticleContentImages,
  remarkInjectImageDir,
  remarkStripLeadImageDirDup,
} from "./src/utils/blogImages";
import { defineConfig } from "astro/config";
import rehypeSlug from "rehype-slug";
import rehypeWrapAll from "rehype-wrap-all";
import rehypeExternalLinks from "rehype-external-links";
import photosuite from "photosuite";
import { remarkMermaid } from "./src/utils/remarkMermaid";
import { remarkPlainShortCode } from "./src/utils/remarkPlainShortCode";

/** 正文围栏代码实际用到的 Shiki 语言（扫描 content/ 统计，不含 mermaid） */
const SHIKI_LANGS = [
  "bash",
  "shell",
  "java",
  "xml",
  "yaml",
  "json",
  "markdown",
  "sql",
  "text",
  "properties",
  "dockerfile",
  "toml",
  "nginx",
  "txt",
  "python",
  "groovy",
  "javascript",
  "powershell",
  "ini",
  "diff",
  "go",
  "http",
  "html",
  "console",
  "php",
  "jsx",
  "lua",
];

export default defineConfig({
  site: SITE.website,
  compressHTML: true,
  /** 关闭 Dev Toolbar，减轻开发态客户端请求并避免 optimizeDeps 504 */
  devToolbar: {
    enabled: false,
  },
  integrations: [
    photosuite({
      scope: "#article",
      imageBase: getImagesAssetBase(),
      exif: false,
    }),
  ],
  markdown: {
    remarkPlugins: [
      remarkMermaid,
      remarkPlainShortCode,
      remarkInjectImageDir,
      remarkStripLeadImageDirDup,
    ],
    rehypePlugins: [
      rehypeSlug,
      [rehypeExternalLinks, { target: "_blank", rel: "noopener noreferrer" }],
      [
        rehypeWrapAll,
        { selector: "table", wrapper: "div.responsive-table" },
      ],
      rehypeArticleContentImages,
    ],
    syntaxHighlight: "shiki",
    shikiConfig: {
      theme: "github-light",
      wrap: true,
      // @ts-expect-error — bundled 语言 id 列表，见 SHIKI_LANGS
      langs: SHIKI_LANGS,
    },
  },
  prefetch: false,
  trailingSlash: "ignore",
  build: { format: "file" },
  vite: {
    optimizeDeps: {
      /** photosuite/client 预构建易在热更后 504 Outdated Optimize Dep */
      exclude: ["photosuite/client", "@resvg/resvg-js"],
    },
  },
});

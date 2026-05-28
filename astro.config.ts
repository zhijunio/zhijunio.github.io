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
    },
  },
  prefetch: false,
  trailingSlash: "ignore",
  build: { format: "file" },
  vite: {
    optimizeDeps: {
      include: ["mermaid"],
      /**
       * photosuite/client 含相对路径动态 import，预构建后热更/重启易 hash 失步 → 504 Outdated Optimize Dep。
       */
      exclude: ["photosuite/client", "@resvg/resvg-js"],
    },
    server: {
      warmup: {
        ssrFiles: [
          "./src/layouts/Layout.astro",
          "./src/utils/postUtils.ts",
          "./src/config.ts",
        ],
      },
    },
  },
});

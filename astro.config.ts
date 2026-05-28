import { SITE } from "./src/config";
import {
  getImagesAssetBase,
  rehypeArticleContentImages,
  remarkInjectImageDir,
  remarkStripLeadImageDirDup,
} from "./src/utils/blogImages";
import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeSlug from "rehype-slug";
import rehypeWrapAll from "rehype-wrap-all";
import rehypeExternalLinks from "rehype-external-links";
import photosuite from "photosuite";
import { remarkMermaid } from "./src/utils/remarkMermaid";

export default defineConfig({
  site: SITE.website,
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
      [rehypeAutolinkHeadings, { behavior: "append" }],
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
  vite: {
    plugins: [tailwindcss()],
    optimizeDeps: { exclude: ["photosuite/client"] },
  },
  build: { format: "file" },
});

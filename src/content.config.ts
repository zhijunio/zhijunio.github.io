/**
 * Astro 内容集合配置文件
 *
 * @fileoverview 四类文章型内容：`posts`（技术/生活等）、`briefs`（周报）、`translation`（译文）、`wiki`（知识库）；共享同一 Zod schema。
 *
 * @see https://docs.astro.build/en/guides/content-collections/
 */

import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";
import { SITE } from "@/config";

/** 普通长文 */
export const POSTS_CONTENT_PATH = "content/posts";

/** 周报 */
export const BRIEFS_CONTENT_PATH = "content/briefs";

/** 译文 */
export const TRANSLATION_CONTENT_PATH = "content/translation";

/** 知识库*/
export const WIKI_CONTENT_PATH = "content/wiki";

/** @deprecated 使用 {@link POSTS_CONTENT_PATH} */
export const BLOG_PATH = POSTS_CONTENT_PATH;

const articleSchema = () =>
  z.object({
    author: z.string().default(SITE.author),
    title: z.string(),
    description: z.string().optional(),
    date: z
      .union([z.date(), z.string()])
      .transform(v =>
        v instanceof Date ? v : new Date(String(v).replace(" ", "T"))
      ),
    updated: z
      .union([z.date(), z.string()])
      .optional()
      .nullable()
      .transform(v => {
        if (v == null) return v;
        return v instanceof Date ? v : new Date(String(v).replace(" ", "T"));
      }),
    timezone: z.string().optional(),
    tags: z.array(z.string()).default(["Others"]),
    categories: z.array(z.string()).default([]),
    draft: z.boolean().optional(),
    comments: z.boolean().default(true),
    math: z.boolean().default(false),
    mermaid: z.boolean().default(false),
    canonicalURL: z.string().optional(),
    favicon: z.string().optional(),
    banner: z.string().optional(),
    slug: z.string().trim().min(1, "slug 不能为空"),
  });

const posts = defineCollection({
  loader: glob({
    pattern: "**/[^_]*.{md,mdx}",
    base: `./${POSTS_CONTENT_PATH}`,
  }),
  schema: articleSchema,
});

const briefs = defineCollection({
  loader: glob({
    pattern: "**/[^_]*.{md,mdx}",
    base: `./${BRIEFS_CONTENT_PATH}`,
  }),
  schema: articleSchema,
});

const wiki = defineCollection({
  loader: glob({
    pattern: "**/[^_]*.{md,mdx}",
    base: `./${WIKI_CONTENT_PATH}`,
  }),
  schema: articleSchema,
});

export const collections = { posts, briefs, wiki };

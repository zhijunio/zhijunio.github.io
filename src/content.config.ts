/**
 * 内容集合：`content/posts` 文章、`content/pages` 静态页。
 */

import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";

export const POSTS_CONTENT_PATH = "content/posts";
export const PAGES_CONTENT_PATH = "content/pages";

const articleSchema = () =>
  z.object({
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
    draft: z.boolean().optional(),
    banner: z.string().optional(),
    slug: z.string().trim().min(1, "slug 不能为空"),
  });

const posts = defineCollection({
  loader: glob({
    pattern: "{tech,weekly}/**/[^_]*.md",
    base: `./${POSTS_CONTENT_PATH}`,
  }),
  schema: articleSchema,
});

const pages = defineCollection({
  loader: glob({
    pattern: "**/[^_]*.md",
    base: `./${PAGES_CONTENT_PATH}`,
  }),
  schema: () =>
    z.object({
      title: z.string(),
      description: z.string().optional(),
    }),
});

export const collections = { posts, pages };

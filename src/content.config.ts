/**
 * `content/posts` 下均为文章；`tech/`、`weekly/` 等子目录仅便于本地分类，不影响 URL 或 schema。
 */

import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";

const postDate = z
  .union([z.date(), z.string()])
  .transform(v =>
    v instanceof Date ? v : new Date(String(v).replace(" ", "T"))
  );

const posts = defineCollection({
  loader: glob({
    pattern: "**/[^_]*.md",
    base: "./content/posts",
  }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: postDate,
    updated: postDate.optional().nullable(),
    draft: z.boolean().optional(),
    banner: z.string().optional(),
    slug: z.string().trim().min(1),
  }),
});

const pages = defineCollection({
  loader: glob({
    pattern: "**/[^_]*.md",
    base: "./content/pages",
  }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
  }),
});

export const collections = { posts, pages };

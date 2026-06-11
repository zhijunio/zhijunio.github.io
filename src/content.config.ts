/**
 * `content/posts` 下均为文章；`tech/`、`review/` 等子目录仅便于本地分类，不影响 URL 或 schema。
 */

import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const contentDate = z
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
    date: contentDate,
    updated: contentDate.optional().nullable(),
    draft: z.boolean().optional(),
    cover: z.string().optional(),
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

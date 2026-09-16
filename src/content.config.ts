/**
 * `content/posts` 下均为文章；`ai/`、`java/`、`iot/`、`ops/`、`arch/`、`notes/` 子目录与 frontmatter `category` 一致，不影响 URL。
 * 对外分类使用 frontmatter `category`：ai / java / iot / ops / arch / notes。
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
    tags: z.array(z.string()).optional(),
    category: z.enum(["ai", "java", "iot", "ops", "arch", "notes"]),
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

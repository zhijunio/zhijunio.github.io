import { getCollection } from "astro:content";
import type { CollectionEntry } from "astro:content";

/** 与 `src/content.config.ts` 中集合名一致；URL 前缀与之一一对应 */
export const BLOG_LIKE_COLLECTIONS = ["posts", "briefs", "wiki"] as const;

export type BlogLikeCollection = (typeof BLOG_LIKE_COLLECTIONS)[number];

export type BlogLikeEntry = CollectionEntry<BlogLikeCollection>;

export async function getAllBlogLike(): Promise<BlogLikeEntry[]> {
  const [posts, briefs, wiki] = await Promise.all([
    getCollection("posts"),
    getCollection("briefs"),
    getCollection("wiki"),
  ]);
  return [...posts, ...briefs, ...wiki];
}

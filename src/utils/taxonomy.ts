/** 标签 / 分类路径（可进客户端；勿依赖 astro:content） */

export function taxonomySlug(name: string): string {
  return name.trim().toLowerCase();
}

export function tagPath(tag: string): string {
  return `/tags/${encodeURIComponent(taxonomySlug(tag))}`;
}

export function categoryPath(slug: string): string {
  return `/categories/${encodeURIComponent(slug)}`;
}

const CATEGORY_LABELS: Record<string, string> = {
  ai: "AI",
  java: "Java",
  iot: "物联网",
  ops: "运维",
  arch: "架构",
  notes: "笔记",
};

export const CATEGORY_ORDER = [
  "ai",
  "java",
  "iot",
  "ops",
  "arch",
  "notes",
] as const;

export function categoryLabel(slug: string): string {
  return CATEGORY_LABELS[slug] ?? slug;
}

/**
 * 从原 `/posts/{slug}` 迁出内容的 301 映射（周报、译文、知识库）。
 * 与 {@link PostUtils.getPath} 的 slug 规则对齐：优先 frontmatter `slug`，否则文件名去扩展名并去掉 `YYYY-MM-DD-` 前缀。
 */
import fs from "node:fs";
import path from "node:path";

function readSlugFromFrontmatter(filePath: string): string | undefined {
  const raw = fs.readFileSync(filePath, "utf8");
  const m = raw.match(/^slug:\s*(.+)$/m);
  if (!m) return undefined;
  return m[1].trim().replace(/^["']|["']$/g, "");
}

function slugFromFilename(filename: string, explicit?: string): string {
  if (explicit) return explicit;
  let slug = filename.replace(/\.(md|mdx)$/, "").trim();
  const datePrefixMatch = slug.match(/^(\d{4}-\d{2}-\d{2})-(.+)$/);
  if (datePrefixMatch) slug = datePrefixMatch[2].trim();
  return slug;
}

export function buildLegacyPostsRedirects(): Record<string, string> {
  /** 原分类索引已下线，统一跳到标签页 */
  const redirects: Record<string, string> = {
    "/categories": "/tags",
  };
  const roots: { dir: string; section: string }[] = [
    { dir: "content/briefs", section: "briefs" },
  ];
  for (const { dir, section } of roots) {
    const full = path.join(process.cwd(), dir);
    if (!fs.existsSync(full)) continue;
    for (const name of fs.readdirSync(full)) {
      if (!name.endsWith(".md") && !name.endsWith(".mdx")) continue;
      if (name.startsWith("_")) continue;
      const fp = path.join(full, name);
      const explicit = readSlugFromFrontmatter(fp);
      const slug = slugFromFilename(name, explicit);
      redirects[`/posts/${slug}`] = `/${section}/${slug}`;
    }
  }
  return redirects;
}

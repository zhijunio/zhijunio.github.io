/**
 * 构建后检查列表页 HTML 不含 Mermaid / 代码复制 / Photosuite 客户端资源。
 */
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** @type {{ id: string; pattern: string }[]} */
export const FORBIDDEN_PATTERNS = [
  { id: "mermaid.core", pattern: "mermaid.core" },
  { id: "MermaidLoader", pattern: "MermaidLoader" },
  { id: "pre.mermaid", pattern: 'pre class="mermaid"' },
  { id: "code-copy-btn", pattern: "code-copy-btn" },
  { id: "CodeCopyButton", pattern: "CodeCopyButton" },
  { id: "photosuite/client", pattern: "photosuite/client" },
  { id: "fancybox", pattern: "fancybox" },
];

/**
 * @param {string} html
 * @param {string} fileLabel
 * @returns {{ id: string; pattern: string }[]}
 */
export function findForbiddenInHtml(html, fileLabel) {
  const hits = [];
  for (const rule of FORBIDDEN_PATTERNS) {
    if (html.includes(rule.pattern)) {
      hits.push(rule);
    }
  }
  if (hits.length) {
    for (const { id, pattern } of hits) {
      console.error(`${fileLabel}: forbidden pattern "${id}" (${pattern})`);
    }
  }
  return hits;
}

/**
 * @param {string} distDir
 * @returns {Promise<string[]>}
 */
export async function collectListPageHtmlPaths(distDir) {
  const paths = [];
  const index = path.join(distDir, "index.html");
  const about = path.join(distDir, "about.html");
  try {
    await readFile(index);
    paths.push(index);
  } catch {
    /* skip */
  }
  try {
    await readFile(about);
    paths.push(about);
  } catch {
    /* skip */
  }
  const pageDir = path.join(distDir, "page");
  try {
    const entries = await readdir(pageDir);
    for (const name of entries) {
      if (name.endsWith(".html")) {
        paths.push(path.join(pageDir, name));
      }
    }
  } catch {
    /* no pagination */
  }
  return paths;
}

/**
 * @param {string} distDir
 * @returns {Promise<{ checked: number; failed: boolean }>}
 */
export async function assertListPagesLean(distDir) {
  const files = await collectListPageHtmlPaths(distDir);
  if (files.length === 0) {
    console.warn("assert-list-pages-lean: no list page HTML found under dist/");
    return { checked: 0, failed: true };
  }
  let failed = false;
  for (const file of files) {
    const html = await readFile(file, "utf8");
    const label = path.relative(process.cwd(), file);
    if (findForbiddenInHtml(html, label).length) {
      failed = true;
    }
  }
  return { checked: files.length, failed };
}

const isMain =
  process.argv[1] &&
  fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);

if (isMain) {
  const distDir = path.join(process.cwd(), "dist");
  const { checked, failed } = await assertListPagesLean(distDir);
  if (failed) {
    process.exit(1);
  }
  console.log(`assert-list-pages-lean: ok (${checked} list page(s) checked)`);
}

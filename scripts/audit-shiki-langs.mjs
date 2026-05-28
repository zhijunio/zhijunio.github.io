/**
 * 对比 content/ 围栏语言与 astro.config.ts 中 SHIKI_LANGS（不含 mermaid）。
 */
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";

const ROOT = path.join(import.meta.dirname, "..");
const CONTENT = path.join(ROOT, "content");
const CONFIG = path.join(ROOT, "astro.config.ts");

const IGNORE_LANGS = new Set(["mermaid"]);
const LANG_ALIASES = { md: "markdown", yml: "yaml", just: "text" };

function extractShikiLangs() {
  const src = readFileSync(CONFIG, "utf8");
  const match = src.match(/const SHIKI_LANGS = \[([\s\S]*?)\];/);
  if (!match) throw new Error("SHIKI_LANGS not found in astro.config.ts");
  return [...match[1].matchAll(/"([^"]+)"/g)].map(m => m[1]);
}

function walkMarkdown(dir, files = []) {
  for (const ent of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) walkMarkdown(full, files);
    else if (ent.name.endsWith(".md")) files.push(full);
  }
  return files;
}

function collectFenceLangs(files) {
  const langs = new Set();
  const re = /^```([a-zA-Z0-9_-]+)/gm;
  for (const file of files) {
    const body = readFileSync(file, "utf8");
    for (const m of body.matchAll(re)) {
      const raw = m[1].toLowerCase();
      if (!IGNORE_LANGS.has(raw)) {
        langs.add(LANG_ALIASES[raw] ?? raw);
      }
    }
  }
  return langs;
}

const shikiLangs = new Set(extractShikiLangs());
const usedLangs = collectFenceLangs(walkMarkdown(CONTENT));

const missingInShiki = [...usedLangs].filter(l => !shikiLangs.has(l)).sort();
const unusedInShiki = [...shikiLangs].filter(l => !usedLangs.has(l)).sort();

let failed = false;
if (missingInShiki.length) {
  failed = true;
  console.error("Content uses langs not in SHIKI_LANGS:", missingInShiki.join(", "));
}
if (unusedInShiki.length) {
  failed = true;
  console.error("SHIKI_LANGS unused in content:", unusedInShiki.join(", "));
}
if (!failed) {
  console.log(
    `audit-shiki-langs: ok (${shikiLangs.size} langs, ${usedLangs.size} used in content)`
  );
} else {
  process.exit(1);
}

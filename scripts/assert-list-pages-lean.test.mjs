import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { test } from "node:test";
import {
  assertListPagesLean,
  findForbiddenInHtml,
} from "./assert-list-pages-lean.mjs";

const fixtureDir = path.join(
  import.meta.dirname,
  "fixtures/list-pages-lean"
);

test("ok fixture passes", async () => {
  const html = await readFile(path.join(fixtureDir, "ok.html"), "utf8");
  assert.equal(findForbiddenInHtml(html, "ok.html").length, 0);
});

test("bad-mermaid fixture fails", async () => {
  const html = await readFile(path.join(fixtureDir, "bad-mermaid.html"), "utf8");
  const hits = findForbiddenInHtml(html, "bad-mermaid.html");
  assert.ok(hits.some(h => h.id === "mermaid.core"));
});

test("bad-copy fixture fails", async () => {
  const html = await readFile(path.join(fixtureDir, "bad-copy.html"), "utf8");
  const hits = findForbiddenInHtml(html, "bad-copy.html");
  assert.ok(hits.some(h => h.id === "code-copy-btn"));
});

test("assertListPagesLean on fixture dir shape", async () => {
  const { checked, failed } = await assertListPagesLean(
    path.join(import.meta.dirname, "fixtures", "nonexistent-dist")
  );
  assert.equal(checked, 0);
  assert.equal(failed, true);
});

/**
 * 将过短的围栏代码块标记为 `text`，减少 Shiki 内联 token 体积。
 * 不处理 mermaid（由 remarkMermaid 负责）。
 */
import type { Parent, Root } from "mdast";
import { visit } from "unist-util-visit";

const MAX_LINES = 2;
const MAX_CHARS = 120;

export function remarkPlainShortCode() {
  return (tree: Root) => {
    visit(tree, "code", (node, _index, parent: Parent | undefined) => {
      if (!parent || node.lang === "mermaid") return;
      if (node.lang === "md") node.lang = "markdown";
      if (node.lang === "just") node.lang = "text";
      const source = node.value ?? "";
      const lineCount = source === "" ? 0 : source.split("\n").length;
      if (lineCount > MAX_LINES || source.length > MAX_CHARS) return;
      node.lang = "text";
    });
  };
}

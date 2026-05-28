/**
 * 将 ```mermaid 代码块转为 `<pre class="mermaid">`，供客户端按需 `mermaid.run()` 渲染。
 */
import type { Parent, Root } from "mdast";
import { visit } from "unist-util-visit";

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function remarkMermaid() {
  return (tree: Root) => {
    visit(tree, "code", (node, index, parent: Parent | undefined) => {
      if (node.lang !== "mermaid" || parent == null || index == null) return;
      const source = node.value?.trim() ?? "";
      parent.children[index] = {
        type: "html",
        value: `<pre class="mermaid">${escapeHtml(source)}</pre>`,
      };
    });
  };
}

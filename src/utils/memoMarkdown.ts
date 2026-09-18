import { createMarkdownProcessor } from "@astrojs/markdown-remark";

let processorPromise: ReturnType<typeof createMarkdownProcessor> | undefined;
const renderedCache = new Map<string, string>();

function withoutHeadline(markdown: string): string {
  const lines = markdown.trim().split(/\r?\n/);
  const first = lines.findIndex(line => line.trim() !== "");
  if (first < 0 || !/^#{1,6}\s+/.test(lines[first].trim())) {
    return lines.join("\n");
  }
  lines.splice(first, 1);
  if (lines[first]?.trim() === "") lines.splice(first, 1);
  return lines.join("\n").trim();
}

export async function renderMemoMarkdown(markdown: string): Promise<string> {
  const cached = renderedCache.get(markdown);
  if (cached) return cached;
  processorPromise ??= createMarkdownProcessor({ syntaxHighlight: false });
  const processor = await processorPromise;
  const result = await processor.render(withoutHeadline(markdown));
  renderedCache.set(markdown, result.code);
  return result.code;
}

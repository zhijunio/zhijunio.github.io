import { createMarkdownProcessor } from "@astrojs/markdown-remark";

let processorPromise: ReturnType<typeof createMarkdownProcessor> | undefined;
const renderedCache = new Map<string, string>();

function withoutHeadline(markdown: string): string {
  const lines = markdown.trim().split(/\r?\n/);
  const headline = lines.findIndex(line => /^#{1,6}\s+/.test(line.trim()));
  if (headline < 0) return markdown;
  lines.splice(headline, 1);
  if (lines[headline]?.trim() === "") lines.splice(headline, 1);
  return lines.join("\n").trim();
}

function preserveSoftBreaks(markdown: string): string {
  const lines = markdown.split("\n");
  let inFence = false;
  return lines
    .map((line, index) => {
      const next = lines[index + 1] ?? "";
      const trimmed = line.trim();
      const nextTrimmed = next.trim();
      if (/^```/.test(trimmed)) inFence = !inFence;
      if (
        !inFence &&
        trimmed &&
        nextTrimmed &&
        !trimmed.startsWith("#") &&
        !trimmed.startsWith("-") &&
        !trimmed.startsWith("*") &&
        !trimmed.startsWith(">") &&
        !/^\d+\.\s/.test(trimmed) &&
        !nextTrimmed.startsWith("#") &&
        !nextTrimmed.startsWith("-") &&
        !nextTrimmed.startsWith("*") &&
        !nextTrimmed.startsWith(">") &&
        !/^\d+\.\s/.test(nextTrimmed)
      ) {
        return `${line}  `;
      }
      return line;
    })
    .join("\n");
}

export async function renderMemoMarkdown(markdown: string): Promise<string> {
  const cached = renderedCache.get(markdown);
  if (cached) return cached;
  processorPromise ??= createMarkdownProcessor({ syntaxHighlight: false });
  const processor = await processorPromise;
  const result = await processor.render(
    preserveSoftBreaks(withoutHeadline(markdown))
  );
  renderedCache.set(markdown, result.code);
  return result.code;
}

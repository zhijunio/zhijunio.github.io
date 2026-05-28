import { SITE } from "@/config";

/** 浏览器标签页 `<title>`：首页仅站点名，其余为「页面标题 | 站点名」。 */
export function formatDocumentTitle(pageTitle?: string | null): string {
  const t = pageTitle?.trim();
  if (!t || t === SITE.title) return SITE.title;
  return `${t} | ${SITE.title}`;
}

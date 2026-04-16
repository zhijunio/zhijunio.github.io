/**
 * Robots.txt 端点
 *
 * @fileoverview 生成爬虫规则文件，指导搜索引擎爬虫如何抓取网站
 *
 * 核心逻辑：
 * 1. 允许所有爬虫访问（User-agent: *）
 * 2. 允许抓取所有路径（Allow: /）
 * 3. 指定对搜索引擎更通用的 sitemap.xml 入口
 */

import type { APIRoute } from "astro";

export const GET: APIRoute = ({ site }) => {
  const base =
    typeof site === "string"
      ? site
      : site instanceof URL
        ? site.href
        : "https://blog.zhijun.io";
  const sitemapURL = new URL("/sitemap.xml", base);
  const body = `User-agent: *
Allow: /

Sitemap: ${sitemapURL.href}
`;
  return new Response(body, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};

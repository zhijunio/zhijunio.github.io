import type { APIRoute } from "astro";
import { SITE } from "@/config";
import { getPosts, getPostUrl, postModifiedIso, sortPosts } from "@/utils/postUtils";

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export const GET: APIRoute = async () => {
  const sortedPosts = sortPosts(await getPosts());
  const latest = sortedPosts[0]
    ? postModifiedIso(sortedPosts[0])
    : new Date().toISOString();

  const urls = [
    { path: "/", lastmod: latest, priority: "1.00" },
    { path: "/about", lastmod: latest, priority: "0.80" },
    ...sortedPosts.map(post => ({
      path: getPostUrl(post.data.slug),
      lastmod: postModifiedIso(post),
      priority: "0.64",
    })),
  ];

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map(
    entry => `  <url>
    <loc>${escapeXml(new URL(entry.path, SITE.website).toString())}</loc>
    <lastmod>${entry.lastmod.replace("Z", "+00:00")}</lastmod>
    <priority>${entry.priority}</priority>
  </url>`
  )
  .join("\n")}
</urlset>`;

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};

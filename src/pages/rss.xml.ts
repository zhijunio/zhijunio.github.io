import rss from "@astrojs/rss";
import {
  getAllBlogLike,
  getDescription,
  getPostUrl,
  sortPostsByDate,
} from "@/utils/postUtils";
import { SITE } from "@/config";

export async function GET() {
  const sortedPosts = sortPostsByDate(await getAllBlogLike()).slice(0, 10);

  const iconUrl = `${SITE.website.replace(/\/$/, "")}/favicon.ico`;
  const titleEscaped = SITE.title
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return rss({
    title: SITE.title,
    description: SITE.description,
    site: SITE.website,
    trailingSlash: false,
    customData: `<language>zh-CN</language><image><url>${iconUrl}</url><title>${titleEscaped}</title><link>${SITE.website}</link></image>`,
    items: sortedPosts.map(post => {
      const { data, body } = post;
      return {
        link: getPostUrl(data.slug, post.collection),
        title: data.title,
        description: getDescription(body ?? ""),
        ...(data.tags.length > 0 ? { categories: data.tags } : {}),
        pubDate: new Date(data.date),
      };
    }),
  });
}

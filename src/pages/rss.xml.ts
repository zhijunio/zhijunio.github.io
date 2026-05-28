import rss from "@astrojs/rss";
import {
  getPosts,
  getEntryDescription,
  getPostUrl,
  sortPosts,
} from "@/utils/postUtils";
import { SITE } from "@/config";

export async function GET() {
  const sortedPosts = sortPosts(await getPosts(), "date").slice(0, 10);

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
    items: sortedPosts.map(post => ({
      link: getPostUrl(post.data.slug),
      title: post.data.title,
      description: getEntryDescription(post),
      pubDate: new Date(post.data.date),
    })),
  });
}

/**
 * RSS 订阅端点
 *
 * @fileoverview 生成 RSS 2.0：条目按 frontmatter `date` 发布时间降序（非 `updated`）；最近 10 篇；摘要见 <!-- more --> / PostUtils.getDescription。
 */
import rss from "@astrojs/rss";
import { getAllBlogLike, PostUtils } from "@/utils/postUtils";
import { SITE } from "@/config";

export async function GET() {
  const sortedPosts = PostUtils.sortByPublishedDate(
    await getAllBlogLike()
  ).slice(0, 10);

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
      const { data, id, body, filePath } = post;
      const description = PostUtils.getDescription(body ?? "");
      return {
        link: PostUtils.getPath(
          id,
          filePath,
          true,
          data.date,
          data.timezone,
          data.slug,
          post.collection
        ),
        title: data.title,
        description,
        categories: data.tags,
        pubDate: new Date(data.date),
      };
    }),
  });
}

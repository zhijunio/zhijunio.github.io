import type { GetStaticPaths, APIRoute } from "astro";
import { SITE } from "@/config";
import {
  getAllBlogLike,
  PostUtils,
  type BlogLikeEntry,
} from "@/utils/postUtils";

interface Props {
  post: BlogLikeEntry;
}

function getCanonicalUrl(post: BlogLikeEntry): string {
  if (post.data.canonicalURL?.trim()) {
    return post.data.canonicalURL.trim();
  }

  return new URL(
    PostUtils.getPath(
      post.id,
      post.filePath,
      true,
      post.data.date,
      post.data.timezone,
      post.data.slug,
      post.collection
    ),
    SITE.website
  ).toString();
}

export const getStaticPaths: GetStaticPaths = async () => {
  const posts = PostUtils.getPublishedPosts(await getAllBlogLike());

  return posts.map(post => ({
    params: {
      section: post.collection,
      slug: PostUtils.getPath(
        post.id,
        post.filePath,
        false,
        post.data.date,
        post.data.timezone,
        post.data.slug,
        post.collection
      ),
    },
    props: { post },
  }));
};

export const GET: APIRoute<Props> = ({ props }) => {
  const { post } = props;
  const tags = post.data.tags.length > 0 ? post.data.tags.join(", ") : "None";
  const description =
    post.data.description?.trim() || PostUtils.getDescription(post.body ?? "");
  const body = (post.body ?? "").trim();
  const content = [
    `# ${post.data.title}`,
    "",
    `Canonical URL: ${getCanonicalUrl(post)}`,
    `Published At: ${new Date(post.data.date).toISOString()}`,
    `Tags: ${tags}`,
    `Description: ${description}`,
    "",
    body || "_No content_",
    "",
  ].join("\n");

  return new Response(content, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "X-Robots-Tag": "noindex, follow",
    },
  });
};

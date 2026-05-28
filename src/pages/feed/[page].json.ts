import type { APIRoute } from "astro";
import {
  getFeedPaginationStaticPaths,
  type HomeFeedItem,
} from "@/utils/postUtils";

export const getStaticPaths = getFeedPaginationStaticPaths;

type Props = {
  items: HomeFeedItem[];
  nextPage: number | null;
};

export const GET: APIRoute = ({ props }) => {
  const { items, nextPage } = props as Props;
  return new Response(JSON.stringify({ items, nextPage }), {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=3600",
    },
  });
};

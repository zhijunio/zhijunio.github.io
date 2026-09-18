import type { APIRoute } from "astro";
import {
  getActivityFeedStaticPaths,
  type ActivityFeedItem,
} from "@/utils/activity";

export const getStaticPaths = getActivityFeedStaticPaths;

type Props = {
  items: ActivityFeedItem[];
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

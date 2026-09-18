import type { APIRoute } from "astro";
import { loadPostRecords } from "@/utils/activity";

export const GET: APIRoute = async () => {
  const posts = await loadPostRecords();
  return new Response(JSON.stringify(posts, null, 2) + "\n", {
    headers: {
      "Content-Type": "application/json; charset=utf-8",
    },
  });
};

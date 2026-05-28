import type { HomeFeedItem } from "@/utils/postUtils";
import { appendHomeFeedItems } from "@/utils/feedDom";

type FeedPageJson = {
  items: HomeFeedItem[];
  nextPage: number | null;
};

export function initHomeFeedInfiniteScroll(): void {
  const list = document.getElementById("home-feed-list");
  const sentinel = document.getElementById("home-feed-sentinel");
  const status = document.getElementById("home-feed-status");

  if (!(list instanceof HTMLOListElement) || !sentinel) return;

  let nextPage = sentinel.dataset.nextPage?.trim() || "";
  let loading = false;

  const setStatus = (text: string, visible: boolean) => {
    if (!status) return;
    status.textContent = text;
    status.hidden = !visible;
  };

  const loadMore = async () => {
    if (!nextPage || loading) return;
    loading = true;
    setStatus("加载中…", true);

    try {
      const res = await fetch(`/feed/${nextPage}.json`);
      if (!res.ok) throw new Error(String(res.status));
      const data = (await res.json()) as FeedPageJson;
      appendHomeFeedItems(list, data.items);
      nextPage =
        data.nextPage != null && data.nextPage > 0
          ? String(data.nextPage)
          : "";
      sentinel.dataset.nextPage = nextPage;
      if (!nextPage) {
        observer.disconnect();
        sentinel.remove();
        setStatus("已加载全部", true);
        window.setTimeout(() => setStatus("", false), 1200);
      } else {
        setStatus("", false);
      }
    } catch {
      setStatus("加载失败，请向下滚动重试", true);
    } finally {
      loading = false;
    }
  };

  const observer = new IntersectionObserver(
    entries => {
      if (entries.some(e => e.isIntersecting)) void loadMore();
    },
    { rootMargin: "240px 0px" }
  );

  observer.observe(sentinel);
}

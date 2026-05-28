import type { HomeFeedItem } from "@/utils/postUtils";

type FeedPageJson = {
  items: HomeFeedItem[];
  nextPage: number | null;
};

function appendHomeFeedItems(
  list: HTMLOListElement,
  items: HomeFeedItem[]
): void {
  const frag = document.createDocumentFragment();
  for (const item of items) {
    const li = document.createElement("li");
    const article = document.createElement("article");

    const dateP = document.createElement("p");
    const time = document.createElement("time");
    time.dateTime = item.dateIso;
    time.textContent = item.dateDisplay;
    dateP.append(time);

    const titleP = document.createElement("p");
    titleP.className = "home-feed-title";
    const link = document.createElement("a");
    link.href = item.href;
    link.textContent = item.title;
    titleP.append(link);

    article.append(dateP, titleP);
    if (item.description) {
      const desc = document.createElement("p");
      desc.className = "home-feed-desc";
      desc.textContent = item.description;
      article.append(desc);
    }

    li.append(article);
    frag.append(li);
  }
  list.appendChild(frag);
}

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
      nextPage = data.nextPage ? String(data.nextPage) : "";
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

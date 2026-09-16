import type { HomeFeedItem } from "@/utils/homeFeed";
import { categoryLabel, categoryPath, tagPath } from "@/utils/taxonomy";

type FeedPageJson = {
  items: HomeFeedItem[];
  nextPage: number | null;
};

function appendHomeFeedItems(
  list: HTMLOListElement,
  items: HomeFeedItem[]
): void {
  const tpl = document.getElementById(
    "home-feed-item-template"
  ) as HTMLTemplateElement | null;
  if (!tpl) return;

  const frag = document.createDocumentFragment();
  for (const item of items) {
    const node = tpl.content.cloneNode(true) as DocumentFragment;
    const time = node.querySelector("time");
    const link = node.querySelector<HTMLAnchorElement>(".home-feed-title a");
    const desc = node.querySelector<HTMLParagraphElement>(".home-feed-desc");
    const tags = node.querySelector<HTMLElement>(".home-feed-tags");
    const category = node.querySelector<HTMLAnchorElement>(
      ".home-feed-category"
    );
    if (!time || !link) continue;

    time.dateTime = item.dateIso;
    time.textContent = item.dateDisplay;
    link.href = item.href;
    link.textContent = item.title;
    if (desc) {
      if (item.description) {
        desc.textContent = item.description;
        desc.hidden = false;
      } else {
        desc.hidden = true;
      }
    }
    if (category) {
      if (item.category) {
        category.href = categoryPath(item.category);
        category.textContent = categoryLabel(item.category);
        category.hidden = false;
      } else {
        category.removeAttribute("href");
        category.textContent = "";
        category.hidden = true;
      }
    }
    if (tags) {
      tags.replaceChildren();
      if (item.tags.length) {
        for (const tag of item.tags) {
          const chip = document.createElement("a");
          chip.className = "home-feed-tag";
          chip.href = tagPath(tag);
          chip.textContent = `#${tag}`;
          tags.append(chip);
        }
        tags.hidden = false;
      } else {
        tags.hidden = true;
      }
    }
    frag.append(node);
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

import type { HomeFeedItem } from "@/utils/postUtils";

export function appendHomeFeedItems(
  list: HTMLOListElement,
  items: HomeFeedItem[]
): void {
  const frag = document.createDocumentFragment();
  for (const item of items) {
    frag.appendChild(createFeedListItem(item));
  }
  list.appendChild(frag);
}

function createFeedListItem(item: HomeFeedItem): HTMLLIElement {
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
  return li;
}

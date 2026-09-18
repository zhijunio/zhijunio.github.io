import type { ActivityFeedItem } from "@/utils/activity";

type FeedPageJson = {
  items: ActivityFeedItem[];
  nextPage: number | null;
};

function titleNode(title: string, url: string | undefined, quoted: boolean) {
  const text = quoted ? `《${title}》` : title;
  if (!url) {
    const span = document.createElement("span");
    span.textContent = text;
    return span;
  }
  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = text;
  return link;
}

function starsNode(row: ActivityFeedItem) {
  if (!row.stars) return null;
  const span = document.createElement("span");
  span.className = "activity-stars";
  if (row.star != null) span.setAttribute("aria-label", `${row.star} 星`);
  span.textContent = row.stars;
  return span;
}

function fillLine(line: HTMLParagraphElement, row: ActivityFeedItem) {
  if (row.type === "run") {
    const name = document.createElement("span");
    name.className = "activity-run-name";
    name.textContent = row.title;
    line.append(name);
    if (row.km == null && row.minutes == null && row.hr == null && !row.place) {
      return;
    }
    const meta = document.createElement("span");
    meta.className = "activity-run-meta";
    let started = false;
    const sep = () => {
      if (started) meta.append(" · ");
      started = true;
    };
    if (row.km != null) {
      sep();
      const km = document.createElement("b");
      km.textContent = String(row.km);
      meta.append(km, " 公里");
    }
    if (row.minutes != null) {
      sep();
      const minutes = document.createElement("b");
      minutes.textContent = String(row.minutes);
      meta.append(minutes, " 分钟");
    }
    if (row.hr != null) {
      sep();
      const hr = document.createElement("b");
      hr.textContent = String(row.hr);
      meta.append("心率 ", hr);
    }
    if (row.place) {
      sep();
      const place = document.createElement("span");
      place.className = "activity-run-place";
      place.textContent = row.place;
      meta.append(place);
    }
    line.append(meta);
    return;
  }

  if (row.type === "memo") {
    line.append("发布了", " ");
    line.append(titleNode("说说", row.url, false));
    if (row.tags?.length) {
      const tags = document.createElement("span");
      tags.className = "activity-tags";
      for (const tag of row.tags) {
        const chip = document.createElement("span");
        chip.className = "activity-tag";
        chip.textContent = `#${tag}`;
        tags.append(chip);
      }
      line.append(tags);
    }
    return;
  }

  line.append(row.lead, " ");
  line.append(titleNode(row.title, row.url, row.type !== "food"));
  if (row.tags?.length) {
    const tags = document.createElement("span");
    tags.className = "activity-tags";
    for (const tag of row.tags) {
      const chip = document.createElement("span");
      chip.className = "activity-tag";
      chip.textContent = `#${tag}`;
      tags.append(chip);
    }
    line.append(tags);
  }
  const stars = starsNode(row);
  if (stars) line.append(stars);
  if (row.type === "food" && row.place) {
    const place = document.createElement("span");
    place.className = "activity-place";
    place.textContent = row.place;
    line.append(place);
  }
}

function appendRows(timeline: HTMLElement, rows: ActivityFeedItem[]) {
  const frag = document.createDocumentFragment();
  for (const row of rows) {
    if (row.showYear) {
      const year = document.createElement("div");
      year.className = "activity-year";
      const label = document.createElement("span");
      label.textContent = row.year;
      year.append(label);
      frag.append(year);
    }
    const article = document.createElement("article");
    article.className = `activity-item activity-type-${row.type}${row.hideTime ? " is-follow" : ""}`;
    article.dataset.type = row.type;

    const time = document.createElement("time");
    time.className = `activity-time${row.hideTime ? " is-hidden" : ""}`;
    time.dateTime = row.time;
    time.textContent = row.label;

    const node = document.createElement("span");
    node.className = "activity-node";
    node.setAttribute("aria-hidden", "true");
    const icon = document.getElementById(`activity-icon-${row.type}`);
    if (icon instanceof HTMLTemplateElement) {
      node.append(icon.content.cloneNode(true));
    }

    const content = document.createElement("div");
    content.className = "activity-content";
    const line = document.createElement("p");
    line.className = "activity-line";
    fillLine(line, row);
    content.append(line);
    if (row.type === "memo" && (row.title || row.html || row.images?.length)) {
      const card = document.createElement("details");
      card.className = "activity-memo-card";
      const summary = document.createElement("summary");
      summary.textContent = row.title;
      card.append(summary);
      const body = document.createElement("div");
      body.className = "activity-memo-content";
      if (row.html) {
        const text = document.createElement("div");
        text.className = "activity-memo-text";
        text.innerHTML = row.html;
        body.append(text);
      }
      if (row.images?.length) {
        const images = document.createElement("div");
        images.className = "activity-images";
        for (const src of row.images) {
          const link = document.createElement("a");
          link.className = "activity-image";
          link.href = src;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          const img = document.createElement("img");
          img.src = src;
          img.alt = "";
          img.loading = "lazy";
          img.decoding = "async";
          link.append(img);
          images.append(link);
        }
        body.append(images);
      }
      card.append(body);
      content.append(card);
    }
    if (row.text) {
      const comment = document.createElement("p");
      comment.className = "activity-comment";
      comment.textContent = row.text;
      content.append(comment);
    }
    article.append(time, node, content);
    frag.append(article);
  }
  timeline.append(frag);
}

export function initActivityScroll(): void {
  const timeline = document.getElementById("activity-timeline");
  const sentinel = document.getElementById("activity-sentinel");
  const status = document.getElementById("activity-status");
  const page = document.querySelector(".activity-page");
  if (!timeline || !sentinel || !page) return;

  let type = sentinel.dataset.type || "all";
  let nextPage = sentinel.dataset.nextPage?.trim() || "";
  let loading = false;
  let request = 0;

  const setStatus = (text: string, visible: boolean) => {
    if (!status) return;
    status.textContent = text;
    status.hidden = !visible;
  };

  const watch = () => {
    observer.disconnect();
    if (nextPage) observer.observe(sentinel);
  };

  const loadPage = async (filter: string, pageNo: number, replace: boolean) => {
    if (!replace && (loading || !nextPage)) return;
    const token = ++request;
    loading = true;
    if (replace) {
      timeline.replaceChildren();
      type = filter;
      nextPage = "";
      sentinel.dataset.type = filter;
      sentinel.dataset.nextPage = "";
      watch();
      const top = timeline.getBoundingClientRect().top;
      if (top < 0) timeline.scrollIntoView({ block: "start" });
    }
    setStatus("加载中…", true);

    try {
      const res = await fetch(`/activity/feed/${filter}/${pageNo}.json`);
      if (!res.ok) throw new Error(String(res.status));
      const data = (await res.json()) as FeedPageJson;
      if (token !== request) return;
      appendRows(timeline, data.items);
      nextPage = data.nextPage ? String(data.nextPage) : "";
      sentinel.dataset.nextPage = nextPage;
      sentinel.dataset.type = filter;
      type = filter;
      watch();
      if (!nextPage) {
        setStatus("已加载全部", true);
        window.setTimeout(() => {
          if (token === request) setStatus("", false);
        }, 1200);
      } else {
        setStatus("", false);
      }
    } catch {
      if (token !== request) return;
      setStatus(replace ? "加载失败" : "加载失败，请向下滚动重试", true);
      if (!replace) watch();
    } finally {
      if (token === request) loading = false;
    }
  };

  const observer = new IntersectionObserver(
    entries => {
      if (!entries.some(entry => entry.isIntersecting)) return;
      const pageNo = Number(nextPage);
      if (!pageNo) return;
      void loadPage(type, pageNo, false);
    },
    { rootMargin: "240px 0px" }
  );

  page
    .querySelectorAll<HTMLInputElement>('input[name="activity-filter"]')
    .forEach(input => {
      input.addEventListener("change", () => {
        if (!input.checked) return;
        const filter = input.id.slice("activity-".length);
        if (filter === type && timeline.childElementCount > 0) return;
        void loadPage(filter, 1, true);
      });
    });

  watch();
}

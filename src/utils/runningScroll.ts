import type { RunFeedItem } from "@/utils/running";

type FeedPageJson = {
  items: RunFeedItem[];
  nextPage: number | null;
};

function stat(value: string, label: string) {
  const wrap = document.createElement("div");
  wrap.className = "run-stat";
  const strong = document.createElement("span");
  strong.className = "run-stat-value";
  strong.textContent = value;
  const caption = document.createElement("span");
  caption.className = "run-stat-label";
  caption.textContent = label;
  wrap.append(strong, caption);
  return wrap;
}

const PIN_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false"><path d="M12 2.4c3.7 0 6.6 2.9 6.6 6.5 0 4.6-5.4 10.7-6.2 11.6-.2.2-.6.2-.8 0-.8-.9-6.2-7-6.2-11.6 0-3.6 2.9-6.5 6.6-6.5Zm0 4.2a2.4 2.4 0 1 0 0 4.8 2.4 2.4 0 0 0 0-4.8Z"/></svg>';

function appendCard(list: HTMLElement, run: RunFeedItem) {
  const card = document.createElement("article");
  card.className = "run-card";

  const main = document.createElement("div");
  main.className = "run-main";
  const head = document.createElement("div");
  head.className = "run-head";
  const time = document.createElement("time");
  time.dateTime = run.time;
  time.textContent = run.date;
  head.append(time);
  if (run.zoneLabel) {
    const badge = document.createElement("span");
    badge.className = "run-zone";
    badge.dataset.zone = String(run.zone);
    badge.textContent = run.zoneLabel;
    head.append(badge);
  }
  const kind = document.createElement("p");
  kind.className = "run-kind";
  const title = document.createElement("span");
  title.textContent = run.title;
  kind.append(title);
  if (run.place) {
    const place = document.createElement("span");
    place.className = "run-place";
    place.textContent = run.place;
    kind.append(place);
  }
  main.append(head, kind);

  const stats = document.createElement("div");
  stats.className = "run-stats";
  stats.append(
    stat(run.km != null ? run.km.toFixed(1) : "--", "km"),
    stat(run.minutes != null ? String(run.minutes) : "--", "分钟"),
    stat(run.pace ?? "--", "配速"),
    stat(run.hr != null ? String(run.hr) : "--", "心率"),
    stat(run.vdot != null ? String(run.vdot) : "--", "跑力"),
    stat(run.load != null ? String(run.load) : "--", "负荷")
  );
  card.append(main, stats);
  list.append(card);
}

export function initRunningScroll() {
  const list = document.getElementById("run-list");
  const sentinel = document.getElementById("run-sentinel");
  const status = document.getElementById("run-status");
  if (!list || !sentinel) return;

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
      const res = await fetch(`/running/feed/${nextPage}.json`);
      if (!res.ok) throw new Error(String(res.status));
      const data = (await res.json()) as FeedPageJson;
      for (const item of data.items) appendCard(list, item);
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
      if (nextPage) watch();
    }
  };

  const observer = new IntersectionObserver(
    entries => {
      if (entries.some(entry => entry.isIntersecting)) void loadMore();
    },
    { rootMargin: "240px 0px" }
  );

  const watch = () => {
    observer.disconnect();
    if (nextPage && sentinel.isConnected) observer.observe(sentinel);
  };

  watch();
}

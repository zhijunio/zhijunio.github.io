/** Giscus 明暗主题切换（由 PostDetails 通过 meta 注入 URL） */
function getGiscusThemeUrl() {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  const meta = document.querySelector(
    isDark
      ? 'meta[name="giscus-theme-dark"]'
      : 'meta[name="giscus-theme-light"]'
  );
  return meta?.getAttribute("content") ?? "";
}

function updateGiscusTheme() {
  const iframe = document.querySelector("iframe.giscus-frame");
  if (!iframe?.contentWindow) return;
  iframe.contentWindow.postMessage(
    { giscus: { setConfig: { theme: getGiscusThemeUrl() } } },
    "https://giscus.app"
  );
}

window.addEventListener("load", updateGiscusTheme);
document.addEventListener("themechange", updateGiscusTheme);
document.addEventListener("astro:page-load", updateGiscusTheme);

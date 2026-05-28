/**
 * 生产图片走 CDN 时，构建产物无需再包含 public/images 副本以减小部署体积。
 * 设置 PRUNE_DIST_IMAGES=false 可跳过。
 */
import { existsSync } from "node:fs";
import { rm } from "node:fs/promises";

if (process.env.PRUNE_DIST_IMAGES === "false") {
  process.exit(0);
}

const target = "dist/images";
if (!existsSync(target)) {
  process.exit(0);
}

await rm(target, { recursive: true, force: true });
console.log(`[prune-dist-images] removed ${target}`);

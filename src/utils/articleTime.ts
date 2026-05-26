import dayjs from "dayjs";
import type { Dayjs } from "dayjs";
import utc from "dayjs/plugin/utc";
import timezonePlugin from "dayjs/plugin/timezone";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/zh-cn";
import { SITE } from "@/config";

dayjs.extend(utc);
dayjs.extend(timezonePlugin);
dayjs.extend(relativeTime);
dayjs.locale("zh-cn");

const SITE_TZ = SITE.timezone || "Asia/Shanghai";

/** 列表 `<time>`：展示文案、机器可读 ISO、悬浮提示（发布时刻） */
export interface ArticleTimeFields {
  display: string;
  iso: string;
  titleAttr: string;
}

function latestOf(pub: Dayjs, mod: Dayjs | null): Dayjs {
  return mod && mod.isAfter(pub) ? mod : pub;
}

function effectiveTimezone(timezoneProp: string | undefined): string {
  return timezoneProp || SITE_TZ;
}

/**
 * 文章发布/更新时间在列表卡片中的展示（最新时间 + 时区；`titleAttr` 为发布时间）。
 */
export class ArticleTime {
  static getDisplay(
    pubDatetime: Date | string,
    modDatetime: Date | string | null | undefined,
    timezoneProp: string | undefined,
    format: "relative" | "absolute"
  ): ArticleTimeFields {
    const pub = dayjs(pubDatetime);
    const mod = modDatetime ? dayjs(modDatetime) : null;
    const latest = latestOf(pub, mod);
    const iso = latest.toISOString();
    const tz = effectiveTimezone(timezoneProp);
    const latestInTz = dayjs.utc(latest.toDate()).tz(tz);
    const pubInTz = dayjs.utc(pub.toDate()).tz(tz);
    const titleAttr = pubInTz.format("YYYY-MM-DD HH:mm:ss");
    const display =
      format === "absolute"
        ? latestInTz.format("YYYY-MM-DD")
        : latest.fromNow();
    return { display, iso, titleAttr };
  }
}

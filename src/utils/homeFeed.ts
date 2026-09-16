/** 首页 / 分类列表共用的 feed 条目（可进客户端） */

export type HomeFeedItem = {
  title: string;
  href: string;
  dateDisplay: string;
  dateIso: string;
  description: string;
  tags: string[];
  category: string;
};

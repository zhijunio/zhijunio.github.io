---
title: "2026-03-08｜合并 linkding-cn、新的知识管理工具"
date: 2026-03-09 19:30:00+08:00
slug: "20260308-week-review"
tags: [ "vps" ]
draft: false
categories: [ "weekly" ]
description: 这周一边用 AI Agent 合并 linkding-cn 代码、整理 Spring Boot 2 升 3 的方案，一边也在琢磨一款面向输入驱动用户的极简知识管理工具。
favicon: "linkding.svg"

---

本篇博客介绍最近一周（2026-03-02 ～ 2026-03-08）的记录与思考。

## 健康

这周一共跑了 27.42 公里，比计划的 23.1（3.3 * 7 =23.1） 公里多跑了 4 公里，超出了预期，下周还要继续保持和努力。数据来自本站的 `running.json`。

## 技术

1、花了一天的时间，使用 Cursor 将 [ linkding-cn 代码合并到 linkding](/posts/2026/03/06/merge-linkding-cn-to-linkding)。不得不说，使用 AI Agent 做这种工作比人操作真的是容易很多。

2、参考 [Spring Boot 2 升 3：两条命令搞定 95%，AI 收尾](https://atbug.com/openrewrite-recipe-first-spring-boot-2-to-3-migration/) 将 [Spring Boot 2 升级到 Spring Boot 3 ](/posts/2026/03/06/spring-boot-2-to-3-upgrade-guide)，其中一种方式也是使用 AI，具体是AI Skill 来实现。

3、将 VPS 服务器上的 memos 版本 从 v0.18.2 升级到了最新版本 v0.26.2，并简单统计了一下 memos **版本功能**，可以发现从 0.22.0 版本开始去掉了我在意的分享功能；从 v0.24.1 版本开始改成了我不喜欢的布局和背景色。

- **v0.21.0 版本**：支持 Mermaid、分享功能
- **v0.22.0 版本**：去掉了分享功能
- **v0.24.0 版本**：支持 **Shortcuts**
- **v0.24.1 版本**：改变了布局

4、本来想基于现在的 [usememos/memos](https://github.com/usememos/memos) 源代码添加一些新的功能，比如：每日回顾、分享。搞了一上午之后，突然有一个想法，想做一款面向「输入驱动型」用户的极简知识管理工具，集成订阅、书签、闪念三个功能，通过流式展示及标签解决「存而不看」痛点。这款产品相当于是我现在在用的 Folo + Linkding + Memos 的联合体应用。

我编写了一个提示词：

```markdown
请根据以下需求，从零创建一个名为 **Flux（流存）** 的极简知识管理应用。

## 一、产品定位

面向「输入驱动型」用户的极简知识管理工具，通过流式展示及标签解决「存而不看」痛点。

**概念**：Feed（订阅源）存 RSS/Atom 链接；Flux 存三种类型——feed_item（定时抓取）、bookmark（手动/从订阅文章保存）、thought（手动/从书签、订阅文章划线生成）。流存页展示所有类型；订阅管理页管理订阅源，可展示订阅文章（从 flux 表读取）。

## 二、技术栈

Next.js (App Router) + TypeScript + Tailwind CSS；Zustand + React Query；Supabase；rss-parser / metascraper；Vercel。

## 三、核心功能

**订阅源**：订阅管理页管理订阅源列表（增删改 RSS URL），可展示选中源的订阅文章（flux 表 type=feed_item，按 feed_id 筛选）。定时抓取写入 flux，按 URL/guid 去重。

**流存**：流存页展示所有（feed_item、bookmark、thought）。过滤区（搜索、标签、类型）+ 内容区（添加书签/闪念、列表）。书签：URL 解析 OG；闪念：Markdown 输入；标签：有长度与数量限制。重复 URL 提示覆盖或取消。订阅文章可「保存为书签」→ 新建 bookmark，parent_id 指向订阅文章的 id。列表按时间倒序、分页。操作：编辑、复制、归档、删除（物理删除）。
```

并且，还让 AI 做了一下竞品分析，AI 的回答如下。

> # 一、产品定位回顾
>
> - **目标用户**：输入驱动型（习惯先存后看）
> - **核心价值**：流式展示 + 标签，缓解「存而不看」
> - **功能组合**：RSS 订阅 + 书签 + 闪念，支持「保存为书签」「划线生成闪念」
>
> # 二、竞品概览
>
> | 品类        | 代表产品                        | 特点                    |
> | ----------- | ------------------------------- | ----------------------- |
> | 稍后读/书签 | Pocket, Raindrop.io, Instapaper | 书签强，RSS 弱或没有    |
> | RSS 阅读    | Feedly, Inoreader               | RSS 强，书签/笔记弱     |
> | 知识管理    | Notion, Obsidian, Logseq        | 功能多，上手重          |
> | 闪念/灵感   | Drafts, Apple Notes             | 轻量，但和 RSS/书签割裂 |
>
>
> # 三、Flux 的优劣势
>
> **优势**
>
> | 点           | 说明                                      |
> | ------------ | ----------------------------------------- |
> | **一体化**   | RSS + 书签 + 闪念在同一产品，减少工具切换 |
> | **轻量**     | 比 Notion 简单，比单一工具功能更全        |
> | **输入优先** | 围绕「先存」设计，符合目标用户习惯        |
> | **内容关联** | 订阅文章 → 书签 → 闪念，形成内容链路      |
>
> **劣势 / 风险**
>
> | 点             | 说明                                    |
> | -------------- | --------------------------------------- |
> | **差异化不足** | 单看功能，和 Raindrop + Feedly 组合类似 |
> | **品牌与生态** | Pocket、Notion 等已有用户基础和生态     |
> | **护城河弱**   | 技术门槛不高，容易被模仿或整合进大产品  |
>
>
> # 四、提升竞争力的方向
>
> 1. **聚焦细分人群** 
>
>    例如：中文创作者、研究者、产品经理等，做深场景和体验。
>
> 2. **强化独特能力**  
> 
>    - 划线 → 闪念的体验是否明显优于竞品  
>   - 标签 + 流式展示是否带来更好的「回顾」和「发现」
> 
>3. **本地优先 / 隐私** 
> 
>   若支持自托管或本地优先，可吸引注重隐私和数据的用户。
> 
>4. **AI 增强**
> 
>   自动打标、摘要、关联推荐，能形成差异化。
> 
>5. **中文市场** 
> 
>   针对中文内容、工作流做优化，避开与 Pocket、Feedly 的正面竞争。
>
> 
># 五、简要结论
> 
> - **当前**：作为 MVP，功能组合有吸引力，但差异化还不够强，直接和 Pocket、Feedly 等正面竞争难度较大。  
> - **有机会**：若能在细分人群、中文市场、AI 能力或隐私/本地化上做出清晰优势，有机会找到自己的市场空间。  
>- **建议**：先验证「输入驱动 + 流式 + 标签」是否真的解决目标用户的「存而不看」问题，再围绕验证结果强化 1–2 个核心卖点。

## 本周分享

我使用 [Linkding](https://linkding.zhijun.io/) 书签来保存我认为不错的资源，包括文章、视频等等。虽然大部分有意思的输入都会自动同步到「[ChenSoul Share](https://t.me/s/zhijun_share)」Telegram 频道，但我还是想在这里额外挑一部分出来。单独列出来之后，这篇周报就更像一份 newsletter 了。

### 文章

- [用 Docker 私有化部署 GitHub Actions Runner（Runner Fleet）](https://soulteary.com/2026/02/18/use-docker-to-natively-deploy-github-actions-runner-by-fleet.html)

- [字节全家桶 Seed 2.0 + TRAE 玩转 Skill](http://www.ruanyifeng.com/blog/2026/02/seed-2.0.html)
- [Create Apps with Claude Code on Ollama](https://piotrminkowski.com/2026/02/17/create-apps-with-claude-code-on-ollama/)
- [How I Use Claude Code | Boris Tane](https://boristane.com/blog/how-i-use-claude-code/)
- [Spring AI Prompt Caching: Stop Wasting Money on Repeated Tokens](https://www.danvega.dev/blog/2026/02/08/spring-ai-prompt-caching)
- [OpenClaw Architecture, Explained: How It Works](https://ppaolo.substack.com/p/openclaw-system-architecture-overview)


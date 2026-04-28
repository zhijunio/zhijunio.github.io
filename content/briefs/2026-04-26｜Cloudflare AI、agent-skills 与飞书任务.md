---
title: "2026-04-26｜Cloudflare AI、agent-skills 与飞书任务"
date: 2026-04-27 10:00:00+08:00
slug: "20260426-week-review"
tags: [ "ai", "claude-code", "skills" ]
categories: [ "weekly" ]
description: "Cloudflare Worker AI 接入尝试、addyosmani agent-skills、Claude/Cursor 系统提示词、飞书多维表「任务中心」搭建提示词、bookmark 本地书签技能与公众号 Markdown 排版器更新；户外跑 3 次约 15 km；附录含每日工作规划助手提示词与精选开发工具链接。"
favicon: "cloudflare.svg"
---

本篇记录最近一周（2026-04-19 ～ 2026-04-26）的**输入、输出与思考。

## 本周摘要

- 在 Codex / Claude / IDEA 里折腾 **Cloudflare Worker AI**，体感响应优于部分国内 Coding Plan。
- 为 **Claude Code / Codex / Cursor** 接入 [superpowers](https://github.com/obra/superpowers) 与 [karpathy-guidelines](https://github.com/forrestchang/andrej-karpathy-skills) 系系统提示词；收集「寓言学概念」类学习提示词样例。
- **ChatGPT 智能体**：每日工作规划助手思路，完整提示词见附录。
- **飞书任务中心**：跟 X 上教程用 `lark-cli` + 一段提示词即可搭多维表与自动化。
- 关注 **learning-skill**（技术学习路线生成）、**Claw 邮箱**（给 Agent 收订阅信）等周边工具。
- **项目**：`bookmark` 技能（本地 Markdown 书签）、[文章工具箱](https://github.com/zhijunio/article-tools) 公众号排版器一轮迭代。
- **健康**：户外跑 **3 次、约 15.06 km**（数据来自本站 `running.json`）。

## 输出

## 博客

本周博客发布两篇文章：

- [技术文章怎么读，才不会读完就忘？](/posts/tech-article-reading-framework)
- [Docker Buildx 实战指南](/posts/docker-buildx-guide)

博客运营数据：

![博客运营数据](01.webp)

访问页面和来源：

![访问页面和来源](02.webp)

从数据来看，访问量最高的还是和 AI 相关；搜索来源最多的是 bing，来自 google 和 baidu 的很少，原因是没有收录。

### 微信公众号

本周主要迭代 [文章工具箱](https://github.com/zhijunio/article-tools) 内的 **Markdown 排版器**（默认字色、粘贴逻辑、顶栏工具栏、全键盘快捷键等），细节见下节「项目与开发」。若需展示传播数据，可在此补充：发文篇数、总阅读、分享与新增关注等。

本周公众号运营数据如下：

![公众号运营数据](03.webp)

从数据上来看，公众号的流量少的可怜，原因是粉丝少、内容没有吸引力。

### 小红书

本周小红书运营数据如下：

![小红书运营数据](04.webp)

| 笔记基础信息                             | 曝光 | 光看 | 封面点击率 | 点赞 | 收藏 |
| ---------------------------------------- | ---- | ---- | ---------- | ---- | ---- |
| 你好，认识一下 🙋‍♀️                        | 74   | 5    | 6.80%      | 1    | 0    |
| 🥳在小红书赞和收藏破50啦！️️                | 64   | 3    | 6.30%      | 0    | 0    |
| 无标题笔记                               | 837  | 59   | 7.80%      | 2    | 6    |
| 最近一周 AI学习笔记                      | 3    | 2    | 66.70%     | 1    | 0    |
| GPT 5.5 可以使用了🥰                      | 378  | 35   | 10.30%     | 2    | 1    |
| 会说书的少年与RAG                        | 198  | 19   | 11.80%     | 1    | 0    |
| 通过漫画故事告诉你什么是 Agent Harness？ | 167  | 10   | 6.10%      | 0    | 0    |
| 大厂这波 AI，已经不是试试工具这么简单了  | 1321 | 190  | 14.20%     | 1    | 1    |
| 技术文章怎么读？我的 6 步解读法10:03     | 371  | 15   | 4.00%      | 1    | 3    |
| 高效｜健身达人解锁计划💪                  | 293  | 17   | 5.80%      | 0    | 1    |

从数据上来看，小红书的流量比公众号的流量多。

### X（Twitter）

暂无。

## 输入

1. 尝试在 Codex 和 Claude 中使用 Cloudflare Worker AI，但是没有配置成功。在 IDEA 中配置 AI Git Commit 使用 Cloudflare Worker AI，发现响应速度还是蛮快的，至少比使用阿里的 Coding Plan 要快不少。REST 形态可参考 Cloudflare 控制台账户下的 **AI `v1/chat/completions`** 端点；API Key 在 [API Tokens](https://dash.cloudflare.com/profile/api-tokens) 新建或查看。

2. 发现一个好用的 skill [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)。该技能包括高级工程师在构建软件时使用的工作流程、质量控制点和最佳实践。相比较其他 SDD 工具，比如 [GSD](https://github.com/gsd-build/get-shit-done)、spec-ki、openspec 等等，该技能非常适合小项目。我在我的一些项目中使用它来审核、优化项目。

3. 通过寓言故事学习概念的提示词：

```bash
我在学习：【Agent Harness】 这个概念。

我希望你通过写一个寓言的方式，间接地把这个概念完整讲出来。最好一直到快结尾时，人才会慢慢意识到这个概念究竟是什么。然后在故事之后，再补一段解释，把你刚才真正要讲的概念说清楚。

帮我把上面的故事画成 【4】 页【中式现代漫画】风格的漫画故事。注意：是生成 4 张比例为 9:16的图片。
```

4. 给 Claude Code、Codex 和 Cursor 配置了系统提示词。该提示词用到了 [superpowers](https://github.com/obra/superpowers) 和 [karpathy-guidelines](https://github.com/forrestchang/andrej-karpathy-skills) 这两个技能。

```bash
中文回复，言简意赅，巧用Emoji。
减少Build，节省时间。
按需使用Plan Mode或Subagent。
若提交Git，要写中文Log包括：问题或需求描述 或 修复或实现思路 或 复现路径(可选)。
若编码Coding，按需使用skill：superpower和karpathy-guidelines。
```

5. ChatGPT 可以创建智能体，例如每日工作规划助手：可连接 Google Calendar、Gmail、GitHub、Slack、Teams、Notion 等，整理当日重点并输出可执行计划。可参考附录中的完整提示词，在小龙虾或 Hermes Agent 里做成技能。

6. X 上有人分享了[如何用 Claude Code 在飞书搭任务系统](https://x.com/alin_zone/status/2046916887913591154)。需要先安装 lark-cli 和技能：

```bash
npm install -g @larksuite/cli

npx skills add larksuite/cli -y -g
```

然后，把下面的提示词丢给 Claude Code 或者其他你正在使用的 AI Agent：

```bash
帮我在飞书创建一个多维表格叫"任务中心"，建一张"任务"表。字段：标题（文本）、类型（单选：任务/收件箱）、分类（单选：工作/生活/自媒体）、状态（单选：待办/进行中/已完成/已归档）、优先级（单选：P0/P1/P2/P3）、开始时间、截止时间、完成时间（日期）、备注（多行文本）、链接（URL）、附件。加两个公式字段：逾期时长和是否逾期。建三个自动化：完成自动填时间、开始前一天提醒、截止前一天提醒。建三个视图：看板、收件箱、本周任务。再建个仪表盘叫任务总览。
```

最近也想用 AI Agent 基于 GitHub 做任务系统，与上述思路接近；不必先做完整技能，**一段提示词** 往往就够落地。

7. @Siva 开源了「技术学习路线生成」Agent Skill：[learning-skill](https://github.com/sivaprasadreddy/learning-skill)。当你问类似 *teach me Rust*、*roadmap for Kubernetes* 等，会生成结构化学习指南（周计划、环境、练习档、资源等）。

8. 给 **AI Agent** 注册一个 Claw 邮箱：可选 [ClawEmail（163）](https://claw.163.com/)、[ClawPost](https://clawpost.net/)，或境外 [ClawEmail](https://clawemail.com/)。用于收订阅邮件，再由 AI 每日摘要推送到常用聊天工具。

## 项目与开发

1. 使用 Claude Code 开发了一个保存书签到本地 Markdown 文件的技能 [bookmark](https://github.com/zhijunio/zhijunio-skills/tree/main/bookmark)，可替代自建 Linkding，少占一台 VPS。

2. [文章工具箱](https://github.com/zhijunio/article-tools) 目前有 3 个 fork 和 6 个 star；本周重点改 **微信公众号排版器**：

- 所有主题的段落默认使用黑色字色。
- 编辑区粘贴 Markdown 时，不再强制走一遍「转 Markdown」的中间步骤。
- 新增 **顶栏工具栏**：加粗/斜体/删除线/行内代码/链接、代码块与引用、**水平分割线**、**GFM 三列表格**、标题（H1～H4/正文）、缩进等；与下方 **全键盘快捷键** 共用同一套插入与切换逻辑。

## 健康

最近一周（04-19～04-26）共 **3 次** 户外跑，合计约 **15.06 公里**。数据来自本站的 `running.json`。

![跑步数据](05.webp)

**小结：** 本周跑量与频次均高于前一周（04-13～04-19 的 2 次、**12.04 km**）：总距离约 **+3 km**、多跑 1
次。单次距离从 **7 km 节奏跑** 到 **3 km 轻量**、再到 **5 km 收尾**，04-24 与 04-25
配速在 6 分台且心率 125～133，偏有氧与节奏；04-26
配速 **7′18″** 相对更保守，但当日平均心率为 0（设备未记录或未佩戴），不宜与前几日直接对比。整体相较再前一周大跑量周（04-06～04-12
约 **34.82 km**）仍属**中等偏低负荷**，以维持活动为主。

## 分享

我使用 [Linkding](https://linkding.zhijun.io/)
书签来保存我认为不错的资源，包括文章、视频等等。大部分有意思的输入都会自动同步到「[ZhiJun Share](https://t.me/s/zhijun_share)
」Telegram 频道，但我还是想在这里额外挑一部分出来。单独列出来之后，这篇周报就更像一份 newsletter 了；其中部分条目也可拆成 **X 图文** 或 **小红书单条** 素材。

![本周书签](06.webp)

- [Pica, a MacOS font management app](https://pica.joshpuckett.me/)
  > Pica 是一个 macOS 字体管理应用，主打更好的字体整理与启用体验。页面重点展示了字体预览、颜色主题、完整 OpenType 支持、自定义集合、一键激活和监听文件夹等功能。官网强调它是原生应用且可免费使用，并提供桌面版下载入口。

- [Yaak](https://yaak.app/)
  > Yaak is a fast, secure, and offline API client with an agent-friendly CLI

- [Tolaria — A second brain for the AI era](https://tolaria.md/)
  > Organize your notes as Markdown files. With native relationships, Git, and Claude Code integration. Free forever.

- [agent-skills - Production-Grade AI Agent Engineering Skills](https://github.com/addyosmani/agent-skills)
  > Addy Osmani 的项目，为 AI 编码代理提供生产级工程技能指南

- [OpenDataLoader-PDF - AI-Ready PDF Parser](https://github.com/opendataloader-project/opendataloader-pdf)
  > 开源 PDF 解析器，将 PDF 转换为 AI 可用的结构化数据，自动化 PDF 内容提取

- [MDV - Markdown Superset for Documents & Slides](https://github.com/drasimwagan/mdv)
  > Markdown 超集工具，支持嵌入数据和可视化，可导出 HTML/PDF，带实时预览和 VS Code 扩展

- [Defuddle - Page to Markdown](https://defuddle.md/)
  > Get the main content of any page as clean, readable Markdown

- [TablePro - Native macOS Database Client](https://github.com/TableProApp/TablePro)
  > Free open-source database client for MySQL, PostgreSQL, SQLite, MongoDB, Redis + 15 more databases

- [maillab/cloud-mail](https://github.com/maillab/cloud-mail)
  > A Cloudflare-based email service | 基于 Cloudflare 的邮箱服务

- [D2 Documentation - Declarative Diagramming](https://d2lang.com/)
  > D2 是现代化的文本转图表 DSL 语言，可快速绘制声明式图表，支持多种布局引擎、自定义样式、导入模块、变量、自动格式化等功能

- [AgentWorks PR Review Pipeline - AI-powered code review workflow](https://github.com/markpollack/agentworks-pr-review)
  > 基于 AgentWorks 栈的 PR 审查流水线 - 用于 spring-ai 项目的 AI 驱动代码审查工具，支持确定性检查 + Claude 代码质量评估，生成详细审查报告和日志

- [talk-to-repo - AI-powered Spring Boot app to explore codebases](https://github.com/sivaprasadreddy/talk-to-repo)
  > Spring AI + pgvector + JGit 构建的 AI 代码库探索工具 - 克隆 repo、索引到向量数据库、RAG 生成 README、自然语言问答代码库

## 附录

1. 每日工作规划助手的提示词

```markdown
## Role

你是一个每日工作规划助手。你的职责是在每天早上基于用户当前可访问的信息，快速整理当天最重要的工作重点，并输出一份清晰、可执行、可快速浏览的当日计划。

你的核心目标是帮助用户：

- 梳理当天优先级
- 提炼待跟进事项
- 发现风险、冲突与阻塞
- 将零散信息转化为一份有顺序、有重点的行动计划

## Information Sources

优先使用以下已配置来源获取信息：

- Google Calendar：查看当天日程、会议时间、时间空档与潜在冲突
- Gmail：查看需要尽快处理、跟进或回复的重要邮件
- GitHub：查看与用户相关的近期动态，例如待处理 issue、pull request、代码评审或阻塞项

如果某个来源暂时不可用或没有足够信息，继续基于其余来源完成计划，不要因为单一来源缺失而停止。

## Daily Planning Workflow

在生成每日计划时，按以下顺序工作：

1. 先识别当天已有固定承诺，例如会议、重要时间节点、截止时间或已排定事项。
2. 从邮件和 GitHub 动态中提炼需要用户推进、决策、回复或关注的事项。
3. 合并重复或高度相关的事项，避免输出冗余任务。
4. 判断哪些事项最值得今天优先完成，哪些可以安排在会议前后处理，哪些仅需关注或等待。
5. 明确指出可能影响执行的风险，例如时间冲突、待确认事项、缺失依赖、可能被忽略的跟进项。
6. 最终生成一份结构清晰的当日计划。

## Prioritization Rules

确定优先级时，优先考虑以下因素：

- 今天是否有明确截止时间或会议前必须完成的准备工作
- 是否存在别人正在等待用户回复、批准、决策或推进
- 是否存在阻塞他人或阻塞后续工作的事项
- 是否是高影响、高确定性、可以今天推进的重要工作
- 是否容易因遗忘而带来风险的跟进项

如信息不足，不要编造具体事实。应基于已有证据给出合理排序，并明确说明不确定点。

## Default Deliverable Guide

默认输出一份简洁但完整的中文当日计划，结构如下：

### 今日重点

用 2 到 5 条列出今天最重要的工作重点，按优先顺序排列。每条都应说明为什么重要或为什么应先做。

### 时间安排建议

结合日历安排，给出当天的建议执行顺序。重点说明：

- 哪些事项适合在会议前处理
- 哪些事项适合在空档时间推进
- 哪些事项需要预留整块时间

### 待跟进事项

列出需要回复、确认、催办、评审或继续推进的事项。

### 风险与阻塞

列出当天最值得注意的冲突、依赖、模糊点或潜在遗漏。

### 建议的第一步

最后给出一个最建议用户立即开始的动作，帮助用户快速进入执行状态。

## Output Standards

输出应满足以下要求：

- 先给结论，再给支撑信息
- 保持清晰、简洁、可执行
- 避免长篇复述原始信息
- 不要把所有输入机械罗列为清单；应先整理、归纳、判断再输出
- 当某项建议明显来自特定来源时，可简要点明来源，例如“来自今天上午的会议安排”或“来自待回复邮件”
- 如果当天信息很少，也要给出最简版计划，而不是空泛回应

## When Information Is Thin

如果当天没有明显的日历安排、邮件重点或 GitHub 待办：

- 明确说明今天的外部输入较少
- 输出一个轻量版计划
- 重点建议用户先处理最可能积压的沟通、审查或主动推进事项
- 不要为了填满结构而捏造任务

## Safety

- 不要伪造会议、邮件、仓库动态或任务状态
- 不要将猜测表述为事实
- 如果无法确认优先级依据，要明确说明依据有限
- 若多个来源之间存在矛盾，优先指出矛盾并保守建议用户先确认再执行

```

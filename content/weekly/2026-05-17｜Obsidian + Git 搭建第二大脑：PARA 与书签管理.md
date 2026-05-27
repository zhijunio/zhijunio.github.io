---
title: "Obsidian + Git 搭建第二大脑：PARA 与书签管理"
date: 2026-05-19 10:00:00+08:00
slug: "20260517-weekly"
tags: [ "weekly", "obsidian", "hermes", "ai" ]
draft: false
description: "本周（5/11～5/17）：用 Obsidian + Git 搭建 second-brain 第二大脑，Telegram/Hermes Agent、PARA 目录与书签 Skill 替代 Linkding；9 路定时日推、Memos 同步与注意力治理；精简 GitHub 与 Wiki 囤积。"
---

本篇记录 **2026-05-11～2026-05-17** 的输入、输出与思考。重点是 **Obsidian 第二大脑（second-brain）** 知识库搭建：以 [Hermes Agent](/posts/20260412-week-review) 与 Telegram 为入口，用 Markdown、Agent Skill 和 PARA 目录整理个人知识，并梳理定时日推与注意力管理。

## 本周摘要

- **知识库**：Obsidian Vault 命名为 second-brain，Git 同步；目录按「输入 → 消化 → 输出 → 领域」流转（`01-raw` → `02-digest` → `11-note` / `12-review` → `21–23` 领域层）；`03-todo` 合并原计划与想法；`11-note/tech`、`11-note/reading` 承接两类深度产出。
- **入口**：Telegram + Hermes 替代部分自建服务；书签用 Skill 写入 Markdown，Memos 作 Web 展示。
- **自动化**：工作日 9 路日推（逻辑、面试、概念、育儿等）+ 周日周报，产出进 Memos 与 Telegram。
- **治理**：按年度目标做周报审计；精简 GitHub 仓库、Obsidian 插件与 wiki 囤积，聚焦注意力。

## Obsidian 第二大脑

目前，我主要用 [Obsidian](https://obsidian.md/) 管理笔记，并按个人成长、工作、健康等领域划分目录；另有一个 wiki 目录，曾用 [LLM 搭建 Obsidian 知识库](/posts/build-llm-wiki-with-karpathy) 收录 500+ 原始文件。

在使用 [Hermes Agent](/posts/20260412-week-review) 的过程中，逐渐把 **Telegram + Hermes** 当作知识管理入口：有了 Agent Skill，许多自建 Docker 服务与独立 App 的必要性下降——在大模型加持下，用 Markdown 即可管理知识与信息。

例如：此前在 VPS 部署 [Linkding](/posts/linkding-rss-personal-knowledge-management-system) 管理书签，现改为 **Skill + Markdown** 落盘。在 Hermes 中创建书签入库技能很容易，把提示词发给 Hermes 即可生成 Skill。

```markdown
你是「书签整理员」（按需技能）。

**触发**：用户消息经 trim 后**整段仅为一条**合法 `http(s)` URL（首末可仅有空白或换行；**不得**夹附言、第二条链接或指令）；否则
**不执行**本技能。Webhook / 管道**负载为单条纯 URL** 时等同。**落盘前**仍检查：同目录是否已有同一 URL。

**锚文（`[]` 内：只选用、不后处理）**

- **优先**页面**标题**：`og:title` > `twitter:title` > `document.title`。
- 若缺失、过泛或不可信，改用**站点名称**（如 `og:site_name`、`application-name`、页内品牌/全站名，或读者熟悉的站名如「维基百科」「GitHub」）。
- **GitHub**：Issue/PR 页用**条目标题**字段；仓库根页可用 `owner/repo` 风格短名。

**正文**：正文无 `#` / `##`。同一行内：`[锚文](https://完整URL)` + 半角空格 + AI 总结（先「它是什么」，句号后再「使用场景」；*
*行内不换行**；过长压缩；不杜撰）。

**保存**：`02-digest/bookmark/YYYY-MM-DD-{文件名段}.md`。文件名段与 `[锚文]` **字面一致**，仅把 **`/`** 换成 **`-`**；**不**
改空格、**不**为缩短而裁字。**文末空行后另起一行**添加标签：`#书签`（标签只放在文件末尾）。

vault 根：`git pull` → 写文件 → `git add` 该文件 → `git commit`（含日期与文件名段）→ `git push`；失败则中止。

然后将文件内容发送到 Memos 和 Telegram。
```

书签保存在 Obsidian Vault 中；Vault 用 **Git** 管理与同步，只需在运行 Hermes 的服务器上 clone 该仓库即可。

我给这个 Obsidian 的 Vault 取了一个名字，叫做 second-brain，也就是第二大脑的意思。

再比如：我在 VPS 上部署了一个 memos 的服务，现在也可以改为使用 SKILL + Markdown 的方式来实现。只是，目前我并没有这样做，我现在将 memos 作为一个 web 展示系统，用来同步存储和展示 Obsidian 中的笔记。

![Memos 展示 Obsidian 笔记的自定义样式](01.webp)

> 之前，一直没有将 memos 用起来的一个原因是觉得 memos 的页面配色和布局太丑了。在大模型的帮助下，使用了自定义的 css 调整了页面配色、加宽二楼右栏宽度。

从上面可以看的出来，越来越多的文件在 SKILL 的助力下使用 markdown 的格式保存到了 Obsidian 当中。这时候，我就在想是否可以让 Obsidian 成为我的知识管理中心或者说是汇聚地。

于是有了更多的想法，比如，是否可以有一个轻便的日程和待办管理系统？这个系统不需要自建服务、不需要安装 APP，但是能够对外提供 API 接口查询日程和待办事项？

我想到了可以使用 GitHub Issues 构建一套个人日程和待办管理系统，实现以下功能：

- 随时随地创建任务（Telegram/网页/命令）
- 定时提醒和汇总（晨间简报/到期提醒/周报）
- 任务分类和优先级管理
- 历史记录和统计回顾

我让大模型帮我规划了这个系统的功能，还没有来得及实现。这时候，我在 github 上看到了一个开源的项目、任务、笔记、标签管理系统 [tududi](https://github.com/chrisvel/tududi)。tududi 采用了 PARA 的思想，将任务和笔记关联在一起而且是开源的、可以提供 API 接口，这个正是我想要的一个知识管理系统。

只是在试用的过程中，发现 tududi 的笔记不支持批量导入和导出功能、Markdown 编辑器也不好用、不支持 markdown 文件本地存储。如果在 tududi 上进行改造，会花费一定的时间和精力，是一件性价比比较低的投入。于是，我放弃了使用 tududi 的想法。

仍以 Obsidian **本地 Markdown** 管理笔记，便于同步与迁移。参考 tududi 与 [PARA 方法](https://fortelabs.com/blog/para/)，将目录重新整理（也可对照 [Obsidian CEO 的知识管理实践](/posts/how-obsidian-ceo-does-knowledge-management)）。

整理后的 Obsidian 一级目录如下：

- 01-index
- 02-project
- 03-area
- 04-resource
- 05-archive

在 03-area 下面再按领域进行划分子目录，比如 work、growth、family 等等。这时候，发现如果 work 目录下面再添加子目录，则目录层级就达到了三级。这不是我喜欢的，我希望目录层级不要太深。

于是，我将目录调整成了如下的样子。

```markdown
second-brain/
├── 01-raw/                # 收藏 URL 抓取下来的原始内容
├── 02-digest/             # Hermes/AI 处理后的知识摘要，待消费
│   ├── biography/
│   ├── bookmark/
│   ├── car/
│   ├── concept/
│   ├── github-repo/
│   ├── interview/
│   ├── logic/
│   ├── parenting/
│   └── relationship/
├── 03-todo/               # 待办、计划、想法（原 04-plan、05-idea 已合并）
├── 11-note/               # 通用输出笔记
│   ├── tech/              # 单技术详细拆解（技能「技术名称详解」）
│   ├── reading/           # 技术文章 5D 拆解（技能「技术文章拆解」）
│   └── wiki/              # 工具/主题索引类笔记
├── 12-review/             # 周报、日记、复盘等时间型输出
├── 13-resource/           # 工具资产，如提示词、模板、参考物
│   └── AI提示词/
├── 21-growth/             # 成长领域
├── 22-family/             # 家庭领域
│   └── assets/
├── 23-work/               # 工作领域
└── _docs/                 # Hermes 系统文档
    ├── cron/
    ├── skill/             # 技能正文（书签入库、技术文章拆解、技术名称详解）
    └── prompt/            # 技能索引（指向 skill/ 同名文件）
```

**命名约定：**

- 目录编号只表达层级语义，不表达时间、优先级或任务顺序。
- `0x` 表示输入。
- `1x` 表示输出。
- `2x` 表示领域。
- `_` 前缀表示系统目录，不属于普通笔记内容。

**目录职责如下：**

```markdown
### 输入层

- `01-raw/`：外部收藏内容的原始正文，只保存，不提炼。
- `02-digest/`：Hermes 或其他 AI 处理后的摘要内容。这里是待消费知识，不代表已经内化。
- `03-todo/`：待办、计划、方案草稿、想法与行动提醒。

### 输出层

- `11-note/`：不强绑定某个领域的通用笔记、总结、方法、思考。
- `11-note/tech/`：单技术详细拆解（Hermes 技能「技术名称详解」），如 `mysql-mvcc.md`。
- `11-note/reading/`：技术文章 5D 深度拆解（Hermes 技能「技术文章拆解」）。
- `11-note/wiki/`：索引、清单类笔记。
- `12-review/`：按时间组织的输出，如周报、复盘、阶段记录。
- `13-resource/`：工具型资源，不属于正文知识或领域内容，例如 AI 提示词、模板、参考清单。

### 领域层

- `21-growth/`：个人成长相关长期内容。
- `22-family/`：家庭相关长期内容。
- `23-work/`：工作相关长期内容。

### 系统层

- `_docs/`：Hermes agent 使用的系统文档，不存放普通笔记。
- `_docs/cron/`：定时任务提示词和执行说明。
- `_docs/skill/`：技能正文（触发、落盘、Git 等）。
- `_docs/prompt/`：技能索引页，指向 `skill/` 同名文件。
```

**使用规则：**

1. 原始收藏内容优先进入 `01-raw/`。
2. AI 处理后的摘要进入 `02-digest/`，不要直接视为自己的最终知识。
3. 自己的待办、计划、想法统一放到 `03-todo/`。
4. 自己消化后的输出，优先放到 `11-note/` 或 `12-review/`；Hermes 技能默认：`11-note/tech/`（技术名称详解）、`11-note/reading/`（技术文章拆解）。
5. 明确属于成长、家庭、工作的内容，放到 `21-growth/`、`22-family/`、`23-work/`。
6. 提示词、模板、工具型资料放到 `13-resource/`，不要混入正文笔记。
7. `_docs/` 只保存系统运行文档，不放临时草稿和普通知识笔记。

**推荐的最小流转路径：**

```text
01-raw -> 02-digest -> 11-note / 12-review -> 21-growth / 22-family / 23-work
```

**补充说明：**

- `03-todo` 主要承接待办、计划与想法。
- `02-digest` 承接 Hermes/AI 的预处理输入（日推短稿等）。
- `11-note/tech`、`11-note/reading` 承接深度拆解；`12-review` 承接周报与复盘。
- `21-23` 是输出最终落到具体生活领域后的长期归档位置。

## Hermes 定时任务

在我的 second-brain 中，`02-digest` 承接 Hermes/AI 的预处理输入。我创建了一些定时任务，让 Hermes agent 定时的给我推送一些知识或者说是笔记。这些笔记是 Hermes 整理的，不是我自己整理的，是需要我消化、理解、吸收的，甚至需要我将他们进行输出。

![Hermes 定时任务与 second-brain 日推配置](02.webp)

我在 hermes 中创建了以下定时任务：

- Java 仓库日推：**每周一至周五 10:00**（UTC+8）从 GitHub 中推荐 **1 个**值得学习的中文短评。**不是**追热门，而是**先判断值不值得学，再推荐 1 个**。
- 亲密关系日推：**每周一至周五 19:00**（UTC+8）产出一篇短稿，让读者「少焦虑、能行动」，并尽量贴合当前关系阶段与相处场景。
- 传记日推：**每周一至周五 11:00**（UTC+8）产出一篇叙事紧凑的传记切片。**不是**全书导读，**不是**堆年份表。
- 概念日推：**每周一至周五 13:00**（UTC+8）产出一篇「单个词语或概念」的短分享。**本期讲什么由你自行选定**；**不要反问用户**，**不必**虚构读者画像。
- 汽车知识日推：**每周一至周五 12:00**（UTC+8）产出一篇短稿，让车主「少焦虑、能行动」，并尽量贴合当前车龄与用车场景。
- 育儿知识日推：**每周一至周五 06:00**（UTC+8）产出一篇短稿，让家长「少焦虑、能行动」，并尽量贴合当前月龄与家庭场景。
- 逻辑晨读：**每周一至周五 07:00**（UTC+8）产出一篇短稿，让读者「少困惑、能马上练」。
- 面试日推：**每周一至周五 08:30**（UTC+8）产出一篇**单点深挖**短稿，让读者能**答得清、说得透、少踩坑**。重心是 **「原理—边界—例子—自测」**，不是堆八股、不是只背定义。
- 做菜教程日推：**每天 17:00**（UTC+8）产出一篇菜谱，让读者「少翻车、能上桌」，并在忙碌生活中吃得更好。
- 每周工作总结：**每周日 22:00** 生成并发出一篇**中文周报**。统计窗口为**最近 7 天**（重点覆盖周一到周日），以我的2026年度目标为导向，采用「上帝视角」做直接的工作方式审查：评估时间安排是否合理、是否过度分散、投入产出是否匹配，并给出具体可执行建议。

以上定时任务产出的结果都会推送到我搭建的 [memos](https://memos.zhijun.io/) 上面，目前都是私有的，没有公开。如果你想要什么定时任务的提示词，可以联系我。

为了不让我每天的时间被 hermes 的定时任务的推送占满，我将大多数定时任务设置在周一至周五每天执行，周末时间用在带娃和理解消化上。

## 管理注意力

hermes 每天推送到定时任务比较多，容易出现自己的注意力分散，甚至根本没有消化定时任务推送到内容。于是，如何管理好自己的注意力是一件很重要的事情了。

首先，我会让每周工作总结这个定时任务以我的2026年度目标（在 Obsidian 中可以找到）为导向，采用「上帝视角」做直接的工作方式审查：评估时间安排是否合理、是否过度分散、投入产出是否匹配，并给出具体可执行建议。

![每周工作总结与 2026 年度目标对照](03.webp)

其次，我让 hermes 审核我的 github 中是否存在一些占用我注意力的项目：

![Hermes 审核 GitHub 仓库注意力占用](04.webp)

hermes 对我的 github 给出以下诊断：

- **严重的“碎碎念”与“脚手架”陷阱 (Fragmentation)**
- **虚荣指标型项目 (Vanity Metrics)**
- **“造轮子”陷阱 (Tool Building vs Product Building)**
- **过时或无用的「死资产」**

并给出了建议：

![Hermes 对 GitHub 仓库的改进建议](05.webp)

hermes 对我的博客给出以下诊断：

- 博客跑步页面：典型的重“展示”轻“跑步”
- 博客聚合页面：信息囤积的“松鼠症”

- SDD (Spec-Driven Development) 研究：双刃剑

![Hermes 对博客与 SDD 研究的诊断建议（二）](06.webp)

也给出了建议：

- 删除博客跑步页面
- 砍掉 80% RSS 订阅源
- 合并聚合页面到“友链”或直接废弃
- 将 SDD 研究转化为“项目实战

最后，我让 hermes 对我的 second-brain 也进行了分析：

> 基于你对我的了解，参考李笑来的思维方式和观点，我有哪些需要注意或者改进的地方？比如，必须管理好注意力，对此你有什么建议？我的 github、blog 仓库里面是否有一些占据了我的注意力且需要清理

以下是 hermes 的分析结果：

---
李笑来最核心的观点：注意力 > 时间 > 钱。注意力是唯一你真正拥有、且花出去就回不来的资源。

我从你的 GitHub 和 second-brain 里看到了三个明显的注意力黑洞：

**黑洞一：Wiki 系统（510 个 raw 文件，7.8MB，占总文件数的 69%）**

这是最大的问题。

wiki/raw/ 里有 510 篇从各种博客抓下来的长文（每篇 25-70KB），wiki/concepts/ 41 个概念卡片，wiki/sources/ 82 个来源页，wiki/entities/ 19 个公司/人物页。

李笑来的判断标准：**这东西在产出价值，还是在消耗注意力？**

Wiki 本质上是一个"信息收集系统"——把别人写的好文章搬进自己的仓库。但：

- 你读了多少？（`11-note/reading/` 里当时只有 1 篇深度拆解）
- 这些 raw 文件有多少被引用过？（绝大部分孤立存在，没有被其他笔记链接）
- 你在用它做什么决策？（几乎没有）

这是一个典型的"收集 = 学习"幻觉。 李笑来反复说：囤积信息不会让你变聪明，只会让你觉得"我在变聪明"。

**黑洞二：Obsidian 插件生态（13 个插件）**

你装了 13 个 Obsidian 插件：dataview、obsidian-git、github-sync、obsidian-tasks、quickadd、templater、obsidian-kanban、excalidraw、claudian、realclaudian、terminal、brat、Minimal 主题。

李笑来的判断标准：工具是在服务你，还是你在伺候工具？

Obsidian 是一个本地 Markdown 编辑器。你装了 13 个插件，意味着你花了很多时间在：

- 配置插件互相兼容
- 调 dataview 查询语法
- 搞 github-sync 和 obsidian-git 的冲突
- 折腾 kanban 面板
- 维护 claudian / realclaudian（两个 AI 插件？）

但你真正用的工作流是 Second Brain（纯 Git 仓库） + Telegram + Hermes Agent。Obsidian 只是偶尔打开看看——你不需要一个功能全开的笔记软件，你需要的是一个能用的文本编辑器。

**黑洞三：9 个定时日推 + README 过度工程化**

你现在的 cron 任务排满了每天：

- 06:00 育儿 → 07:00 逻辑 → 08:30 面试 → 10:00 Java 仓库 → 11:00 传记 → 12:00 汽车 → 20:00 亲密关系

每天 7 条推送，加上每篇都要写 Second Brain → Git → Memos → Telegram，这意味着你每天要消费 7 篇自己系统生成的内容。

李笑来的判断标准：你在用这些内容，还是这些内容在占用你的注意力？

每天 7 条 = 每周 49 条 = 每月 200+ 条。你不可能逐条消化。结果是：

- Telegram 通知变成噪音，你会习惯性忽略
- Second Brain 文件越来越多但没人回顾
- 系统越做越大，但产出（真正对你有用的学习成果）没跟上

---

在 hermes 的建议之下，我做了以下改进：

- 将我的 github 上一些 forked 项目删除，将长期不更新的项目归档。最终 github 项目数从 81 个减为 48 个。
- 卸载 Obsidian 中的 12 个插件，只保留 Git 插件，仅用 Obsidian 的 Markdown 文件管理功能。
- second-brain 中保留 raw 原始收藏文件，删除旧 wiki 目录；输出层拆为 `11-note/tech`、`11-note/reading`，周报迁入 `12-review/`，待办与计划合并进 `03-todo/`（后续又做了目录与 Hermes 技能拆分，见上文树状图）。

## 分享

有意思的输入多数会同步到 Telegram「[ZhiJun Share](https://t.me/s/zhijun_share)」。这里再挑一部分，方便当周报 / newsletter 用。

- [pixel-point/media-downloader](https://github.com/pixel-point/media-downloader) 一个开源的多平台媒体下载工具，支持从
  YouTube、TikTok、Spotify 等数百个站点下载视频和音频。适合需要批量抓取多源媒体资源的场景。
- [taigaio](https://github.com/taigaio) Taiga 开源敏捷项目管理工具的官方 GitHub 组织，包含后端 (taiga-back)、前端 (
  taiga-front)、Docker 部署 (taiga-docker) 等核心仓库。适用于需要自建、可定制的 Scrum + 看板项目管理方案的团队。
- [yetone/native-feel-skill](https://github.com/yetone/native-feel-skill) 一个跨平台桌面应用开发 Agent Skill，提炼自
  Raycast 2.0 架构深度分析与 Beta 版逆向工程。总结八大架构原则、四层架构设计、WebKit/WebView2 兼容性指南，以及 75
  项发布前审计清单。适合需要开发类原生体验桌面应用的场景。
- [用 Bub 和飞书搭一个更懂群聊上下文的小机器人](https://mp.weixin.qq.com/s/dDPEyZo2KLa0vG6yc9pQow) 一篇教程文章，介绍如何用
  Bub 和飞书搭建轻量化 AI 群聊助理，能理解群聊上下文且对话风格自然。适合需要为团队或社群部署智能助手的场景。

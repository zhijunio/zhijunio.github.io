---
title: "2026-04-12｜OpenClaw 迁移到 Hermes"
date: 2026-04-14 10:40:00+08:00
slug: "20260412-week-review"
tags: [ "ai", "openclaw", "hermes" ]
draft: false
categories: [ "weekly" ]
description: "本周记录：将 OpenClaw 迁移到 Hermes Agent、博客评论系统从 Artalk 切换到 Giscus、发表 5 篇技术博文与 10 篇公众号文章，以及 6 次户外跑 34.82 公里的运动总结。"
favicon: "openclaw.svg"
---

本篇博客介绍最近一周（2026-04-06 ～ 2026-04-12）的记录与思考。

## 摘要

- 博客：博客发布 5 篇文章。

  - [使用 OpenClaw 调用 Claude Code 开发应用](/posts/create-app-with-claude-code-in-openclaw)
  - [学 Karpathy 使用 LLM 搭建 Obsidian 知识库](/posts/build-llm-wiki-with-karpathy)
  - [SkillsJars：用 Maven 依赖管理 AI Agent Skills](/posts/skillsjars-quickstart)
  - [普通人如何用小龙虾记日记](/posts/how-to-use-xiaolongxia-diary)
  - [从 Vim 到 AI：开发工具这些年](/posts/programming-tools-evolution-timeline)

- 公众号：发表内容 10 篇文，原创文章 6 篇，图文 4 篇。阅览量 281 次，被分享 18 次。累计关注用户数 7 人，比上周增加 4 人。
  
  - 公众号贴图的封面图使用 [封面生成器 · Cover Maker](https://zhijunio.github.io/article-tools/cover.html) 工具制作，其源码在 [github](https://github.com/zhijunio/article-tools)。
  
- Wiki：发布一篇 wiki。

  - [Skills](/wiki/skills)：整理一些我觉得不错的 skill。

- 小龙虾。将 OpenClaw 迁移到 Hermes。在 claude 中输入下面提示词完成 Hermes 安装和配置迁移。如果你在 OpenClaw 里面是有了多
  Agent，则还需要额外的操作。因为 Hermes 是使用 Profile 来实现多 Agent。具体说明，可以参考官方文档。

  ```bash
  给我安装 hermes agent，并把在 openclaw 里面的所有配置迁移到 hermes 中（hermes 提供了迁移工具），包括但不限于和 Telegram 的配置、模型 API Key、Skill、记忆体系等等。
  ```

- 将博客评论从 Artalk 改为使用 Giscus，原因是博客目前本身没有多少评论，改为使用基于 Git 的 Giscus，可以不用自己中 VPS
  上单独部署服务。

## 健康

本周（04-06～04-12）共 **6 次**户外跑，合计约 **34.82 公里**。按原先「每天约 3.3 km」推算的周目标约 **23.1 公里**
。数据来自本站的 `running.json`。

| 日期    | 距离       | 配速    | 平均心率 |
|-------|----------|-------|------|
| 04-07 | 10.75 公里 | 7′38″ | 113  |
| 04-08 | 5.02 公里  | 7′22″ | 139  |
| 04-09 | 5.02 公里  | 7′58″ | 119  |
| 04-10 | 5.00 公里  | 8′19″ | 141  |
| 04-11 | 4.52 公里  | 8′25″ | —    |
| 04-12 | 4.51 公里  | 8′39″ | 145  |

**小结：** 本周跑了 6 次，其中 04-07 有一次 **10.75 km** 长距离，其余为 **4.5～5 km** 常规跑；配速从 **7′22″**（04-08）到 ***8′39″**（04-12）不等。*
**04-11** 平均心率为 **0**（未戴心率或未记录）。在有记录的几天里，平均心率大致在 **113～145**，整体仍偏有氧；04-07
长距离日心率较低（113），节奏控制得不错。

## 分享

我使用 [Linkding](https://linkding.zhijun.io/) 书签来保存我认为不错的资源，包括文章、视频等等。虽然大部分有意思的输入都会自动同步到「[ZhiJun Share](https://t.me/s/zhijun_share)
」Telegram 频道，但我还是想在这里额外挑一部分出来。单独列出来之后，这篇周报就更像一份 newsletter 了。

### 技巧

**国内打开登录 Antigravity 账号的技巧**
小伙伴发现一个打开登录 Antigravity 账号的方式，确保你的地址是美国，年龄符合情况下，也很有可能登录不上，试了很多方法都不行，最后想着用
antigravity-tools 转发使用，没想到它有一个一键打开功能，登录后点击下面这个，一键唤起居然可以直接可以使用了，很神奇，分享给需要的朋友。

```bash
brew install --cask --no-quarantine antigravity-tools
```

**如何把你的歌单迁移到另外一个平台？**
https://tunemymusic.com/zh-CN/transfer
今天有一个歌单需要从网易云音乐转移到 Apple
Music，查了查解决方案，还不错，导入了绝大部分歌曲，首先去 [https://music.unmeta.cn](https://music.unmeta.cn/)
把歌单地址转化成文本格式。然后去 https://tunemymusic.com/zh-CN/transfer 选择任意文本模式，复制刚刚的歌单文本转化成歌单格式列表，点击转化选择
Apple Music，然后登录后，点击转化，你将看到一首首歌到了你的 Music，非常好用，然后就改改名称就好。

### 文章

- [Roadmap To Learn Agentic AI](https://github.com/krishnaik06/Roadmap-To-Learn-Agentic-AI)
  > Krish Naik 整理的 Agentic AI 学习路线，涵盖 Python、NLP、Generative AI、MCP、LangChain、CrewAI、AutoGen 等

- [Agentic Engineering Roadmap 2026](https://github.com/jcouso/agentic-engineering-roadmap)
  > 90 天成为 agentic engineering 和 model systems 专家，包含 CLI 工具栈、多 Agent 系统、模型微调与评估

- [openclaw/skills - diagram-generator](https://github.com/openclaw/skills/tree/main/skills/matthewyin/diagram-generator)
  > clawhub.com 收录的 diagram-generator 技能，用于生成架构图等图表

- [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill)
  > 让 Claude Code 及其他编码 Agent 能够生成美观实用的 Excalidraw 图表的技能工具

- [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator)
  > 生成深色主题系统架构图的工具，可输出 standalone HTML/SVG 文件，支持作为 Claude AI skill 使用

- [XiaomingX/ai-money-maker-handbook](https://github.com/XiaomingX/ai-money-maker-handbook)
  > AI副业赚钱方法合集，提供多种利用AI赚钱的策略和具体项目案例。涵盖内容创作、自动化工具开发、SaaS平台、咨询服务等多个方向，帮助在AI时代赚取额外收益。

- [魔方简历 - AI 驱动简历编辑器](https://magicv.art/zh)
  > 魔方简历是一款开源的简历编辑器，免费，隐私优先。无需注册登录，数据完全存储在本地，支持数据导出备份，确保您的简历数据随时可用。

- [EwingYangs/x-user-skill-creator](https://github.com/EwingYangs/x-user-skill-creator)
  > 这是一个从任意推特用户的推文生成 AI agent skill
  的工具。提供推特资料链接后自动抓取推文、提炼知识、生成可安装的技能目录。包含推文抓取、主题发现、知识包生成、原子库构建等完整流程，支持人工审查确认。

- [Erduo Skills - AI Agent 技能库](https://github.com/rookie-ricardo/erduo-skills)
  > Erduo Skills 是一个 AI Agent 技能库，收录了一系列可被 Agent 直接调用的结构化技能，提供信息获取、内容处理、图像工具等场景的智能工作流。包含每日日报（多源抓取+智能筛选）、AK
  RSS Digest（固定 RSS 源精选摘要）、转录精修师（语音转录文本精修为可读文章）、翻译精修师（四步精翻工作流，支持中英/中日双向）、Web
  To Markdown（URL 路由抓取输出干净 Markdown）、Gemini 水印移除（逆向 Alpha 混合算法去除水印）等技能。支持作为 Claude Code
  plugin marketplace 注册使用。

- [microsoft/markitdown](https://github.com/microsoft/markitdown)
  > MarkItDown 是微软开源的轻量级 Python 工具，用于将各种文件和办公文档转换为 Markdown，供 LLM 和文本分析管道使用。支持
  PDF、PowerPoint、Word、Excel、图片（EXIF 元数据和 OCR）、音频（EXIF 元数据和语音转录）、HTML、文本格式（CSV、JSON、XML）、ZIP
  文件、YouTube URL、EPub 等。专注于保留重要的文档结构和内容（标题、列表、表格、链接等）。可与 Azure Document Intelligence 和 LLM
  集成用于图像描述。支持插件系统和 MCP 服务器。

- [Distributed Transaction Management Using Apache Seata | Baeldung](https://www.baeldung.com/apache-seata-distributed-transaction-management)
  > This article introduces how to use Apache Seata to implement distributed transaction management in Java
  microservices applications. It explains why distributed transactions are needed, the architecture of Seata (
  Transaction Coordinator, Transaction Manager, Resource Manager), how to use Seata Server via Docker, how to configure
  Seata in Spring Boot (including configuration files and undo_log table), how to use the @GlobalTransactional
  annotation, how to handle transaction propagation in Spring (via HTTP headers to pass XID), how to use Seata in Spring
  Cloud, and provides complete code examples.

- [Mill Build Tool](https://mill-build.org/)
  > Mill 是一个为 Java、Scala 和 Kotlin 提供的构建工具，旨在改进传统 JVM 生态系统中的构建工具。比 Maven 更简单（配置文件通常是
  pom.xml 的 1/10），比 Gradle 或 SBT 更容易（采用面向对象的构建方式），是 JVM 上最快的构建工具（通过积极的缓存和并行化实现
  3-7 倍的速度提升）。支持内置的大多数 JVM 开发工作流，包括依赖管理、测试、代码检查、打包、发布等。

- [https://linklearner.com/](https://linklearner.com/)

- [Sink](https://sink.cool/)
  > 一款简单/快速/安全的链接缩短服务，带有分析功能，100% 基于 Cloudflare 运行。

- [How to Start a Successful YouTube Channel in 2026](https://timqueen.com/youtube-start-channel)
  > 看到一篇很详细的教你做 Youtube 频道的文章「2024 年如何打造一个成功的 Youtube
  频道」，从为什么、心态、为啥可以赚钱、怎么做、如何优化、如何选题、分析等方面都有介绍，挺值得想做视频的小伙伴一看。

- [开源的 dub 短链工具](https://dub.co/)
  > 这个开源的 dub
  短链工具有推荐过，后面一些长链接我一般会用这个转一下，相比其他的产品有几个好处，可自定义短地址字符串、可以项目方式管理、免费版本够使用、不会过期、可以统计点击流量，把我想到的一个短链产品该做的都做到了，居然还做得这么好。

- [一个超级易用的临时邮箱](http://email.ml/)
  > 看到一个超级易用的临时邮箱 Email.ML，在 Cloudflare 上运行，使用的时候直接生成一个临时的地址，测试了一下，效果挺好用的，特别适合一些你不想把你真正邮箱放出去的场景。

- [Get out of my <head>](https://getoutofmyhead.dev/)
  > 一个关于网页优化指南，通过移除网站 <head> 标签中的某些标签，让网站更快、更易访问、更环保。

- [独立开发者出海工具箱](https://indiehackertools.net/)
  > 独立开发者出海工具箱

- [李沐讲座：大语言模型的实践经验和未来预测](https://www.youtube.com/watch?v=ziHUcDh0DwM)
  > 假如你对 AI 发展感兴趣 ，想了解大语言模型的实践经验和对于 AI 的未来预测，可以看看李沐在上海交大的讲座，讲得挺好的，相比国外的事情，这个视频会更有技术亲切感。

- [Modern CSS Solutions](https://moderncss.dev/)
  > 假如你对 CSS 感兴趣，或者写习惯了 Tailwind 这种格式化的样式，或许可以去看看这个现代 CSS 解决方案，介绍了很不错最近几年不错的
  CSS 的写法，可以去把玩把玩。

- [AI-native project management | Plane](https://plane.so/)
  > 这个开源的项目管理工具 Plane 做得挺完善的，JIRA、Linear、Monday 这一类产品的开源替代，用简单产品化的思路来跟进
  issue、产品里程碑、节奏的工具，可以去试试看。

- [NewsNow](https://newsnow.busiyi.world/)
  > NewsNow 是一个实时新闻聚合阅读器，汇集全球热点新闻，提供优雅的阅读体验。

- [Y2Z/monolith](https://github.com/Y2Z/monolith)
  > 一条命令行就把一个网页打包成一个单独的 html 文件

- [Choose an open source license | Choose a License](https://choosealicense.com/)
  > 如何选择一个合适的开源协议

- [Lucide](https://lucide.dev/)
  > Lucide 是由社区创建的美观一致的图标工具包。提供轻量级可缩放的 SVG 图标，具有严格的设计规则确保风格和可读性的一致性。支持自定义颜色、大小、描边宽度等，可
  Tree shaking 仅导入使用的图标。活跃的社区，支持所有主要包管理器。

- [本地运行 GitHub Actions 的工具](https://github.com/nektos/act)
  > 假如你有 GitHub Actions 需要更高效的调试效果，可以试试 act 这个本地运行 GitHub Actions 的工具，安装后直接读取
  .github/workflows/ 里面的文件去执行，相比每次改动去看云端的变化可以提高开发效率。

- [Cap: Self-hosted CAPTCHA for the modern web.](https://capjs.js.org/)
  > Cap is a lightweight, modern open-source CAPTCHA alternative using SHA-256 proof-of-work and instrumentation
  challenges

- [Rybbit](https://rybbit.com/zh)
  > Rybbit 是下一代开源、轻量级、无 Cookie 的网页和产品分析工具，Google Analytics
  的替代品。支持实时数据、会话回放、漏斗分析、用户旅程、网页性能指标、自定义事件、机器人拦截等功能。100% 开源，可自托管或使用云服务。隐私优先设计，零
  Cookie，零横幅，GDPR & CCPA 合规。几分钟内完成部署，提供完整 API 和数据导出功能。

- [好拼 - 免费在线拼图工具](https://img.ops-coffee.cn/photo/)
  > 一款强大的免费在线拼图工具，支持多种网格布局，无水印免登录直接下载。无需下载软件，浏览器在线即可轻松拖拽图片，调整间距、圆角和背景，创作出个性化的照片拼图。支持直接拖拽替换图片、按住
  Alt (Option ⌥) 拖拽平移、使用方向键平移。适合制作小红书首图、抖音封面、淘宝拼图、拼多多拼图等。

- [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)
  > 12-factor Agents 是受 12 Factor Apps 启发的指南，旨在探讨构建适合生产环境的 LLM 驱动软件的核心工程原则。涵盖 12
  个原则：自然语言转工具调用、掌握提示词、管理上下文窗口、工具即结构化输出、统一执行状态与业务状态、启动/暂停/恢复
  API、通过工具调用联系人类、掌控控制流、压缩错误到上下文、小型专注的代理、从任何地方触发、无状态化约器等。强调模块化概念和自建可控方案优于完全依赖框架。

- [Color Generator – Kigen](https://kigen.design/color)
  > Kigen Color Generator 是一个设计系统配色工具，可生成优美的调色板。支持 RGB 输入、Tailwind CSS 算法、对比度调整、50-900
  命名模式、11 种色阶，以及 SVG/Figma 导出。支持多种颜色格式（HEX、RGBA、HSL、OKLCH）和 CSS 输出（Tailwind、Tailwind 4、Tokens）。由
  Overlayz Studio 开发。

- [Clash Party](https://mihomo.party/)
  > Clash Party 是一个更易用的 Clash 客户端，提供更友好的用户界面和体验。页面推荐认证机场服务，提供自研 iOS
  客户端、真人客服、高速专线、Quic 协议支持、流媒体和 AI 解锁等功能。

- [一系列开源、可靠、全球 CDN 加速的开放 API 集合](https://docs.60s-api.viki.moe/)
  > 一系列开源、可靠、全球 CDN 加速的开放 API 集合，包括日更资讯、榜单、翻译、百科、热搜这种常用工具接口的开放能力，也可以自己部署。

- [Figma Design for beginners – Figma Learn](https://help.figma.com/hc/en-us/sections/30880632542743)
  > Figma 官方帮助文档页面，提供 Figma Design 初学者教程。包含 Figma Design、Dev Mode、FigJam、Figma Slides、Figma Draw、Figma
  Buzz、Figma Sites、Figma Make 等产品的文档，以及 AI 功能、可访问性、开发者文档、社区资源等。提供课程、项目、教程和故障排除支持。

- [21 Lessons, Get Started Building with Generative AI](https://github.com/microsoft/generative-ai-for-beginners)
  > 微软开源的这个 21 Lessons, Get Started Building with Generative AI 值得一看，用 21 节课来学习构建生成式 AI
  应用，新鲜内容，适合新手跟着一步一步走下去。

- [Resend](https://resend.com/)
  > Resend 是面向开发者的电子邮件 API 服务，提供简单、现代化的 API 来大规模发送事务性和营销邮件。支持 CLI 工具、MCP
  服务器、多种语言的 SDK（Node.js、Python、PHP、Ruby、Go、Java、Laravel、Rust、.NET），并提供完整的 OpenAPI 规范和文档。

- [addyosmani/gemini-cli-tips](https://github.com/addyosmani/gemini-cli-tips)
  > Gemini CLI 实用技巧集合，涵盖约 30 个专业提示，帮助用户更有效地使用 Gemini CLI 进行智能编程。包括：使用 GEMINI.md
  持久化上下文、创建自定义斜杠命令、通过 MCP 服务器扩展功能、内存管理与检查点、文件引用、系统故障排除、YOLO 模式、无头/脚本模式等。

- [Building an AI-native engineering team](https://cdn.openai.com/business-guides-and-resources/building-an-ai-native-engineering-team.pdf)
  > OpenAI 的这个 Building an AI-native engineering team 的 pdf 值得一看，告诉技术团队的管理者，如何构建一个 AI 原生的工程师团队。

- [bylinxx/MacCalendar](https://github.com/bylinxx/MacCalendar)
  > 完全免费且开源的离线 macOS 菜单栏日历应用，界面简洁精致。支持中国农历、24节气、大部分节日（公历或农历）、中国法定放假安排（2015年以来）、读取系统日历数据。可自定义菜单栏显示内容，支持手动安装或
  Homebrew 安装。

- [Manus' Final Interview Before the Acquisition: Oh, the Surreal Odyssey of 2025…](https://www.youtube.com/watch?v=UqMtkgQe-kI)
  > Manus 联合创始人兼首席科学家 Peak Ji 在被收购前的最后一次采访。记录于 2025 年 12 月 1 日，分享了 2025 年的超现实旅程。

- [Agentic Design Patterns | 《Agentic Design Patterns》中文翻译项目 - 系统介绍 AI Agent 系统的各种设计模式](https://adp.xindoo.xyz/)
  > 《Agentic Design Patterns》中文翻译项目，系统介绍 AI Agent 系统的各种设计模式，涵盖 21
  个核心章节（如提示链、路由、并行化、反思、工具使用、规划、多智能体协作等）和多个附录章节。所有 32 个文件已完成初步翻译，目前处于待审核状态。

- [Storyset | Customize, animate and download illustration for free](https://storyset.com/)
  > 免费插画网站

- [一个挺有意思的网站检查工具 Web-Check](https://web-check.xyz/)
  > 最近发现一个挺有意思的网站检查工具 Web-Check，整体偏 hacker 风格。它可以把一个网站的几乎所有底层信息都拆给你看：IP
  与服务器位置、SSL 与 DNS 记录、Cookie、域名信息、爬虫规则、跳转历史、开放端口、Traceroute、DNSSEC、站点性能以及关联主机等，信息密度很高，适合随手查一查好玩的。

- [TwiN/gatus 面向开发者的可视化状态报警工具](https://github.com/TwiN/gatus)
  > Gatus 是一个面向开发者的健康仪表板，你可以使用 HTTP、ICMP、TCP 以及 DNS
  查询来监控你的服务，并通过一系列条件（如状态码、响应时间、证书过期、正文等）评估查询结果，然后健康检查可以与
  Slack、Teams、PagerDuty、Discord、Twilio 等多种警报系统相配合使用。

- [Codia AI NoteSlide — Turn NotebookLM Slides into Fully Editable PowerPoint](http://codia.ai/noteslide)
  > Codia AI NoteSlide 把 NotebookLM 导出的 PDF 直接转成 PPT

- [Beautiful Mermaid](https://github.com/lukilabs/beautiful-mermaid)
  > 好看的 Mermaid 渲染器，专为 AI 时代设计

- [nanobot](https://github.com/HKUDS/nanobot)
  > nanobot 这种更轻、更适合放在个人电脑上的 OpenClaw 形态

- [Amphetamine 让你的 Mac 电脑不休眠](https://apps.apple.com/us/app/amphetamine/id937984704)
  > 当你需要运行类似龙虾或者 nanobot 的时候，其实很不想关掉息屏，甚至想着关上盖子也继续运行，找到了这个软件，免费不错，非常适合你用家里的
  Mac 但是想它关掉屏幕一直开着，就可以试试这个。

- [Readout](https://readout.org)
  > 可实时可视化你的 Claude Code 环境，它能展示 AI、会话、仓库、费用、MCP、端口等信息，并提供即时全局搜索，以及带时间轴回放的完整会话重播，本地运行，不要账号，期待他接下来的发展。

- [MicroGPT explained interactively | growingSWE](https://growingswe.com/blog/microgpt)
  > 一个非常棒的交互式 MicroGPT 演示。这个是基于 Andrej Karpathy 用大约 200 行 Python 代码实现的
  GPT，并以可视化的方式解释了语言模型的工作原理的学习网站，值得看看。

- [Learn Claude Code](https://learn.shareai.run/en/)
  > 了解类 Claude Code 的原理的学习， 一步步引导你从零开始构建一个极简的类似 Claude Code 的 Agent，并详细解释每个机制，值得一看。

- [Jina AI - Your Search Foundation, Supercharged.](https://jina.ai/)
  > Jina AI 提供一流的嵌入、重排序、网页阅读器、深度搜索和小语言模型。支持多语言和多模态数据搜索的 AI 搜索基础设施。

- [TinyFish – Enterprise Infrastructure for AI Web Agents](https://www.tinyfish.ai/)
  > TinyFish 为 AI Web Agent 提供企业级基础设施，支持同时运行数百个网站操作。提供无服务器架构，可导航、认证、提取数据和自动化工作流，一个
  API 调用即可完成任务。

- [jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud)
  > Claude Code 插件，实时显示上下文使用情况、活跃工具、运行中的代理和 todo 进度。支持多种布局预设、中英文界面、自定义颜色和显示选项，通过原生状态栏
  API 集成，无需额外窗口。

- [The Universal Documentation Engine - docmd](https://docmd.io/)
  > docmd.io 是一个通用文档引擎，提供自定义 Markdown 语法支持复杂布局，内置深色/浅色模式、即时模糊搜索、SEO 插件等功能。支持多版本文档、AI
  友好的语义容器，以及零重载导航和超轻量级独立 HTML 文件。

- [在 AI 时代，我是如何深入学习一个技术领域的](https://tw93.fun/2026-04-06/learn.html)
  > 想聊聊在 AI 时代我是怎么深入学一个新领域的，从收集资料、筛选阅读、写大纲，到 AI 辅助精简、自读发布，我把整个过程当代码一样组织起来。

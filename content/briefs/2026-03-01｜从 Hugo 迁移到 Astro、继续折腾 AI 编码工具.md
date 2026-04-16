---
title: "2026-03-01｜从 Hugo 迁移到 Astro、AI 编码工具"
date: 2026-03-05 21:00:00+08:00
slug: "20260301-week-review"
tags: [ "astro" ]
draft: false
categories: [ "weekly" ]
description: 这周主要在两条线上投入时间：把博客从 Hugo 迁移到 Astro，也继续试用了 Codex CLI、Gemini CLI、Claude Code 和 OpenClaw。
favicon: "astro.svg"
---

本篇博客介绍最近一周（2026-02-23 ～ 2026-03-01）的记录与思考。

## 博客从 Hugo 迁移到 Astro

花了一个多星期将[博客从 Hugo 迁移到了 Astro](/posts/2026/02/26/from-hugo-to-astro-blog)，并美化主题。当然，这篇文章只记录迁移的部分内容，后续我又对 Astro 主题做了进一步重构。

初始的 Hugo 搭建的博客如下图，使用的是 [rose-hugo](https://github.com/zhijunio/rose-hugo) 主题，这个主题是我基于 [Mainroad](https://github.com/Vimux/Mainroad) 主题做了一些修改。

![blog-hugo-rose-theme](/images/20260301-week-review/01.webp)

后来看到了 [Frost's Blog](https://frostming.com/)，发现该博客风格比较简洁，于是想使用该主题，但是找不到该博客主题的源码，于是使用 AI 复刻了该主题。再后来，看到 [游钓四方](https://blog.lhasa.icu/) 之后，发现该博客访问速度快、样式美规紧凑、主题源码开源，于是就有了 [博客从 Hugo 迁移到了 Astro](/posts/2026/02/26/from-hugo-to-astro-blog) 这篇文章。

在迁移过程中，遇到的最大的问题是主题切换的功能一直存在问题，于是禁用了 Astro 动画，改为整个页面刷新，并且修改了 critters 的配置（`mergeStylesheets: false`），避免 CSS 裁剪或重排导致样式被覆盖。

再后来看到 [Yiran's Blog](https://zdyxry.github.io/) 之后，参考该网站，将导航修改为固定模式、Footer 部分添加了社交链接、重构了 Astro 布局、去掉了分类页面（将分类列表添加到了归档页面上方，同时添加了按年份导航）。

![blog-astro-archives](/images/20260301-week-review/02.webp)

总结一下，花在博客主题改造和排错的时间太多了，有点因小失大。毕竟铁打的营盘流水的兵，三十年河东三十年河西。博客只是一个记录文字的工具，博客构建工具层出不穷，博客主题也会随着时间流逝让人出现审美疲劳，说不定以后的哪天又换了一个博客生成器和主题。所以，完全不应该在博客主题上花费太多时间了，而应该把时间花在学习有用、回报率高的事情上，比如说 AI、大模型等等。

## 大模型

一直在使用 Cursor 作为 vibe coding 的主力工具，因为账号是公司开通的，不用担心费用问题。奈何20美元的额度总是早早用完了，导致只能使用免费在模型。以下是最近一个月 Curosr 的提交代码统计。

![cursor-dashboard-20260305](/images/20260301-week-review/03.webp)

为了解决这个问题，于是尝试了 Codex CLI（[Codex CLI 安装、配置、使用与认证指南](/posts/2026/03/03/codex-cli-guide)）和 Gemini（[Gemini CLI 安装、配置、使用与认证指南](/posts/2026/03/02/gemini-cli-guide)）以及 Claude Code（[Claude Code 安装、配置、使用与认证指南](/posts/2026/03/05/claude-code-guide)）。

公司也提供了 Codex 的 token，只是之前一直没有配置好，所以用的少。摸索了一下之后，就把配置搞定了。这里推荐一个工具，叫做 [CC Switch](https://github.com/farion1231/cc-switch)，可以通过图形化的方式配置 Claude Code、Codex、Gemini CLI、OpenCode 和 OpenClaw 等 CLI 工具。

Codex 发布了桌面客户端，这篇视频 [Codex APP 保姆级使用教程，实战项目全流程讲解，覆盖 Codex APP十一个特性](https://www.bilibili.com/video/BV1oJAoz2Emf)  介绍了 Codex App 的使用技巧。 

**Gemini CLI** 安装之后，使用到倒是不多，网页版的倒是用起来很不错。**Google Gemini** 的基础版本（使用 Gemini 3 Pro 或 Flash 模型）对个人用户是完全免费的，且支持中文对话。

部分地区或特定账户设置可能会限制图像生成功能。需要确保使用的是 **Gemini Advanced** 或在支持的地区（如美国、新加坡）。

Claude Code 我没有在官网购买订阅，因为没有 Visa 信用卡，所以只能使用中转站。Claude Code 的配置之前也是存在问题，直到使用 CC Switch，才解决了配置的问题。我使用 OpenRouter 接入，充值了 5 美元（实际支付 5.8 美元），不到半天时间就花光了。于是，还是回过头来使用 Cursor 和 Codex 。

## OpenClaw 小龙虾

因为要安装 OpenClaw，我把我的 VPS 服务器重装了系统。因为之前使用到是 Centos 8，能够安装到 Nodejs 版本低，无法成功安装 OpenClaw。重装后的系统是 AlmaLinux 9，是 Centos 9 的开源版本，命令一致，对于熟悉 Centos 的我来说，很容易上手。

VPS 系统重装了之后，花了时间重新设置系统、部署 Docker 服务，并且更新了文章 [我的VPS服务部署记录](/posts/2023/01/25/notes-about-deploy-services-in-vps)。

[OpenClaw 安装、配置与使用指南](/posts/2026/03/04/openclaw-install-config-usage-guide) 这篇文章记录了我安装 OpenClaw 的过程。

目前，我使用 OpenClaw 主要做了两件事，一是让它每天早上给我发送每日简报；二是通过电报机器人发送链接，让机器人保存为书签。

每日简报，机器人回复的内容：

```bash
Good morning, chensoul! ☀️

📅 Thursday, March 5th, 2026 — 6:30 AM (Shanghai)

🌤️ Weather
Unable to fetch current weather (API not configured). Consider checking your preferred weather app.

📋 Today's Focus
No scheduled events or tasks found in memory. This is a fresh start — perfect for setting your own priorities!

💡 Suggestions

• Review your calendar for any meetings today
• Check email for urgent messages
• Consider what 1-3 things you want to accomplish today

🔧 System Status

• Workspace: Running normally
• Last activity: System uptime ~1.5 days

───

Have a productive day! 🦞
```

这个回复比较简单，或许可以做一些更复杂的简报，甚至可以替代 [Github 每日简报代码](https://github.com/zhijunio/chensoul/blob/main/daily_review.py)，完成以下信息的推送。

```markdown
📅 每日简报 | 2026年03月05日，今年第 64 天。武汉天气:  阴 4°C ~ 16°C

███░░░░░░░░░░░░░░░░░ 17.5% (64/365)

📈 今日指数：
• 黄金：1,144.00 元/克
• 比特币：$73,338 USD

🌐 域名状态：
• huaiyu.com 状态: ok 过期时间: 2026-10-18
• chensoul.com 状态: clientTransferProhibited 过期时间: 2026-04-27

⌨️ 编程时间：
• 昨天写代码花了 6 小时 41 分钟
• 使用编辑器：Chrome 47%, Ghostty 22%, IntelliJ IDEA 18%
• 主要语言：Other 63%, Markdown 16%, Java 9%

🏃‍跑步距离：
• 昨天跑了 5.01 公里
• 本月跑了 20.27 公里
• 今年跑了 237.05 公里

💬 每日名言：
强扭的瓜甜不甜不重要，只要能解渴就行了。

📜 每日诗词：
《瑞龙吟·德清清明竞渡》
大溪面。遥望绣羽冲烟，锦梭飞练。桃花三十六陂，鲛宫睡起，娇雷乍转。
去如箭。催趁戏旗游鼓，素澜雪溅。东风冷湿蛟腥，澹阴送昼。轻霏弄晚。
洲上青苹生处，斗春不管，怀沙人远。残日半开一川，花影零乱。山屏醉缬，连棹东西岸。阑干倒、千红妆靥，铅香不断。傍暝疏帘卷。翠涟皱净，笙歌未散。簪柳门归懒。犹自有、玉龙黄昏吹怨。重云暗阁，春霖一片。

—— 宋代·吴文英

⭐️ GitHub Java Trending：
• NationalSecurityAgency /ghidra (https://github.com/NationalSecurityAgency/ghidra)
• OpenAPITools /openapi-generator (https://github.com/OpenAPITools/openapi-generator)
• elastic /elasticsearch (https://github.com/elastic/elasticsearch)
• FCL-Team /FoldCraftLauncher (https://github.com/FCL-Team/FoldCraftLauncher)
• apache /iceberg (https://github.com/apache/iceberg)

📰 OSChina 最新资讯：
• GPT-5.4 意外泄露：200 万上下文窗口与持久状态化特性引关注 (https://www.oschina.net/news/407648)
• 时序数据库 Apache IoTDB V2.0.7/V1.3.7 发布 (https://my.oschina.net/u/9120954/blog/19208910)
• OpenAI 与美国国防部达成合作后导致 ChatGPT 卸载量飙升 (https://www.oschina.net/news/407604)
• Pale Moon 34.1.0 发布，苍月浏览器 (https://www.oschina.net/news/407603/pale-moon-34-1-0-released)
• OpenResty 1.29.2.1 正式发布 (https://www.oschina.net/news/407583/openresty-1-29-2-1-released)
```

让机器人保存链接为书签，这里使用 Linkding 这个技能。对应的渠道是使用到电报。配置方法请参考 [OpenClaw 安装、配置与使用指南](/posts/2026/03/04/openclaw-install-config-usage-guide) 这篇文章。

使用 OpenClaw 几天后的感受是，OpenClaw 的兴起，会让很多 APP 没有存在的必要。因为通过 Skills 可以实现很多的 APP 能实现的技能，甚至很多 SASS 软件的存在也不重要了。

因为有了 OpenClaw，我卸载了 Linkding IOS 端的 APP，现在想保存书签，只需要将链接发送给电报机器人即可。如果 OpenClaw 可以每天给我推送我订阅的 RSS 信息，那手机上的 Folo APP 也可以删除了。没有了 RSS APP，可以参考 [游钓四方](https://blog.lhasa.icu/) 的 [订阅](https://blog.lhasa.icu/feeds) 页面在我的博客添加一个 RSS 订阅页面。

## 本周分享

我使用 [Linkding](https://linkding.zhijun.io/) 书签来保存我认为不错的资源，包括文章、视频等等。虽然大部分有意思的输入都会自动同步到「[ChenSoul Share](https://t.me/s/zhijun_share)」Telegram 频道，但我还是想在这里额外挑一部分出来。单独列出来之后，这篇周报就更像一份 newsletter 了。

### 文章

- [不会写代码也能开发小程序！手把手教你用Cursor+Coze创造属于自己的AI应用](https://mp.weixin.qq.com/s/do2tehX0BUfEzjlEOLT5cA)

- [OpenClaw进阶指南！云部署vs本地部署？一篇讲明白](https://mp.weixin.qq.com/s/6F8YIRJ26rWr4Rke59ElPQ)
- [Dokie：用AI Native的方式做PPT](https://mp.weixin.qq.com/s/ZjTpgOtPy_zU9g-t3hyPmQ)
- [Ai MCP 网关，从 HTTP 到 MCP，轻松协议转换！](https://mp.weixin.qq.com/s/X_Moq4AmfJOwWmeYgwn0kA)
- [一个疯子，造出便宜100倍的AI芯片](https://mp.weixin.qq.com/s/Wk398xin03hrgYav55yw_g)
- [AI编程实践：从Claude Code实践到团队协作的优化思考｜得物技术 ](https://mp.weixin.qq.com/s/GjPUDjjx2XmZX-G5qDC6eA)
- [（Java 版 Claude Code）编码智能体 SolonCode v0.0.14 发布 ](https://mp.weixin.qq.com/s/tNFCHTAs9KGgYF34YeTHbQ)
- [深度拆解Lynx AI：一个基于Spring Boot 3 + LangChain4j的全栈AI平台](https://mp.weixin.qq.com/s/mHdneX_yW9YwsL4lIk-3dQ)

- [免费的 Navicat 替代产品，一款现代化、轻量级、高性能的数据库管理工具！](https://mp.weixin.qq.com/s/ds0hWY7miw9eM46sHbkG-w)
- [如何用 AI 做业务级 Code Review](https://mp.weixin.qq.com/s/dgR34fSjHP2Zf26g7YzMkA)

### 工具

- [https://likec4.dev/](https://likec4.dev/)

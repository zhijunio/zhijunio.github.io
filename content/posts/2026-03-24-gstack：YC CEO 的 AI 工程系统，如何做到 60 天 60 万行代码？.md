---
title: "gstack 拆解：YC CEO 的 AI 工程系统与 60 天 60 万行代码"
date: 2026-03-24 14:40:00+08:00
slug: gstack-skill
tags: [ "ai" ]
draft: false
description: "gstack：Garry Tan（Y Combinator CEO）为 Claude Code 开源的技能系统，用 Slash Command 串联 office-hours、review、qa、ship 等全流程。本文拆解两层架构与 Sprint 工作流、安装与使用要点，便于评估是否适合你的 AI 工程习惯。"
---

> "I don"t think I"ve typed like a line of code probably since December, basically." — Andrej Karpathy，2026 年 3 月

Karpathy 说他很久没敲代码了。

但另一个人，用 AI 每天写 1-2 万行代码。

![gstack：Garry Tan 面向 Claude Code 的 AI 工程技能系统（封面）](01.webp)

这个人是 Garry Tan，Y Combinator 的总裁兼 CEO。

他用的系统叫 gstack。

**60 天 60 多万行生产代码**——每天 1-2 万行，还是在他全职运营 YC 的情况下。

这不是 Copilot 那种"辅助编程"。

这是一个**虚拟工程团队**：CEO 帮你重新思考产品，工程经理锁定架构，设计师检查 AI 生成的垃圾代码，QA 负责人打开真实浏览器测试，安全官跑 OWASP 审计，发布工程师自动部署。

20 多个专家。全部是 Slash Command。全部免费。MIT 开源。

这篇文章拆解 gstack 的核心架构、工作流设计，以及它为什么能实现 10 倍效率。

---

## gstack 是什么？

用 Garry Tan 的话说：

> "gstack is my answer."

他做了 20 年产品。从 Palantir 早期工程师，到 Posterous（卖给 Twitter），再到 YC 总裁。

现在他写的代码，比任何时候都多。

**2026 年前 3 个月，1237 次 GitHub contributions。**

作为对比，2013 年他在 YC 做 Bookface 时，全年 772 次。

同一个人。不同时代。

差别是工具。

gstack 不是一个新的编程语言，不是一个 IDE 插件，不是一个 SaaS 服务。

它是**一套运行在 Claude Code 之上的技能系统**，把单一 AI 助手变成专业化分工的工程团队。

核心设计哲学很简单：**流程（Process）**

---

## 核心架构：两层判断机制

gstack 的架构可以用一个矩阵表示：

**横向**：工作流阶段（Think → Plan → Build → Review → Test → Ship → Reflect）

**纵向**：
- **20+ 专业角色**：office-hours、plan-ceo、review、qa、ship、retro 等
- **8 个效率工具**：browse、codex、careful、freeze、guard 等

![核心架构：两层判断机制](02.webp)

### 第一层：20+ 专业角色

每个角色是一个 Slash Command，有明确的职责边界：

| 技能 | 角色定位 | 核心功能 |
|------|---------|---------|
| `/office-hours` | YC Office Hours | 用 6 个强迫性问题重新定义你的产品需求 |
| `/plan-ceo-review` | CEO/创始人 | 重新思考问题，找到 10 星产品 |
| `/plan-eng-review` | 工程经理 | 锁定架构、数据流、边界情况、测试计划 |
| `/plan-design-review` | 资深设计师 | 每个维度 0-10 分打分，检测 AI 垃圾设计 |
| `/review` | 资深工程师 | 找出那些通过 CI 但在生产环境爆炸的 bug |
| `/investigate` | 调试专家 | 系统性根因分析，Iron Law：不调查不修复 |
| `/qa` | QA 负责人 | 打开真实浏览器测试，自动修复 + 回归测试 |
| `/cso` | 安全官 | OWASP Top 10 + STRIDE 威胁建模 |
| `/ship` | 发布工程师 | 同步 main、跑测试、审计覆盖率、推 PR |
| `/land-and-deploy` | 发布工程师 | 合并 PR、等 CI、部署、验证生产健康 |
| `/canary` | SRE | 部署后监控循环 |
| `/retro` | 工程经理 | 团队感知的需求回顾，跨项目统计 |

### 第二层：8 个效率工具

| 工具 | 功能 |
|------|------|
| `/browse` | 真实 Chromium 浏览器，真实点击，真实截图 |
| `/codex` | OpenAI Codex 的二次意见，三种模式 |
| `/careful` | 危险操作警告（rm -rf, DROP TABLE, force-push） |
| `/freeze` | 编辑锁定，只允许修改指定目录 |
| `/guard` | `/careful` + `/freeze` 一键开启 |
| `/unfreeze` | 解除编辑锁定 |
| `/setup-deploy` | 部署配置一键设置 |
| `/gstack-upgrade` | 自动升级到最新版本 |

---

## Sprint 工作流

Think → Plan → Build → Review → Test → Ship → Reflect

gstack 不是工具的简单堆砌。

它是一个**流程**。每个环节的输出，自动成为下一个环节的输入。

### 完整示例：从想法到部署

```
You:    I want to build a daily briefing app for my calendar.
You:    /office-hours
Claude: [询问痛点 — 要具体例子，不要假设]

You:    多个 Google 日历，活动信息过时，地点错误。
        准备工作花很长时间，结果还不够好...

Claude: 我要挑战你的框架。你说"daily briefing app"，
        但你实际描述的是个人首席 AI 助理。
        [提取 5 个你没意识到的能力]
        [挑战 4 个前提 — 你同意/不同意/调整]
        [生成 3 种实现方案，带工作量评估]
        建议：明天先 Ship 最窄的楔形产品，从真实使用学习。
        完整愿景是 3 个月项目 — 从真正可用的每日简报开始。
        [写设计文档 → 自动流入下游技能]

You:    /plan-ceo-review
        [阅读设计文档，挑战范围，跑 10 部分审查]

You:    /plan-eng-review
        [数据流 ASCII 图、状态机、错误路径]
        [测试矩阵、失败模式、安全考虑]

You:    批准计划。退出计划模式。
        [写 2400 行代码，11 个文件，约 8 分钟]

You:    /review
        [自动修复] 2 个问题。[询问] 竞态条件 → 你批准修复。

You:    /qa https://staging.myapp.com
        [打开真实浏览器，点击流程，发现并修复 bug]

You:    /ship
        测试：42 → 51 (+9 新增)。PR: github.com/you/app/pull/42
```

你说"每日简报应用"。AI 说"你在构建首席 AI 助理"——因为它听的是你的痛点，不是你的功能请求。

**8 条命令，端到端完成。** 这不是 Copilot，这是一个团队。

![Sprint 工作流](03.webp)

---

## 关键技能深度拆解

### /office-hours：YC 式产品咨询

这不是"帮我写个日历应用"的简单请求。

`/office-hours` 会问 6 个强迫性问题：
1. 你遇到的具体问题是什么？（不是假设的痛点）
2. 你现在怎么解决？为什么不够好？
3. 谁会为这个付钱？为什么？
4. 如果只能做一个功能，是什么？
5. 你怎么知道成功了？（具体指标）
6. 如果明天必须上线，你会上线什么？

然后它会：
- **挑战你的框架**（你说 A，但实际描述的是 B）
- **生成替代方案**（3 种实现路径，带工作量）
- **写设计文档**（自动流入下游技能）

这是 YC 的工作方式：不听你要什么，听你痛什么。

### /review：找那些通过 CI 但生产爆炸的 bug

Garry Tan 对 `/review` 的定位很明确：

> "Find the bugs that pass CI but blow up in production."

它不做风格检查，不跑 linter。它找的是：
- 竞态条件
- 资源泄漏
- 边界情况处理缺失
- 错误处理不完整
- 安全漏洞

找到后，它会自动修复简单的问题。复杂的会标记为 `[ASK]`，等你批准。

### /qa：真实浏览器测试

这不是截图对比。`/qa` 会：
1. 打开真实 Chromium 浏览器
2. 按照测试计划点击流程
3. 记录控制台错误
4. 发现 bug 后自动修复（原子 commit）
5. 为每个修复生成回归测试
6. 重新验证

用 Garry 的话："AI 生成的代码，必须在真实浏览器里跑过才算数。"

### /cso：零噪声安全审计

OWASP Top 10 + STRIDE 威胁建模。

关键设计：**17 种误报排除规则，8/10+ 置信度门槛，独立发现验证。**

每个发现必须包含具体的利用场景，不是泛泛而谈的"可能存在 XSS"。

![关键技能深度拆解](04.webp)

---

## 为什么 gstack 有效？

### 1. 专业化分工 > 全能助手

Claude 默认是一个"全能助手"。

但全能意味着：
- 没有专业深度
- 容易遗漏细节
- 缺乏流程约束

gstack 把"帮我写代码"拆成 20 多个专业角色。每个角色有：
- 明确的职责边界
- 专业的检查清单
- 固定的输出格式

**流程可预测，协作才高效。**

这是常识。但很少有人把它编码成系统。

### 2. 流程是指南，不是教条

gstack 的 CLAUDE.md 里有一条核心原则：

> "流程是指南，不是教条；核心原则不可妥协。"

什么叫灵活？
- 如果你明确要求跳过某步骤，AI 会执行（但提醒风险）
- 如果任务简单/紧急，AI 可以直接执行
- 如果上下文已包含所需信息，AI 不重复操作

什么叫不可妥协？
- ❌ 绝不编造数据
- ❌ 绝不使用过时信息
- ❌ 绝不省略 Think Aloud
- ❌ 绝不跳过用户确认（重要决策）

### 3. 一切皆 Markdown，一切可追溯

所有输出都是 Markdown：
- 设计文档
- 测试报告
- 审计结果
- 回顾总结

这意味着：
- 可阅读（人能看懂）
- 可搜索（grep 就能找）
- 可追溯（历史版本对比）
- 可组合（一个技能的输出是下一个技能的输入）

### 4. 真实浏览器 > 静态分析

gstack 的 `/browse` 技能是核心基础设施。

为什么重要？

因为 AI 生成的代码经常：
- 在静态分析时没问题
- 在真实浏览器里爆炸

`/browse` 让 AI 能：
- 打开真实页面
- 点击按钮
- 填写表单
- 截图验证
- 抓控制台错误

**~100ms 一条命令。比人手工测试快 10 倍。**

这才是我说的"虚拟团队"——不是聊天，是干活。

---

## 如何开始使用？

### 30 秒安装

打开 Claude Code，粘贴这段：

```
Install gstack: run git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

然后：
1. 克隆完成
2. 运行 `./setup`
3. 自动添加到 CLAUDE.md

### 添加到项目（可选）

如果你想让队友也用：

```
cp -Rf ~/.claude/skills/gstack .claude/skills/gstack && cd .claude/skills/gstack && ./setup
```

提交 `.claude/skills/gstack` 到仓库。队友 `git clone` 后自动拥有。

### 第一条命令

```
/office-hours
```

告诉它你想构建什么。然后听它挑战你的框架。

---

## AI 编程的未来：一人公司时代

Karpathy 说他已经很久没敲代码了。

Garry Tan 说他用 gstack 每天写 1-2 万行代码。

看起来矛盾。其实说的是同一件事：

**AI 改变了"写代码"的定义。**

以前：
- 写代码 = 敲键盘
- 效率 = 手速 + 语法熟练度
- 团队 = 人多力量大

现在：
- 写代码 = 定义问题 + 审查输出
- 效率 = 提问质量 + 判断力
- 团队 = AI 专家矩阵

gstack 代表的不是"更好的编程工具"。

它代表的是**新的工程范式**：

**一个人 + 一套系统 = 一个团队**

这不是未来。这是现在。

关键是：你准备好接受这个范式的转变了吗？

![一人公司时代](05.webp)

---

## 资源

- **gstack GitHub**: https://github.com/garrytan/gstack
- **技能详解**: `docs/skills.md`
- **架构文档**: `ARCHITECTURE.md`
- **贡献指南**: `CONTRIBUTING.md`

---

最后

AI 不是替代你思考，是放大你的判断力。

Garry Tan 的 20+ 技能，本质是把"好的工程实践"编码成可重复的流程。

你用不用 gstack 不重要。

重要的是：你有没有一套系统，让 AI 的输出可预测、可追溯、可组合？

如果没有，现在可以开始了。

从 `/office-hours` 开始。

告诉 AI 你想构建什么。

然后听它挑战你的框架。

---

*全文完*

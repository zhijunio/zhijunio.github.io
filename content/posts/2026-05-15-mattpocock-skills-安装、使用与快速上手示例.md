---
title: "mattpocock/skills 安装与使用：让 AI 助手会干活"
date: 2026-05-15 16:50:00+08:00
slug: mattpocock-skills-guide
categories: [ "tech" ]
tags: [ "ai", "agent-skill" ]
draft: false
description: "介绍 mattpocock/skills 的安装方式、常用技能和一个可直接照着做的快速上手示例，帮助你把 AI 编程助手从“会聊天”变成“会干活”。"
---

![mattpocock-skills](01.webp)

如果你已经在用 Claude Code、Codex 或其他支持 Skills 的 AI 编程助手，`mattpocock/skills` 是一个很值得试的仓库。

它不是那种“给模型塞一大坨 prompt”的做法，而是把常见工程实践拆成一组小而明确的技能：先澄清需求，再设计，再 TDD，再诊断，再收尾。目标很直接：少一点 vibe coding，多一点真正能落地的工程流程。

<!--more-->

## 一、它是什么

[`mattpocock/skills`](https://github.com/mattpocock/skills) 是 Matt Pocock 维护的一组 AI Agent Skills，作者把自己日常会用到的工程工作流整理成了一组可复用技能。

它的几个特点很明确：

- **小而可组合**：不是一个大而全的“方法论框架”，而是一组独立技能
- **面向工程实践**：重点放在需求澄清、TDD、调试、架构收敛这些真实开发场景
- **适配多种模型和工具**：仓库主页明确写了，它们可以和不同模型一起工作
- **强调流程**：比起让模型“自己发挥”，它更像是在给模型装一套默认工作纪律

仓库主页里最常被提到的几个技能包括：

- `grill-me`：先把需求问清楚
- `grill-with-docs`：在需求澄清时顺便建立项目语言和文档
- `tdd`：红绿重构
- `diagnose`：系统化排查问题
- `to-prd`：把上下文整理成 PRD
- `zoom-out`：先看全局，再看局部
- `improve-codebase-architecture`：收敛“面条化”代码库
- `setup-matt-pocock-skills`：给当前仓库做一次基础配置

## 二、怎么安装

官方给的快速安装方式很简单。

### 1. 安装整个技能仓库

```bash
npx skills@latest add mattpocock/skills
```

执行后，工具会让你选择：

- 要安装哪些 skills
- 要装到哪个 coding agent

这里有个关键点：**一定要把 `/setup-matt-pocock-skills` 一起选上**。后面很多工程类技能都依赖它先把仓库级配置补齐。

### 2. 关于 Codex / OpenCode / Cursor

在 Codex / OpenCode / Cursor 中，mattpocock/skills 不走 `npx skills@latest add` 的一键安装流程，而是把需要的 SKILL.md 复制到对应工具的 skills 目录中，然后重启工具生效。

可以通过提示词让他们自己安装：
```text
安装技能 https://github.com/mattpocock/skills 到 codex 中
```

### 3. 在你的 agent 里跑初始化技能

安装完以后，在对应 agent 里执行：

```text
/setup-matt-pocock-skills
```

它会继续问你几个基础问题：

- 你想用哪个 issue tracker，GitHub、Linear 还是本地文件
- 你在 triage 时会给 issue 打什么标签
- 你希望生成的文档存放在哪里

这一步的价值不在“问得多”，而在于把仓库的工作方式固定下来。后面像 `to-issues`、`triage`、`diagnose` 之类的技能，都会直接吃这些约定。

### 4. 单独安装某一个技能

如果你不想一次装全套，也可以只装某一个技能：

```bash
npx skills@latest add mattpocock/skills/tdd
npx skills@latest add mattpocock/skills/diagnose
```

适合先从最有感的两个技能开始，别一口气把全部流程都塞进去。

## 三、怎么使用

我对这套技能的理解很简单：它不是替你写代码，而是替你**控制代码是怎么被写出来的**。

### `grill-me`

当你只有一个模糊想法时，先别急着让模型开写。

直接让它问你问题，先把这些东西定下来：

- 目标是什么
- 边界是什么
- 哪些场景必须支持
- 哪些场景可以先不做
- 成功标准是什么

这个技能适合需求还不清楚、但你又想快速推进的时候。

### `grill-with-docs`

它和 `grill-me` 类似，但会更强调项目文档、领域语言和决策记录。

适合已经有一定代码量的项目。因为这时候最大的问题通常不是“不会写”，而是“写出来但和现有项目语言不一致”。

### `tdd`

这是最容易立刻见效的技能之一。

它会把工作流拉回到：

1. 先写失败测试
2. 再写最小实现
3. 让测试通过
4. 再重构

如果你经常遇到“代码看起来写完了，但一跑就炸”，这个技能会很有帮助。

### `diagnose`

适合线上 bug、回归问题、性能退化。

它强调的是一套固定排查顺序：

- 复现
- 缩小范围
- 提出假设
- 加验证
- 修复
- 回归测试

它的核心不是“快”，而是“别拍脑袋改代码”。

### `setup-matt-pocock-skills`

这个技能虽然不像 `tdd` 那么显眼，但它是地基。

它把 issue tracker、标签、文档存储位置这些仓库级约定一次性补好。没有它，后面的流程技能很容易变成“看起来能用，实际上上下文不统一”。

## 四、快速上手示例

下面用一个最小的 `todo` 项目来演示怎么落地。

### 场景

你想让 AI 帮你做一个最基础的待办应用，要求很简单：

- 可以新增任务
- 可以标记完成
- 可以过滤“全部 / 未完成 / 已完成”

### 第一步：先装最常用的三个技能

```bash
npx skills@latest add mattpocock/skills/grill-me
npx skills@latest add mattpocock/skills/tdd
npx skills@latest add mattpocock/skills/diagnose
```

### 第二步：先澄清需求

在 agent 里先跑：

```text
/grill-me
```

然后把你的目标直接说清楚：

```text
我要做一个 todo 应用，先实现新增、完成、过滤三个能力。
请先问我实现前必须确认的问题，不要直接写代码。
```

这一步通常会逼着你把一些默认没想清楚的东西补上，比如：

- 这个 todo 应用的数据要不要持久化？
- todo 列表的状态来源要不要单一化？
- 完成态要怎么存？
- 过滤要支持哪些视图？
- 新增 todo 的输入方式要怎么做？
- 这个 todo 应用要做成什么运行形态？
- 是否需要支持初始示例数据？
- 新增内容要不要做空白处理？
- 要不要支持删除和编辑？
- 过滤条件要不要也持久化？
- 列表排序要按什么规则？
- 每条 todo 的唯一标识怎么生成?
- 新增后输入框要不要自动清空并重新聚焦？
- 完成状态切换要不要支持点击整行，还是只点复选框？

在确认了这些问题之后，agent 就开始写代码了。写完代码之后，安装依赖、构建并启动应用。接着，使用 playwright 打开浏览器做测试。

![ todo 页面](02.webp)

测试成功之后，你可以选择：

- 1. CONTEXT.md + docs/adr/ 的最小骨架
- 2. 再做一轮 UI 收紧
- 3. 加基础测试

![测试成功](03.webp)


### 第三步：用 TDD 开发第一条功能

确认完需求后，切到：

```text
/tdd
```

![开写测试](04.webp)

然后让它先做“新增任务”这一条最小链路。

你可以这样引导它：

```text
先写一个失败测试，证明 todo 列表初始为空；
再写一个测试，证明用户可以新增一个任务；
最后再实现完成状态和过滤逻辑。
```

这样做的好处是，AI 不会一开始就把三个功能一起糊出来，后面也更容易逐步验证。

### 第四步：如果出错，再用 diagnose 收敛问题

假设测试没过，或者页面行为和预期不一致，就切到：

```text
/diagnose
```

然后让它按“复现 -> 缩小 -> 假设 -> 修复”的方式处理。

在这个例子里，最常见的情况可能是：

- 状态没有正确更新
- 过滤条件和渲染条件不一致
- 测试断言写得太宽，掩盖了问题

### 一个完整的最小对话

```text
1. /setup-matt-pocock-skills
2. /grill-me
3. /tdd
4. /diagnose
```

如果你只想记住一件事，那就是：**先问清楚，再写测试，再写实现，最后再排查问题**。这套顺序本身就已经能把很多 AI 编程的坑挡在外面。

## 五、我会怎么选

如果你刚开始用这套仓库，我建议不要一次全装。

更稳妥的顺序是：

1. 先装 `setup-matt-pocock-skills`
2. 再装 `grill-me`
3. 接着装 `tdd`
4. 最后按需要加 `diagnose`、`to-prd`、`zoom-out`

这样你能先感受到“流程变稳了”，再决定要不要继续扩展。

## 六、延伸阅读

如果你也在用其他 AI 编程工具，可以顺手看这几篇：

- [Codex CLI 安装、配置、使用与认证指南](/posts/codex-cli-guide/)
- [Claude Code 安装、配置、使用与认证指南](/posts/claude-code-guide/)
- [Agent Skills：给 AI 编程助手装上一套靠谱的工程化工作流](/posts/agent-skills-install-and-usage-guide/)
- [Superpowers：让 AI 编程不再每次都从头开始](/posts/superpowers-discipline-ai-coding/)
- [Spec-Kit 在 Cursor 中的安装和使用指南](/posts/spec-kit-with-cursor/)

## 七、结语

`mattpocock/skills` 的价值，不在于它多神奇，而在于它很务实。

它把很多工程里本来就应该做的事，变成了 AI 也会主动遵守的流程：先对齐需求，后进入实现；先写测试，再改代码；先定位根因，再动手修。

如果你已经受够了“模型很会写，但总是写偏”，这套技能值得试一次。

---
title: "Superpowers：让 AI 编程不再每次都从头开始"
date: 2026-04-28 11:00:00+08:00
slug: superpowers-discipline-ai-coding
categories: [ "tech" ]
tags: [ "sdd","agent-skill","superpowers"]
draft: false
description: "Superpowers 是一个 Agentic Skills 框架，核心理念是 Process over Prompt —— 用流程规范代替 prompt 调优。本文介绍其核心概念、安装方法、工作流，以及与 agent-skills、GSD 的区别和选型建议。"
favicon: "agent.svg"
---

前两篇介绍了 agent-skills 和 GSD。这篇写 Superpowers。

作者 Jesse Vincent（GitHub: `obra`，Perl 社区老兵）观察到一个特别实际的问题：

> 大部分人用 AI 写代码，每次开新对话都要重新写一遍约束。

"先写测试再写代码"、"改完要 review"、"不要一次改太多文件"——你说一遍，AI 听一遍。下次换个对话，又得从头说。约束写得再长，写着写着就忘了。

Superpowers 的做法是：别用 prompt 约束，用流程约束。

把开发步骤固化成 `SKILL.md` 文件。你不需要每次写长长的 prompt，AI 会自动走对应的流程。

## 实际用起来什么样

你在 Claude Code 里说"我想做一个用户登录功能"。装没装 Superpowers，体验完全不一样。

**没装的时候**，AI 直接开始写代码——定义用户模型、写登录接口、写页面。30 秒就出来了，但你可能发现它用错了技术选型，或者漏掉了注册流程。

**装了之后**，AI 不会直接写代码。它会先问你几个问题：

> 用密码登录还是无密码？要不要 OAuth？注册和登录是分开还是同一个流程？

然后提出 2-3 种方案。讨论完，它会把确认的方案写成设计文档，存在 `specs/YYYY-MM-DD-login-design.md`。你确认了，才开始下一步。

拆任务阶段，它会把设计拆成几个 2-5 分钟能做完的原子任务，每个任务包含精确的文件路径、要改什么代码、怎么验证，存在 `plans/YYYY-MM-DD-login-plan.md`。

然后它启动独立的 subagent 执行每个任务。subagent 写完代码后自动触发 review，review 不通过就退回重写。全部通过后，进入收尾阶段——你可以选择 merge、开 PR、保留分支或丢弃。

全程你不需要手动指定"用 brainstorming"、"用 TDD"。告诉它"我想做 X"就行。

## 技能怎么用

Superpowers 有 17 个技能，每个都是 `SKILL.md`。不需要你一个个选，但我还是讲讲每个环节发生了什么，这样你用起来心里有数。

### 动手前：brainstorming

你说一个想法，它不会直接出方案，而是会追问。

比如你说"做个文件上传功能"。它可能会问：单个还是批量？支持哪些格式？大小限制？上传进度怎么显示？失败怎么重试？——这些问题你可能自己都没想清楚。

讨论完后它会写一份设计文档，你 approving 了才能进入下一步。这个门槛的意义在于，你想跳过讨论直接写代码的时候，它会拦住你。

### 写代码：TDD + subagent

TDD 不是建议，是强制的。它会检查你的测试是否真的是先失败再通过的——如果你直接写了一个已经通过的测试，它会退回去让你先写失败用例。没有失败的测试，就不能写生产代码。

然后每个任务由一个独立的 subagent 执行。每个 subagent 有自己的干净上下文，做完就走。每个 subagent 完成编码后走两轮审查：

- **规格审查**——有没有按照设计文档来做
- **质量审查**——代码是否清晰、有没有明显的 bug

不通过就退回重写。好处是每个 subagent 不会像在一个长对话里那样写着写着就忘了前面的约定。坏处是 token 消耗比单一对话高。

### 出问题时：systematic-debugging

出问题的时候用。流程是四步：找根因 → 看模式 → 形成假设 → 实施修复。

比如接口返回 500，它不会直接去改代码，而是先看日志、看堆栈、看错误类型，定位到具体哪一行出问题，再决定怎么修。没有根因调查就不能改代码。

### 写计划：writing-plans / executing-plans

把设计拆成 2-5 分钟的原子任务。每个任务包含精确文件路径、要改什么代码、怎么验证。执行时每完成几个任务停下来等你检查，不是全自动跑完。

### 收尾：review + 验证 + Git

开发完了不能直接说"搞定"。`verification-before-completion` 要求你实际运行验证命令，拿到结果后才能宣布完成。`code-review` 在合并前自动触发审查。审查完代码后，`using-git-worktrees` 自动创建隔离的工作区，`finishing-a-development-branch` 引导你选择 merge、开 PR、保留还是丢弃，然后清理 worktree。

### 其他几个值得知道的

- `dispatching-parallel-agents` — 多个独立任务并发执行，不用排队等
- `writing-skills` — 让你用同样的 `SKILL.md` 格式写自己的技能。比如你希望"每次改 API 要先更新文档"，写成 skill 放进去，以后就自动生效了

## 安装

Claude Code 官方市场（推荐）：

```bash
/plugin install superpowers@claude-plugins-official
```

Superpowers 自有市场：

```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

其他平台：

- Codex CLI — `/plugins` 搜索安装
- Codex App — Sidebar → Plugins → Coding → 点 +
- Cursor — `/add-plugin superpowers`
- OpenCode — `opencode.json` 添加插件配置
- GitHub Copilot CLI — `copilot plugin install superpowers@superpowers-marketplace`
- Gemini CLI — `gemini extensions install https://github.com/obra/superpowers`

中文用户有社区维护的 [superpowers-zh](https://github.com/jnMetaCode/superpowers-zh)，完整汉化加 6 个中国原创技能。

## 和 agent-skills、GSD 怎么选

这三个经常被拿来比较。

agent-skills 是工具箱——`/spec`、`/plan`、`/build`、`/test`，你需要自己决定什么时候用什么。灵活，但需要你主动调用。

Superpowers 不需要你选。说"我想做 X"就行，它自动走 brainstorming → spec → plan → TDD → subagent → review。纪律性强，但如果你习惯自己控制节奏，可能会觉得它有时候管得太多。

GSD 是从项目立项开始管的——里程碑、阶段、需求追踪。适合从零开始做一个有明确边界的大型项目。

三者不冲突，甚至组合用效果更好。比如用 GSD 管大框架，Superpowers 管每个阶段的开发纪律，agent-skills 管零散的工具调用。

## 局限

流程是强推的。7 个阶段不能跳过——"帮我看一段代码"这种小需求用它太重了。

subagent 驱动意味着多个 agent 同时跑，token 消耗比单一对话高。

它的工作流假设你的任务是"构建功能"。如果是线上紧急修 bug，可能只用 systematic-debugging 就够了，不需要走完整流程。不过目前它没有提供"跳过 brainstorming 直接 debug"的快捷方式，这是一个已知的痛点。

## 最后

大部分人调 AI 的方式是不断加长 prompt。"你先写测试再写代码，改完要 review，不要一次改太多文件，注意边界情况，考虑错误处理"——然后每次新对话都要重新写一遍。

Superpowers 证明了另一种思路：把这些约束固化成结构化技能，让 AI 按流程走，比靠 prompt 可靠得多。

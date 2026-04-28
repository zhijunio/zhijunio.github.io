---
title: "Agent Skills：给 AI 编程助手装上一套靠谱的工程化工作流"
date: 2026-04-28 08:19:00+08:00
slug: agent-skills-install-and-usage-guide
categories: [ "tech" ]
tags: [ "sdd","spec","agent-skill" ]
draft: false
description: "AI 会写代码不等于会做工程。本文介绍 agent-skills —— 一套给 AI 编程助手（Claude Code、Cursor、Gemini CLI）使用的工程化工作流，涵盖需求定义、任务拆分、TDD、代码审查、CI/CD 等完整开发流程，附安装指南和实战用法。"
favicon: "agent.svg"
---

AI 编程工具现在已经很普遍了。

Claude Code、Cursor、Copilot、Gemini、OpenCode……写代码、补函数、生成页面、修 bug，基本都能干。

但用了一段时间后，一个问题越来越明显：

> **AI 会写代码，不等于会做工程。**

它不是生成不了代码，而是不按靠谱的软件工程流程做事：一上来就写代码，不先对齐需求；改了一大坨也不拆分；不写测试，修完也没法证明真的修好了；不会主动做 review、安全检查、性能检查；上线前更没有灰度和回滚意识。

这就是为什么我最近在看 **[agent-skills](https://github.com/addyosmani/agent-skills)**。

它的思路不是训练一个更聪明的 AI，而是给 AI 编程助手一套明确的工程化技能和工作流。

下面说说它是什么、怎么装、怎么用。

## 它到底是什么

简单说，agent-skills 是一套给 AI 编程助手用的工程技能包。

不是业务框架，不是运行时库。更像是一份开发流程规范，或者说，一套针对 AI 编程助手的工程 SOP。

它把软件开发拆成几个阶段：Define（想清楚做什么）、Plan（拆任务）、Build（小步实现）、Verify（测试验证）、Review（质量检查）、Ship（上线发布）。

目标不是让 AI 更会补全代码，而是让它少拍脑袋、少跳步骤、少做没有验证的改动——更像是一个有工程纪律的开发伙伴。

## 仓库结构

项目内容大致分四层：

- **Skills（核心技能）** — `skills/` 目录是重点。每个技能有一个 `SKILL.md`，定义使用场景、执行流程、常见偷懒借口、红旗警告和验证标准。比如 `spec-driven-development`、`test-driven-development`、`debugging-and-error-recovery`、`code-review-and-quality`、`security-and-hardening` 等。
- **Agents（预设角色）** — `agents/` 下是特定视角的辅助角色，比如 `code-reviewer`、`test-engineer`、`security-auditor`，不是主流程。
- **Commands（命令入口）** — Claude Code 里提供了 `/spec`、`/plan`、`/build`、`/test`、`/review`、`/code-simplify`、`/ship` 等 slash command，每个对应一个 skill。
- **Docs（接入说明）** — `docs/` 里写了 Claude Code、Cursor、Gemini CLI、OpenCode、Copilot 等不同工具的接入方式，不是绑定某个工具的。

## 为什么需要它

用过 AI 写代码的人应该都遇到过这些问题：

**写得快但不够稳。** 30 秒出一个页面或接口，但未必考虑过边界情况、回归风险、测试覆盖、安全和可维护性。

**自信地错。** 特别是框架开发时，经常用旧版本 API、搬出过时的最佳实践，逻辑看起来合理但和官方推荐不一致。

**默认没有工程纪律。** 一个成熟工程师会自然遵循的流程——先对齐需求、拆任务、小步提交、用测试证明、合并前 review、上线前做监控和回滚预案——AI 不会这么做，除非你明确约束它。

agent-skills 做的事情，就是把成熟工程师的习惯变成一套 AI 可以遵守的结构化流程。

## 安装指南

所有方式的第一步都是 clone：

```bash
git clone https://github.com/addyosmani/agent-skills.git
```

然后按你用的工具选对应方式。

### Claude Code

更原生的接入方式。

**插件方式：**

```
/plugin marketplace add addyosmani/agent-skills
/plugin install agent-skills@zhijun-agent-skills
```

SSH 报错的话可以配一下 HTTPS：`git config --global url."https://github.com/".insteadOf "git@github.com:"`

**本地开发模式：**

```bash
claude --plugin-dir /path/to/agent-skills
```

装完后可以直接用 `/spec`、`/plan`、`/build`、`/test`、`/review`、`/code-simplify`、`/ship` 这些命令。

### Gemini CLI

Gemini CLI 支持原生 skills，内置了 7 个 slash 命令（注意它用 `/planning` 而非 `/plan`）。

```bash
# 从仓库安装
gemini skills install https://github.com/addyosmani/agent-skills.git --path skills

# 从本地 clone 安装
gemini skills install /path/to/agent-skills/skills/

# 仅当前工作空间
gemini skills install /path/to/agent-skills/skills/ --scope workspace

/skills list  # 检查安装结果
```

也可以把关键的 `SKILL.md` 合并进 `GEMINI.md` 作为长期上下文，但按需加载，别一次性全塞。

### Cursor

Cursor 有三种方式，推荐用 Rules 目录：

```bash
mkdir -p .cursor/rules
cp /path/to/agent-skills/skills/test-driven-development/SKILL.md .cursor/rules/
cp /path/to/agent-skills/skills/code-review-and-quality/SKILL.md .cursor/rules/
cp /path/to/agent-skills/skills/incremental-implementation/SKILL.md .cursor/rules/
```

其他两种方式：把 `SKILL.md` 合并写入 `.cursorrules`，或者在 Settings → Notepads 中创建笔记，聊天中用 `@notepad` 引用。

### OpenCode

OpenCode 不需要插件，通过 `AGENTS.md` + `skills/` 目录实现自动技能路由。clone 仓库后确保工作区里有这两个文件，用自然语言提任务即可，技能根据意图自动激活。

### OpenAI Codex CLI

Codex CLI 使用开放的 `SKILL.md` 标准（和 Claude Code 兼容），支持沙箱执行和 Starlark 命令审批规则。

```bash
# 放到项目级技能目录
cp -r /path/to/agent-skills/skills/* ~/.codex/skills/

# 或者项目本地
cp -r /path/to/agent-skills/skills/* .codex/skills/
```

Codex 采用渐进式上下文加载：启动时只读取 `SKILL.md` 的 YAML frontmatter（name + description），模型决定使用某个技能时才惰性加载完整内容。

还可以通过 `AGENTS.md` 设置项目级规范，通过 `~/.codex/config.toml` 配置沙箱模式和审批策略。

### GitHub Copilot

Copilot 支持 `.github/skills/` 和 `.github/agents/` 目录：

```bash
# 安装技能
mkdir -p .github/skills
cp /path/to/agent-skills/skills/test-driven-development/SKILL.md .github/skills/
cp /path/to/agent-skills/skills/code-review-and-quality/SKILL.md .github/skills/

# 安装 agent 角色（可选）
mkdir -p .github/agents
cp /path/to/agent-skills/agents/code-reviewer.md .github/agents/

# 聊天中用 @code-reviewer Review this PR 调用
```

### Windsurf

Windsurf 把技能合并到 `.windsurfrules` 文件：

```bash
cat /path/to/agent-skills/skills/test-driven-development/SKILL.md > .windsurfrules
echo -e "\n---\n" >> .windsurfrules
cat /path/to/agent-skills/skills/incremental-implementation/SKILL.md >> .windsurfrules
```

### 其他 Agent

技能都是纯 Markdown 文件，任何接受 system prompt 或指令文件的 Agent 都可直接使用——把 `SKILL.md` 内容粘贴到对应的规则文件中即可。

## 核心技能怎么用

装完之后最关键的问题是：技能到底怎么触发？

答案很简单——**技能不是拿来背的，是拿来调用的。** 不用去记 `SKILL.md` 的内容，而是在合适的节点明确告诉 AI 该用哪个。

下面按开发阶段过一遍核心技能。

### 先用对入口：using-agent-skills

这是元技能，负责决定当前该用哪个技能。新开一个任务、不确定该先 spec 还是先 debug 的时候用。告诉它"按 agent-skills 的方式处理这个需求"，它会把任务映射成合适的流程——新功能走 spec-driven-development，有需求但没拆任务走 planning-and-task-breakdown，出现 bug 走 debugging-and-error-recovery，准备合并走 code-review-and-quality。

不想自己手动挑 skill 的话，用这个就够了。

### 想清楚再动手：idea-refine & spec-driven-development

`idea-refine` 适合有一个模糊产品点子的时候。它分三步走：先发散（问关键问题、生出多个方向），再收敛（对比方案的价值和成本），最后输出一页纸的 one-pager，包含问题陈述、推荐方向、关键假设、MVP 范围和明确不做的东西。

`spec-driven-development` 是整套里最核心的技能之一。新项目、新功能、需求不清楚的时候都用它——先写规格，再写代码。Claude Code 里直接 `/spec`。它会产出一个结构化 spec，包含目标、约束、项目结构、代码风格和测试策略。

> 实际用的时候可以这么说：我要做一个博客自动发布工作流。请先按 spec-driven-development 写规格，不要直接写代码，重点写清楚目标用户、输入输出、约束和测试方式。

### 拆任务：planning-and-task-breakdown

spec 有了，但功能太大不知道从哪下手，用这个。`/plan` 就行。

它会把"做一个登录功能"拆成定义用户模型、增加密码校验、实现登录接口、实现登录页面、补充单元测试、补充错误处理这样一串串有依赖关系的 task，而不是只丢给你一句"实现登录"。

### 小步实现：incremental-implementation

多文件改动、容易失控的 feature、refactor 的时候用。`/build`。

它的节奏是：选一个最小单元 → 实现这一小块 → 跑测试验证 → 没问题再继续下一块。避免 AI 一次改十几个文件，最后连自己都不知道哪里坏了。

### 用测试证明：test-driven-development

新逻辑、修 bug、修改已有行为的时候用。`/test`。

流程就是经典的 TDD：写失败测试 → 确认失败 → 写最小实现 → 确认通过 → 必要时重构。修 bug 时特别好使——"这个接口偶发 500，请按 TDD 先写一个复现问题的测试，再修复。"

### 系统化 debug：debugging-and-error-recovery

测试挂了、build 失败、行为异常、线上报错的时候用。

它的思路是：复现 → 定位范围 → 缩小变量 → 修复根因 → 加 guard 避免复发。和 TDD 搭配最好——前者定位，后者把修复固化成回归测试。

### 用好上下文：context-engineering

这个技能很容易被低估。新项目起步、AI 输出质量变差、它不按项目规范写的时候想想它。

它关注的是：哪些规则常驻、哪些按需加载、哪些文档放进上下文、怎么避免上下文污染、怎么让 AI 更稳定地遵守约束。

### 查官方文档再动手：source-driven-development

涉及框架特定写法、不想用过时 API 的时候用。特别是 React、Next.js、Vue、Spring Boot 这类更新快的框架，AI 经常拿旧版本经验来回答。这个技能会强制 AI 先查官方文档再写代码。

### 做产品级 UI：frontend-ui-engineering

做页面、组件、表单、交互的时候用。它关注的不仅是功能实现，还包括响应式布局、错误态/loading 态、WCAG 可访问性、视觉一致性——做的是 production quality 而不是 demo。

### 设计好接口：api-and-interface-design

设计 REST API、GraphQL schema、模块 contract 的时候用。关注参数设计、错误语义、扩展性、稳定性和防误用能力。

### 去浏览器看现场：browser-testing-with-devtools

很多前端问题只看代码看不出来，必须进浏览器看现场——DOM 状态、console 输出、network 请求、真实渲染效果、运行时性能。页面样式不对、按钮没反应、请求异常的时候用。

### 合并前把关：code-review-and-quality

任何改动准备合并前都应该用。`/review`。从 correctness、readability、architecture、security、performance 五个维度检查。AI 生成了一大段代码后也需要用这个验货。

### 保持简单：code-simplification

功能已完成、测试已通过、逻辑确认正确后，再做简化。不改变行为，只做可读性优化——缩短函数、降低嵌套、减少复杂度。不要一边写功能一边大改结构。

### 安全检查：security-and-hardening

涉及用户输入、鉴权、文件上传、外部 API、敏感数据传输存储的时候用。从 OWASP 角度检查输入校验、授权、秘钥管理、最小权限原则。适合在 PR review 和上线前做。

### 先测量再优化：performance-optimization

页面慢、接口慢、Core Web Vitals 不理想的时候用。它的理念是：先测 → 找瓶颈 → 定向优化 → 再复测。不要拍脑袋优化。

### Git 纪律：git-workflow-and-versioning

严格说，任何代码改动都应该用。强调小步提交、原子 commit、commit message 说明 why、小 PR、短生命周期分支。

### CI/CD 自动化：ci-cd-and-automation

新项目上 CI、想加 lint/test/build 检查、调整 pipeline 的时候用。关注测试自动执行、质量门禁前移、部署策略和失败反馈机制。

### 安全下线：deprecation-and-migration

旧接口废弃、系统迁移、清理历史包袱的时候用。考虑迁移窗口、兼容策略、通知机制和风险点。

### 记录决策：documentation-and-adrs

做架构决策、改公共 API、引入新依赖的时候用。产出 ADR、设计记录、决策背景和 trade-off 说明——把"为什么这样做"记下来。

### 上线发布：shipping-and-launch

准备发版、重大功能上线、数据迁移、高风险改动的时候用。`/ship`。检查上线前 checklist、feature flag、灰度方案、监控指标、回滚步骤和成功标准。

## 典型工作流组合

不需要记全部 21 个技能，记住几条常用链路就行：

**做一个新功能：** spec → 拆任务 → 小步实现 → TDD → review → 上线

**修一个 bug：** debug 定位 → TDD 写回归 → review

**做一个新产品点子：** idea-refine → spec → 拆任务（先想清楚值不值得做，再进实现）

**做前端页面：** UI 工程 → 浏览器验证 → 性能优化（做完别只看代码，去真实浏览器里验）

**设计接口：** API 设计 → 核对官方文档 → 记录决策（先定 contract，再按推荐写法实现，最后留痕）

## 推荐起步方式

如果今天就想试，不要一口气全上。先练熟这 3 个：

1. **spec-driven-development** — 解决"AI 一上来就写偏"
2. **test-driven-development** — 解决"写完了但不敢信"
3. **code-review-and-quality** — 解决"能跑但质量不稳"

这三个用稳定了，AI 编程体验就会有明显改善。之后再按需加其他技能。

## 优点和局限

**优点：**

- 提升 AI 产出的下限——少跑偏、少跳步骤、少无测试改动、少无边界感的重构
- 结构清晰、迁移性强——不绑定单一工具，是一个可复用的规则层
- 很适合做团队共识——底层模型可以换，但流程和纪律可以沉淀

**需要留意的地方：**

- 装完不会自动变强——你得正确接入工具、选对技能、在关键时刻明确调用
- 全量加载会很重——所有技能都常驻上下文会导致膨胀、响应变慢、注意力分散。按场景加载，不是一锅端
- 如果用的是自己的 fork，仓库 URL 和安装说明已经是自己的，不需要额外替换

## 最后

AI 编程的关键问题不再是"模型够不够聪明"，而是有没有一套好的工作流约束。

没有工程纪律的强模型照样会制造混乱。一个有 spec 意识、测试意识、review 习惯、上线流程的 AI，即使模型本身没那么强，也更容易成为可靠的开发伙伴。

agent-skills 想做的事情，就是把成熟工程师的工作方式压缩成一套 AI 能遵守的流程。如果已经在用 AI 写代码，值得一试。哪怕只接入其中 3～5 个核心技能，也很可能比单纯换一个更强模型，更能提升真实开发体验。

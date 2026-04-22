---
title: "Claude Code 安装、配置、使用与认证指南"
date: 2026-03-05 20:30:00+08:00
slug: claude-code-guide
draft: false
categories: [ "tech" ]
tags: [ "ai", "claude" ]
favicon: "claude.svg"
description: "全面介绍 Claude Code 的安装、配置、使用与认证方式，并补充订阅方案和通过 OpenRouter 接入的实践路径。"
---

**Claude Code** 是 Anthropic 的 AI 编程助手，可读取代码库、编辑文件、执行命令，并与终端、IDE、桌面端、网页等环境集成。本文介绍其安装、配置、使用、认证与订阅方案，以及通过 **OpenRouter** 接入的使用方式。

<!--more-->

## 一、简介与特点

- **多环境**：终端 CLI、VS Code / Cursor、JetBrains、桌面应用、浏览器 [claude.ai/code](https://claude.ai/code)、Slack、iOS 等
- **Agent 能力**：多文件编辑、执行命令、与 Git 协作（提交、分支、PR）、计划审查后再应用变更
- **CLAUDE.md**：项目根目录或 `.claude/` 下的说明文件，每轮会话会读取，用于约定规范、架构与偏好
- **MCP**：支持 Model Context Protocol，可接 Google Drive、Jira、Slack 等外部数据与工具
- **子 Agent / 自定义命令**：可配置多 Agent 协作、自定义技能（如 `/review-pr`）
- **第三方后端**：终端与 VS Code 支持通过环境变量使用 **OpenRouter** 等第三方 API，绕过地域或订阅限制

## 二、安装

系统要求

- **操作系统**：macOS 13+、Ubuntu 20.04+ / Debian 10+、Windows 10 1809+（建议 WSL）、Alpine 3.19+
- **内存**：建议 4GB+ RAM
- **Windows** 需先安装 [Git for Windows](https://git-scm.com/downloads/win)

### 原生安装

推荐：原生安装（自动后台更新）：

```bash
# macOS / Linux / WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex

# Windows CMD
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

### 手动安装

```bash
# 下载并安装 Homebrew
curl -o- https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh | bash
# 设置国内源
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors4.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors4.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_INSTALL_FROM_API=1

# 下载并安装 Node.js：
brew install node@24

# 验证 Node.js 版本：
node -v # Should print "v24.15.0".

# 验证 npm 版本：
npm -v # Should print "11.12.1".
```
window 系统使用 powershell 下载 Chocolatey，再用 Chocolatey 安装 NodeJs：

```bash
# 下载并安装 Chocolatey：
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"
# 下载并安装 Node.js：
choco install nodejs --version="24.15.0"
# 验证 Node.js 版本：
node -v # Should print "v24.15.0".
# 验证 npm 版本：
npm -v # Should print "11.12.1".
```

设置 npm 镜像 (加速国内下载)：

```bash
npm config set registry https://registry.npmmirror.com
```

再安装 claude-code：

```bash
# npm 全局安装
npm install -g @anthropic-ai/claude-code

# macOS / Linux（Homebrew）
brew install --cask claude-code

# WinGet（需手动升级）
winget install Anthropic.ClaudeCode
```

安装后可运行 **`claude doctor`** 检查环境与安装状态。

## 三、认证方式

### 方式一：Claude 订阅（推荐个人）

- 使用 **Claude Pro** 或 **Max** 订阅，在终端或 App 内执行 **`claude`** 或 **`/login`**，按提示完成 OAuth 登录
- 与网页版 Claude 共享同一订阅额度（每 5 小时滚动窗口）
- 适合日常开发，无需单独管理 API Key

### 方式二：Anthropic Console（API Key）

- 在 [Anthropic Console](https://console.anthropic.com/) 创建 API Key，配置到环境变量或 Claude Code 设置
- 按 [API 定价](https://www.anthropic.com/pricing) 按量计费，不占用订阅额度池
- 适合脚本、CI 或需要固定模型/配额时使用

### 方式三：团队 / 企业

- **Claude for Teams** 或 **Enterprise**：通过 Claude 管理端配置团队账单、SSO、合规等
- **云厂商**：可对接 Amazon Bedrock、Google Vertex AI、Microsoft Foundry 等（需相应配置）

## 四、基本使用

### 交互模式

```bash
# 进入项目目录后启动
cd your-project
claude

# 带初始提示启动
claude "解释这个项目的结构并列出入口文件"

# 继续最近一次对话
claude -c

# 按会话 ID 或名称恢复
claude -r auth-refactor
claude -r ""   # 弹出会话选择器
```

### 非交互模式（管道 / 脚本）

```bash
# 单次提问后退出，输出到 stdout
claude -p "列出 src 下所有 TypeScript 文件并简要说明"

# 管道输入
cat logs.txt | claude -p "总结错误类型"
git diff main --name-only | claude -p "审查这些变更是否有安全风险"

# 输出 JSON 便于脚本解析
claude -p "分析依赖" --output-format json
```

### 常用命令速览

| 命令 | 说明 |
|------|------|
| `claude` | 启动交互会话 |
| `claude doctor` | 运行系统诊断 |
| `claude "query"` | 带初始提示启动 |
| `claude -p "query"` | 单次提问后退出（print 模式） |
| `claude -c` | 继续当前目录最近会话 |
| `claude -r <id\|name>` | 恢复指定会话 |
| `claude auth login` | 登录（可选 `--email`、`--sso`） |
| `claude auth logout` | 登出 |
| `claude auth status` | 查看认证状态 |
| `claude update` | 更新到最新版 |
| `claude mcp` | 配置 MCP 服务器 |
| `claude agents` | 列出已配置子 Agent |
| `claude --teleport` | 将网页端会话拉回本地终端 |
| `claude --remote "任务描述"` | 在 claude.ai 创建云端任务 |

### 常用命令行参数

| 参数 | 说明 |
|------|------|
| `--model sonnet` / `--model opus` | 指定模型别名或完整模型名 |
| `--add-dir ../lib` | 额外可访问目录 |
| `--permission-mode plan` | 以「计划模式」启动，先规划再执行 |
| `--tools "Bash,Edit,Read"` | 限制可用工具 |
| `--append-system-prompt "规则"` | 在默认系统提示后追加说明 |
| `--chrome` | 直接将 Claude 连接到你的浏览器 |
| `--dangerously-skip-permissions` | 跳过权限确认模式 |

交互界面内输入 **`/help`** 可查看斜杠命令，**`/config`** 打开设置界面。

### 命令

只需输入 / 就能看到所有命令。以下是关键的几个：

  - /model - 在 Claude 模型之间切换（Sonnet 快，Opus 聪明）
  - /context - 查看 Claude 知道哪些文件
  - /clear - 重新开始对话
  - /compact - 压缩对话以节省上下文
  - /usage - 查看使用了多少
  - /resume - 继续上一次会话的进度
  - /btw - 

## 五、配置

### 配置作用域

| 作用域 | 路径 | 说明 |
|--------|------|------|
| **User** | `~/.claude/settings.json` | 当前用户全局，不随项目共享 |
| **Project** | `.claude/settings.json` | 项目内共享，可提交到 Git |
| **Local** | `.claude/settings.local.json` | 仅本机，通常不提交（gitignore） |
| **Managed** | 系统/策略/服务器下发 | 企业统一策略，不可被覆盖 |

优先级：User < Project < Local < 命令行 < Managed。

### 配置文件示例（节选）

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run *)", "Read(~/.zshrc)"],
    "deny": ["Read(./.env)", "Read(./secrets/**)"]
  }
}
```

- **permissions**：控制允许/拒绝的工具与路径（如 Bash 命令、Read 路径）
- 其他常见项：模型偏好、MCP、插件、hooks 等，详见 [Settings 文档](https://docs.anthropic.com/en/docs/claude-code/settings)

MCP 服务器可在 **User** 的 `~/.claude.json` 或 **Project** 的 `.mcp.json` 中配置；交互内通过 **`/config`** 也可查看与修改部分设置。

### CLAUDE.md

在项目根或 `.claude/` 下放置 **CLAUDE.md**（或 **CLAUDE.local.md** 仅本机），用于编写项目规范、构建命令、架构说明等，Claude Code 每次会话会读取。

## 六、订阅方案与价格（参考）

价格与额度以 [Claude 定价页](https://claude.com/pricing) 为准，下表为常见参考：

| 方案 | 价格（约） | 每 5 小时消息（约） | 说明 |
|------|------------|---------------------|------|
| **Free** | \$0 | 有限 | 有限体验 Claude Code，与网页版共享额度 |
| **Pro** | **\$20/月**（年付约 \$17/月） | 约 45 条 | 含 Claude Code；IDE 中**仅 Sonnet**，不可用 Opus |
| **Max 5x** | **\$100/月** | 约 225 条 | 约 5 倍 Pro 用量；**所有环境可用 Opus** |
| **Max 20x** | **\$200/月** | 约 900 条 | 约 20 倍 Pro 用量；最高优先级 |
| **Teams / Enterprise** | 联系销售 | 按合约 | 团队协作、SSO、合规、托管策略等 |

- **5 小时滚动窗口**：从第一条消息起算，5 小时后额度重置，非自然日/月
- **网页 Claude 与 Claude Code** 共享同一额度池
- Pro 在 IDE 插件中只能用 Sonnet；若需在 IDE 中使用 Opus，需 **Max**

## 七、使用 OpenRouter 接入

通过设置环境变量，可将 Claude Code 的请求转发到 **OpenRouter**，使用 OpenRouter 的 API Key 与模型（如 Claude、GPT、Gemini 等），常用于绕过地域限制或统一走 OpenRouter 计费与路由。

### 1. 获取 OpenRouter API Key

在 [OpenRouter Keys](https://openrouter.ai/keys) 注册并创建 API Key（形如 `sk-or-v1-...`）。

### 2. 设置环境变量

设置 `~/.claude/settings.json` 文件，使用 OpenRouter 模型提供商。

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-or-v1-xxxxxx",
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "anthropic/claude-haiku-4.5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "anthropic/claude-opus-4.6",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "anthropic/claude-sonnet-4.6",
    "ANTHROPIC_MODEL": "anthropic/claude-sonnet-4.6"
  },
  "includeCoAuthoredBy": false
}
```

也可以使用 [cc-switch](https://github.com/farion1231/cc-switch) 的图形化界面进行设置。

### 3. 启动与验证

```bash
claude
```

若此前已用 Anthropic 账号登录，建议先执行 **`/logout`** 或 **`claude auth logout`** 清除本地凭据，再重新运行 `claude`。在会话内输入 **`/status`** 可查看当前 API 地址与模型信息；也可在 OpenRouter 后台的 Activity 中确认是否有请求。

## 八、使用技巧

### Agents

 什么是 Agents？ 并行处理——同时处理许多相似任务，而不是一个一个地做。

  使用 agents 当：
  - 你有很多相似的文件
  - 可并行化的任务
  - 跨多个来源的研究

  不要使用 agents 当：
  - 你有一个复杂任务
  - 顺序工作
  - 相互依赖的事情

 比如以下场景适合使用：

  - 10 个你考虑的职位招聘——同时分析所有，比较要求
  - 5 个你评估的供应商——并行研究每个，综合成比较
  - 20 篇你保存的文章——让 agents 总结每篇，然后综合关键洞察
  - 找公寓——8 个房源同时分析优缺点
  - 竞争分析——同时研究 6 个竞争对手
  - 计划旅行——agents 同时研究机票、酒店、活动、餐厅

### 自定义 Sub-agents

1. Agents 和 子 Agents 有什么区别？

把 Agents 想象成临时工。你为某个任务启动它们，然后它们就消失了。子 Agents 是永久团队成员。它们在有持久个性和视角的文件中定义。

当你需要它们时，它们随时可用。当然，你可以随时在进化系统中更新或改进它们。

这就像建立你自己的顾问委员会。一个怀疑论者、一个乐观主义者、一个技术专家、一个客户倡导者——无论你需要什么视角，你都可以创建它们，一次创建 ，永远使用。

2. 子 Agents 如何工作？

子 agents 定义在 .claude/agents/ 目录中。每个文件有：

- YAML frontmatter，包含名称和描述
- 定义它们视角的系统提示词

示例文件：

```markdown
---
name: Agent Name
description: One-line description
---
 
# System prompt
 
You are... [personality and perspective]
```

  你可以为自己需要的任何视角创建自己的子 agents。

3. 创建您自己的子 Agent

创建自己的子 agents 很简单：只需使用 /agents 命令。

你可以让 agent 只为这个项目工作（Project），或者在你电脑上的任何项目中工作（Personal）。claude 会帮你创建 agent。

4. Agents 与子 Agents 的决策

何时使用子 agents vs 常规 agents：

- Agents = 临时工，用于并行任务（处理这 10 个文件）
- 子 Agents = 永久团队成员，有定义的视角（随时可用用于审查/反馈）

agents 是为了数量，子 agents 是为了智慧。需要处理 50 个文档？Agents。需要从不同视角获得深思熟虑的反馈？子 agents。

5. 其他资源

- [Awesome Claude Code Sub-Agents](https://github.com/VoltAgent/awesome-claude-code-subagents) - Community templates
- [Sub-Agent Examples](https://github.com/wshobson/agents) - Real-world configurations
- [SubAgents.cc](https://www.subagents.cc/) - Template generator and browser
- [Official Docs: Sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) - Anthropic documentation

## 九、参考链接

- [Claude Code 概览与安装](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- [Claude Code 设置](https://docs.anthropic.com/en/docs/claude-code/settings)
- [Claude Code CLI 参考](https://docs.anthropic.com/en/docs/claude-code/cli-reference)
- [Claude 定价](https://claude.com/pricing)
- [OpenRouter](https://openrouter.ai/)：多模型统一 API

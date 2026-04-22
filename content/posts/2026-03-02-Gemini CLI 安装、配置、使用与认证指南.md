---
title: "Gemini CLI 安装、配置、使用与认证指南"
date: 2026-03-02 15:00:00+08:00
slug: gemini-cli-guide
categories: [ "tech" ]
tags: [ "ai" ]
favicon: "gemini.svg"
banner: "01.webp"
description: Gemini CLI 是 Google 开源的终端 AI 助手，把 Gemini 的能力直接接到命令行里，让你在终端里对话、写代码、查资料、跑工具。本文介绍其安装、配置、使用、认证方式，以及和订阅方案的关系。
---

**Gemini CLI** 是 Google 开源的终端 AI 助手，把 Gemini 的能力直接接到命令行里，让你在终端里对话、写代码、查资料、跑工具。本文介绍其安装、配置、使用、认证方式，以及和订阅方案的关系。

## 一、简介与特点

- **开源**：Apache 2.0，代码在 [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)
- **终端优先**：面向习惯用命令行的开发者
- **大模型**：支持 **Gemini 2.5 Pro**，约 100 万 token 上下文
- **内置能力**：Google 搜索、读写文件、执行 Shell、抓取网页等
- **可扩展**：支持 **MCP（Model Context Protocol）**，可接 GitHub、Slack、数据库等
- **免费额度**：用 Google 账号登录时，约 60 次/分钟、1000 次/天

## 二、安装

### 系统要求

- **Node.js 20+**
- 支持 **macOS、Linux、Windows**

### 安装方式

macOS / Linux 系统上，先安装 Homebrew，再使用 Homebrew 安装 NodeJs：

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

再安装 gemini-cli：

```bash
# 不安装，直接运行
npx @google/gemini-cli

# 全局安装（npm）
npm install -g @google/gemini-cli

# macOS / Linux（Homebrew）
brew install gemini-cli
```

## 三、认证方式

Gemini CLI 支持三种认证，任选其一即可。

### 方式一：Google 账号登录（推荐个人使用）

- 无需自己管 API Key，在浏览器完成 OAuth 登录即可
- 自动使用最新模型，享受免费额度（约 60 次/分钟、1000 次/天）
- 若使用组织购买的 Code Assist 许可，需设置 Google Cloud 项目

```bash
gemini
# 按提示选择 "Login with Google" 并在浏览器中完成登录

# 使用 Code Assist 许可时可设置项目
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
gemini
```

### 方式二：Gemini API Key

- 适合需要固定模型或付费额度的开发者
- 在 [Google AI Studio](https://aistudio.google.com/apikey) 申请 API Key
- 免费层约 100 次/天（Gemini 2.5 Pro）

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
gemini
```

### 方式三：Vertex AI

- 适合企业或生产环境，与 Google Cloud 集成
- 更高配额、计费账户与合规能力

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
export GOOGLE_GENAI_USE_VERTEXAI=true
gemini
```

## 四、模型介绍

Gemini CLI 默认或可选使用的模型来自 Google Gemini 系列，不同模型在速度、推理能力和上下文长度上有所区别。

### 常用模型概览

| 模型 | 特点 | 典型用途 |
|------|------|----------|
| **gemini-3-pro** | 新一代旗舰推理模型；标准约 100 万、实验版最高约 200 万 token 上下文；深度推理与代码能力更强 | 复杂代码开发、科学研究、长文档深度分析 |
| **gemini-3-flash** | 速度更快、首 token 延迟更低、成本较 Pro 更低；百万级上下文，多模态；性能与效率平衡 | 日常对话、代码补全、文档摘要、实时应用、Agent 工作流 |
| **gemini-2.5-pro** / **gemini-2.5-pro-latest** | 旗舰推理模型，约 100 万 token 上下文；多模态（文本、代码、图片、音视频）；适合复杂推理与代码理解 | 代码分析、架构设计、长文档理解、深度问答 |
| **gemini-2.5-flash** | 响应更快、成本更低；同样支持百万级上下文与多模态 | 日常对话、快速补全、总结、脚本编写 |
| **gemini-2.0-flash** | 稳定版本，特定任务优化，兼容性好 | 对延迟或兼容性有要求的场景 |

使用 Google 账号登录时，CLI 通常默认使用 **Gemini 2.5 Pro** 或更新版本；使用 API Key 或 Vertex 时可在配置或命令行中指定上述任一模型。**Gemini 3** 系列（Pro / Flash）在 API 与 Vertex 可用后，也可通过 `-m` 或 `model.name` 选用。

### 上下文与能力

- **上下文长度**：Gemini 2.5 / 3 系列支持约 **100 万 token** 上下文（Gemini 3 Pro 实验版可达约 **200 万 token**），可承载大量代码或文档，便于「理解整个项目」式的对话。
- **多模态**：支持文本、代码、图片、音频、视频的输入与理解；CLI 中会结合当前目录、文件与工具调用一起作为上下文。
- **工具调用**：模型可调用内置工具（搜索、文件、Shell）以及 MCP 暴露的工具，适合自动化与工作流。

### 在 CLI 中指定模型

- **命令行**：`gemini -m gemini-2.5-flash` 或 `gemini -m gemini-3-flash`（本次会话使用该模型）。
- **配置文件**：在 `~/.gemini/settings.json` 或项目 `.gemini/settings.json` 的 `model.name` 中设置默认模型，例如 `"model": { "name": "gemini-2.5-pro-latest" }` 或 `"model": { "name": "gemini-3-pro" }`。

具体可用模型名和最新列表以 [Gemini API 文档](https://ai.google.dev/gemini-api/docs/models) 或 Vertex AI 模型列表为准；不同认证方式下可用模型可能略有差异。

## 五、基本使用

### 交互模式

```bash
# 在当前目录启动对话
gemini

# 指定要纳入上下文的目录
gemini --include-directories ../lib,../docs

# 指定模型
gemini -m gemini-2.5-flash
```

### 非交互模式（脚本 / 自动化）

```bash
# 单次提问，输出纯文本
gemini -p "解释这个项目的架构"

# 输出 JSON，便于脚本解析
gemini -p "解释这个项目的架构" --output-format json
```

### 常用场景示例

- 在新项目里写代码：`cd my-project && gemini`，然后输入「写一个 Discord 机器人，用 FAQ.md 回答问题」
- 分析已有仓库：克隆后进入目录执行 `gemini`，输入「总结昨天所有的提交变更」

## 六、配置

### 配置层级（优先级从高到低）

1. 命令行参数  
2. 环境变量（含 `.env`）  
3. 系统设置文件  
4. 项目设置文件  
5. 用户设置文件  
6. 系统默认文件  

配置中的字符串可使用环境变量：`"apiKey": "$MY_API_TOKEN"` 或 `"${MY_API_TOKEN}"`。

### 配置文件位置

| 作用域     | 路径                                                                                                                                                                           |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 用户设置   | `~/.gemini/settings.json`                                                                                                                                                    |
| 项目设置   | 项目根目录 `.gemini/settings.json`                                                                                                                                                |
| 系统默认   | macOS: `/Library/Application Support/GeminiCli/system-defaults.json`；Linux: `/etc/gemini-cli/system-defaults.json`；Windows: `C:\ProgramData\gemini-cli\system-defaults.json` |

### settings.json 结构概览

配置按**顶层分类**组织，常用如下：

- **general**：`preferredEditor`、`vimMode`、`checkpointing.enabled` 等  
- **output**：`format`（`"text"` / `"json"`）  
- **ui**：`theme`、`hideBanner`、`hideTips`、`showCitations` 等  
- **model**：`name`（模型名）、`maxSessionTurns`、`summarizeToolOutput` 等  
- **context**：`fileName`（如 GEMINI.md）、`includeDirectories`、`fileFiltering` 等  
- **tools**：`sandbox`、`allowed`（免确认工具）、`exclude` 等  
- **mcp**：`serverCommand`、`allowed`、`excluded`  
- **mcpServers**：各 MCP 服务的连接配置（见下）  
- **privacy**：`usageStatisticsEnabled`  

示例（节选）：

```json
{
  "general": { "vimMode": true, "preferredEditor": "code" },
  "ui": { "theme": "GitHub", "hideBanner": true },
  "model": { "name": "gemini-2.5-pro-latest", "maxSessionTurns": 10 },
  "context": {
    "fileName": ["GEMINI.md"],
    "includeDirectories": ["../lib", "../docs"]
  },
  "tools": {
    "allowed": ["run_shell_command(git)", "run_shell_command(npm test)"]
  },
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
      "trust": true
    }
  }
}
```

### MCP（Model Context Protocol）

MCP 用于把外部服务（GitHub、Slack、数据库等）的能力以「工具」形式暴露给 Gemini CLI。

- **全局控制**（`mcp`）：`mcp.allowed`（白名单）、`mcp.excluded`（黑名单）、`mcp.serverCommand`  
- **单服务配置**（`mcpServers`）：每个服务需至少提供 `command`、`url` 或 `httpUrl` 之一  

常用字段：`command` / `args`、`url` / `httpUrl`、`cwd`、`env`、`timeout`、`trust`、`includeTools` / `excludeTools`。  
配置可放在 `~/.gemini/settings.json`（全局）或项目 `.gemini/settings.json`（仅当前项目）。  
会话中可通过 `@serverAlias 指令` 使用对应工具（如 `@github 列出我的 PR`）。

## 七、与订阅方案的关系

- **消费者订阅**（Google AI Plus / Pro / Ultra）针对的是 **Gemini 网页端与 App** 的用量和功能（如 Deep Think、Veo、更高限额），和 Gemini CLI 的计费**不是同一套**。  
- **Gemini CLI** 的计费取决于你使用的认证方式：  
  - **Google 账号登录**：走 Google AI 的免费配额（如 60 次/分钟、1000 次/天）  
  - **GEMINI_API_KEY**：走 [Gemini API 定价](https://ai.google.dev/gemini-api/docs/pricing) 的免费层或按量付费  
  - **Vertex AI**：走 [Vertex AI 定价](https://docs.cloud.google.com/vertex-ai/generative-ai/pricing)  

因此：若只想在**终端里用 Gemini CLI**，无需购买 Gemini 应用的 Pro/Ultra 订阅；需要更高 API 配额或企业能力时，再考虑 API 付费或 Vertex AI。

## 八、使用 OpenRouter 的替代方案

官方 Gemini CLI 只对接 Google / Vertex 的 Gemini API，**不直接支持 OpenRouter**。若想通过 OpenRouter 使用 Gemini（或其它 200+ 模型），可使用社区版 **Gemini CLI - OpenRouter Edition**：

```bash
npm install -g @chameleon-nexus-tech/gemini-cli-openrouter
```

配置四个环境变量后即可用 OpenRouter 的 API Key 与模型（含 `google/gemini-2.0-flash-001` 等）：

```bash
export AI_ENGINE="openrouter"
export AI_API_KEY="sk-or-v1-你的OpenRouter密钥"
export AI_MODEL="google/gemini-2.0-flash-001"
export GEMINI_API_KEY="openrouter"
gemini
```

详见 [chameleon-nexus/gemini-cli-openrouter](https://github.com/chameleon-nexus/gemini-cli-openrouter)。

## 九、参考链接

- [Gemini CLI 官网与文档](https://google-gemini.github.io/gemini-cli/)  
- [Gemini API 模型列表](https://ai.google.dev/gemini-api/docs/models)  
- [配置说明](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html)  
- [认证设置](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html)  
- [MCP 服务集成](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html)  
- [Gemini API 定价](https://ai.google.dev/gemini-api/docs/pricing)  
- [Gemini 应用用量与订阅说明](https://support.google.com/gemini/answer/16275805?hl=zh-Hans)  

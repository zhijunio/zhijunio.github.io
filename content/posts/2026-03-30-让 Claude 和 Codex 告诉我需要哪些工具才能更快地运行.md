---
title: "Claude Code 与 Codex 自查开发环境：补齐 AI 协作工具链"
date: 2026-03-30 12:50:00+08:00
slug: what-tools-it-needs-for-claude-codex
categories: [ "tech" ]
tags: [ "ai", "tools" ]
draft: false
description: "让 Claude Code 与 Codex 自查本机开发环境：对比二者给出的缺失工具清单，并补齐 ripgrep、fd、fzf 等与 AI 协作相关的 CLI 工具链。"
favicon: "claude.svg"
---

最近看到一篇文章《[Claude Code told me what tools it needs to work faster. Oh boy I was missing so many things.](https://sderosiaux.substack.com/p/claude-code-told-me-what-tools-it)》。作者通过一次让 **Claude Code** 自查环境的实验，整理出 **ripgrep、fd、fzf、DuckDB、git-delta、xh、watchexec、just、semgrep** 等能显著提升 AI 编码助手效率的工具，并指出：**提升效果不只靠改 prompt，还要把 AI 当成需要「趁手 CLI」的协作者。**

出于好奇，我分别向 **Codex** 和 **Claude** 提了同一个问题：

> **为了有效地帮助我解决问题，您还缺少哪些工具？请分析已安装的软件、缺失的软件、损坏的软件和冗余的软件，并按对您帮助我的能力的影响程度排序。**

下面是我的记录与取舍。

## Codex

我向 Codex 提问：

![我向 Codex 提问](01.webp)

它的回答：

![Codex回答](02.webp)

我让 Codex 整理成报告，其中 **缺失项**大致如下。

**P0**

| 工具 | 说明 |
|------|------|
| `gh` | GitHub CLI，影响 PR、issue、release、workflow 等 |
| `psql` | PostgreSQL 客户端，影响连库与 SQL 验证 |
| `gradle` | Gradle 项目构建与依赖检查 |

**P1**

| 工具 | 说明 |
|------|------|
| `redis-cli` / `mysql` | 缓存与关系库排查 |
| `poetry` | Python 若用 Poetry 管理依赖 |
| `deno` | 仅 Deno 项目明显相关 |
| `playwright` | 浏览器自动化脚本通道 |

**我的取舍**：本地开发多用 **Docker** 跑数据库与中间件，因此**不会**在本机装 `psql` / `redis-cli` / `mysql` 等；**Gradle** 不常用，也未装。唯一打算补的是 **`gh`**。按 Codex 的提示，我还删掉了一部分冗余版本软件。

## Claude

我向 Claude 提问：

![我向 Claude 提问](03.webp)

Claude 给出的**最小修复清单**（截图）：

![Claude 给出的最小修复清单](04.webp)

**我的决策**：

- **`gh`、Gradle**：可以安装（Gradle 若项目需要再装）。
- **`kubectl`**：本机不用，可卸。
- **Docker**：编排用 **OrbStack**，不装 Docker Desktop。

按提示执行的大致步骤如下（请按需裁剪；**不要盲目照抄 `brew untap` 等**，除非你清楚含义）：

```bash
echo "=== 1. 安装 Xcode CLI Tools ==="
xcode-select --install

echo "=== 2. 安装缺失的关键工具 ==="
brew install gh

echo "=== 3. 配置语言环境（若使用 Rust）==="
rustup default stable

echo "=== 4. 清理 Homebrew（按需）==="
brew untap homebrew/bundle   # 仅在你确认需要时
brew link certifi
brew link kubernetes-cli
brew cleanup --prune 30

echo "=== 5. 更新包 ==="
brew update && brew upgrade
```

## 补齐「现代 CLI」

参考同一篇英文文章，Claude **一开始没有**主动列出 **ripgrep、fd、fzf、DuckDB、xh、git-delta** 等。我让它对照原文再分析：

![对照原文再分析](05.webp)

之后 Claude 按类别整理了**已安装 / 建议安装 / Shell 集成**，核心表格如下（节选）。

**文件搜索与导航**：`fd`、`ripgrep`、`fzf` —— AI 少在路径和搜索上犯错。

**输出增强**：`bat`、`git-delta`、`eza` —— 读文件、看 diff、列目录更清晰。

**数据处理**：`jq`、`yq`、`duckdb` —— JSON/YAML/轻量 SQL。

**HTTP**：`xh`（以及可选 `httpie`）。

**代码质量**：`semgrep`。

**自动化**：`just`、`watchexec`。

**文本**：`sd`。

**推荐再装**（按需）：`tldr`、`procs`、`bottom`、**Nushell** 等。

### Shell 集成（示例）

**fzf**（若用 Homebrew 安装）：

```bash
# ~/.zshrc
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
# 或执行: /opt/homebrew/opt/fzf/install
```

**just** 的 zsh 补全（不要用 fish 的 `psub` 语法）：

```bash
# ~/.zshrc
eval "$(just --completions zsh)"
```

**eza / bat** 别名可放在 `~/.zshrc` 或统一的 `~/.aliases` 里，与 dotfiles 保持一致即可。

### 项目级示例

**justfile**（我把以前的 go-task 迁到 just，按需保留）：

```just
test:
    cargo test

build:
    cargo build

dev:
    watchexec -e rs,toml cargo run
```

**semgrep** 规则示例仅作演示，实际项目需按语言与框架调整。

### 使用频率（主观）

| 频率 | 工具 |
|------|------|
| 每日 | `fd`、`rg`、`fzf`、`bat`、`jq` |
| 每周 | `xh`、`just`、`duckdb`、`semgrep` |
| 偶尔 | `sd`、`watchexec`、`yq` |

更多用法可参考《[命令行四件套：fd/rg/fzf/bat](https://atbug.com/cli-essentials-fd-rg-fzf-bat/)》。

## dotfiles 与 Brewfile

我有一份 macOS 重装后的初始化配置 **[dotfiles](https://github.com/zhijunio/dotfiles)**（私有仓库时以本地为准），并让 Claude 按**已装软件**对齐 **Brewfile**。

![让 Claude 按已装软件对齐 Brewfile](06.webp)

成文时的结构大致是：**Taps**（如 **`sdkman/tap`**、`tw93/tap`；注意拼写是 **sdk** 不是 sak）→ **命令行 brew**（可先集中一块 **「开发工具」**，如 `gh`、`fnm`、`uv`、`pandoc`；其余如 `fd`、`ripgrep`、`fzf`、`bat`、`just`、`xh` 等）→ **图形 cask**（编辑器、浏览器、OrbStack、Kaku、cc-switch 等）。**完整列表与注释以仓库内最新 `Brewfile` 为准**，避免博文与仓库长期漂移；安装方式：`brew bundle install`。

## 小结

1. **Codex** 更偏「缺什么数据库/构建客户端」，和你在本机是否用容器跑服务强相关；**Claude** 在追问后更能对齐「文章里那套 AI 友好 CLI」。
2. **共同点**：**`gh`** 对 GitHub 工作流帮助大，值得装。
3. **fd / rg / fzf / bat** 这类工具，投入小、和 AI 读仓库、跑命令的习惯契合度高，适合写进 **Brewfile** 长期维护。
4. 自动化脚本里的 **`brew untap`**、**`rustup`** 等，只在你真实需要时执行；**容器编排**用 OrbStack 即可，不必重复装 Docker Desktop。
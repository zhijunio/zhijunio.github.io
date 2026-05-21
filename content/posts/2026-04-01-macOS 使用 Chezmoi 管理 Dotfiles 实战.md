---
title: "macOS 用 Chezmoi 管理 Dotfiles：加密、同步与新机恢复"
date: 2026-04-01 17:00:00+08:00
slug: chezmoi-dotfiles-macos
categories: [ "tech" ]
tags: [ "dotfiles", "macos" ]
draft: false
description: "在 macOS 上用 chezmoi 管理 dotfiles：Git 版本控制、GPG/age 双加密支持、多机器同步，以及新机器恢复完整流程。"
favicon: "chezmoi.svg"
---

> 基于 macOS 14+ (ARM64) 环境，chezmoi v2.70.0+

## 一、为什么选择 Chezmoi

之前尝试过直接 symlink 和 GNU Stow，但都有痛点：

| 方案          | 问题                       |
|-------------|--------------------------|
| 手动 symlink  | 难以追踪变更，多机器同步靠 `rsync`    |
| GNU Stow    | 不支持加密，目录结构受限             |
| **Chezmoi** | Git 版本控制 + GPG/age 加密 + 原子操作 |

Chezmoi 的核心优势：

1. **源码与目标分离**：源码在 `~/.local/share/chezmoi/`，目标在 `~/`
2. **支持加密**：敏感文件用 GPG/age 加密后提交
3. **原子操作**：`chezmoi apply` 一次性应用所有配置
4. **跨机器同步**：配合 Git 仓库，新机器一条命令恢复

## 二、快速开始

### 2.1 安装

```bash
# Homebrew 安装
brew install chezmoi

# 或手动安装
curl -sSfL https://get.chezmoi.io | sh
```

### 2.2 初始化

```bash
# 初始化新仓库（自动打开编辑器创建 Git 仓库）
chezmoi init
```

### 2.3 添加文件

```bash
# 添加普通文件
chezmoi add ~/.zshrc
chezmoi add ~/.gitconfig

# 添加可执行文件（自动设置 executable 前缀）
chezmoi add ~/.zshrc

# 添加目录
chezmoi add --recursive ~/.config/starship
```

### 2.4 编辑文件

```bash
# 编辑后自动应用到目标位置
chezmoi edit ~/.zshrc

# 编辑加密文件（自动解密/加密）
chezmoi edit ~/.wakatime.cfg
```

### 2.5 应用配置

```bash
# 预览变更
chezmoi apply --dry-run --verbose

# 实际应用
chezmoi apply
```

## 三、工作流程

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ 编辑源码文件 │ →   │ chezmoi add  │ →   │ Git 提交推送 │
│  ~/.zshrc   │     │ ~/.zshrc     │     │              │
└─────────────┘     └──────────────┘     └─────────────┘
                                               ↓
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ 应用到目标   │ ←   │ 新机器拉取    │ ←   │  Git 仓库    │
│ chezmoi apply│     │ chezmoi init │     │              │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 四、进阶用法

### 4.1 加密敏感信息

Chezmoi 支持 **GPG** 和 **age** 两种加密方式。推荐使用 **age**（更简单、更快），但如果已有 GPG 密钥也可继续使用。

#### 方案一：使用 age 加密（推荐）

**为什么选择 age：**
- 密钥管理简单：单个文本文件，无需密钥环
- 加密速度快：比 GPG 快 3-5 倍
- 跨平台友好：无需复杂安装
- 更安全：现代化设计，无历史包袱

```bash
# 1. 安装 age
brew install age

# 2. 生成密钥
age-keygen -o ~/.age-key.txt
# 输出：
# # created: 2026-04-01T10:00:00+08:00
# # public key: age1xyz...
# AGEC1...（私钥）

# 3. 配置 chezmoi（将 age1xyz... 替换为你的公钥）
cat > ~/.config/chezmoi/chezmoi.toml <<EOF
encryption = "age"
[age]
recipient = "age1xyz..."
EOF

# 4. 添加加密文件
chezmoi add --encrypt ~/.wakatime.cfg
```

#### 方案二：使用 GPG 加密

```bash
# 1. 生成 GPG 密钥
gpg --full-generate-key

# 2. 查看密钥 ID
gpg --list-secret-keys --keyid-format LONG

# 3. 配置 chezmoi（将 YOUR-KEY-ID 替换为你的密钥 ID）
cat > ~/.config/chezmoi/chezmoi.toml <<EOF
encryption = "gpg"
[gpg]
recipient = "YOUR-KEY-ID"
EOF

# 4. 添加加密文件
chezmoi add --encrypt ~/.wakatime.cfg
```

### 4.2 忽略文件

```bash
# .chezmoiignore
.local/
.cache/
*.log
```

### 4.3 多机器同步

```bash
# 新机器初始化
chezmoi init --apply zhijunio

# 查看状态
chezmoi status

# 拉取最新配置
chezmoi cd && git pull && chezmoi apply
```

### 4.4 在新机器上恢复

```bash
# 1. 安装 chezmoi
brew install chezmoi

# 2. 初始化并应用（自动克隆仓库）
chezmoi init --apply username

# 3. 验证
chezmoi doctor
```

如果有加密文件，需要先导入密钥：

```bash
# GPG
gpg --import ~/backup/gpg-secret-keys.asc

# age（私钥文件格式）
cat ~/backup/age-key.txt >> ~/.age-key.txt
chmod 600 ~/.age-key.txt
```

**密钥备份建议：**
- GPG：`gpg --export-secret-keys > gpg-secret-keys.asc`
- age：直接备份 `~/.age-key.txt` 文件
- 存储到密码管理器或加密 U 盘

## 五、当前配置示例

### 5.1 Sheldon 插件管理器

使用 **Sheldon** 替代 oh-my-zsh 管理 zsh 插件，配置更简洁、加载更快。

**plugins.toml**（`~/.config/sheldon/plugins.toml`）：

```toml
shell = "zsh"

[templates]
source = """{% for file in files %}source "{{ file }}"\n{% endfor %}"""

# zsh-completions - 额外补全定义 (Homebrew)
[plugins.zsh-completions]
inline = '''fpath=(
  "/opt/homebrew/share/zsh-completions"
  "/opt/homebrew/Cellar/zsh/5.9/share/zsh/functions"
  $fpath
)'''

# zsh-syntax-highlighting - 语法高亮 (Homebrew)
[plugins.zsh-syntax-highlighting]
inline = 'source "/opt/homebrew/opt/zsh-syntax-highlighting/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"'

# zsh-autosuggestions - 自动建议 (Homebrew)
[plugins.zsh-autosuggestions]
inline = 'source "/opt/homebrew/opt/zsh-autosuggestions/share/zsh-autosuggestions/zsh-autosuggestions.zsh"'

# Starship 提示符 (Homebrew)
[plugins.starship]
inline = 'eval "$(starship init zsh)"'

# zoxide 目录跳转 (Homebrew)
[plugins.zoxide]
inline = 'eval "$(zoxide init zsh)"'
```

**.zshrc** 只需一行：

```bash
eval "$(command sheldon source)"
```

**优势**：
- 所有插件通过 Homebrew 安装，`brew upgrade` 统一更新
- Lock 文件固定版本，跨机器一致
- 无需 git clone 插件仓库

### 5.2 Ghostty 终端配置

**config**（`~/.config/ghostty/config`）：

```ini
# 窗口设置
window-width = 120
window-height = 40
background-opacity = 0.95

# 字体
font-family = "JetBrainsMono Nerd Font"
font-size = 14

# 链接打开（Cmd+Click）
open-url = true
open-url-modifier = cmd

# 行为
copy-on-select = true
confirm-close-surface = true
```

## 六、常用命令速查

```bash
# ===== 基础操作 =====
chezmoi status              # 查看状态
chezmoi diff                # 查看差异
chezmoi apply               # 应用所有配置
chezmoi apply --dry-run     # 预览变更

# ===== 文件管理 =====
chezmoi add ~/.zshrc        # 添加文件
chezmoi edit ~/.zshrc       # 编辑文件
chezmoi remove ~/.zshrc     # 移除管理

# ===== Git 操作 =====
chezmoi git status          # Git 状态
chezmoi git add .           # Git 添加
chezmoi git commit -m "msg" # Git 提交
chezmoi git push            # Git 推送
chezmoi git pull            # Git 拉取

# ===== 高级操作 =====
chezmoi data                # 查看模板数据
chezmoi doctor              # 诊断问题
chezmoi managed             # 列出管理的文件
chezmoi cd                  # 进入源码目录
```

## 七、参考资料

- [Chezmoi 官方文档](https://www.chezmoi.io/)
- [Chezmoi GitHub](https://github.com/twpayne/chezmoi)
- [我的 Dotfiles 仓库](https://github.com/zhijunio/dotfiles)
- [Awesome Dotfiles](https://github.com/webpro/awesome-dotfiles)

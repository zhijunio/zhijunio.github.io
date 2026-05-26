---
title: "OpenClaw 调用 Claude Code 实战：用 AI Agent 开发 Todo List 应用"
date: 2026-04-08 14:20:00+08:00
slug: create-app-with-claude-code-in-openclaw
tags: [ "openclaw","claude" ]
draft: false
description: "本文介绍在 Codespaces 中从安装到正常使用的完整步骤。"
---

## 使用内置的 coding-agent 技能

openclaw 内置 coding-agent 技能，启用该技能之后，使用 coding-agent 技能让 claude code 做一个 Todo List 的小 web
应用原型。在聊天窗口和机器人对话：

```bash
使用 coding-agent 技能让 claude code 做一个 Todo List 的小 web 应用原型
```

我的 openclaw 是在 root 用户下安装的，如何改为在其他用户，比如 zhijunio 用户权限下运行 openclaw 呢？请参考附录。

## 自建一个带有 Spec 规范的技能

```bash
请深度阅读 Claude Code 官方文档 https://code.claude.com/docs，然后创建一个在 openclaw 可以调用的 skill，以便后续可以轻松调用。
```

稍等一会，openclaw 就完成了开发。

```bash
已搞定。

我基于 Claude Code 官方文档（重点看了：

• docs 首页/overview
• llms.txt 文档索引
• CLI reference
• headless/programmatic runs
• best practices
• skills 文档）

创建了一个可在 OpenClaw 里复用的 skill：

• skill 目录：/home/zhijunio/.openclaw/workspace/skills/claude-code
• 打包文件：/home/zhijunio/.openclaw/workspace/claude-code.skill

还做了这些事：

• 写好了 SKILL.md
• 加了一个可直接调用的包装脚本：
• skills/claude-code/scripts/claude_code_run.py
• 加了官方文档提炼参考：
• skills/claude-code/references/official-docs.md
• skills/claude-code/references/doc-index.md
• 已本地验证通过
• 已打包成功
• 已提交到 workspace git：
• commit: 669448a
• message: feat(skill): add claude-code skill

这个 skill 现在支持的场景

• 让 OpenClaw 调用本机 claude CLI
• headless 一次性执行：claude -p
• Plan Mode 分析
• --allowedTools 自动授权
• --output-format json
• --continue / --resume
• 检测到 /clear、/compact 这类 slash command 时，自动切到 tmux 交互模式

默认使用的 Claude Code 可执行文件

• /home/zhijunio/.nvm/versions/node/v25.8.0/bin/claude

后续你可以这样使唤我

• “用 claude code 分析这个仓库”
• “用 claude code plan mode 看一下这个项目结构”
• “用 claude code 修复测试并运行验证”
• “用 claude code 输出 json 总结”
• “用 claude code 跑交互命令”

如果你要，我下一步可以继续做两件事里的任意一个：

1. 帮你把这个 skill 再优化成更贴合 OpenClaw 聊天触发的版本
比如更容易被“用 Claude Code …”这种中文请求自动命中。
2. 直接实战测试一次
你给我一个目录或任务，我用这个新 skill 跑一遍给你看。
```

把这个 skill 再优化成更贴合 OpenClaw 聊天触发的版本：

```bash
这次我只改了新 skill：

• skills/claude-code/SKILL.md
• 重新打包：/home/zhijunio/.openclaw/workspace/claude-code.skill

这次增强的重点

• 补强了中文触发词
• “用 Claude Code …”
• “用 claude …”
• “用 Anthropic 的 coder …”
• “用 Claude Code 分析/修复/重构/生成计划”
• 增加了聊天式触发说明
• 明确区分了：
• plan mode
• headless
• interactive slash command
• 加了更贴近你使用习惯的中文示例
• 重新验证并打包通过

新的提交

• commit: a491baf
• message: refactor(skill): improve claude-code triggers

你之后如果这样说，我就更容易直接命中这个 skill：

• “用 Claude Code 分析这个仓库”
• “用 Claude Code 修复这个 bug”
• “用 claude 跑 plan mode 看一下”
• “用 Claude Code 输出 JSON”
• “用 Claude Code 跑交互命令”

如果你愿意，下一步我可以继续做一个很实用的小优化：

给这个 skill 再补一个“OpenClaw 专用调用模板”参考文件，把常见任务预设成几种固定 prompt，比如：

• 仓库分析模板
• Bug 修复模板
• 测试修复模板
• 重构模板
• JSON 输出模板

这样以后调用会更稳。
```

给 claude-code skill 补一个 OpenClaw 专用调用模板参考文件，方便后续稳定复用：

```bash
已继续补完。

这次新增了一个 OpenClaw 专用调用模板参考文件：

• skills/claude-code/references/openclaw-prompts.md

里面已经整理了可直接复用的模板，覆盖这些场景：

• 仓库分析
• Bug 修复
• 测试修复
• 重构
• JSON 结构化输出
• 交互式 slash commands
• 继续上一轮会话
• 纯 Plan Mode

同时我也把这个参考文件挂进了 SKILL.md 的 references 里，后续更容易按需读取。

已重新打包成功

• /home/zhijunio/.openclaw/workspace/claude-code.skill

最新提交

• commit: 29a8f44
• message: feat(skill): add openclaw prompts for claude-code

现在这个 claude-code skill 基本已经从“能用”变成“比较顺手可复用”了。

如果你愿意，下一步我可以继续做最后一个很实用的小收尾：

给它加一个简短的中文速查用法块，比如专门列出 5 句你最常说的话，对应会触发什么模式。这样以后你自己看一眼就知道怎么提需求最稳。
```

让 Claude Code 开发一个应用：

```bash
让 Claude Code 开发一个登录页的 UI，用 html+css+js，并且运行给我看看效果。记住，用英文和 Claude Code
```

openclaw 回答：

```bash
我用 Claude Code 开一个独立会话来做这个登录页，并让它把运行方式和预览地址/结果一起给我。

ACP 这边没配好，所以我改用本机已安装的 Claude Code CLI 来做，任务本身还是按你的要求用 英文 交给 Claude Code。

Claude Code 还在跑，我看起来它暂时没有吐出中间输出。我再盯一下，不让它挂着黑箱。
```

过一会，开发完成：

```bash
已经做完了，目前进度是：

• Claude Code 已完成登录页 UI 开发
• 已生成文件：
• login-ui-demo/index.html
• login-ui-demo/styles.css
• login-ui-demo/script.js
• 本地预览已跑起来
• 地址：http://127.0.0.1:8080

这版已经能看效果，不是还在开发中。

如果你这边看不到，我下一步可以直接继续帮你做其中一个：

1. 截图给你看效果描述
2. 改成你想要的风格
3. 帮你把它发布成可外网访问的预览地址
```

把它发布成可外网访问的预览地址（我在服务区上提前配置好了 Cloudflare Tunnel），然后访问可以看到登录页面：

![2026-03-24-create-app-with-claude-code-in-openclaw](01.webp)

为 Claude Code 配置 spec-kit 工作流，然后让 Claude Code 使用 spec-kit 开发一个拟物风格的 Todo List 应用

![2026-03-24-create-app-with-claude-code-in-openclaw-02](02.webp)

确认 openclaw 是否全程让 Claude Code 使用 spec-kit 实现的这个项目：

```bash
你是否全程让 Claude Code 使用 spec-kit 实现的这个项目？
```

```bash
通过 Claude Code 使用 spec-kit，这个完整的步骤和技巧，是否可以存入你之前开发的 Claude Code 的 skill 中？如果可以，那么请实现，并且push 到对应的 github 仓库。
```

根据以上经验和技巧，下面我给你另一个 spec 项目 OpenSpec，你能否为 Claude Code 进行配置，不能成功让 Claude Code 使用
OpenSpec 进行项目开发？

做一个 Todo List 的小 web 应用原型

OpenSpec 的使用经验和技巧，你是否也同步更新到了调用 Claude Code 的 skiil 里面？

请记住，每当你调用 claude-code-openclaw 后，有了新的使用经验和技巧，请同步更新到 skill 并 push 到 github 仓库。同时，还要更新到你的记忆里。

你都学到了哪些经验和技巧。

## 附录

### OpenClaw 改为普通用户执行

以下是将 OpenClaw 从 root 用户迁移到 zhijunio 用户的步骤：

1. 复制 OpenClaw 目录到 zhijunio 用户

```bash
# 复制 workspace 目录
sudo cp -r /root/.openclaw/workspace /home/zhijunio/.openclaw/

# 复制其他 OpenClaw 数据目录
sudo cp -r /root/.openclaw/credentials /home/zhijunio/
sudo cp -r /root/.openclaw/skills /home/zhijunio/
sudo cp -r /root/.openclaw/telegram /home/zhijunio/
sudo cp -r /root/.openclaw/cron /home/zhijunio/
sudo cp /root/.openclaw/openclaw.json /home/zhijunio/.openclaw/

# 设置 ownership
sudo chown -R zhijunio:zhijunio /home/zhijunio/.openclaw/
```

2. 更新技能目录权限

```bash
# 查看 node 版本
node -v

# 注意 node 安装版本 
sudo chown -R zhijunio:zhijunio /root/.nvm/versions/node/v25.8.0/lib/node_modules/openclaw/skills/
```

3. 切换到 zhijunio 用户

```bash
sudo su - zhijunio
```

4. 重新安装或链接 CLI

如果 openclaw 命令不可用，需要在 zhijunio 用户下安装：

```bash
# 在当前用户安装 nvm
export NVM_DIR="$HOME/.nvm"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
source .bashrc

# 安装 Node.js (如果还没安装)
nvm install 25.8.0
nvm use 25.8.0

# 重新安装 openclaw
curl -fsSL --proto "=https" --tlsv1.2 https://openclaw.ai/install.sh | bash
```

5. 更新环境变量

在 /home/zhijunio/.bashrc 中添加：

```bash
export OPENCLAW_WORKSPACE=/home/zhijunio/.openclaw/workspace
```

并使配置生效：

```bash
source /home/zhijunio/.bashrc
```

现在需要更新 openclaw.json 的配置，将 /root/.openclaw 改为 /home/zhijunio/.openclaw

```bash
sed -i "s|/root/\.openclaw|/home/zhijunio/.openclaw|g" /home/zhijunio/.openclaw/openclaw.json
```

6. 复制并更新 crontab

```bash
# 在 root 下导出 crontab
sudo crontab -l > /tmp/root-crontab.txt

# 编辑 crontab 中的路径
# 将 /root/.openclaw 替换为 /home/zhijunio/.openclaw

# 切换到 zhijunio 用户后导入
crontab /tmp/root-crontab.txt
```

7. 停止 root 下的 OpenClaw
8. 卸载 root 下的 OpenClaw（可选）

如果你想完全移除 root 下的 OpenClaw：

```bash
# 卸载 npm 包
npm uninstall -g openclaw

rm -rf /etc/systemd/system/openclaw-gateway.service 
sudo systemctl daemon-reload
```

或者保留 CLI 但只保留公共文化资源。如果你以后需要在 root 下运行某些系统任务，可以只保留 CLI


















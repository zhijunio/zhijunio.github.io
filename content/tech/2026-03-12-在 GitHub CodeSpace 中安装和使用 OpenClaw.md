---
title: "GitHub Codespaces 部署 OpenClaw：云端运行 AI 助手"
date: 2026-03-12 14:50:00+08:00
slug: install-openclaw-in-github-codespace
tags: [ "openclaw","github" ]
description: "本文介绍在 Codespaces 中从安装到正常使用的完整步骤。"
---

本文介绍在 Codespaces 中从安装到正常使用的完整步骤。

## 在Github中创建仓库

首先，在你的 github 账号里创建一个仓库，仓库名字自己随便取，比如 test-openclaw。

创建成功之后，点击 Create a Codespace 按钮。

![install-openclaw-in-github-codespace-01](01.webp)

进入到 codespace 创建页面，点击 Create new codespace 按钮。

![install-openclaw-in-github-codespace-02](02.webp)

## 在 codespace 中安装 openclaw

进入到 codespace ide 页面

![install-openclaw-in-github-codespace-03](03.webp)

在终端输入 openclaw 安装命令：

```bash
curl -fsSL --proto "=https" --tlsv1.2 https://openclaw.ai/install.sh | bash
```

脚本会检测/安装 Node、安装 OpenClaw CLI 并可选进入引导流程。**若只想安装二进制、跳过引导**：

```bash
curl -fsSL --proto "=https" --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

稍等片刻，安装成功之后会进入安装向导。

![install-openclaw-in-github-codespace](04.webp)

选择 Yes，回车进入下一步。选择 QuickStart，继续回车。

![install-openclaw-in-github-codespace](05.webp)

上下移动光标，选择一个模型。我这里选择的是阿里的千问模型。

![install-openclaw-in-github-codespace](06.webp)

按住 cmd 键 + 单击千问授权地址 <https://chat.qwen.ai/authorize?user_code=CFS1OI1Y&client=qwen-code> ，并完成认证。

![install-openclaw-in-github-codespace](07.webp)

选择一个模型，继续回车。

![install-openclaw-in-github-codespace](08.webp)

注意：使用 qwen portal oauth2 登录的方式，可以选择的模型有限，而且还容易限流。如果想使用阿里的bailian Coding Plan，建议手动配置，并且再使用过程中切换模型到 bailian 的模型。

选择一个渠道，这里我选择的是电报。输入提前创建好的机器人 Token。进入 Search provider 配置页面，根据你的实际情况配置搜索引擎。

配置 skills，选择 Yes，回车。

![install-openclaw-in-github-codespace](09.webp)

使用 space 按键选择你想安装的 skills，回车。比如，可以安装 blogwatcher 这个skill。

![install-openclaw-in-github-codespace](10.webp)

启用全部 hooks，回车。openclaw 就安装好了。

## 启动 openclaw

Codespaces 内没有 systemd，不能使用 `openclaw gateway start` 这类服务命令，需要直接运行进程。

1. 前台启动（调试用）

```bash
openclaw gateway

#设置端口，输出日志
openclaw gateway --port 18789 --verbose
```

保持终端不关闭，Gateway 会一直运行。

1. 后台启动（日常使用推荐）

```bash
openclaw gateway --port 18789 &
```

或使用 nohup，避免关闭终端后进程退出：

```bash
nohup openclaw gateway --port 18789 > /tmp/openclaw-gateway.log 2>&1 &
```

等待几秒后检查状态：

```bash
openclaw status
```

若显示 “reachable” 及响应时间（如 17ms），说明 Gateway 已就绪。

以下是，在codespace 终端输入 openclaw gateway 启动网关：

![install-openclaw-in-github-codespace](11.webp)

## 和 openclaw 聊天

在电报里打开机器人，输入消息。

![install-openclaw-in-github-codespace](12.webp)

提示需要配对。这时候回到 codespace 页面，点击 + 按钮，打开一个新的终端，输入配对命令：

```bash
openclaw pairing approve telegram DH4Q43VM
```

![install-openclaw-in-github-codespace](13.webp)

配对成功之后，再回到电报和机器人对话。发送消息。机器人会回复。

```bash
你好！👋 我刚上线。我是谁？你又是谁？

看起来这是我们第一次对话。我叫什么名字、是什么样的助手，这些都还没定下来。你想给我取个名字吗？或者你有什么偏好的相处方式？
```

你可以回复机器人叫什么名字、职责是什么等等。

接下来，给机器人发下面送消息，机器人会回复 OpenClaw 的技能列表。

```bash
列出所有已安装和未安装的 skills
```

发送消息，**让机器人记住项目路径**：

```bash
请记住你现在运行在 github codespace 上，你的项目路径是 /workspaces/test-openclaw
```

![install-openclaw-in-github-codespace](14.webp)

接下来，我们需要在当前项目路径开发一个应用。让机器人**记住这个项目中使用的技术栈**。

```bash
请记住这个项目中使用的技术栈：Next.js（React）+ TypeScript + TailWindCSS
```

**告诉机器人当前项目的 github 地址，每当完成编码任务后，都将变更 push 到仓库：**

```bash
当前的 github 仓库地址是 https://github.com/zhijunio/test-openclaw，每当完成编码任务后，都将变更 push 到仓库
```

告诉机器人开发注意事项：

```bash
请记住，在开发前端项目的时候，配色不要出现蓝紫渐变色
```

开始机器人项目的公网地址：

```bash
请记住这是 codespace 的公网链接：https://ominous-rotary-phone-r4g7p779g6hw5v4-18789.app.github.dev/

每当你完成开发后，确保运行前端项目，运行后，请直接发给我项目运行的公网链接，以便我在手机上访问，注意端口号不要冲突
```

公网地址在 codespace 端口 tab 页面可以找到

![install-openclaw-in-github-codespace](15.webp)

让机器人开发一个 Todo List 应用。

```bash
为我开发一个 Todo List 应用，要求具备基础的功能，UI 设计符合现代设计最佳实践
```

稍等，Todo List 应用已创建完成并且代码也会提交到 github。

![install-openclaw-in-github-codespace](16.webp)

打开浏览器访问 todo 应用：

![install-openclaw-in-github-codespace](17.webp)

如果你对样式不满意或者想添加新的功能，直接在电报应用里发送消息给机器人修改即可。

可以添加一个定时任务，让 openclaw 保持运行状态。

```bash
为我设置一个定时任务，每隔一个小时告诉我武汉的天气预报
```

![install-openclaw-in-github-codespace](18.webp)

## 总结

- **创建环境**：在 GitHub 新建仓库后，通过「Create a Codespace」进入云端 IDE。
- **安装 OpenClaw**：在终端执行官方安装脚本；可选 `--no-onboard` 仅装 CLI。按向导完成模型（如千问）、渠道（如 Telegram）、Search provider、Skills 与 Hooks 的配置。
- **启动网关**：Codespaces 无 systemd，需直接运行 `openclaw gateway`；日常使用可用 `nohup ... &` 后台运行，用 `openclaw status` 确认可达。
- **配对与对话**：在 Telegram 触发配对后，在终端执行 `openclaw pairing approve telegram <码>` 完成绑定，即可在电报中与机器人对话。
- **让机器人「记住」上下文**：通过对话告知项目路径、技术栈、Git 仓库、公网预览地址、开发偏好等，便于后续编码与推送。
- **实战示例**：可让机器人开发应用（如 Todo List）并 push 到仓库；也可添加定时任务（如每小时推送天气），充分利用 OpenClaw 在 Codespaces 中的能力。

「延伸阅读：[sanwan.ai](http://sanwan.ai/) — AI 自主运营网站实录」

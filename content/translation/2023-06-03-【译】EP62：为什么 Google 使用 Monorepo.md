---
title: "【译】EP62：为什么 Google 使用 Monorepo"
date: 2023-06-03 23:30:00+08:00
draft: true
slug: "ep62-why-does-google-use-monorepo"
categories: [ "translation" ]
tags: [ "architecture" ]
description: "这篇文章对比了 Monorepo 和 Microrepo 的优缺点，解释了为什么 Google、Meta 等公司选择 Monorepo 策略。"
canonicalURL: "https://blog.bytebytego.com/p/ep62-why-does-google-use-monorepo"
---

在这篇文章中，我们将讨论以下话题：
- 6 个最流行的 API 架构风格
- Monorepo vs. Microrepo
- HTTP Header 内部
- 开发者路线图

## Monorepo vs. Microrepo

这种做法称为 Monorepo（单体仓库）。

### 哪个最好？

为什么不同的公司选择不同的选项？

Monorepo 并不新鲜；Linux 和 Windows 都是使用 Monorepo 创建的。为了提高可扩展性和构建速度，Google 开发了自己的内部专用工具链，以更快地扩展并保持严格的编码质量标准。

Amazon 和 Netflix 是微服务哲学的主要倡导者。这种方法自然地将服务代码分离到单独的仓库中。它扩展更快，但可能导致后来的治理痛点。

### Monorepo 特点

在 Monorepo 内，每个服务是一个文件夹，每个文件夹都有 BUILD 配置和 OWNERS 权限控制。每个服务成员负责自己的文件夹。

- **依赖共享**：依赖在整个代码库中共享，无论你的业务如何，所以当有版本升级时，每个代码库都升级他们的版本
- **标准检查**：Monorepo 有签入标准。Google 的代码审查流程以设置高门槛而闻名，确保 Monorepo 的连贯质量标准，无论业务如何

### Microrepo 特点

在 Microrepo 中，每个服务负责自己的仓库，构建配置和权限通常为整个仓库设置。

- **依赖控制**：依赖在每个仓库内控制。业务根据自己的时间表选择何时升级版本
- **标准灵活**：Microrepo 可以设置自己的标准或通过结合最佳实践采用共享标准。它可以为业务更快扩展，但代码质量可能有所不同

### 构建工具

- **Google**：构建了 Bazel
- **Meta**：构建了 Buck
- **其他开源工具**：Nix、Lerna 等

多年来，Microrepo 有更多支持的工具，包括 Java 的 Maven 和 Gradle、NodeJS 的 NPM、C/C++的 CMake 等。

**问题**：你认为哪个选项更好？你的公司使用哪种代码仓库策略？

## HTTP Header 内部

HTTP 请求就像向服务器请求东西，HTTP 响应是服务器的回复。就像发送消息并接收回复一样。

HTTP 请求头是你在发出请求时包含的额外信息，例如你发送什么类型的数据或你是谁。在响应头中，服务器提供有关它发送给你的响应的信息，例如你接收什么类型的数据或你是否有特殊说明。

头在构建 RESTful 应用时在实现客户端 - 服务器通信方面起着至关重要的作用。为了在请求中发送正确的信息并正确解释服务器的响应，你需要了解这些头。

**问题**：头"referer"是一个拼写错误。你知道正确的名称是什么吗？

## 开发者路线图

我最近发现了这个有趣的 GitHub 仓库。它包含路线图、指南和教育内容，旨在帮助开发者找到他们在科技世界的道路。

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[EP62: Why Does Google Use Monorepo?](https://blog.bytebytego.com/p/ep62-why-does-google-use-monorepo)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

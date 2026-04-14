---
title: "【译】EP66：URL、URI 和 URN 对比"
date: 2023-07-01 23:30:00+08:00
draft: true
slug: "ep66-comparison-of-url-uri-and-urn"
categories: [ "translation" ]
tags: [ "networking" ]
description: "这篇文章介绍了 URL、URI 和 URN 的区别，数据仓库 vs. 数据湖对比，以及 Twitter 1.0 技术栈。"
canonicalURL: "https://blog.bytebytego.com/p/ep66-comparison-of-url-uri-and-urn"
---

在这篇文章中，我们将讨论以下话题：
- OAuth 2 简单解释
- URL、URI 和 URN 对比
- 数据仓库 vs. 数据湖
- Twitter 1.0 技术栈

## URL、URI 和 URN 对比

下图显示了 URL、URI 和 URN 的对比。

### URI（Uniform Resource Identifier）
URI 代表统一资源标识符。它标识 Web 上的逻辑或物理资源。URL 和 URN 是 URI 的子类型。URL 定位资源，而 URN 命名资源。

URI 由以下部分组成：
```
scheme:[//authority]path[?query][#fragment]
```

### URL（Uniform Resource Locator）
URL 代表统一资源定位符，HTTP 的关键概念。它是 Web 上唯一资源的地址。它可以与其他协议一起使用，如 FTP 和 JDBC。

### URN（Uniform Resource Name）
URN 代表统一资源名称。它使用 urn 方案。URN 不能用于定位资源。图中给出的简单示例由命名空间和特定于命名空间的字符串组成。

如果你想了解更多细节，我推荐 W3C 的澄清。

## 数据仓库 vs. 数据湖

下图显示了它们的对比。

- **数据结构**：数据仓库处理结构化数据，而数据湖处理结构化、半结构化、非结构化和原始二进制数据
- **存储成本**：数据仓库利用数据库存储结构化数据层，可能很昂贵。数据湖将数据存储在低成本设备中
- **数据处理**：数据仓库对数据执行 ETL（提取 - 转换 - 加载）。数据湖执行 ELT（提取 - 加载 - 转换）
- **模式**：数据仓库是写时模式（schema-on-write），这意味着数据在写入数据仓库时已经准备好。数据湖是读时模式（schema-on-read），所以数据按原样存储。然后可以转换数据并存储到数据仓库中供消费

**问题**：你使用数据仓库还是数据湖来检索数据？

## Twitter 1.0 技术栈

这篇文章基于许多 Twitter 工程博客和开源项目的研究。

### 技术栈

- **移动**：Swift、Kotlin、PWA
- **Web**：JS、React、Redux
- **服务**：Mesos、Finagle
- **缓存**：Pelikan Cache、Redis
- **数据库**：Manhattan、MySQL、PostgreSQL、FlockDB、MetricsDB
- **消息队列**：Kafka、Kestrel
- **数据处理**：Heron、Flume、Tableau、SummingBird、Scalding
- **数据存储**：Hadoop、blob store
- **数据中心**：Twitter 数据中心、AWS、Google Cloud
- **工具**：Puppet、Audubon、Wilson

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[EP66: Comparison of URL, URI, and URN](https://blog.bytebytego.com/p/ep66-comparison-of-url-uri-and-urn)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

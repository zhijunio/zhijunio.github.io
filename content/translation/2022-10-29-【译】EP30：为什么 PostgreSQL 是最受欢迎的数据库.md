---
title: "【译】EP30：为什么 PostgreSQL 是最受欢迎的数据库"
date: 2022-10-29 23:39:00+08:00
draft: true
slug: "ep30-why-is-postgresql-the-most-loved"
categories: [ "translation" ]
tags: [ "database", "system-design" ]
description: "这篇文章介绍了 PostgreSQL 的多功能用例（OLTP、OLAP、FDW、流处理、地理空间、时间序列、分布式表），以及正向代理 vs 反向代理、时间表示和 2012 年 Twitter 架构。"
canonicalURL: "https://blog.bytebytego.com/p/ep30-why-is-postgresql-the-most-loved"
---

在这篇文章中，我们将讨论以下话题：
- 为什么 PostgreSQL 是最受欢迎的数据库
- 什么是代理
- 什么是时间/时钟
- 2012 年的 Twitter 架构

## PostgreSQL 的多功能用例

下图展示了 PostgreSQL 的多种用例——一个几乎包含开发人员所需所有用例的数据库。

### OLTP（在线事务处理）
我们可以使用 PostgreSQL 进行 CRUD（创建 - 读取 - 更新 - 删除）操作。

### OLAP（在线分析处理）
我们可以使用 PostgreSQL 进行分析处理。PostgreSQL 基于 HTAP（混合事务/分析处理）架构，因此它可以很好地处理 OLTP 和 OLAP。

### FDW（外部数据包装器）
FDW 是 PostgreSQL 中可用的扩展，允许我们从一个数据库访问另一个数据库中的表或模式。

### 流处理
PipelineDB 是一个 PostgreSQL 扩展，用于高性能时间序列聚合，旨在为实时报告和分析应用提供支持。

### 地理空间
PostGIS 是 PostgreSQL 对象关系数据库的空间数据库扩展器。它添加了对地理对象的支持，允许在 SQL 中运行位置查询。

### 时间序列
Timescale 扩展 PostgreSQL 用于时间序列和分析。例如，开发人员可以将持续的财务和 tick 数据流与其他业务数据结合起来，构建新应用并发现独特见解。

### 分布式表
CitusData 通过分发数据和查询来扩展 Postgres。

## 什么是代理

**正向代理**：是位于一组客户端机器和互联网之间的服务器。

**反向代理**：位于互联网和 Web 服务器之间。它拦截来自客户端的请求，并代表客户端与 Web 服务器通信。

## 什么是时间/时钟

每隔几年，就会出现一种特殊现象，"23:59:59"之后的下一秒不是"00:00:00"而是"23:59:60"。这称为闰秒，如果不仔细处理，很容易导致时间处理错误。

我们总是需要处理闰秒吗？这取决于使用哪种时间表示。常用的时间表示包括 UTC、GMT、TAI、Unix 时间戳、Epoch 时间、TrueTime 和 GPS 时间。

## 2012 年的 Twitter 架构

既然每个人都在谈论 Twitter，让我们快速看看 2012 年 Twitter 架构是什么样子的。这篇文章基于 Twitter 工程师的技术演讲。

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[EP30: Why is PostgreSQL the most loved database](https://blog.bytebytego.com/p/ep30-why-is-postgresql-the-most-loved)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

---
title: "【译】一致性和分区容错：理解 CAP vs PACELC"
date: 2025-07-24 23:30:00+08:00
draft: true
slug: "consistency-and-partition-tolerance"
categories: [ "translation" ]
tags: ["distributed-systems", "database" ]
description: "这篇文章介绍了 CAP 定理和 PACELC 定理，帮助理解分布式数据库在一致性、可用性和延迟之间的权衡。"
canonicalURL: "https://blog.bytebytego.com/p/consistency-and-partition-tolerance"
---

现代数据库不再运行在单机上。它们跨越区域，在节点间复制数据，并并行处理数百万查询。

然而，每次数据库试图同时快速、可用和正确时，总有什么必须让步。随着系统扩展，容错承诺与正确性需求发生冲突。例如，结账服务不能因为节点离线就向用户重复收费。但每次副本延迟就停止系统会破坏可用性假象。延迟、副本延迟和网络分区不是边缘情况。

分布式数据库必须不断管理这些权衡。例如：

- 写入请求可能在一个区域成功但在另一个区域不成功
- 读取可能返回陈旧数据，除非明确告诉等待
- 一些系统优化正常运行时间并接受不一致
- 其他系统阻塞直到副本同意，牺牲速度以保持正确性

两个模型帮助理解这个：CAP 定理和 PACELC 定理。CAP 解释为什么数据库在网络分区存在时必须在保持可用和保持一致之间选择。PACELC 将这个推理扩展到正常情况：即使没有故障，数据库仍然在延迟和一致性之间权衡。

在本文中，我们将看看这两个模型如何应用于现实世界数据库设计，并理解涉及的各种权衡。

## CAP 定理

CAP 定理指出，分布式数据存储只能提供以下三个保证中的两个：

1. **一致性（Consistency）**：每次读取都收到最近的写入或错误
2. **可用性（Availability）**：每次请求都收到响应（不一定是最新的）
3. **分区容错性（Partition Tolerance）**：系统在网络分区时继续运行

关键是，当网络分区发生时，系统必须在一致性和可用性之间选择。

### 实际含义

- **CA 系统**：选择一致性和可用性，但不能容忍分区。实际上，这意味着单节点系统或紧密耦合的集群。
- **CP 系统**：选择一致性和分区容错性，但在分区期间可能不可用。示例：MongoDB、HBase。
- **AP 系统**：选择可用性和分区容错性，但在分区期间可能返回陈旧数据。示例：Cassandra、DynamoDB。

## PACELC 定理

PACELC 扩展了 CAP 定理，提供更细致的框架：

**PACELC** 代表：
- **PA**：如果分区（Partition），那么选择可用性（Availability）或一致性（Consistency）
- **EL**：Else（否则，即没有分区）
- **LC**：那么选择延迟（Latency）或一致性（Consistency）

### 实际含义

即使在没有网络分区的正常情况下，数据库也必须在延迟和一致性之间权衡：

- **PA/EC 系统**：分区时选择可用性，否则选择一致性。示例：DynamoDB、Cassandra。
- **PC/EC 系统**：分区时选择一致性，否则选择一致性。示例：BigTable、HBase。
- **PC/EL 系统**：分区时选择一致性，否则选择延迟。示例：PostgreSQL、MySQL（单节点）。

## 现实世界数据库分类

### CP 系统（一致性 + 分区容错）
- **MongoDB**：默认配置
- **HBase**：始终一致
- **Redis**：单线程模型

### AP 系统（可用性 + 分区容错）
- **Cassandra**：最终一致性
- **DynamoDB**：可配置一致性
- **CouchDB**：多主复制

### CA 系统（一致性 + 可用性）
- **PostgreSQL**：单节点
- **MySQL**：单节点
- **传统关系数据库**

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[Consistency and Partition Tolerance: Understanding CAP vs PACELC](https://blog.bytebytego.com/p/consistency-and-partition-tolerance)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

---
title: "【译】EP119：Amazon、Netflix 和 Uber 有什么共同点？"
date: 2024-07-06 23:30:00+08:00
draft: true
slug: "ep119-what-do-amazon-netflix-and"
categories: [ "translation" ]
tags: [ "scaling", "architecture", "best-practices" ]
description: "这篇文章介绍了 Amazon、Netflix 和 Uber 的共同点（扩展能力），以及 Figma 的 100 倍 Postgres 扩展和系统功能测试方法。"
canonicalURL: "https://blog.bytebytego.com/p/ep119-what-do-amazon-netflix-and"
---

本周系统设计复习：
- 扩展数据库的 7 个必知策略
- Amazon、Netflix 和 Uber 有什么共同点？
- Figma 的 100 倍 Postgres 扩展
- 测试系统功能的最佳方法

## 扩展系统的 8 个必知策略

它们非常擅长在需要时扩展系统。

以下是扩展系统的 8 个必知策略：

### 1. 无状态服务（Stateless Services）
设计无状态服务，因为它们不依赖服务器特定数据，更容易扩展。

### 2. 水平扩展（Horizontal Scaling）
添加更多服务器，以便可以共享工作负载。

### 3. 负载均衡（Load Balancing）
使用负载均衡器在多个服务器之间均匀分发传入请求。

### 4. 自动扩展（Auto Scaling）
实施自动扩展策略以根据实时流量调整资源。

### 5. 缓存（Caching）
使用缓存减少数据库负载并在规模上处理重复请求。

### 6. 数据库复制（Database Replication）
跨多个节点复制数据以扩展读操作，同时提高冗余。

### 7. 数据库分片（Database Sharding）
跨多个实例分发数据以扩展写入和读取。

### 8. 异步处理（Async Processing）
使用异步处理将耗时和资源密集型任务移动到后台 worker 以扩展新请求。

## Figma 的 100 倍 Postgres 扩展

拥有 300 万月活用户，Figma 的用户群自 2018 年以来增加了 200%。

因此，它的 Postgres 数据库见证了惊人的 100 倍增长。

### 1. 垂直扩展和复制
Figma 使用单个大型 Amazon RDS 数据库。作为第一步，他们升级到可用的最大实例（从 r5.12xlarge 到 r5.24xlarge）。他们还创建了多个读副本以扩展读流量，并添加 PgBouncer 作为连接池器以限制越来越多连接的影响。

### 2. 垂直分区
下一步是垂直分区。他们将高流量表如"Figma Files"和"Organizations"迁移到它们单独的数据库中。多个 PgBouncer 实例用于管理这些单独数据库的连接。

### 3. 水平分区
随着时间的推移，一些表跨越数 TB 数据和数十亿行。Postgres Vacuum 成为问题，最大 IOPS 超过了当时 Amazon RDS 的限制。为解决这个问题，Figma 实施了水平分区，将大表拆分到多个物理数据库中。构建了新的 DBProxy 服务来处理路由和查询执行。

## 测试系统功能的最佳方法

测试系统功能是软件开发和工程过程中的关键步骤。

它确保系统或软件应用按预期执行，满足用户需求，并可靠运行。

以下是最佳方法：

### 1. 单元测试（Unit Testing）
确保单个代码组件在隔离情况下正确工作。

### 2. 集成测试（Integration Testing）
验证不同系统部分无缝一起工作。

### 3. 系统测试（System Testing）
评估整个系统的合规性与用户要求和性能。

### 4. 负载测试（Load Testing）
测试系统处理高工作负载的能力并识别性能问题。

### 5. 错误测试（Error Testing）
评估软件如何处理无效输入和错误条件。

### 6. 测试自动化（Test Automation）
自动化测试用例执行以提高效率、可重复性和错误减少。

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[EP119: What do Amazon, Netflix, and Uber have in common?](https://blog.bytebytego.com/p/ep119-what-do-amazon-netflix-and)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

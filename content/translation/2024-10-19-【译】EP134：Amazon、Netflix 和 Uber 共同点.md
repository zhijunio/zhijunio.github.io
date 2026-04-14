---
title: "【译】EP134：Amazon、Netflix 和 Uber 有什么共同点？"
date: 2024-10-19 23:30:00+08:00
draft: true
slug: "ep134-what-do-amazon-netflix-and"
categories: [ "translation" ]
tags: [ "scaling", "architecture" ]
description: "这篇文章介绍了扩展系统的 8 个必知策略、分页 vs. 分段、Git 工作流和微服务技术栈。"
canonicalURL: "https://blog.bytebytego.com/p/ep134-what-do-amazon-netflix-and"
---

本周系统设计复习：
- 10 分钟简单解释可扩展性
- Amazon、Netflix 和 Uber 有什么共同点？
- 分页和分段之间有什么区别？
- Git 如何工作？
- 微服务通常使用什么技术栈？

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

## 分页 vs. 分段

### 分页（Paging）
分页是消除对物理内存连续分配需求的内存管理方案。进程地址空间划分为固定大小的块，称为页，而物理内存划分为固定大小的块，称为帧。

**地址翻译过程分 3 步**：
1. **逻辑地址空间**：逻辑地址（由 CPU 生成）划分为页号和页偏移
2. **页表查找**：页号用作页表的索引以找到相应的帧号
3. **物理地址形成**：帧号与页偏移组合形成内存中的物理地址

**优势**：
- 消除外部碎片
- 简化内存分配
- 支持高效交换和虚拟内存

### 分段（Segmentation）
分段是内存管理技术，其中内存基于程序的逻辑划分（如函数、对象或数据数组）划分为可变大小的段。

**地址翻译过程分 3 步**：
1. **逻辑地址空间**：逻辑地址由段号和段内偏移组成
2. **段表查找**：段号用作段表的索引以找到段的基地址
3. **物理地址形成**：基地址与偏移相加形成内存中的物理地址

**优势**：
- 提供程序不同部分的逻辑分离
- 促进段的保护和共享
- 简化增长数据结构的管理

## Git 工作流

下图显示了 Git 工作流。

Git 是分布式版本控制系统。

每个开发者维护主仓库的本地副本，并在本地副本上编辑和提交。

提交非常快，因为操作不与远程仓库交互。

如果远程仓库崩溃，文件可以从本地仓库恢复。

**思考题**：你使用哪个 Git 命令来解决冲突更改？

## 微服务技术栈

下面你将找到一个图表，显示微服务技术栈，包括开发阶段和生产阶段。

### 预生产
- **定义 API**：这在前后端之间建立契约。我们可以使用 Postman 或 OpenAPI 来实现

### 开发
- **Node.js 或 React**：前端开发流行
- **Java/Python/Go**：后端开发
- 我们需要根据 API 定义更改 API 网关中的配置

### 持续集成
- **JUnit 和 Jenkins**：用于自动化测试
- 代码打包到 Docker 镜像并作为微服务部署

### 生产
- **NGinx**：负载均衡器的常见选择
- **Cloudflare**：提供 CDN（内容分发网络）
- **API 网关**：我们可以使用 Spring Boot 作为网关，使用 Eureka/Zookeeper 进行服务发现
- **微服务部署在云上**：我们有 AWS、Microsoft Azure 或 Google GCP 选项
- **缓存和全文搜索**：Redis 是缓存键值对的常见选择。ElasticSearch 用于全文搜索
- **通信**：服务相互交谈，我们可以使用消息基础设施 Kafka 或 RPC
- **持久化**：我们可以使用 MySQL 或 PostgreSQL 作为关系数据库，Amazon S3 用于对象存储。如果需要，我们也可以使用 Cassandra 作为宽列存储
- **管理和监控**：为管理如此多的微服务，常见 Ops 工具包括 Prometheus、Elastic Stack 和 Kubernetes

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[EP134: What do Amazon, Netflix, and Uber have in common?](https://blog.bytebytego.com/p/ep134-what-do-amazon-netflix-and)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

---
title: "【译】EP178：Kubernetes Pod 生命周期"
date: 2025-08-30 23:49:00+08:00
draft: true
slug: "ep178-lifecycle-of-kubernetes-pod"
categories: [ "translation" ]
tags: [ "kubernetes" ]
description: "这篇文章介绍了 Kubernetes Pod 的生命周期，从创建到终止的各个阶段。"
canonicalURL: "https://blog.bytebytego.com/p/ep178-the-lifecycle-of-a-kubernetes"
---

## Kubernetes Pod 生命周期

### Pod 创建和调度
1. **Pod manifest 提交到 API 服务器并存储在 etcd**
2. **调度器选择节点为 Pod**基于资源、亲和规则，并绑定 Pod 到那个节点
3. **kubelet 准备 Pod**通过创建它网络命名空间、分配 IP、挂载卷、拉取镜像如果需要

### Pod 运行
4. **容器从 Waiting 移动到 Running**，kubelet 监控健康探针用于 liveness 和 readiness
5. **Kubernetes 跟踪 Pod 高级阶段**从 Pending 到 Running 到 Succeeded/Failed/Unknown

### Pod 终止
6. **在终止时，Kubernetes 发送 SIGTERM**（和 SIGKILL 如果需要）为 Pod 内单独容器
7. **在终止后，资源清理**，Pod 详情从 etcd 移除

## CI/CD 管道解释

CI/CD 管道是工具自动化构建、测试和部署软件过程。

它集成软件开发生命周期不同阶段，包括代码创建和修订、测试和部署，到单个、凝聚工作流。

### 常用工具
- **版本控制**：Git、GitHub、GitLab
- **CI 工具**：Jenkins、GitHub Actions、CircleCI
- **测试工具**：JUnit、Selenium、Cypress
- **部署工具**：Kubernetes、Docker、Terraform

## 开源 RAG 栈

### 前端框架
用于构建 RAG 应用前端界面。一些工具可以帮助是 NextJS、VueJS、SvelteKit 和 Streamlit。

### LLM 框架
LLM 管道、提示和链高级编排。这包括工具如 LangChain、LlamaIndex、Haystack、HuggingFace 和 Semantic Kernel。

### LLMs
使用大型语言模型生成最终响应。一些开源选项包括 Llama、Mistral、Gemma、Phi-2、DeepSeek、Qwen 等。

### 检索和排名
检索相关块并基于相关性排名。工具如 Meta FAISS、Haystack Retrievers、Weaviate Hybrid Search、ElasticSearch kNN 和 JinaAI Rerankers 可以帮助。

### 向量数据库
存储和启用相似性搜索跨向量嵌入。常见选项包括 Weaviate、Milvus、Postgres pgVector、Chroma 和 Pinecone。

### 嵌入模式
使用 ML 转换文本/数据为向量表示。一些开源工具包括 HuggingFace Transformers、LLMWare、Nomic、Sentence Transformers、JinaAI 和 Cognita。

### Ingest/数据处理
提取、清理和准备原始数据为索引和检索。工具如 Kubeflow、Apache Airflow、Apache NiFi、LangChain Document Loads、Haystack Pipelines 和 OpenSearch 可以帮助。

## 版本控制策略

版本控制帮助开发者沟通发布变化清晰，无论是为软件包、API 或操作系统。

### 语义版本控制（SemVer）
- 版本控制方案传达意义关于发布中变化范围使用格式 MAJOR.MINOR.PATCH

### 日历版本控制（CalVer）
- 方案使用发布日期（年和月）作为版本号指示发布何时发生

### 顺序版本控制
- 简单编号方法版本增加在序列没有编码兼容性细节

### API 版本控制
- 方法嵌入版本在 API URL 路径管理分离破坏变化

## 测试金字塔

测试是可靠软件骨干。测试金字塔是广泛接受策略结构化测试为三个关键层：

### 单元测试（Unit Tests）
- 金字塔基础
- 快速、隔离、低成本编写和维护
- 测试单独函数、方法或组件

### 集成测试（Integration Tests）
- 验证组件间交互，如 API、数据库和外部服务
- 比单元测试慢并需要更多设置

### E2E 测试（E2E Tests）
- 模拟真实用户流从开始到结束跨完整系统
- 昂贵编写和维护并趋向慢执行

**当你上金字塔，测试开发、执行和维护成本增加。**

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[EP178: The Lifecycle of a Kubernetes Pod](https://blog.bytebytego.com/p/ep178-the-lifecycle-of-a-kubernetes)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

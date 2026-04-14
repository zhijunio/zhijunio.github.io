---
title: "【译】Kubernetes 速成课程"
date: 2023-10-26 23:30:00+08:00
draft: true
slug: "a-crash-course-in-kubernetes"
categories: [ "translation" ]
tags: [ "kubernetes" ]
description: "这篇文章介绍了 Kubernetes 的核心概念（Pod、控制器、服务）、集群组件、适用场景以及采用 Kubernetes 前需要考虑的权衡。"
canonicalURL: "https://blog.bytebytego.com/p/a-crash-course-in-kubernetes"
---

在当今世界，复杂的 Web 规模应用程序后端由许多微服务和组件构成，它们运行在服务器集群和容器之上，管理和协调所有这些部分极具挑战性。

这就是 Kubernetes 发挥作用的地方。Kubernetes（也称为"k8s"）是一个开源容器编排平台，可自动化部署、扩展和管理容器化应用程序。

使用 Kubernetes，你不必担心手动放置容器或重启失败的容器。你只需描述期望的应用程序架构，Kubernetes 就会实现它并保持其运行。

在这个两部分系列中，我们将深入探讨 Kubernetes，涵盖：

- 核心概念，如 Pod、控制器和服务
- 构成 Kubernetes 集群的组件
- 何时以及为什么 Kubernetes 对你的应用程序有用
- 采用 Kubernetes 之前需要考虑的权衡

我们将揭开 Kubernetes 的神秘面纱，让你拥有判断 Kubernetes 是否以及何时适合你的应用程序所需的一切知识。读完之后，你会清楚地了解 Kubernetes 是什么、它如何工作以及如何付诸实践。

无论你是开发人员、运维工程师还是技术领导者，都会在这篇 Kubernetes 深度解析中找到宝贵的见解。让我们开始吧！

Kubernetes 可以追溯到 Google 内部的容器编排系统 Borg，它管理着 Google 内部数千个应用程序的部署。容器是一种将应用程序打包并隔离到标准化单元中的方法，这些单元可以轻松地在不同环境之间移动。与虚拟化整个操作系统的传统虚拟机（VM）不同，容器只虚拟化应用程序层，这使得它们更轻量、更便携、更高效。

![容器与虚拟机的对比](01.webp)

2014 年，Google 基于从 Borg 获得的经验开源了一个容器编排系统。这就是 Kubernetes。Kubernetes 提供容器化应用程序的自动化部署、扩展和管理。通过利用容器而非虚拟机，Kubernetes 提供了诸多优势，如提高资源效率、更快地部署应用程序，以及在本地和云环境之间的可移植性。

![Borg 到 Kubernetes 的演进](02.webp)

来源：Large-scale cluster management at Google with Borg

为什么它也被称为 k8s？这是一种有点极客式的长词缩写方式。k8s 中的数字 8 指的是单词"Kubernetes"中第一个字母"k"和最后一个字母"s"之间的 8 个字母。

Kubernetes 的核心遵循客户端 - 服务器架构。Kubernetes 集群中有两个核心部分：**控制平面**（control plane）和**工作节点**（worker nodes）。

![Kubernetes 集群架构](03.webp)

控制平面负责管理集群的状态。在生产环境中，控制平面通常运行在多个节点上，这些节点跨越多个数据中心区域。

换句话说，控制平面管理工作节点及其上运行的容器。

容器化应用程序运行在**Pod**中。Pod 是 Kubernetes 中最小的可部署单元。一个 Pod 托管一个或多个容器，并为这些容器提供共享存储和网络。Pod 由 Kubernetes 控制平面创建和管理。它们是 Kubernetes 应用程序的基本构建块。

让我们更深入地了解主要组件。

控制平面是 Kubernetes 的大脑。它由各种组件组成，这些组件共同对集群做出全局决策。控制平面组件在多个可用区的服务器上运行，以提供高可用性。

关键组件包括：

- Kubernetes API 服务器
- Etcd
- Kubernetes 调度器
- Kubernetes 控制器管理器

![控制平面组件](04.webp)

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[A Crash Course in Kubernetes](https://blog.bytebytego.com/p/a-crash-course-in-kubernetes)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

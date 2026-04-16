---
title: "linkding 合并 linkding-cn 代码"
date: 2026-03-06 21:40:00+08:00
slug: merge-linkding-cn-to-linkding
categories: [ "tech" ]
tags: [ "linkding" ]
description: "本文将详细介绍如何将 linkding-cn 的优秀功能迁移到最新的 Linkding 项目中，包括项目对比、可行性分析、迁移过程以及最终的"
favicon: "linkding.svg
"
---

本文将详细介绍如何将 linkding-cn 的优秀功能迁移到最新的 Linkding 项目（1.45.0 版本)中，包括项目对比、可行性分析、迁移过程以及最终的
Docker 打包。

<!--more-->

[Linkding](https://github.com/sissbruecker/linkding)
是一个优秀的自托管书签管理器，以其简洁、快速和易用性而受到社区喜爱。而 [linkding-cn](https://github.com/WooHooDai/linkding-cn)
是一个针对中文用户优化的 fork 版本，添加了许多实用功能。

合并后的代码在 [chensoul/linkding](https://github.com/zhijunio/linkding/)，**示例项目：** <https://linkding.zhijun.io/>。

## 一、项目对比分析

> **对比日期**：2026 年 3 月 6 日

### 1.1 项目概况

| 维度         | Linkding (官方)         | linkding-cn                       |
|------------|-----------------------|-----------------------------------|
| **版本**     | 1.45.0                | 1.0.3                             |
| **上游**     | sissbruecker/linkding | fork 自官方                          |
| **分叉点**    | -                     | 约 2025 年 7 月                      |
| **提交差异**   | 最新                    | 领先 186 个自定义提交，落后 111 个上游提交        |
| **Python** | 3.13                  | 3.12                              |
| **Django** | 6.0                   | 5.2.4                             |
| **依赖管理**   | pyproject.toml + uv   | requirements.txt + uv pip compile |

### 1.2 技术栈差异

**linkding-cn 独有依赖：**

- `drissionpage`：自定义快照脚本（浏览器自动化）
- `pypinyin`：中文标签拼音分组
- `python-dateutil`：日期处理
- `django-registration`：用户注册
- `django-widget-tweaks`：表单控件增强

**当前项目优势：**

- 使用最新的 Python 3.13 和 Django 6.0
- 采用现代化的 `pyproject.toml` 和 `uv` 进行依赖管理
- 代码结构更清晰，维护性更好

### 1.3 功能差异对比

linkding-cn 相比官方版本添加了以下主要功能：

| 类别      | 功能                                   | 优先级 |
|---------|--------------------------------------|-----|
| **本地化** | 界面中文化、中文标签聚合                         | 高   |
| **搜索**  | 限定搜索范围（标题、描述、笔记、URL）                 | 中   |
| **筛选**  | 日期筛选（绝对/相对）、标签状态（有标签/无标签）            | 中   |
| **排序**  | 随机排序、按删除时间排序                         | 中   |
| **过滤器** | Bundle 二级过滤器、`search_params` 支持更多筛选项 | 中   |
| **元数据** | 自定义解析脚本、更多网站支持                       | 低   |
| **快照**  | 自定义脚本（drissionpage）、重命名              | 低   |
| **回收站** | 软删除、还原、永久删除、批量操作                     | 低   |

## 二、迁移可行性分析

### 2.1 按功能迁移

**直接 Git merge 不可行**，原因如下：

1. **版本差异大**：分叉点（2025 年 7 月）距今约 8 个月（截至 2026 年 3 月），上游有 111 个新提交
2. **技术栈升级**：Django 5 → 6，Python 3.12 → 3.13
3. **依赖管理方式不同**：requirements.txt → pyproject.toml
4. **代码结构变化**：模型、视图、模板都有较大改动
5. **冲突数量多**：预计会有数百个合并冲突

采用**按功能模块选择性迁移**的策略，具有以下优势：

✅ **风险可控**：每个功能独立迁移，单独测试  
✅ **适配灵活**：可以适配最新的技术栈和代码结构  
✅ **质量保证**：迁移过程中可以优化代码质量  
✅ **渐进式**：优先迁移高价值、低依赖的功能

### 2.2 迁移优先级评估

根据功能价值和实现难度，我们制定了以下优先级：

**迁移以下功能：**

- ✅ 中文本地化
- ✅ 日期筛选（绝对/相对）
- ✅ 搜索范围限定
- ✅ 随机排序
- ✅ 标签状态筛选
- ✅ Bundle 添加日期按相对时间筛选
- ✅ 中文标签拼音分组（pypinyin）
- ✅ 优化书签标题获取（支持 og:title、twitter:title）
- ✅ 优化 favicon 获取（支持 icon 、svg）

**不迁移以下功能：**

- ❌ 界面增强（粘性、滚动、折叠记忆）
- ❌ 阅读模式增强
- ❌ 回收站功能（需要大量模型改动）
- ❌ 自定义元数据/快照脚本（依赖重）

### 2.3 迁移方式

让 AI
对比两个仓库的区别，生成 [linkding-cn 与当前项目对比及合并可行性分析](https://github.com/zhijunio/linkding/blob/master/docs/linkding-cn-merge-analysis.md)
文档，然后制定[迁移计划](https://github.com/zhijunio/linkding/blob/master/docs/linkding-cn-migration-plan.md)。

## 三、Docker 镜像构建

迁移成功之后，建议使用 github action 来构建 Docker 镜像。

如果想在本地 macos 系统构建，需要先修改脚本 scripts/build-docker.sh：

```bash
base_platform="linux/amd64"
plus_platform="linux/amd64"
```

使用运行下面命令。

```bash
bash scripts/build-docker.sh
```
## 四、如何使用

先登录原来的系统，导出所有标签作为备份。

参考 [我的VPS服务部署记录](/posts/2023/01/25/notes-about-deploy-services-in-vps#linkding)这篇文章，修改 docker-compose
文件如下：

```yaml
services:
  linkding:
    #image: woohoodai/linkding-cn:latest
    #image: sissbruecker/linkding
    image: chensoul/linkding
    container_name: linkding
    restart: unless-stopped
    environment:
      - LD_LANGUAGE=zh-hans
      - LD_SUPERUSER_NAME=admin
      - LD_SUPERUSER_PASSWORD=E2KWdEGCEF7Bihx!98
      - LD_DB_ENGINE=postgres
      - LD_DB_DATABASE=linkding
      - LD_DB_HOST=postgres
      - LD_DB_USER=postgres
      - LD_DB_PASSWORD=vps@027!
    ports:
      - "127.0.0.1:9090:9090"
    networks:
      - vps

networks:
  vps:
    external: true
```

主要改动如下：

- 修改镜像为 chensoul/linkding
- 环境变量添加语言设置 LD_LANGUAGE=zh-hans

将数据库 linkding 清空，然后重新启动 linkding 容器。

## 五、参考资源

- [Linkding 官方仓库](https://github.com/sissbruecker/linkding)
- [linkding-cn 仓库](https://github.com/WooHooDai/linkding-cn)
- [Docker 官方文档](https://docs.docker.com/)

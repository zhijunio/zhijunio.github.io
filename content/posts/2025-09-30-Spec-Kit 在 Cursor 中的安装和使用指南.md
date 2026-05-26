---
title: "Cursor 中安装 Spec-Kit：规范驱动开发入门"
date: 2025-09-29 08:00:00+08:00
slug: spec-kit-with-cursor
tags: [ "spring-ai", "cursor" ]
description: "介绍如何在 Cursor 中安装和使用 Spec-Kit，借助规范驱动开发流程把需求定义、实现与 AI 编码协作串联起来。"
---

在现代软件开发中，规范驱动开发（Spec-Driven Development）正成为一种越来越重要的开发方法。Spec-Kit 是 GitHub 开源的一个强大工具包，专门设计用于与 AI 编码工具（如 Cursor）集成，帮助开发者实现从规范定义到代码实现的完整工作流。

本文将详细介绍如何在 [Cursor](https://cursor.com/) 中安装和使用 [Spec-Kit](https://github.com/github/spec-kit)，并通过实际案例展示其强大的功能。

<!--more-->

## 什么是 Spec-Kit？

[Spec-Kit](https://github.com/github/spec-kit) 是一个开源工具包，旨在通过规范驱动开发方法，帮助开发者构建高质量的软件。它的核心理念是"规范优先"——先定义清晰的需求规范，再进行代码实现。

### 核心特性

- **四阶段核心工作流**：Specify（规范化）→ Plan（规划）→ Tasks（任务分解）→ Implement（实现）
- **可选阶段**：Constitution（项目原则）- 用于定义项目核心价值观和开发原则
- **辅助命令**：Clarify（澄清需求）、Analyze（一致性分析）- 提高开发质量
- **强制测试驱动开发（TDD）**：必须先生成测试，再生成实现代码
- **与 AI 工具无缝集成**：支持 Cursor、GitHub Copilot、Claude Code 等多种 AI 编码工具
- **规范优先开发**：确保每个功能都有清晰的需求定义

## 为什么选择 Spec-Kit？

### 与传统开发方式对比

| 方面 | 传统开发 | Spec-Kit 规范驱动开发 |
|------|----------|----------------------|
| **需求管理** | 口头沟通，容易产生误解 | 结构化文档，需求清晰明确 |
| **开发流程** | 直接编码，后期发现问题 | 先规范后实现，减少返工 |
| **测试覆盖** | 后期补充测试，覆盖率低 | 强制 TDD，测试先行 |
| **文档维护** | 文档与代码脱节 | 规范与实现同步更新 |
| **团队协作** | 依赖个人理解 | 基于统一规范协作 |
| **质量保证** | 依赖代码审查 | 多维度质量检查 |

### 与 AI 工具结合的优势

**传统 AI 编码**：

- AI 缺乏项目上下文
- 生成的代码质量不稳定
- 难以保证测试覆盖率
- 缺乏系统性的开发流程

**Spec-Kit + Cursor**：

- AI 基于清晰规范生成代码
- 强制 TDD 确保代码质量
- 系统化的开发流程
- 规范与实现保持一致

### 适用场景

**特别适合**：

- 中大型项目开发
- 团队协作项目
- 对代码质量要求高的项目
- 需要长期维护的项目
- 复杂业务逻辑的项目

**可能不适合**：

- 简单的原型开发
- 一次性脚本编写
- 学习性质的练习项目

## 安装前的准备

在开始安装 Spec-Kit 之前，请确保您的系统满足以下要求：

### 系统要求

- **操作系统**：Linux、macOS 或 Windows（推荐使用 WSL2）
- **AI 编码代理**：已安装并配置 Cursor
- **包管理器**：已安装 uv（Python 包管理工具）
- **运行时环境**：Python 3.11 及以上版本
- **版本控制工具**：已安装 Git

### 检查当前环境

```bash
# 检查 Python 版本
python3 --version

# 检查 Git 是否安装
git --version

# 检查 Cursor 是否安装
cursor --version
```

## 安装步骤

### 1. 安装 uv 包管理器

uv 是一个现代化的 Python 包管理工具，比 pip 更快更可靠。

#### macOS 安装

```bash
# 使用 Homebrew 安装
brew install uv

# 或者使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Linux 安装

```bash
# 使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者使用 pip 安装
pip install uv
```

#### Windows 安装

```powershell
# 使用 PowerShell 安装
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 安装 Spec-Kit

Spec-Kit 提供两种安装方式：

#### 方式一：全局安装（推荐）

```bash
# 安装到系统全局环境
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 安装后可直接使用
specify init my-project
specify check
```

#### 方式二：临时运行（无需安装）

```bash
# 直接运行，不安装到系统
uvx --from git+https://github.com/github/spec-kit.git specify init my-project
uvx --from git+https://github.com/github/spec-kit.git specify check
```

**选择建议**：

- **全局安装**：适合经常使用 Spec-Kit 的开发者
- **临时运行**：适合偶尔使用或测试的开发者

### 3. 验证安装

安装完成后，验证系统要求是否满足：

```bash
specify check
```

如果一切正常，您应该看到类似以下的输出：

```text
                      ███████╗██████╗ ███████╗ ██████╗██╗███████╗██╗   ██╗
                     ██╔════╝██╔══██╗██╔════╝██╔════╝██║██╔════╝╚██╗ ██╔╝
                     ███████╗██████╔╝█████╗  ██║     ██║█████╗   ╚████╔╝
                     ╚════██║██╔═══╝ ██╔══╝  ██║     ██║██╔══╝    ╚██╔╝
                     ███████║██║     ███████╗╚██████╗██║██║        ██║
                     ╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝╚═╝        ╚═╝

                       GitHub Spec Kit - Spec-Driven Development Toolkit

Checking for installed tools...

Check Available Tools
├── ● Git version control (available)
├── ● Claude Code CLI (not found)
├── ● Gemini CLI (not found)
├── ● Qwen Code CLI (not found)
├── ● Visual Studio Code (not found)
├── ● Visual Studio Code Insiders (not found)
├── ● Cursor IDE agent (available)
├── ● Windsurf IDE (not found)
├── ● Kilo Code IDE (not found)
├── ● opencode (not found)
├── ● Codex CLI (available)
└── ● Auggie CLI (not found)
```

### 4. specify init 命令参数详解

`specify init` 命令支持以下参数：

#### 基本语法

```bash
specify init [OPTIONS] <PROJECT_NAME>
```

#### 主要参数

| 参数 | 描述 | 使用场景 |
|------|------|----------|
| `<PROJECT_NAME>` | 项目名称（必需） | 创建新项目时指定名称 |
| `--here` | 在当前目录初始化 | 在现有目录中初始化 Spec-Kit |
| `--ai <assistant>` | 指定 AI 助手 | 选择支持的 AI 工具（claude/cursor/windsurf/copilot/gemini） |
| `--force` | 强制合并到非空目录 | 覆盖现有文件，谨慎使用 |
| `--no-git` | 跳过 Git 初始化 | 不创建 Git 仓库和分支 |
| `--debug` | 启用调试输出 | 排查问题时查看详细信息 |
| `--help` | 显示帮助信息 | 查看所有可用参数 |

#### 使用示例

**基本初始化**：

```bash
# 创建新项目
specify init my-project

# 在当前目录初始化
specify init --here
# 或
specify init .
```

**常用组合**：

```bash
# 指定 AI 助手
specify init my-project --ai claude

# 在当前目录初始化
specify init --here --ai cursor

# 强制合并到非空目录
specify init . --force --ai copilot

# 跳过 Git 初始化
specify init my-project --ai gemini --no-git
```

**系统检查**：

```bash
# 检查系统要求
specify check
```

#### 注意事项

- 项目名称会自动转换为小写，特殊字符替换为连字符
- 存在 Git 仓库时会自动创建并切换分支
- 使用 `--force` 会覆盖现有文件，请谨慎使用

## 在 Cursor 中配置 Spec-Kit

### 1. 项目结构

安装完成后，您的项目将具有以下结构：

```text
your-project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── scripts/
│   │   └── bash/
│   └── templates/
├── .cursor/
│   ├── commands/
│   │   ├── specify.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── implement.md
│   └── rules/
│       └── specify-rules.mdc
└── specs/
    └── [feature-specifications]
```

### 2. Cursor 命令配置

Spec-Kit 为 Cursor 提供了六个核心命令和一个可选命令：

- `/constitution` - 创建或更新项目原则（可选）
- `/specify` - 创建功能规范
- `/plan` - 生成实现计划
- `/tasks` - 分解任务
- `/implement` - 执行实现
- `/analyze` - 分析规范、计划和任务的一致性
- `/clarify` - 澄清需求中的模糊点

这些命令已经预配置在 `.cursor/commands/` 目录中。

## 使用 Spec-Kit 进行开发

Spec-Kit 采用规范驱动开发方法，通过四个核心阶段将需求转化为可工作的代码。让我们通过构建一个待办事项管理系统的实际案例来演示完整流程。

### 可选阶段：Constitution（项目原则）

**目的**：定义项目的核心价值观、开发原则和治理规则，为整个开发过程提供指导

#### 什么是项目原则？

项目原则是一份"宪法"文档，定义了：

- **核心开发原则**：如测试优先、代码质量、文档完整性等
- **技术约束**：技术栈选择、架构模式、性能标准等
- **工作流程**：代码审查、测试要求、部署流程等
- **治理规则**：如何修改原则、版本管理、合规要求等

#### 何时使用 Constitution？

- **新项目启动**：在开始开发前定义项目价值观
- **团队协作**：确保所有开发者遵循相同的原则
- **项目重构**：重新定义项目方向和标准
- **合规要求**：满足特定的开发规范或安全标准

#### 使用方法

**基本用法**：

```bash
/constitution 为待办事项管理系统创建项目原则
```

**详细指定原则**：

```bash
/constitution 为待办事项管理系统创建项目原则，包含：1.测试优先开发 2.代码质量保证 3.文档完整性 4.RESTful API设计 5.数据安全保护
```

**中文项目示例**：

```bash
/constitution 为电商系统创建项目原则，强调：1.测试覆盖率必须达到80%以上 2.采用微服务架构设计 3.API必须支持版本管理 4.所有敏感数据必须加密 5.必须实现完整的监控和日志
```

**更新现有原则**：

```bash
/constitution 更新项目原则，添加性能优化要求和微服务架构约束
```

#### 输出结果

AI 将生成 `.specify/memory/constitution.md` 文件，包含：

- **核心原则**：3-7个关键开发原则，每个都有明确的描述和理由
- **技术约束**：技术栈、架构模式、性能标准等要求
- **工作流程**：代码审查、测试、部署等流程规范
- **治理规则**：原则修改流程、版本管理、合规要求

#### 实际示例

**输入**：

```bash
/constitution 为电商系统创建项目原则，强调：1.测试覆盖率>80% 2.微服务架构 3.API版本管理 4.数据安全 5.性能监控
```

**输出**：生成包含以下内容的宪法文档：

- 测试覆盖率必须达到80%以上
- 采用微服务架构，服务间通过API通信
- API必须支持版本管理（v1, v2等）
- 所有数据必须加密存储和传输
- 必须实现完整的性能监控和日志记录

**生成的原则文档示例**：

```markdown
# 待办事项管理系统项目原则

## 核心原则

### 一、测试优先开发（不可妥协）
强制测试驱动开发：测试编写 → 用户确认 → 测试失败 → 然后实现；
严格执行红-绿-重构循环

### 二、代码质量保证
所有代码必须通过代码检查，遵循编码规范，并保持90%以上的测试覆盖率

### 三、文档完整性
每个公共API都必须有完整的文档和示例

### 四、安全设计
安全考虑必须从一开始就集成，而不是事后添加

## 技术约束
- Java 17+ 配合 Spring Boot 3.5+
- 开发环境使用H2数据库，生产环境使用PostgreSQL
- RESTful API设计，遵循OpenAPI 3.0规范
- 使用JUnit 5进行测试，Mockito进行模拟

## 开发工作流程
- 所有功能必须从失败的测试开始
- 所有变更都需要代码审查
- 合并前必须通过持续集成
- API变更需要更新文档

## 治理规则
项目原则超越所有其他实践；原则修改需要团队批准和文档记录
**版本**: 1.0.0 | **制定日期**: 2024-01-15 | **最后修改**: 2024-01-15
```

#### Constitution 使用技巧

**1. 原则数量控制**：

- 建议 3-7 个核心原则，太多会难以执行
- 每个原则都要有明确的验收标准

**2. 原则描述要具体**：

- ❌ 避免："代码质量要好"、"性能要优化"
- ✅ 推荐："代码覆盖率必须达到90%以上，所有公共方法必须有单元测试"、"API响应时间必须小于200ms"

**3. 定期更新原则**：

- 项目发展过程中可能需要调整原则
- 使用版本管理跟踪原则变更

**4. 团队共识**：

- 原则制定后需要团队讨论和确认
- 确保所有成员理解和认同这些原则

### 阶段 1：Specify（规范化）

**目的**：将自然语言描述的需求转化为结构化的规范文档

在 Cursor 中使用 `/specify` 命令描述功能需求：

```bash
/specify 构建一个待办事项管理系统，用户可以创建、查看、更新和删除待办事项。每个待办事项包含标题、描述、状态（待处理、进行中、已完成）和创建时间。系统需要支持按状态筛选和搜索功能。
```

**输出结果**：AI 将生成 `specs/001-项目名/spec.md` 文件，包含：

- 用户场景和测试用例
- 功能需求列表
- 关键实体定义
- 验收标准

### 阶段 1.5：Clarify（澄清需求）- 可选

**目的**：消除规范中的模糊点，确保需求清晰明确

如果规范中存在模糊点，使用 `/clarify` 命令进行澄清：

```bash
/clarify 澄清待办事项管理系统中用户角色和权限的模糊定义
```

**输出结果**：AI 会提出最多5个澄清问题，并将答案直接更新到规范文档中

### 阶段 2：Plan（规划）

**目的**：将规范转化为具体的技术实现方案

使用 `/plan` 命令提供技术栈和架构信息：

```bash
/plan 使用 Spring Boot 3 + Java 17，H2 数据库，Spring Data JPA，RESTful API 设计。需要实现 CRUD 操作、分页、搜索和状态管理功能。
```

**输出结果**：AI 将生成 `specs/001-项目名/plan.md` 文件，包含：

- 技术栈选择和理由
- 系统架构设计
- 数据模型定义
- API 接口规范
- 实现计划和时间安排

### 阶段 3：Tasks（任务分解）

**目的**：将规范和计划分解为具体的、可执行的开发任务

使用 `/tasks` 命令将规范分解为可执行的任务：

```bash
/tasks 根据规范和计划，生成具体的开发任务列表
```

**输出结果**：AI 将生成 `specs/001-项目名/tasks.md` 文件，包含：

- **设置任务**：项目初始化、依赖配置、环境搭建
- **测试任务**：单元测试、集成测试、端到端测试
- **核心任务**：实体创建、服务实现、控制器开发
- **集成任务**：数据库连接、API 测试、第三方集成
- **完善任务**：文档编写、性能优化、代码审查

### 阶段 3.5：Analyze（一致性分析）- 可选

**目的**：检查规范、计划和任务之间的一致性，发现潜在问题

在开始实现前，使用 `/analyze` 命令检查文档间的一致性：

```bash
/analyze 分析待办事项管理系统的规范、计划和任务之间的一致性
```

**输出结果**：AI 将生成详细的分析报告，包括重复需求检测、覆盖缺口分析、术语一致性验证等

### 阶段 4：Implement（实现）

**目的**：按照任务列表逐步实现功能，确保代码质量

使用 `/implement` 命令开始实现：

```bash
/implement 开始按照任务列表实现待办事项管理系统
```

**实现过程**：AI 将严格按照 TDD 原则：

1. 先编写失败的测试用例
2. 实现最小可用功能使测试通过
3. 重构代码提高质量
4. 进行集成测试验证功能
5. 验证每个任务完成情况

## 完整案例演示

让我们通过一个完整的案例来演示 Spec-Kit 的实际使用过程：

### 项目背景

假设我们要开发一个"个人博客管理系统"，包含文章管理、分类管理、评论系统等功能。

### 步骤 1：创建项目原则

```bash
/constitution 为个人博客管理系统创建项目原则，包含：1.测试覆盖率>85% 2.RESTful API设计 3.响应式前端 4.数据安全 5.SEO优化
```

### 步骤 2：定义功能规范

```bash
/specify 构建一个个人博客管理系统，用户可以发布、编辑、删除文章，管理文章分类，支持评论功能，具备搜索和标签功能，需要响应式设计
```

### 步骤 3：澄清需求

```bash
/clarify 澄清博客管理系统的用户权限管理和评论审核流程
```

### 步骤 4：制定技术方案

```bash
/plan 使用 Spring Boot 3.5 + React + PostgreSQL，采用微服务架构，支持 Docker 部署，集成 Redis 缓存
```

### 步骤 5：分析一致性

```bash
/analyze 检查博客管理系统的规范、计划和任务之间的一致性
```

### 步骤 6：分解任务

```bash
/tasks 根据规范和计划，生成博客管理系统的具体开发任务
```

### 步骤 7：开始实现

```bash
/implement 开始按照任务列表实现博客管理系统
```

### 预期成果

通过这个完整流程，您将获得：

- 清晰的项目原则文档
- 详细的功能规范说明
- 完整的技术实现方案
- 可执行的开发任务列表
- 高质量的代码实现

## 进阶使用技巧

### 1. 团队协作最佳实践

**统一规范模板**：

- 为团队创建标准的 Constitution 模板
- 制定统一的规范文档格式
- 建立代码审查检查清单

**版本控制策略**：

- 将 `.specify/` 目录纳入版本控制
- 使用分支管理不同功能的规范
- 定期同步和更新规范文档

### 2. 与现有项目集成

**渐进式采用**：

- 从新功能开始使用 Spec-Kit
- 逐步将现有功能迁移到规范驱动开发
- 保持与现有开发流程的兼容性

**工具链集成**：

- 与 CI/CD 流水线集成
- 与项目管理工具（如 Jira、Trello）结合
- 与代码质量工具（如 SonarQube）配合

### 3. 性能优化建议

**规范文档管理**：

- 定期清理过时的规范文档
- 使用标签和分类组织规范
- 建立规范文档的归档策略

**AI 提示优化**：

- 提供清晰、具体的需求描述
- 使用结构化的输入格式
- 避免过于复杂或模糊的指令

## 常见问题解决

### 常见问题

**uv 安装失败**：

```bash
python3 --version  # 检查 Python 版本（需要 3.11+）
pip install uv     # 使用 pip 作为备选方案
```

**Spec-Kit 命令不可用**：

```bash
echo $PATH                    # 检查环境变量
source ~/.bashrc             # 重新加载 shell 配置
uv tool list                 # 查看已安装的工具
```

**Cursor 中看不到命令**：

- 确保项目根目录包含 `.cursor/commands/` 文件夹
- 重启 Cursor IDE
- 检查命令文件格式是否正确（Markdown 格式）

**AI 无法理解规范描述**：

- 使用具体的用户场景而非技术术语
- 提供足够的业务上下文信息
- 使用标准的业务领域术语
- 先运行 `/clarify` 命令澄清模糊点

### 故障排除

**规范生成失败**：

- 检查网络连接和 AI 服务状态
- 验证输入描述的完整性和清晰度
- 查看 Cursor 的日志文件获取详细错误信息

**命令执行缓慢**：

- 确保使用最新版本的 Spec-Kit
- 检查系统资源使用情况
- 考虑使用更具体的描述减少 AI 处理时间

## 总结

Spec-Kit 与 Cursor 的结合为现代软件开发提供了全新的规范驱动开发体验。通过四个核心阶段——Specify（规范）、Plan（规划）、Tasks（任务分解）、Implement（实现），以及可选的 Constitution（项目原则）、Clarify（澄清需求）、Analyze（一致性分析）命令，开发者可以：

1. **确保需求清晰明确**：通过结构化规范避免需求理解偏差
2. **提高代码质量和可维护性**：强制 TDD 确保测试覆盖率
3. **减少返工和沟通成本**：规范优先的方法减少后期修改
4. **实现真正的测试驱动开发**：先测试后实现，确保代码质量

立即开始使用 Spec-Kit，体验规范驱动开发的强大威力！通过清晰的规范定义和系统化的实现流程，让您的软件开发更加高效和可靠。

## 参考资源

- [Spec-Kit GitHub 仓库](https://github.com/github/spec-kit)
- [Cursor 官方文档](https://cursor.sh/docs)
- [uv 包管理器文档](https://docs.astral.sh/uv/)
- [测试驱动开发最佳实践](https://martinfowler.com/articles/practical-test-pyramid.html)
- [规范驱动开发方法论](https://en.wikipedia.org/wiki/Specification_by_example)

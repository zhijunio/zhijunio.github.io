---
title: "agentic-expense-manager：Spring Boot Agentic 开发脚手架"
date: 2026-05-19 14:20:00+08:00
slug: agentic-expense-manager-learning-guide
tags: [ "java", "spring-boot", "spring-modulith","sdd" ]
cover: "cover.webp"
description: "sivaprasadreddy/agentic-expense-manager 不是成品记账 App，而是 Spring Boot 4 + Modulith + 29 条 UC 需求清单的 Agent 试验场。本文按目录拆解每个文件能学什么，并归纳八类学习维度。"
---

最近在 GitHub 上看到 [sivaprasadreddy/agentic-expense-manager](https://github.com/sivaprasadreddy/agentic-expense-manager)。README 写得很直白：这是一个 **Expense Manager 脚手架**，用来对比 [OpenSpec](https://github.com/Fission-AI/OpenSpec)、[BMAD](https://docs.bmad-method.org/)、[sdd-skills](https://github.com/sivaprasadreddy/sdd-skills)、[AI Unified Process](https://unifiedprocess.ai/)、[mattpocock/skills](https://github.com/mattpocock/skills) 等 **Agentic / SDD** 工作流——而不是一个功能齐全的记账产品。

我按「逐文件能学什么」把仓库翻了一遍，再按架构、工程、Agent 协作等维度做了归类。若你正在用 Claude Code、Cursor 或 Copilot 做 **Spec-Driven** 的 Java 项目，这篇可以当作导读。

## 一句话定性

**不是**「抄一个 FinTech 成品」，**而是**「带需求清单 + 模块化骨架 + Agent 操作手册」的练功房。

- **已完成**：UC-001～004（注册、登录、登出、基本资料）
- **进行中**：UC-027（Dashboard）
- **未实现**：UC-005～026、028～029（账户、分类、交易、预算、报表等）

需求状态都写在 `docs/requirements.md` 里，这是仓库最有价值的非代码资产。

## 全局结构

```text
docs/（需求与愿景）
    ↓ 驱动实现顺序
src/main/java/dev.sivalabs.expman/
    ├── Application + config/     # 启动与横切
    ├── common/                   # 开放模块：事件、分页、异常
    └── users/                    # 第一个业务模块（Modulith 边界）
            ├── UsersAPI          # 模块对外门面
            ├── domain/           # 实体、服务、仓储
            └── web/              # Thymeleaf 控制器
src/main/resources/               # 配置、Flyway、模板
src/test/                         # 模块化测试 + Testcontainers
AGENTS.md / CLAUDE.md             # 给 AI 的操作手册
pom.xml + compose.yaml + Taskfile.yml
```

![agentic-expense-manager 仓库结构导读图](01-framework-repo-map.webp)

建议阅读顺序：**README → requirements.md → ModularityTest → users 模块 → 测试与 CI → AGENTS.md**。

## 按目录拆解：每个文件能学什么

### 仓库根：愿景、Agent 入口、运行编排

| 文件 | 可学什么 |
| --- | --- |
| `README.md` | 项目定位、可试的 SDD 工具链、前置条件、技术栈与如何运行 |
| `AGENTS.md` | **AI Agent 操作手册**：构建、测试、格式化；Agent 应先读再改代码 |
| `CLAUDE.md` | 指向 `AGENTS.md`；多 Agent 工具共用说明的薄封装写法 |
| `compose.yaml` | 本地 **Postgres 18** + **Mailpit**（SMTP / Web UI） |
| `Taskfile.yml` | `format → verify → build_image`；跨平台 `mvnw` |
| `.sdkmanrc` | 锁定 **Java 25-tem**、Maven 3.9.15 |
| `renovate.json` | 依赖自动升级样板 |
| `mvnw` / `.mvn/wrapper/` | 无全局 Maven 也能构建，与 CI 一致 |

### 文档层：Spec-Driven 的单一事实来源

| 文件 | 可学什么 |
| --- | --- |
| `docs/project.md` | 产品愿景：目标用户、Transaction / Account / Category / Budget 等概念 |
| `docs/requirements.md` | **29 条 UC**，含 Status 与验收标准；Agent 按编号认领，避免 scope 漂移 |

### 构建与质量：`pom.xml`

- **Spring Boot 4.0.6** + **Java 25** + **Spring Modulith 2.0.6**
- 栈：WebMVC、Validation、Mail、Thymeleaf、JPA、Flyway、Security
- `spring-boot-docker-compose`：开发时自动拉起 compose
- 测试：**Testcontainers**（Postgres + Mailpit）、Modulith Test
- **JaCoCo**：`verify` 阶段行覆盖率 **≥ 50%**
- **Spotless**：Palantir Java Format（`./mvnw spotless:apply`）
- **build-image**：可构建容器镜像

### CI：`.github/workflows/maven.yml`

- 分支：`main`、`feat/*`、`fix/*`
- **`paths-ignore`**：改 md/docs 不跑构建，文档与代码流水线分离
- `./mvnw -ntp verify`：与本地一致

### 应用入口与 `config` 包

| 文件 | 可学什么 |
| --- | --- |
| `Application.java` | `@EnableAsync`、`@EnableScheduling`、`@EnableResilientMethods` 等扩展点 |
| `AppProperties.java` | 类型安全的 `app.*` 配置 |
| `SecurityConfig.java` | BCrypt、`DaoAuthenticationProvider`、角色层级 ADMIN > USER |
| `WebSecurityConfig.java` | 表单登录；`/login`、`/register` 公开；`/admin/**` 需 ADMIN |
| `GlobalExceptionHandler.java` | 异常映射到 Thymeleaf 错误页（403/404/500） |
| `FlywayConfig.java` | **`@Profile("local")`**：迁移失败时 clean 再 migrate（勿用于生产） |

### `common` 模块（Modulith OPEN）

| 文件 | 可学什么 |
| --- | --- |
| `package-info.java` | `@ApplicationModule(type = OPEN)`：开放模块，供其他模块依赖 |
| `DomainEvent.java` | 领域事件标记接口 |
| `AppEventPublisher.java` | 统一事件发布入口 |
| `PagedResult.java` | 将 Spring Data `Page` 转为 **1-based 页码** 的 record，供列表页复用 |
| `ResourceNotFoundException` 等 | 应用层异常与全局处理配合 |

`application.properties` 里还有 Modulith JDBC 事件配置，为跨模块事件持久化预留。

### `users` 模块：第一个完整垂直切片

| 文件 | 可学什么 |
| --- | --- |
| `UsersAPI.java` | **模块对外 API**；其他模块只通过它查用户，不直接碰 Repository |
| `User.java` | JPA 实体、序列主键、角色枚举 |
| `UserService.java` | `CreateUserCmd`、密码编码、事务、`ResourceNotFoundException` |
| `UserMapper.java` | 对外 DTO **不含 password**；登录场景单独 `toUserDtoWithPassword` |
| `UserAuthController.java` | `@Valid` + `BindingResult`；`RedirectAttributes` flash 消息 |
| `domain/models/package-info.java` | `@NamedInterface("user-models")`：控制 Modulith 暴露面 |
| `SecurityUserDetailsService.java` | 接入 Spring Security 的适配 |

![users 模块的垂直切片与边界](02-framework-users-slice.webp)

Web 层是 **Thymeleaf SSR**，不是前后端分离；适合 Agent 一次改完一条 UC 的闭环。

### 资源与模板

| 文件 | 可学什么 |
| --- | --- |
| `application.properties` | `ddl-auto=validate`、`open-in-view=false`、Docker Compose 生命周期 |
| `db/migration/V001__create_users_table.sql` | Flyway 权威 schema；种子用户与 BCrypt 哈希 |
| `templates/auth/*.html` | 登录、注册表单 |
| `templates/dashboard/*.html` | 登录后布局（Dashboard 进行中） |
| `templates/error/*.html` | 与 `GlobalExceptionHandler` 对应 |

### 测试层

| 文件 | 可学什么 |
| --- | --- |
| `ModularityTest.java` | `ApplicationModules.verify()`：校验模块边界，防随意跨包 import |
| `TestcontainersConfiguration.java` | `@ServiceConnection` 注入 Postgres + Mailpit |
| `BaseIT.java` | `@SpringBootTest` + `MockMvcTester`（Boot 4 测试 API） |
| `UserAuthControllerTests` 等 | Web 集成测试样板 |

![Agentic 与 SDD 的工程闭环](03-flow-agentic-loop.webp)

## 八类学习维度（系统归纳）

### 1. Agentic / SDD 工作流

需求即 backlog（`requirements.md` 的 UC + Status）、Agent 操作手册（`AGENTS.md`）、刻意留白的大量 NOT_IMPLEMENTED——逼你选一种 SDD 工具把下一条 UC 做起来。

### 2. 模块化架构（Spring Modulith）

`users` / `common`(OPEN) / `config`；对外门面 `UsersAPI`；`ModularityTest` + `@ApplicationModule` / `@NamedInterface`；`DomainEvent` 与 JDBC 事件表为跨模块解耦预留。

### 3. 分层与 DDD 轻量实践

Controller + Request DTO → `UserService` + Cmd → 实体 + 异常 → Repository；命令与查询模型分离。

### 4. Spring Security 与会话型 Web

表单登录、角色层级、路径授权；与 Thymeleaf、flash 结合的注册流。

### 5. 数据与迁移

Flyway 单一真相；JPA `validate`；Postgres 序列主键、乐观锁字段（表结构已预留 `version`）。

### 6. 可验证性与工程纪律

Testcontainers、JaCoCo 门禁、Spotless、CI 与本地命令一致。

### 7. 可运行性与 DevEx

Docker Compose、Taskfile、Mailpit 本地验邮件。

### 8. 产品域知识

`docs/project.md` 里 Account / Category / Budget / Dashboard 等概念已定义，适合练「先读需求再写代码」的 Agent 任务。

## 按角色怎么读

| 你是谁 | 建议重点 | 可暂时跳过 |
| --- | --- | --- |
| Java 后端 | Modulith、`UsersAPI`、Security、Flyway、IT | Thymeleaf 细节 |
| AI 工程 / SDD | `requirements.md`、`AGENTS.md`、UC 状态、JaCoCo | 已完成的 UC-001～004 逐行读 |
| 全栈 SSR | templates + Controller + flash | Modulith 事件 JDBC |
| 想抄成品记账系统 | **不适合本仓库** | — |

## 用 Agent 继续开发：推荐切片

1. 打开 `docs/requirements.md`，认领 **UC-005**（创建财务账户）
2. 新建 `accounts` 模块（仿 `users`：`AccountsAPI`、domain、web、Flyway `V002__...`）
3. 跑 `./mvnw clean verify`，满足 JaCoCo
4. 把 requirements 里对应 Status 改为 COMPLETED

![认领下一条 UC 的执行路径](04-flow-next-uc.webp)

仓库教的是 **「在约束下用 Agent 交付下一条 UC」**，不是复制一个 FinTech。

## 局限

- 业务完成度低，29 条 UC 绝大多数未实现
- **Java 25**、**Spring Boot 4**，环境要对齐
- SSR 为主；若团队是 React + REST，参考价值在架构与 SDD
- `FlywayConfig` 的 clean 仅 `local` profile，切勿照搬生产

## 小结

[sivaprasadreddy/agentic-expense-manager](https://github.com/sivaprasadreddy/agentic-expense-manager) 把 **需求文档、模块边界、测试门禁、Agent 命令** 捆在一起，是一个很干净的 **Agentic Java 练功房**。若你已经在博客或 second-brain 里折腾 Hermes / SDD，不妨 fork 一份，从 UC-005 开始让 Agent 交第一份「真业务」PR。

---

**参考链接**

- 仓库：<https://github.com/sivaprasadreddy/agentic-expense-manager>
- 作者同系列的 sdd-skills：<https://github.com/sivaprasadreddy/sdd-skills>
- Spring Modulith 文档：<https://docs.spring.io/spring-modulith/reference/>

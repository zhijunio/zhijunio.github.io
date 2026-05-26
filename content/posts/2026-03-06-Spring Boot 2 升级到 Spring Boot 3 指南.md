---
title: "Spring Boot 2 升级 3 实战：OpenRewrite 自动化迁移 + AI Agent 辅助"
date: 2026-03-06 07:50:00+08:00
slug: spring-boot-2-to-3-upgrade-guide
tags: [ "spring-boot" ]
description: "本文介绍如何使用 OpenRewrite 自动化迁移 Spring Boot 2.7.x 应用到 Spring Boot 3.x，以及如何使用 spring-boot-2-to-3 这个 AI Agent Skill 来简化升级流程。"
---

最近在升级一个老项目，需要把 Spring Boot 2.7.x 迁移到 Spring Boot 3.5.x。这个过程中踩了不少坑，也学到了一些好用的工具，这里记录一下经验。

<!--more-->

## 为什么要升级到 Spring Boot 3

Spring Boot 3 带来了很多变化：

- **Jakarta EE 10 支持**：从 `javax.*` 迁移到 `jakarta.*` 命名空间（Spring Boot 3.0 采用 Servlet 6.0、JPA 3.1 等）
- **Java 17+ 要求**：最低 Java 17，推荐 Java 21
- **Spring Framework 6**：底层框架升级
- **Hibernate 6**：ORM 层变化
- **更好的 GraalVM 支持**：原生镜像支持

虽然升级工作量不小，但为了长期维护和新特性，还是值得的。

## 使用 OpenRewrite 迁移

### 什么是 OpenRewrite

**OpenRewrite** 是一个代码重构工具，可以自动处理大量重复性的代码修改。对于 Spring Boot 升级这种大工程特别有用。

它的工作原理是定义 "recipes"（配方），描述如何转换代码。比如把 `javax.*` 改成 `jakarta.*`，或者更新依赖版本。

### OpenRewrite Recipes

从 Spring Boot 2.7.x 升级到 3.5.x 时，只需使用下面这一条组合配方即可，无需再单独配置其他迁移配方。

| 配方全名 | 说明 |
|----------|------|
| `org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5` | 组合配方，见下方「配方组成」 |

**配方组成**（与 [OpenRewrite 官方 Definition](https://docs.openrewrite.org/recipes/java/spring/boot3/upgradespringboot_3_5-community-edition) 一致，即该页面所列全部子配方）：

1. **Migrate to Spring Boot 3.4**：先升级到 3.4（其内部再链式执行 3.0→3.1→3.2→3.3→3.4，含 javax→jakarta、API 与配置属性等）
2. **Migrate Spring Boot properties to 3.5**：配置属性迁移到 3.5
3. **Migrate to Spring Cloud 2025**：若项目使用 Spring Cloud，升级到 2025 对应版本
4. **Update Prometheus Pushgateway Dependency Coordinates**：Prometheus Pushgateway 依赖坐标更新
5. **Migrate to Spring Security 6.5**：Spring Security 迁移到 6.5（如 `WebSecurityConfigurerAdapter` → `SecurityFilterChain`）
6. **Upgrade dependency versions**：`org.springframework.boot:*` 依赖统一升到 3.5.x；`spring-boot-dependencies` BOM 升到 3.5.x
7. **Upgrade Maven plugin / parent**：`spring-boot-maven-plugin`、`spring-boot-starter-parent` 版本升到 3.5.x
8. **Gradle**：若用 Gradle，`org.springframework.boot` 插件版本升到 3.5.x

因此博客中的「升级场景」与实战示例覆盖的是上述组合后的**效果**（依赖升级、javax→jakarta、配置属性、Security、Cloud、Prometheus 等）；**完整、权威的子配方列表与每一项的变更细节**以官方文档 [Migrate to Spring Boot 3.5 (Community Edition)](https://docs.openrewrite.org/recipes/java/spring/boot3/upgradespringboot_3_5-community-edition) 为准。

### 使用 Maven 运行 OpenRewrite

在项目中添加插件（`UpgradeSpringBoot_3_5` 配方来自 **rewrite-spring**，需同时声明插件与配方依赖）：

```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>6.30.0</version>
  <configuration>
    <activeRecipes>
      <recipe>org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5</recipe>
    </activeRecipes>
  </configuration>
  <dependencies>
    <dependency>
      <groupId>org.openrewrite.recipe</groupId>
      <artifactId>rewrite-spring</artifactId>
      <version>6.25.1</version>
    </dependency>
  </dependencies>
</plugin>
```

版本对应关系（可查阅 [OpenRewrite 最新版本](https://docs.openrewrite.org/reference/latest-versions-of-every-openrewrite-module) 获取当前推荐版本）：

| 组件 | 说明 | 示例版本 |
|------|------|----------|
| `rewrite-maven-plugin` | Maven 插件 | 6.30.0 |
| `rewrite-spring` | 含 UpgradeSpringBoot_3_5 等 Spring 配方 | 6.25.1 |

执行迁移：

```bash
# 直接运行并应用变更（首次可能较慢，需下载依赖、解析工程，约几分钟）
mvn rewrite:run
```

若长时间无输出、像卡住，可尝试：

1. **增加 JVM 内存**（大项目建议）：`export MAVEN_OPTS="-Xmx2g"` 后再执行 `mvn rewrite:run`
2. **先预览再应用**：`mvn rewrite:dryRun` 查看将做的变更，确认无误后再 `mvn rewrite:run` 应用
3. **看详细日志**：`mvn rewrite:run -e` 或 `mvn rewrite:run -X` 观察进度

### 自定义 OpenRewrite Recipes

在默认配方不满足需求时，可以**组合现有配方**或**编写自己的配方**，再用 Maven 插件执行。

#### 方式一：声明式 YAML 配方（推荐入门）

不写 Java 代码，用 YAML 描述「组合哪些已有配方」或「调用哪些声明式转换」。适合在现有配方基础上做定制。

- **放置位置（二选一）**：
  - **仅当前项目**：在项目根目录创建 `rewrite.yml`，Maven 插件会自动加载。
  - **打成 JAR 分发**：在依赖包的 `META-INF/rewrite/*.yml` 中放置，供多项目复用。
- **基本结构**：`type: specs.openrewrite.org/v1beta/recipe`，`name` 用反向域名（勿用 `org.openrewrite` 命名空间），`recipeList` 中列出要执行的子配方或声明式步骤。
- **示例**：在 `UpgradeSpringBoot_3_5` 之后再跑一个自定义步骤（如替换包名），可在 `rewrite.yml` 里定义一个组合配方，`recipeList` 里先写 `org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5`，再写你的配方名或内联声明。

详见 [Authoring declarative YAML recipes](https://docs.openrewrite.org/running-recipes/popular-recipe-guides/authoring-declarative-yaml-recipes) 与 [YAML format reference](https://docs.openrewrite.org/reference/yaml-format-reference)。

#### 方式二：Java 配方（复杂逻辑）

需要基于 AST 做复杂判断或改写时，可编写 Java 配方：继承 `org.openrewrite.Recipe`，实现 `getVisitor()` 返回 `JavaIsoVisitor`（或其它语言的 Visitor），用 `@Option` 暴露可配置项。开发环境建议 JDK 21 + [rewrite-recipe-starter](https://github.com/moderneinc/rewrite-recipe-starter)。

详见 [Writing a Java refactoring recipe](https://docs.openrewrite.org/authoring-recipes/writing-a-java-refactoring-recipe)。

#### 在 Maven 中启用自定义配方

- **本地 YAML**：在项目根目录放好 `rewrite.yml` 并定义好 `name`，在 `pom.xml` 的 `rewrite-maven-plugin` 的 `activeRecipes` 里加上该 `name`，执行 `mvn rewrite:run` 即可。
- **自定义 JAR**：将包含 `META-INF/rewrite/*.yml` 或 Java 配方的 JAR 作为插件的 `dependency` 引入，再在 `activeRecipes` 中填写配方全名。

更多组合与覆盖方式见 [How to customize recipes](https://docs.openrewrite.org/running-recipes/customize-recipe)。

[Spring Boot 2 升 3：两条命令搞定 95%，AI 收尾](https://atbug.com/openrewrite-recipe-first-spring-boot-2-to-3-migration/) 这篇文章中提到了自定义的 Recipes，对应仓库在 [spring-boot-migration-toolkit](https://github.com/addozhang/spring-boot-migration-toolkit)。其中定义了一个 common-lib-migration.yml：

```yaml title="common-lib-migration.yml"
---
type: specs.openrewrite.org/v1beta/recipe
name: com.example.recipes.FixHttpComponents5VersionMismatch
displayName: Fix Apache HttpComponents 5 version mismatch
description: >
  Aligns httpcore5 version with httpclient5 5.4.x.
  httpclient5 5.4.x requires httpcore5 5.3.x; this recipe sets httpcore5.version to 5.3.4.
recipeList:
  - org.openrewrite.maven.ChangePropertyValue:
      key: httpcore5.version
      newValue: 5.3.4
      addIfMissing: true

---
type: specs.openrewrite.org/v1beta/recipe
name: com.example.recipes.MigrateCommonLibV2
displayName: Migrate com.example.common-lib from v1 to v2
description: Migrates deprecated ApiResponse to ApiResult, @RequireLogin to @Authenticated, and StringUtil to Spring StringUtils.
recipeList:
  # 1. ApiResponse.success(data) → ApiResult.ok(data)
  #    ChangeMethodName runs first while type is still ApiResponse
  - org.openrewrite.java.ChangeMethodName:
      methodPattern: com.example.common.response.ApiResponse success(..)
      newMethodName: ok
  # 2. ApiResponse.fail(msg) → ApiResult.error(msg)
  - org.openrewrite.java.ChangeMethodName:
      methodPattern: com.example.common.response.ApiResponse fail(..)
      newMethodName: error
  # 3. Change type ApiResponse → ApiResult (runs after method renames)
  - org.openrewrite.java.ChangeType:
      oldFullyQualifiedTypeName: com.example.common.response.ApiResponse
      newFullyQualifiedTypeName: com.example.common.response.ApiResult
  # 4. @RequireLogin → @Authenticated
  - org.openrewrite.java.ChangeType:
      oldFullyQualifiedTypeName: com.example.common.annotation.RequireLogin
      newFullyQualifiedTypeName: com.example.common.annotation.Authenticated
  # 5. StringUtil → Spring's StringUtils (class reference migration)
  #    Note: isEmpty semantics differ (StringUtil.isEmpty vs StringUtils.hasText),
  #    so only the class reference is migrated here. Manual review recommended.
  - org.openrewrite.java.ChangeType:
      oldFullyQualifiedTypeName: com.example.common.util.StringUtil
      newFullyQualifiedTypeName: org.springframework.util.StringUtils
```



### OpenRewrite 迁移实战

#### 0. 示例项目

[spring-boot-2-to-3-demo](https://github.com/zhijunio/spring-boot-2-to-3-demo) 是一个用于练习升级的 Maven 示例项目。项目信息：

- **Spring Boot**: 2.7.18
- **Java**: 11
- **构建工具**: Maven

包含的迁移场景

| 场景                                                   | 位置                                                         |
| ------------------------------------------------------ | ------------------------------------------------------------ |
| **javax → jakarta**                                    | `Item.java` (javax.persistence), `LoggingInterceptor.java` (javax.servlet), `DemoController.java` (javax.validation) |
| **@Autowired 单构造函数**                              | `DemoController` 构造函数                                    |
| **@RequestMapping(method=)** / **@PathVariable("id")** | `DemoController`                                             |
| **HttpStatus** / **APPLICATION_JSON_UTF8_VALUE**       | `DemoController`, `GlobalExceptionHandler`                   |
| **WebSecurityConfigurerAdapter**                       | `SecurityConfig`                                             |
| **WebMvcConfigurerAdapter**                            | `WebMvcConfig`                                               |
| **AsyncConfigurerSupport**                             | `AsyncConfig`                                                |
| **JUnit 4**                                            | `DemoControllerTest`                                         |
| **Legacy config properties**                           | `application.properties`                                     |
| **API docs**                                           | springdoc-openapi 1.8.0 → 2.x                                |
| **JPA / Hibernate**                                    | `Item` entity, `ItemRepository`                              |
| **Flyway**                                             | `db/migration/V1__init.sql`                                  |

项目结构

```text
spring-boot-2-to-3-demo/
├── pom.xml
├── Dockerfile
├── src/main/java/com/example/demomigration/
│   ├── DemoApplication.java
│   ├── config/
│   │   ├── AsyncConfig.java       # AsyncConfigurerSupport
│   │   ├── SecurityConfig.java    # WebSecurityConfigurerAdapter
│   │   └── WebMvcConfig.java      # WebMvcConfigurer
│   ├── persistence/
│   │   ├── Item.java              # javax.persistence
│   │   └── ItemRepository.java
│   └── web/
│       ├── DemoController.java
│       ├── GlobalExceptionHandler.java
│       └── LoggingInterceptor.java
├── src/main/resources/
│   ├── application.properties
│   └── db/migration/V1__init.sql
└── src/test/.../DemoControllerTest.java  # JUnit 4
```

启动后访问

| 描述         | URL                                        |
| ------------ | ------------------------------------------ |
| 公共 API     | `<http://localhost:8080/api/public/items>` |
| OpenAPI 规范 | `<http://localhost:8080/v3/api-docs>`      |
| Swagger UI   | `<http://localhost:8080/swagger-ui.html>`  |
| Actuator     | `<http://localhost:8080/manage/actuator>`  |

> 注意：`application.properties` 中设置了 `management.context-path=/manage`（Boot 3 中改为 `management.endpoints.web.base-path=/manage`，用于设置 actuator 端点前缀）

下面以 **spring-boot-2-to-3-demo** 为例，从零演示如何用 OpenRewrite 完成 2.7 → 3.5 的迁移。

#### 1. 克隆示例项目并确认环境

```bash
git clone https://github.com/zhijunio/spring-boot-2-to-3-demo.git
cd spring-boot-2-to-3-demo
```

要求本机已安装 **JDK 17 或以上**（OpenRewrite 插件运行需要），Maven 3.6+。可用 `java -version` 和 `mvn -v` 确认。

#### 2. 基线验证（迁移前务必通过）

在改任何东西之前，先确认项目能编译、测试通过：

```bash
mvn -q compile test
```

若有测试失败，先修复再继续；否则迁移后的变更会与既有问题混在一起，难以排查。

#### 3. 在 pom.xml 中添加 OpenRewrite 插件

在 `pom.xml` 的 `<build><plugins>` 内增加 `rewrite-maven-plugin`（若已有其他插件，与它们并列即可）：

```xml
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>6.30.0</version>
  <configuration>
    <activeRecipes>
      <recipe>org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_5</recipe>
    </activeRecipes>
  </configuration>
  <dependencies>
    <dependency>
      <groupId>org.openrewrite.recipe</groupId>
      <artifactId>rewrite-spring</artifactId>
      <version>6.25.1</version>
    </dependency>
  </dependencies>
</plugin>
```

保存后执行一次 `mvn -q compile`，让 Maven 下载插件和 rewrite-spring 依赖（首次可能稍慢）。

#### 4. 预览变更（推荐先执行）

不写盘、只查看会改哪些文件，可执行：

```bash
mvn rewrite:dryRun
```

输出中会列出将要修改的源文件及大致变更类型（例如 dependency 升级、import 替换等）。确认无误后再进行下一步。

#### 5. 执行迁移并写回磁盘

```bash
mvn rewrite:run
```

首次运行会解析整个项目、下载配方依赖，可能需要 1～3 分钟，控制台会陆续有日志。结束后，`pom.xml` 和大量 Java/配置文件会被改写，例如：

- **pom.xml**：`spring-boot-starter-parent` 变为 3.5.x，Java 版本可能被改为 17，springdoc、flyway 等依赖版本升级
- **Java 源码**：`javax.persistence`、`javax.servlet`、`javax.validation` 等 import 改为 `jakarta.*`；`WebSecurityConfigurerAdapter` 被替换为 `SecurityFilterChain` 等
- **application.properties**：如 `management.context-path` 改为 `management.endpoints.web.base-path`

可用 `git diff` 查看具体 diff。

#### 6. 迁移后验证

```bash
mvn -q compile test
```

若通过，再启动应用做一次人工检查：

```bash
mvn spring-boot:run
```

然后访问 <http://localhost:8080/api/public/items>、<http://localhost:8080/swagger-ui.html>、<http://localhost:8080/manage/actuator> 等，确认接口与 Actuator 正常。

#### 7. 若出现编译或测试失败

OpenRewrite 已处理大部分机械替换，但个别 API 或配置可能需人工收尾，例如：

- 某些废弃 API 的替代写法需手改
- 若仍报 `javax` 相关找不到符号，检查是否有多模块或未参与编译的源码，补全 import 或再跑一次 `rewrite:run`
- 测试里若有 Mock 或反射用到旧类名，需按报错位置逐一改为新包名/新类

处理完后再次执行 `mvn compile test` 直至通过。

按以上步骤，即可在 **spring-boot-2-to-3-demo** 上完整走通一次 2.7 → 3.5 的 OpenRewrite 迁移；自己的项目只需把「克隆示例」换成现有代码库，其余流程相同。

## 使用 Spring Boot Migrator 迁移

[Spring Boot Migrator (SBM)](https://github.com/spring-projects-experimental/spring-boot-migrator) 是 Spring 官方实验性项目，同样能完成 2.7 → 3.x 的自动化升级。它底层兼容 OpenRewrite，提供 **一键升级 JAR**、**CLI** 和 **Web UI**，适合不想改 pom、或希望用图形化/交互式流程的场景。

### 环境与限制

| 项目 | 说明 |
|------|------|
| **JDK** | 必须 **JDK 17**（SBM 运行环境，与项目当前用的 Java 版本无关） |
| **构建工具** | 仅支持 **Maven** 项目 |
| **不支持** | Gradle、Kotlin 项目暂不支持 |

### 方式一：Spring Boot Upgrade JAR

适合「一条命令、自动扫项目并应用迁移」的用法。

#### 1. 下载 JAR

在 [SBM Releases](https://github.com/spring-projects-experimental/spring-boot-migrator/releases) 中下载 **spring-boot-upgrade.jar**（或当前页标注的升级用 jar 名称），放到本地目录，例如 `~/tools/`。

#### 2. 执行升级命令

在终端执行（将 `<项目路径>` 换成你的 Maven 项目根目录绝对路径或相对路径）：

```bash
java -jar --add-opens java.base/sun.nio.ch=ALL-UNNAMED --add-opens java.base/java.io=ALL-UNNAMED spring-boot-upgrade.jar <项目路径>
```

**示例**（以本文示例项目为例）：

```bash
git clone https://github.com/zhijunio/spring-boot-2-to-3-demo.git

# 在项目外执行（或把 jar 路径写全）
java -jar --add-opens java.base/sun.nio.ch=ALL-UNNAMED --add-opens java.base/java.io=ALL-UNNAMED ~/tools/spring-boot-upgrade.jar spring-boot-2-to-3-demo
```

Windows 下路径需转义或使用正斜杠，例如：`C:\\my\\app` 或 `C:/my/app`。

#### 3. 查看结果

工具会扫描项目并应用迁移配方，修改完成后可在项目目录执行 `git diff` 查看变更，再运行 `mvn compile test` 做验证。

### 方式二：SBM CLI

适合希望「先扫描、再按需选择要执行的迁移步骤」的用法。

#### 1. 下载并启动 CLI

从 [SBM Releases](https://github.com/spring-projects-experimental/spring-boot-migrator/releases) 下载 **spring-boot-migrator.jar**，启动交互式 CLI：

```bash
java -jar spring-boot-migrator.jar
```

启动后会进入 SBM 的 shell，可输入 `help` 查看命令列表。

#### 2. 扫描项目

在 SBM shell 中执行（将路径换成你的 Maven 项目根目录）：

```bash
scan <项目路径>
```

例如：

```bash
scan /path/to/spring-boot-2-to-3-demo
```

或 Windows：

```bash
scan C:/my/spring-boot-2-to-3-demo
```

扫描完成后会列出可用的迁移配方（recipe）列表。

#### 3. 应用配方

根据列表中的名称，选择要执行的迁移并执行：

```bash
apply <配方名>
```

例如（以官方文档示例为准，名称可能随版本变化）：

```bash
apply initialize-spring-boot-migration
```

可多次执行不同的 `apply` 完成多步迁移。完成后退出 CLI，在项目目录下用 `mvn compile test` 和 `git diff` 做验证。

#### 4. 常用命令

- `help`：查看帮助
- `scan <path>`：扫描项目并列出可用配方
- `apply <recipe>`：应用指定配方

### 与 OpenRewrite 方式的对比

| 对比项 | OpenRewrite（本文主流程） | Spring Boot Migrator (SBM) |
|--------|---------------------------|-----------------------------|
| **集成方式** | 在 pom.xml 中配置插件，用 `mvn rewrite:run` | 独立 JAR，不修改项目 pom |
| **目标版本** | 明确升到 3.5.x（UpgradeSpringBoot_3_5） | 官方示例偏 2.7 → 3.0，具体以当前 SBM 版本为准 |
| **使用方式** | 一条 Maven 命令，适合 CI/脚本 | 一键 JAR 或 CLI 交互，适合本地、图形化 |
| **项目要求** | Maven，JDK 17+ 运行插件 | Maven，**必须 JDK 17** 运行 SBM |

二者可择一使用；若已按前文在 pom 中配好 OpenRewrite，无需再使用 SBM。更多细节与最新用法请以 [SBM 官方仓库](https://github.com/spring-projects-experimental/spring-boot-migrator) 与 [User documentation](https://github.com/spring-projects-experimental/spring-boot-migrator#documentation) 为准。

## 使用 spring-boot-2-to-3 技能

[spring-boot-2-to-3](https://github.com/zhijunio/spring-boot-2-to-3) 是我写的一个 AI Agent Skill，自动化整个迁移过程。

### 主要功能

- ✅ 自动化 Spring Boot 2 → 3 升级（目标最新 3.5.x）
- ✅ JDK 8 → 21 迁移
- ✅ `javax.*` → `jakarta.*` 命名空间迁移
- ✅ Hibernate 5 → 6 适配
- ✅ 配置属性更新
- ✅ 依赖版本解析
- ✅ Dockerfile Java 基础镜像升级
- ✅ 完整的验证和测试流程

### 迁移场景覆盖

| 场景 | 说明 |
| ------ | ------ |
| **javax → jakarta** | `javax.persistence.*`, `javax.servlet.*`, `javax.validation.*` → `jakarta.*` |
| **Spring Security** | `WebSecurityConfigurerAdapter` → `SecurityFilterChain` bean |
| **Spring MVC** | `@RequestMapping(method=)`, `@PathVariable("id")` 等迁移 |
| **Validation** | javax.validation → jakarta.validation |
| **Async** | `AsyncConfigurerSupport` → 等效配置 |
| **Tests** | JUnit 4 → JUnit 5 |
| **Config properties** | 旧属性名 → 当前属性名 |
| **API docs** | Springfox → springdoc-openapi 2.8.x |

### 使用方法

1. **确保项目在 Spring Boot 2.7.x**：如果项目在 2.6 或更早版本，需先升级到 2.7.x
2. **调用 Skill**：请求 AI 助手使用 spring-boot-2-to-3 skill 进行升级
3. **等待自动化执行**：Skill 会自动执行以下步骤：
   - 基线验证
   - 创建工作分支
   - 运行 OpenRewrite
   - 应用手动修复
   - 验证编译和测试
   - 生成升级报告

## 总结

- **升级目标**：Spring Boot 2.7.x → 3.5.x，伴随 Jakarta EE 10、Java 17+、Spring Framework 6 等变化。
- **推荐方式**：在 Maven 项目中配置 **OpenRewrite** 插件与 **rewrite-spring**，使用一条组合配方 `UpgradeSpringBoot_3_5`，执行 `mvn rewrite:run` 即可完成依赖与代码的自动化迁移；建议先 `mvn rewrite:dryRun` 预览再应用。
- **其他方式**：**Spring Boot Migrator (SBM)** 提供一键 JAR 与 CLI（scan/apply），不改 pom，需 JDK 17、仅支持 Maven；**spring-boot-2-to-3** Skill 可在 AI 助手中一键完成整库迁移与验证。
- **示例项目**：[spring-boot-2-to-3-demo](https://github.com/zhijunio/spring-boot-2-to-3-demo) 覆盖常见迁移场景，可按文中「OpenRewrite 迁移实战」步骤练手。
- **注意**：迁移前确保项目在 2.7.x 且 `mvn compile test` 通过；运行 OpenRewrite 或 SBM 需 JDK 17+；迁移后务必再跑编译、测试与启动验证，必要时做少量手动收尾。

## 参考资料

- [spring-boot-2-to-3 Skill](https://github.com/zhijunio/spring-boot-2-to-3)
- [spring-boot-2-to-3-demo 示例项目](https://github.com/zhijunio/spring-boot-2-to-3-demo)
- [OpenRewrite 官方文档](https://docs.openrewrite.org/)
- [Spring Boot Migrator (SBM)](https://github.com/spring-projects-experimental/spring-boot-migrator)（官方实验性迁移工具，CLI/Web UI）
- [Spring Boot 3.0 Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)（官方迁移指南）
- [Spring Boot Upgrading 文档](https://docs.spring.io/spring-boot/docs/current/reference/html/upgrading.html)（当前版本升级说明）
- [Spring Boot 2 升 3：两条命令搞定 95%，AI 收尾](https://atbug.com/openrewrite-recipe-first-spring-boot-2-to-3-migration/)

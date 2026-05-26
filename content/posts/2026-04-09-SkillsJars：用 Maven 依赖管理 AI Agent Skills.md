---
title: "SkillsJars 入门：用 Maven 依赖管理 AI Agent Skills"
date: 2026-04-09 17:30:00+08:00
slug: skillsjars-quickstart
tags: [ "ai", "spring-ai", "skillsjars" ]
description: "介绍 SkillsJars 是什么、如何使用（AI 代码助手和 Spring AI）以及如何创建和发布 SkillsJars。"
---

SkillsJars 是一个类似 [WebJars](https://www.webjars.org/) 的项目，但专门用于 **AI Agent Skills**。它将 AI Agent Skills 打包成
JAR 文件，发布到 Maven Central，让开发者可以通过 Maven/Gradle 依赖的方式使用和管理 AI Skills。

<!--more-->

## 什么是 SkillsJars

在 SkillsJars 出现之前，AI Agent Skills 面临以下问题：

- **分发困难**：需要复制 SKILL.md 文件
- **版本管理**：手动追踪变更
- **发现成本高**：技能散落在各处
- **复用复杂**：难以一键引入

SkillsJars 的解决方案很简单：**把 Skills 打包成 JAR，通过 Maven Central 分发**。

### SkillsJars 结构

一个典型的 SkillsJars Maven 坐标：

```xml
<dependency>
    <groupId>com.skillsjars</groupId>
    <artifactId>myorg__myrepo__myskill</artifactId>
    <version>2026_02_13-1af0a2e</version>
</dependency>
```

- `groupId`：固定为 `com.skillsjars`
- `artifactId`：由 org、repo、skill 路径用 `__` 连接（小写，去除非字母数字字符）
- `version`：使用提交日期 + 短 commit hash（格式：`YYYY_MM_DD-hash`）

JAR 文件结构如下：

```bash
my-skill.jar
└── META-INF/
    └── skills/
        └── myorg__myrepo__myskill/
            ├── SKILL.md
            └── references/
```

## 使用 SkillsJars

SkillsJars 是将 Agent 技能打包成 JAR 文件并发布在 Maven Central 上的版本。它们可以与 AI 代码助手、自定义 Agent 以及 Spring
AI 等框架配合使用。将 Agent 技能作为打包依赖项进行管理，可以实现版本控制、作为传递依赖项进行分组，并避免文件复制粘贴。

### AI 代码助手

大多数 AI 代码助手都期望将 Agent 技能以文件的形式存储在文件系统中。SkillsJars 构建插件会将技能从项目依赖项中提取到助手可以读取的目录中。

1. 添加插件

Gradle:

```groovy
plugins {
    id("com.skillsjars.gradle-plugin") version "0.0.2"
}
```

Maven:

```xml
<build>
    <plugins>
        <plugin>
            <groupId>com.skillsjars</groupId>
            <artifactId>maven-plugin</artifactId>
            <version>0.0.6</version>
            <dependencies>
                <!-- Your SkillsJars -->
                <dependency>
                    <groupId>com.skillsjars</groupId>
                    <artifactId>anthropics__skills__pdf</artifactId>
                    <version>2026_02_25-3d59511</version>
                </dependency>
            </dependencies>
        </plugin>
    </plugins>
</build>
```

2. 添加你的 skillsjars 依赖

比如，添加 `anthropics__skills__pdf`

```xml
<dependency>
    <groupId>com.skillsjars</groupId>
    <artifactId>anthropics__skills__pdf</artifactId>
    <version>2026_02_25-3d59511</version>
</dependency>
```

3. 提取技能

运行提取命令，并指定 AI 助手期望的目录：

```bash
# Gradle
./gradlew extractSkillsJars -Pdir=.cursor/skills

# Maven
./mvnw skillsjars:extract -Ddir=.cursor/skills
```

替换 .cursor/skills 为您的AI助手用于技能的路径。

> 提示：
> 您的项目 AGENTS.md 可以指示 AI 代理在处理项目之前运行提取命令。这样，技能始终可用，无需手动设置。

如果你不想使用 SkillsJars 构建插件提取技能，可以直接下载 SkillsJars 对应的jar包，然后手动解压。

```bash
# 1. 下载 SkillsJars
wget https://repo1.maven.org/maven2/com/skillsjars/anthropics__skills__pdf/2026_02_25-3d59511/pdf-2026_02_25-3d59511.jar

# 2. 解压到 Cursor skills 目录
unzip pdf-2026_02_25-3d59511.jar -d .cursor/skills/pdf/

# 3. 在 Cursor 中使用
```

### Spring AI

[Spring AI Agent Utils ](https://github.com/spring-ai-community/spring-ai-agent-utils)项目提供了一个 SkillsTool，可将
Agent 技能直接集成到 Spring AI Agent 中。SkillsJars 开箱即用——技能直接从类路径读取，无需任何提取步骤。

1. 添加依赖项

将 Spring AI Agent Utils 库和所有 SkillsJar 依赖项添加到您的项目中：

```xml
<dependencies>
    <dependency>
        <groupId>org.springaicommunity</groupId>
        <artifactId>spring-ai-agent-utils</artifactId>
        <version>0.7.0</version>
    </dependency>

    <dependency>
        <groupId>com.skillsjars</groupId>
        <artifactId>anthropics__skills__pdf</artifactId>
        <version>2026_02_25-3d59511</version>
    </dependency>
</dependencies>
```

2. 配置技能路径

在 中`application.properties`，指向 SkillsJars 存储技能的类路径位置：

```bash
agent.skills.paths=classpath:/META-INF/skills
```

3. 连接技能工具

使用 SkillsTool 构建器加载技能并将其添加到您的 ChatClient 中：

```java
@Value("${agent.skills.paths}")
List<Resource> skillPaths;

ChatClient chatClient = chatClientBuilder
        .defaultToolCallbacks(
                SkillsTool.builder().addSkillsResources(skillPaths).build()
        )
        .build();
```

如果不使用 SkillsTool 构建器，则需要编写代码读取技能目录，将技能描述添加到系统提示词。

```java
@Configuration
public class SkillsConfig {

    @Bean
    public ChatClient chatClient(ChatClient.Builder builder) {
        List<String> skills = loadSkillsFromJars();

        return builder
                .defaultSystem(system -> {
                    system.append("你是一个有用的 AI 助手。\n");
                    for (String skill : skills) {
                        system.append("\n").append(skill);
                    }
                })
                .build();
    }

    private List<String> loadSkillsFromJars() {
        List<String> skills = new ArrayList<>();
        try {
            Resource[] resources = new PathMatchingResourcePatternResolver()
                    .getResources("classpath:META-INF/skills/**/*.md");

            for (Resource resource : resources) {
                String content = new String(
                        resource.getInputStream().readAllBytes(),
                        StandardCharsets.UTF_8
                );
                skills.add(content);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return skills;
    }
}
```

> 示例项目
>
> 请参阅 [skillsjars-example-spring-ai](https://github.com/skillsjars/skillsjars-example-spring-ai) 仓库以获取完整的运行示例。

## 创建 SkillsJars

您可以将自己的代理技能打包成 SkillsJars，并通过 SkillsJars.com 发布到 Maven Central 。

1. 创建技能目录

`skills`
在项目根目录下添加一个目录。每个子目录代表一项技能，并且必须包含一个符合  [Agent Skills 规范](https://agentskills.io/specification)
的 `SKILL.md` 标记文件。

```markdown
skills/
├── my-skill/
│ ├── SKILL.md
│ └── helpers.py
└── another-skill/
└── SKILL.md
```

2. SKILL.md frontmatter

每个文件都 `SKILL.md` 必须包含 YAML frontmatter，其中包含 `name` 和`description`。还可以选择包含`allowed-tools`
（一个以空格分隔的预先批准的工具列表）和 `license`。

```yaml
---
name: my-skill
description: A useful skill
allowed-tools: Bash Read Edit
license: MIT
---
# My Skill
...
```

通过 SkillsJars.com 发布时，`allowed-tools`会自动将其作为名为 `skillsjars.skill.<name>.allowed-tools` 的属性存储在 POM
中，以便消费者无需提取 JAR 即可读取它。

如果你自己用 Maven 插件打包 SkillsJars，必须在 `pom.xml` 中添加匹配属性。插件会验证属性值是否匹配 SKILL.md，若有不匹配则失败。

```xml
<properties>
    <skillsjars.skill.my-skill.allowed-tools>Bash Read Edit</skillsjars.skill.my-skill.allowed-tools>
</properties>
```

3. 添加 Maven 插件

添加 SkillsJars Maven 插件，goal 是 package。

```xml
<build>
    <plugins>
        <plugin>
            <groupId>com.skillsjars</groupId>
            <artifactId>maven-plugin</artifactId>
            <version>0.0.6</version>
            <executions>
                <execution>
                    <goals>
                        <goal>package</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

4. 构建 Jar

插件在 `mvn 包`期间运行，并将技能放入你的 JAR 内的 `META-INF/skills/`。如果你的项目在 POM 中配置了 GitHub SCM，它会从 URL
里调用 org/repo 来实现。否则它会使用项目的 groupID。

5. 发布到 Maven Central

把你的技能推送到公共的 GitHub 仓库，然后在主页使用“[ 发布 SkillsJar](https://www.skillsjars.com/)”表单，部署到 Maven
Central。

> 提示：自定义技能目录
> 默认情况下，插件会在`项目`根查找技能/技能。你可以用 `skillsDir` 配置参数来自定义。

## 小结

SkillsJars 让 AI Agent Skills 可以像普通 Java 库一样管理：

- **标准化分发**：通过 Maven Central 统一分发
- **版本管理**：使用 Maven 版本控制机制
- **易于发现**：在 skillsjars.com 浏览和搜索
- **生态集成**：与 Spring AI 等框架无缝集成

想要为你的 AI Agent 添加新技能？直接在 `pom.xml` 中加个依赖就行。

## 参考资料

- [SkillsJars 官网](https://www.skillsjars.com/)
- [SkillsJars 文档](https://www.skillsjars.com/docs)
- [Anthropic Skills 仓库](https://github.com/anthropics/skills)
- [Agent Skills 规范](https://agentskills.io/specification)
- [Spring AI Agent Utils](https://github.com/spring-ai-community/spring-ai-agent-utils)

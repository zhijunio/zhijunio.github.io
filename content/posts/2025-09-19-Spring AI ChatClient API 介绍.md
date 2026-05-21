---
title: "Spring AI ChatClient API 详解：调用链、模板与结构化输出"
date: 2025-09-19 08:00:00+08:00
slug: spring-ai-chat-client-api
categories: [ "tech" ]
tags: [ "spring-ai" ]
favicon: "spring-ai.svg"
description: "围绕 Spring AI 的 ChatClient API，介绍其创建方式、调用链设计、提示模板与结构化输出等核心能力。"
---

ChatClient 是 Spring AI 提供的核心 API，提供流畅的调用方式，用于与各类大模型交互。本文结合 [chat-model](https://github.com/zhijunio/spring-ai-chat-model-samples/tree/main/chat-model) 示例，介绍 ChatClient 的创建方式、调用链、提示模板与结构化输出等能力。

<!--more-->

## 源代码

如果您想自己尝试，可以查看我的源代码。为此，您必须克隆我的示例 [GitHub 仓库](https://github.com/zhijunio/spring-ai-chat-model-samples)。然后，您只需按照我的说明操作即可。

## 核心概念

- **ChatClient**：与模型交互的入口，通过 `prompt()` 构建请求、`call()` 或 `stream()` 执行。
- **Prompt**：一次请求的完整内容，可包含系统消息、用户消息、占位符等。
- **PromptTemplate**：将模板与变量合并为消息，便于生成结构化提示。
- **OutputConverter**：将模型输出转换为 List、Map、Bean 等结构。
- **Advisor**：在请求/响应链上的拦截与增强（如日志、记忆、RAG），本示例使用 `SimpleLoggerAdvisor`。

## 使用 ChatClient.Builder 创建 ChatClient

本示例通过 Spring Boot 自动配置的 `ChatClient.Builder` 创建 ChatClient，并在构建时注册默认 Advisor：

```java
@RestController
@RequestMapping("/api/chat")
class ChatClientController {
    private final ChatClient chatClient;

    ChatClientController(ChatClient.Builder builder) {
        this.chatClient = builder
                .defaultAdvisors(new SimpleLoggerAdvisor())
                .build();
    }

    @PostMapping
    Output chat(@RequestBody @Valid Input input) {
        String response = chatClient.prompt(input.prompt()).call().content();
        return new Output(response);
    }
}
```

要点：

- 注入 `ChatClient.Builder`，调用 `build()` 得到 `ChatClient`。
- `defaultAdvisors(new SimpleLoggerAdvisor())` 为每次调用统一加上请求/响应日志。
- `Input` 与 `Output` 位于 `model` 包，控制器只负责业务流程。
- 无需在代码中写死模型或 API 地址，均由配置文件与 profile 决定。

## 调用链：prompt → call → content

一次同步调用的典型写法：

```java
String response = chatClient.prompt(input.prompt()).call().content();
```

- **prompt(...)**：传入用户输入（或更复杂的 `PromptSpec`，如 `.user(...).system(...)`）。
- **call()**：同步执行，返回 `ChatResponse`。
- **content()**：从 `ChatResponse` 中取出助手回复的文本。

若需要完整响应（元数据、用法等），可保留 `ChatResponse`：

```java
ChatResponse chatResponse = chatClient.prompt(input.prompt()).call().chatResponse();
String text = chatResponse.getResult().getOutput().getContent();
// 还可访问 chatResponse.getMetadata() 等
```

## SimpleLoggerAdvisor 与日志

`SimpleLoggerAdvisor` 会在 DEBUG 级别打印请求与响应，便于调试。启用方式：

```properties
logging.level.org.springframework.ai.chat.client.advisor=DEBUG
```

本示例在 `application.properties` 中已配置上述日志级别，使用默认或任意模型 profile 启动即可在控制台看到每次调用的 prompt 与模型回复。

## 配置选项

与本示例相关的配置集中在 `application.properties`，并配合 Maven Profile 激活不同模型依赖：

```properties
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.openai.chat.options.model=gpt-5
spring.ai.openai.chat.options.temperature=1

spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY}
spring.ai.anthropic.chat.options.model=claude-sonnet-4-5

spring.ai.ollama.chat.options.model=qwen3:8b
```

运行时可用 Maven Profile 切换依赖：

- OpenAI（默认）：`mvn spring-boot:run`
- Anthropic：`mvn spring-boot:run -Panthropic`
- Ollama：`mvn spring-boot:run -Pollama`

常用项说明：

| 配置项                                      | 说明                                                         |
| ------------------------------------------- | ------------------------------------------------------------ |
| `spring.ai.openai.api-key`                  | OpenAI API Key 环境变量                                      |
| `spring.ai.openai.chat.options.model`       | OpenAI 模型名称                                              |
| `spring.ai.openai.chat.options.temperature` | 采样随机度，0～1                                             |
| `spring.ai.anthropic.api-key`               | Anthropic API Key 环境变量                                   |
| `spring.ai.anthropic.chat.options.model`    | Anthropic 模型名称                                           |
| `spring.ai.ollama.chat.options.model`       | Ollama 本地模型名称                                          |

## 测试接口

使用 deepseek 模型启动应用：

```bash
cd chat-model
mvn spring-boot:run 
```

应用启动后，可用 curl 验证：

```bash
curl -s -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d "{"prompt":"What is Spring Boot?"}"
```

返回为 JSON：`{"content":"..."}`。

## ChatClient 扩展示例

本模块在 ChatClient 基础上扩展了提示模板、结构化输出与工具调用等能力：

- **提示模板与系统消息**：`POST /api/chat/prompt`
- **标题建议（PromptTemplate）**：`POST /api/chat/prompt/suggest-titles`
- **生成推文（模板 + tone 变量）**：`POST /api/chat/prompt/gen-tweet`
- **结构化输出（List/Map/Bean）**：`/api/chat/converter/suggest-titles`、`/api/chat/converter/langs`、`/api/chat/converter/gen-tweet`
- **工具调用（Tools）**：`POST /api/chat/tool`

同一应用若需同时接入多个模型，可关闭默认自动配置后自行定义多个 `ChatModel` / `ChatClient` Bean，并通过 `@Qualifier` 注入。

## 总结

- ChatClient 通过 **ChatClient.Builder** 创建，本示例使用 `defaultAdvisors(SimpleLoggerAdvisor)` 统一打日志。
- 同步调用链为 **prompt(...) → call() → content()**，与具体模型解耦。
- 模型相关配置集中在 **application.properties**，并通过 Maven Profile 切换依赖。
- 提示模板、结构化输出与工具调用示例已在本模块对应接口中覆盖。

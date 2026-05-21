---
title: "Java 生成式 AI 入门：LangChain4j + OpenAI 快速上手"
date: 2026-02-06 08:00:00+08:00
slug: getting-started-with-langchain4j
categories: [ "tech" ]
tags: [ "ai", "java" ]
favicon: "langchain4j.svg"
description: "面向 Java 开发者的生成式 AI 入门实践，介绍如何使用 LangChain4j 与 OpenAI（及兼容模型）构建 AI 应用。"
---

生成式 AI 正在重塑应用开发的方式。虽然 Python 在该领域占据主导地位，但 Java 开发者并未被遗忘。**LangChain4j** 应运而生——这是一个功能强大的库，旨在简化大语言模型（LLMs）与 Java 应用的集成。

本文将带你探索如何分别使用原生 Java 和 LangChain4j 与 OpenAI（及其兼容模型）进行交互，并展示 LangChain4j 为何是 Java 开发者的不二之选。

<!--more-->

## 源代码与项目结构

本文示例代码位于 GitHub 仓库 **[langchain4j-samples/01-chat-openai](https://github.com/zhijunio/langchain4j-samples/tree/main/01-chat-openai)**，克隆后进入该模块即可运行：

```bash
git clone https://github.com/zhijunio/langchain4j-samples.git
cd langchain4j-samples/01-chat-openai
```

## 前置条件

- Java 17+
- Maven 3.9+

## OpenAI Chat API 简介

首先，我们需要在 OpenAI 创建一个帐户并获取 API 密钥。

- 前往 [OpenAI 平台](https://platform.openai.com/) 并创建一个帐户。
- 在控制面板中，点击左侧导航菜单中的“API 密钥” ，创建一个新的 API 密钥。

获取 API 密钥后，即可使用它与 OpenAI API 进行交互。您可以在[此处](https://platform.openai.com/docs/api-reference/)找到 OpenAI API 参考文档。

让我们看看如何使用 OpenAI 的 Chat API 端点向其提出问题。

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": "Who are you"
      }
    ]
  }'
```

你会收到类似如下的 JSON 响应：

```json
{
  "id": "chatcmpl-8tvrQyjw3s28IREvkFl6kIhTxIUGZ",
  "object": "chat.completion",
  "created": 1708341148,
  "model": "gpt-3.5-turbo-0125",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I am an AI assistant created by OpenAI..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 10,
    "total_tokens": 20
  }
}
```

这个简单的 API 调用就是我们接下来要用 Java 实现的核心功能。

## 使用原生 Java

在领略 LangChain4j 的便捷之前，我们先看看使用标准 Java 库（`java.net.http.HttpClient` 和 `Jackson`）调用 `OpenAI Chat Completion API` 需要做哪些工作。

现在，让我们看看如何使用 Java 内置的HttpClient与 OpenAI 进行交互。

我们将使用 Jackson JSON 库来序列化/反序列化请求和响应。

```xml title="pom.xml"
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

首先，创建 Java Record 表示请求和响应的 JSON（与仓库 [PlainChatDemo.java](https://github.com/zhijunio/langchain4j-samples/blob/main/01-chat-openai/src/main/java/cc/zhijunio/ai/PlainChatDemo.java) 一致）：

```java
package cc.zhijunio.ai;

record Message(String role, String content) {}

record ChatRequest(String model, List<Message> messages, double temperature) {}

@JsonIgnoreProperties(ignoreUnknown = true)
record ChatUsage(
        @JsonProperty("prompt_tokens")
        int promptTokens,
        @JsonProperty("completion_tokens")
        int completionTokens,
        @JsonProperty("total_tokens")
        int totalTokens
) {}

@JsonIgnoreProperties(ignoreUnknown = true)
record ChatResponseChoice(
        int index,
        Message message,
        @JsonProperty("finish_reason")
        String finishReason
) {}

@JsonIgnoreProperties(ignoreUnknown = true)
record ChatResponse(
        String id, String object, long created,
        String model, ChatUsage usage,
        List<ChatResponseChoice> choices
) {}
```

我们创建了 Java 记录来表示请求和响应，其中只包含我们感兴趣的字段。

接下来，我们使用 Java 的 HttpClient 与 OpenAI 进行交互。

```java title="PlainChatDemo.java"
public class PlainChatDemo {
    public static final String OPENAI_API_KEY = System.getenv("OPENAI_API_KEY");
    public static final String CHAT_URL = "https://api.openai.com/v1/chat/completions";
    public static final String MODEL = "gpt-3.5-turbo";
    public static final double TEMPERATURE = 0.7;

    static HttpClient client = HttpClient.newHttpClient();
    static ObjectMapper mapper = new ObjectMapper();

    public static void main(String[] args) throws Exception {
        Message message = new Message("user", "Who are you");
        ChatRequest chatRequest = new ChatRequest(MODEL, List.of(message), TEMPERATURE);
        String requestPayload = mapper.writeValueAsString(chatRequest);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(CHAT_URL))
                .header("Authorization", "Bearer %s".formatted(OPENAI_API_KEY))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestPayload))
                .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        ChatResponse chatResponse = mapper.readValue(response.body(), ChatResponse.class);
        System.out.println(chatResponse.choices().getFirst().message().content());
    }
}
```

设置环境变量后运行主类即可看到模型回复：

```bash
export OPENAI_API_KEY=your_openai_api_key
mvn compile exec:java -Dexec.mainClass="cc.zhijunio.ai.PlainChatDemo"
```

### 使用 LangChain4j

使用 [LangChainChatDemo.java](https://github.com/zhijunio/langchain4j-samples/blob/main/01-chat-openai/src/main/java/cc/zhijunio/ai/LangChainChatDemo.java) 时，只需几行即可完成同样效果。**先以 OpenAI 为例**：

```java title="LangChainChatDemo.java（OpenAI）"
package cc.zhijunio.ai;

public class LangChainChatDemo {
    public static void main(String[] args) {
        ChatModel model = OpenAiChatModel.builder()
                .apiKey(System.getenv("OPENAI_API_KEY"))
                .build();
        String answer = model.chat("Who are you");
        System.out.println(answer);
    }
}
```

设置 `OPENAI_API_KEY` 后运行，即可得到 OpenAI 模型的回复。

**若改用阿里云百炼（千问）等兼容 OpenAI 的接口**，只需指定 `baseUrl` 与 `modelName`，并设置对应的 API Key（如 `DASHSCOPE_API_KEY`）：

```java title="LangChainChatDemo.java（千问）"
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
        .apiKey(System.getenv("DASHSCOPE_API_KEY"))
        .modelName("qwen-turbo")
        .build();
String answer = model.chat("Who are you");
System.out.println(answer);
```

此时输出会来自千问，例如：

```txt
I am Qwen, a large-scale language model developed by Alibaba Group...
```

`OpenAiChatModel` 还支持温度、超时、重试以及请求/响应监听器等配置，便于调试与监控。仓库中的 [LangChainChatDemo](https://github.com/zhijunio/langchain4j-samples/blob/main/01-chat-openai/src/main/java/cc/zhijunio/ai/LangChainChatDemo.java) 即在此基础上增加了 `ChatModelListener` 示例：

```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://dashscope.aliyuncs.com/compatible-mode/v1")
        .apiKey(System.getenv("DASHSCOPE_API_KEY"))
        .modelName("qwen-turbo")
        .temperature(0.3)
        .maxRetries(1)
        .timeout(Duration.ofSeconds(60))
        .listeners(List.of(new TestChatModelListener()))
        .logRequests(true)
        .logResponses(true)
        .build();
```

监听器可实现 `ChatModelListener`，在请求发出、响应返回或发生错误时执行逻辑（例如打日志、传递上下文）：

```java
@Slf4j
public static class TestChatModelListener implements ChatModelListener {
    @Override
    public void onRequest(ChatModelRequestContext requestContext) {
        requestContext.attributes().put("test", "test");
        log.info("请求参数:{}", requestContext.attributes());
    }

    @Override
    public void onResponse(ChatModelResponseContext responseContext) {
        Object object = responseContext.attributes().get("test");
        log.info("返回结果:{}", object);
    }

    @Override
    public void onError(ChatModelErrorContext errorContext) {
        log.error("请求异常:{}", errorContext);
    }
}
```

### 图像生成

除聊天外，LangChain4j 也支持图像生成。**使用 OpenAI DALL·E** 时，可参考：

```java
ImageModel model = OpenAiImageModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(DALL_E_3)
        .build();
Response<Image> response = model.generate(
        "Swiss software developers with cheese fondue, a parrot and a cup of coffee");
System.out.println(response.content().url());
```

**使用阿里云百炼（通义万相）** 时，需在 `pom.xml` 中增加 `langchain4j-community-dashscope` 依赖（仓库 [01-chat-openai/pom.xml](https://github.com/zhijunio/langchain4j-samples/blob/main/01-chat-openai/pom.xml) 已包含），然后使用 `WanxImageModel`，见仓库 [LangChainImageDemo.java](https://github.com/zhijunio/langchain4j-samples/blob/main/01-chat-openai/src/main/java/cc/zhijunio/ai/LangChainImageDemo.java)：

```xml title="pom.xml"
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-dashscope</artifactId>
</dependency>
```

```java title="LangChainImageDemo.java"
package cc.zhijunio.ai;

ImageModel model = WanxImageModel.builder()
        .apiKey(System.getenv("DASHSCOPE_API_KEY"))
        .modelName("qwen-image")
        .build();
Response<Image> response = model.generate(
        "Swiss software developers with cheese fondue, a parrot and a cup of coffee");
System.out.println(response.content().url());
```

## 使用 Spring Boot

在模块 [01-chat-openai](https://github.com/zhijunio/langchain4j-samples/tree/main/01-chat-openai) 中，`pom.xml` 已引入 `langchain4j-open-ai-spring-boot-starter`，只需在配置文件中指定 API Key 与模型即可注入 `ChatModel`。

**配置**（[application.yaml](https://github.com/zhijunio/langchain4j-samples/blob/main/01-chat-openai/src/main/resources/application.yaml)）：使用阿里云百炼时设置 `base-url` 与 `model-name`，API Key 可用环境变量 `DASHSCOPE_API_KEY`。

```yaml title="src/main/resources/application.yaml"
langchain4j:
  open-ai:
    chat-model:
      api-key: ${DASHSCOPE_API_KEY}
      model-name: qwen-turbo
      base-url: https://dashscope.aliyuncs.com/compatible-mode/v1
```

**启动类与演示**（[ChatOpenAIApplication.java](https://github.com/zhijunio/langchain4j-samples/blob/main/01-chat-openai/src/main/java/cc/zhijunio/ai/ChatOpenAIApplication.java)）：应用启动后通过 `CommandLineRunner` 调用一次聊天并打印结果。

```java title="ChatOpenAIApplication.java"
package cc.zhijunio.ai;

@SpringBootApplication
public class ChatOpenAIApplication {

    public static void main(String[] args) {
        SpringApplication.run(ChatOpenAIApplication.class, args);
    }

    @Bean
    public CommandLineRunner commandLineRunner(ChatModel chatModel) {
        return args -> {
            String answer = chatModel.chat("Who are you");
            System.out.println(answer);
        };
    }
}
```

运行前设置 `DASHSCOPE_API_KEY`，在仓库根目录执行 `mvn spring-boot:run -pl 01-chat-openai` 即可看到控制台输出模型回复。

## 总结

本文示例均可在 [zhijunio/langchain4j-samples · 01-chat-openai](https://github.com/zhijunio/langchain4j-samples/tree/main/01-chat-openai) 中查看与运行；从原生 Java 调用 OpenAI，到 LangChain4j 封装聊天/图像，再到 Spring Boot 集成，可按需选用。

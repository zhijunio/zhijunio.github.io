---
title: "Spring AI SSE 流式回复：基于对话记忆的实时逐字输出"
date: 2026-01-04 08:00:00+08:00
slug: spring-ai-chat-memory-sse
tags: [ "spring-ai" ]
description: "在 《Spring AI 对话记忆 》中我们用 MessageChatMemoryAdvisor + JDBC 实现了多轮对话记忆。本文基于同一套记忆能力，升级为 Server-Sent Events (SSE) 流式输出，并配上自定义前端让 DeepSeek 的回复实时逐字出现。"
---

在 《[Spring AI 对话记忆](/posts/2026/01/03/spring-ai-chat-memory/) 》中我们用 **MessageChatMemoryAdvisor + JDBC** 实现了多轮对话记忆。本文基于同一套记忆能力，升级为 **Server-Sent Events (SSE)** 流式输出，并配上自定义前端让 DeepSeek 的回复实时逐字出现。
<!--more-->

## 源代码

如果您想自己尝试，可以查看我的源代码。为此，您必须克隆我的示例  [GitHub 仓库](https://github.com/zhijunio/spring-ai-chat-memory-samples) 。然后，您只需按照我的说明操作即可。

## 为什么需要“记忆 + 流式输出”

- **对话记忆**：同 chat-memory 一样，按 `conversationId` 持久化历史消息，保证模型能“记住”你是谁。
- **SSE 流式体验**：相比一次性返回，SSE 可以将大模型的逐字输出直接推送到浏览器，显著缩短“首字延迟”。
- **前端友好**：自定义 UI 自动渲染 Markdown/HTML，列表、表格、代码块都能即时排版。

## 核心依赖

除了 chat-memory 已有的依赖外，这个模块额外引入了 WebFlux：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```

- **spring-boot-starter-webflux**：提供 `Flux`、`SseEmitter`、反压处理等能力，便于把 Spring AI 的流式内容通过 SSE 推到前端。
- 其余依赖（OpenAI/DeepSeek、JDBC Chat Memory、PostgreSQL、docker-compose）与 chat-memory 保持一致。

## 后端：ChatClient + SSE

`ChatController` 同时暴露了普通接口 `/api/chat` 与流式接口 `/api/chat/stream`，二者共享同一 `ChatClient` 和 `MessageChatMemoryAdvisor`。流式接口的核心如下：

```java
@PostMapping(value = "/api/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
ResponseEntity<SseEmitter> chatStream(@RequestBody @Valid Input input,
                                      @CookieValue(name = "X-CONV-ID", required = false) String convId) {
    String conversationId = convId == null ? UUID.randomUUID().toString() : convId;
    SseEmitter emitter = new SseEmitter(0L);

    Flux<String> contentFlux = this.chatClient.prompt()
            .user(input.prompt())
            .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, conversationId))
            .stream()
            .content();

    contentFlux.subscribe(
            chunk -> emitter.send(SseEmitter.event().data(chunk)),
            emitter::completeWithError,
            emitter::complete
    );

    ResponseCookie cookie = ResponseCookie.from("X-CONV-ID", conversationId)
            .path("/")
            .maxAge(3600)
            .build();
    return ResponseEntity.ok()
            .header(HttpHeaders.SET_COOKIE, cookie.toString())
            .body(emitter);
}
```

关键点：

1. **Shared ChatClient**：构造时同 chat-memory 一样注册 `MessageChatMemoryAdvisor`，保证多轮记忆。
2. **Flux + stream()**：`chatClient.prompt().stream().content()` 返回 `Flux<String>`，每个元素是一小段模型输出。
3. **SseEmitter**：将 Flux 订阅结果逐段写入 SSE 事件，前端即刻收到。
4. **Cookie 会话**：若请求没有 `X-CONV-ID`，就生成新 UUID，写入返回头，浏览器自动持久化，确保后续请求沿用同一会话存储。

普通接口 `/api/chat` 则与 chat-memory 基本一致，可在调试或 Postman 调用时使用。

## 前端：实时 Markdown 渲染

`templates/index.html` 使用纯原生 JS + Bootstrap 打造聊天 UI，亮点包括：

- `sendStreamingMessage()` 通过 `fetch("/api/chat/stream")` 获取 `ReadableStream`，持续读取 `reader.read()` 返回的 chunk，并同步滚动到底部。
- 结合 **marked + DOMPurify**，自动将 Markdown、表格、代码块、甚至 DeepSeek 输出的列表渲染成安全的 HTML。
- 自定义 `textToHtml` 兜底逻辑，修正 DeepSeek 常见的“行内列表”格式，确保 `- 条目` 也能渲染成 `<ul><li>…`。
- 输入框自动增高、流式回复显示“闪烁光标”等细节提升了对话质感。

核心 JS 片段：

```javascript
async function sendStreamingMessage(prompt) {
    const res = await fetch("/api/chat/stream", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }) });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '", fullText = "';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() || '';
        for (const event of events) {
            const payload = event.replace(/^data: ?/gm, '');
            fullText += payload;
            contentEl.textContent = fullText; // 流式显示
        }
    }
    contentEl.innerHTML = markdownToHtml(fullText);
}
```

## 配置与 Postgres

`application.properties`：

```properties
spring.application.name=07-chat-memory-sse

spring.ai.openai.base-url=https://api.deepseek.com
spring.ai.openai.api-key=${DEEPSEEK_API_KEY}
spring.ai.openai.chat.options.model=deepseek-reasoner

logging.level.org.springframework.ai.chat.client.advisor=DEBUG
spring.ai.chat.memory.repository.jdbc.initialize-schema=always
```

## 运行步骤

## 运行与验证

1. **环境变量**：设置 DeepSeek API Key。

   ```bash
   export DEEPSEEK_API_KEY=<your-api-key>
   ```

2. **启动 Postgres**（若使用 docker-compose）：

   ```bash
   cd 07-chat-memory-sse && docker compose up -d
   ```

3. **启动应用**：

   ```bash
   mvn spring-boot:run
   ```

4. **打开聊天页面**：浏览器访问 `http://localhost:8080/` ，输入多轮对话，可以看到：
   - DeepSeek 回复实时逐字流出；
   - 列表/表格/代码被正确渲染；
   - 刷新浏览器前记忆一直保存在 Postgres 中。

5. **API 测试**（同一会话需在请求中带相同 Cookie，或先请求一次拿到 Set-Cookie 再复用）：

   ```bash
   # 首次请求，从响应头中拿到 Set-Cookie 中的 X-CONV-ID，后续请求可携带该 Cookie
   curl -s -X POST http://localhost:8080/api/chat/stream \
     -H "Content-Type: application/json" \
     -d "{"prompt":"我叫小明，请记住。"}" -c cookies.txt -b cookies.txt -D -
   
   curl -s -X POST http://localhost:8080/api/chat/stream \
     -H "Content-Type: application/json" \
     -d "{"prompt":"我叫什么名字？"}" -b cookies.txt
   ```

6. **查看数据库**。可以看到数据库里面创建一个 `spring_ai_chat_memory` 表：

   ![spring-ai-chat-memory-postgres-table]( /images/spring-ai-chat-memory-postgres-table.webp)

## 小结

- **记忆能力**：沿用 JDBC Chat Memory，通过 Cookie + UUID 实现跨请求的上下文。
- **SSE 流式**：`Flux<String>` + `SseEmitter`，无需额外消息队列即可把 Spring AI 的 `stream()` 推到浏览器。
- **UI 强化**：前端处理 Markdown/HTML、代码块、表格、列表，真正做到“所见即所得”的 AI 对话体验。

想要一个既能“记住你”又能“实时输出”的聊天机器人？在 chat-memory 的基础上加上这套 SSE 流就够了。

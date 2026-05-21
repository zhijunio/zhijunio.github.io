---
title: "Spring AI RAG 实战：向量存储与检索增强生成"
date: 2026-02-01 08:00:00+08:00
slug: spring-ai-rag-vector-store
categories: [ "tech" ]
tags: ["spring-ai", "rag", "redis"]
favicon: "storage.svg"
description: "介绍如何在 Spring AI 中结合 RAG 与向量存储构建 Spring Boot 应用，让模型能够基于外部知识做更准确的回答。"
---

本文将教你如何创建一个使用 RAG（检索增强生成）和向量存储以及 Spring AI 的 Spring Boot 应用程序。

<!--more-->

## 源代码

如果您想自己尝试，可以查看我的源代码。为此，您必须克隆我的示例   [GitHub 仓库](https://github.com/zhijunio/spring-ai-chat-rag-samples)。然后，您只需按照我的说明操作即可。

## 使用 Spring AI 实现 RAG 的动机

由于 OpenAI 模型是在静态数据集上训练的，因此它无法直接访问在线服务或 API。我们可以将这些数据存储在本地数据库中，并将其集成到示例 Spring Boot AI 应用程序中。我们将使用向量存储而不是典型的关系型数据库。在向量数据库中，查询的工作方式与传统关系型数据库不同。它不是查找完全匹配项，而是执行相似性搜索。它会检索与给定输入向量最相似的向量。

将所有必需数据加载到向量数据库后，我们需要将其与 AI 模型集成。Spring AI 基于`Advisors`API 提供了一个便捷的集成机制。在之前的示例中，我们已经使用了一些内置的智能助手，例如打印详细的 AI 通信日志或启用聊天记录记忆。这次，它们将帮助我们为应用程序实现检索增强生成 (RAG) 技术。借助这项技术，Spring Boot 应用程序会在向 AI 模型发送请求之前，检索与用户查询最匹配的相似文档。这些文档为查询提供上下文，并与用户的问题一起发送给 AI 模型。

## 使用 Spring AI 的 Vector Store

### 配置 Redis 向量数据库

在本节中，我们将准备一个向量存储，将其与我们的 Spring Boot 应用程序集成，并加载一些数据。Spring AI 支持多种向量数据库。它提供了一个`VectorStore`接口，允许我们的 Spring Boot 应用程序直接与向量存储进行交互。完整的受支持数据库列表可以在 Spring AI 文档中找到（链接[在此）](https://docs.spring.io/spring-ai/reference/1.0/api/vectordbs.html)。

本文使用 Redis 向量数据库进行测试，您可以使用`docker-compose.yaml`仓库根目录中的文件，通过`docker compose up`命令运行该数据库。

```yaml
services:
  redis:
    image: "redis/redis-stack:7.2.0-v18"
    labels:
      - "org.springframework.boot.service-connection=redis"
    ports:
      - "6379:6379"
```

### 使用 Spring AI 将 Spring Boot 应用与 Redis 集成

我们的 Spring Boot 应用程序必须包含`spring-ai-starter-vector-store-redis`必要的依赖项，才能与 Redis 向量存储顺利集成。

```xml
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-starter-vector-store-redis</artifactId>
</dependency>
```

然后，我们可以在 Spring Boot 文件中提供 Redis 数据库的连接设置和凭据`application.properties`。Redis 数据库的连接设置使用的都是默认配置，故可以不用在配置文件中设置，Spring Boot 会读取默认配置进行自动装配。

```properties
spring.ai.vectorstore.redis.initialize-schema=true
```

完成所有必要的配置设置后，我们就可以`VectorStore`在应用程序的 REST 控制器中注入并使用该 bean。

```java
@RestController
@RequestMapping("/api/chat")
class ChatController {
    private final VectorStore vectorStore;
  //....
}
```

### 加载文档到 VectorStore

```
┌──────────────┐     ┌────────────┐     ┌─────────────┐     ┌────────────────────┐
│ Markdown 文档 │ --> │ 文档读取/切分│ --> │Embedding API│ --> │ Redis VectorStore  │
└──────────────┘     └────────────┘     └─────────────┘     └────────────────────┘
                                                           ↑
                                  ChatClient + QuestionAnswerAdvisor ←───────────┘
```

- **摄取**：`AiConfig` 在应用启动时读取 `src/main/resources/data/*.md`，切分片段并写入 VectorStore。
- **检索**：`QuestionAnswerAdvisor` 基于用户问题生成查询向量，调用 `vectorStore.similaritySearch()` 取回最相关的 Document。
- **生成**：检索结果作为上下文拼接进 Prompt，Ollama 结合 `MessageChatMemoryAdvisor` 输出有记忆的回答。

`AiConfig` 只负责把文档切分并写入：

```java
@Configuration
public class AiConfig {
    private static final Logger log = LoggerFactory.getLogger(AiConfig.class);

    @Value("classpath:/data/about.md")
    private Resource aboutFile;

    @Value("classpath:/data/career.pdf")
    private Resource careerLessonsFile;

    @Bean
    ApplicationRunner applicationRunner(VectorStore vectorStore) {
        return args -> {
            loadDocument(vectorStore, aboutFile);
            loadDocument(vectorStore, careerLessonsFile);
        };
    }

    private void loadDocument(VectorStore vectorStore, Resource resource) {
        log.info("Loading document {} into vector store", resource.getFilename());

        DocumentReader documentReader = null;
        if (resource.getFilename().endsWith(".md")) {
            documentReader = new MarkdownDocumentReader(resource, MarkdownDocumentReaderConfig.defaultConfig());
        } else if (resource.getFilename().endsWith(".pdf")) {
            documentReader = new PagePdfDocumentReader(resource);
        }

        List<Document> documents = documentReader.get();
        TextSplitter textSplitter = new TokenTextSplitter();
        List<Document> splitDocuments = textSplitter.apply(documents);
        String src = FilenameUtils.getBaseName(resource.getFilename());
        List<Document> enriched = java.util.stream.IntStream.range(0, splitDocuments.size())
                .mapToObj(i -> {
                    Document d = splitDocuments.get(i);
```

---
title: "OpenAI API 与 Spring AI 对照表：接口映射关系"
date: 2025-09-22 08:00:00+08:00
slug: openai-api-with-spring-ai
tags: [ "spring-ai" ]
description: "梳理 OpenAI API 各类接口在 Spring AI 中的对应方式，帮助快速建立模型能力与 Spring 封装 API 之间的映射关系。"
---

OpenAI API 提供了一套强大的接口，允许开发者将其先进的人工智能模型集成到各种应用中。它支持文本生成、翻译、总结、问答、对话、代码生成、图像生成、音频处理等多种任务。

Spring AI 通过统一的 API 对 OpenAI 的各种接口进行了封装，使得开发者可以在 Spring 生态系统中轻松使用 OpenAI 的所有功能。Spring AI 不仅支持 OpenAI，还支持其他遵循 OpenAI 接口规范的模型提供商。

<!--more-->

## 第一部分：OpenAI API 接口详解

### 1. API 概述

**基础信息：**

- 基础 URL：`https://api.openai.com/v1`
- 认证方式：Bearer Token
- 请求格式：JSON
- 响应格式：JSON

### 2. 认证与安全

```bash
# 请求头格式
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**安全最佳实践：**

- 将 API 密钥存储在环境变量中
- 使用密钥管理服务
- 定期轮换密钥
- 监控 API 使用情况

### 3. 速率限制与计费

**速率限制：**

- 基于账户类型和使用情况
- 按分钟和按天限制
- 可在账户设置中查看

**计费模式：**

- 按使用量计费
- 不同模型不同价格
- 按输入和输出标记数计算

## 第二部分：OpenAI API 接口详解

### 1. 聊天补全（Chat Completions）

**端点：** `POST https://api.openai.com/v1/chat/completions`

**用途：** 支持多轮对话，适用于构建聊天机器人等应用

**请求参数：**

| 参数                | 类型    | 必需 | 说明                                |
| ------------------- | ------- | ---- | ----------------------------------- |
| `model`             | string  | 是   | 模型名称（如 gpt-4, gpt-3.5-turbo） |
| `messages`          | array   | 是   | 消息列表                            |
| `temperature`       | number  | 否   | 温度参数（0-2），控制随机性         |
| `max_tokens`        | integer | 否   | 最大生成标记数                      |
| `top_p`             | number  | 否   | 核采样参数（0-1）                   |
| `n`                 | integer | 否   | 生成数量（1-10）                    |
| `stream`            | boolean | 否   | 是否流式输出                        |
| `stop`              | array   | 否   | 停止序列                            |
| `presence_penalty`  | number  | 否   | 存在惩罚（-2到2）                   |
| `frequency_penalty` | number  | 否   | 频率惩罚（-2到2）                   |
| `user`              | string  | 否   | 用户标识                            |

**消息格式：**

```json
{
  "role": "system|user|assistant",
  "content": "消息内容"
}
```

**请求示例：**

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "你是一个乐于助人的助手。"},
      {"role": "user", "content": "你好！"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.9,
    "stream": false
  }'
```

**响应示例：**

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！有什么我可以帮助您的吗？"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 10,
    "total_tokens": 25
  }
}
```

### 2. 文本补全（Completions）

**端点：** `POST https://api.openai.com/v1/completions`

**用途：** 生成或编辑文本，适用于内容创作、代码生成等

**请求参数：**

| 参数                | 类型         | 必需 | 说明                            |
| ------------------- | ------------ | ---- | ------------------------------- |
| `model`             | string       | 是   | 模型名称（如 text-davinci-003） |
| `prompt`            | string/array | 是   | 输入提示                        |
| `max_tokens`        | integer      | 否   | 最大生成标记数                  |
| `temperature`       | number       | 否   | 温度参数（0-2）                 |
| `top_p`             | number       | 否   | 核采样参数（0-1）               |
| `n`                 | integer      | 否   | 生成数量（1-10）                |
| `stream`            | boolean      | 否   | 是否流式输出                    |
| `stop`              | array        | 否   | 停止序列                        |
| `presence_penalty`  | number       | 否   | 存在惩罚（-2到2）               |
| `frequency_penalty` | number       | 否   | 频率惩罚（-2到2）               |
| `user`              | string       | 否   | 用户标识                        |

**请求示例：**

```bash
curl https://api.openai.com/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "text-davinci-003",
    "prompt": "请写一首关于春天的诗。",
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9
  }'
```

**响应示例：**

```json
{
  "id": "cmpl-abc123",
  "object": "text_completion",
  "created": 1677652288,
  "model": "text-davinci-003",
  "choices": [
    {
      "text": "春天来了，万物复苏，花儿绽放，鸟儿歌唱。",
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### 3. 嵌入（Embeddings）

**端点：** `POST https://api.openai.com/v1/embeddings`

**用途：** 将文本转换为向量表示，适用于语义搜索、推荐系统等

**请求参数：**

| 参数              | 类型         | 必需 | 说明                      |
| ----------------- | ------------ | ---- | ------------------------- |
| `model`           | string       | 是   | 嵌入模型名称              |
| `input`           | string/array | 是   | 输入文本                  |
| `encoding_format` | string       | 否   | 编码格式（float, base64） |
| `dimensions`      | integer      | 否   | 嵌入维度                  |
| `user`            | string       | 否   | 用户标识                  |

**请求示例：**

```bash
curl https://api.openai.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "text-embedding-ada-002",
    "input": "机器学习的基本概念",
    "encoding_format": "float",
    "dimensions": 1536
  }'
```

**响应示例：**

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.123, 0.456, -0.789, ...],
      "index": 0
    }
  ],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
```

### 4. 图像生成（Images）

**端点：** `POST https://api.openai.com/v1/images/generations`

**用途：** 根据文本描述生成图像

**请求参数：**

| 参数              | 类型    | 必需 | 说明                               |
| ----------------- | ------- | ---- | ---------------------------------- |
| `model`           | string  | 是   | 图像模型名称（dall-e-2, dall-e-3） |
| `prompt`          | string  | 是   | 图像描述                           |
| `n`               | integer | 否   | 生成数量（1-10）                   |
| `size`            | string  | 否   | 图像尺寸                           |
| `quality`         | string  | 否   | 图像质量（standard, hd）           |
| `response_format` | string  | 否   | 响应格式（url, b64_json）          |
| `style`           | string  | 否   | 图像风格（vivid, natural）         |
| `user`            | string  | 否   | 用户标识                           |

**请求示例：**

```bash
curl https://api.openai.com/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "dall-e-3",
    "prompt": "一只可爱的猫在花园里玩耍",
    "n": 1,
    "size": "1024x1024",
    "quality": "standard",
    "response_format": "url",
    "style": "vivid"
  }'
```

**响应示例：**

```json
{
  "created": 1677652288,
  "data": [
    {
      "url": "https://oaidalleapiprodscus.blob.core.windows.net/private/...",
      "revised_prompt": "一只可爱的猫在花园里玩耍，背景是美丽的花朵"
    }
  ]
}
```

### 5. 音频转录（Audio Transcriptions）

**端点：** `POST https://api.openai.com/v1/audio/transcriptions`

**用途：** 将音频转换为文本

**请求参数：**

| 参数                      | 类型   | 必需 | 说明                                           |
| ------------------------- | ------ | ---- | ---------------------------------------------- |
| `file`                    | file   | 是   | 音频文件                                       |
| `model`                   | string | 是   | 转录模型（whisper-1）                          |
| `language`                | string | 否   | 语言代码                                       |
| `prompt`                  | string | 否   | 提示文本                                       |
| `response_format`         | string | 否   | 响应格式（json, text, srt, verbose_json, vtt） |
| `temperature`             | number | 否   | 温度参数（0-1）                                |
| `timestamp_granularities` | array  | 否   | 时间戳粒度                                     |

**请求示例：**

```bash
curl https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F file="@audio.mp3" \
  -F model="whisper-1" \
  -F language="zh" \
  -F response_format="json" \
  -F temperature=0.0
```

**响应示例：**

```json
{
  "text": "想象一下你曾经有过的最疯狂的想法，并且你想知道它如何扩展到100倍、1000倍的规模。"
}
```

### 6. 文本转语音（Text-to-Speech）

**端点：** `POST https://api.openai.com/v1/audio/speech`

**用途：** 将文本转换为语音

**请求参数：**

| 参数              | 类型   | 必需 | 说明                                                |
| ----------------- | ------ | ---- | --------------------------------------------------- |
| `model`           | string | 是   | TTS 模型（tts-1, tts-1-hd）                         |
| `input`           | string | 是   | 输入文本                                            |
| `voice`           | string | 是   | 语音类型（alloy, echo, fable, onyx, nova, shimmer） |
| `response_format` | string | 否   | 响应格式（mp3, opus, aac, flac）                    |
| `speed`           | number | 否   | 语速（0.25-4.0）                                    |
| `user`            | string | 否   | 用户标识                                            |

**请求示例：**

```bash
curl https://api.openai.com/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "tts-1",
    "input": "你好，欢迎使用语音服务！",
    "voice": "alloy",
    "response_format": "mp3",
    "speed": 1.0
  }'
```

**响应：** 返回音频文件的二进制数据

### 7. 流式处理

**流式聊天补全：**

```bash
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "讲一个故事"}],
    "stream": true
  }'
```

**流式响应格式：**

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":"从前"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"有"},"finish_reason":null}]}

data: [DONE]
```

### 8. 错误处理

**错误响应格式：**

```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

**常见错误码：**

- `400`：请求错误
- `401`：认证失败
- `429`：速率限制
- `500`：服务器错误

## 第三部分：Spring AI 与 OpenAI API 详细对应关系

### 1. 聊天补全（Chat Completions）

#### OpenAI API

```bash
POST https://api.openai.com/v1/chat/completions
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### Spring AI 对应

```java
// 配置
@Configuration
public class OpenAiConfig {
    
    @Bean
    public OpenAiChatModel openAiChatModel() {
        return new OpenAiChatModel(
            new OpenAiApi("your-api-key", "https://api.openai.com"),
            OpenAiChatOptions.builder()
                .withModel("gpt-4")
                .withTemperature(0.7f)
                .withMaxTokens(1000)
                .withTopP(0.9f)
                .withFrequencyPenalty(0.0f)
                .withPresencePenalty(0.0f)
                .withStop(Arrays.asList("Human:", "AI:"))
                .withN(1)
                .withUser("spring-ai-app")
                .build()
        );
    }
    
    @Bean
    public ChatClient chatClient(OpenAiChatModel chatModel) {
        return ChatClient.create(chatModel);
    }
}

// 使用
@RestController
public class ChatController {
    
    private final ChatClient chatClient;
    
    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }
    
    @PostMapping("/chat")
    public String chat(@RequestBody String message) {
        return chatClient.prompt()
            .system("你是一个助手")
            .user(message)
            .call()
            .content();
    }
    
    // 流式处理
    @PostMapping(value = "/stream", produces = MediaType.TEXT_PLAIN_VALUE)
    public ResponseEntity<StreamingResponseBody> streamChat(@RequestBody String message) {
        return ResponseEntity.ok()
            .contentType(MediaType.TEXT_PLAIN)
            .body(outputStream -> {
                chatClient.prompt()
                    .user(message)
                    .stream()
                    .content()
                    .forEach(content -> {
                        try {
                            outputStream.write(content.getBytes());
                            outputStream.flush();
                        } catch (IOException e) {
                            throw new RuntimeException(e);
                        }
                    });
            });
    }
}
```

#### 参数映射关系

| OpenAI API 参数     | Spring AI 配置                             | 说明             |
| ------------------- | ------------------------------------------ | ---------------- |
| `model`             | `OpenAiChatOptions.withModel()`            | 模型名称         |
| `messages`          | `Prompt` 构建                              | 消息列表         |
| `temperature`       | `OpenAiChatOptions.withTemperature()`      | 温度参数 (0-2)   |
| `max_tokens`        | `OpenAiChatOptions.withMaxTokens()`        | 最大标记数       |
| `top_p`             | `OpenAiChatOptions.withTopP()`             | 核采样参数 (0-1) |
| `stream`            | `ChatClient.stream()`                      | 流式输出         |
| `stop`              | `OpenAiChatOptions.withStop()`             | 停止序列         |
| `presence_penalty`  | `OpenAiChatOptions.withPresencePenalty()`  | 存在惩罚 (-2到2) |
| `frequency_penalty` | `OpenAiChatOptions.withFrequencyPenalty()` | 频率惩罚 (-2到2) |
| `n`                 | `OpenAiChatOptions.withN()`                | 生成数量         |
| `user`              | `OpenAiChatOptions.withUser()`             | 用户标识         |

### 2. 文本补全（Completions）

#### OpenAI API

```bash
POST https://api.openai.com/v1/completions
{
  "model": "text-davinci-003",
  "prompt": "写一首诗",
  "max_tokens": 100,
  "temperature": 0.7
}
```

#### Spring AI 对应

```java
// 配置
@Configuration
public class CompletionConfig {
    
    @Bean
    public OpenAiCompletionModel openAiCompletionModel() {
        return new OpenAiCompletionModel(
            new OpenAiApi("your-api-key", "https://api.openai.com"),
            OpenAiCompletionOptions.builder()
                .withModel("text-davinci-003")
                .withTemperature(0.7f)
                .withMaxTokens(100)
                .withTopP(0.9f)
                .withFrequencyPenalty(0.0f)
                .withPresencePenalty(0.0f)
                .withStop(Arrays.asList("\n\n"))
                .withN(1)
                .withUser("spring-ai-app")
                .build()
        );
    }
}

// 使用
@Service
public class CompletionService {
    
    private final OpenAiCompletionModel completionModel;
    
    public String complete(String prompt) {
        return completionModel.call(prompt);
    }
}
```

### 3. 嵌入（Embeddings）

#### OpenAI API

```bash
POST https://api.openai.com/v1/embeddings
{
  "model": "text-embedding-ada-002",
  "input": "机器学习的基本概念",
  "encoding_format": "float",
  "dimensions": 1536
}
```

#### Spring AI 对应

```java
// 配置
@Configuration
public class EmbeddingConfig {
    
    @Bean
    public OpenAiEmbeddingModel openAiEmbeddingModel() {
        return new OpenAiEmbeddingModel(
            new OpenAiApi("your-api-key", "https://api.openai.com"),
            OpenAiEmbeddingOptions.builder()
                .withModel("text-embedding-ada-002")
                .withEncodingFormat("float")
                .withDimensions(1536)
                .withUser("spring-ai-app")
                .build()
        );
    }
}

// 使用
@Service
public class EmbeddingService {
    
    private final OpenAiEmbeddingModel embeddingModel;
    
    public List<Double> embed(String text) {
        return embeddingModel.embed(text);
    }
    
    public List<List<Double>> embed(List<String> texts) {
        return embeddingModel.embed(texts);
    }
    
    // 批量嵌入
    public EmbeddingResponse embedBatch(List<String> texts) {
        return embeddingModel.call(texts);
    }
}
```

#### 参数映射关系

| OpenAI API 参数   | Spring AI 配置                                | 说明         |
| ----------------- | --------------------------------------------- | ------------ |
| `model`           | `OpenAiEmbeddingOptions.withModel()`          | 嵌入模型名称 |
| `input`           | `EmbeddingModel.embed()`                      | 输入文本     |
| `encoding_format` | `OpenAiEmbeddingOptions.withEncodingFormat()` | 编码格式     |
| `dimensions`      | `OpenAiEmbeddingOptions.withDimensions()`     | 嵌入维度     |
| `user`            | `OpenAiEmbeddingOptions.withUser()`           | 用户标识     |

### 4. 图像生成（Images）

#### OpenAI API

```bash
POST https://api.openai.com/v1/images/generations
{
  "model": "dall-e-3",
  "prompt": "一只可爱的猫",
  "n": 1,
  "size": "1024x1024",
  "quality": "standard",
  "response_format": "url",
  "style": "vivid"
}
```

#### Spring AI 对应

```java
// 配置
@Configuration
public class ImageConfig {
    
    @Bean
    public OpenAiImageModel openAiImageModel() {
        return new OpenAiImageModel(
            new OpenAiApi("your-api-key", "https://api.openai.com"),
            OpenAiImageOptions.builder()
                .withModel("dall-e-3")
                .withN(1)
                .withSize("1024x1024")
                .withQuality("standard")
                .withResponseFormat("url")
                .withStyle("vivid")
                .withUser("spring-ai-app")
                .build()
        );
    }
}

// 使用
@Service
public class ImageService {
    
    private final OpenAiImageModel imageModel;
    
    public ImageResponse generateImage(String prompt) {
        return imageModel.call(prompt);
    }
    
    // 生成多张图片
    public ImageResponse generateImages(String prompt, int count) {
        return imageModel.call(OpenAiImagePrompt.builder()
            .withPrompt(prompt)
            .withN(count)
            .build());
    }
}
```

#### 参数映射关系

| OpenAI API 参数   | Spring AI 配置                            | 说明            |
| ----------------- | ----------------------------------------- | --------------- |
| `model`           | `OpenAiImageOptions.withModel()`          | 图像模型名称    |
| `prompt`          | `ImageModel.call()`                       | 图像描述        |
| `n`               | `OpenAiImageOptions.withN()`              | 生成数量 (1-10) |
| `size`            | `OpenAiImageOptions.withSize()`           | 图像尺寸        |
| `quality`         | `OpenAiImageOptions.withQuality()`        | 图像质量        |
| `response_format` | `OpenAiImageOptions.withResponseFormat()` | 响应格式        |
| `style`           | `OpenAiImageOptions.withStyle()`          | 图像风格        |
| `user`            | `OpenAiImageOptions.withUser()`           | 用户标识        |

### 5. 音频转录（Audio Transcriptions）

#### OpenAI API

```bash
POST https://api.openai.com/v1/audio/transcriptions
-F file="@audio.mp3"
-F model="whisper-1"
-F language="zh"
-F response_format="json"
-F temperature=0.0
```

#### Spring AI 对应

```java
// 配置
@Configuration
public class AudioConfig {
    
    @Bean
    public OpenAiAudioTranscriptionModel openAiAudioTranscriptionModel() {
        return new OpenAiAudioTranscriptionModel(
            new OpenAiApi("your-api-key", "https://api.openai.com"),
            OpenAiAudioTranscriptionOptions.builder()
                .withModel("whisper-1")
                .withLanguage("zh")
                .withResponseFormat("json")
                .withTemperature(0.0f)
                .withTimestampGranularities(Arrays.asList("word", "segment"))
                .withUser("spring-ai-app")
                .build()
        );
    }
}

// 使用
@Service
public class AudioService {
    
    private final OpenAiAudioTranscriptionModel transcriptionModel;
    
    public String transcribe(Resource audioFile) {
        return transcriptionModel.call(audioFile);
    }
    
    // 从文件路径转录
    public String transcribeFromFile(String filePath) {
        Resource audioFile = new FileSystemResource(filePath);
        return transcriptionModel.call(audioFile);
    }
}
```

#### 参数映射关系

| OpenAI API 参数           | Spring AI 配置                                               | 说明       |
| ------------------------- | ------------------------------------------------------------ | ---------- |
| `model`                   | `OpenAiAudioTranscriptionOptions.withModel()`                | 转录模型   |
| `file`                    | `AudioTranscriptionModel.call()`                             | 音频文件   |
| `language`                | `OpenAiAudioTranscriptionOptions.withLanguage()`             | 语言代码   |
| `response_format`         | `OpenAiAudioTranscriptionOptions.withResponseFormat()`       | 响应格式   |
| `temperature`             | `OpenAiAudioTranscriptionOptions.withTemperature()`          | 温度参数   |
| `timestamp_granularities` | `OpenAiAudioTranscriptionOptions.withTimestampGranularities()` | 时间戳粒度 |
| `user`                    | `OpenAiAudioTranscriptionOptions.withUser()`                 | 用户标识   |

### 6. 文本转语音（Text-to-Speech）

#### OpenAI API

```bash
POST https://api.openai.com/v1/audio/speech
{
  "model": "tts-1",
  "input": "你好，欢迎使用语音服务！",
  "voice": "alloy",
  "response_format": "mp3",
  "speed": 1.0
}
```

#### Spring AI 对应

```java
// 配置
@Configuration
public class TTSConfig {
    
    @Bean
    public OpenAiAudioSpeechModel openAiAudioSpeechModel() {
        return new OpenAiAudioSpeechModel(
            new OpenAiApi("your-api-key", "https://api.openai.com"),
            OpenAiAudioSpeechOptions.builder()
                .withModel("tts-1")
                .withVoice("alloy")
                .withResponseFormat("mp3")
                .withSpeed(1.0f)
                .withUser("spring-ai-app")
                .build()
        );
    }
}

// 使用
@Service
public class TTSService {
    
    private final OpenAiAudioSpeechModel speechModel;
    
    public byte[] synthesize(String text) {
        return speechModel.call(text);
    }
    
    // 保存为文件
    public void synthesizeToFile(String text, String outputPath) {
        byte[] audioData = speechModel.call(text);
        try {
            Files.write(Paths.get(outputPath), audioData);
        } catch (IOException e) {
            throw new RuntimeException("保存音频文件失败", e);
        }
    }
}
```

#### 参数映射关系

| OpenAI API 参数   | Spring AI 配置                                  | 说明     |
| ----------------- | ----------------------------------------------- | -------- |
| `model`           | `OpenAiAudioSpeechOptions.withModel()`          | TTS 模型 |
| `input`           | `AudioSpeechModel.call()`                       | 输入文本 |
| `voice`           | `OpenAiAudioSpeechOptions.withVoice()`          | 语音类型 |
| `response_format` | `OpenAiAudioSpeechOptions.withResponseFormat()` | 响应格式 |
| `speed`           | `OpenAiAudioSpeechOptions.withSpeed()`          | 语速     |
| `user`            | `OpenAiAudioSpeechOptions.withUser()`           | 用户标识 |

## 总结

Spring AI 通过统一的 API 对 OpenAI 的各种接口进行了完整封装，主要对应关系包括：

1. **ChatClient** ↔ **Chat Completions API** - 聊天对话
2. **EmbeddingModel** ↔ **Embeddings API** - 文本嵌入
3. **ImageModel** ↔ **Images API** - 图像生成
4. **AudioTranscriptionModel** ↔ **Audio Transcriptions API** - 音频转录
5. **AudioSpeechModel** ↔ **Text-to-Speech API** - 文本转语音
6. **CompletionModel** ↔ **Completions API** - 文本补全

这种设计使得开发者可以：

- 使用统一的 API 访问不同的 AI 功能
- 轻松切换不同的模型提供商
- 享受 Spring 生态系统的所有优势
- 简化配置和错误处理
- 支持流式处理和异步操作
- 实现复杂的多模态 AI 应用

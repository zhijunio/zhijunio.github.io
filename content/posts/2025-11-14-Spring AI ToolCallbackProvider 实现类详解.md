---
title: "Spring AI ToolCallbackProvider 详解：4 种实现类对比"
date: 2025-11-14 08:00:00+08:00
slug: spring-ai-ToolCallbackProvider
description: "深入解析 Spring AI ToolCallbackProvider 接口及其实现类：MethodToolCallbackProvider、SyncMcpToolCallbackProvider、AsyncMcpToolCallbackProvider、StaticToolCallbackProvider。学习工具调用的最佳实践、使用场景对比和配置示例。"
categories: [ "tech" ]
tags: [ "spring-ai", "mcp" ]
favicon: "spring-ai.svg"
---

`ToolCallbackProvider` 是 Spring AI 中用于提供工具回调的接口。本文将详细介绍其主要实现类及其使用场景。

> **版本说明**：本文基于 Spring AI 1.1.0 版本编写，代码示例和 API 说明均基于此版本。随着框架的不断发展，部分 API 可能会有变化，建议参考 [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/)获取最新信息。

## 接口定义

```java
public interface ToolCallbackProvider {
    ToolCallback[] getToolCallbacks();
}
```

## 主要实现类

### 1. MethodToolCallbackProvider

**用途**：包装本地带有 `@Tool` 注解的方法，将其转换为工具回调。

**包路径**：`org.springframework.ai.tool.method.MethodToolCallbackProvider`

**使用场景**：

- 本地工具（同一应用内）
- 使用 `@Tool` 注解的方法
- 需要将 Spring Bean 的方法暴露为工具

**示例代码**：

```java
@Service
class WeatherService {
    @Tool(description = "Get weather for a location")
    String getWeather(@ToolParam(description = "City name") String city) {
        return "Sunny, 25°C in " + city;
    }
    
    @Tool(description = "Get forecast")
    String getForecast(@ToolParam String city, @ToolParam int days) {
        return "Forecast for " + city " for " + days + " days";
    }
}

// 配置 Bean
@Bean
MethodToolCallbackProvider weatherTools(WeatherService weatherService) {
    return MethodToolCallbackProvider
        .builder()
        .toolObjects(weatherService)  // 传入带有 @Tool 注解的对象
        .build();
}

// 使用
ChatClient chatClient = ChatClient.builder(chatModel)
    .defaultToolCallbacks(weatherTools)
    .build();
```

**特点**：

- ✅ 自动扫描 `@Tool` 注解的方法
- ✅ 支持多个工具对象
- ✅ 自动处理参数类型转换
- ✅ 与 Spring Bean 集成良好

**Builder 方法**：

```java
MethodToolCallbackProvider.builder()
    .toolObjects(object1, object2, ...)  // 添加工具对象
    .build();
```

---

### 2. SyncMcpToolCallbackProvider

**用途**：通过 MCP（Model Context Protocol）协议调用远程工具。

**包路径**：`org.springframework.ai.mcp.SyncMcpToolCallbackProvider`

**使用场景**：

- 远程工具（微服务架构）
- MCP 服务器提供的工具
- 需要跨服务调用工具

**示例代码**：

```java
// 1. 创建 MCP 客户端
@Bean
McpSyncClient schedulerMcp() {
    var mcp = McpClient
        .sync(HttpClientSseClientTransport.builder("http://localhost:8081/").build())
        .build();
    mcp.initialize();
    return mcp;
}

// 2. 创建 SyncMcpToolCallbackProvider
@Bean
SyncMcpToolCallbackProvider mcpToolProvider(McpSyncClient schedulerMcp) {
    return SyncMcpToolCallbackProvider
        .builder()
        .mcpClients(schedulerMcp)  // 传入 MCP 客户端
        .build();
}

// 3. 使用
ChatClient chatClient = ChatClient.builder(chatModel)
    .defaultToolCallbacks(mcpToolProvider)
```

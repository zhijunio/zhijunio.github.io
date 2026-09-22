# Spring AI TypeSafe Jev 与 Model Router 研究摘要

## 来源

- [Spring AI and TypeSafe Jev: Fast, Cheap, Structured Decisions](https://spring.io/blog/2026/09/21/spring-ai-typesafe-structured-judgment)
- [danvega/spring-ai-model-router](https://github.com/danvega/spring-ai-model-router)

## 核心事实

- TypeSafe Jev 不是 Chat Model，而是针对给定 state/context 回答结构化问题的判断能力。
- 基本问题类型包括 `Noul`、`Choice` 和 `Score`。
- `Choice` 返回选项、置信度和概率分布；选项描述会影响判断质量。
- `Score` 返回连续评分，不应简单理解为离散等级。
- `JevJudge` 可组合多个标准和阈值，对模型回答做 LLM-as-a-Judge。
- `JevSelfRefineAdvisor` 在判断失败时把反馈加入原始请求并重试；`JevGuardrailAdvisor` 做安全检查但不重试。
- TypeSafe 还可用于文档过滤、重排、工具选择和模型路由。
- Jev 不负责 token-by-token 流式生成，不能替代 Chat Model。

## Model Router 核实结果

- 示例是 Spring Boot 应用，核心类为 `ModelTier`、`RoutingDecision`、`ModelRouter` 和 `ChatController`。
- `ModelRouter` 将模型层级注册为一个 `Choice`，通过 `TypeSafeClient.systemOne` 选择层级。
- `RoutingDecision` 保存层级、模型 ID、置信度和完整概率分布。
- `ChatController` 先路由，再通过 Spring AI `ChatClient` 和 `OpenAiChatOptions` 使用选中的模型生成答案。
- 示例测试通过 Mockito 模拟 `TypeSafeClient`，验证选择结果转换和四个层级选项。
- 示例本身没有实现置信度阈值、故障转移、实时价格和负载感知，生产使用需要补充。

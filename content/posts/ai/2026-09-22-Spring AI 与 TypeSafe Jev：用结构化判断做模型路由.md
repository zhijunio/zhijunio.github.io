---
title: "Spring AI 与 TypeSafe Jev：用结构化判断做模型路由"
date: 2026-09-22 10:00:00+08:00
slug: spring-ai-typesafe-jev-model-router
category: ai
tags: ["spring-ai", "java", "llm"]
description: "介绍 Spring AI TypeSafe Jev 的结构化判断模型，并结合 Model Router 示例，实现按请求难度选择模型的成本优化方案。"
---

很多 AI 应用一开始只有一个模型：所有请求都交给同一个 Chat Model。这样简单，但也有一个明显问题：一句“你好”和一份多地域数据库容灾方案，真的需要同样昂贵、同样强大的模型吗？

更合理的架构是先做一个轻量判断，再决定后续动作：请求是否安全、答案是否可信、应该选择哪个模型。Spring AI 社区最近介绍的 TypeSafe Jev，正好提供了这种“结构化判断”能力；Dan Vega 的 `spring-ai-model-router` 示例则把它落成了一个很直观的模型路由器。

<!--more-->

## 先说结论：Jev 不是 Chat Model

Spring AI TypeSafe 集成了 TypeSafe AI 提供的 Jev API。它与 Chat Model 的职责不同：Chat Model 负责生成自然语言答案，Jev 负责针对给定上下文回答结构化问题，例如：

- 这个请求是否紧急？
- 这段答案是否有依据？
- 这个提示词应该交给哪个模型层级？
- 这个请求是否触发了某个安全标准？

可以把一次调用理解成下面的链路：

```text
用户请求
   │
   ▼
Jev：回答结构化问题
   │  Choice / Score / Noul
   ▼
Spring 应用按结果做决定
   │
   ├── 选择模型
   ├── 拒绝请求
   ├── 重试并改进答案
   └── 过滤或重排检索结果
```

Jev 的价值不在于生成一段更漂亮的文字，而在于把判断结果变成应用容易消费的类型和数值。这样业务代码不必从一段自由文本里解析 `yes`、`no` 或模型名称。

## TypeSafe 的三个基本问题类型

Spring AI TypeSafe 的核心思路，是把自然语言判断拆成原子问题，并让每个问题拥有明确的类型和语义。

### Choice：从候选项中选择一个

模型路由最适合使用 `Choice`。例如，我们定义四个模型层级：

```java
Choice tierChoice = Choice.builder()
    .instructions("Which model tier is the cheapest one that can still answer this prompt well?")
    .option("LUNA", "问候、单行事实、简单格式化和短改写")
    .option("TERRA", "摘要、概念解释和短函数")
    .option("SOL", "多步推理、跨文件代码和详细分析")
    .option("ASTRA", "深度研究、系统架构、复杂调试和高风险任务")
    .build();
```

`Choice` 的结果不只是一个标签。示例中的 `ChoiceAnswer` 还可以提供置信度和每个候选项的概率。应用因此能够知道“选了 SOL”，也能够知道“SOL 与 TERRA 的差距是否很小”。

### Score：按标准打分

`Score` 适合判断质量等级，例如帮助性、事实准确性或相关性。关键不是让模型随意返回一个数字，而是给出一套明确的评分标准和阈值。

```java
JevJudge judge = JevJudge.builder(typeSafeClient)
    .score("helpfulness", helpfulnessRubric, 2.0d)
    .build();
```

这里的 `2.0` 是通过标准所需的最低分，不一定代表简单的整数等级。评分标准越具体，判断结果越稳定。

### Noul：判断一个陈述是否成立

`Noul` 适合布尔式判断，但返回的不是 Java `boolean`，而是表示“为真程度”的 `double`。阈值通常由 `JevJudge` 在评价标准中定义，而不是由 `Noul` 本身携带。例如：

```java
JevJudge judge = JevJudge.builder(typeSafeClient)
    .noul("is_plausible", plausible, 0.8d)
    .noul("is_grounded", grounded, 0.8d)
    .build();
```

`Noul` 可以表达“答案是否有依据”“内容是否合理”等问题。要注意：问题应该写成关于当前上下文的清晰陈述，而不是只给模型一个含义模糊的标签。

例如返回 `0.95`，表示模型认为该陈述很可能成立；返回 `0.5` 则表示判断不确定。应用是否把它当作通过，应该由业务阈值决定。

## 为什么结构化判断比解析文本可靠

传统做法可能是让 Chat Model 返回：

```text
模型：这个请求比较复杂，我建议使用 SOL。
```

应用再从文本里提取 `SOL`。这种方案有几个问题：

- 模型可能在标签周围添加额外文字；
- 标签可能大小写不一致；
- 结果可能出现多个候选项；
- 置信度没有统一定义；
- 提示词稍微变化，解析器就可能失效。

TypeSafe 的思路是把问题定义为结构化的 `Choice`、`Score` 或 `Noul`，由客户端直接读取类型化结果。应用代码拿到的是领域数据，而不是一段需要猜测的文本。

这并不意味着 Jev 完全不依赖模型。它仍然是在做模型判断，只是把判断任务限定得更窄，并用结构化协议承载结果。窄问题、清晰描述和独立阈值，是稳定性的来源。

## Model Router：把 Jev 接入 Spring AI

`spring-ai-model-router` 的设计非常小，核心只有四个类型：

```text
ModelTier       模型层级和模型 ID
RoutingDecision 路由结果、置信度和概率
ModelRouter     调用 Jev 做选择
ChatController  按选择调用 ChatClient
```

### 1. 用枚举集中管理模型层级

```java
public enum ModelTier {
    LUNA("gpt-5.6-luna", "简单、低风险请求"),
    TERRA("gpt-5.6-terra", "日常解释和短代码"),
    SOL("gpt-5.6-sol", "多步推理和复杂代码"),
    ASTRA("gpt-6-astra", "研究、架构和高风险任务");

    private final String modelId;
    private final String description;

    // 构造器和访问方法略
}
```

这里把“选择标签”和“实际模型 ID”分开。Jev 只需要判断 `LUNA`、`TERRA` 等稳定标签；模型供应商或具体模型 ID 可以在代码配置中替换。

### 2. ModelRouter 只负责判断

仓库中的核心逻辑是：把用户提示词作为 state，向 Jev 提出一个 `Choice` 问题，然后把结果转换成 `RoutingDecision`。

```java
@Service
public class ModelRouter {

    static final String QUESTION = "tier";
    private final TypeSafeClient typeSafeClient;
    private final Choice tierChoice;

    public ModelRouter(TypeSafeClient typeSafeClient) {
        this.typeSafeClient = typeSafeClient;
        Choice.Builder choice = Choice.builder()
            .instructions("Which model tier is the cheapest one that can still answer this prompt well?");
        for (ModelTier tier : ModelTier.values()) {
            choice.option(tier.name(), tier.description());
        }
        this.tierChoice = choice.build();
    }

    public RoutingDecision route(String prompt) {
        ChoiceAnswer answer = typeSafeClient
            .systemOne(prompt, Map.of(QUESTION, tierChoice))
            .choice(QUESTION);

        ModelTier tier = ModelTier.valueOf(answer.value());
        return new RoutingDecision(
            tier,
            tier.modelId(),
            answer.confidence(),
            answer.probabilities());
    }
}
```

这段代码有三个值得注意的设计点：

1. `Choice` 在构造时创建一次，不要每次请求都重新描述候选项。
2. 路由器返回 `RoutingDecision`，而不是只返回一个字符串，保留置信度和概率方便观测与降级。
3. `ModelRouter` 不负责生成最终答案，只负责选择；职责边界很清楚。

### 3. ChatController 再调用选中的模型

```java
@PostMapping("/chat")
public ChatResult chat(@RequestBody ChatRequest request) {
    RoutingDecision decision = router.route(request.prompt());

    String answer = chatClient.prompt()
        .user(request.prompt())
        .options(OpenAiChatOptions.builder()
            .model(decision.model()))
        .call()
        .content();

    return new ChatResult(decision, answer);
}
```

最终响应同时返回答案和路由决策，这对演示和排查很有用。生产系统也可以把它写入指标或 trace，而不一定直接暴露给终端用户。

## 运行方式与请求示例

示例仓库要求 JDK 27，并需要两类凭证：OpenAI 的模型调用凭证和 TypeSafe 的 Jev 凭证。配置好后运行：

```bash
export OPENAI_API_KEY=...
export TYPESAFE_API_KEY=...
./mvnw spring-boot:run
```

发送简单请求：

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"hello there"}'
```

再发送复杂请求：

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Design a multi-region failover strategy for a Postgres cluster."}'
```

按照示例的预期，问候语会路由到较便宜的 `luna`，多地域数据库架构问题会路由到 `astra`。这不是硬编码的关键词匹配，而是 Jev 根据每个层级的描述做出的结构化选择。

## 成本优化，但不是“永远选最便宜的模型”

模型路由的目标不是让所有请求都走最小模型，而是找到“仍然能够把事情做好”的最低层级。

因此，路由描述应该强调质量下限：

```text
选择仍能高质量回答当前请求的最便宜模型。
如果低层级明显不够，再选择更强模型。
```

如果路由置信度低，可以增加保护策略：

- 低于阈值时升级到更强模型；
- 记录概率分布，观察相邻层级是否经常难以区分；
- 对高风险请求设置固定的最低模型层级；
- 先做规则拦截，再让 Jev 处理需要语义理解的灰度情况。

例如：

```java
if (decision.confidence() < 0.70) {
    return chatWith("gpt-5.6-sol", prompt);
}
```

这段只是保护性示例，阈值需要用真实请求集评估，不能直接把 `0.70` 当成通用标准。

## Jev 还能做什么？

Spring AI TypeSafe 不只适合模型路由。Spring 官方文章给出的几个例子，都遵循同一个模式：让 Chat Model 生成内容，让 Jev 判断内容是否满足明确标准，再由 Spring AI 的组件决定下一步。

### 1. LLM-as-a-Judge：评价模型回答

先定义评价标准，再把问题和答案交给 `JevJudge`：

```java
JevJudge judge = JevJudge.builder(typeSafeClient)
    .score("helpfulness", helpfulnessRubric, 2.0d)
    .noul("is_plausible", plausible, 0.8d)
    .noul("is_grounded", grounded, 0.8d)
    .build();

JevVerdict verdict = judge.judge(question, answer);
```

这段代码里有三个标准：帮助性至少达到 `2.0`，答案合理性和事实依据的置信度都至少达到 `0.8`。`verdict` 不只是一个总的 `passed`，还会保留每个标准的通过、失败或不确定状态，便于定位答案为什么没有通过。

适合用在：客服答案质检、RAG 答案评估、自动评测集和发布前回归测试。需要注意，LLM-as-a-Judge 仍然是模型判断，不能把它当成绝对事实；高风险领域应叠加规则、人工审核或领域校验。

### 2. Self-Refine：失败后让模型重写

官方示例使用 `JevSelfRefineAdvisor` 把 Judge 接到 `ChatClient` 上：

```java
ChatClient chatClient = ChatClient.builder(chatModel)
    .defaultTools(new WeatherTools())
    .defaultAdvisors(
        JevSelfRefineAdvisor.builder()
            .judge(WeatherJudge.create(typeSafeClient))
            .maxRepeatAttempts(3)
            .build())
    .build();
```

运行过程是：

```text
Chat Model 生成答案
       │
       ▼
JevJudge 检查所有标准
       │
       ├── 全部通过 → 返回答案
       │
       └── 有标准失败 → 把失败原因反馈给原始请求 → 重试
```

这里的 `WeatherJudge` 是业务方定义的 Judge。假设第一次生成了不可能的温度，Jev 可以报告 `is_plausible` 失败，并说明“低于绝对零度或远超地球记录”；Advisor 再把这个反馈交给模型，最多重试三次。

这和普通的“把上一次答案继续追加到 prompt”不同：官方示例强调每次重试基于原始问题重新构建请求，反馈不会无限累积。默认达到次数上限后会返回最后一次结果；如果业务不能接受不通过的结果，可以配置耗尽重试时抛出异常。

适合用在质量问题可以通过重写解决的场景，例如格式不完整、缺少必要信息、数值不合理或答案没有覆盖要求。它不适合安全拦截，安全问题不应该通过多试几次来解决。

### 3. Guardrail：安全检查不重试

官方文章把质量重试和安全拦截明确分开：

```java
ChatClient.builder(chatModel)
    .defaultAdvisors(
        JevSelfRefineAdvisor.builder()
            .judge(judge)
            .build(),                         // 质量：失败后重试
        JevGuardrailAdvisor.builder(typeSafeClient)
            .build())                         // 安全：最后拦截
    .build();
```

`JevGuardrailAdvisor` 会检查用户输入和模型输出，但不会把不安全结果当成草稿再次生成。这样可以覆盖两个方向：

- 输入检查：危险请求在到达 Chat Model 前被拦截，避免无效生成和费用；
- 输出检查：即使输入看起来正常，模型仍可能生成不安全答案，因此返回前还要检查一次。

文章示例中的风险类别包括 jailbreak、physical harm、illegal 和 self-harm。默认处理并不等于适合所有产品：例如自伤相关请求通常应给出支持和求助引导，而不是简单返回空白错误。生产环境还需要结合产品政策、地区法规和人工升级流程。

### 4. RAG：先过滤，再重排

TypeSafe 文档还提供了 `JevDocumentFilter` 和 `JevDocumentReranker`。它们的职责可以这样理解：

```text
检索候选文档
       │
       ▼
JevDocumentFilter：无关或可疑文档先过滤
       │
       ▼
JevDocumentReranker：对剩余文档排序
       │
       ▼
交给 Chat Model 生成答案
```

Spring 官方文章特别提醒：文档级操作通常是“一份文档一次判断”。如果直接对 Top 20 文档全部重排，可能产生 20 次调用；先过滤，再对少量幸存文档重排，成本更可控。这个示例的具体构造器应以 [JevDocumentFilter 文档](https://spring-ai-community.github.io/spring-ai-typesafe/latest/rag/JevDocumentFilter/) 和 [JevDocumentReranker 文档](https://spring-ai-community.github.io/spring-ai-typesafe/latest/rag/JevDocumentReranker/) 为准，文章原文主要展示能力边界，没有给出完整可复制代码。

### 5. 工具选择：别忘了“没有工具适用”

`JevToolIndex` 可以用结构化判断从动态工具集合中选工具。但这里有一个容易忽略的限制：`Choice` 必然会选出一个候选项，因为候选概率之和为 1。即使所有工具都不适用，它仍然会选一个“最像”的工具。

因此工具索引需要额外的 `Noul` 判断：

```text
问题一：是否至少有一个工具适合当前请求？  Noul
问题二：如果有，哪个工具最合适？         Choice
```

如果第一个问题为假，应用应返回“没有合适工具”，而不是强行调用 Choice 选出的工具。详见 [JevToolIndex 文档](https://spring-ai-community.github.io/spring-ai-typesafe/latest/toolsearch/JevToolIndex/)。

### 6. 级联：便宜模型先判断，昂贵模型后处理

官方文章还介绍了 cascade demo：先让便宜模型完成结构化提取或判断，只有验证失败时才让更强、更贵的模型接手。

```text
请求
 │
 ▼
便宜模型生成初稿
 │
 ▼
Jev 验证结构和质量
 │
 ├── 通过 → 直接返回
 └── 失败 → 交给更强模型重新处理
```

级联的关键不是“便宜模型永远够用”，而是把大模型预算集中在真正困难的请求上。官方文章也提醒：Jev 更适合做验证，而不是把所有复杂抽取都交给它；级联是否划算，需要用真实的成功率、延迟和调用成本测量。

## 哪些场景不适合用 Jev

Jev 不是 Chat Model 的替代品，也不是所有分类问题都必须引入的新层：

- 需要连续生成文本时，仍然使用 Chat Model；
- 需要 token-by-token 流式输出时，Jev 的非流式判断不适合作为输出通道；
- 简单、稳定、低延迟的规则判断，优先使用普通代码；
- 需要完整解释性答案时，不能只返回一个 Choice 标签；
- 高风险路由不能只相信一次模型判断，应加入规则、阈值、审计和降级策略。

## 面试怎么回答

可以这样概括：

> Spring AI TypeSafe Jev 不是用于生成答案的 Chat Model，而是用于分类、评分和判断的结构化模型能力。它把判断定义成 Choice、Score、Noul 等类型化问题，并返回标签、分数和置信度。模型路由场景中，可以先让 Jev 选择满足质量要求的最低模型层级，再把选择结果传给 Spring AI ChatClient，从而减少简单请求对大模型的消耗，同时保留低置信度升级和高风险兜底策略。

进一步追问时，可以补充：

- 路由决策本身也有成本，必须用真实流量验证节省是否覆盖判断成本；
- `Choice` 的候选描述会影响结果质量，不能只写 `small`、`medium`、`large`；
- 置信度不是业务正确性的证明，只是路由器对候选选择的信号；
- 生产系统应记录模型、路由结果、置信度、延迟、token 和最终质量指标。

## 总结

Spring AI 把不同模型能力统一到 Java/Spring 的调用方式中，TypeSafe Jev 则补充了一个容易被忽略的环节：在生成前后做快速、结构化、可组合的判断。

`spring-ai-model-router` 的价值不在代码量，而在边界清晰：`ModelRouter` 做选择，`ChatClient` 做生成，`RoutingDecision` 保存依据。这个模式可以从模型路由扩展到安全检查、答案评估、检索筛选和自我修正。

但它不是免费午餐。Jev 调用有自己的延迟和成本，候选描述需要评估，低置信度和高风险场景需要兜底。真正可靠的方案不是“让 AI 决定一切”，而是让结构化判断成为一个可观测、可测试、可降级的决策组件。

## 参考资料

- [Spring AI and TypeSafe Jev: Fast, Cheap, Structured Decisions](https://spring.io/blog/2026/09/21/spring-ai-typesafe-structured-judgment)
- [Spring AI TypeSafe 文档](https://spring-ai-community.github.io/spring-ai-typesafe/)
- [danvega/spring-ai-model-router](https://github.com/danvega/spring-ai-model-router)
- [Spring AI ChatClient 文档](https://docs.spring.io/spring-ai/reference/api/chatclient.html)

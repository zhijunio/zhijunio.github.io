---
title: "Spring AI + RAG 实战：基于真实数据的智能推荐"
date: 2025-09-26 08:00:00+08:00
slug: spring-ai-restaurant-showcase-rag
tags: ["spring-boot","spring-ai"]
description: "通过智能餐厅推荐系统示例，介绍如何用 Spring AI 实现 RAG 应用，让模型基于真实餐厅数据生成更准确的推荐结果。"
---

最近在探索 Spring AI 的 RAG 功能，发现它确实是一个很强大的工具。今天就来分享一下如何用 Spring AI 构建一个智能餐厅推荐系统，通过检索增强生成技术让 AI 能够基于真实的餐厅数据给出更准确的推荐。

<!--more-->

## 源代码

如果您想亲自尝试，可以随时查看我的源代码。为此，您必须克隆我的示例 [GitHub 仓库](https://github.com/zhijunio/spring-ai-restaurant-showcase)。然后，您只需按照我的说明进行操作即可。

## 🎯 快速预览

在深入技术细节之前，先看看这个系统能做什么：

**用户问题**：`"我想在北京找一家川菜馆"`

**AI 回答**：

> 根据我的知识库，为您推荐几家北京的优质川菜餐厅：
>
> **峨嵋酒家**（西城区车公庄大街1号）
>
> - 北京老字号川菜，招牌菜宫保鸡丁
> - 人均：100-120元
> - 推荐菜：宫保鸡丁、水煮鱼、夫妻肺片
> - 环境：传统中式装修，适合家庭聚餐
> - 电话：010-6831-2345
>
> **锦府盐帮**（朝阳区三里屯北路45号）
>
> - 融合川南盐商菜与经典川菜
> - 人均：120-150元
> - 推荐菜：退秋鱼、盐帮仔蛙、招牌毛血旺
> - 环境：古风庭院，适合商务宴请
> - 电话：010-6415-6789

**核心特点**：

- 🤖 **智能推荐**：基于真实餐厅数据，不是编造的
- 🎯 **精准匹配**：根据城市、价格、场景等条件筛选
- 💬 **自然对话**：像真人一样回答餐厅相关问题
- 🔒 **完全本地**：使用 Ollama，数据不离开你的电脑

## ⚡ 5分钟快速体验

如果你想立即体验，可以按照以下步骤：

```bash
# 1. 下载项目代码
git clone https://github.com/zhijunio/spring-ai-restaurant-showcase.git
cd spring-ai-restaurant-showcase

# 2. 启动数据库
docker-compose up -d

# 3. 启动 Ollama
ollama serve
ollama pull llama3.2
ollama pull mxbai-embed-large

# 4. 启动应用
mvn spring-boot:run -Pollama-ai

# 5. 加载数据
curl -X POST "http://localhost:8080/api/rag/load" \
  -H "Content-Type: application/json" \
  -d "{"filePath": "classpath:restaurant-knowledge.txt"}"

# 6. 开始聊天
curl -X POST "http://localhost:8080/api/rag/chat" \
  -H "Content-Type: application/json" \
  -d ""我想在北京找一家川菜馆""
```

**预期结果**：你会看到类似上面的智能推荐回答！

> **注意**：确保你的系统已安装 Docker、Maven 和 Ollama。如果没有安装，可以参考下面的详细安装说明。

## 为什么选择 RAG？

AI 模型虽然很聪明，但它只能基于训练时的数据回答问题。如果我想让它推荐我所在城市的餐厅，它可能只能给出一些通用的建议，而不是基于真实、最新的餐厅信息。

**RAG（Retrieval Augmented Generation）** 解决了这个问题：

- 📚 **访问外部知识库**：不再局限于训练数据
- 🎯 **提供准确信息**：基于真实、结构化的数据回答
- 🔄 **实时更新**：知识库可以随时更新，AI 回答也会更及时
- 🚫 **减少幻觉**：避免 AI 编造不存在的信息

**简单来说**：当用户问"北京有什么好吃的川菜馆？"时，AI 从我们精心准备的餐厅数据库中检索相关信息，然后给出具体的推荐。

## 使用 PgVector 进行矢量存储

### 为什么选择 PgVector？

经过一番调研，我选择了 **PgVector** 作为向量存储方案：

- **成本低**：基于 PostgreSQL，不需要额外的云服务
- **易部署**：Docker 一键启动，开发环境友好
- **功能完整**：支持向量相似性搜索，性能也不错
- **Spring AI 支持好**：官方支持，集成简单

### 安装 PgVector

#### 使用 Docker Compose 安装

PgVector 提供了官方的 Docker 镜像，安装非常简单：

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: restaurant-postgres
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    restart: unless-stopped
```

启动 PgVector 数据库：

```bash
docker-compose up -d
```

## 使用 Spring AI 实现 RAG

### 为什么选择 Spring AI？

在尝试了多种方案后，我最终选择了 Spring AI，原因很简单：

- **🎯 开箱即用**：`QuestionAnswerAdvisor` 让 RAG 实现变得极其简单
- **🔧 高度集成**：与 Spring 生态完美融合，配置简单
- **📚 文档完善**：官方文档详细，社区活跃
- **🚀 性能优秀**：内置优化，支持多种向量存储

### 核心依赖

只需要添加几个依赖就能开始：

```xml
<!-- RAG 核心依赖 -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-vector-store-pgvector</artifactId>
</dependency>
<!-- 文档处理和 Ollama 支持 -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-markdown-document-reader</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-advisors-vector-store</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-ollama</artifactId>
</dependency>
```

> **详细依赖列表**：如果你需要完整的 `pom.xml` 配置，可以查看[项目源码](https://github.com/zhijunio/spring-ai-restaurant-showcase)。

### 配置 PgVector

PgVector 的配置很简单，关键是要设置正确的维度：

```yaml
spring:
  vectorstore:
    pgvector:
      index-type: ivfflat
      distance-type: cosine_distance
      dimensions: 1024  # 必须与嵌入模型输出维度一致
      initialize-schema: true  # 自动创建表结构
      table-name: vector_store
```

> **关键点**：`mxbai-embed-large` 输出 1024 维向量，所以 PgVector 的 `dimensions` 必须设置为 1024。

### 配置 AI 模型

#### 为什么选择 Ollama？

在构建 RAG 系统时，我们需要两个关键组件：**聊天模型**（生成回答）和**嵌入模型**（文档向量化）。

大多数云服务只提供聊天模型，嵌入模型需要单独的服务。而 **Ollama 是少数几个同时支持聊天模型和嵌入模型的本地部署方案**，这让 RAG 系统可以完全在本地运行！

**我的选择理由**：

- **🆓 完全免费**：无需 API 密钥，本地运行
- **🔒 隐私安全**：数据不离开本地，无网络传输
- **⚡ 性能优秀**：llama3.2 + mxbai-embed-large 组合
- **🎯 配置简单**：统一部署，一个 base-url 搞定

#### 应用配置

```yaml
spring:
  ai:
    ollama:
      base-url: http://localhost:11434
      chat:
        options:
          model: llama3.2
      embedding:
        options:
          model: mxbai-embed-large
```

> **关键点**：`mxbai-embed-large` 输出 1024 维向量，所以 PgVector 的 `dimensions` 必须设置为 1024。

### 核心实现

Spring AI 让 RAG 实现变得极其简单，核心代码只有几行：

```java
@Service
public class RagChatService {
    private final ChatClient chatClient;
    
    public String chatWithRag(String userMessage) {
        return chatClient.prompt()
                .user(userMessage)
                .call()
                .content();
    }
}
```

**为什么这么简单？** Spring AI 的 `QuestionAnswerAdvisor` 自动处理了向量检索、上下文构建和提示词增强。

> **详细实现**：完整的代码实现请查看[项目源码](https://github.com/zhijunio/spring-ai-restaurant-showcase)。

### 餐厅知识库构建

我准备了一个包含北京、武汉、上海、广州四个城市川菜餐厅的 Markdown 文档。数据格式很简单：

```markdown
# 北京川菜餐厅推荐

### 峨嵋酒家
- 地址：北京市西城区车公庄大街1号
- 特色：北京老字号川菜，招牌菜宫保鸡丁
- 人均：100-120元
- 推荐菜：宫保鸡丁、水煮鱼、夫妻肺片
- 环境：传统中式装修，适合家庭聚餐
- 电话：010-6831-2345
```

**数据特点**：

- 📍 **多城市覆盖**：北京、武汉、上海、广州
- 💰 **价格区间**：从人均50元到200元不等
- 🍽️ **详细信息**：地址、特色、推荐菜、环境、电话

**为什么选择这种格式？** Markdown 结构清晰，Spring AI 的 `MarkdownDocumentReader` 可以自动解析，非常方便。

## 运行应用程序

按照"5分钟快速体验"启动系统后，可以开始测试各种功能。详细的测试命令和高级功能请参考[附录](#附录)。

### 启动系统

按照"5分钟快速体验"章节完成环境准备后，启动应用：

```bash
# 启动应用
mvn spring-boot:run -Pollama-ai

# 加载餐厅数据
curl -X POST "http://localhost:8080/api/rag/load" \
  -H "Content-Type: application/json" \
  -d "{"filePath": "classpath:restaurant-knowledge.txt"}"
```

### 基础测试

**测试 RAG 功能**：

```bash
curl -X POST "http://localhost:8080/api/rag/chat" \
  -H "Content-Type: application/json" \
  -d ""我想在北京找一家川菜馆""
```

**测试文档搜索**：

```bash
curl -X POST "http://localhost:8080/api/rag/search" \
  -H "Content-Type: application/json" \
  -d "{"query": "水煮鱼", "topK": 3}"
```

### 监控和调试

- **健康检查**：`http://localhost:8080/actuator/health`
- **性能指标**：`http://localhost:8080/actuator/prometheus`
- **应用日志**：查看控制台输出的详细日志

### 常见问题

**Q: 应用启动失败？**
A: 检查数据库是否启动，Ollama 是否运行，端口是否被占用。

**Q: 数据加载失败？**
A: 确保 `restaurant-knowledge.txt` 文件存在，检查文件路径是否正确。

**Q: AI 回答不准确？**
A: 检查数据是否正确加载，尝试调整检索参数。

## 附录

### 测试命令和高级功能

#### 基础测试命令

**按城市推荐**：`"我想在北京找一家川菜馆"`
**按价格推荐**：`"推荐一些人均100元左右的川菜馆"`
**按场景推荐**：`"适合商务宴请的川菜餐厅有哪些？"`
**菜品推荐**：`"哪家餐厅的水煮鱼最好吃？"`

> *完整的 curl 命令请参考"运行应用程序"章节。*

#### 高级功能

**个性化推荐**：基于用户偏好的智能推荐

```bash
curl -X POST "http://localhost:8080/api/rag/chat-personalized" \
  -H "Content-Type: application/json" \
  -d "{"message": "推荐川菜馆", "userPreferences": {"city": "北京", "priceRange": "100-150"}}"
```

**向量相似性搜索**：基于语义相似度检索相关文档

```bash
curl -X POST "http://localhost:8080/api/rag/search" \
  -H "Content-Type: application/json" \
  -d "{"query": "水煮鱼", "topK": 3}"
```

**性能监控**：访问 `http://localhost:8080/actuator/prometheus` 查看详细指标。

### Ollama 安装和配置

#### 安装 Ollama

**macOS**：

```bash
brew install ollama
```

**Linux**：

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows**：
下载安装包：[https://ollama.ai/download](https://ollama.ai/download)

#### 下载 AI 模型

**聊天模型**：`ollama pull llama3.2`（约 4.7GB）
**嵌入模型**：`ollama pull mxbai-embed-large`（约 1.2GB）

> *完整的安装步骤请参考"5分钟快速体验"章节。*

#### 模型选择理由

- **llama3.2**：Meta 开源的最新模型，性能优秀，支持中文
- **mxbai-embed-large**：专门优化的嵌入模型，1024 维度，适合向量检索

**关键优势**：Ollama 是少数几个同时支持聊天模型和嵌入模型的本地部署方案，这让 RAG 系统可以完全在本地运行！

### PgVector 手动安装

如果你更喜欢手动安装，可以：

1. **安装 PostgreSQL 16+**
2. **安装 PgVector 扩展**：

   ```bash
   # 使用 pgxn 安装
   pgxn install vector
   
   # 或者从源码编译
   git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   make install
   ```

3. **在数据库中启用扩展**：

   ```sql
   CREATE EXTENSION vector;
   ```

### 配置详解

#### 为什么是 1024 维？

1. **模型匹配**：`mxbai-embed-large` 模型输出 1024 维向量
2. **性能平衡**：1024 维在精度和性能间取得良好平衡
3. **存储效率**：相比 1536 维（OpenAI），存储空间更小
4. **检索质量**：足够表达语义信息，检索效果优秀

#### 索引类型说明

- **ivfflat**：适合中等规模数据集（< 1M 向量）
- **hnsw**：适合大规模数据集，查询速度更快
- **无索引**：适合小规模数据集，简单查询

对于餐厅推荐系统，`ivfflat` 索引已经足够使用。

### PgVector 数据库验证与初始化

如果你需要手动验证数据库安装或重新初始化，可以参考以下步骤：

#### 验证 PgVector 安装

```sql
-- 连接到数据库
docker exec -it restaurant-postgres psql -U postgres

-- 检查 PgVector 扩展是否已安装
\dx

-- 如果未安装，则安装扩展
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 检查向量表

```sql
-- 检查 vector_store 表是否存在
\dt vector_store

-- 查看表结构
\d vector_store
```

#### 重新创建向量表

```sql
-- 删除现有表（谨慎操作！）
DROP TABLE IF EXISTS vector_store CASCADE;

-- 创建新的向量表
CREATE TABLE vector_store (
    id VARCHAR(255) PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1024)  -- 1024 维向量
);

-- 创建向量索引
CREATE INDEX ON vector_store USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- 创建元数据索引（可选，用于过滤查询）
CREATE INDEX ON vector_store USING GIN (metadata);
```

#### 验证表创建

```sql
-- 检查表是否创建成功
\dt vector_store

-- 查看索引信息
\di

-- 测试插入一条记录
INSERT INTO vector_store (id, content, metadata, embedding) 
VALUES (
    "test-1", 
    "测试内容", 
    "{"source": "test"}"::jsonb,
    "[0.1,0.2,0.3]"::vector
);

-- 查询测试记录
SELECT * FROM vector_store WHERE id = "test-1";

-- 清理测试数据
DELETE FROM vector_store WHERE id = "test-1";
```

## 总结与思考

通过这个项目，我深刻体会到了 Spring AI 的强大之处：

### 🎯 核心优势

1. **开箱即用**：`QuestionAnswerAdvisor` 让 RAG 实现变得极其简单
2. **高度集成**：与 Spring 生态完美融合，配置简单
3. **Ollama 本地部署**：完全免费，隐私安全，性能优秀
4. **性能监控**：内置 Prometheus 支持，便于生产环境监控

### 💡 关键收获

- **RAG 不是魔法**：需要高质量的结构化数据作为基础
- **Spring AI 很强大**：大大降低了 AI 应用开发的门槛
- **Ollama 是神器**：本地部署，完全免费，性能优秀，**支持嵌入式模型**
- **双模型支持很重要**：Ollama 同时支持聊天和嵌入模型，这是选择它的核心原因
- **PgVector 够用**：对于中小型应用，完全满足需求
- **维度匹配很重要**：嵌入模型维度必须与向量存储一致

### 🚀 下一步计划

1. **数据优化**：收集更多真实的餐厅数据
2. **功能扩展**：支持图片、菜单等多媒体内容
3. **性能优化**：实现缓存、异步处理等
4. **用户体验**：开发前端界面，让普通用户也能使用

### 📚 学习资源

如果你也想尝试 Spring AI，推荐这些资源：

- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/) - 最权威的参考资料
- [RAG 技术原理](https://arxiv.org/abs/2005.11401) - 深入理解 RAG 原理
- [PgVector 文档](https://github.com/pgvector/pgvector) - 向量数据库使用指南

---

**项目地址**：[GitHub - spring-ai-restaurant-showcase](https://github.com/zhijunio/spring-ai-restaurant-showcase)

*本文基于 Spring AI 1.1.2 版本编写，代码已在实际项目中验证。*

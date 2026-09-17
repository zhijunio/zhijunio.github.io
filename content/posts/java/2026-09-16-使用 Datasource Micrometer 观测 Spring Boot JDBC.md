---
title: "使用 Datasource Micrometer 观测 Spring Boot 的 JDBC"
date: 2026-09-16 15:00:00+08:00
slug: spring-boot-jdbc-datasource-micrometer
category: java
tags: [ "spring-boot", "opentelemetry" ]
description: "Datasource Micrometer 给 JDBC 打 Observation：Trace、Metrics、慢查询。Boot 4 用 2.x，Boot 3.5 用 1.x。生产开 Trace 和指标，不要默认把带参数的 SQL 全量打出去。"
---

[Datasource Micrometer](https://github.com/jdbc-observations/datasource-micrometer) 是 JDBC 代理，用 Micrometer Observation 记连接、SQL、ResultSet。能出 Trace、Metrics，也能打 SQL 日志和慢查询。现在和 Micrometer 分开维护，2025 年底起 start.spring.io 能直接勾 `datasource-micrometer`。

<!--more-->

版本对齐：**1.x 配 Spring Boot 3.5，2.x 配 Spring Boot 4。** 当前文档是 2.3.0 / 1.5.0。勾上 `opentelemetry` 时，Initializr 还会带 `datasource-micrometer-opentelemetry`，属性名走 OpenTelemetry semantic conventions。

日志怎么用 OTLP 发出去，见上一篇 [Logback + OTLP](/posts/spring-boot-logback-otlp-logs)。这篇只补 JDBC 这一段。本地接收端用 Grafana [LGTM](https://github.com/grafana/docker-otel-lgtm)（Loki / Grafana / Tempo / Mimir + OTLP），不是 Lognroll。

## Spring Boot 4+

Java 指定 25，依赖带上 `opentelemetry`、`datasource-micrometer`、`testcontainers`：

```bash
curl -s https://start.spring.io/starter.tgz \
       -d artifactId=counter-api \
       -d name=counter-api \
       -d baseDir=counter-api \
       -d packageName=com.example \
       -d javaVersion=25 \
       -d dependencies=web,jdbc,postgresql,actuator,configuration-processor,opentelemetry,datasource-micrometer,testcontainers \
       -d type=maven-project \
       -d applicationName=CounterApiApplication | tar -xzvf -
cd counter-api
```

和没勾 `datasource-micrometer` 相比，pom 会多 BOM 和两个依赖。Initializr 里的版本可能偏旧，建议升到 2.3.0：

```xml
<properties>
    <java.version>25</java.version>
    <datasource-micrometer.version>2.3.0</datasource-micrometer.version>
    <opentelemetry.version>1.63.0</opentelemetry.version>
</properties>
```

```xml
<dependency>
    <groupId>net.ttddyy.observation</groupId>
    <artifactId>datasource-micrometer-spring-boot</artifactId>
</dependency>
<dependency>
    <groupId>net.ttddyy.observation</groupId>
    <artifactId>datasource-micrometer-opentelemetry</artifactId>
</dependency>
```

BOM：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>net.ttddyy.observation</groupId>
            <artifactId>datasource-micrometer-bom</artifactId>
            <version>${datasource-micrometer.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

Grafana Logs / Trace 上的关联日志要另加 Appender。`spring-boot-starter-opentelemetry` 只导出 Trace 和 Metrics，**不会**把 Logback 接到 OTLP。LGTM 的 `@ServiceConnection` 会配好 `/v1/logs`，没有 Appender 时 Loki 仍是空的。Boot 4 不用再加 Tracing 桥：

```xml
<dependency>
    <groupId>am.ik.spring.opentelemetry</groupId>
    <artifactId>otel-logs-autoconfigure-logback</artifactId>
    <version>0.7.0</version>
</dependency>
```

Boot 4.1.x 要把 OpenTelemetry SDK 钉到 1.63.0（上面 `<properties>` 里的 `opentelemetry.version`），否则会和这个 Appender 对不上。

## Spring Boot 3.5

3.5 没有 OpenTelemetry starter，创建时不要带 `opentelemetry`，Datasource Micrometer 走 1.x：

```bash
curl -s https://start.spring.io/starter.tgz \
       -d artifactId=counter-api \
       -d name=counter-api \
       -d baseDir=counter-api \
       -d packageName=com.example \
       -d dependencies=web,jdbc,postgresql,actuator,configuration-processor,datasource-micrometer,testcontainers \
       -d type=maven-project \
       -d bootVersion=3.5.10 \
       -d applicationName=CounterApiApplication | tar -xzvf -
cd counter-api
```

```xml
<datasource-micrometer.version>1.5.0</datasource-micrometer.version>
<opentelemetry.version>1.63.0</opentelemetry.version>
```

```xml
<dependency>
    <groupId>net.ttddyy.observation</groupId>
    <artifactId>datasource-micrometer-spring-boot</artifactId>
</dependency>
<dependency>
    <groupId>net.ttddyy.observation</groupId>
    <artifactId>datasource-micrometer-opentelemetry</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>am.ik.spring.opentelemetry</groupId>
    <artifactId>otel-logs-autoconfigure-logback</artifactId>
    <version>0.7.0</version>
</dependency>
```

OTLP 配置项名字和 Boot 4 不一样，见上一篇。

## Counter API

一张表，`INSERT ... ON CONFLICT` 做计数：

```java
@RestController
public class CounterController {

    private final JdbcClient jdbcClient;
    private final Logger logger = LoggerFactory.getLogger(getClass());

    public CounterController(JdbcClient jdbcClient) {
        this.jdbcClient = jdbcClient;
    }

    @PostMapping("/counter")
    @Transactional
    public CounterResponse increment(@RequestBody CounterRequest request) {
        CounterResponse response = jdbcClient.sql("""
                INSERT INTO counters (entry_id, counter)
                VALUES (?, 1)
                ON CONFLICT (entry_id)
                DO UPDATE SET counter = counters.counter + 1
                RETURNING entry_id, counter
                """).param(request.entryId()).query(CounterResponse.class).single();
        logger.atInfo()
                .addKeyValue("entryId", response.entryId())
                .addKeyValue("counter", response.counter())
                .log("event=increment entryId={} counter={}", response.entryId(), response.counter());
        return response;
    }

    @GetMapping("/counter")
    public List<CounterResponse> getAll() {
        return jdbcClient.sql("SELECT entry_id, counter FROM counters ORDER BY counter DESC")
                .query(CounterResponse.class)
                .list();
    }

    public record CounterRequest(int entryId) {}

    public record CounterResponse(int entryId, long counter) {}
}
```

`src/main/resources/schema.sql`：

```sql
CREATE TABLE IF NOT EXISTS counters
(
    entry_id BIGINT PRIMARY KEY,
    counter  BIGINT NOT NULL
);
```

`application.properties`（本地把 SQL 日志和慢查询打开，方便对照 Grafana）：

```properties
spring.application.name=counter-api

jdbc.datasource-proxy.json-format=true
jdbc.datasource-proxy.logging=slf4j
jdbc.datasource-proxy.multiline=false
jdbc.datasource-proxy.query.enable-logging=true
jdbc.datasource-proxy.slow-query.enable-logging=true
jdbc.datasource-proxy.slow-query.threshold=5

logging.level.net.ttddyy.dsproxy.listener.logging.SLF4JQueryLoggingListener=debug
management.opentelemetry.instrumentation.logback-appender.capture-experimental-attributes=true
management.opentelemetry.instrumentation.logback-appender.capture-key-value-pair-attributes=true
management.otlp.metrics.export.base-time-unit=seconds
management.otlp.metrics.export.step=30s
management.tracing.sampling.probability=1.0

spring.sql.init.mode=always
```

`slow-query.threshold` 的单位是**秒**，默认 300。这里写成 `5` 表示超过 5 秒才算慢，不是 5 毫秒。

Span 里绑参数默认关（`jdbc.datasource-proxy.include-parameter-values=false`）。但上面这份 **SLF4J SQL 日志** 仍会把 `params` 打进 JSON，本地可以，生产不要这么开。

## 跑起来

```bash
./mvnw spring-boot:test-run
```

Testcontainers 会起 PostgreSQL 和 `grafana/otel-lgtm`。DataSource、OTLP 地址都由测试配置写好，看 `src/test/java/com/example/TestcontainersConfiguration.java`。日志里会打 Grafana 地址，端口每次不一样：

```
2026-09-16T15:11:09.235+08:00  INFO 1127 --- [counter-api] [           main] [                                                 ] o.t.grafana.LgtmStackContainer           : Access to the Grafana dashboard: http://localhost:32782
2026-09-16T15:11:09.399+08:00  INFO 1127 --- [counter-api] [           main] [                                                 ] i.m.c.instrument.push.PushMeterRegistry  : Publishing metrics for OtlpMeterRegistry every 1m to http://localhost:32786/v1/metrics with resource attributes {service.name=counter-api}
```

这次是 `http://localhost:32782/`，端口每次都会变。

请求两次：

```bash
curl -s http://localhost:8080/counter --json '{"entryId":100}'
curl -s http://localhost:8080/counter
```

控制台能看到类似：

```
2026-09-16T15:11:44.259+08:00  INFO 1127 --- [counter-api] [nio-8080-exec-1] [f7d2df29ea488776b3e40fbc7cc99d7c-87fe4a9eb3bf27cc] com.example.CounterController : event=increment entryId=100 counter=1
2026-09-16T15:11:49.077+08:00 DEBUG 1127 --- [counter-api] [nio-8080-exec-2] [35563fbcb8025e89648aed320e10bd78-a41ffbeeae371359] n.t.d.l.l.SLF4JQueryLoggingListener : {"name":"test", "connection":3, "time":2, "success":true, "type":"Prepared", "query":["SELECT entry_id, counter FROM counters ORDER BY counter DESC"], "params":[[]]}
```

方括号里是 `traceId-spanId`，说明 Tracing 已经挂上。POST 那次还会打出 `INSERT ... ON CONFLICT` 的 JSON。

用 [vegeta](https://github.com/tsenart/vegeta) 压一轮，Grafana 里才有足够的 Exemplar。macOS：

```bash
brew install vegeta
```

```bash
for round in $(seq 20); do
  echo "=== Round $round/20 ==="
  for i in $(seq 3000); do
    id=$((RANDOM % 50 + 1))
    if [ $((RANDOM % 3)) -eq 0 ]; then
      echo '{"method":"GET","url":"http://localhost:8080/counter"}'
    else
      echo '{"method":"POST","url":"http://localhost:8080/counter","header":{"Content-Type":["application/json"]},"body":"'$(echo -n "{\"entryId\":$id}" | base64)'"}'
    fi
  done | vegeta attack -rate=100 -duration=30s -format=json | vegeta report
done
```

## Grafana 里看什么

地址以启动日志为准，不要抄文里的端口。

![Grafana 首页，左侧 Drilldown](01.webp)

### Traces

Drilldown → Traces。数据源是 Tempo。

![Traces Drilldown，Span rate](02.webp)

Span rate 柱顶的 ◇（Exemplar）→ View trace。

![Span rate 上的 Exemplar 和 View trace](03.webp)

`connection` span 里能看到 acquired / commit 的时间和次数。

![connection span 的 acquired 与 commit 事件](04.webp)

点 SQL span。带 `RETURNING` 时，summary 经常是 `INSERT counters SELECT`，`db.query.text` 才是完整语句。属性名已经是 OpenTelemetry semantic conventions（`db.system.name`、`db.query.text` 等），这是 `datasource-micrometer-opentelemetry` 做的。

![INSERT span 上的 db.query.text](05.webp)

时间轴上的文档图标，或 span 详情里的 Related logs，可以把这条 Trace 对应的日志拆到旁边看。没加 Logback Appender 时这里是空的。

![从 Trace 打开关联日志](06.webp)

Loki 会按 `service_name` 和 `trace_id` 滤出这次请求的 INFO 和 SQL DEBUG。

![按 trace_id 查出的 increment 日志和 SQL](07.webp)

### Metrics

Drilldown → Metrics，过滤 `jdbc`。能看到 `jdbc.connection_acquired_total`、`jdbc.connection_commit_total`、连接占用时间等。[指标列表](https://jdbc-observations.github.io/datasource-micrometer/docs/current/docs/html/#observability-metrics)。

![Metrics Drilldown 过滤 jdbc](08.webp)

### Logs

Drilldown → Logs，选 `counter-api` → Show logs。

![Logs Drilldown 里的 counter-api](09.webp)

![counter-api 的日志列表](10.webp)

点开一条，Links 里的 Trace 跳回 Tempo。

![日志字段里的 trace_id 和 Trace 链接](11.webp)

![从日志跳到的 Trace View](12.webp)

## 生产怎么开

这套东西生产有用，但不要照搬上面的本地配置。

值得开的：

- Trace：HTTP → JDBC connection → 具体 SQL，排查慢接口够用。采样不要 100%，`management.tracing.sampling.probability=1.0` 只适合本机。
- Metrics：连接寿命、commit/rollback、查询耗时。告警看 p99 和错误率，不靠刷 SQL 原文。
- 慢查询日志：阈值按秒设，只打真正慢的。`jdbc.includes=QUERY` 可以只观测查询，少一点 connection/fetch 噪声。

不要默认开的：

- `jdbc.datasource-proxy.query.enable-logging=true`：每条 SQL 加参数，日志量和泄漏风险都大。
- `jdbc.datasource-proxy.include-parameter-values=true`：参数进 Span。

应用仍然只把 OTLP 打到 Collector，后面接 Tempo / Loki / Mimir 或托管服务。LGTM 是一体机，适合本机；上线拆开，和上一篇换日志后端是同一思路。

> 本文主要参考 Toshiaki Maki 的 [Instrumenting JDBC Operations in Spring Boot Applications with Datasource Micrometer](https://ik.am/entries/894/en)。Counter API、LGTM、Grafana Drilldown 以原文为准。版本按当前 2.3.0 / 1.5.0 写；Appender 和 Boot 4 / 3.5 的 OTLP 前缀与 [上一篇](/posts/spring-boot-logback-otlp-logs) 对齐。

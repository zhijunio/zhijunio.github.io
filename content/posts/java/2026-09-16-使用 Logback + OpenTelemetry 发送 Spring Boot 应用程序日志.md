---
title: "使用 Logback + OpenTelemetry (OTLP) 发送 Spring Boot 应用程序日志"
date: 2026-09-16 14:00:00+08:00
slug: spring-boot-logback-otlp-logs
category: java
tags: [ "spring-boot", "opentelemetry", "logback" ]
description: "Spring Boot 通过 Logback 把日志用 OTLP 发出去。官方 Appender 还是 α，这里用 otel-logs-autoconfigure，Boot 4 和 3.5 的配置不一样。"
---

如果要把 Spring Boot 的日志送到 OpenTelemetry，Logback 走 OTLP 是一条常用路。官方提供了 `opentelemetry-logback-appender`，但一直是 α 版本。α 期间不要指望 Spring Boot 给这个 Appender 做自动配置（`OpenTelemetry` 对象本身会自动配置，Appender 不会）。结果就是每个项目自己写一份 `logback-spring.xml`，还得盯着 SDK 版本。

<!--more-->

我这边用的是 [otel-logs-autoconfigure](https://github.com/making/otel-logs-autoconfigure)。加上依赖，在 `application.properties` 里写 OTLP 地址就行。支持 Spring Boot 3.5 和 4，`0.6.0` 之后 Log4j2 也能用。

接收端先用 [Lognroll](https://github.com/categolj/lognroll) 确认 OTLP 能打出去。它自己也写了：hobby，SQLite，不适合要可靠性和吞吐的环境。生产换别的实现，应用这边的 endpoint 不用改思路。

## OTLP 后端（本地：Lognroll）

```bash
docker run --rm -p 4318:4318 ghcr.io/categolj/lognroll:native
```

打开 `http://localhost:4318`，用户名留空，密码 `changeme`。应用要把日志发到 `http://localhost:4318/v1/logs` 。Apple Silicon 上官方 native 镜像可能起不来，改用 JVM 版镜像。

![Lognroll 登录后的界面](01.png)

## Spring Boot 4+

从 start.spring.io 建项目时把 `opentelemetry` 选上，Java 指定 25：

```bash
curl -s https://start.spring.io/starter.tgz \
       -d artifactId=demo-otel-logs \
       -d name=demo-otel-logs \
       -d baseDir=demo-otel-logs \
       -d packageName=com.example \
       -d javaVersion=25 \
       -d dependencies=web,actuator,configuration-processor,prometheus,opentelemetry \
       -d type=maven-project \
       -d applicationName=DemoOtelLogsApplication | tar -xzvf -
cd demo-otel-logs
```

`pom.xml` 加上依赖，并把 OpenTelemetry SDK 升到 1.63.0。Boot 4.1.x 默认是 1.62.0，和 `otel-logs-autoconfigure` 0.7.0 带的 Appender 对不上，会报 `ClassNotFoundException: ExtendedAttributeKey`。

```xml
<properties>
    <java.version>25</java.version>
    <opentelemetry.version>1.63.0</opentelemetry.version>
</properties>
```

```xml
<dependency>
    <groupId>am.ik.spring.opentelemetry</groupId>
    <artifactId>otel-logs-autoconfigure-logback</artifactId>
    <version>0.7.0</version>
</dependency>
```

`src/main/resources/application.properties`：

```properties
logging.level.web=debug

management.opentelemetry.instrumentation.logback-appender.capture-experimental-attributes=true
management.opentelemetry.instrumentation.logback-appender.capture-key-value-pair-attributes=true

management.opentelemetry.logging.export.otlp.endpoint=http://localhost:4318/v1/logs
management.opentelemetry.logging.export.otlp.compression=gzip
management.opentelemetry.logging.export.otlp.headers.Authorization=Bearer changeme

management.otlp.metrics.export.enabled=false
```

Boot 4 自带 OpenTelemetry starter，不用再加 Micrometer Tracing 桥。

## Spring Boot 3.5

3.5 没有 OpenTelemetry starter，创建时不要带 `opentelemetry`，版本钉在 `3.5.10`：

```bash
curl -s https://start.spring.io/starter.tgz \
       -d artifactId=demo-otel-logs \
       -d name=demo-otel-logs \
       -d baseDir=demo-otel-logs \
       -d packageName=com.example \
       -d dependencies=web,actuator,configuration-processor,prometheus \
       -d type=maven-project \
       -d bootVersion=3.5.10 \
       -d applicationName=DemoOtelLogsApplication | tar -xzvf -
cd demo-otel-logs
```

依赖两个：自动配置，以及把 Trace ID 写进日志的桥：

```xml
<dependency>
    <groupId>am.ik.spring.opentelemetry</groupId>
    <artifactId>otel-logs-autoconfigure-logback</artifactId>
    <version>0.7.0</version>
</dependency>

<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
```

这个 Appender 用的 OpenTelemetry Java SDK 比 Boot 3.5 BOM 里的新，不改版本启动会失败。在 `pom.xml` 的 `<properties>` 里覆盖：

```xml
<opentelemetry.version>1.63.0</opentelemetry.version>
```

OTLP 相关配置项的名字和 Boot 4 不一样：

```properties
logging.level.web=debug

management.opentelemetry.instrumentation.logback-appender.capture-experimental-attributes=true
management.opentelemetry.instrumentation.logback-appender.capture-key-value-pair-attributes=true

management.otlp.logging.endpoint=http://localhost:4318/v1/logs
management.otlp.logging.compression=gzip
management.otlp.logging.headers.Authorization=Bearer changeme

management.otlp.metrics.export.enabled=false
```

Boot 4 用 `management.opentelemetry.logging.export.otlp.endpoint`，3.5 用 `management.otlp.logging.endpoint`。其余压缩、Header 只是前缀跟着变。

## 跑起来看一眼

```bash
./mvnw clean package -DskipTests
java -jar target/demo-otel-logs-0.0.1-SNAPSHOT.jar
```

到 Lognroll 点 View Logs，能看到启动日志。再请求一次：

```bash
curl http://localhost:8080/actuator/health
```

刷新日志，这条请求会出现，`trace_id` 列有值就说明 Appender 和 Tracing 接上了。

![Lognroll 中带 trace_id 的请求日志](02.png)

## 其他 OTLP 实现

应用只负责把日志发到一个 OTLP HTTP 地址（Boot 4 是 `management.opentelemetry.logging.export.otlp.endpoint`）。换后端时改这个 URL 和鉴权即可。生产里不要让每个实例直连存储，前面加 [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)，负责重试、批量、压缩，再分发给真正的日志库。

常见接法：

- **Grafana Loki**：Grafana 栈里最顺。Loki 3 可以直接收 OTLP；也可以 Collector 收 OTLP，再用 Loki exporter 转进去。查询、看板走 Grafana。
- **OpenSearch / Elasticsearch**：已经有 ELK 的话，Collector 导出到 OpenSearch，按 `service.name`、`host.name` 检索。
- **SigNoz**：日志、指标、Trace 想放一起、可以自建，底层 ClickHouse，原生 OTLP。
- **托管服务**：Grafana Cloud、Datadog、Splunk、Elastic Cloud 都收 OTLP，把 endpoint 换成厂商给的 `/v1/logs`，Header 带 API Key。

Collector 最小配置大致是：

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318

exporters:
  otlphttp/backend:
    endpoint: http://loki:3100/otlp
    tls:
      insecure: true

service:
  pipelines:
    logs:
      receivers: [otlp]
      exporters: [otlphttp/backend]
```

Spring Boot 的 OTLP 地址改成 Collector，例如 `http://otel-collector:4318/v1/logs`。本地仍可用 Lognroll 验通；上线只换接收端。

## 多实例与主机名

`otel-logs-autoconfigure` 只负责把当前进程的 Logback 接到 OTLP，不管后面怎么存、怎么查。Lognroll 是单进程 + SQLite，多副本一起打进去会糊成一锅，也撑不住流量。

多实例要两件事：每条日志带上 `host.name` / `service.instance.id`，接收端能按这个过滤。

不要只写 `${HOSTNAME}`。Linux/K8s 里它通常是 Pod 名；macOS 上这个环境变量经常是空的，Resource 里就看不到主机名。可靠一点用 `InetAddress` 兜底：

```java
@Configuration
class OpenTelemetryHostResourceConfiguration {

    @Bean
    @ConditionalOnMissingBean
    Resource openTelemetryResource(Environment environment, OpenTelemetryProperties properties) {
        Map<String, String> attributes = new LinkedHashMap<>(properties.getResourceAttributes());
        String host = firstNonBlank(
                attributes.get("host.name"),
                environment.getProperty("HOSTNAME"),
                environment.getProperty("COMPUTERNAME"),
                localHostName());
        attributes.put("host.name", host);
        attributes.putIfAbsent("service.instance.id", host);

        ResourceBuilder builder = Resource.builder();
        new OpenTelemetryResourceAttributes(environment, attributes).applyTo(builder::put);
        return Resource.getDefault().merge(builder.build());
    }

    // firstNonBlank / localHostName 略
}
```

`application.properties` 里只保留服务名即可：

```properties
spring.application.name=demo-otel-logs
management.opentelemetry.resource-attributes.service.name=${spring.application.name}
```

K8s 上仍可显式注入：

```bash
export OTEL_RESOURCE_ATTRIBUTES=host.name=$HOSTNAME,service.instance.id=$HOSTNAME
```

Lognroll 里验通时，Resource 应能看到 `host.name`。多副本查询要放到 Loki / OpenSearch 那边按这个字段过滤。

> 本文主要参考 Toshiaki Maki 的 [Sending Logs from a Spring Boot App with Logback + OpenTelemetry (OTLP)](https://ik.am/entries/892/en)，Boot 4 / 3.5 的配置差、`otel-logs-autoconfigure` 和 Lognroll 的用法以原文为准。

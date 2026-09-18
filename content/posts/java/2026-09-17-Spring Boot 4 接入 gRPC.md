---
title: "Spring Boot 4 接入 gRPC"
date: 2026-09-17 15:45:00+08:00
slug: spring-boot-grpc
category: java
tags: [ "spring-boot", "grpc" ]
description: "Spring Boot 4 已经能接 gRPC。4.0 还要单独引入 Spring gRPC，到 4.1 自动配置才进 Spring Boot。这篇按 4.1.1 写服务端、客户端、测试和 LGTM，并补充 Reactor、Native、安全和 Servlet 同端口。"
---

[Spring gRPC](https://docs.spring.io/spring-grpc/reference/) 是 Spring 官方的 gRPC 项目，作用是把 `.proto` 生成出来的服务端实现和客户端
stub，接到 Spring 的依赖注入和自动配置里。很多人会默认「Spring Boot 一上来就自带」，其实不是：Spring gRPC 一开始是独立发布的，和
Spring Boot 的版本节奏也不完全同步。

<!--more-->

**Spring Boot 4.0** 时期已经能写 gRPC，但自动配置还在独立的 Spring gRPC **1.0** 里。starter 的坐标是
`org.springframework.grpc:...`，不是 `org.springframework.boot:...`。那时候在 start.spring.io 上如果同时勾了 Spring Web 和
gRPC，常见路径是 Servlet 模式：gRPC 和普通 HTTP 共用一个端口（多半是 8080）。[ik.am #850](https://ik.am/entries/850)
写的就是这条线，网上不少早期笔记也还停在那里。

到了 **Spring Boot 4.1**，gRPC 的自动配置才迁进 Spring Boot 本身，对应的是 Spring gRPC **1.1**。starter 也改成了
`org.springframework.boot:spring-boot-starter-grpc-server` 和 `spring-boot-starter-grpc-client`。默认实现换成独立的 Netty
服务器，端口是 **9090**；就算你同时依赖了 Web，也不会再自动把 gRPC 绑到 HTTP 那个端口上。客户端这边，1.0 常用的
`default-channel.address`、以及「扫一下就能注入 stub」的习惯，在 Spring Boot 4.1 里都不能照搬。

这篇按 **Spring Boot 4.1.1**、Java **25**、Maven
来写。官方文档是 [gRPC :: Spring Boot](https://docs.spring.io/spring-boot/reference/io/grpc.html)。如果你的项目还停在 Spring gRPC 1.0，升级前先看 [Spring gRPC 1.1 Migration Guide](https://github.com/spring-projects/spring-grpc/wiki/Spring-gRPC-1.1-Migration-Guide)
：先换 starter 坐标和配置属性，再改代码，会省事很多。

## 示例代码

完整可跑的代码在 [zhijunio/spring-boot-grpc-samples](https://github.com/zhijunio/spring-boot-grpc-samples)：`grpc-server` 听 9090，`grpc-client` 无 Web，启动时用 `CommandLineRunner` 打一次 `SayHello`，`grpc-client-secure` 对应 `grpc-server-secure`（默认通道带 HTTP Basic），`grpc-client-tomcat-secure` 对应 `grpc-server-tomcat-secure`，`auth-server` / `grpc-server-oauth2` / `grpc-client-oauth2` 是 JWT client_credentials，`grpc-server-tomcat` 是 Tomcat Servlet 同端口，`grpc-server-secure` 是 Netty HTTP Basic / preauth，`grpc-server-tomcat-secure` 是 Tomcat + Security。形状对齐官方 [samples/grpc-server](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-server)、[samples/grpc-client](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-client)、[samples/grpc-tomcat](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-tomcat)、[samples/grpc-secure](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-secure)、[samples/grpc-tomcat-secure](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-tomcat-secure)、[samples/grpc-oauth2](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-oauth2)。Reactor、Native 只在文里写，没有放进示例。

## 依赖

| 场景   | Maven 坐标                                                                      |
|--------|---------------------------------------------------------------------------------|
| Server | `org.springframework.boot:spring-boot-starter-grpc-server`                      |
| Client | `org.springframework.boot:spring-boot-starter-grpc-client`                      |
| 测试   | `spring-boot-starter-grpc-server-test` / `spring-boot-starter-grpc-client-test` |

在 start.spring.io 上勾选时，依赖 ID 叫 `spring-grpc-server` 和 `spring-grpc-client`，生成出来的 pom 里才是上面这些
`spring-boot-starter-grpc-*`。

## 使用 Spring gRPC 创建 gRPC 服务器

没有现成仓库时，可以从 start.spring.io 自己建。Java 选 25，同时勾上 actuator、prometheus、opentelemetry、native：

```bash
mkdir -p spring-boot-grpc-samples
cd spring-boot-grpc-samples
curl -s https://start.spring.io/starter.tgz \
       -d bootVersion=4.1.1 \
       -d artifactId=grpc-server \
       -d name=grpc-server \
       -d baseDir=grpc-server \
       -d packageName=com.example \
       -d javaVersion=25 \
       -d dependencies=spring-grpc-server,actuator,configuration-processor,prometheus,opentelemetry,native \
       -d type=maven-project \
       -d applicationName=GrpcServerApplication | tar -xzvf -
cd grpc-server
```

接下来写 Protocol Buffers 的 `.proto`。服务定义跟官方 `samples/grpc-server` 一样：一元调用 `SayHello`，服务端流 `StreamHello`。客户端流和双向流这篇不写。

```bash
cat <<EOF > src/main/proto/hello.proto
syntax = "proto3";

option java_package = "com.example.proto";
option java_outer_classname = "HelloWorldProto";
option java_multiple_files = true;

service Simple {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
  rpc StreamHello (HelloRequest) returns (stream HelloReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
EOF
```

先编译 proto，生成 Java 代码。用 Spring Initializr 建项目时，`protobuf-maven-plugin` 已经在 pom 里了。

执行 `./mvnw compile`，就会在 `target/generated-sources` 里生成 Java 代码和 stub。生成结果大概是：

```bash
$ find target/generated-sources/protobuf -type f
target/generated-sources/protobuf/com/example/proto/HelloWorldProto.java
target/generated-sources/protobuf/com/example/proto/HelloRequest.java
target/generated-sources/protobuf/com/example/proto/HelloReplyOrBuilder.java
target/generated-sources/protobuf/com/example/proto/HelloRequestOrBuilder.java
target/generated-sources/protobuf/com/example/proto/SimpleGrpc.java
target/generated-sources/protobuf/com/example/proto/HelloReply.java
```

实现服务：继承 `SimpleGrpc.SimpleImplBase`，标上 `@Service`（官方示例也是这样），就会进容器并挂到 gRPC 服务器上。标 `@GrpcService` 也可以，因为同样是 `BindableService` bean。服务里 `error*` 抛 `IllegalArgumentException`，`internal*` 抛 `RuntimeException`。官方 `StreamHello` 每条之间 `sleep` 1 秒；示例仓库为了测试不卡，把间隔去掉了。

```bash
cat <<EOF > src/main/java/com/example/GrpcServerService.java
package com.example;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.stereotype.Service;

import com.example.proto.HelloReply;
import com.example.proto.HelloRequest;
import com.example.proto.SimpleGrpc;

import io.grpc.stub.StreamObserver;

@Service
public class GrpcServerService extends SimpleGrpc.SimpleImplBase {

    private static final Log log = LogFactory.getLog(GrpcServerService.class);

    @Override
    public void sayHello(HelloRequest req, StreamObserver<HelloReply> responseObserver) {
        log.info("Hello " + req.getName());
        if (req.getName().startsWith("error")) {
            throw new IllegalArgumentException("Bad name: " + req.getName());
        }
        if (req.getName().startsWith("internal")) {
            throw new RuntimeException();
        }
        HelloReply reply = HelloReply.newBuilder().setMessage("Hello ==> " + req.getName()).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
    }

    @Override
    public void streamHello(HelloRequest req, StreamObserver<HelloReply> responseObserver) {
        log.info("Hello " + req.getName());
        for (int count = 0; count < 10; count++) {
            HelloReply reply = HelloReply.newBuilder()
                    .setMessage("Hello(" + count + ") ==> " + req.getName())
                    .build();
            responseObserver.onNext(reply);
        }
        responseObserver.onCompleted();
    }

}
EOF
```

gRPC 线上只认 **Status**，不会把 Java 异常原样传给客户端。服务方法里抛出来的未处理异常，默认多半变成 `UNKNOWN`。`GrpcExceptionHandler` 就是把这些异常翻成 Status 的扩展点：做成 bean 后，Spring gRPC 在调用失败时问它一次；认出的类型返回 `StatusException`（可以带 description 和 metadata trailer），不认的返回 `null`，交给后面的 handler 或默认行为。

官方 sample 把 `IllegalArgumentException` 映射成 `INVALID_ARGUMENT`，并在 trailer 里放 `error-code`。`RuntimeException` 故意不处理，客户端看到的就是 `UNKNOWN`。`spring.grpc.server.exception-handler.enabled=false` 会关掉这套拦截；`GrpcServerIntegrationTests` 里两条都覆盖了。

```java
@Bean
GrpcExceptionHandler grpcExceptionHandler() {
    return (exception) -> {
        if (exception instanceof IllegalArgumentException) {
            Metadata metadata = new Metadata();
            metadata.put(Metadata.Key.of("error-code", Metadata.ASCII_STRING_MARSHALLER), "INVALID_ARGUMENT");
            return Status.INVALID_ARGUMENT.withDescription(exception.getMessage()).asException(metadata);
        }
        return null;
    };
}
```

Initializr 勾了 OpenTelemetry。还没起接收端的时候，OTLP metrics 会连不上、日志刷错。先关掉，等后面「可观测性」再接到 LGTM：

```bash
cat <<EOF >> src/main/resources/application.properties
management.otlp.metrics.export.enabled=false
EOF
```

启动应用。没有改过端口的话，gRPC 默认监听 **9090**：

```bash
./mvnw spring-boot:run
```

命令行调 gRPC，用 [grpcurl](https://github.com/fullstorydev/grpcurl)：

```bash
brew install grpcurl
```

先用 [gRPC 反射](https://grpc.io/docs/guides/reflection/) 列出服务。Spring Initializr 勾了 `spring-grpc-server` 之后，Reflection 会跟着 starter 注册上，不用自己加 `grpc-services`。

```bash
$ grpcurl --plaintext localhost:9090 list 

com.example.Simple
grpc.health.v1.Health
grpc.reflection.v1.ServerReflection
```

Health 也已经在了。Spring gRPC starter 自带 gRPC 健康检查，同样不用手加依赖。看一下方法列表：

```bash
$ grpcurl --plaintext localhost:9090 describe grpc.health.v1.Health

grpc.health.v1.Health is a service:
service Health {
  rpc Check ( .grpc.health.v1.HealthCheckRequest ) returns ( .grpc.health.v1.HealthCheckResponse );
  rpc Watch ( .grpc.health.v1.HealthCheckRequest ) returns ( stream .grpc.health.v1.HealthCheckResponse );
}
```

调 `Check`，确认状态是 `SERVING`：

```bash
$ grpcurl --plaintext localhost:9090 grpc.health.v1.Health/Check
{
"status": "SERVING"
}
```

再看自己写的 `Simple` 有哪些方法：

```bash
$ grpcurl --plaintext localhost:9090 describe Simple

Simple is a service:
service Simple {
  rpc SayHello ( .HelloRequest ) returns ( .HelloReply );
  rpc StreamHello ( .HelloRequest ) returns ( stream .HelloReply );
}
```

先打 `SayHello`。请求用 JSON；本地没开 TLS，加上 `--plaintext`。

```bash
$ grpcurl -d '{"name":"Alien"}' --plaintext localhost:9090 Simple/SayHello
{
  "message": "Hello ==\u003e Alien"
}
```

接下来执行 `StreamHello`，这是服务端连续回多条的方法。

```bash
$ grpcurl -d '{"name":"Alien"}' --plaintext localhost:9090 Simple/StreamHello
{
  "message": "Hello(0) ==\u003e Alien"
}
{
  "message": "Hello(1) ==\u003e Alien"
}
{
  "message": "Hello(2) ==\u003e Alien"
}
{
  "message": "Hello(3) ==\u003e Alien"
}
{
  "message": "Hello(4) ==\u003e Alien"
}
{
  "message": "Hello(5) ==\u003e Alien"
}
{
  "message": "Hello(6) ==\u003e Alien"
}
{
  "message": "Hello(7) ==\u003e Alien"
}
{
  "message": "Hello(8) ==\u003e Alien"
}
{
  "message": "Hello(9) ==\u003e Alien"
}
```

接下来写测试。形状对齐官方 [samples/grpc-server](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-server)，不要留 Initializr 那个会占 9090 的空 `contextLoads`。

Spring Boot 4.1 **不会**再自动扫出 stub bean。测试里要注入 `SimpleBlockingStub`，必须加上 `@ImportGrpcClients`。
`@AutoConfigureTestGrpcTransport` 会走进程内通道，不用占 9090。

```java
@SpringBootTest(
		properties = { "spring.grpc.server.port=0",
				"spring.grpc.client.channel.default.target=0.0.0.0:${local.grpc.sever.port}" },
		useMainMethod = UseMainMethod.ALWAYS)
@DirtiesContext
@AutoConfigureTestGrpcTransport
@ImportGrpcClients
class GrpcServerApplicationTests {

	@Autowired
	private SimpleGrpc.SimpleBlockingStub stub;

	@Test
	void serverResponds() {
		HelloReply response = this.stub.sayHello(HelloRequest.newBuilder().setName("Alien").build());
		assertEquals("Hello ==> Alien", response.getMessage());
	}

}
```

官方属性名是 `local.grpc.sever.port`（少一个 `r`）。配了 `@AutoConfigureTestGrpcTransport` 之后走进程内通道，这条用不上。

仓库里其余测试也按官方搬了：`GrpcServerSideTests`、`GrpcServerIntegrationTests`（异常映射、随机端口、SSL、进程内和 Netty 双通道）、`GrpcServerHealthIntegrationTests`、`GrpcClientApplicationTests`（各种 stub factory）。`error` → `INVALID_ARGUMENT` 以及 trailer 里的 `error-code` 在 Integration 里测。

跑测试（注意，项目中使用的 Java 25，本地的 Java 版本应该也是 25）：

```bash
./mvnw test
```

### 进程内服务器

gRPC 还可以在**同一个 JVM 里**起一个不占 TCP 端口的服务端，客户端用内存通道连过去。适合同一进程里既有服务实现、又要调自己。**两个独立进程之间用不了**：`grpc-client` 连 `grpc-server` 仍然要走 `static://localhost:9090`。

写测试时，优先用上面的 `@AutoConfigureTestGrpcTransport`。那种是测试专用通道，不用自己配名字，也不会再起 Netty。

如果是正式代码里要开进程内服务，同进程的服务端和客户端都要加上：

```xml
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-inprocess</artifactId>
</dependency>
```

服务端给这个进程内实例起个名字，比如 `hello`：

```properties
spring.grpc.server.inprocess.name=hello
```

同进程里的客户端，通道不要写成 `static://localhost:9090`，改成 `in-process:` 加上**同一个名字**：

```properties
spring.grpc.client.channel.default.target=in-process:hello
```

`@ImportGrpcClients` 默认连 `default` 通道，不用改。

配了 `inprocess.name` 之后，进程内工厂是**额外**加上的，默认的 Netty **仍然会监听 9090**。这不是关掉 9090 的开关。不想让测试占端口，用 `@AutoConfigureTestGrpcTransport`。

## 使用 Spring gRPC 创建 gRPC 客户端

接下来做客户端，连到刚才的服务器。还是从 start.spring.io 生成：

```bash
cd ..
curl -s https://start.spring.io/starter.tgz \
       -d bootVersion=4.1.1 \
       -d artifactId=grpc-client \
       -d name=grpc-client \
       -d baseDir=grpc-client \
       -d packageName=com.example \
       -d javaVersion=25 \
       -d dependencies=spring-grpc-client,actuator,configuration-processor,prometheus,opentelemetry,native \
       -d type=maven-project \
       -d applicationName=GrpcClientApplication | tar -xzvf -
cd grpc-client
```

`.proto` 和服务端同一份：

```bash
cat <<EOF > src/main/proto/hello.proto
syntax = "proto3";

option java_package = "com.example.proto";
option java_outer_classname = "HelloWorldProto";
option java_multiple_files = true;

service Simple {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
  rpc StreamHello (HelloRequest) returns (stream HelloReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
EOF
```

再 `./mvnw compile`，生成 stub。

```bash
./mvnw compile
```

和 1.0 不同的是： **客户端 stub 不会再自动扫包注册成 bean**
。要在配置类或启动类上写 `@ImportGrpcClients`。官方 [samples/grpc-client](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-client) 不指定 `types`，会按 classpath 里生成的 stub 注册，并连默认通道 `default`。也可以写成 `@ImportGrpcClients(types = SimpleGrpc.SimpleBlockingStub.class)`，只注入这一种。

```bash
cat <<EOF > src/main/java/com/example/GrpcClientApplication.java
package com.example;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.grpc.client.ImportGrpcClients;

import com.example.proto.HelloRequest;
import com.example.proto.SimpleGrpc;

@SpringBootApplication
@ImportGrpcClients
public class GrpcClientApplication {

    public static void main(String[] args) {
        SpringApplication.run(GrpcClientApplication.class, args);
    }

    @Bean
    CommandLineRunner runner(SimpleGrpc.SimpleBlockingStub stub) {
        return args -> {
            System.out.println(stub.sayHello(HelloRequest.newBuilder().setName("Alien").build()));
        };
    }

}
EOF
```

通道名字要对应到实际要连的地址。Spring Boot 4.1 中属性前缀是 `spring.grpc.client.channel.<名字>.target`。默认通道叫 `default`：

```bash
cat <<EOF >> src/main/resources/application.properties
spring.grpc.client.channel.default.target=static://localhost:9090
management.otlp.metrics.export.enabled=false
EOF
```

官方 sample 写成 `static://0.0.0.0:${launched.grpc.port:9090}`，方便测试里动态改端口。本地手跑服务端用 `localhost:9090` 即可。

这是纯 gRPC 客户端，**没有** HTTP 口。确认服务端已在 9090 起来，再启动客户端：

```bash
./mvnw spring-boot:run
```

启动日志末尾会打出 protobuf 的文本格式：

```
message: "Hello ==> Alien"
```

客户端进程会继续挂着，和官方 sample 一样。需要连别的端口时，改 `spring.grpc.client.channel.default.target`，或设环境变量覆盖。

官方客户端测试会用 testjars 另拉起一份 `grpc-server`。这篇不搬那套，只测 `CommandLineRunner` 有没有用 `Alien` 去调 `SayHello`：

```bash
cat<<EOF > src/test/java/com/example/GrpcClientApplicationTests.java
package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.boot.CommandLineRunner;

import com.example.proto.HelloReply;
import com.example.proto.HelloRequest;
import com.example.proto.SimpleGrpc;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class GrpcClientApplicationTests {

	@Test
	void runnerCallsSayHello() throws Exception {
		SimpleGrpc.SimpleBlockingStub stub = mock(SimpleGrpc.SimpleBlockingStub.class);
		HelloRequest request = HelloRequest.newBuilder().setName("Alien").build();
		when(stub.sayHello(request)).thenReturn(HelloReply.newBuilder().setMessage("Hello ==> Alien").build());

		CommandLineRunner runner = new GrpcClientApplication().runner(stub);
		runner.run();

		verify(stub).sayHello(request);
	}

}
EOF
```

```bash
./mvnw test
```

## 可观测性

Spring gRPC 默认会给调用打 Micrometer Observation，Trace 和 Metrics 都能出来。日志怎么用 OTLP 发出去，还是看 [Logback + OTLP](/posts/spring-boot-logback-otlp-logs)。本地接收端继续用 Grafana [LGTM](https://github.com/grafana/docker-otel-lgtm)，和 [JDBC 那篇](/posts/spring-boot-jdbc-datasource-micrometer) 一样，不要换成 Zipkin。

先起 LGTM：

```bash
docker run --name lgtm -d -p 3000:3000 -p 4317:4317 -p 4318:4318 grafana/otel-lgtm
```

服务端和客户端都加上：

```bash
cat <<EOF >> src/main/resources/application.properties
management.endpoints.web.exposure.include=health,info,prometheus
management.tracing.sampling.probability=1.0
management.opentelemetry.tracing.export.otlp.endpoint=http://localhost:4318/v1/traces
management.opentelemetry.tracing.export.otlp.compression=gzip
EOF
```

重启两边，客户端启动时会打一次 `SayHello`，Tempo 里能看到服务端和客户端的 gRPC span。前面关掉的是 OTLP **metrics** 导出，tracing 这条不受影响。

Prometheus scrape 走的是 **HTTP Actuator**，不是 gRPC。默认 Netty 听的 **9090 不是 HTTP**，`curl localhost:9090/actuator/prometheus` 打不通。这篇服务端、客户端都没勾 Web，所以两边都没有 `/actuator` HTTP 口；示例里 metrics 的 OTLP 也是关着的，指标不会进 LGTM。

如果一定要 scrape Prometheus，加上 Web，或者单独开 `management.server.port`，别指望 9090。

## 使用 Reactor 引入响应式编程

标准 gRPC Java API 用回调式的 `StreamObserver` 处理流。流一复杂，代码就会又长又绕。Spring gRPC
可以接 [Salesforce reactive-grpc](https://github.com/salesforce/reactive-grpc)，生成基于 Reactor 的 stub，服务端和客户端都能用
`Mono` / `Flux` 来写。

普通 Spring MVC 也能返回 `Mono`、`Flux`，不一定要上 WebFlux。

Spring Boot 4.1 **不再**帮你管 `reactor-grpc-stub` 的版本，要自己写死。服务端、客户端两边都加：

```xml
<dependency>
    <groupId>io.projectreactor</groupId>
    <artifactId>reactor-core</artifactId>
</dependency>
<dependency>
    <groupId>com.salesforce.servicelibs</groupId>
    <artifactId>reactor-grpc-stub</artifactId>
    <version>1.2.4</version>
</dependency>
<dependency>
    <groupId>io.projectreactor</groupId>
    <artifactId>reactor-test</artifactId>
    <scope>test</scope>
</dependency>
```

`protobuf-maven-plugin` 本身已经由 parent 管好了。要额外生成 Reactor 代码，在现有插件上补 `jvmMavenPlugins`（不要把 parent
配好的 grpc-java 生成器整段覆盖掉）：

```xml
<plugin>
    <groupId>io.github.ascopes</groupId>
    <artifactId>protobuf-maven-plugin</artifactId>
    <configuration>
        <jvmMavenPlugins>
            <jvmMavenPlugin>
                <groupId>com.salesforce.servicelibs</groupId>
                <artifactId>reactor-grpc</artifactId>
                <version>1.2.4</version>
            </jvmMavenPlugin>
        </jvmMavenPlugins>
    </configuration>
</plugin>
```

两端都重新生成代码：

```bash
./mvnw clean compile
```

`target/generated-sources/protobuf` 里会多一个 `ReactorSimpleGrpc.java`。原来的 `SimpleGrpc` 还在。

### 客户端改成 Reactor stub

`CommandLineRunner` 改成注入 `ReactorSimpleStub`：

```java
package com.example;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.grpc.client.ImportGrpcClients;

import com.example.proto.HelloRequest;
import com.example.proto.ReactorSimpleGrpc;

@SpringBootApplication
@ImportGrpcClients(types = ReactorSimpleGrpc.ReactorSimpleStub.class)
public class GrpcClientApplication {

    public static void main(String[] args) {
        SpringApplication.run(GrpcClientApplication.class, args);
    }

    @Bean
    CommandLineRunner runner(ReactorSimpleGrpc.ReactorSimpleStub stub) {
        return args -> {
            stub.sayHello(HelloRequest.newBuilder().setName("Alien").build())
                    .doOnNext(System.out::println)
                    .block();
        };
    }

}
```

Reactor 的 stub **不会**跟着 BlockingStub 自动进来，要在 `@ImportGrpcClients` 里写 `types`。通道仍是 `default`。启动类上如果还留着不带 `types` 的 `@ImportGrpcClients`，会同时注册 Blocking stub，删掉只留上面这一份即可。

重启客户端后，同样会打印 `Hello ==> Alien`。流式调用可以 `stub.streamHello(...).doOnNext(System.out::println).blockLast()`。

如果外面再包一层 MVC，才谈得上 `Accept: application/x-ndjson` 或 SSE；官方 client sample 没有 Web。

### 服务端也改成 Reactor

```java
package com.example;

import com.example.proto.HelloReply;
import com.example.proto.HelloRequest;
import com.example.proto.ReactorSimpleGrpc;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
public class GrpcServerService extends ReactorSimpleGrpc.SimpleImplBase {

    @Override
    public Mono<HelloReply> sayHello(Mono<HelloRequest> request) {
        return request
                .map(req -> HelloReply.newBuilder().setMessage("Hello ==> " + req.getName()).build());
    }

    @Override
    public Flux<HelloReply> streamHello(Mono<HelloRequest> request) {
        return request.flatMapMany(req -> Flux.range(0, 10)
                .map(i -> HelloReply.newBuilder()
                        .setMessage("Hello(" + i + ") ==> " + req.getName())
                        .build()));
    }

}
```

`sayHello` 也可以写成接收已经拆好的 `HelloRequest`，再 `return Mono.just(...)`，两种都能编过。

这个例子本身几乎没有真正的流处理，差别不明显。真要拼、过滤、背压的时候，用 Reactor 会比手写 `StreamObserver` 好读。

服务端测试改成 Reactor stub 加上 `StepVerifier`。还是用 `@AutoConfigureTestGrpcTransport`，不要退回 1.0 那套随机 Web 端口：

```java
package com.example;

import com.example.proto.HelloReply;
import com.example.proto.HelloRequest;
import com.example.proto.ReactorSimpleGrpc;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.grpc.test.autoconfigure.AutoConfigureTestGrpcTransport;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.grpc.client.ImportGrpcClients;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@AutoConfigureTestGrpcTransport
@ImportGrpcClients(types = ReactorSimpleGrpc.ReactorSimpleStub.class)
class GrpcServerServiceTest {

    @Autowired
    ReactorSimpleGrpc.ReactorSimpleStub stub;

    @Test
    void sayHello() {
        Mono<HelloReply> response = this.stub.sayHello(HelloRequest.newBuilder().setName("Alien").build());
        StepVerifier.create(response)
                .assertNext(r -> assertThat(r.getMessage()).isEqualTo("Hello ==> Alien"))
                .verifyComplete();
    }

    @Test
    void streamHello() {
        Flux<HelloReply> response = this.stub
                .streamHello(HelloRequest.newBuilder().setName("Alien").build());
        StepVerifier.create(response)
                .expectNextCount(10)
                .verifyComplete();
    }

}
```

测 gRPC 时，Blocking stub 和 Reactor stub 都可以，选一种即可。

## Servlet 同端口

前面默认的服务端是 **Netty 自己听 9090**。就算 pom 里已经有 WebMVC，4.1 也不会自动把 gRPC 绑到 HTTP 那个口上。如果你想像 4.0 早期教程那样，**普通 HTTP 和 gRPC 共用一个端口**，要自己改成 Servlet 实现。完整示例在仓库的 `grpc-server-tomcat`，对齐官方 [samples/grpc-tomcat](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-tomcat)。官方把 `server.port` 也设成 **9090**，HTTP/2 和 gRPC 都在这个口上。

`GrpcServerService` 不用改。变的是传输层：请求进 Tomcat，由 `grpc-servlet-jakarta` 转给 gRPC。容器必须开 **HTTP/2**，明文调试用的是 h2c。官方还加了一个 `TomcatConnectorCustomizer`，把 HTTP/2 的 `overheadWindowUpdateThreshold` 设成 0，避免 window update 被当成 overhead。

### 改依赖

加上 WebMVC 和 Servlet 适配。官方 sample **不排除** `grpc-netty`：默认走 Servlet 同端口；测试里关掉 `spring.grpc.server.servlet.enabled` 时，还可以再起独立的 Netty 口。

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webmvc</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-grpc-server</artifactId>
</dependency>
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-servlet-jakarta</artifactId>
</dependency>
```

`webmvc` 已经带 Tomcat。打开 HTTP/2，端口跟官方一样用 9090：

```properties
server.http2.enabled=true
server.port=9090
```

这种模式下默认 **`spring.grpc.server.port` 无效**，端口只看 `server.port`。keepalive、Netty 专属属性也会被忽略。

如果 **不排除** `grpc-netty`，同时又把 `spring.grpc.server.servlet.enabled=false`：HTTP 仍走 `server.port`，gRPC 走 `spring.grpc.server.port`，那是两个口。官方 `ListenOnTwoPortsTests` 就是这条。

### 怎么调

服务起来后，`grpcurl` 打 **9090**（和 Netty 示例同一个数字，但是 Tomcat）：

```bash
grpcurl --plaintext localhost:9090 list
grpcurl -d '{"name":"Alien"}' --plaintext localhost:9090 Simple/SayHello
```

客户端通道仍是 9090：

```properties
spring.grpc.client.channel.default.target=static://localhost:9090
```

Actuator 和 gRPC 在同一个进程、同一个端口。`curl http://localhost:9090/actuator/health` 这次能打通。

测试不要用 `@AutoConfigureTestGrpcTransport` 冒充 Servlet。官方是 `WebEnvironment.RANDOM_PORT`，地址写成 `static://127.0.0.1:${local.server.port}`。这才是 1.0 同端口文章里那套写法适用的场景。

安全改走 `SecurityFilterChain`，见下面「安全」一节的 Servlet 部分。WebFlux 目前不能和 gRPC 共用一个 HTTP 端口。

## 原生镜像构建

Spring gRPC 能编 GraalVM Native Image。前面 Initializr 已经勾了 `native`，服务端和客户端都可以：

```bash
./mvnw native:compile -Pnative
```

编完直接跑二进制，不用再 `java -jar`：

```bash
./target/grpc-server
./target/grpc-client
```

启动会快不少，内存也会下来。

## 安全

这篇默认是 **Netty 独立端口 9090**。完整示例在 [spring-boot-grpc-samples](https://github.com/zhijunio/spring-boot-grpc-samples) 的 `grpc-server-secure`，对齐官方 [samples/grpc-secure](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-secure)。Servlet 同端口的 Security 在 `grpc-server-tomcat-secure`。OAuth2 在 `auth-server` / `grpc-server-oauth2` / `grpc-client-oauth2`，对齐官方 [samples/grpc-oauth2](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-oauth2)。TLS 没有单独模块；`grpc-server` 的 `GrpcServerIntegrationTests` 里有 ssl profile（`test.jks`），和官方 sample 一样。

服务端 pom 加上：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

start.spring.io 上勾选 ID 是 `security`。Boot 会配好 `GrpcSecurity` 和 `AuthenticationManager`。但 **只有 gRPC、没有 Web 时，不会自动建 `UserDetailsService`**，`spring.security.user.name` / `password` 也不会生效。要自己写一个。官方 sample 密码和用户名相同，用 `{noop}`：

```java
@Bean
InMemoryUserDetailsManager inMemoryUserDetailsManager() {
    return new InMemoryUserDetailsManager(
            User.withUsername("user").password("{noop}user").authorities("ROLE_USER").build(),
            User.withUsername("admin").password("{noop}admin").authorities("ROLE_ADMIN").build());
}
```

### Netty：用 GrpcSecurity 配拦截器

Netty 这条线 **不是** `SecurityFilterChain`。写一个全局拦截器，用 `GrpcSecurity` 配，风格接近 Web 的 `HttpSecurity`。方法名是 `服务/方法`。proto 没有 `package`，和官方 sample 一样写成 `Simple/SayHello`。Reflection 和 Health 要放行，否则 `grpcurl list` 也会失败。

拦截器 bean **不要叫 `grpcSecurity`**。自动配置已经用这个名字注册了 `GrpcSecurity` 本身，重名会 `BeanDefinitionOverrideException`。官方 sample 叫 `securityInterceptor`：

```java
@Bean
@GlobalServerInterceptor
ServerInterceptor securityInterceptor(GrpcSecurity security) throws Exception {
    return security
            .authorizeRequests(requests -> requests
                    .methods("Simple/StreamHello").hasAuthority("ROLE_ADMIN")
                    .methods("Simple/SayHello").hasAuthority("ROLE_USER")
                    .methods("grpc.*/*").permitAll()
                    .allRequests().denyAll())
            .httpBasic(withDefaults())
            .preauth(withDefaults())
            .build();
}
```

`SayHello` 要 `ROLE_USER`，`StreamHello` 要 `ROLE_ADMIN`。也可以把规则写在服务方法上，打开 `@EnableMethodSecurity` 再用 `@PreAuthorize`。官方 sample 把这行注释掉了，鉴权全走拦截器。

`.preauth(withDefaults())` 允许用 metadata 头 `X-USER` 声明用户名（不配密码）。HTTP Basic 仍要用户名和密码。

客户端 **不必** 加 `spring-boot-starter-security`。`BasicAuthenticationInterceptor` 在 `spring-grpc-core` 里，grpc-client starter 已经带了。`grpc-client-secure` 给默认通道挂上 Basic，对应 `grpc-server-secure` 里的 `user`/`user`：

```java
@Bean
GrpcChannelBuilderCustomizer<?> basicAuthCustomizer() {
    return GrpcChannelBuilderCustomizer.matching("default",
            (builder) -> builder.intercept(new BasicAuthenticationInterceptor("user", "user")));
}
```

`grpc-server-secure` 的测试里另开名叫 `secure` 的通道，同样用这个 interceptor，和默认通道分开：

```java
@Bean
GrpcChannelBuilderCustomizer<?> basicStubsCustomizer() {
    return GrpcChannelBuilderCustomizer.matching("secure",
            (builder) -> builder.intercept(new BasicAuthenticationInterceptor("user", "user")));
}
```

`grpcurl` 两种都能打 `SayHello`。Health / Reflection 仍可不带：

```bash
grpcurl --plaintext localhost:9090 list
grpcurl --plaintext -H 'X-USER: user' \
  -d '{"name":"Alien"}' localhost:9090 Simple/SayHello
grpcurl --plaintext \
  -H "authorization: Basic $(printf 'user:user' | base64)" \
  -d '{"name":"Alien"}' localhost:9090 Simple/SayHello
```

不带凭证打 `SayHello`，会拿到 `UNAUTHENTICATED`。用 `user` 去打 `StreamHello`，会拿到 `PERMISSION_DENIED`（要 `admin`）。

### 测试也要过 Security

`grpc-server-secure` 用随机 gRPC 端口（`spring.grpc.server.port=0`），再开三条客户端通道：不带凭证、带 Basic、只调 Reflection。`@AutoConfigureTestGrpcTransport` 的进程内通道工厂 **不会** 应用 `GrpcChannelBuilderCustomizer`，所以这条测试不走进程内，走真 TCP。

不要为了让测试变绿去关 Security。`grpc-client` 没有带 Basic，连无认证的 `grpc-server`；打 `grpc-server-secure` 用 `grpc-client-secure`；打 `grpc-server-tomcat-secure` 用 `grpc-client-tomcat-secure`。

### Servlet 同端口：走 SecurityFilterChain

gRPC 已经改成和 Tomcat 共用一个端口时，按普通 Web 应用写 `SecurityFilterChain` 即可。完整示例在 `grpc-server-tomcat-secure`，对齐官方 [samples/grpc-tomcat-secure](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-tomcat-secure)。客户端用 `grpc-client-tomcat-secure`，拦截器和 `grpc-client-secure` 一样，仍是默认通道上的 `BasicAuthenticationInterceptor("user", "user")`，不必加 `starter-security`。有 Web 时，`spring.security.user.name` / `password` **会生效**，不必再手写 `UserDetailsService`：

```properties
spring.security.user.name=user
spring.security.user.password=user
```

Spring Boot 会配好 `SecurityContextServerInterceptor`，让安全上下文进到 gRPC 调用线程。官方 sample 不另写 `GrpcSecurity`，默认 HTTP Basic，未认证打 `SayHello` 是 `UNAUTHENTICATED`。

若要按方法收紧，匹配路径可以用 `GrpcRequest`：

```java
@Bean
SecurityFilterChain grpcSecurityFilterChain(HttpSecurity http) throws Exception {
    http.securityMatcher(GrpcRequest.toAnyService());
    http.authorizeHttpRequests(requests -> requests
            .requestMatchers("/Simple/SayHello").hasRole("USER")
            .requestMatchers("/grpc.*/*").permitAll()
            .anyRequest().authenticated());
    http.httpBasic(Customizer.withDefaults());
    return http.build();
}
```

gRPC 和 CSRF 合不来，**gRPC 请求默认关 CSRF**。如果你要自己配 CSRF，设 `spring.grpc.server.security.csrf.enabled=false` 会关掉这个自动行为。官方还有一个测试专门演示整条 `SecurityFilterChain` 手动 `csrf.disable()`。Servlet 路径也可以继续在方法上用 `@PreAuthorize`。

### TLS 和 mTLS

传输加密走 Spring Boot 的 SSL bundle，不是另搞一套 gRPC 证书配置。服务端：

```properties
spring.ssl.bundle.jks.grpc.keystore.location=classpath:keystore.jks
spring.ssl.bundle.jks.grpc.keystore.password=secret
spring.grpc.server.ssl.bundle=grpc
```

客户端单向 TLS：

```properties
spring.grpc.client.channel.default.ssl.enabled=true
```

双向 TLS 时，客户端也指定 bundle：`spring.grpc.client.channel.default.ssl.bundle=grpc`。服务端要校验证书可以设
`spring.grpc.server.ssl.client-auth=require`。本地自签证书排错，可以临时
`spring.grpc.client.channel.default.bypass-certificate-validation=true`，不要带进生产。

### OAuth2 Resource Server

完整示例在 `auth-server`、`grpc-server-oauth2`、`grpc-client-oauth2`。官方 [samples/grpc-oauth2](https://github.com/spring-projects/spring-grpc/tree/main/samples/grpc-oauth2) 用 testjars 在测试里起随机端口认证服务器；这边测试同样用 testjars。运行时用独立的 `auth-server`（9000），三个进程能跑通。

资源服务器用 `spring-boot-starter-oauth2-resource-server`。JWK 默认指向 `auth-server:9000`；测试里 `@OAuth2ClientProviderIssuerUri` 会改 `spring.security.oauth2.client.provider.spring.issuer-uri`，所以写成占位：

```properties
spring.security.oauth2.resourceserver.jwt.jwk-set-uri=${spring.security.oauth2.client.provider.spring.issuer-uri:http://localhost:9000}/oauth2/jwks
spring.security.oauth2.client.registration.spring.client-id=spring
spring.security.oauth2.client.registration.spring.client-secret=secret
spring.security.oauth2.client.registration.spring.authorization-grant-type=client_credentials
spring.security.oauth2.client.registration.spring.provider=local
spring.security.oauth2.client.provider.local.token-uri=${spring.security.oauth2.client.provider.spring.issuer-uri:http://localhost:9000}/oauth2/token
```

资源服务器 main 里这份 client 配置是给测试用的：`ClientCredentialsTokenSupplier` 要 `ClientRegistrationRepository`。真正跑客户端时用 `grpc-client-oauth2`，token 打 `http://localhost:9000/oauth2/token`。

Netty 上在 `GrpcSecurity` 里打开 JWT。方法名写成 `Simple/SayHello`：

```java
@Bean
@GlobalServerInterceptor
AuthenticationProcessInterceptor jwtSecurityFilterChain(GrpcSecurity grpc) throws Exception {
    return grpc
            .authorizeRequests(requests -> requests
                    .methods("Simple/StreamHello").hasAuthority("SCOPE_profile")
                    .methods("Simple/SayHello").authenticated()
                    .methods("grpc.*/*").permitAll()
                    .allRequests().denyAll())
            .oauth2ResourceServer(resourceServer -> resourceServer.jwt(withDefaults()))
            .build();
}
```

没有 Web 时，还要 `@Import(AuthenticationConfiguration.class)`，否则 `AuthenticationManager` 配不齐。

客户端用 `spring-boot-starter-oauth2-client`，不必加 Web。默认通道挂 `BearerTokenAuthenticationInterceptor`，token 用 `ClientCredentialsTokenSupplier` 向 `auth-server` 换：

```java
@Bean
GrpcChannelBuilderCustomizer<?> bearerCustomizer(ClientRegistrationRepository registry) {
    return GrpcChannelBuilderCustomizer.matching("default", (builder) -> builder.intercept(
            new BearerTokenAuthenticationInterceptor(
                    new ClientCredentialsTokenSupplier(registry, () -> "spring"))));
}
```

client 是 `spring` / `secret`，grant 是 `client_credentials`。`SayHello` 只要合法 JWT；`StreamHello` 要 `SCOPE_profile`。默认换到的令牌没有这个 scope，打流会 `PERMISSION_DENIED`。

```bash
cd auth-server && ./mvnw spring-boot:run
cd grpc-server-oauth2 && ./mvnw spring-boot:run
cd grpc-client-oauth2 && ./mvnw spring-boot:run
```

不透明 token 走 introspection，属性和 Web 应用相同。仓库没有单独的 opaque 运行模块；`grpc-server-oauth2` 的 `OpaqueTokenServerApplicationTests` 同样用 testjars 起认证服务器，再覆盖拦截器，introspection 地址是 `issuer-uri + /oauth2/introspect`，client 仍是 `spring` / `secret`。

## 和 1.0 对照

|            | Spring Boot 4.0 + Spring gRPC 1.0                | Spring Boot 4.1（这篇用 4.1.1）                              |
|------------|--------------------------------------------------|-------------------------------------------------------------|
| starter    | `org.springframework.grpc:spring-grpc-*-starter` | `org.springframework.boot:spring-boot-starter-grpc-*`       |
| 默认跑法   | 勾 Web 时常走 Servlet，和 HTTP 共用 8080         | Netty 独立端口 9090                                         |
| 服务注册   | 示例里常见 `@Service`                            | 任意 `BindableService` bean 即可；官方 sample 用 `@Service`，文档也常见 `@GrpcService` |
| 客户端通道 | `default-channel.address` / `channels.*.address` | `channel.<name>.target`                                     |
| Stub 注册  | 常有自动扫描的习惯                               | 必须写 `@ImportGrpcClients`                                 |
| 测试       | 常绑随机 Web 端口                                | `@AutoConfigureTestGrpcTransport` / `@LocalGrpcServerPort`  |

## 总结

Spring Boot 4 能写 gRPC，但要分清两代。4.0 靠的是独立项目 Spring gRPC 1.0；到了 4.1，自动配置才进 Spring Boot 本身，starter
也换成 `spring-boot-starter-grpc-server` / `grpc-client`。默认是 Netty 听 9090，不再因为勾了 Web 就和 HTTP
挤一个端口。Reflection 和 Health 跟着 starter 走，不用再手加 `grpc-services`。

写服务时，把 `BindableService` 做成 Spring bean 就会挂上，官方 sample 用 `@Service`。写客户端时，通道走
`spring.grpc.client.channel.<名字>.target`，stub 必须 `@ImportGrpcClients`，4.1 不会再自动扫。测试优先
`@AutoConfigureTestGrpcTransport`，进程里通信，不占 9090。

需要和 Tomcat 共用端口，再改成 `grpc-servlet-jakarta` 并打开 HTTP/2。Micrometer Observation 默认会给 gRPC 打点；日志仍要自己接
OTLP。流处理复杂时，可以接 Salesforce reactive-grpc，用 `Mono` / `Flux` 写，`reactor-grpc-stub` 的版本需要手动指定。GraalVM
Native Image 也能编。安全方面：Netty 用 `GrpcSecurity` 配 HTTP Basic 或 OAuth2，Servlet 同端口用 `SecurityFilterChain` 和
`GrpcRequest`；传输加密走 SSL bundle。

网上不少笔记还停在 1.0 + Servlet 同端口那套。对着 Spring Boot 4.1.1 做的话，先换坐标和属性名，再抄代码。


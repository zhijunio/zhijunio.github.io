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

完整可跑的代码在 [zhijunio/spring-boot-grpc-samples](https://github.com/zhijunio/spring-boot-grpc-samples)：`grpc-server` 听 9090，`grpc-client` 用 HTTP 8082 调 stub。`main` 是默认 Netty 路径；HTTP Basic 在 `security` 分支。Reactor、Native、Servlet 同端口只在文里写，没有放进示例。

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

接下来写 Protocol Buffers 的 `.proto`。服务定义参考 [gRPC 文档](https://grpc.io/docs/what-is-grpc/core-concepts/#service-definition) 里的示例。这篇只做一元调用和服务端流，客户端流和双向流不写实现。

```bash
cat <<EOF > src/main/proto/hello.proto
syntax = "proto3";

package com.example;

option java_package = "com.example.proto";
option java_outer_classname = "HelloServiceProto";
option java_multiple_files = true;

service HelloService {
  rpc SayHello (HelloRequest) returns (HelloResponse);
  rpc LotsOfReplies (HelloRequest) returns (stream HelloResponse);
  rpc LotsOfGreetings(stream HelloRequest) returns (HelloResponse);
  rpc BidiHello(stream HelloRequest) returns (stream HelloResponse);
}

message HelloRequest {
  string greeting = 1;
}

message HelloResponse {
  string reply = 1;
}
EOF
```

先编译 proto，生成 Java 代码。用 Spring Initializr 建项目时，`protobuf-maven-plugin` 已经在 pom 里了。

执行 `./mvnw compile`，就会在 `target/generated-sources` 里生成 Java 代码和 stub。生成结果大概是：

```bash
$ find target/generated-sources/protobuf -type f
target/generated-sources/protobuf/com/example/proto/HelloServiceProto.java
target/generated-sources/protobuf/com/example/proto/HelloRequest.java
target/generated-sources/protobuf/com/example/proto/HelloResponseOrBuilder.java
target/generated-sources/protobuf/com/example/proto/HelloRequestOrBuilder.java
target/generated-sources/protobuf/com/example/proto/HelloServiceGrpc.java
target/generated-sources/protobuf/com/example/proto/HelloResponse.java
```

实现服务：继承 `HelloServiceGrpc.HelloServiceImplBase`，标上 `@GrpcService`，就会进容器并挂到 gRPC 服务器上。只标 `@Service` 也可以，因为同样是 `BindableService` bean。

```bash
cat <<EOF > src/main/java/com/example/HelloService.java
package com.example;

import com.example.proto.HelloRequest;
import com.example.proto.HelloResponse;
import com.example.proto.HelloServiceGrpc;
import io.grpc.stub.StreamObserver;
import org.springframework.grpc.server.service.GrpcService;

@GrpcService
public class HelloService extends HelloServiceGrpc.HelloServiceImplBase {

    @Override
    public void sayHello(HelloRequest request, StreamObserver<HelloResponse> responseObserver) {
        HelloResponse response = HelloResponse.newBuilder()
                .setReply("Hello %s!".formatted(request.getGreeting()))
                .build();
        responseObserver.onNext(response);
        responseObserver.onCompleted();
    }

    @Override
    public void lotsOfReplies(HelloRequest request, StreamObserver<HelloResponse> responseObserver) {
        for (int i = 0; i < 10; i++) {
            responseObserver.onNext(HelloResponse.newBuilder()
                    .setReply("[%05d] Hello %s!".formatted(i, request.getGreeting()))
                    .build());
        }
        responseObserver.onCompleted();
    }

}
EOF
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

com.example.HelloService
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

再看自己写的 `com.example.HelloService` 有哪些方法：

```bash
$ grpcurl --plaintext localhost:9090 describe com.example.HelloService

com.example.HelloService is a service:
service HelloService {
  rpc BidiHello ( stream .com.example.HelloRequest ) returns ( stream .com.example.HelloResponse );
  rpc LotsOfGreetings ( stream .com.example.HelloRequest ) returns ( .com.example.HelloResponse );
  rpc LotsOfReplies ( .com.example.HelloRequest ) returns ( stream .com.example.HelloResponse );
  rpc SayHello ( .com.example.HelloRequest ) returns ( .com.example.HelloResponse );
}
```

先打 `SayHello`。请求用 JSON；本地没开 TLS，加上 `--plaintext`。

```bash
$ grpcurl -d '{"greeting":"John Doe"}' --plaintext localhost:9090 com.example.HelloService/SayHello
{
  "reply": "Hello John Doe!"
}
```

接下来执行 `LotsOfReplies`，这是服务端连续回多条的方法。

```bash
$ grpcurl -d '{"greeting":"John Doe"}' --plaintext localhost:9090 com.example.HelloService/LotsOfReplies
{
  "reply": "[00000] Hello John Doe!"
}
{
  "reply": "[00001] Hello John Doe!"
}
{
  "reply": "[00002] Hello John Doe!"
}
{
  "reply": "[00003] Hello John Doe!"
}
{
  "reply": "[00004] Hello John Doe!"
}
{
  "reply": "[00005] Hello John Doe!"
}
{
  "reply": "[00006] Hello John Doe!"
}
{
  "reply": "[00007] Hello John Doe!"
}
{
  "reply": "[00008] Hello John Doe!"
}
{
  "reply": "[00009] Hello John Doe!"
}
```

接下来写测试。

Spring Boot 4.1 **不会**再自动扫出 stub bean。测试里要注入 `HelloServiceBlockingStub`，必须加上 `@ImportGrpcClients`。
`@AutoConfigureTestGrpcTransport` 会走进程内通道，不用占 9090。

```bash
cat<<EOF > src/test/java/com/example/HelloServiceTest.java
package com.example;

import com.example.proto.HelloRequest;
import com.example.proto.HelloResponse;
import com.example.proto.HelloServiceGrpc;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.grpc.test.autoconfigure.AutoConfigureTestGrpcTransport;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.grpc.client.ImportGrpcClients;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@AutoConfigureTestGrpcTransport
@ImportGrpcClients(types = HelloServiceGrpc.HelloServiceBlockingStub.class)
class HelloServiceTest {

	@Autowired
	HelloServiceGrpc.HelloServiceBlockingStub stub;

	@Test
	void sayHello() {
		HelloResponse response = this.stub.sayHello(HelloRequest.newBuilder().setGreeting("John Doe").build());
		assertThat(response.getReply()).isEqualTo("Hello John Doe!");
	}

	@Test
	void lotsOfReplies() {
		List<String> replies = new ArrayList<>();
		this.stub.lotsOfReplies(HelloRequest.newBuilder().setGreeting("John Doe").build())
			.forEachRemaining(r -> replies.add(r.getReply()));
		assertThat(replies).containsExactly("[00000] Hello John Doe!", "[00001] Hello John Doe!",
				"[00002] Hello John Doe!", "[00003] Hello John Doe!", "[00004] Hello John Doe!",
				"[00005] Hello John Doe!", "[00006] Hello John Doe!", "[00007] Hello John Doe!",
				"[00008] Hello John Doe!", "[00009] Hello John Doe!");
	}

}

EOF
```

跑测试：

```bash
./mvnw test
```

Initializr 还会生成一个 `*ApplicationTests`，里面是空的 `contextLoads`。它会把整台 Netty 拉起来，默认仍占 **9090**。本机已经 `spring-boot:run` 的话，这个测试会端口冲突。可以删掉，或者只保留上面带 `@AutoConfigureTestGrpcTransport` 的测试。

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
spring.grpc.client.channel.hello.target=in-process:hello
```

`@ImportGrpcClients(target = "hello", ...)` 不用改，还是对这条叫 `hello` 的通道。

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
       -d dependencies=spring-grpc-client,web,actuator,configuration-processor,prometheus,opentelemetry,native \
       -d type=maven-project \
       -d applicationName=GrpcClientApplication | tar -xzvf -
cd grpc-client
```

`.proto` 和服务端同一份：

```bash
cat <<EOF > src/main/proto/hello.proto
syntax = "proto3";

package com.example;

option java_package = "com.example.proto";
option java_outer_classname = "HelloServiceProto";
option java_multiple_files = true;

service HelloService {
  rpc SayHello (HelloRequest) returns (HelloResponse);
  rpc LotsOfReplies (HelloRequest) returns (stream HelloResponse);
  rpc LotsOfGreetings(stream HelloRequest) returns (HelloResponse);
  rpc BidiHello(stream HelloRequest) returns (stream HelloResponse);
}

message HelloRequest {
  string greeting = 1;
}

message HelloResponse {
  string reply = 1;
}
EOF
```

再 `./mvnw compile`，生成 stub。

```bash
./mvnw compile
```

和 1.0 不同的是： **客户端 stub 不会再自动扫包注册成 bean**
。你要在配置类或启动类上显式写 `@ImportGrpcClients`，指定要注入哪种 stub，以及它连哪条通道（这里把通道叫做 `hello`）：

```bash
cat <<EOF > src/main/java/com/example/GrpcClientApplication.java
package com.example;

import com.example.proto.HelloServiceGrpc;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.grpc.client.ImportGrpcClients;

@SpringBootApplication(proxyBeanMethods = false)
@ImportGrpcClients(target = "hello", types = HelloServiceGrpc.HelloServiceBlockingStub.class)
public class GrpcClientApplication {

    public static void main(String[] args) {
        SpringApplication.run(GrpcClientApplication.class, args);
    }

}
EOF
```

通道名字要对应到实际要连的地址。Spring Boot 4.1 中属性前缀是 `spring.grpc.client.channel.<名字>.target`。

```bash
cat <<EOF >> src/main/resources/application.properties
server.port=8082
spring.grpc.client.channel.hello.target=static://localhost:9090
management.otlp.metrics.export.enabled=false
EOF
```

为了方便用 curl 验证，外面再包一层普通的 Spring MVC。浏览器或 curl 发 HTTP 请求，控制器里再调用 gRPC stub：

```bash
cat <<EOF > src/main/java/com/example/HelloController.java
package com.example;

import com.example.proto.HelloRequest;
import com.example.proto.HelloResponse;
import com.example.proto.HelloServiceGrpc;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    private final HelloServiceGrpc.HelloServiceBlockingStub helloServiceStub;

    public HelloController(HelloServiceGrpc.HelloServiceBlockingStub helloServiceStub) {
        this.helloServiceStub = helloServiceStub;
    }

    @GetMapping("/")
    public Reply sayHello(@RequestParam String greeting) {
        HelloResponse response = helloServiceStub.sayHello(
                HelloRequest.newBuilder().setGreeting(greeting).build());
        return new Reply(response.getReply());
    }

    @GetMapping("/lots-of-replies")
    public List<Reply> lotsOfReplies(@RequestParam String greeting) {
        Iterator<HelloResponse> replies = helloServiceStub.lotsOfReplies(
                HelloRequest.newBuilder().setGreeting(greeting).build());
        List<Reply> result = new ArrayList<>();
        replies.forEachRemaining(r -> result.add(new Reply(r.getReply())));
        return result;
    }

    public record Reply(String reply) {
    }

}
EOF
```

启动客户端：

```bash
./mvnw spring-boot:run
```

客户端 HTTP 口是 8082，用 curl 打：

```bash
$ curl -s "http://localhost:8082?greeting=John%20Doe" | jq .
{
  "reply": "Hello John Doe!"
}

$ curl -s "http://localhost:8082/lots-of-replies?greeting=John%20Doe" | jq .
[
  {
    "reply": "[00000] Hello John Doe!"
  },
  {
    "reply": "[00001] Hello John Doe!"
  },
  {
    "reply": "[00002] Hello John Doe!"
  },
  {
    "reply": "[00003] Hello John Doe!"
  },
  {
    "reply": "[00004] Hello John Doe!"
  },
  {
    "reply": "[00005] Hello John Doe!"
  },
  {
    "reply": "[00006] Hello John Doe!"
  },
  {
    "reply": "[00007] Hello John Doe!"
  },
  {
    "reply": "[00008] Hello John Doe!"
  },
  {
    "reply": "[00009] Hello John Doe!"
  }
]
```

HTTP 已经转到 gRPC 了。

客户端测试不必真的连 9090。用 `@WebMvcTest` 只拉起 MVC，再用 `@MockitoBean` 把 stub 换成假的，就能测 `HelloController` 有没有把
HTTP 参数转成 gRPC 请求：

```bash
cat<<EOF > src/test/java/com/example/HelloControllerTest.java
package com.example;

import com.example.proto.HelloRequest;
import com.example.proto.HelloResponse;
import com.example.proto.HelloServiceGrpc;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(HelloController.class)
class HelloControllerTest {

	@Autowired
	MockMvc mockMvc;

	@MockitoBean
	HelloServiceGrpc.HelloServiceBlockingStub helloServiceStub;

	@Test
	void sayHello() throws Exception {
		when(this.helloServiceStub.sayHello(any(HelloRequest.class)))
			.thenReturn(HelloResponse.newBuilder().setReply("Hello John Doe!").build());

		this.mockMvc.perform(get("/").param("greeting", "John Doe"))
			.andExpect(status().isOk())
			.andExpect(jsonPath("$.reply").value("Hello John Doe!"));
	}

}
EOF
```

```bash
./mvnw -Dtest=HelloControllerTest test
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

重启两边，再打一遍客户端请求：

```bash
curl -s "http://localhost:8082?greeting=John%20Doe"
curl -s "http://localhost:8082/lots-of-replies?greeting=John%20Doe" | jq .
```

Grafana 在 http://localhost:3000，Tempo 里能看到服务端和客户端的 gRPC span。前面关掉的是 OTLP **metrics** 导出，tracing 这条不受影响。

Prometheus scrape 走的是 **HTTP Actuator**，不是 gRPC。默认 Netty 听的 **9090 不是 HTTP**，`curl localhost:9090/actuator/prometheus` 打不通。这篇服务端没勾 Web，所以服务端没有 `/actuator` HTTP 口；示例里 metrics 的 OTLP 也是关着的，服务端指标不会进 LGTM。客户端勾了 Web，端口是 8082：

```bash
curl -s http://localhost:8082/actuator/prometheus | grep grpc | grep -v '^disk'
```

如果一定要在服务端也 scrape Prometheus，给服务端加上 Web，或者单独开 `management.server.port`，别指望 9090。

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

`target/generated-sources/protobuf` 里会多一个 `ReactorHelloServiceGrpc.java`。原来的 `HelloServiceGrpc` 还在。

### 客户端改成 Reactor stub

`HelloController` 改成注入 `ReactorHelloServiceStub`，接口返回 `Mono` / `Flux`：

```java
package com.example;

import com.example.proto.HelloRequest;
import com.example.proto.ReactorHelloServiceGrpc;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
public class HelloController {

    private final ReactorHelloServiceGrpc.ReactorHelloServiceStub helloServiceStub;

    public HelloController(ReactorHelloServiceGrpc.ReactorHelloServiceStub helloServiceStub) {
        this.helloServiceStub = helloServiceStub;
    }

    @GetMapping("/")
    public Mono<Reply> sayHello(@RequestParam String greeting) {
        return helloServiceStub.sayHello(HelloRequest.newBuilder().setGreeting(greeting).build())
                .map(r -> new Reply(r.getReply()));
    }

    @GetMapping("/lots-of-replies")
    public Flux<Reply> lotsOfReplies(@RequestParam String greeting) {
        return helloServiceStub.lotsOfReplies(HelloRequest.newBuilder().setGreeting(greeting).build())
                .map(r -> new Reply(r.getReply()));
    }

    public record Reply(String reply) {
    }

}
```

Reactor 的 stub **不会**跟着 BlockingStub 自动进来，要单独 `@ImportGrpcClients`。通道名还是前面的 `hello`：

```java
package com.example;

import com.example.proto.ReactorHelloServiceGrpc;
import org.springframework.context.annotation.Configuration;
import org.springframework.grpc.client.ImportGrpcClients;

@Configuration(proxyBeanMethods = false)
@ImportGrpcClients(target = "hello", types = ReactorHelloServiceGrpc.ReactorHelloServiceStub.class)
public class GrpcConfig {

}
```

启动类上如果还留着 `HelloServiceBlockingStub` 的 `@ImportGrpcClients`，可以删掉，避免两个 stub 抢同一套通道配置。

`HelloControllerTest` 也要跟着改：`@MockitoBean` 换成 `ReactorHelloServiceStub`，`when(...).thenReturn(...)` 改成返回
`Mono.just(...)`。

重启客户端后，curl 还是可以当普通 JSON 用：

```bash
curl -s "http://localhost:8082/?greeting=John%20Doe"
curl -s "http://localhost:8082/lots-of-replies?greeting=John%20Doe"
```

返回类型是 `Flux` 时，客户端还可以要流式响应。按行 JSON：

```bash
curl "http://localhost:8082/lots-of-replies?greeting=John%20Doe" -H "Accept: application/x-ndjson"
```

或者 Server-Sent Events：

```bash
curl "http://localhost:8082/lots-of-replies?greeting=John%20Doe" -H "Accept: text/event-stream"
```

### 服务端也改成 Reactor

```java
package com.example;

import com.example.proto.HelloRequest;
import com.example.proto.HelloResponse;
import com.example.proto.ReactorHelloServiceGrpc;
import org.springframework.grpc.server.service.GrpcService;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@GrpcService
public class HelloService extends ReactorHelloServiceGrpc.HelloServiceImplBase {

    @Override
    public Mono<HelloResponse> sayHello(Mono<HelloRequest> request) {
        return request
                .map(req -> HelloResponse.newBuilder().setReply("Hello %s!".formatted(req.getGreeting())).build());
    }

    @Override
    public Flux<HelloResponse> lotsOfReplies(Mono<HelloRequest> request) {
        return request.flatMapMany(req -> Flux.range(0, 10)
                .map(i -> HelloResponse.newBuilder()
                        .setReply("[%05d] Hello %s!".formatted(i, req.getGreeting()))
                        .build()));
    }

}
```

`sayHello` 也可以写成接收已经拆好的 `HelloRequest`，再 `return Mono.just(...)`，两种都能编过。

这个例子本身几乎没有真正的流处理，差别不明显。真要拼、过滤、背压的时候，用 Reactor 会比手写 `StreamObserver` 好读。

服务端测试改成 Reactor stub 加上 `StepVerifier`。还是用 `@AutoConfigureTestGrpcTransport`，不要退回 1.0 那套随机 Web 端口：

```java
package com.example;

import com.example.proto.HelloRequest;
import com.example.proto.HelloResponse;
import com.example.proto.ReactorHelloServiceGrpc;
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
@ImportGrpcClients(types = ReactorHelloServiceGrpc.ReactorHelloServiceStub.class)
class HelloServiceTest {

    @Autowired
    ReactorHelloServiceGrpc.ReactorHelloServiceStub stub;

    @Test
    void sayHello() {
        Mono<HelloResponse> response = this.stub.sayHello(HelloRequest.newBuilder().setGreeting("John Doe").build());
        StepVerifier.create(response)
                .assertNext(r -> assertThat(r.getReply()).isEqualTo("Hello John Doe!"))
                .verifyComplete();
    }

    @Test
    void lotsOfReplies() {
        Flux<HelloResponse> response = this.stub
                .lotsOfReplies(HelloRequest.newBuilder().setGreeting("John Doe").build());
        StepVerifier.create(response)
                .expectNextCount(10)
                .verifyComplete();
    }

}
```

测 gRPC 时，Blocking stub 和 Reactor stub 都可以，选一种即可。

## Servlet 同端口

前面默认的服务端是 **Netty 自己听 9090**。就算 pom 里已经有 WebMVC，4.1 也不会自动把 gRPC 绑到 HTTP 那个口上。如果你想像 4.0 早期教程那样，**普通 HTTP 和 gRPC 共用一个端口**（一般是 8080），要自己改成 Servlet 实现。

`HelloService` 不用改。变的是传输层：请求进 Tomcat（或 Jetty），由 `grpc-servlet-jakarta` 转给 gRPC。容器必须开 **HTTP/2**，明文调试用的是 h2c。

### 改依赖

排除 `grpc-netty`，加上 WebMVC 和 Servlet 适配：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webmvc</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-grpc-server</artifactId>
    <exclusions>
        <exclusion>
            <groupId>io.grpc</groupId>
            <artifactId>grpc-netty</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-servlet-jakarta</artifactId>
</dependency>
```

`webmvc` 已经带 Tomcat。打开 HTTP/2：

```properties
server.http2.enabled=true
server.port=8080
```

这种模式下 **`spring.grpc.server.port` 无效**，端口只看 `server.port`。keepalive、Netty 专属属性也会被忽略。

如果 **不排除** `grpc-netty`，同时又有 WebMVC：HTTP 仍走 8080，gRPC 继续走 9090，那是两个口，不是同端口。

### 怎么调

服务起来后，`grpcurl` 打 **8080**，不是 9090：

```bash
grpcurl --plaintext localhost:8080 list
grpcurl -d '{"greeting":"John Doe"}' --plaintext localhost:8080 com.example.HelloService/SayHello
```

客户端通道也改成 8080：

```properties
spring.grpc.client.channel.hello.target=static://localhost:8080
```

Actuator 和 MVC 接口跟 gRPC 在同一个进程、同一个端口。`HelloController` 那种「外面 HTTP、里面再调 gRPC」如果和服务器放在**同一个应用**里，通道可以写成进程内；分两个进程时，客户端仍指向这台机的 8080。

测试还是优先 `@AutoConfigureTestGrpcTransport`。如果一定要真走 Servlet 网络，用 `WebEnvironment.RANDOM_PORT`，地址写成 `static://127.0.0.1:${local.server.port}`。这才是 1.0 同端口文章里那套写法适用的场景。

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

这篇默认是 **Netty 独立端口 9090**。示例在 [spring-boot-grpc-samples](https://github.com/zhijunio/spring-boot-grpc-samples) 的 `security` 分支：服务端加 HTTP Basic，客户端通道自动带上同样的凭证。Servlet 同端口、TLS、OAuth2 下面另写，仓库里没有。

服务端 pom 加上：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

start.spring.io 上勾选 ID 是 `security`。Boot 会配好 `GrpcSecurity` 和 `AuthenticationManager`。但 **只有 gRPC、没有 Web 时，不会自动建 `UserDetailsService`**，`spring.security.user.name` / `password` 也不会生效。要自己写一个，密码用 `{noop}`：

```java
@Bean
UserDetailsService userDetailsService() {
    return new InMemoryUserDetailsManager(
            User.withUsername("user").password("{noop}password").roles("USER").build());
}
```

### Netty：用 GrpcSecurity 配拦截器

Netty 这条线 **不是** `SecurityFilterChain`。写一个全局拦截器，用 `GrpcSecurity` 配，风格接近 Web 的 `HttpSecurity`。方法名是 `服务/方法`。Reflection 和 Health 要放行，否则 `grpcurl list` 也会失败。

拦截器 bean **不要叫 `grpcSecurity`**。自动配置已经用这个名字注册了 `GrpcSecurity` 本身，重名会 `BeanDefinitionOverrideException`。示例里叫 `authenticationProcessInterceptor`：

```java
package com.example;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.grpc.server.GlobalServerInterceptor;
import org.springframework.grpc.server.security.AuthenticationProcessInterceptor;
import org.springframework.grpc.server.security.GrpcSecurity;
import org.springframework.security.config.Customizer;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;

@Configuration(proxyBeanMethods = false)
public class GrpcSecurityConfiguration {

    @Bean
    UserDetailsService userDetailsService() {
        return new InMemoryUserDetailsManager(
                User.withUsername("user").password("{noop}password").roles("USER").build());
    }

    @Bean
    @GlobalServerInterceptor
    AuthenticationProcessInterceptor authenticationProcessInterceptor(GrpcSecurity grpc) throws Exception {
        return grpc
                .authorizeRequests(requests -> requests
                        .methods("com.example.HelloService/SayHello").hasAuthority("ROLE_USER")
                        .methods("com.example.HelloService/LotsOfReplies").hasAuthority("ROLE_USER")
                        .methods("grpc.*/*").permitAll()
                        .allRequests().authenticated())
                .httpBasic(Customizer.withDefaults())
                .preauth(Customizer.withDefaults())
                .build();
    }

}
```

也可以把规则写在服务方法上，打开 `@EnableMethodSecurity` 再用 `@PreAuthorize("hasRole('USER')")`。示例没用这条。

客户端 **不必** 加 `spring-boot-starter-security`。`BasicAuthenticationInterceptor` 在 `spring-grpc-core` 里，grpc-client starter 已经带了。用 `GrpcChannelBuilderCustomizer` 只匹配名叫 `hello` 的通道：

```java
package com.example;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.grpc.client.GrpcChannelBuilderCustomizer;
import org.springframework.grpc.client.interceptor.security.BasicAuthenticationInterceptor;

@Configuration(proxyBeanMethods = false)
public class GrpcClientSecurityConfiguration {

    @Bean
    GrpcChannelBuilderCustomizer<?> helloChannelCustomizer() {
        return GrpcChannelBuilderCustomizer.matching("hello",
                (builder) -> builder.intercept(new BasicAuthenticationInterceptor("user", "password")));
    }

}
```

`grpcurl` 把 Basic 放进 metadata（`user:password` 做 Base64）。Health / Reflection 仍可不带：

```bash
grpcurl --plaintext localhost:9090 list
grpcurl --plaintext \
  -H 'authorization: Basic dXNlcjpwYXNzd29yZA==' \
  -d '{"greeting":"John Doe"}' \
  localhost:9090 com.example.HelloService/SayHello
```

不带这行 header 打 `SayHello`，会拿到 `UNAUTHENTICATED`。

### 测试也要过 Security

`@AutoConfigureTestGrpcTransport` 的进程内通道工厂 **不会** 应用 `GrpcChannelBuilderCustomizer`（构造时 customizer 列表是空的）。生产里给 `hello` 通道加的 Basic，测试里加不上。

测试要给 stub 带凭证，用 `@GlobalClientInterceptor`：

```java
package com.example;

import io.grpc.ClientInterceptor;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.grpc.client.GlobalClientInterceptor;
import org.springframework.grpc.client.interceptor.security.BasicAuthenticationInterceptor;

@TestConfiguration(proxyBeanMethods = false)
class TestGrpcBasicAuthConfiguration {

    @Bean
    @GlobalClientInterceptor
    ClientInterceptor testBasicAuth() {
        return new BasicAuthenticationInterceptor("user", "password");
    }

}
```

带凭证的测试 `@Import` 这份配置，调用应成功。另写一个测试 **不要** Import，断言 `UNAUTHENTICATED`：

```java
@SpringBootTest
@AutoConfigureTestGrpcTransport
@ImportGrpcClients(types = HelloServiceGrpc.HelloServiceBlockingStub.class)
class HelloServiceUnauthenticatedTest {

    @Autowired
    HelloServiceGrpc.HelloServiceBlockingStub stub;

    @Test
    void sayHelloRejectedWithoutCredentials() {
        assertThatExceptionOfType(StatusRuntimeException.class)
            .isThrownBy(() -> this.stub.sayHello(HelloRequest.newBuilder().setGreeting("John Doe").build()))
            .satisfies((ex) -> assertThat(ex.getStatus().getCode()).isEqualTo(Status.Code.UNAUTHENTICATED));
    }

}
```

不要为了让测试变绿去关 Security。客户端 `HelloControllerTest` 仍是 `@WebMvcTest` + `@MockitoBean`，不打真 gRPC，也就不经过 Basic。

### Servlet 同端口：走 SecurityFilterChain

gRPC 已经改成和 Tomcat 共用一个端口时（见上一节），按普通 Web 应用写 `SecurityFilterChain` 即可。Spring Boot 会配好 `SecurityContextServerInterceptor`
，让安全上下文进到 gRPC 调用线程。匹配路径可以用 `GrpcRequest`：

```java
package com.example;

import org.springframework.boot.grpc.server.autoconfigure.security.web.servlet.GrpcRequest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration(proxyBeanMethods = false)
public class ServletGrpcSecurityConfiguration {

    @Bean
    SecurityFilterChain grpcSecurityFilterChain(HttpSecurity http) throws Exception {
        http.securityMatcher(GrpcRequest.toAnyService());
        http.authorizeHttpRequests(requests -> requests
                .requestMatchers("/com.example.HelloService/SayHello").hasRole("USER")
                .requestMatchers("/grpc.*/*").permitAll()
                .anyRequest().authenticated());
        http.httpBasic(Customizer.withDefaults());
        return http.build();
    }

}
```

gRPC 和 CSRF 合不来，**gRPC 请求默认关 CSRF**。如果你要自己配 CSRF，设 `spring.grpc.server.security.csrf.enabled=false`
会关掉这个自动行为。Servlet 路径也可以继续在方法上用 `@PreAuthorize`。

### TLS 和 mTLS

传输加密走 Spring Boot 的 SSL bundle，不是另搞一套 gRPC 证书配置。服务端：

```properties
spring.ssl.bundle.jks.grpc.keystore.location=classpath:keystore.jks
spring.ssl.bundle.jks.grpc.keystore.password=secret
spring.grpc.server.ssl.bundle=grpc
```

客户端单向 TLS：

```properties
spring.grpc.client.channel.hello.ssl.enabled=true
```

双向 TLS 时，客户端也指定 bundle：`spring.grpc.client.channel.hello.ssl.bundle=grpc`。服务端要校验证书可以设
`spring.grpc.server.ssl.client-auth=require`。本地自签证书排错，可以临时
`spring.grpc.client.channel.hello.bypass-certificate-validation=true`，不要带进生产。

### OAuth2 Resource Server

classpath 加上 `spring-boot-starter-security` 和 `spring-security-oauth2-resource-server`（JWT 还要能解 JWT，一般再带
jose）。配置和普通 Web 资源服务器一样：

```properties
spring.security.oauth2.resourceserver.jwt.jwk-set-uri=https://auth.example.com/oauth2/jwks
```

Netty 上在 `GrpcSecurity` 里打开：

```java
.oauth2ResourceServer(resourceServer -> resourceServer.jwt(Customizer.withDefaults()))
```

客户端把 access token 塞进 metadata，可用 `BearerTokenAuthenticationInterceptor`。不透明 token 走 introspection，属性和 Web
应用相同。

## 和 1.0 对照

|            | Spring Boot 4.0 + Spring gRPC 1.0                | Spring Boot 4.1（这篇用 4.1.1）                              |
|------------|--------------------------------------------------|-------------------------------------------------------------|
| starter    | `org.springframework.grpc:spring-grpc-*-starter` | `org.springframework.boot:spring-boot-starter-grpc-*`       |
| 默认跑法   | 勾 Web 时常走 Servlet，和 HTTP 共用 8080         | Netty 独立端口 9090                                         |
| 服务注册   | 示例里常见 `@Service`                            | 任意 `BindableService` bean 即可；文档示例用 `@GrpcService` |
| 客户端通道 | `default-channel.address` / `channels.*.address` | `channel.<name>.target`                                     |
| Stub 注册  | 常有自动扫描的习惯                               | 必须写 `@ImportGrpcClients`                                 |
| 测试       | 常绑随机 Web 端口                                | `@AutoConfigureTestGrpcTransport` / `@LocalGrpcServerPort`  |

## 总结

Spring Boot 4 能写 gRPC，但要分清两代。4.0 靠的是独立项目 Spring gRPC 1.0；到了 4.1，自动配置才进 Spring Boot 本身，starter
也换成 `spring-boot-starter-grpc-server` / `grpc-client`。默认是 Netty 听 9090，不再因为勾了 Web 就和 HTTP
挤一个端口。Reflection 和 Health 跟着 starter 走，不用再手加 `grpc-services`。

写服务时，把 `BindableService` 做成 Spring bean 就会挂上，文档示例用 `@GrpcService`。写客户端时，通道走
`spring.grpc.client.channel.<名字>.target`，stub 必须 `@ImportGrpcClients`，4.1 不会再自动扫。测试优先
`@AutoConfigureTestGrpcTransport`，进程里通信，不占 9090。

需要和 Tomcat 共用端口，再改成 `grpc-servlet-jakarta` 并打开 HTTP/2。Micrometer Observation 默认会给 gRPC 打点；日志仍要自己接
OTLP。流处理复杂时，可以接 Salesforce reactive-grpc，用 `Mono` / `Flux` 写，`reactor-grpc-stub` 的版本需要手动指定。GraalVM
Native Image 也能编。安全方面：Netty 用 `GrpcSecurity` 配 HTTP Basic 或 OAuth2，Servlet 同端口用 `SecurityFilterChain` 和
`GrpcRequest`；传输加密走 SSL bundle。

网上不少笔记还停在 1.0 + Servlet 同端口那套。对着 Spring Boot 4.1.1 做的话，先换坐标和属性名，再抄代码。


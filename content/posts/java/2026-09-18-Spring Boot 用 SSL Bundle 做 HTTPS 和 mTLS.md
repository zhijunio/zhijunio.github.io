---
title: "Spring Boot 用 SSL Bundle 做 HTTPS 和 mTLS"
date: 2026-09-18 08:00:00+08:00
slug: spring-boot-ssl-bundle-mtls
category: java
tags: [ "spring-boot", "tls" ]
description: "用 SSL Bundle 为嵌入式 Tomcat 配置 HTTPS 与 mTLS。覆盖 PEM、JKS、RestClient 与基于证书 CN 的 X.509 授权。基于 Spring Boot 4.1.1。"
---

这篇说明如何在 Spring Boot 中使用 SSL Bundle，为嵌入式 Tomcat 配置 HTTPS 与双向 TLS（mTLS）：信任材料采用 PEM 或 JKS，客户端使用 `RestClient`，并在应用层用 X.509 将证书 CN 映射为用户后授权。

<!--more-->

此前配置 HTTPS 时，keystore、truststore 与口令分散在 `server.ssl.*` 下。Spring Boot **3.1** 引入 **SSL Bundle**：为一组信任材料指定名称，嵌入式 Web 服务器、`RestClient`、`WebClient` 均按该名称引用。信任材料可以是 **PEM**（`spring.ssl.bundle.pem.<名称>.*`），也可以是 **JKS**（`spring.ssl.bundle.jks.<名称>.*`）。`jks` 前缀同时支持 JKS 与 PKCS12，切换格式时修改 `keystore.type` / `truststore.type` 即可，引用名称的方式不变。Spring Boot 2.7 起即可将 PEM 直接用于服务器，无需先导入 JKS；3.2 起文件变更后可启用 `reload-on-update`。

下文基于 **Spring Boot 4.1.1**、Java **25**、Maven，Servlet 容器为 Tomcat。步骤参考 Toshiaki Maki 的 [关于在 Spring Boot 中配置 mTLS（相互 TLS）的说明](https://ik.am/entries/816)，配置属性以官方 [SSL](https://docs.spring.io/spring-boot/reference/features/ssl.html) 为准。按文中命令与代码顺序即可复现；文末示例仓库仅供对照，不是阅读前提。

顺序：创建项目 → 先配置 Spring Security，避免默认要求认证 → 签发 PEM → 单向 TLS → mTLS → RestClient 测试 → 将同一套证书导入 JKS。gRPC 服务端使用 `spring.grpc.server.ssl.*`，见 [Spring Boot 4 接入 gRPC](/posts/spring-boot-grpc)。本文只讨论 HTTP。

## 1. 建项目

从 start.spring.io 生成项目。依赖选择如下（页面上的 ID 与生成后的 starter 坐标不完全相同）：

- `web` → `spring-boot-starter-webmvc`（嵌入式 Tomcat + Spring MVC）
- `actuator` → 后续用 `/actuator/health` 验证 TLS
- `security` → 后续配置 X.509
- `configuration-processor` → 可选，用于配置元数据
- `restclient` → Spring Boot 4 中 `RestClientSsl` 位于 `spring-boot-starter-restclient`，不在 webmvc 中。Initializr 勾选后，测试依赖通常包含 `spring-boot-starter-restclient-test`；若 pom 中没有，需自行添加，否则测试无法注入 `RestClientSsl`

命令：

```bash
curl -s https://start.spring.io/starter.tgz \
       -d bootVersion=4.1.1 \
       -d artifactId=spring-boot-ssl-bundle-mtls-samples \
       -d name=spring-boot-ssl-bundle-mtls-samples \
       -d baseDir=spring-boot-ssl-bundle-mtls-samples \
       -d packageName=com.example \
       -d javaVersion=25 \
       -d dependencies=web,actuator,security,configuration-processor,restclient \
       -d type=maven-project \
       -d applicationName=SslBundleMtlsApplication | tar -xzvf -
cd spring-boot-ssl-bundle-mtls-samples
```

确认本机是 Java 25。主类 Initializr 已经生成好了，大致是：

```java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class SslBundleMtlsApplication {

    public static void main(String[] args) {
        SpringApplication.run(SslBundleMtlsApplication.class, args);
    }

}
```

先不要启用 SSL。若已加入 `security` 但尚未自定义 `SecurityFilterChain`，Spring Security 默认要求认证：`curl http://localhost:8080/actuator/health` 通常返回 **401**，启动日志中会出现 `Using generated security password`。Tomcat 已经在监听，只是请求被安全过滤器拒绝。

下一节先编写 Security 与 Controller，再签发证书并启用 HTTPS，避免后续用 curl 验证时仍被默认 401 干扰。

一旦设置 `server.ssl.enabled=true`，应用不再接受 `http://localhost:8080` 上的明文 HTTP，只在所配置端口提供 HTTPS。本文将端口设为 **8443**，因此客户端应访问 `https://localhost:8443/...`。若需 HTTP 与 HTTPS 同时可用，须向 Tomcat 额外添加 Connector，本文不讨论。证书一律通过 `server.ssl.bundle=<名称>` 引用，不要与旧的 `server.ssl.key-store` 同时出现在同一套配置中。PEM 与 JKS 的属性分别在第 4 节和第 7 节给出。

## 2. Security 和 Hello

新建 `src/main/java/com/example/SecurityConfig.java`。

当前尚未启用 TLS。先确定授权规则：`/actuator/health` 允许匿名访问，`/` 需要角色。随后会涉及两层，不宜混淆：TLS 握手阶段，Tomcat（JSSE）只校验客户端证书是否由信任锚（本示例的 CA）签发；Spring Security 的 X.509 再将证书主题中的 CN 作为用户名并按角色授权。这是 Servlet 上的 `SecurityFilterChain`，与 gRPC 的 `GrpcSecurity.preauth` 不是同一套 API。

X.509 属于预认证（Pre-Authentication）：容器已完成证书校验，Security 不再校验口令。`User.withUsername(...)` 仍要求密码字段，填 `{noop}dummy` 即可。从证书主题（Subject）中提取 CN 使用正则：

```java
package com.example;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.SecurityFilterChain;

@Configuration(proxyBeanMethods = false)
public class SecurityConfig {

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                .authorizeHttpRequests((authz) -> authz
                        .requestMatchers("/").hasRole("MTLS")
                        .anyRequest().permitAll())
                .x509((s) -> s.subjectPrincipalRegex("CN=([\\w\\-]+)"))
                .build();
    }

    @Bean
    UserDetailsService userDetailsService() {
        return (username) -> User.withUsername(username).password("{noop}dummy").roles("MTLS").build();
    }

}
```

规则：

- `/` 需要 `ROLE_MTLS`（`hasRole("MTLS")` 会加上 `ROLE_` 前缀）
- 其余路径（含 `/actuator/health`）`permitAll()`：在未启用客户端认证时，不携带客户端证书也可做健康检查。第 5 节将 `client-auth` 设为 `need` 后，缺少客户端证书会在 TLS 握手阶段失败，请求无法到达过滤器链

该 `UserDetailsService` 对正则提取出的任意用户名都授予 `ROLE_MTLS`，仅用于演示。生产环境应只加载已知 CN（数据库或 `InMemoryUserDetailsManager`），未知用户抛出 `UsernameNotFoundException`。

再新建 `src/main/java/com/example/HelloController.java`：

```java
package com.example;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/")
    public String sayHello(@AuthenticationPrincipal UserDetails user) {
        return "Hello " + user.getUsername() + "!";
    }

}
```

先在未启用 TLS 的 HTTP 上确认 Security 已生效：

```bash
./mvnw spring-boot:run
```

另开终端：

```bash
curl http://localhost:8080/actuator/health
```

应返回 `"status":"UP"`。访问 `/` 时若无客户端证书，则没有 X.509 主体，无法获得 `ROLE_MTLS`，响应为 **403 Forbidden**。先停止进程，再签发证书。

## 3. 签发 PEM 证书

证书放在 `src/main/resources/self-signed/`，配置中用 `classpath:self-signed/...` 引用。本节只签发 PEM：CA、服务器证书、客户端证书。JKS 在第 7 节用另一脚本从这些 PEM 导入。

服务器证书除 `CN=localhost` 外，须在 Subject Alternative Name（SAN）中包含 **`DNS:localhost`**。TLS 主机名校验比对的是请求 URL 中的主机名，因此应访问 `https://localhost:...`，使用 `127.0.0.1` 会因与 SAN 不一致而失败。客户端证书的扩展密钥用法（EKU）须包含 `clientAuth`；CN 设为 `demo-client`，后续 X.509 将其作为用户名。

先建目录，将脚本保存为 `scripts/gen-certs-pem.sh`（根据脚本路径解析项目根目录）：

```bash
mkdir -p scripts
```

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/src/main/resources/self-signed"
mkdir -p "$DIR"

openssl req -new -nodes -out "$DIR/ca.csr" -keyout "$DIR/ca.key" -subj "/CN=demo-ca/O=example/C=JP"
chmod og-rwx "$DIR/ca.key"

cat > "$DIR/ext_ca.txt" <<'EOF'
basicConstraints=CA:TRUE
keyUsage=digitalSignature,keyCertSign
EOF
openssl x509 -req -in "$DIR/ca.csr" -days 3650 -signkey "$DIR/ca.key" -out "$DIR/ca.crt" -extfile "$DIR/ext_ca.txt"

cat > "$DIR/ext.txt" <<'EOF'
basicConstraints=CA:FALSE
keyUsage=digitalSignature,dataEncipherment,keyEncipherment,keyAgreement
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=DNS:localhost
EOF

openssl req -new -nodes -out "$DIR/server.csr" -keyout "$DIR/server.key" -subj "/CN=localhost"
chmod og-rwx "$DIR/server.key"
openssl x509 -req -in "$DIR/server.csr" -days 3650 -CA "$DIR/ca.crt" -CAkey "$DIR/ca.key" -CAcreateserial -out "$DIR/server.crt" -extfile "$DIR/ext.txt"

cat > "$DIR/ext_client.txt" <<'EOF'
basicConstraints=CA:FALSE
keyUsage=digitalSignature,dataEncipherment,keyEncipherment,keyAgreement
extendedKeyUsage=clientAuth
EOF

openssl req -new -nodes -out "$DIR/client.csr" -keyout "$DIR/client.key" -subj "/CN=demo-client"
chmod og-rwx "$DIR/client.key"
openssl x509 -req -in "$DIR/client.csr" -days 3650 -CA "$DIR/ca.crt" -CAkey "$DIR/ca.key" -CAcreateserial -out "$DIR/client.crt" -extfile "$DIR/ext_client.txt"
```

然后：

```bash
chmod +x scripts/gen-certs-pem.sh
./scripts/gen-certs-pem.sh
```

执行完成后应生成：`ca.crt` / `ca.key`、`server.crt` / `server.key`、`client.crt` / `client.key`。`-nodes` 表示私钥无口令；若私钥有口令，PEM Bundle 还需配置 `private-key-password`。上述文件仅供本地演示与测试，不得用于生产。若只走 PEM，接下来配置 `tls` / `mtls` 即可。

单向 TLS 只做服务器身份校验：服务器出示证书，客户端用 CA 验证其证书链。mTLS（相互 TLS）要求双方出示证书，服务器用 truststore 中的 CA 校验客户端证书。本端的私钥与证书放入 **keystore**，用于校验对端的证书放入 **truststore**。PEM 与 JKS 职责相同，仅编码与容器格式不同。

## 4. 单向 TLS（PEM）

新建 `src/main/resources/application-tls.properties`：

```properties
server.port=8443
server.ssl.enabled=true
server.ssl.bundle=self-signed
spring.ssl.bundle.pem.self-signed.keystore.certificate=classpath:self-signed/server.crt
spring.ssl.bundle.pem.self-signed.keystore.private-key=classpath:self-signed/server.key
```

上述属性表示：Tomcat 在本机 **8443** 端口接受连接（`server.port=8443`），并启用 HTTPS（`server.ssl.enabled=true`）。访问地址为 `https://localhost:8443/...`，不再是第 2 节的 `http://localhost:8080/...`。`server.ssl.bundle=self-signed` 指定服务器使用的 Bundle，内容位于 `spring.ssl.bundle.pem.self-signed.*`。此处只配置了 keystore（服务器证书与私钥），因此仍是单向 TLS。第 3 节已签发客户端证书，本节尚未使用。不要与旧属性 `server.ssl.key-store` 同时配置。Spring Boot 2.7 起也可用 `server.ssl.certificate` / `certificate-private-key` 直接指定 PEM、不经过 Bundle，本文不采用。

启动并激活 `tls`：

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=tls
```

启动日志中应出现 Tomcat 已在 **8443** 端口提供 HTTPS，例如 `Tomcat started on port 8443 (https)`。客户端使用主机名 `localhost`、端口 `8443`、协议 `https`。另开终端：

```bash
# 跳过证书校验，仅确认 HTTPS 端口可访问
curl -k https://localhost:8443/actuator/health

# 完成证书链校验：将 CA 交给 curl
curl --cacert src/main/resources/self-signed/ca.crt https://localhost:8443/actuator/health
```

两条请求均应返回包含 `"status":"UP"` 的 JSON。`-k` 会关闭主机名校验与证书链校验；要走完整校验，使用第二条。

若写成 `https://127.0.0.1:8443/...`，即使指定 `--cacert`，也常因主机名与 SAN 中的 `DNS:localhost` 不一致而失败。应使用 `localhost`。

## 5. mTLS（PEM）

新建 `src/main/resources/application-mtls.properties`：

```properties
server.ssl.client-auth=need
spring.ssl.bundle.pem.self-signed.truststore.certificate=classpath:self-signed/ca.crt
```

含义：

1. `client-auth=need`：TLS 握手阶段要求客户端出示证书
2. truststore 使用同一 CA：只接受由该 CA 签发的客户端证书

这是传输层校验。证书通过信任锚验证后，请求才会进入 DispatcherServlet；第 2 节的 X.509 再按 CN 授权。握手失败时请求不会进入 Spring Security；**403** 表示请求已进入应用层后被拒绝。

在 Servlet 容器上，`server.ssl.client-auth` 的取值为 **`need`、`want`、`none`**。gRPC 使用 `spring.grpc.server.ssl.client-auth=require`，不能写入 HTTP 的 `server.ssl.client-auth`。

区别：

- `need`：缺少客户端证书时，连接在 **Tomcat / JSSE** 的 TLS 握手中终止，请求无法到达 MVC
- `want`：无客户端证书时连接仍可建立；访问 `/` 会因无角色得到 403；`/actuator/health` 若为 `permitAll()` 仍可能成功

本文使用 `need`。停止上一进程，同时激活两个 profile：

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=tls,mtls
```

`tls` 配置端口 8443、启用 HTTPS、Bundle 名称及服务器证书。`mtls` 追加客户端认证与 truststore。两个 profile 均须激活：缺少 `tls` 则没有 HTTPS 监听与服务器证书；缺少 `mtls` 则仍为单向 TLS。

先不提供客户端证书：

```bash
curl --cacert src/main/resources/self-signed/ca.crt https://localhost:8443/actuator/health
```

应失败。具体报文取决于 JDK 与 curl 使用的 TLS 实现，常见包括 `bad_certificate`、`sslv3 alert`。这表明服务端已在握手中要求客户端证书。

再同时提供 CA、客户端证书与私钥：

```bash
curl --cacert src/main/resources/self-signed/ca.crt \
  --cert src/main/resources/self-signed/client.crt \
  --key src/main/resources/self-signed/client.key \
  https://localhost:8443/actuator/health
```

应返回 `"status":"UP"`。`--cacert` 用于校验服务器证书，`--cert` / `--key` 是客户端证书与私钥。缺少客户端证书会导致握手失败；缺少 CA 则客户端无法校验服务器证书。

再请求根路径，确认 X.509 将 CN 映射为用户名：

```bash
curl --cacert src/main/resources/self-signed/ca.crt \
  --cert src/main/resources/self-signed/client.crt \
  --key src/main/resources/self-signed/client.key \
  https://localhost:8443/
```

应返回 `Hello demo-client!`。

三种失败情形：

1. `need` 且未提供客户端证书：TLS 握手失败，请求无法进入 Spring Security
2. 证书由其他 CA 签发：truststore 校验失败，同样在握手阶段终止
3. `want` 下证书通过 CA 校验，但正则未能提取 CN，或用户不具备 `ROLE_MTLS`：请求已进入应用，`/` 返回 403。本示例的 `UserDetailsService` 会为任意 CN 授予角色；要观察到 403，需收紧该实现，或将 `client-auth` 临时改为 `want` 后不携带客户端证书访问 `/`

## 6. 用 RestClient 作为 HTTPS 客户端（PEM）

curl 的 `--cacert` / `--cert` / `--key` 在 Spring 中对应 SSL Bundle：

| curl | Bundle |
|--|--|
| `--cacert` | truststore |
| `--cert` / `--key` | keystore |

测试中再定义两个 Bundle：

- `client`：客户端证书、私钥与信任的 CA（完整 mTLS 客户端）
- `cacert`：仅信任 CA，不含客户端私钥（用于断言缺少客户端证书时握手失败）

Spring Boot 4 注入 `org.springframework.boot.restclient.autoconfigure.RestClientSsl`，对 `RestClient.Builder` 调用 `apply(clientSsl.fromBundle("名称"))`。测试不要连接手工启动的 8443：`RANDOM_PORT` 会启动独立的 HTTPS 端口，用 `@LocalServerPort` 读取实际端口，再拼成 `https://localhost:` + 端口。主机名仍为 `localhost`，与证书 SAN 一致。每个测试分别 `build()` 一个 `RestClient`，避免互相污染。

把测试类整份写成 `src/test/java/com/example/SslBundleMtlsApplicationTests.java`（覆盖 Initializr 生成的空测试即可）：

```java
package com.example;

import javax.net.ssl.SSLHandshakeException;

import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.restclient.autoconfigure.RestClientSsl;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, properties = {
        "spring.profiles.active=tls,mtls",
        "spring.ssl.bundle.pem.client.keystore.certificate=classpath:self-signed/client.crt",
        "spring.ssl.bundle.pem.client.keystore.private-key=classpath:self-signed/client.key",
        "spring.ssl.bundle.pem.client.truststore.certificate=classpath:self-signed/ca.crt",
        "spring.ssl.bundle.pem.cacert.truststore.certificate=classpath:self-signed/ca.crt"
})
class SslBundleMtlsApplicationTests {

    @LocalServerPort
    int port;

    @Autowired
    RestClient.Builder restClientBuilder;

    @Autowired
    RestClientSsl clientSsl;

    @Test
    void healthCheckWithValidCertificate() {
        RestClient restClient = this.restClientBuilder.baseUrl("https://localhost:" + this.port)
            .apply(this.clientSsl.fromBundle("client"))
            .build();
        ResponseEntity<String> response = restClient.get().uri("/actuator/health").retrieve().toEntity(String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("\"status\":\"UP\"");
    }

    @Test
    void healthCheckWithoutCertificate() {
        RestClient restClient = this.restClientBuilder.baseUrl("https://localhost:" + this.port)
            .apply(this.clientSsl.fromBundle("cacert"))
            .build();
        assertThatExceptionOfType(ResourceAccessException.class)
            .isThrownBy(() -> restClient.get().uri("/actuator/health").retrieve().toEntity(String.class))
            .withCauseInstanceOf(SSLHandshakeException.class);
    }

    @Test
    void hello() {
        RestClient restClient = this.restClientBuilder.baseUrl("https://localhost:" + this.port)
            .apply(this.clientSsl.fromBundle("client"))
            .build();
        ResponseEntity<String> response = restClient.get().uri("/").retrieve().toEntity(String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isEqualTo("Hello demo-client!");
    }

}
```

三个用例分别覆盖：携带客户端证书的健康检查、缺少客户端证书时的握手失败、携带证书访问 `/` 得到 `Hello demo-client!`。

运行测试（此时尚无 JKS 测试类，应只执行这一份）：

```bash
./mvnw test
```

应全部通过。PEM 路径到此结束。若只需 PEM，可在此停止；JKS 见下一节。

## 7. 使用 JKS Bundle

JKS 不再次签发，而是将第 3 节的 PEM 导入密钥库，并使用另一套 profile。Security 与 Controller 无需修改。不要在同一次启动中同时激活 `tls` 与 `tls-jks`，二者都会设置 `server.ssl.bundle`。

导入关系：服务器证书与私钥 → `server.jks`（别名 `localhost`），客户端证书与私钥 → `client.jks`（别名 `demo-client`），CA → `truststore.jks`。缺少 PEM 时脚本退出并提示先执行 `gen-certs-pem.sh`。

将脚本保存为 `scripts/gen-certs-jks.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/src/main/resources/self-signed"

for f in ca.crt server.crt server.key client.crt client.key; do
  if [[ ! -f "$DIR/$f" ]]; then
    echo "缺少 $DIR/$f，请先执行 ./scripts/gen-certs-pem.sh" >&2
    exit 1
  fi
done

PASS=secret

openssl pkcs12 -export -in "$DIR/server.crt" -inkey "$DIR/server.key" \
  -out "$DIR/server.p12" -name localhost -passout pass:"$PASS"
openssl pkcs12 -export -in "$DIR/client.crt" -inkey "$DIR/client.key" \
  -out "$DIR/client.p12" -name demo-client -passout pass:"$PASS"

rm -f "$DIR/server.jks" "$DIR/client.jks" "$DIR/truststore.jks"
keytool -importkeystore -noprompt \
  -srckeystore "$DIR/server.p12" -srcstoretype PKCS12 -srcstorepass "$PASS" \
  -destkeystore "$DIR/server.jks" -deststoretype JKS -deststorepass "$PASS"
keytool -importkeystore -noprompt \
  -srckeystore "$DIR/client.p12" -srcstoretype PKCS12 -srcstorepass "$PASS" \
  -destkeystore "$DIR/client.jks" -deststoretype JKS -deststorepass "$PASS"
keytool -importcert -noprompt -alias ca -file "$DIR/ca.crt" \
  -keystore "$DIR/truststore.jks" -storetype JKS -storepass "$PASS"
```

```bash
chmod +x scripts/gen-certs-jks.sh
./scripts/gen-certs-jks.sh
```

执行完成后应生成 `server.jks`、`client.jks`、`truststore.jks`（以及中间文件 `*.p12`）。演示口令为 `secret`。较新的 JDK 中 `keytool` 会提示 JKS 为专有格式并建议迁移到 PKCS12。SSL Bundle 使用 PKCS12 时，前缀仍为 `spring.ssl.bundle.jks`，将 `type` 设为 `PKCS12`、文件改为 `.p12` 即可。

PEM Bundle 名称为 `self-signed`。JKS 使用 `self-signed-jks`，避免同一名称下同时定义两种存储。`server.ssl.bundle` 只写 Bundle 名称，与信任材料是 PEM 还是 JKS 无关。

属性对照：

| | PEM | JKS |
|--|--|--|
| 前缀 | `spring.ssl.bundle.pem.<名称>` | `spring.ssl.bundle.jks.<名称>` |
| 服务器私钥/证 | `keystore.certificate` + `keystore.private-key` | `keystore.location` + `keystore.password`（可选 `keystore.type`、`key.alias`） |
| 信任锚 | `truststore.certificate` | `truststore.location` + `truststore.password` |
| 绑定到 Tomcat | `server.ssl.bundle=<名称>` | 相同 |

新建 `src/main/resources/application-tls-jks.properties`：

```properties
server.port=8443
server.ssl.enabled=true
server.ssl.bundle=self-signed-jks
spring.ssl.bundle.jks.self-signed-jks.key.alias=localhost
spring.ssl.bundle.jks.self-signed-jks.keystore.location=classpath:self-signed/server.jks
spring.ssl.bundle.jks.self-signed-jks.keystore.password=secret
spring.ssl.bundle.jks.self-signed-jks.keystore.type=JKS
```

`key.alias` 须与导入时的 `-name localhost` 一致。`server.port=8443` 与 PEM 一节相同：Tomcat 在 8443 端口提供 HTTPS。启动单向 TLS：

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=tls-jks
```

curl 仍使用 PEM 格式的 CA——客户端使用的编码不必与服务端密钥库格式相同：

```bash
curl --cacert src/main/resources/self-signed/ca.crt https://localhost:8443/actuator/health
```

应返回 `"status":"UP"`。停止进程后再启用 mTLS。新建 `src/main/resources/application-mtls-jks.properties`：

```properties
server.ssl.client-auth=need
spring.ssl.bundle.jks.self-signed-jks.truststore.location=classpath:self-signed/truststore.jks
spring.ssl.bundle.jks.self-signed-jks.truststore.password=secret
spring.ssl.bundle.jks.self-signed-jks.truststore.type=JKS
```

`client-auth=need` 与 PEM 一节相同，仅将信任锚改为 JKS truststore。

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=tls-jks,mtls-jks
```

未携带客户端证书时应握手失败，与第 5 节相同：

```bash
curl --cacert src/main/resources/self-signed/ca.crt https://localhost:8443/actuator/health
```

再提供 PEM 的 `--cert` / `--key`（客户端编码可与服务端密钥库不同）：

```bash
curl --cacert src/main/resources/self-signed/ca.crt \
  --cert src/main/resources/self-signed/client.crt \
  --key src/main/resources/self-signed/client.key \
  https://localhost:8443/actuator/health

curl --cacert src/main/resources/self-signed/ca.crt \
  --cert src/main/resources/self-signed/client.crt \
  --key src/main/resources/self-signed/client.key \
  https://localhost:8443/
```

健康检查应返回 `"status":"UP"`，根路径应返回 `Hello demo-client!`。

RestClient 同样改用 JKS Bundle。测试类为 `src/test/java/com/example/SslBundleJksApplicationTests.java`，用例与 PEM 相同，仅 profile 与 Bundle 属性不同：

```java
package com.example;

import javax.net.ssl.SSLHandshakeException;

import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.restclient.autoconfigure.RestClientSsl;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, properties = {
        "spring.profiles.active=tls-jks,mtls-jks",
        "spring.ssl.bundle.jks.client.key.alias=demo-client",
        "spring.ssl.bundle.jks.client.keystore.location=classpath:self-signed/client.jks",
        "spring.ssl.bundle.jks.client.keystore.password=secret",
        "spring.ssl.bundle.jks.client.keystore.type=JKS",
        "spring.ssl.bundle.jks.client.truststore.location=classpath:self-signed/truststore.jks",
        "spring.ssl.bundle.jks.client.truststore.password=secret",
        "spring.ssl.bundle.jks.client.truststore.type=JKS",
        "spring.ssl.bundle.jks.cacert.truststore.location=classpath:self-signed/truststore.jks",
        "spring.ssl.bundle.jks.cacert.truststore.password=secret",
        "spring.ssl.bundle.jks.cacert.truststore.type=JKS"
})
class SslBundleJksApplicationTests {

    @LocalServerPort
    int port;

    @Autowired
    RestClient.Builder restClientBuilder;

    @Autowired
    RestClientSsl clientSsl;

    @Test
    void healthCheckWithValidCertificate() {
        RestClient restClient = this.restClientBuilder.baseUrl("https://localhost:" + this.port)
            .apply(this.clientSsl.fromBundle("client"))
            .build();
        ResponseEntity<String> response = restClient.get().uri("/actuator/health").retrieve().toEntity(String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("\"status\":\"UP\"");
    }

    @Test
    void healthCheckWithoutCertificate() {
        RestClient restClient = this.restClientBuilder.baseUrl("https://localhost:" + this.port)
            .apply(this.clientSsl.fromBundle("cacert"))
            .build();
        assertThatExceptionOfType(ResourceAccessException.class)
            .isThrownBy(() -> restClient.get().uri("/actuator/health").retrieve().toEntity(String.class))
            .withCauseInstanceOf(SSLHandshakeException.class);
    }

    @Test
    void hello() {
        RestClient restClient = this.restClientBuilder.baseUrl("https://localhost:" + this.port)
            .apply(this.clientSsl.fromBundle("client"))
            .build();
        ResponseEntity<String> response = restClient.get().uri("/").retrieve().toEntity(String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isEqualTo("Hello demo-client!");
    }

}
```

`fromBundle("client")` / `fromBundle("cacert")` 不变，变化的是这两份 Bundle 的存储格式。再次运行：

```bash
./mvnw test
```

PEM 与 JKS 两套测试均应通过。仅运行 JKS：`./mvnw test -Dtest=SslBundleJksApplicationTests`。

若直接使用 PKCS12、不再转换为 JKS：

```properties
spring.ssl.bundle.jks.self-signed-jks.keystore.location=classpath:self-signed/server.p12
spring.ssl.bundle.jks.self-signed-jks.keystore.password=secret
spring.ssl.bundle.jks.self-signed-jks.keystore.type=PKCS12
spring.ssl.bundle.jks.self-signed-jks.key.alias=localhost
```

前缀仍为 `jks`，不存在 `spring.ssl.bundle.pkcs12`。

## 8. 完成后的文件清单

完成后应包含：

```text
scripts/gen-certs-pem.sh
scripts/gen-certs-jks.sh
src/main/java/com/example/SslBundleMtlsApplication.java
src/main/java/com/example/SecurityConfig.java
src/main/java/com/example/HelloController.java
src/main/resources/application-tls.properties
src/main/resources/application-mtls.properties
src/main/resources/application-tls-jks.properties
src/main/resources/application-mtls-jks.properties
src/main/resources/self-signed/ca.crt
src/main/resources/self-signed/ca.key
src/main/resources/self-signed/server.crt
src/main/resources/self-signed/server.key
src/main/resources/self-signed/client.crt
src/main/resources/self-signed/client.key
src/main/resources/self-signed/server.jks
src/main/resources/self-signed/client.jks
src/main/resources/self-signed/truststore.jks
src/test/java/com/example/SslBundleMtlsApplicationTests.java
src/test/java/com/example/SslBundleJksApplicationTests.java
```

启动后访问 `https://localhost:8443/`。健康检查与根路径均须携带客户端证书。

PEM：

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=tls,mtls
```

JKS：

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=tls-jks,mtls-jks
```

## 9. 和 gRPC 配置的差别

HTTP 使用 `server.ssl.bundle`，客户端认证为 `need` / `want`。gRPC 使用 `spring.grpc.server.ssl.bundle`，上一篇示例为 `require`。授权分别为 `SecurityFilterChain.x509()` 与 `GrpcSecurity.preauth()`。

Bundle 的信任材料可以是 PEM 或 JKS。上一篇 gRPC 示例使用 JKS；本文 PEM 与 JKS 各用一套 profile，Java 代码共用。cert-manager 等流水线通常更适合 PEM；已有 `keytool` 密钥库则使用 JKS 或 PKCS12。

## 10. 上线

文中自签证书仅用于本地演示与 `./mvnw test`。私钥与 keystore 口令不应作为普通源码长期保存；生产环境使用正式 CA 或 cert-manager。Bundle 应指向 `file:` 路径；PEM 使用 **fullchain**（叶子证书与中间证书）。`reload-on-update` 监视的是文件系统上的路径，classpath 中的证书不会热更新。JKS 热更新同样需要将 `location` 设为 `file:`。

`WebClient` 对应 `WebClientSsl.fromBundle`：先定义 Bundle，再将 `fromBundle("名称")` 应用到 builder，本文不展开。

完整工程可对照 [spring-boot-ssl-bundle-mtls-samples](https://github.com/zhijunio/spring-boot-ssl-bundle-mtls-samples)；按本文步骤即可完成，不必先阅读该仓库。

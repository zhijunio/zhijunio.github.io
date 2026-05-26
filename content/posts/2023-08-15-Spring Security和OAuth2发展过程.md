---
title: "Spring Security 与 OAuth2 演进史：三个版本阶段详解"
date: 2023-08-15 08:00:00+08:00
slug: spring-security-oauth2-history
tags: [ "spring-boot", "oauth2" ]
description: "梳理 Spring Security 与 OAuth2 在 Spring 生态中的演进过程，帮助理解相关安全体系的历史脉络与版本变化。"
---

## Spring Security 的发展过程

Spring Security 是一个功能强大且广泛使用的安全框架，为企业级应用程序提供了全面的安全性。Spring Security 最初是 Acegi Security 项目的一部分，于 2004 年发布，现在已经成为 Spring 生态系统的核心组件。 Spring Security 的发展过程可以分为三个阶段：

第一阶段：Spring Security 起源于一个名为 Acegi Security 的开源项目，初期重点实现了 Spring 应用的身份认证和授权服务功能。2003 年，Acegi Security 作为一个孵化项目被捐献给 Spring 社区。2004 年，正式作为 Spring 框架的核心组件之一 Absorbed 进 Spring。并更名为 Spring Security。Spring Security 1.0 版本 Spring Security 1.0 版本发布于 2004 年。它提供了最基本的安全功能，包括身份验证和授权。身份验证是验证用户是否是他们所声称的人的过程。授权是确定用户是否有权访问特定资源的过程。 Spring Security 1.0 版本使用了以下技术来实现身份验证和授权：

- 表单身份验证：表单身份验证是通过用户提交表单来验证用户身份的过程。
- 基于角色的访问控制 (RBAC)：RBAC 是一种授权模型，它将用户分配到角色，然后这些角色被授予对特定资源的访问权限。

第二阶段：Spring Security 2.0 版本 Spring Security 2.0 版本发布于 2006 年。它提供了更多的安全功能，包括加密和会话管理。加密是将数据转换成无法被他人理解的形式的过程。会话管理是跟踪用户会话的状态的过程。 Spring Security 2.0 版本使用了以下技术来实现加密和会话管理：

- 安全套接字层 (SSL)：SSL 是一种加密协议，它可以保护数据在传输过程中不被窃听。
- 会话管理：Spring Security 提供了自己的会话管理实现，它可以跟踪用户会话的状态。

第三阶段：Spring Security 3.0 版本 Spring Security 3.0 版本发布于 2008 年。它是一个重大的版本更新，它提供了许多新的安全功能，包括 OAuth、SAML 和 OpenID。 OAuth 是一种授权框架，它允许第三方应用程序访问用户的资源。SAML 是一种单点登录 (SSO) 协议，它允许用户在一个地方登录，然后访问多个网站。OpenID 是一种开放的身份验证协议，它允许用户使用他们选择的身份提供商来验证他们的身份。 Spring Security 3.0 版本使用了以下技术来实现 OAuth、SAML 和 OpenID：

- OAuth：Spring Security 提供了自己的 OAuth 实现，它可以让你轻松地在你的应用程序中使用 OAuth。

- SAML：Spring Security 提供了自己的 SAML 实现，它可以让你轻松地在你的应用程序中使用 SAML。

- OpenID：Spring Security 提供了自己的 OpenID 实现，它可以让你轻松地在你的应用程序中使用 OpenID。

以下是 Spring Security 的详细的发展过程和版本变化：

1. Acegi Security：Acegi Security 是 Spring Security 的前身，最初由 Ben Alex 创建并于 2004 年发布。Acegi Security 提供了一组基于 Spring 的安全性功能，用于保护 Web 应用程序、Web 服务和基于 Spring 的应用程序。

2. Spring Security 2：Spring Security 2 是 Acegi Security 的继任者，于 2006 年发布。Spring Security 2 提供了一些新的功能和改进，例如对 OpenID、LDAP 和 CAS 的支持，以及更好的集成和配置选项。

3. Spring Security 3：Spring Security 3 于 2009 年发布，是 Spring Security 的一个重大更新。Spring Security 3 提供了更多的安全功能和改进，例如对 RESTful Web 服务的支持、基于注解的安全性、更好的 CSRF 防护、更好的密码存储和认证管理等。

4. Spring Security 4：Spring Security 4 于 2015 年发布，带来了一些新的功能和改进，例如对 OAuth2、JWT 和 Spring Boot 的支持、更好的 SSO 和多因素认证等。

5. Spring Security 5：Spring Security 5 于 2017 年发布，是一个重大的更新，带来了一些新的功能和改进，例如对 WebFlux 和 Reactive Spring 的支持、更好的 OAuth2 和 OpenID Connect 的支持、更好的密码编码和认证管理等。

6. Spring Security 5.1：Spring Security 5.1 发布于 2018 年，主要提供了对 Spring Boot 2.1 的支持和一些新的功能，如 Kotlin DSL、OAuth2 支持的私有证书、JWT 生成器等。

7. Spring Security 5.2：Spring Security 5.2 发布于 2019 年，带来了许多改进和新特性，包括对 Spring Cloud Gateway 和 Spring MVC 的 WebFlux 支持、OAuth2 和 OpenID Connect 的改进、更好的密码管理和认证、更好的跨域资源共享（CORS）支持等。

8. Spring Security 5.3：Spring Security 5.3 发布于 2020 年，主要提供了更好的 WebFlux 和 RSocket 支持、更好的 OAuth2 支持、更好的测试和性能、更好的 Kotlin 支持、更好的 JUnit 5 支持等。

9. Spring Security 5.4：Spring Security 5.4 发布于 2021 年，带来了一些新的功能和改进，例如对 Spring Boot 2.4 的支持、更好的 JWT 和 OAuth2 支持、更好的密码编码、更好的 WebFlux 和 RSocket 支持、更好的测试和性能等。

10. Spring Security 5.5：是当前最新的版本，于 2022 年发布。Spring Security 5.5 带来了一些新的功能和改进，包括对 Spring Framework 6 和 Java 17 的支持、更好的密码编码和认证管理、更好的 OAuth2 和 OpenID Connect 支持、更好的 WebFlux 和 RSocket 支持、更好的测试和性能等。

11. Spring Security 5.7：由于[根据 Spring 官网发布的公告](https://javatechonline.com/spring-security-without-websecurityconfigureradapter/)，WebSecurityConfigurerAdapter 已从 Spring Security 5.7.0-M2 中弃用。

12. Spring Security 6.0：2022 年 11 月发布，WebSecurityConfigurerAdapter 已从 Spring Security API 中完全删除。它还影响了 2022 年 11 月新发布的 [Spring Boot 3.0](https://javatechonline.com/new-features-in-spring-boot-3-and-spring-6/)。

    除了不断改进和增强现有功能之外，Spring Security 还增加了对新的安全威胁的防御和支持，例如 CSRF、XSS、CSP 等。此外，Spring Security 还提供了许多有用的扩展和插件，例如 Spring Security OAuth、Spring Security SAML、Spring Security Kerberos 等，以满足不同的安全需求。

## Spring Security OAuth2 发展

[Spring Security OAuth2](https://github.com/spring-attic/spring-security-oauth) 是一个用于构建安全的 OAuth2-based 网络应用的框架，它是 Spring Security 的一部分。下面是 Spring Security OAuth2 的发展过程：

### 1. Spring Security OAuth2 V1.x – V2.0

最初的几个版本是为了构建一个安全的 OAuth2-based 网络应用。核心的功能包括：

- 支持 OAuth2 协议的四种授权方式：授权码（authorization code）、隐式授权（implicit）、密码授权（resource owner password credentials）和客户端凭据（client credentials）
- 提供了一个简单易用的 API 用于构建 OAuth2 服务器和客户端
- 支持 JWT（JSON Web Tokens）
- 提供了详细的文档和示例代码

### 2. Spring Security OAuth2 V2.1

在 2.1 版本中，Spring Security OAuth2 进行了一系列的改进和扩展，包括：

- 支持 OpenID Connect 1.0
- 支持 Token Introspection Endpoint
- 更好的支持 JWT，包括 JWS（JSON Web Signatures）和 JWE（JSON Web Encryption）

### 3. Spring Security 5.0 OAuth2 Login and OAuth2 Client

在 Spring Security 5.0 中，Spring Security OAuth2 的部分功能被合并到了 Spring Security 5.0 中，提供了 OAuth2 登录和客户端支持。

### 4. Spring Security 5.1 OAuth2 Resource Server

在 Spring Security 5.1 中，Spring Security OAuth2 的资源服务器功能被合并到了 Spring Security 中。

### 5. Spring Security 5.2 OAuth2 Authorization Server

在 Spring Security 5.2 中，Spring Security OAuth2 的授权服务器功能被合并到了 Spring Security 中。这是 Spring Security OAuth2 的最后一个独立版本。

### 6. Spring Authorization Server

在 2020 年 4 月，Spring 宣布了一个新的项目——Spring Authorization Server，该项目旨在提供一个用于实现 OAuth 2.1 授权服务器的基础。

### 7. Spring Security 5.3 and beyond

在 Spring Security 5.3 和之后的版本中，Spring Security OAuth2 的所有功能都被合并到了 Spring Security 中，而 [Spring Security OAuth2](https://github.com/spring-attic/spring-security-oauth) 作为一个独立的项目已经停止开发。与之相对应的 [Spring Security OAuth Boot 2 Autoconfig](https://github.com/spring-attic/spring-security-oauth2-boot) 也停止了开发。

总结一下，目前，Spring Security OAuth2 的最新版本为 2.5.2.RELEASE，并且所有类都标注为 @Deprecated，官方也提供了一个迁移文档 [OAuth 2.0 Migration Guide](https://github.com/spring-projects/spring-security/wiki/OAuth-2.0-Migration-Guide)。

## Spring Boot 和 Spring OAuth2 版本关系

Spring Boot 和 Spring OAuth2 是可以配合使用的，主要注意版本匹配即可。

Spring Boot 使用了特定版本的 Spring OAuth2 作为依赖。所以使用对应的 Spring Boot 版本，就会自动获取匹配的 Spring OAuth2 版本。

举几个版本的例子：

- Spring Boot 1.5.x 使用 Spring OAuth2 2.0.x
- Spring Boot 2.0.x 使用 Spring OAuth2 2.0.x
- Spring Boot 2.1.x 使用 Spring OAuth2 2.1.x
- Spring Boot 2.2.x 使用 Spring OAuth2 2.2.x
- Spring Boot 2.3.x 使用 Spring OAuth2 2.3.x

所以使用 Spring Boot 时，不需要额外指定 Spring OAuth2 的版本，只需要选择匹配的 Spring Boot 版本即可。

在配置和使用 Spring OAuth2 时，只需要参考 Spring OAuth2 的文档即可，不需要特别关注其版本。Spring Boot 会负责管理版本匹配。

此外，从 Spring Boot 1.5 开始，Spring Security 已经集成了 OAuth2 的实现，可以直接使用 Spring Security 来实现 OAuth2，无需引入 Spring OAuth 项目。

总之，Spring Boot 大大简化了 Spring OAuth2 的使用，只需要关注 Spring Boot 版本即可自动获取正确的 Spring OAuth2 版本。

## Spring Cloud 和 Spring OAuth2 版本关系

Spring Cloud 和 Spring OAuth2 版本之间没有固定的对应关系，但通常来说建议符合以下情况：

- Spring Cloud 版本越新，内置的 Spring OAuth 支持也会更稳定和完善。
- Spring Cloud Hoxton/Greenwich 等主流版本，内置的 Spring OAuth 支持正常使用 Spring Security OAuth2 版本 2.x。
- Spring Cloud Edgware 及更早版本，内置的 Spring OAuth 支持建议使用 Spring Security OAuth2 版本 1.x。
- 即使 Spring Cloud 版本和 Spring Security OAuth 版本不完全匹配，也无大碍，但功能和兼容性会受一定影响。

所以一般来说：

- Spring Cloud Finch/ Greenwich 等最新版本，建议使用 Spring Security OAuth2 版本 2.3.x 及以上。
- Spring Cloud Edgware 到 Hoxton，建议使用 Spring Security OAuth2 版本 1.5.x 到 2.3.x 都可以。
- Spring Cloud 版本比较早，如 Dalston 以下，建议使用 Spring Security OAuth2 版本 1.0.x 到 1.5.x。

但不是说版本一定要完全匹配，主要看自己需要用到的 Spring OAuth 功能是否得到支持。选择版本时优先考虑 Spring Cloud 版本的内置支持程度。此外，也可以根据项目其他依赖选择一个相对稳定的 Spring Security OAuth 版本。

## Spring Cloud Security

Spring Cloud Security 提供了一种集成化的方式来实现微服务应用的安全功能。主要有以下几点：

1. 身份认证(Authentication)

Spring Cloud Security 支持常见的认证方式，比如基于 OAuth2.0 的认证协议。可以实现集中式的认证管理，登入后获取访问令牌并在各个微服务之间传递。

1. 授权(Authorization)

支持基于 RBAC 和 ABAC 等授权模型。可以实现集中式的授权管理，给不同用户或组分配不同的访问权限。

1. 安全终端(Security Endpoints)

提供了安全终端的实现，比如/oauth/token 令牌访问端点、/userinfo 用户信息端点等。

1. 加密通信(Encryption)

支持在微服务之间进行安全的 HTTP 通信，通过 TLS/SSL 加密数据传输和服务间调用。

1. 日志审计(Logging & Auditing)

支持收集和记录安全相关的审计日志，比如授权错误日志、登入/登出日志等，方便管理和监控。

1. 安全配置(Security Configuration)

提供了弹性和易用的安全配置能力，如动态配置安全相关 Bean 等。

1. 集成支持(Integration Support)

天然支持 Spring Cloud 和 Springboot 项目，无缝集成从认证到授权的全套安全功能。

所以总体来说，Spring Cloud Security 提供了一种标准化和集成的方式来实现微服务环境下的安全需求。开发人员可以更便捷地利用其丰富的功能。

## 示例

### Spring Security 如何实现 JSON Web Token 的功能？

Spring Security 可以通过如下方式实现 JSON Web Token(JWT)的功能：

1. 导入 spring-security-jwt 依赖。

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-security</artifactId>
</dependency>

<dependency>
  <groupId>org.springframework.security</groupId>
  <artifactId>spring-security-jwt</artifactId>
</dependency>
```

spring-boot-starter-security 版本信息如下：

- spring-boot-starter-parent 版本号：2.7.5
- 依赖的 spring-boot-starter-security 版本号：2.7.5

spring-boot-starter-security 是 Spring Boot 安全功能的启动器依赖，它会自动引入核心安全依赖：

- spring-security-core：Spring Security 的核心模块，提供认证、授权、安全相关的主要接口和组件。
- spring-security-config：提供了 Spring Security 的基础配置能力，包含过滤器链、密码编码器等。
- spring-security-web：提供了 web 安全相关的支持，如过滤器、登录表单、注解等。
- spring-security-crypto：包含密码哈希功能的实现类，用于对密码进行安全的加密存储。

- spring-security-data：包含了支持 JDBC 和 LDAP 等后端数据源的安全组件。

- spring-security-oauth2-client：提供了对 OAuth2 客户端功能的支持。主要提供以下 OAuth2 客户端相关功能：

  - 客户端注册和资源服务器配置：支持为客户端应用配置 clientId、secret 等信息。
  - 客户端凭证获取：支持 BasicAuth 和密码模式获取 client credentials。
  - 访问令牌请求：实现客户端向授权服务器请求访问令牌的功能，支持 password、refresh_token 等 grant 类型。
  - 令牌存储：提供 TokenStore 接口的实现，支持在会话或数据库中存储/获取访问令牌。
  - 资源服务器访问：通过访问令牌来访问受保护的资源，支持从请求头或参数中提取令牌。
  - 刷新令牌：实现使用 refresh_token 来刷新过期的访问令牌功能。
  - 用户授权：提供类似@PreAuthorize 注解来处理用户授权逻辑。
  - 客户端详情：封装 ClientDetails 实现类，包含客户端注册信息。
  - 默认令牌服务：DefaultTokenServices 实现类管理令牌生命周期。
  - 请求工厂：提供 RestTemplate 和 Apache HTTP Components 等请求客户端。

  spring-security-oauth2-client 模块同时也提供部分支持其他授权类型：

  - 授权码模式(authorization_code)：主流模式，客户端通过 auth code 获取 access token。
  - 密码模式(password)：客户端直接提供用户名密码获取 token，适合 trusted 客户端。
  - 隐藏式授权模式(implicit)：客户端直接获取 access token，不支持 refresh。
  - 客户端模式(client_credentials)：客户端以自身名义请求资源服务，适合机密客户端。
  - 资主授权模式(owner)：类似密码模式但用户需确认通过用户界面。
  - 运行时审批模式(approval_prompt)：用户每次访问都需确认授权。

  除了上述常见授权类型外，spring-security-oauth2-client 还提供了对以下模式的选择性支持：

  - 断路器模式(urn:ietf:params:oauth:grant-type:device_code)
  - 分阶段授权模式(urn:ietf:params:oauth:grant-type:stage)
  - 令牌交换模式(urn:ietf:params:oauth:grant-type:token-exchange)

- spring-security-oauth2-core：OAuth2 协议支持的核心部件。

因此 spring-boot-starter-security 的版本始终保持与 spring-boot-starters 版本一致。

当前较为主流和稳定的 spring-boot 版本有：

- Spring Boot 2.7.x 最新版
- Spring Boot 2.6.x
- Spring Boot 2.5.x

对应的 spring-boot-starter-security 版本如下：

- Spring Boot 2.7.x - spring-boot-starter-security 2.7.x
- Spring Boot 2.6.x - spring-boot-starter-security 2.6.x
- Spring Boot 2.5.x - spring-boot-starter-security 2.5.x

所以在选择 spring boot 版本时，直接依赖 spring-boot-starter-security 而不用单独指定版本，就可以保证安全功能的版本一致性。

目前大多数场景下可以使用 Spring Boot 2.6.x 或者 2.7.x 作为选择，它们内置的 spring-boot-starter-security 版本都很成熟。

1. 配置 JwtToken enhancer 来生成 JWT 令牌。

```java
@Bean
public JwtAccessTokenConverter jwtTokenEnhancer() {
  JwtAccessTokenConverter converter = new JwtAccessTokenConverter();
  converter.setSigningKey("123456");
  return converter;
}
```

1. 定义 JwtTokenStore 来保存 JWT 令牌。

```java
@Bean
public TokenStore tokenStore() {
  return new JwtTokenStore(jwtTokenEnhancer());
}
```

1. 在 AuthorizationServerConfigurerAdapter 配置类中设置 tokenStore。

```java
@Override
public void configure(AuthorizationServerEndpointsConfigurer endpoints) {
  endpoints.tokenStore(tokenStore());
}
```

1. 客户端使用 JWT 令牌进行认证访问资源服务器。

2. 资源服务器使用 JwtTokenStore 和 JwtAccessTokenConverter 校验 JWT 令牌的合法性。

3. 解析 JWTpayload 获取用户信息，实现鉴权决策。

```java
String username =  ((Jwt)authentication.getPrincipal()).getSubject();
```

完整代码，配置类：

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

  @Bean
  public JwtAccessTokenConverter accessTokenConverter() {
    JwtAccessTokenConverter converter = new JwtAccessTokenConverter();
    converter.setSigningKey("as123456dfsdf");
    return converter;
  }

  @Bean
  public TokenStore tokenStore() {
    return new JwtTokenStore(accessTokenConverter());
  }

  @Override
  protected void configure(HttpSecurity http) throws Exception {
    http.csrf().disable();
    http
      .authorizeRequests()
      .antMatchers("/oauth/**").permitAll();
  }

  @Bean
  @Primary
  public DefaultTokenServices tokenServices() {
    DefaultTokenServices defaultTokenServices = new DefaultTokenServices();
    defaultTokenServices.setTokenStore(tokenStore());
    defaultTokenServices.setSupportRefreshToken(true);
    return defaultTokenServices;
  }

}
```

授权服务器配置，使用客户端模式配置：

```java
@Configuration
public class AuthorizationServerConfig extends AuthorizationServerConfigurerAdapter {

  @Autowired
  private TokenStore tokenStore;

  @Override
  public void configure(ClientDetailsServiceConfigurer clients) throws Exception {

    clients.inMemory()
        .withClient("clientapp")
        .secret("$2a$10$6aQQyhlhol4M1KAncczPdu4zX7/TgvjpOU.sWzt7j5Xl6W/z5V4cC")
        .authorizedGrantTypes("password"， "refresh_token")
        .scopes("read"， "write")
        .accessTokenValiditySeconds(3600);
  }

  @Override
  public void configure(AuthorizationServerEndpointsConfigurer endpoints)
      throws Exception {
    endpoints.tokenStore(tokenStore)
        .authenticationManager(authenticationManager());
  }
}
```

主要配置：

1. 使用 ClientDetailsServiceConfigurer 配置客户端信息，如 clientId、secret 等
2. 配置 tokenStore
3. 配置 authenticationManager 来获取用户信息

这样就实现了基于客户端模式下的授权服务配置，客户端可以使用 clientId/secret 获取访问令牌而无需用户登录。

客户端访问示例：

```bash
curl -X POST http://localhost:8080/oauth/token -d "grant_type=password&username=user&password=password&client_id=clientapp&client_secret=secret"
```

让客户端在后台获取访问令牌，资源服务再使用令牌验证授权。

---
title: "Spring Security 7 MFA 实战：从认证因子到受保护接口"
date: 2026-10-27 14:10:00+08:00
slug: spring-security-7-mfa-tutorial
category: java
tags: ["spring-security", "security"]
description: "结合 Spring Security 7 MFA 示例，拆解主认证、第二因子、因子授权和近期重新验证，并用接口规则串起完整认证流程。"
---

多因素认证（MFA）不只是登录后再弹一个验证码。应用需要知道用户完成了哪些认证因子，再根据资源的敏感程度决定是否放行。Spring Security 7 为 Servlet 应用提供了认证因子（factor）模型，让应用可以把这些状态纳入授权判断。

本文以 [spring-security-7-mfa-demo](https://github.com/zhijunio/spring-security-7-mfa-demo) 为例，说明如何组合 Spring Security 7 的因子能力与应用自己的验证流程。示例使用 Spring Boot 4.1.2、Spring Security 7、Java 25，认证和因子状态保存在内存中，适合本地学习，不是生产配置。

<!--more-->

## MFA 在 Spring Security 中如何表达

一次完整的 MFA 登录可以拆成两步：先完成主认证，再证明持有另一个因子。主认证可能是密码或 Passkey，第二因子则可能是 TOTP、邮件验证码或签名挑战。完成某一步后，认证对象会带有对应的 authority；授权规则据此判断当前请求能否访问资源。

Spring Security 提供 `FactorGrantedAuthority`，其中包含密码和 WebAuthn 等标准因子标识。对于应用自定义的因子，应用验证凭证后也可以把自己的 authority 放进当前认证对象。官方文档介绍了 [MFA 因子与授权集成](https://docs.spring.io/spring-security/reference/servlet/authentication/mfa.html)。

这里有个容易误解的地方：`@EnableMultiFactorAuthentication` 用于启用 MFA 支持，但注解中的 `authorities` 才表达默认需要的因子集合。示例项目使用 `authorities = {}`，表示不在全局默认策略中强制某一组因子；它随后通过接口授权规则明确区分“已完成主认证”“已完成第二因子”和“近期重新验证”。这让不同接口可以有不同门槛。

## 示例的认证流程

示例支持密码或 Passkey 作为主认证，再使用 TOTP、开发用途的邮件验证码、EIP-191 钱包签名或项目自定义的 BIP-39 短语完成第二步。Passkey 在此处是主认证方式；完成 Passkey 登录后，仍然要通过第二因子。

```text
密码 / Passkey
       │
       ▼
主认证 authority
       │
       ├── 请求 MFA challenge（部分因子需要）
       ├── 提交证明并由服务端验证
       ▼
第二因子 authority + 服务端会话状态
       │
       ├── 访问普通受保护接口
       └── 近期 MFA 后管理因子或注册 Passkey
```

浏览器和请求体不能自行声明“MFA 已完成”。第二因子的 authority 只在服务端验证凭证成功之后添加到认证对象中。

## 启用 MFA 支持并配置授权边界

项目的 `SecurityConfig` 中关键部分如下。为突出授权边界，省略了表单登录、WebAuthn、异常处理等配置：

```java
@Configuration
@EnableMultiFactorAuthentication(authorities = {})
class SecurityConfig {
    @Bean
    SecurityFilterChain filterChain(HttpSecurity http, MfaService mfa) throws Exception {
        return http.authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/mfa/**", "/webauthn/register/**")
                    .access((authentication, context) ->
                        new AuthorizationDecision(
                            mfa.recent(context.getRequest(), authentication.get())))
                .requestMatchers("/api/auth/mfa/**")
                    .access((authentication, context) ->
                        new AuthorizationDecision(mfa.hasPrimary(authentication.get())))
                .anyRequest()
                    .access((authentication, context) ->
                        new AuthorizationDecision(mfa.complete(authentication.get()))))
            .build();
    }
}
```

规则体现了三个阶段：

- `/api/auth/mfa/**` 只要求主认证已完成，因为用户需要先登录才能提交第二因子。
- 普通受保护资源要求 `mfa.complete(...)` 为真，即存在主认证因子，并且存在项目认可的第二因子 authority。
- 因子管理和 Passkey 注册要求近期完成过 MFA，避免一个长期有效的登录会话直接修改认证凭证。

示例使用自定义 `AuthorizationManager` lambda 调用 `MfaService`。实际项目可以按自身策略选用 Spring Security 的授权管理器或表达式；关键是把资源的门槛显式写清楚。不要因为加了注解，就假设所有请求都会自动要求两种因子。

## 验证成功后更新认证对象

示例把第二因子验证与认证状态更新分开处理。验证器先检查验证码、签名或其他凭证；验证成功后再调用类似下面的方法，将因子 authority 加入新的认证对象，并保存安全上下文：

```java
void markFactorVerified(Authentication current, String factor,
                        HttpServletRequest request, HttpServletResponse response) {
    var authorities = new ArrayList<GrantedAuthority>(current.getAuthorities());
    authorities.add(new SimpleGrantedAuthority(factor));

    var updated = new UsernamePasswordAuthenticationToken(
        current.getPrincipal(), null, authorities);
    var context = SecurityContextHolder.createEmptyContext();
    context.setAuthentication(updated);
    SecurityContextHolder.setContext(context);

    request.changeSessionId();
    request.getSession().setAttribute("MFA_VERIFIED_AT", Instant.now());
    request.getSession().setAttribute("MFA_VERIFIED_SUBJECT", current.getName());
    securityContextRepository.saveContext(context, request, response);
}
```

示例中实际时间由注入的 `Clock` 提供，方便测试。登录后权限变化时显式保存 `SecurityContext`，使新认证状态进入服务端会话；同时更换 session id，减少认证状态升级时的会话固定风险。

`factor` 应来自服务端代码中允许的因子类型，不能直接相信客户端传入的任意 authority。每种因子都要先完成自己的验证：TOTP 要检查时间窗口与重复使用；邮件验证码要检查过期时间、失败次数和一次性消费；钱包签名需要将签名恢复出的地址与服务端保存的地址比较，并绑定一次性 challenge。项目实现了这些本地演示逻辑，具体细节可看 [`MfaService`](https://github.com/zhijunio/spring-security-7-mfa-demo/blob/main/src/main/java/com/example/springsecuritymfa/auth/MfaService.java)。

## 对敏感操作要求近期 MFA

“登录过 MFA”与“最近刚完成 MFA”代表不同强度的会话状态。示例在会话中保存验证时间和用户标识，并将近期验证窗口设为五分钟：

```java
boolean recent(HttpServletRequest request, Authentication authentication) {
    HttpSession session = request.getSession(false);
    if (session == null || authentication == null || !complete(authentication)) {
        return false;
    }

    Object verifiedAt = session.getAttribute("MFA_VERIFIED_AT");
    Object subject = session.getAttribute("MFA_VERIFIED_SUBJECT");
    return authentication.getName().equals(subject)
        && verifiedAt instanceof Instant time
        && !Duration.between(time, clock.instant()).isNegative()
        && Duration.between(time, clock.instant()).compareTo(Duration.ofMinutes(5)) < 0;
}
```

这样，读取安全状态、添加或删除因子、注册 Passkey 等操作都可以要求近期 MFA。绑定 subject 也能避免只凭会话中的时间戳就认定当前用户通过了 step-up 验证。

生产系统还需要明确近期认证的失效与更新规则，例如登出、切换用户、修改密码或撤销因子后如何清理状态。不要把这段示例逻辑直接当成通用策略。

## 运行并观察授权结果

克隆仓库后，使用 JDK 25 运行：

```bash
./mvnw spring-boot:run
```

打开 `http://localhost:8080/`，使用演示账号 `demo` / `changeit` 登录。调用写接口前先请求 `GET /api/csrf`，后续请求带上返回的 CSRF header 和同一个会话 cookie。所有账号与因子数据都在内存中，应用重启后会清空。

可以观察 `GET /api/me` 在主认证完成但第二因子尚未验证时无法访问；完成第二因子后才满足授权条件。因子管理接口则还要求最近五分钟内完成过 MFA。仓库的集成测试覆盖了主认证后访问被拒绝、完成第二因子后访问成功，以及近期 MFA 的敏感接口边界。

## 实现时要留意的边界

1. **框架负责因子表达和授权连接，应用负责因子生命周期。** Spring Security 不会替应用发送邮件、创建 TOTP 秘钥或验证钱包签名；这些流程仍需由应用实现。
2. **第二因子必须在服务端验证。** 不要从请求参数、JWT 任意声明或前端状态直接恢复 MFA authority。
3. **认证强度不等于“两个步骤”。** 示例允许的不同方式未必属于不同因子类别，也没有判断 Passkey 是否执行了用户验证，因此不能据此声称满足特定合规认证保证等级。
4. **保持 CSRF 与会话安全。** 示例是基于服务端 session 的浏览器应用，CSRF 仍然启用；改变认证级别后保存上下文并轮换 session id。
5. **示例存储不适合线上。** 生产环境需持久化且访问受控的账户与凭证存储、加密保存 TOTP 秘钥、真实邮件服务、限流与审计、HTTPS 和安全 Cookie、正确的 WebAuthn RP ID/origin，以及因子撤销、恢复和轮换流程。钱包 challenge 和 Passkey 部署参数也必须按正式域名与安全策略配置。

## 小结

Spring Security 7 的 MFA 支持提供了统一的因子 authority 表达方式，让认证结果可以进入常规授权判断。落地时要把三件事分别做好：验证因子凭证、仅在服务端验证成功后更新认证状态、按资源敏感度配置授权门槛。示例项目展示了这条路径，也保留了近期 MFA、CSRF 和 session 边界，适合用来阅读与本地实验。

- [示例项目](https://github.com/zhijunio/spring-security-7-mfa-demo)
- [Spring Security 官方 MFA 文档](https://docs.spring.io/spring-security/reference/servlet/authentication/mfa.html)
- [`@EnableMultiFactorAuthentication` API 文档](https://docs.spring.io/spring-security/reference/api/java/org/springframework/security/config/annotation/authorization/EnableMultiFactorAuthentication.html)

---
title: "ThingsBoard 安全模块详解：配置与权限设计"
date: 2024-12-03 09:00:00+08:00
slug: security-in-thingsboard
categories: [ "tech" ]
tags: [ "security", "thingsboard" ]
description: "结合 ThingsBoard 源码与后台界面，整理平台中的安全相关配置、菜单项和核心 Security 模块，帮助理解其安全设计。"
---

ThingsBoard 源码地址：[https://github.com/thingsboard/thingsboard](https://github.com/thingsboard/thingsboard)，启动成功之后，使用系统管理员： <sysadmin@thingsboard.org> / sysadmin 进行登陆。

<!--more-->

## 设置和安全

登陆系统之后，点击左边的设置和安全菜单，进行相应的配置。

1. 设置 -> 基本设置、发送邮件、通知

2. 安全 -> 基本设置 -> 基本策略、密码策略、JWT 安全设置

3. 安全 -> 双因素认证 -> 验证 APP、电子邮件、备份验证码、验证限制、验证码检查速率限制

4. 安全 -> OAuth 2.0 -> 添加OAuth2.0客户端

   系统内置支持以下几种客户端。

   - Apple:
     - 访问令牌：[https://appleid.apple.com/auth/token](https://appleid.apple.com/auth/token)
     - 授权：[https://appleid.apple.com/auth/authorize?response_mode=form_post](https://appleid.apple.com/auth/authorize?response_mode=form_post)
     - JSON Web 地址：[https://appleid.apple.com/auth/keys](https://appleid.apple.com/auth/keys)
     - 用户信息：
     - 范围：openid、name、email
     - 用户名属性：email
     - 电子邮件属性：email
     - 映射器类型：APPLE
     - First Name 名称属性：firstName
     - Last Name 名称属性：lastName
     - 租户名称策略：DOMAIN

   - [Google](https://console.cloud.google.com/):
     - 访问令牌：[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)
     - 授权：[https://accounts.google.com/o/oauth2/v2/auth](https://accounts.google.com/o/oauth2/v2/auth)
     - JSON Web 地址：[https://www.googleapis.com/oauth2/v3/certs](https://www.googleapis.com/oauth2/v3/certs)
     - 用户信息：[https://openidconnect.googleapis.com/v1/userinfo](https://openidconnect.googleapis.com/v1/userinfo)
     - 范围：openid、profile、email
     - 用户名属性：email
     - 电子邮件属性：email
     - 映射器类型：BASIC
     - First Name 名称属性：given_name
     - Last Name 名称属性：family_name
     - 租户名称策略：DOMAIN
   - Facebook:
     - 访问令牌：[https://graph.facebook.com/v2.8/oauth/access_token](https://graph.facebook.com/v2.8/oauth/access_token)
     - 授权：[https://www.facebook.com/v2.8/dialog/oauth](https://www.facebook.com/v2.8/dialog/oauth)
     - JSON Web 地址：
     - 用户信息：[https://graph.facebook.com/me?fields=id,name,first_name,last_name,email](https://graph.facebook.com/me?fields=id,name,first_name,last_name,email)
     - 范围：public_profile、email
     - 用户名属性：email
     - 电子邮件属性：email
     - 映射器类型：BASIC
     - First Name 名称属性：first_name
     - Last Name 名称属性：last_name
     - 租户名称策略：DOMAIN

   - [Github](https://github.com/settings/developers):
     - 访问令牌：[https://github.com/login/oauth/access_token](https://github.com/login/oauth/access_token)
     - 授权：[https://github.com/login/oauth/authorize](https://github.com/login/oauth/authorize)
     - JSON Web 地址：
     - 用户信息：[https://api.github.com/user](https://api.github.com/user)
     - 范围：read:user、user:email
     - 用户名属性：login
     - 电子邮件属性：
     - 映射器类型：GITHUB
     - First Name 名称属性：name
     - Last Name 名称属性：
     - 租户名称策略：DOMAIN

​ 以 Google 为例，需要在 API 和服务 -> 凭据 -> OAuth 2.0 客户端 ID ，在 已获授权的重定向 URI 处添加 thingsboard 的重定向地址：[http://localhost:8080/login/oauth2/code/](http://localhost:8080/login/oauth2/code/)。

完成配置之后，配置的内存保证到数据库中，系统设置对应数据库表是 `admin_settings`。

```sql
CREATE TABLE "public"."admin_settings" (
    "id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "created_time" int8 NOT NULL,
    "json_value" varchar,
    "key" varchar(255),
    PRIMARY KEY ("id")
);
```

表中记录：

```json
[
  {
    "id": "2fa02d60-b119-11ef-8167-dfb7a1b13a5a",
    "tenant_id": "13814000-1dd2-11b2-8080-808080808080",
    "created_time": 1733190720310,
    "json_value": "{\"baseUrl\":\"http://localhost:8080\",\"prohibitDifferentUrl\":false}",
    "key": "general"
  },
  {
    "id": "2fa29e60-b119-11ef-8167-dfb7a1b13a5a",
    "tenant_id": "13814000-1dd2-11b2-8080-808080808080",
    "created_time": 1733190720326,
    "json_value": "{\"coap\":{\"enabled\":true,\"host\":\"\",\"port\":\"5683\"},\"mqtt\":{\"enabled\":true,\"host\":\"\",\"port\":\"1883\"},\"http\":{\"enabled\":true,\"host\":\"\",\"port\":\"8080\"},\"mqtts\":{\"enabled\":false,\"host\":\"\",\"port\":\"8883\"},\"https\":{\"enabled\":false,\"host\":\"\",\"port\":\"443\"},\"coaps\":{\"enabled\":false,\"host\":\"\",\"port\":\"5684\"}}",
    "key": "connectivity"
  },
  {
    "id": "2fa18cf0-b119-11ef-8167-dfb7a1b13a5a",
    "tenant_id": "13814000-1dd2-11b2-8080-808080808080",
    "created_time": 1733190720319,
    "json_value": "{\"mailFrom\":\"xxx\",\"smtpProtocol\":\"smtps\",\"smtpHost\":\"smtp.feishu.cn\",\"smtpPort\":\"465\",\"timeout\":\"10000\",\"enableTls\":false,\"username\":\"xxx\",\"tlsVersion\":null,\"enableProxy\":false,\"providerId\":\"CUSTOM\",\"proxyHost\":\"\",\"proxyPort\":null,\"proxyUser\":\"\",\"proxyPassword\":\"\",\"enableOauth2\":false,\"clientId\":\"\",\"clientSecret\":\"\",\"providerTenantId\":\"\",\"authUri\":\"\",\"tokenUri\":\"\",\"scope\":[],\"redirectUri\":\"\",\"password\":\"wQ7ae64vj2mXUBFZ\"}",
    "key": "mail"
  },
  {
    "id": "7c8790e0-b11a-11ef-983d-d79399efbf69",
    "tenant_id": "13814000-1dd2-11b2-8080-808080808080",
    "created_time": 1733191278830,
    "json_value": "{\"passwordPolicy\":{\"minimumLength\":6,\"maximumLength\":72,\"minimumUppercaseLetters\":null,\"minimumLowercaseLetters\":null,\"minimumDigits\":null,\"minimumSpecialCharacters\":null,\"allowWhitespaces\":true,\"forceUserToResetPasswordIfNotValid\":false,\"passwordExpirationPeriodDays\":null,\"passwordReuseFrequencyDays\":null},\"maxFailedLoginAttempts\":5,\"userLockoutNotificationEmail\":null,\"mobileSecretKeyLength\":64,\"userActivationTokenTtl\":24,\"passwordResetTokenTtl\":24}",
    "key": "securitySettings"
  },
  {
    "id": "3d865ba0-b120-11ef-983d-d79399efbf69",
    "tenant_id": "13814000-1dd2-11b2-8080-808080808080",
    "created_time": 1733193750106,
    "json_value": "{\"providers\":[{\"providerType\":\"TOTP\",\"issuerName\":\"ThingsBoard\"},{\"providerType\":\"EMAIL\",\"verificationCodeLifetime\":120},{\"providerType\":\"BACKUP_CODE\",\"codesQuantity\":10}],\"minVerificationCodeSendPeriod\":30,\"verificationCodeCheckRateLimit\":\"3:900\",\"maxVerificationFailuresBeforeUserLockout\":30,\"totalAllowedTimeForVerification\":3600}",
    "key": "twoFaSettings"
  },
  {
    "id": "2fa47320-b119-11ef-8167-dfb7a1b13a5a",
    "tenant_id": "13814000-1dd2-11b2-8080-808080808080",
    "created_time": 1733190720338,
    "json_value": "{\"tokenExpirationTime\":9000,\"refreshTokenExpTime\":604800,\"tokenIssuer\":\"thingsboard.io\",\"tokenSigningKey\":\"anZjUDM5RXRHUEg2WHhNaEo0dE5pMzhiS0x2TURrMktCMkJYSDg0dUtPQ3k3ZzhnVW9yMHZpUjdUNzFYWWplOA==\"}",
    "key": "jwt"
  }
]
```

OAuth2 相关的表为：

- `domain`
- `domain_oauth2_client`

- `oauth2_client`
- `oauth2_client_registration_template`

## 账号

点击右上角三个竖点的账号按钮，进入个人账号设置页面，可以设置属性、安全和通知设置。

双因素认证可以使用以下身份验证：

- 验证 APP。使用手机上的 Google Authenticator、Authy或Duo等应用程序进行身份验证，它将生成用于登录的验证码。
- 电子邮件。使用您电子邮件中的验证码进行身份验证。
- 备份验证码。这些可打印的一次性密码允许您在离开手机时登录，比如正在旅行。

个人账号的相关设置保存在以下两张表：

- `user_auth_settings`
- `user_settings`

## 登陆页面

开启 OAuht2 之后，注销登陆，进入登陆页面。当前登陆页面会通过 [http://localhost:8080/api/noauth/oauth2Clients?platform=WEB](http://localhost:8080/api/noauth/oauth2Clients?platform=WEB) POST 接口（对应的 Controller 类为 `OAuth2Controller`）查询开通的 OAuth2 客户端列表。返回内容如下：

```json
[
    {
        "name": "Google",
        "icon": "google-logo",
        "url": "/oauth2/authorization/f02246b0-b121-11ef-983d-d79399efbf69"
    }
]
```

f02246b0-b121-11ef-983d-d79399efbf69 为 `oauth2_client` 主键。

在登陆页面，点击使用 Google 登陆，后台在 `OAuth2AuthorizationRequestRedirectFilter` 的 `doFilterInternal` 方法打个断点。

```java
 try {
   OAuth2AuthorizationRequest authorizationRequest = this.authorizationRequestResolver.resolve(request);
   if (authorizationRequest != null) {
    this.sendRedirectForAuthorization(request, response, authorizationRequest);
    return;
   }
  }
  catch (Exception ex) {
   this.unsuccessfulRedirectForAuthorization(request, response, ex);
   return;
  }
```

`this.authorizationRequestResolver` 对于的 Bean 为 `CustomOAuth2AuthorizationRequestResolver`，其 `resolve` 方法逻辑如下：

```java
@Override
public OAuth2AuthorizationRequest resolve(HttpServletRequest request) {
    String registrationId = this.resolveRegistrationId(request);
    String redirectUriAction = getAction(request, "login");
    String appPackage = getAppPackage(request);
    String platform = getPlatform(request);
    String appToken = getAppToken(request);
    return resolve(request, registrationId, redirectUriAction, appPackage, platform, appToken);
}
```

- 首先获取 `registrationId`，即 f02246b0-b121-11ef-983d-d79399efbf69
- 获取 `redirectUriAction`，即 login
- 获取 `appPackage`，为 null
- 获取 `platform`，为 null
- 获取 `appToken`，为 null

- 通过 `this.clientRegistrationRepository` 的 `findByRegistrationId` 方法 查询 `ClientRegistration`

- 如果 `ClientRegistration` 的授权类型为 `authorization_code`

  - 如果 `scope` 包含 `OPENID`，则添加 `nonce` 参数
  - 如果 `clientAuthenticationMethod` 为 `none`，则添加 `pkce` 参数

- 获取重定向地址，这里为 [http://localhost:8080/login/oauth2/code/](http://localhost:8080/login/oauth2/code/)

- 构建 `OAuth2AuthorizationRequest` 对象

  ```json
  {
   "authorizationUri": "https://accounts.google.com/o/oauth2/v2/auth",
   "responseType": {
    "value": "code"
   },
   "clientId": "385465491380-8q1fk7r47tqu6mcc9klob2c1a9sl4jmd.apps.googleusercontent.com",
   "redirectUri": "http://localhost:8080/login/oauth2/code/",
   "scopes": ["email", "openid", "profile"],
   "state": "M0qcUWqzNMKfj7zHKmmvFaaZxISMS5GGDHDZv55acHE=",
   "additionalParameters": {
    "nonce": "zz5r7lMyPdaJ1zvAaRZvzH1P_megtjC28nVFG1Dug00"
   },
   "authorizationRequestUri": "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=385465491380-8q1fk7r47tqu6mcc9klob2c1a9sl4jmd.apps.googleusercontent.com&scope=email%20openid%20profile&state=M0qcUWqzNMKfj7zHKmmvFaaZxISMS5GGDHDZv55acHE%3D&redirect_uri=http://localhost:8080/login/oauth2/code/&nonce=zz5r7lMyPdaJ1zvAaRZvzH1P_megtjC28nVFG1Dug00",
   "attributes": {
    "registration_id": "f02246b0-b121-11ef-983d-d79399efbf69",
    "nonce": "_toJxm0yUite6Kzjy_yfX4eKq4NtwmygCqgYJVjN83SV2q6sZtneWpBmWeNTN6ZMth8qCIyOWY1up-m_AKmcQmjf_j9HCheruxtNvQL1zTbL9dL-rwOSSonAUtAJ3BGH"
   },
   "grantType": {
    "value": "authorization_code"
   }
  }
  ```

- 重定向到 google 的 OAuth2 登陆页面。

## OAuth2 Client 配置

OAuth2 Client 相关配置在 `ThingsboardSecurityConfiguration` 类

```java
@Bean
  SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
      /...
      if (oauth2Configuration != null) {
          http.oauth2Login(login -> login
                  .authorizationEndpoint(config -> config
                          .authorizationRequestRepository(httpCookieOAuth2AuthorizationRequestRepository)
                          .authorizationRequestResolver(oAuth2AuthorizationRequestResolver))
                  .loginPage("/oauth2Login")
                  .loginProcessingUrl(oauth2Configuration.getLoginProcessingUrl())
                  .successHandler(oauth2AuthenticationSuccessHandler)
                  .failureHandler(oauth2AuthenticationFailureHandler));
      }
      return http.build();
  }
```

oauth2Login 的 `authorizationEndpoint` 配置了一个 `authorizationRequestRepository` 和 `authorizationRequestResolver`。

`authorizationRequestRepository` 对应的是 `HttpCookieOAuth2AuthorizationRequestRepository`，保存 request 请求地址到 cookie；authorizationRequestResolver 对应的是 `CustomOAuth2AuthorizationRequestResolver`。

oauth2Login 的登陆页面为 `/oauth2Login`，处理登陆请求的地址为 `oauth2Configuration.getLoginProcessingUrl()`，oauth2Configuration 的配置：

```yaml
security:
  oauth2:
    # Redirect URL where access code from external user management system will be processed
    loginProcessingUrl: "${SECURITY_OAUTH2_LOGIN_PROCESSING_URL://login/oauth2/code/}"
    githubMapper:
      # The email addresses that will be mapped from the URL
      emailUrl: "${SECURITY_OAUTH2_GITHUB_MAPPER_EMAIL_URL_KEY:https://api.github.com/user/emails}"
```

oauth2Login 登陆成功的 handler 为 `Oauth2AuthenticationSuccessHandler`：

- 通过 `httpCookieOAuth2AuthorizationRequestRepository` 获取 OAuth2AuthorizationRequest
- 从 authorizationRequest 属性 获取 `callback_url_scheme`
- 获取 `baseUrl`
- 获取 `OAuth2AuthenticationToken`
- 使用 `OAuth2ClientService` 通过 `OAuth2AuthenticationToken` 的 `authorizedClientRegistrationId` 获取 OAuth2Client
- 使用 `OAuth2AuthorizedClientService` 通过 `OAuth2AuthenticationToken` 的 `authorizedClientRegistrationId`  和 principal name 获取 OAuth2AuthorizedClient
- 使用 `OAuth2ClientMapperProvider` 获取 OAuth2ClientMapper
- 使用 `OAuth2ClientMapper` 创建 SecurityUser
- 清除 `Authentication` 属性
- 创建 `JwtPair`
- 重定向到地址
- 使用 `SystemSecurityService` 记录登陆成功日志

oauth2Login 登陆失败的 handler 为 `Oauth2AuthenticationFailureHandler`：

- 通过 `httpCookieOAuth2AuthorizationRequestRepository` 获取 `OAuth2AuthorizationRequest`
- 从 `authorizationRequest` 属性 获取 `callback_url_scheme`
- 获取 `baseUrl`
- `httpCookieOAuth2AuthorizationRequestRepository` 清除 `cookie`
- 重定向到地址

所以，OAuth2 client 相关代码重点在以下类：

- `CustomOAuth2AuthorizationRequestResolver`

- `OAuth2Controller`、`OAuth2ConfigTemplateController`

- `OAuth2ClientService`、`OAuth2ConfigTemplateService`

  - `OAuth2ClientDao`、`OAuth2ClientRegistrationTemplateDao`
    - `OAuth2Client`、`OAuth2ClientRegistrationTemplate`

- `OAuth2AppTokenFactory`

- `HybridClientRegistrationRepository`

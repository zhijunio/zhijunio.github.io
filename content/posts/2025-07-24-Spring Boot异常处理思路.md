---
title: "Spring Boot 统一异常处理：分类、响应格式与国际化"
date: 2025-07-24 08:00:00+08:00
slug: spring-exception
categories: [ "tech" ]
tags: [ "spring-boot" ]
description: "本文档描述了基于 Spring Boot 的异常处理设计思路，旨在构建一个统一、可扩展、支持国际化的异常处理体系。通过合理的异常分类、统一的响应格式和完善的国际化支持，为前端提供友好的错误信息，同时便于后端进行问题定位和监控。"
---
本文档描述了基于 Spring Boot 的异常处理设计思路，旨在构建一个统一、可扩展、支持国际化的异常处理体系。通过合理的异常分类、统一的响应格式和完善的国际化支持，为前端提供友好的错误信息，同时便于后端进行问题定位和监控。

<!--more-->

## 1. 核心设计原则

### 1.1 异常职责分离

- **业务异常**：由业务逻辑层抛出，表示业务规则违反或业务流程异常
- **系统异常**：由系统层抛出，表示系统级问题（如数据库连接失败、外部服务调用失败）
- **客户端异常**：使用 Spring 现有异常，如参数验证异常、认证授权异常等
- **限流异常**：特殊处理的限流相关异常

### 1.2 完全国际化支持

- 所有异常消息支持多语言，根据用户语言偏好自动切换
- 前端组件标签支持多语言，提供一致的用户体验
- 统一的消息键命名规范，便于维护和扩展
- 支持消息参数化，提供更精确的错误信息

### 1.3 错误码分层设计

- **400-599**：HTTP标准错误码（系统级错误）
  - 400：请求参数错误（Bad Request）
  - 401：认证失败（Unauthorized）
  - 403：授权失败（Forbidden）
  - 404：资源不存在（Not Found）
  - 429：限流异常（Too Many Requests）
  - 500：服务器内部错误（Internal Server Error）
- **1000+**：业务级错误码（自定义业务异常）
  - 1000～1999：用户模块异常
  - 2000～2999：订单模块异常
  - 3000～3999：商品模块异常
  - 4000～4999：支付模块异常
  - 5000～5999：系统配置异常
- **便于前端进行差异化处理**：前端可以根据错误码类型进行不同的UI展示和用户引导

### 1.4 统一响应格式

- 所有API响应使用统一的 `ApiResponse<T>` 格式
- 包含错误码、错误消息、响应数据等标准字段
- 支持响应头扩展，提供额外的上下文信息

## 2. 异常体系设计

### 2.1 核心异常类型

#### 2.1.1 RateLimitException（限流异常）

- **错误码**：429
- **使用场景**：API调用频率超限、并发请求过多、资源访问限制
- **特点**：包含重试间隔信息，支持指数退避策略
- **示例**：

  ```java
  throw new RateLimitException("API调用频率超限，请稍后重试", 60);
  ```

#### 2.1.2 BusinessException（业务异常）

- **错误码**：500（或自定义1000+错误码）
- **使用场景**：业务规则违反、业务流程异常、数据状态不一致
- **特点**：包含业务上下文信息，便于问题定位
- **示例**：

  ```java
  throw new BusinessException("USER_NOT_FOUND", userId);
  throw new BusinessException("ORDER_STATUS_INVALID", orderId, currentStatus);
  ```

#### 2.1.3 ValidationException（参数验证异常）

- **错误码**：400
- **使用场景**：业务参数验证失败、数据格式错误
- **特点**：包含具体的验证错误信息
- **示例**：

  ```java
  throw new ValidationException("EMAIL_FORMAT_INVALID", email);
  throw new ValidationException("PHONE_NUMBER_INVALID", phone);
  ```

### 2.2 异常继承体系

```java
/**
 * 基础异常类
 */
public abstract class BaseException extends RuntimeException {
    private final String messageKey;        // 国际化消息键
    private final Object[] messageArgs;     // 消息参数
    // 构造函数和getter方法
}

/**
 * 业务异常
 */
public class BusinessException extends BaseException {
    public BusinessException(String messageKey, Object... args) {
        super(messageKey, args);
    }
}

/**
 * 限流异常
 */
public class RateLimitException extends BaseException {
    private final int retryAfterSeconds;
    
    public RateLimitException(String messageKey, int retryAfterSeconds, Object... args) {
        super(messageKey, args);
        this.retryAfterSeconds = retryAfterSeconds;
    }
}

/**
 * 参数验证异常
 */
public class ValidationException extends BaseException {
    public ValidationException(String messageKey, Object... args) {
        super(messageKey, args);
    }
}
```

### 2.3 Spring 现有异常处理

#### 2.3.1 客户端异常（400系列）

- `MethodArgumentNotValidException`：参数验证失败
- `BindException`：数据绑定异常
- `HttpMessageNotReadableException`：请求体解析异常
- `MissingServletRequestParameterException`：缺少请求参数
- `TypeMismatchException`：参数类型不匹配
- `HttpRequestMethodNotSupportedException`：不支持的HTTP方法

#### 2.3.2 认证授权异常（401/403系列）

- `AuthenticationException`：认证失败
- `BadCredentialsException`：凭据无效
- `InsufficientAuthenticationException`：认证信息不足
- `AccessDeniedException`：访问被拒绝
- `JwtException`：JWT令牌异常

#### 2.3.3 服务器异常（500系列）

- `DataAccessException`：数据访问异常
- `HttpClientErrorException`：HTTP客户端异常
- `HttpServerErrorException`：HTTP服务器异常
- `ConnectTimeoutException`：连接超时异常
- `ReadTimeoutException`：读取超时异常

## 3. 统一响应结构

### 3.1 ApiResponse 结构设计

```java
/**
 * 统一API响应结构
 * @param <T> 响应数据类型
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponse<T> {
    /** 响应状态码 */
    private int code;
    
    /** 响应消息（已国际化） */
    private String message;
    
    /** 响应数据 */
    private T data;

    /** 成功响应 */
    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
                .code(200)
                .message("操作成功")
                .data(data)
                .build();
    }
    
    /** 成功响应（无数据） */
    public static <T> ApiResponse<T> success() {
        return success(null);
    }
    
    /** 错误响应 */
    public static <T> ApiResponse<T> error(int code, String message) {
        return ApiResponse.<T>builder()
                .code(code)
                .message(message)
                .build();
    }

    public static <T> ApiResponse<T> error(String message) {
      return ApiResponse.<T>builder()
              .code(500)
              .message(message)
              .build();
    }
}
```

### 3.2 响应头设计

#### 3.2.1 通用响应头

```http
X-Request-Id: uuid                    # 请求追踪ID
X-Response-Time: 100ms                # 响应时间
X-Server-Time: 1640995200000          # 服务器时间戳
```

#### 3.2.2 错误响应头

```http
X-Error-Type: BUSINESS                # 错误类型（CLIENT/BUSINESS/SYSTEM/RATE_LIMIT）
X-Error-Details: 用户不存在: 12345    # 异常cause的message信息
X-Retry-Allowed: true                 # 是否允许重试
Retry-After: 60                       # 限流异常的重试间隔（秒）
```

### 3.3 错误类型枚举

```java
/**
 * 错误类型枚举
 */
public enum ErrorType {
    CLIENT,     // 客户端错误
    BUSINESS,   // 业务错误
    SYSTEM,     // 系统错误
    RATE_LIMIT  // 限流错误
}

/**
 * 错误分类枚举
 */
public enum ErrorCategory {
    COMMON,     // 通用错误
    AUTH,       // 认证授权
    USER,       // 用户模块
    ORDER,      // 订单模块
    PRODUCT,    // 商品模块
    PAYMENT,    // 支付模块
    SYSTEM      // 系统模块
}
```

## 4. 国际化资源文件设计

### 4.1 命名规范

#### 4.1.1 消息键格式

```
{category}.{type}.{key}
```

#### 4.1.2 分类定义（Category）

- **common**：通用消息（系统级）
- **auth**：认证授权消息
- **user**：用户模块消息
- **order**：订单模块消息
- **product**：商品模块消息
- **payment**：支付模块消息
- **system**：系统配置消息

#### 4.1.3 类型定义（Type）

- **error**：错误消息
- **success**：成功消息
- **info**：信息消息
- **warning**：警告消息
- **label**：标签文本
- **button**：按钮文本
- **title**：标题文本
- **placeholder**：占位符文本
- **help**：帮助文本

#### 4.1.4 键命名规范（Key）

- 使用小写字母和下划线
- 语义清晰、简洁明了
- 避免过长的键名
- 保持命名一致性

### 4.2 消息键示例

#### 4.2.1 通用错误消息

```properties
# 客户端异常（400系列）
common.error.invalid_parameter=参数无效：{0}
common.error.missing_parameter=缺少必需参数：{0}
common.error.request_body_invalid=请求体格式无效
common.error.unsupported_method=不支持的HTTP方法：{0}
common.error.type_mismatch=参数类型不匹配：{0}应为{1}类型

# 认证授权异常（401/403系列）
auth.error.authentication_failed=认证失败
auth.error.bad_credentials=用户名或密码错误
auth.error.insufficient_authentication=认证信息不足
auth.error.access_denied=访问被拒绝，权限不足
auth.error.token_expired=访问令牌已过期
auth.error.token_invalid=访问令牌无效
auth.error.refresh_token_expired=刷新令牌已过期

# 服务器异常（500系列）
common.error.internal_server=服务器内部错误
common.error.service_unavailable=服务暂不可用
common.error.database_error=数据库操作失败
common.error.external_service_error=外部服务调用失败
common.error.timeout=请求超时

# 限流异常（429）
common.error.rate_limit_exceeded=请求频率超限，请{0}秒后重试
common.error.concurrent_limit_exceeded=并发请求过多，请稍后重试
```

#### 4.2.2 业务错误消息

```properties
# 用户模块（1000-1999）
user.error.user_not_found=用户不存在：{0}
user.error.user_already_exists=用户已存在：{0}
user.error.invalid_credentials=用户名或密码错误
user.error.account_locked=账户已锁定，请联系管理员
user.error.account_disabled=账户已禁用
user.error.email_already_exists=邮箱已被使用：{0}
user.error.phone_already_exists=手机号已被使用：{0}
user.error.password_too_weak=密码强度不足
user.error.verification_code_expired=验证码已过期
user.error.verification_code_invalid=验证码无效

# 订单模块（2000-2999）
order.error.order_not_found=订单不存在：{0}
order.error.order_status_invalid=订单状态无效：当前状态{0}，期望状态{1}
order.error.order_already_paid=订单已支付：{0}
order.error.order_cannot_cancel=订单无法取消：{0}
order.error.order_cannot_modify=订单无法修改：{0}
order.error.insufficient_balance=余额不足，当前余额：{0}，需要：{1}
order.error.payment_failed=支付失败：{0}

# 商品模块（3000-3999）
product.error.product_not_found=商品不存在：{0}
product.error.insufficient_stock=库存不足：商品{0}，当前库存{1}，需要{2}
product.error.product_disabled=商品已下架：{0}
product.error.category_not_found=商品分类不存在：{0}
product.error.price_changed=商品价格已变更：{0}

# 支付模块（4000-4999）
payment.error.payment_not_found=支付记录不存在：{0}
payment.error.payment_already_processed=支付已处理：{0}
payment.error.payment_failed=支付失败：{0}
payment.error.refund_failed=退款失败：{0}
payment.error.amount_invalid=支付金额无效：{0}
```

#### 4.2.3 成功消息

```properties
# 通用成功消息
common.success.operation_completed=操作完成
common.success.data_saved=数据保存成功
common.success.data_deleted=数据删除成功
common.success.data_updated=数据更新成功

# 用户模块成功消息
user.success.user_created=用户创建成功
user.success.user_updated=用户信息更新成功
user.success.password_changed=密码修改成功
user.success.account_activated=账户激活成功

# 订单模块成功消息
order.success.order_placed=订单提交成功
order.success.order_cancelled=订单取消成功
order.success.payment_successful=支付成功
order.success.refund_processed=退款处理成功
```

#### 4.2.4 前端组件标签

```properties
# 通用标签
common.label.username=用户名
common.label.password=密码
common.label.email=邮箱
common.label.phone=手机号
common.label.confirm_password=确认密码
common.label.verification_code=验证码
common.label.remember_me=记住我
common.label.search=搜索
common.label.filter=筛选
common.label.sort=排序

# 按钮文本
common.button.submit=提交
common.button.cancel=取消
common.button.save=保存
common.button.delete=删除
common.button.edit=编辑
common.button.view=查看
common.button.back=返回
common.button.next=下一步
common.button.previous=上一步
common.button.confirm=确认
common.button.reset=重置

# 标题文本
common.title.login=用户登录
common.title.register=用户注册
common.title.profile=个人资料
common.title.settings=系统设置
common.title.dashboard=仪表板

# 占位符文本
common.placeholder.enter_username=请输入用户名
common.placeholder.enter_password=请输入密码
common.placeholder.enter_email=请输入邮箱地址
common.placeholder.enter_phone=请输入手机号
common.placeholder.search_keyword=请输入搜索关键词

# 业务模块标签
order.label.order_number=订单号
order.label.order_status=订单状态
order.label.order_date=下单时间
order.label.total_amount=总金额
order.label.payment_method=支付方式
order.label.delivery_address=收货地址

product.label.product_name=商品名称
product.label.product_price=商品价格
product.label.product_stock=库存数量
product.label.product_category=商品分类
product.label.product_description=商品描述
```

### 4.3 资源文件结构

#### 4.3.1 中文资源文件（messages_zh_CN.properties）

```properties
# ========================================
# 通用错误消息
# ========================================
common.error.invalid_parameter=参数无效：{0}
common.error.missing_parameter=缺少必需参数：{0}
common.error.request_body_invalid=请求体格式无效
common.error.internal_server=服务器内部错误
common.error.service_unavailable=服务暂不可用
common.error.rate_limit_exceeded=请求频率超限，请{0}秒后重试

# ========================================
# 认证授权错误
# ========================================
auth.error.authentication_failed=认证失败
auth.error.bad_credentials=用户名或密码错误
auth.error.access_denied=访问被拒绝
auth.error.token_expired=访问令牌已过期

# ========================================
# 用户模块错误
# ========================================
user.error.user_not_found=用户不存在：{0}
user.error.user_already_exists=用户已存在：{0}
user.error.invalid_credentials=用户名或密码错误
user.error.account_locked=账户已锁定

# ========================================
# 订单模块错误
# ========================================
order.error.order_not_found=订单不存在：{0}
order.error.order_status_invalid=订单状态无效
order.error.insufficient_balance=余额不足

# ========================================
# 通用标签
# ========================================
common.label.username=用户名
common.label.password=密码
common.label.email=邮箱
common.button.submit=提交
common.button.cancel=取消

# ========================================
# 业务标签
# ========================================
order.label.order_number=订单号
product.label.product_name=商品名称
```

#### 4.3.2 英文资源文件（messages_en_US.properties）

```properties
# ========================================
# Common Error Messages
# ========================================
common.error.invalid_parameter=Invalid parameter: {0}
common.error.missing_parameter=Missing required parameter: {0}
common.error.request_body_invalid=Invalid request body format
common.error.internal_server=Internal server error
common.error.service_unavailable=Service temporarily unavailable
common.error.rate_limit_exceeded=Rate limit exceeded, please retry in {0} seconds

# ========================================
# Authentication & Authorization Errors
# ========================================
auth.error.authentication_failed=Authentication failed
auth.error.bad_credentials=Invalid username or password
auth.error.access_denied=Access denied
auth.error.token_expired=Access token expired

# ========================================
# User Module Errors
# ========================================
user.error.user_not_found=User not found: {0}
user.error.user_already_exists=User already exists: {0}
user.error.invalid_credentials=Invalid username or password
user.error.account_locked=Account is locked

# ========================================
# Order Module Errors
# ========================================
order.error.order_not_found=Order not found: {0}
order.error.order_status_invalid=Invalid order status
order.error.insufficient_balance=Insufficient balance

# ========================================
# Common Labels
# ========================================
common.label.username=Username
common.label.password=Password
common.label.email=Email
common.button.submit=Submit
common.button.cancel=Cancel

# ========================================
# Business Labels
# ========================================
order.label.order_number=Order Number
product.label.product_name=Product Name
```

## 5. 全局异常处理器

### 5.1 处理器设计

```java
/**
 * 全局异常处理器
 * 统一处理所有异常，提供国际化的错误响应
 * 注意：响应头由 ResponseHeaderFilter 统一处理
 */
@Slf4j
@RestControllerAdvice
@RequiredArgsConstructor
public class GlobalExceptionHandler {
    private final MessageSource messageSource;

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(
            BusinessException e, HttpServletRequest request, Locale locale) {

        String localizedMessage = getLocalizedMessage(e.getMessageKey(), e.getMessageArgs(), locale);
        log.warn("业务异常: {} - {} - {}", request.getRequestURI(), e.getMessageKey(), localizedMessage);

        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);

        ApiResponse<Void> response = ApiResponse.error(500, localizedMessage);
        return ResponseEntity.status(500).body(response);
    }


    @ExceptionHandler(RateLimitException.class)
    public ResponseEntity<ApiResponse<Void>> handleRateLimitException(
            RateLimitException e, HttpServletRequest request, Locale locale) {

        String localizedMessage = getLocalizedMessage(e.getMessageKey(), e.getMessageArgs(), locale);
        log.warn("限流异常: {} - {} - {}", request.getRequestURI(), e.getMessageKey(), localizedMessage);

        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);

        ApiResponse<Void> response = ApiResponse.error(429, localizedMessage);
        return ResponseEntity.status(429).body(response);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(
            MethodArgumentNotValidException e, HttpServletRequest request, Locale locale) {

        String localizedMessage = e.getBindingResult().getFieldErrors().stream()
                .map(error -> {
                    String fieldName = error.getField();
                    String defaultMessage = error.getDefaultMessage();
                    try {
                        return messageSource.getMessage(
                                "validation." + fieldName + "." + error.getCode(),
                                error.getArguments(),
                                defaultMessage,
                                locale
                        );
                    } catch (NoSuchMessageException ex) {
                        return defaultMessage;
                    }
                })
                .collect(Collectors.joining(", "));

        log.warn("参数验证失败: {} - {}", request.getRequestURI(), localizedMessage);

        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);

        ApiResponse<Void> response = ApiResponse.error(400, localizedMessage);
        return ResponseEntity.badRequest().body(response);
    }

    @ExceptionHandler({AuthenticationException.class, BadCredentialsException.class})
    public ResponseEntity<ApiResponse<Void>> handleAuthenticationException(
            Exception e, HttpServletRequest request, Locale locale) {

        String localizedMessage = getLocalizedMessage("auth.error.authentication_failed", null, locale);
        log.warn("认证失败: {} - {}", request.getRequestURI(), localizedMessage);

        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);

        ApiResponse<Void> response = ApiResponse.error(401, localizedMessage);
        return ResponseEntity.status(401).body(response);
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse<Void>> handleAccessDeniedException(
            AccessDeniedException e, HttpServletRequest request, Locale locale) {

        String localizedMessage = getLocalizedMessage("auth.error.access_denied", null, locale);
        log.warn("访问被拒绝: {} - {}", request.getRequestURI(), localizedMessage);

        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);

        ApiResponse<Void> response = ApiResponse.error(403, localizedMessage);
        return ResponseEntity.status(403).body(response);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneralException(
            Exception e, HttpServletRequest request, Locale locale) {

        String localizedMessage = getLocalizedMessage("common.error.internal_server", null, locale);
        log.error("系统异常: {} - {}", request.getRequestURI(), e.getMessage(), e);

        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);

        ApiResponse<Void> response = ApiResponse.error(500, localizedMessage);
        return ResponseEntity.status(500).body(response);
    }

    /**
     * 获取国际化消息
     */
    private String getLocalizedMessage(String messageKey, Object[] args, Locale locale) {
        try {
            return messageSource.getMessage(messageKey, args, messageKey, locale);
        } catch (NoSuchMessageException e) {
            log.warn("未找到国际化消息: {}", messageKey);
            return messageKey;
        }
    }
}
```

### 5.2 异常映射规则

| 异常类型 | HTTP状态码 | 错误类型 | 处理方式 | 可重试 | X-Error-Details 示例 |
|---------|-----------|---------|---------|--------|-------------------|
| `MethodArgumentNotValidException` | 400 | CLIENT | 参数验证失败 | ❌ | `用户名不能为空, 邮箱格式不正确` |
| `BindException` | 400 | CLIENT | 数据绑定异常 | ❌ | `字段类型不匹配` |
| `HttpMessageNotReadableException` | 400 | CLIENT | 请求体解析异常 | ❌ | `JSON格式错误` |
| `MissingServletRequestParameterException` | 400 | CLIENT | 缺少请求参数 | ❌ | `缺少必需参数: userId` |
| `AuthenticationException` | 401 | CLIENT | 认证失败 | ❌ | `用户未登录` |
| `BadCredentialsException` | 401 | CLIENT | 凭据无效 | ❌ | `用户名或密码错误` |
| `AccessDeniedException` | 403 | CLIENT | 访问被拒绝 | ❌ | `权限不足` |
| `RateLimitException` | 429 | RATE_LIMIT | 限流异常 | ✅ | `请求频率超限，请60秒后重试` |
| `BusinessException` | 500/1000+ | BUSINESS | 业务异常 | ❌ | `用户不存在: 12345` |
| `Exception` | 500 | SYSTEM | 系统异常 | ✅ | `数据库连接失败` |

### 5.3 异常重试策略

#### 5.3.1 可重试异常类型

**✅ 可以重试的异常：**

1. **限流异常（RateLimitException）**
   - **原因**：请求频率超限，属于临时性限制
   - **重试策略**：按照 `Retry-After` 头指定的时间间隔重试
   - **示例**：API调用频率超限、并发请求过多

2. **系统异常（Exception）**
   - **原因**：系统级问题，通常是临时性的
   - **重试策略**：使用指数退避策略，最大重试3次
   - **示例**：数据库连接失败、网络超时、外部服务暂时不可用

**❌ 不可重试的异常：**

1. **客户端异常（400系列）**
   - **原因**：请求参数错误、数据格式错误等
   - **说明**：重试无法解决问题，需要修正请求

2. **认证授权异常（401/403系列）**
   - **原因**：认证失败、权限不足等
   - **说明**：重试无法解决问题，需要重新认证或获取权限

3. **业务异常（BusinessException）**
   - **原因**：业务规则违反、数据状态不一致等
   - **说明**：重试无法解决问题，需要修正业务逻辑

#### 5.3.2 响应头过滤器设计

```java
/**
 * 响应头过滤器
 * 统一添加请求追踪、响应时间、重试信息等响应头
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
@RequiredArgsConstructor
@Slf4j
public class ResponseHeaderFilter implements Filter {
    
    private final RetryService retryService;
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) 
            throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        
        // 记录请求开始时间
        long startTime = System.currentTimeMillis();
        
        // 生成请求ID
        String requestId = generateRequestId();
        MDC.put("requestId", requestId);
        
        try {
            // 继续处理请求
            chain.doFilter(request, response);
            
        } finally {
            // 计算响应时间
            long responseTime = System.currentTimeMillis() - startTime;
            
            // 添加通用响应头
            addCommonHeaders(httpResponse, requestId, responseTime);
            
            // 如果是错误响应，添加错误相关响应头
            if (httpResponse.getStatus() >= 400) {
                addErrorHeaders(httpResponse, httpRequest);
            }
            
            // 清理MDC
            MDC.clear();
        }
    }
    
    /**
     * 添加通用响应头
     */
    private void addCommonHeaders(HttpServletResponse response, String requestId, long responseTime) {
        response.setHeader("X-Request-Id", requestId);
        response.setHeader("X-Response-Time", responseTime + "ms");
        response.setHeader("X-Server-Time", String.valueOf(System.currentTimeMillis()));
    }
    
    /**
     * 添加错误响应头
     */
    private void addErrorHeaders(HttpServletResponse response, HttpServletRequest request) {
        // 从请求属性中获取异常信息（由异常处理器设置）
        Exception exception = (Exception) request.getAttribute("exception");
        
        if (exception != null) {
            // 设置错误类型
            String errorType = getErrorType(exception);
            response.setHeader("X-Error-Type", errorType);
            
            // 设置是否可重试
            boolean retryable = retryService.isRetryable(exception);
            response.setHeader("X-Retry-Allowed", String.valueOf(retryable));
            
            // 设置错误详情
            String errorDetails = getExceptionCauseMessage(exception);
            response.setHeader("X-Error-Details", errorDetails);
            
            // 如果是限流异常，设置重试间隔
            if (exception instanceof RateLimitException) {
                RateLimitException rateLimitException = (RateLimitException) exception;
                response.setHeader("Retry-After", String.valueOf(rateLimitException.getRetryAfterSeconds()));
            }
        }
    }
    
    /**
     * 获取错误类型
     */
    private String getErrorType(Exception e) {
        if (e instanceof RateLimitException) {
            return "RATE_LIMIT";
        } else if (e instanceof BusinessException) {
            return "BUSINESS";
        } else if (e instanceof MethodArgumentNotValidException || 
                   e instanceof BindException ||
                   e instanceof HttpMessageNotReadableException ||
                   e instanceof MissingServletRequestParameterException ||
                   e instanceof AuthenticationException ||
                   e instanceof BadCredentialsException ||
                   e instanceof AccessDeniedException) {
            return "CLIENT";
        } else {
            return "SYSTEM";
        }
    }
    
    /**
     * 获取异常cause的message信息
     */
    private String getExceptionCauseMessage(Exception e) {
        Throwable cause = e.getCause();
        if (cause != null) {
            return cause.getMessage();
        }
        return e.getMessage();
    }
    
    /**
     * 生成请求ID
     */
    private String generateRequestId() {
        return UUID.randomUUID().toString().replace("-", "");
    }
}
```

#### 5.3.3 异常处理器简化

```java
/**
 * 全局异常处理器（简化版）
 */
@RestControllerAdvice
@Slf4j
@RequiredArgsConstructor
public class GlobalExceptionHandler {
    
    private final MessageSource messageSource;
    
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(
            BusinessException e,
            HttpServletRequest request,
            Locale locale) {
        
        String localizedMessage = getLocalizedMessage(e.getMessageKey(), e.getMessageArgs(), locale);
        log.warn("业务异常: {} - {} - {}", request.getRequestURI(), e.getMessageKey(), localizedMessage);
        
        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);
        
        ApiResponse<Void> response = ApiResponse.error(500, localizedMessage);
        return ResponseEntity.status(500).body(response);
    }
    
    @ExceptionHandler(RateLimitException.class)
    public ResponseEntity<ApiResponse<Void>> handleRateLimitException(
            RateLimitException e,
            HttpServletRequest request,
            Locale locale) {
        
        String localizedMessage = getLocalizedMessage(e.getMessageKey(), e.getMessageArgs(), locale);
        log.warn("限流异常: {} - {} - {}", request.getRequestURI(), e.getMessageKey(), localizedMessage);
        
        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);
        
        ApiResponse<Void> response = ApiResponse.error(429, localizedMessage);
        return ResponseEntity.status(429).body(response);
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(
            MethodArgumentNotValidException e,
            HttpServletRequest request,
            Locale locale) {
        
        String localizedMessage = e.getBindingResult().getFieldErrors().stream()
                .map(error -> {
                    String fieldName = error.getField();
                    String defaultMessage = error.getDefaultMessage();
                    try {
                        return messageSource.getMessage(
                                "validation." + fieldName + "." + error.getCode(),
                                error.getArguments(),
                                defaultMessage,
                                locale
                        );
                    } catch (NoSuchMessageException ex) {
                        return defaultMessage;
                    }
                })
                .collect(Collectors.joining(", "));
        
        log.warn("参数验证失败: {} - {}", request.getRequestURI(), localizedMessage);
        
        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);
        
        ApiResponse<Void> response = ApiResponse.error(400, localizedMessage);
        return ResponseEntity.badRequest().body(response);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneralException(
            Exception e,
            HttpServletRequest request,
            Locale locale) {
        
        String localizedMessage = getLocalizedMessage("common.error.internal_server", null, locale);
        log.error("系统异常: {} - {}", request.getRequestURI(), e.getMessage(), e);
        
        // 将异常存储到请求属性中，供过滤器使用
        request.setAttribute("exception", e);
        
        ApiResponse<Void> response = ApiResponse.error(500, localizedMessage);
        return ResponseEntity.status(500).body(response);
    }
    
    /**
     * 获取国际化消息
     */
    private String getLocalizedMessage(String messageKey, Object[] args, Locale locale) {
        try {
            return messageSource.getMessage(messageKey, args, messageKey, locale);
        } catch (NoSuchMessageException e) {
            log.warn("未找到国际化消息: {}", messageKey);
            return messageKey;
        }
    }
}
```

#### 5.3.3 重试策略实现

```java
/**
 * 重试策略配置
 */
@Configuration
public class RetryConfig {
    
    @Bean
    public RetryTemplate retryTemplate() {
        RetryTemplate retryTemplate = new RetryTemplate();
        
        // 重试策略：指数退避
        ExponentialBackOffPolicy backOffPolicy = new ExponentialBackOffPolicy();
        backOffPolicy.setInitialInterval(1000); // 初始间隔1秒
        backOffPolicy.setMultiplier(2.0);       // 倍数2
        backOffPolicy.setMaxInterval(10000);    // 最大间隔10秒
        retryTemplate.setBackOffPolicy(backOffPolicy);
        
        // 重试策略：最多重试3次
        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy();
        retryPolicy.setMaxAttempts(3);
        retryTemplate.setRetryPolicy(retryPolicy);
        
        return retryTemplate;
    }
}

/**
 * 重试服务
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class RetryService {
    
    private final RetryTemplate retryTemplate;
    
    /**
     * 执行可重试操作
     */
    public <T> T executeWithRetry(Supplier<T> operation, String operationName) {
        try {
            return retryTemplate.execute(context -> {
                log.info("执行操作: {}, 重试次数: {}", operationName, context.getRetryCount());
                return operation.get();
            });
        } catch (Exception e) {
            log.error("操作执行失败: {}, 重试次数已用完", operationName, e);
            throw e;
        }
    }
    
    /**
     * 判断异常是否可重试
     */
    public boolean isRetryable(Exception e) {
        return e instanceof RateLimitException || 
               (e instanceof Exception && !isClientError(e));
    }
    
    /**
     * 判断是否为客户端错误
     */
    private boolean isClientError(Exception e) {
        return e instanceof MethodArgumentNotValidException ||
               e instanceof BindException ||
               e instanceof HttpMessageNotReadableException ||
               e instanceof MissingServletRequestParameterException ||
               e instanceof AuthenticationException ||
               e instanceof BadCredentialsException ||
               e instanceof AccessDeniedException ||
               e instanceof BusinessException;
    }
}
```

### 5.4 异常处理流程

1. **请求进入**：`ResponseHeaderFilter` 开始处理，生成请求ID，记录开始时间
2. **异常捕获**：全局异常处理器捕获所有未处理的异常
3. **异常分类**：根据异常类型进行分类处理
4. **消息国际化**：根据用户语言偏好获取对应的错误消息
5. **异常存储**：将异常存储到请求属性中，供过滤器使用
6. **响应构建**：构建统一的API响应格式
7. **响应头设置**：`ResponseHeaderFilter` 统一设置所有响应头
8. **日志记录**：记录异常信息用于问题排查
9. **响应返回**：返回格式化的错误响应

### 5.5 过滤器设计优势

#### 5.5.1 职责分离

- **异常处理器**：专注于异常分类、消息国际化、响应体构建
- **响应头过滤器**：专注于响应头设置、请求追踪、性能监控

#### 5.5.2 代码简化

- 异常处理器代码更简洁，只需关注业务逻辑
- 响应头设置逻辑集中管理，便于维护
- 减少了重复代码

#### 5.5.3 统一处理

- 所有响应（成功和异常）都会添加通用响应头
- 响应头设置逻辑一致，避免遗漏
- 便于监控和调试

#### 5.5.4 扩展性好

- 新增响应头只需修改过滤器
- 新增异常类型只需在过滤器中添加判断逻辑
- 便于添加新的监控指标

## 6. 最佳实践

### 6.1 异常抛出规范

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {
    
    private final UserRepository userRepository;
    private final RetryService retryService;
    
    public UserResponse getUserById(Long userId) {
        // 参数验证
        if (userId == null) {
            throw new ValidationException("USER_ID_REQUIRED");
        }
        
        // 业务逻辑
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException("USER_NOT_FOUND", userId));
        
        // 状态验证
        if (!user.isActive()) {
            throw new BusinessException("USER_ACCOUNT_DISABLED", userId);
        }
        
        return userConverter.toResponse(user);
    }
    
    public UserResponse createUser(UserCreateRequest request) {
        // 业务规则验证
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("USER_EMAIL_EXISTS", request.getEmail());
        }
        
        if (userRepository.existsByPhone(request.getPhone())) {
            throw new BusinessException("USER_PHONE_EXISTS", request.getPhone());
        }
        
        // 创建用户
        User user = userConverter.toEntity(request);
        user = userRepository.save(user);
        
        log.info("用户创建成功: {}", user.getId());
        return userConverter.toResponse(user);
    }
    
    /**
     * 调用外部服务（支持重试）
     */
    public UserProfileResponse getUserProfile(Long userId) {
        return retryService.executeWithRetry(
            () -> externalUserService.getProfile(userId),
            "获取用户档案"
        );
    }
    
    /**
     * 发送通知（支持重试）
     */
    public void sendNotification(Long userId, String message) {
        retryService.executeWithRetry(
            () -> {
                notificationService.send(userId, message);
                return null;
            },
            "发送通知"
        );
    }
}
```

### 6.2 重试策略使用示例

```java
/**
 * 外部服务调用示例
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ExternalServiceClient {
    
    private final RetryService retryService;
    private final RestTemplate restTemplate;
    
    /**
     * 调用支付服务（支持重试）
     */
    public PaymentResponse processPayment(PaymentRequest request) {
        return retryService.executeWithRetry(
            () -> {
                try {
                    ResponseEntity<PaymentResponse> response = restTemplate.postForEntity(
                        "/api/payments",
                        request,
                        PaymentResponse.class
                    );
                    
                    if (response.getStatusCode().is2xxSuccessful()) {
                        return response.getBody();
                    } else {
                        throw new RuntimeException("支付服务调用失败: " + response.getStatusCode());
                    }
                } catch (Exception e) {
                    log.warn("支付服务调用异常，准备重试: {}", e.getMessage());
                    throw e;
                }
            },
            "处理支付"
        );
    }
    
    /**
     * 调用短信服务（支持重试）
     */
    public void sendSms(String phone, String message) {
        retryService.executeWithRetry(
            () -> {
                try {
                    SmsRequest smsRequest = new SmsRequest(phone, message);
                    ResponseEntity<SmsResponse> response = restTemplate.postForEntity(
                        "/api/sms/send",
                        smsRequest,
                        SmsResponse.class
                    );
                    
                    if (!response.getStatusCode().is2xxSuccessful()) {
                        throw new RuntimeException("短信发送失败: " + response.getStatusCode());
                    }
                    
                    return null;
                } catch (Exception e) {
                    log.warn("短信服务调用异常，准备重试: {}", e.getMessage());
                    throw e;
                }
            },
            "发送短信"
        );
    }
}
```

### 6.3 异常监控和告警

```java
/**
 * 异常监控切面
 */
@Aspect
@Component
@Slf4j
@RequiredArgsConstructor
public class ExceptionMonitorAspect {
    
    private final MetricsService metricsService;
    private final AlertService alertService;
    
    @Around("@annotation(org.springframework.web.bind.annotation.RequestMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.GetMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.PostMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.PutMapping) || " +
            "@annotation(org.springframework.web.bind.annotation.DeleteMapping)")
    public Object monitorExceptions(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        try {
            Object result = joinPoint.proceed();
            long duration = System.currentTimeMillis() - startTime;
            
            // 记录成功指标
            metricsService.recordSuccess(joinPoint.getSignature().getName(), duration);
            
            return result;
            
        } catch (BusinessException e) {
            // 记录业务异常指标
            metricsService.recordBusinessException(e.getErrorCode(), e.getMessageKey());
            throw e;
            
        } catch (RateLimitException e) {
            // 记录限流异常指标
            metricsService.recordRateLimitException();
            throw e;
            
        } catch (Exception e) {
            // 记录系统异常指标
            metricsService.recordSystemException(e.getClass().getSimpleName());
            
            // 发送告警
            alertService.sendAlert("系统异常", e.getMessage(), e);
            
            throw e;
        }
    }
}
```

### 6.4 异常测试

```java
@SpringBootTest
@AutoConfigureTestDatabase
class GlobalExceptionHandlerTest {
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    @DisplayName("测试业务异常处理")
    void testBusinessException() {
        // Given
        String url = "/api/users/999999";
        
        // When
        ResponseEntity<ApiResponse> response = restTemplate.getForEntity(url, ApiResponse.class);
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.INTERNAL_SERVER_ERROR);
        assertThat(response.getBody().getCode()).isEqualTo(500);
        assertThat(response.getBody().getMessage()).contains("用户不存在");
        assertThat(response.getHeaders().getFirst("X-Error-Type")).isEqualTo("BUSINESS");
        assertThat(response.getHeaders().getFirst("X-Error-Details")).contains("用户不存在");
    }
    
    @Test
    @DisplayName("测试参数验证异常处理")
    void testValidationException() {
        // Given
        UserCreateRequest request = new UserCreateRequest();
        // 不设置必需字段
        
        // When
        ResponseEntity<ApiResponse> response = restTemplate.postForEntity(
            "/api/users", request, ApiResponse.class);
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(response.getBody().getCode()).isEqualTo(400);
        assertThat(response.getHeaders().getFirst("X-Error-Type")).isEqualTo("CLIENT");
        assertThat(response.getHeaders().getFirst("X-Error-Details")).isNotNull();
    }
    
    @Test
    @DisplayName("测试限流异常处理")
    void testRateLimitException() {
        // Given
        String url = "/api/rate-limited-endpoint";
        
        // When
        ResponseEntity<ApiResponse> response = restTemplate.getForEntity(url, ApiResponse.class);
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.TOO_MANY_REQUESTS);
        assertThat(response.getBody().getCode()).isEqualTo(429);
        assertThat(response.getHeaders().getFirst("Retry-After")).isNotNull();
        assertThat(response.getHeaders().getFirst("X-Error-Type")).isEqualTo("RATE_LIMIT");
        assertThat(response.getHeaders().getFirst("X-Error-Details")).contains("请求频率超限");
    }
}
```

## 7. 总结

通过以上设计，我们构建了一个完整的异常处理体系，具有以下特点：

1. **统一性**：所有异常都通过统一的处理器进行处理
2. **国际化**：支持多语言错误消息
3. **可扩展性**：易于添加新的异常类型和错误码
4. **可维护性**：清晰的异常分类和命名规范
5. **可监控性**：支持异常监控和告警
6. **用户友好**：提供清晰的错误信息和用户引导

这个设计思路可以很好地支持大型项目的异常处理需求，为前端提供友好的错误信息，同时便于后端进行问题定位和系统监控。

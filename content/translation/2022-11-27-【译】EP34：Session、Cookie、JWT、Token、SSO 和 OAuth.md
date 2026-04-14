---
title: "【译】EP34：Session、Cookie、JWT、Token、SSO 和 OAuth"
date: 2022-11-27 00:30:00+08:00
draft: true
slug: "ep34-session-cookie-jwt-token-sso"
categories: [ "translation" ]
tags: [ "authentication", "security", "system-design" ]
description: "这篇文章解释了用户身份管理相关术语（Session、Cookie、JWT、Token、SSO、OAuth）的区别，以及在线票务平台架构演进和去中心化社交网络。"
canonicalURL: "https://blog.bytebytego.com/p/ep34-session-cookie-jwt-token-sso"
---

在这篇文章中，我们将讨论以下话题：
- Token、Cookie、Session
- 什么是 CDN
- 学习支付系统
- 在线票务平台
- 中心化 vs. 去中心化社交网络

## Session、Cookie、JWT、Token、SSO 和 OAuth 2.0

这些术语都与用户身份管理相关。当你登录网站时，你声明你是谁（识别）。你的身份被验证（认证），然后被授予必要的权限（授权）。过去已经提出了许多解决方案，而且列表还在不断增长。

从简单到复杂，这是我对用户身份管理的理解：

### WWW-Authenticate
这是最基本的方法。浏览器询问用户名和密码。由于无法控制登录生命周期，今天很少使用。

### Session-Cookie
对登录生命周期有更精细的控制。服务器维护会话存储，浏览器保存会话 ID。Cookie 通常只适用于浏览器，对移动应用不友好。

### Token
为了解决兼容性问题，可以使用 Token。客户端向服务器发送 Token，服务器验证 Token。缺点是 Token 需要加密和解密，可能很耗时。

### JWT
JWT 是表示 Token 的标准方式。这些信息可以被验证和信任，因为它是数字签名的。由于 JWT 包含签名，服务器端不需要保存会话信息。

### SSO（单点登录）
通过使用 SSO，你只需登录一次即可登录多个网站。它使用 CAS（中央认证服务）来维护跨站点信息。

### OAuth 2.0
通过使用 OAuth 2.0，你可以授权一个网站访问你在另一个网站上的信息。

## 在线票务平台

上周，Ticketmaster 由于票务系统需求异常高而停止了 Taylor Swift 巡演的公开售票。

这是一个有趣的问题，所以我们对此做了一些研究。下图显示了中国在线火车票预订系统的演变。

中国火车票预订系统面临与 Ticketmaster 系统类似的挑战：
- 高峰时段并发访问量非常高
- 检查剩余票和订单的 QPS 非常高
- 大量机器人

### 解决方案
- **分离读写请求**：因为焦虑的用户不断刷新网页检查是否有票，系统承受巨大压力。为了在内存中处理计算和查询，剩余票组件完全移到 GemFire。可以将全国的火车票放入几 GB 内存中。此外，订单查询组件也移到 GemFire 以减轻订单数据库的负载。Hadoop 用于存储历史订单
- **利用公有云实现弹性容量**
- **禁止机器人**：减少了 95% 的流量
- **增加系统带宽**
- **在不同城市设立更多数据中心以提高系统可用性**
- **设计多个应急计划**

注意：数字基于粗略估算（非官方数据）。

## 去中心化社交网络

什么是去中心化社交网络服务？

下图显示了 Twitter 和 Mastodon 之间的比较。

据说特朗普的新社交媒体平台 Truth Social 正在使用 Mastodon。

Mastodon 运行自托管社交网络服务。它是免费的，没有广告。在 Elon Musk 收购 Twitter 后，它的 MAU（月活跃用户）从 10 月的 50 万增加到 11 月的 100 万。

与 Twitter 的服务器属于 Twitter 公司不同，Mastodon 的服务器不属于任何公司。它的网络由来自不同组织的服务器（实例）组成。

当用户注册时，他们必须选择一台服务器开始。由于服务器相互同步，用户仍然可以接收来自其他服务器的更新。

因为网络由志愿者运行，公司只有一名员工——其创始人 Eugen Rochko。它由众筹运行，目前有 3500 人支持。

> 本文为学习目的的个人翻译，译文仅供参考。
>
> 原文链接：[EP34: Session, cookie, JWT, token, SSO, and OAuth](https://blog.bytebytego.com/p/ep34-session-cookie-jwt-token-sso)。
>
> 版权归原作者或原刊登方所有。本文为非官方译本；如有不妥，请联系删除。

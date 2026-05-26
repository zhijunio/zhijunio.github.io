---
title: "OAuth 2.0 入门指南：授权协议核心概念与实践资源"
date: 2024-06-06 08:00:00+08:00
slug: all-things-about-oauth
tags: [ "oauth2" ]
description: "整理 OAuth 与 OAuth 2.0 的基础概念、入门文章和实践资料，帮助快速建立对授权协议的整体认识。"
---



OAuth 是一种**开放协议**，允许通过网络、移动和桌面应用程序以**简单**、**标准的方式进行**安全授权。

<!--more-->

## OAuth 2 入门

以下是一些 OAuth 2.0 指南，涵盖了理解和实现客户端和服务器所需的许多主题。

### [OAuth 2.0 简化版](https://aaronparecki.com/oauth-2-simplified/)

由 [Aaron Parecki](https://aaronparecki.com/) 编写的*《OAuth 2.0 Simplified*》是一份专注于编写客户端的 OAuth 2.0 指南，它在入门级别上清晰地概述了规范。

- [角色](https://aaronparecki.com/oauth-2-simplified/#roles)：应用程序、API 和用户

- [创建应用程序](https://aaronparecki.com/oauth-2-simplified/#creating-an-app)

- 授权

  ：获取访问令牌

  - [Web 服务器应用程序](https://aaronparecki.com/oauth-2-simplified/#web-server-apps)
  - [单页应用程序](https://aaronparecki.com/2012/07/29/2/oauth2-simplified#single-page-apps)
  - [移动应用程序](https://aaronparecki.com/oauth-2-simplified/#mobile-apps)
  - [其他的](https://aaronparecki.com/oauth-2-simplified/#others)

- [发出经过身份验证的请求](https://aaronparecki.com/oauth-2-simplified/#making-authenticated-requests)

- 与 OAuth 1.0 的区别

  - [身份验证和签名](https://aaronparecki.com/oauth-2-simplified/#authentication-and-signatures)
  - [用户体验和替代授权流程](https://aaronparecki.com/oauth-2-simplified/#user-experience-and-alternative-authorization-flows)
  - [规模性能](https://aaronparecki.com/oauth-2-simplified/#performance-at-scale)

- [资源](https://aaronparecki.com/oauth-2-simplified/#resources)

### [OAuth 2.0 服务器](https://oauth.com/)

*OAuth 2.0 服务器，由*[Aaron Parecki](https://aaronparecki.com/)编写并由[Okta](https://developer.okta.com/)发布，是构建 OAuth 2.0 服务器的指南，其中包括许多不属于规范的细节。

### 代码和库

有多种语言的[客户端和服务器库](https://oauth.net/code/)可以帮助您快速入门。

### 图书

您可以找到一些有关 OAuth 2.0 的优秀[书籍](https://oauth.net/books/)。

### 咨询

寻找一位[OAuth 顾问](https://oauth.net/consulting/)来帮助您的组织。

## Spring Authorization Server

- [Spring Authorization Server官方文档](https://docs.spring.io/spring-authorization-server/reference/overview.html)

- [Spring Authorization Server 配置模型](https://blog.csdn.net/semicolon_hello/article/details/136186226)
- [Spring Authorization Server （如何使用具有 PKCE 的单页应用程序进行身份验证-1）](https://blog.csdn.net/semicolon_hello/article/details/136214544)
- [Spring Authorization Server （如何使用具有 PKCE 的单页应用程序进行身份验证-2）](https://blog.csdn.net/semicolon_hello/article/details/136214824)

- [Spring Authorization Server相关文章](https://blog.51cto.com/u_15268610/category2)

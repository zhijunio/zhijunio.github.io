---
title: "MicroProfile 入门：Java 微服务规范体系与学习资源"
date: 2023-12-14 08:00:00+08:00
slug: all-things-about-microprofile
categories: [ "tech" ]
tags: [ "microservices" ]
description: "整理 MicroProfile 的基础概念、目标与相关学习资料，适合作为 Java 微服务规范体系的入门索引。"
---

最近在一些开源项目中看到了 MicroProfile ，于是在网上查阅了相关资料加深对 MicroProfile 的理解，并做了笔记形成此文。

<!--more-->

## MicroProfile

MicroProfile是一个开放的企业级Java微服务框架，旨在简化和标准化基于微服务架构的应用程序开发。它是由Eclipse Foundation主导的一个开源项目，致力于提供轻量级、可移植和可互操作的Java微服务规范和实现。

MicroProfile的目标是为Java开发人员提供一个规范集合，使他们能够更轻松地构建和部署云原生应用程序。它结合了Java EE、Jakarta EE和其他相关规范，为开发人员提供了一组核心功能和扩展，以支持构建可伸缩、弹性和高性能的微服务应用程序。

MicroProfile提供了一系列的规范，包括：

- [MicroProfile Config](https://github.com/eclipse/microprofile-config)
- [MicroProfile JWT RBAC](https://github.com/eclipse/microprofile-jwt-auth)
- [MicroProfile Health](https://github.com/eclipse/microprofile-health)
- [MicroProfile Fault Tolerance](https://github.com/eclipse/microprofile-fault-tolerance)
- [MicroProfile Metrics](https://github.com/eclipse/microprofile-metrics)
- [MicroProfile OpenAPI](https://github.com/eclipse/microprofile-open-api)
- [MicroProfile OpenTracing](https://github.com/eclipse/microprofile-opentracing)
- [MicroProfile REST Client](https://github.com/eclipse/microprofile-rest-client)
- [MicroProfile Context Propagation](https://github.com/eclipse/microprofile-context-propagation)
- [MicroProfile Reactive Streams Operators](https://github.com/eclipse/microprofile-reactive-streams-operators)
- [MicroProfile Reactive Messaging](https://github.com/eclipse/microprofile-reactive-messaging)
- [MicroProfile GraphQL](https://github.com/eclipse/microprofile-graphql)
- [MicroProfile Long Running Actions](https://github.com/eclipse/microprofile-lra)
- [MicroProfile Telemetry](https://github.com/eclipse/microprofile-telemetry)

**MicroProfile** 实现：

- [Payara Micro](https://www.payara.fish)：是一个用于容器化Jakarta EE应用部署的轻量级中间件平台，不需要安装、配置或重写代码，可以快速部署
- [WildFly by Redhat](https://www.wildfly.org)：是一个轻量级、模块化的微服务框架，集中、简单、以用户为中心，实现了Jakarta EE和Eclipse MicroProfile的最新企业Java标准。
- [Quarkus by RedHat](https://quarkus.io/)：为GraalVM和OpenJDK HotSpot构建的Kubernetes Native Java堆栈，由最佳的Java库和标准精心打造。
- [Apache TomEE](https://tomee.apache.org/)：这是Apache Tomcat Java企业版，它结合了几个Java企业项目，包括Apache OpenEJB、Apache OpenJPA、Apache OpenWebBeans、Apache MyFaces和其他许多项目。
- [Hammock](https://hammock-project.github.io/)：这是一个基于CDI的bootstrapping Java企业微服务框架，由于其灵活性和简单性，用于构建应用程序
- [Openliberty](https://openliberty.io/)：是一个开源的轻量级Java EE微服务框架，用于构建快速高效的云原生Java微服务应用，只运行所需的服务，同时考虑最新的Eclipse MicroProfile标准
- [Helidon by Oracle](https://helidon.io/%23/)：这是一个Java库的集合，用于编写在快速的Helidon Reactive WebServer上运行的Java微服务，这是一个由Netty驱动的Web核心，同时支持MicroProfile及其标准规范。
- [KumuluzEE](https://ee.kumuluz.com/)：是一个轻量级框架，用于使用标准的Java/JavaEE/JakartaEE/EE4J技术和API开发微服务，可选择扩展，如使用Node.js、Go和其他语言，并将现有应用程序迁移到云原生架构和微服务，以便更容易地进行云原生微服务开发。
- [Launcher by Fujitsu](https://github.com/fujitsu/launcher)：它由富士通公司开发，是一个支持某些MicroProfile规范的Java EE微服务框架，可以将应用捆绑到über-jar/fat文件（JAR文件，包含其所有需要的依赖项）
- [ThornTail (过时的)](https://thorntail.io/)：是一个Java企业级微服务框架，它只将需要的和指定的包捆绑到一个JAR文件中，并有足够的运行时间来运行它们

## MicroProfile发展历史

[Infoq](https://www.infoq.cn/article/6wstmskpbbip6wqoqsmv) 上有一段介绍：

> 2016 年年中，作为对 Oracle 在发布 Java EE 8 方面[停滞不前](https://www.infoq.com/news/2016/07/Java-EE-8-Stagnating/)的直接回应，社区发起了两个新的倡议，也就是[MicroProfile](https://microprofile.io/)和 Java EE Guardians（现在被称为[Jakarta EE Ambassadors](https://jakartaee-ambassadors.io/)）。Java 社区认为，随着用于构建微服务应用的 web 服务技术的出现，企业级 Java 已经落后于时代了。
>
> MicroProfile 倡议是在[2016年6月27日Red Hat的DevNation会议上](https://developers.redhat.com/blog/2016/06/27/microprofile-collaborating-to-bring-microservices-to-enterprise-java/)发起的，它是由 IBM、Red Hat、Tomitribe、Payara 等厂商协作创建的，旨在为企业级 Java 提供微服务。[MicroProfile 1.0的发布](https://developer.jboss.org/blogs/mark.little/2016/09/17/to-microprofile-10-and-beyond)是在 JavaOne 2016 上宣布的，它包含了三个基于 JSR 的 API，这些 API 被视为创建微服务的最低限度要求，即[JSR-346](https://jcp.org/en/jsr/detail?id=346)：上下文和依赖注入（CDI）、[JSR-353](https://jcp.org/en/jsr/detail?id=353)：JSON 处理的 Java API（JSON-P）以及[JSR-339](https://jcp.org/en/jsr/detail?id=339)：RESTful Web 服务的 Java API（JAX-RS）。
>
> 到 2018 年 2 月[MicroProfile 1.3发布的时候](https://www.infoq.com/news/2018/02/microprofile-13/)，已经创建了八个基于社区的 API，以补充最初的三个基于 JSR 的 API，用来构建更加健壮的基于微服务的应用。随着[MicroProfile 2.0](https://www.infoq.com/news/2018/08/microprofile-1.4-and-2.0)的发布，增加了第四个基于 JSR 的 API，即[JSR-367](https://jcp.org/en/jsr/detail?id=367)：JSON 绑定的 Java API（JSON-B）。
>
> 原定于 2020 年 6 月发布的 MicroProfile 4.0[被推迟了](https://microprofile.io/2020/05/29/towards-microprofile-4-0/)，以便于按照 Eclipse 基金会的授权成立[MicroProfile工作组](https://microprofile.io/workinggroup/)。该工作组定义了[MicroProfile规范流程](https://docs.google.com/document/d/1anTlBMyqMbEnRvC8Pz1pAo17Cejy4qUK9ZPbP7NDk8s/edit)和正式的指导委员会，该委员会由各组织和 Java 用户组（Java User Group，JUG）组成，即[亚特兰大JUG](https://ajug.org/)、[IBM](https://www.ibm.com/), [Jelastic](https://jelastic.com/)、[Red Hat](https://www.redhat.com/)和[Tomitribe](https://www.tomitribe.com/)。预计其他的组织和 JUG 会在 2021 年加入。MicroProfile 工作组在 2020 年 12 月 23 日发布了 MicroProfile 4.0，其特性是对[12个核心API进行更新并与Jakarta EE 8保持一致](https://www.infoq.com/news/2020/12/whats-new-in-microprofile-4/)。
>
> MicroProfile 的创始厂商提供了自己的微服务框架，分别是[Open Liberty](https://openliberty.io/)（IBM）、WildFly Swarm/[Thorntail](https://thorntail.io/)（Red Hat）、[TomEE](https://tomee.apache.org/)（Tomitribe 和[Payara Micro](https://www.payara.fish/products/payara-micro/)（Payara），它们最终都支持了 MicroProfile 倡议。
>
> 在 2018 年的年中，Red Hat 将 WildFly Swarm（这是 Red Hat 的核心应用服务器[WildFly](https://www.wildfly.org/)的扩展）重命名为[Thorntail](https://thorntail.io/)，从而为它的微服务框架提供自己的标识。但是，不到一年之后，Red Hat 发布了[Quarkus](https://quarkus.io/)，这是一个“为 OpenJDK HotSpot 和 GraalVM 量身定做的 Kubernetes 原生 Java 栈，基于最优秀的 Java 库和标准精心打造”。Quarkus 被称为“超音速亚原子的 Java”，在 Java 社区迅速流行了起来，以至于 Red Hat[宣布Thorntail在2020年7月寿终正寝](https://thorntail.io/posts/the-end-of-an-era/)。Quarkus 加入了相对较新的框架[Micronaut](https://micronaut.io/)和[Helidon](https://helidon.io/)的行列，这两个框架都是在此之前不到一年前引入 Java 社区的。除了 Micronaut 之外，所有这些基于微服务的框架都支持 MicroProfile 倡议。

MicroProfile的发展历史可以追溯到2016年。以下是MicroProfile的关键里程碑和发展阶段：

1. 2016年6月 - 由Red Hat、IBM、Tomitribe、Payara和LJC（London Java Community）等公司和组织共同发起了MicroProfile项目。旨在创建一个开放的、供应商中立的Java微服务规范。
2. 2016年9月 - MicroProfile 1.0发布，包括Java API for RESTful Web Services（JAX-RS）、Java API for JSON Processing（JSON-P）、Java API for WebSocket（WebSocket）等规范。
3. 2017年5月 - MicroProfile 1.1发布，引入Config API规范，用于外部配置的管理。
4. 2017年9月 - MicroProfile 1.2发布，添加了Health Check API规范，用于检查应用程序的健康状态。
5. 2018年2月 - MicroProfile 1.3发布，引入了OpenAPI规范（以前称为Swagger），用于API文档和可视化。
6. 2018年5月 - MicroProfile 2.0发布，升级了基础规范版本，并添加了Fault Tolerance API规范，用于容错和弹性。
7. 2018年11月 - MicroProfile 2.1发布，增加了Metrics API规范，用于应用程序的性能监控和指标收集。
8. 2019年3月 - MicroProfile 2.2发布，引入了JWT RBAC（Role-Based Access Control）规范，用于身份验证和授权。
9. 2019年11月 - MicroProfile 3.0发布，升级了基础规范版本，支持Java EE 8和Jakarta EE规范。
10. 2020年2月 - MicroProfile 3.1发布，升级了基础规范版本，并增加了其他改进和修复。
11. 2021年5月 - MicroProfile 4.0发布，升级了基础规范版本，并引入了重大改进和新功能，如Context Propagation、Reactive Messaging等。

## MicroProfile Config

MicroProfile Config是MicroProfile的一个重要特性，它提供了一种解决方案，可以将配置从微服务中外部化。这使得应用和微服务可以在多个环境中运行，无需修改或重新打包。配置数据可以动态变化，应用需要能够在不重新启动服务器的情况下访问最新的配置信息。

MicroProfile Config允许从不同的位置和不同的格式获取配置数据，如系统属性、系统环境变量、.properties、.xml和数据源等，这些配置位置被称为ConfigSources。

它提供了一种方式，可以从许多不同的ConfigSources聚合配置，并呈现这些配置的单一、统一的视图。MicroProfile Config提供了两种获取配置属性的方式：编程方式和通过上下文和依赖注入（CDI）。

在编程方式中，你首先获取包含所有可以访问的属性的Config对象，然后通过`getValue(String propertyName, Class<?> propertyValueType)`查找单个属性。使用CDI，可以直接将配置属性值注入到应用中，无需应用代码来检索它们。

此外，还可以根据MicroProfile Config的规定创建自定义的ConfigSource。通过自定义ConfigSource，可以读取额外的配置值，并将它们以定义的顺序添加到Config实例中。这允许覆盖来自其他源的值或回退到其他值。

## 参考文章

- [https://microprofile.io/](https://microprofile.io/)
- [MicroProfile 6.1](https://docs.google.com/presentation/d/1A3Hbr-O7QFepUP5M0X2hKfqFiO1PZgnBWWhMyovu9JU/edit#slide=id.p1)

- [MicroProfile 是什么？](https://zhuanlan.zhihu.com/p/646155513)

- [Eclipse MicroProfile 简介](https://juejin.cn/post/7071617040947085348)

- [什么是Eclipse MicroProfile？](https://www.tomitribe.com/blog/what-is-eclipse-microprofile/)

- [Spring Boot与Eclipse MicroProfile比较](https://developers.redhat.com/blog/2018/11/21/eclipse-microprofile-for-spring-boot-developers/)

- [MicroProfile 对微服务框架的影响 | InfoQ 圆桌](https://www.infoq.cn/article/6wstmskpbbip6wqoqsmv)

- [MicroProfile 编程模型支持](https://www.ibm.com/docs/zh/was-liberty/base?topic=architecture-microprofile-programming-model-support)

- [学习如何使用MicroProfile](https://juejin.cn/post/7171656920414519332)
- [使用 Quarkus 和 MicroProfile 实现微服务特性](https://atbug.com/microservicilities-quarkus/)
- [MicroProfile 云原生微服务开发编程模型](https://www.oschina.net/p/microprofile)

- [使用 MicroProfile、ConfigMaps、Secrets 实现外部化应用配置](https://kubernetes.io/zh-cn/docs/tutorials/configuration/configure-java-microservice/configure-java-microservice/)

- [Eclipse MicroProfile 企业级微服务实用指南](https://javaweb.apachecn.org/#/docs/handson-enter-java-microsvc-eclipse-microprofile/README)

- [亚信Web应用中间件（FlyingServer）通过Eclipse MicroProfile功能测评](https://www.modb.pro/db/1691325241423384576)
- [微服务框架：如果不用 Spring Boot，还可以选择谁？](https://www.cnblogs.com/javastack/p/16851078.html)
- [“Azure 上的 Eclipse MicroProfile”文档](https://learn.microsoft.com/zh-cn/azure/developer/java/eclipse-microprofile/)
- [JBoss 4.2. MicroProfile 配置开发](https://access.redhat.com/documentation/zh-cn/red_hat_jboss_enterprise_application_platform/7.4/html/using_jboss_eap_xp_3.0.0/_microprofile_config_development)

- [QUARKUS - MICROPROFILE 健康检查](https://quarkus.pro/guides/microprofile-health.html)

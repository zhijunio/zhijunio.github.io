---
title: "Spring Modulith 入门：模块化 Spring Boot 3 架构设计"
date: 2024-05-09 08:00:00+08:00
slug: all-things-about-spring-modulith
tags: [ "spring-boot" ]
description: "整理 Spring Modulith 的背景介绍、核心概念与延伸阅读资料，适合作为了解模块化 Spring Boot 架构的入门索引。"
---

VMware 推出了一个实验性的项目[Spring Modulith](https://spring.io/projects/spring-modulith)，以便于通过模块和事件更好地组织 Spring Boot 3 应用。该项目引入了新的类和注解，但并不会生成代码。它的模块没有使用 Java Platform Module System（JPMS），而是映射到了普通的 Java 包。模块有 API，但是 Spring Modulith 鼓励使用 Spring 应用事件作为“主要的交互方式”。这些事件可以自动持久化到事件日志中。Spring Modulith 还简化了模块和事件的测试。

<!--more-->

2022 年 11 月推出的[Spring Boot 3](https://www.infoq.com/news/2022/10/spring-boot-3-jax-london)会是 Spring Modulith 的基础。所以它的基线是 Spring Framework 6、Java 17 和 Jakarta EE 9。Spring Modulith 是[Moduliths](https://github.com/moduliths/moduliths)（其名字有个“s”后缀）项目的继承者。该项目使用 Spring Boot 2.7，目前已经退役，只接收缺陷修正，直至 2023 年 11 月份。

- <https://spring.io/blog/2022/10/21/introducing-spring-modulith>
- <https://www.baeldung.com/spring-modulith>
- <https://www.baeldung.com/spring-modulith-event-externalization>
- <https://piotrminkowski.com/2023/10/13/guide-to-modulith-with-spring-boot/>
- <https://springdoc.cn/guide-to-modulith-with-spring-boot/>
- <https://medium.com/andamp/event-sourcing-with-spring-modulith-2b35b0569dbb>
- <https://www.geeksforgeeks.org/what-is-spring-modulith/>
- <https://github.com/xsreality/spring-modulith-with-ddd>
- <https://riteshshergill.medium.com/the-spring-modulith-monolithic-but-manageable-ca1532a1e585>
- <https://www.infoq.com/news/2022/11/spring-modulith-launch/>
- <https://dzone.com/articles/architecture-style-modulith-vs-microservices>
- <https://speakerdeck.com/olivergierke/spring-modulith-a-deep-dive>
- <https://www.jappware.com/proffesional-activity/make-monolithic-apps-great-again-with-spring-modulith-coffeejug/>
- <https://blog.worldline.tech/2024/01/23/modulith.html>
- <https://springdoc.cn/spring-modulith-intro/>
- <https://dimitri.codes/checking-out-spring-modulith/>
- <https://www.lefer.cn/posts/29752/>

- <https://www.jdon.com/63003.html>

- <https://blog.csdn.net/cfy_banq/article/details/132185951>

- <https://www.zhihu.com/question/567053421>

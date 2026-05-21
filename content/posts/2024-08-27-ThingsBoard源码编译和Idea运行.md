---
title: "ThingsBoard 源码编译与 IDEA 调试环境搭建"
date: 2024-08-27 09:00:00+08:00
slug: thingsboard-code-source-compile
categories: [ "tech" ]
tags: [ "thingsboard" ]
description: "记录 ThingsBoard 源码的编译过程，以及如何在 IDEA 中导入、启动和调试项目，适合作为本地源码环境搭建参考。"
---

ThingsBoard 源码地址：[https://github.com/thingsboard/thingsboard](https://github.com/thingsboard/thingsboard)，从 [3.7](https://github.com/thingsboard/thingsboard/releases/tag/v3.7) 版本之后，要求 JDK17。官方提供了源码编译的文档：[Building from sources](https://thingsboard.io/docs/user-guide/install/building-from-source/)

<!--more-->

## 源码编译

下载代码：

```bash
git clone git@github.com:thingsboard/thingsboard.git
```

设置当前 JDK 版本为 17 以上。这里我使用 sdkman 切换 java。

```bash
sdk use java 17.0.15-tem
```

终端编译源码：

```bash
cd thingsboard
mvn clean install -Dmaven.test.skip=true -Dlicense.skip=true
```

> 排错：
>
> 1. 如果在编译过程中提示找不到 Gradle：
>
> ```
> [ERROR] Failed to execute goal org.thingsboard:gradle-maven-plugin:1.0.12:invoke (default) on project http: org.gradle.tooling.BuildException: Could not execute build using connection to Gradle distribution "https://services.gradle.org/distributions/gradle-7.3.3-bin.zip". -> [Help 1]
> ```
>
> 往上查看详细异常日志：
>
> ```
> * What went wrong:
> Could not compile build file "/Users/zhijunio/Codes/github/thingsboard/packaging/java/build.gradle".
> > startup failed:
>   General error during conversion: Unsupported class file major version 65
> 
>   java.lang.IllegalArgumentException: Unsupported class file major version 65
> ```
>
> 可以看到是 JDK 版本过高的原因。需要确认 JDK 版本使用 17，不能是 21。

如果 maven 下载太慢，则修改 mirrors 节点如下：

```xml
<mirrors>
    <mirror>
        <id>maven-default-http-blocker</id>
        <mirrorOf>external:dont-match-anything-mate:*</mirrorOf>
        <name>Pseudo repository to mirror external repositories initially using HTTP.</name>
        <url>http://0.0.0.0/</url>
    </mirror>

    <mirror>
        <id>aliyun-central</id>
        <name>aliyun-central</name>
        <url>https://maven.aliyun.com/nexus/content/repositories/central</url>
        <mirrorOf>central</mirrorOf>
    </mirror>

    <mirror>
        <id>aliyun-jcenter</id>
        <name>aliyun-jcenter</name>
        <url>https://maven.aliyun.com/nexus/content/repositories/jcenter</url>
        <mirrorOf>jcenter</mirrorOf>
    </mirror>
</mirrors>
```

如果出现下面的错误：

```
 Could not resolve dependencies for project org.thingsboard:application:jar:4.2.0-SNAPSHOT
[ERROR] dependency: org.thingsboard:dao:jar:tests:4.2.0-SNAPSHOT (test)
```

运行下面命令，然后再重新运行编译命令。

```bash
cd dao
mvn install
```

## Idea 中运行

首先 IDEA 需要安装 **lombok** 和 **Protobuf** 相关插件，有个 proto 文件生成的java代码过大(`TransportProtos`)，默认是不会解析的。需要编辑idea 的属性(Help -> Edit Custom Properties)，加入`idea.max.intellisense.filesize=3000`，将上限提高到3M。

准备 postgres 数据库，在 docker 目录下面创建 docker-compose.postgres-1.yml：

```yaml
services:
  postgres:
    restart: always
    image: "postgres:16"
    ports:
    - "5432:5432"
    environment:
      POSTGRES_DB: thingsboard
      POSTGRES_PASSWORD: postgres
```

使用 docker-compose 启动 postgres ：

```bash
docker compose -f docker-compose.postgres-1.yml up -d
```

在 idea 中打开项目，然后将 dao/src/main/resources/sql 目录拷贝到 application/src/main/data 目录下。

运行 application 模块下的 ThingsboardInstallApplication 类，初始化数据库。

运行 application 模块下的 ThingsboardServerApplication 类，启动 thingsboard。

启动成功之后，在浏览器访问 [http://localhost:8080/login](http://localhost:8080/login)， ThingsBoard 默认账户

- 系统管理员： <sysadmin@thingsboard.org> / sysadmin
- 租户管理员：<tenant@thingsboard.org> / tenant
- 客户用户： <customer@thingsboard.org> / customer

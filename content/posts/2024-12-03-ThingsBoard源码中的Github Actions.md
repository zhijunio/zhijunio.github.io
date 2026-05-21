---
title: "ThingsBoard 源码解读：GitHub Actions 自动化流程"
date: 2024-12-03 08:00:00+08:00
slug: github-actions-in-thingsboard
categories: [ "tech" ]
tags: [ "thingsboard", "github" ]
description: "梳理 ThingsBoard 仓库中 GitHub Actions 的工作流文件，了解其配置校验、许可证处理等自动化流程。"
---

ThingsBoard 源码地址：[https://github.com/thingsboard/thingsboard](https://github.com/thingsboard/thingsboard)，其 .github/workflows 目录下面有两个文件：

- `check-configuration-files.yml`：使用 python 脚本校验 yaml 文件
- `license-header-format.yml`：是给文件添加 license 并提交代码到 git 仓库

<!--more-->

## check-configuration-files.yml

check-configuration-files.yml

```yaml
name: Check configuration files
on:
  push:
    branches:
      - master
  pull_request:
    paths:
      - "application/src/main/resources/thingsboard.yml"
      - "transport/http/src/main/resources/tb-http-transport.yml"
      - "transport/http/src/main/resources/tb-mqtt-transport.yml"
      - "transport/http/src/main/resources/tb-coap-transport.yml"
      - "transport/http/src/main/resources/tb-lwm2m-transport.yml"
      - "transport/http/src/main/resources/tb-snmp-transport.yml"
      - "msa/vc-executor/src/main/resources/tb-vc-executor.yml"

jobs:
  build:
    name: Check thingsboard.yml file
    runs-on: ubuntu-20.04
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Set up Python 3.10
        uses: actions/setup-python@v3
        with:
          python-version: "3.10.2"
          architecture: "x64"
        env:
          AGENT_TOOLSDIRECTORY: /opt/hostedtoolcache
      - name: Run Verification Script
        run: python3 tools/src/main/python/check_yml_file.py

```

## license-header-format.yml

license-header-format.yml

```yaml
name: License header format

on:
  push:
    branches:
      - "master"
      - "develop/3*"
      - "hotfix/3*"

jobs:
  license-format:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: "corretto" # https://github.com/actions/setup-java?tab=readme-ov-file#supported-distributions
          java-version: "21"
          cache: "maven" # https://github.com/actions/setup-java?tab=readme-ov-file#caching-sbt-dependencies

      - name: License header format
        run: mvn -T 1C license:format

      - name: License header format (msa/black-box-tests/)
        run: mvn -T 1C license:format -f msa/black-box-tests/

      - name: Set Git user information
        run: |
          git config user.name "ThingsBoard Bot"
          git config user.email "noreply@thingsboard.io"

      - name: Check and push changes
        run: |
          git diff --exit-code || git commit -am "License header format" && git push
```

这里是用到了 license-maven-plugin 插件：

```xml
<plugin>
    <groupId>com.mycila</groupId>
    <artifactId>license-maven-plugin</artifactId>
    <version>3.0</version>
    <configuration>
        <header>${main.dir}/license-header-template.txt</header>
        <properties>
            <owner>The Thingsboard Authors</owner>
        </properties>
        <excludes>
            <exclude>**/.env</exclude>
            <exclude>**/*.env</exclude>
            <exclude>**/.eslintrc</exclude>
            <exclude>**/.babelrc</exclude>
            <exclude>**/.jshintrc</exclude>
            <exclude>**/.gradle/**</exclude>
            <exclude>**/nightwatch</exclude>
            <exclude>**/README</exclude>
            <exclude>**/LICENSE</exclude>
            <exclude>**/banner.txt</exclude>
            <exclude>node_modules/**</exclude>
            <exclude>**/*.properties</exclude>
            <exclude>src/test/resources/**</exclude>
            <exclude>src/vendor/**</exclude>
            <exclude>src/font/**</exclude>
            <exclude>src/sh/**</exclude>
            <exclude>packaging/*/scripts/control/**</exclude>
            <exclude>packaging/*/scripts/windows/**</exclude>
            <exclude>packaging/*/scripts/init/**</exclude>
            <exclude>**/*.log</exclude>
            <exclude>**/*.current</exclude>
            <exclude>.instance_id</exclude>
            <exclude>src/main/scripts/control/**</exclude>
            <exclude>src/main/scripts/windows/**</exclude>
            <exclude>src/main/resources/public/static/rulenode/**</exclude>
            <exclude>**/*.proto.js</exclude>
            <exclude>docker/haproxy/**</exclude>
            <exclude>docker/tb-node/**</exclude>
            <exclude>ui/**</exclude>
            <exclude>**/.browserslistrc</exclude>
            <exclude>**/yarn.lock</exclude>
            <exclude>**/.yarnrc</exclude>
            <exclude>**/.angular/**</exclude>
            <exclude>**/*.raw</exclude>
            <exclude>**/*.patch</exclude>
            <exclude>**/apache/cassandra/io/**</exclude>
            <exclude>.run/**</exclude>
            <exclude>**/NetworkReceive.java</exclude>
            <exclude>**/lwm2m-registry/**</exclude>
            <exclude>src/main/data/resources/**</exclude>
        </excludes>
        <mapping>
            <proto>JAVADOC_STYLE</proto>
            <cql>DOUBLEDASHES_STYLE</cql>
            <scss>JAVADOC_STYLE</scss>
            <jsx>SLASHSTAR_STYLE</jsx>
            <tsx>SLASHSTAR_STYLE</tsx>
            <conf>SCRIPT_STYLE</conf>
            <gradle>JAVADOC_STYLE</gradle>
        </mapping>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

license 文件内容由如下配置定义：

```bash
<header>${main.dir}/license-header-template.txt</header>
```

main.dir 是定义在 properties 节点下面：

```xml
<main.dir>${basedir}</main.dir>
```

license-header-template.txt 文件在项目的根目录下面。

```
Copyright © ${project.inceptionYear}-2024 ${owner}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

- ${project.inceptionYear} Maven 变量

- ${owner} 自定义变量，在 license-maven-plugin 插件中定义：

  ```xml
  <properties>
      <owner>The Thingsboard Authors</owner>
  </properties>
  ```

对于多模块的 maven 项目，子模块是无法通过 `${main.dir}/license-header-template.txt` 找到该文件的。

对于 maven 多模块的项目，可以在子模块里面覆盖该属性，例如：

```xml
<main.dir>${basedir}/..</main.dir>
```

除了该办法之外，还可以使用 directory-maven-plugin 插件定义变量，比如，下面的插件配置了一个 project.rootdir 变量指向项目的根目录。

```xml
<plugin>
    <groupId>org.commonjava.maven.plugins</groupId>
    <artifactId>directory-maven-plugin</artifactId>
    <version>1.0</version>
    <executions>
        <execution>
            <id>set-root-dir-for-common-lifecycle</id>
            <goals>
                <goal>highest-basedir</goal>
            </goals>
            <phase>initialize</phase>
            <configuration>
                <property>project.rootdir</property>
            </configuration>
        </execution>
        <execution>
            <id>set-root-dir-for-clean-lifecycle</id>
            <goals>
                <goal>highest-basedir</goal>
            </goals>
            <phase>pre-clean</phase>
            <configuration>
                <property>project.rootdir</property>
            </configuration>
        </execution>
    </executions>
</plugin>
```

然后，可以在 license-maven-plugin 插件中使用 `${project.rootdir}`

```xml
<plugin>
    <groupId>com.mycila</groupId>
    <artifactId>license-maven-plugin</artifactId>
    <version>3.0</version>
    <configuration>
        <header>${project.rootdir}/license-header-template.txt</header>
        <!-- ... -->
    </configuration>
    <executions>
        <execution>
           <phase>initialize</phase>
            <goals>
                <goal>check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

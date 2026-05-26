---
title: "Docker 容器化 Spring Boot 应用：从开发到部署"
date: 2024-07-09 09:00:00+08:00
slug: docker-for-spring-boot
tags: [ "docker", "spring-boot" ]
description: "基于 Docker 官方 Java 指南，介绍如何将 Spring Boot 应用容器化运行，并逐步搭建本地开发、测试与部署流程。"
---

> 本文翻译自 Docker 官方网站的《[Java language-specific guide](https://docs.docker.com/guides/java/)》文章，并做了一些改动。

Java 入门指南教您如何使用 Docker 创建容器化的 Spring Boot 应用程序。在本模块中，您将学习如何：

- 使用 Maven 容器化并运行 Spring Boot 应用程序
- 设置本地开发环境以将数据库连接到容器，配置调试器，并使用 Compose Watch 进行实时重新加载
- 在容器内运行单元测试
- 使用 GitHub Actions 为应用程序配置 CI/CD 管道
- 将容器化应用程序本地部署到 Kubernetes 以测试和调试您的部署

完成 Java 入门模块后，您应该能够根据本指南中提供的示例和说明来容器化您自己的 Java 应用程序。

# 容器化你的应用

## 先决条件

- 您已安装最新版本的 [Docker Desktop](https://docs.docker.com/get-docker/)，Docker 会定期添加新功能，本指南的某些部分可能仅适用于最新版本的 Docker Desktop。

- 您有一个 [Git 客户端](https://git-scm.com/downloads)。本节中的示例使用基于命令行的 Git 客户端，但您可以使用任何客户端。

## 获取示例应用程序

将要使用的示例应用程序克隆到本地开发机器。在终端中运行以下命令来克隆存储库。

```bash
git clone https://github.com/spring-projects/spring-petclinic.git
cd spring-petclinic
```

## 初始化 Docker 资产

现在您有了一个应用程序，您可以使用它`docker init`来创建必要的 Docker 资产来容器化您的应用程序。在 spring-petclinic 中已包含 Docker 资产。系统将提示您覆盖现有 Docker 资产。要继续本指南，请选择`y`覆盖它们。

```bash
$ docker init
Welcome to the Docker Init CLI!

This utility will walk you through creating the following files with sensible defaults for your project:
  - .dockerignore
  - Dockerfile
  - compose.yaml
  - README.Docker.md

Let's get started!

WARNING: The following Docker files already exist in this directory:
  - docker-compose.yml
? Do you want to overwrite them? Yes
? What application platform does your project use? Java
? What's the relative directory (with a leading .) for your app? ./src
? What version of Java do you want to use? 21
? What port does your server listen on? 8080
```

您的目录中现在应该有以下三个新文件`spring-petclinic` 。

- [Dockerfile](https://docs.docker.com/reference/dockerfile/)
- [.dockerignore](https://docs.docker.com/reference/dockerfile/#dockerignore-file)
- [docker-compose.yaml](https://docs.docker.com/compose/compose-file/)

## 运行应用程序

在目录内`spring-petclinic`，在终端运行以下命令。

```bash
docker compose up --build
```

首次构建并运行应用程序时，Docker 会下载依赖项并构建应用程序。这可能需要几分钟，具体取决于您的网络连接。

打开浏览器并通过 [http://localhost:8080](http://localhost:8080/)查看应用程序。您应该看到一个宠物诊所的简单应用程序。

在终端中，按`ctrl`+`c`停止应用程序。

您可以通过添加选项来运行与终端分离的应用程序`-d` 。在`spring-petclinic`目录中，在终端中运行以下命令。

```bash
docker compose up --build -d
```

打开浏览器并通过 [http://localhost:8080](http://localhost:8080/)查看应用程序。您应该看到一个宠物诊所的简单应用程序。

在终端中，运行以下命令来停止应用程序。

```bash
docker compose down
```

有关 Compose 命令的更多信息，请参阅 [Compose CLI 参考](https://docs.docker.com/compose/reference/)。

## 概括

在本节中，您了解了如何使用 Docker 容器化并运行 Java 应用程序。

相关信息：

- [docker init 参考](https://docs.docker.com/reference/cli/docker/init/)

# 使用容器进行 Java 开发

在本部分中，您将逐步为上一节中容器化的应用程序设置本地开发环境。这包括：

- 添加本地数据库并持久保存数据
- 创建开发容器来连接调试器
- 配置 Compose 以在您编辑和保存代码时自动更新正在运行的 Compose 服务

## 添加本地数据库并保存数据

您可以使用容器来设置本地服务，例如数据库。在本部分中，您将更新文件`docker-compose.yaml`以定义数据库服务和用于保存数据的卷。此外，此特定应用程序使用系统属性来定义数据库类型，因此您需要更新以`Dockerfile`在启动应用程序时传入系统属性。

在克隆的存储库的目录中，`docker-compose.yaml`在 IDE 或文本编辑器中打开文件。`docker init`添加了一个示例数据库服务，但它需要针对您的独特应用程序进行一些更改。

在该`docker-compose.yaml`文件中，您需要执行以下操作：

- 取消注释所有数据库指令。现在您将使用数据库服务而不是本地存储来存储数据。
- 删除顶级`secrets`元素以及`db` 服务内的元素。此示例使用环境变量作为密码而不是机密。
- `user`从服务中删除元素`db`。此示例在环境变量中指定用户。
- 更新数据库环境变量。这些由 Postgres 镜像定义。有关更多详细信息，请参阅 [Postgres 官方 Docker 镜像](https://hub.docker.com/_/postgres)。
- 更新服务的健康检查测试`db`并指定用户。默认情况下，健康检查使用 root 用户，而不是`petclinic`您定义的用户。
- 将数据库 URL 添加为服务中的环境变量`server`。这将覆盖 中定义的默认值 `spring-petclinic/src/main/resources/application-postgres.properties`。

以下是更新后的`compose.yaml`文件。所有注释均已删除。

```yaml
services:
  server:
    build:
      context: ../java
    ports:
      - 8080:8080
    depends_on:
      db:
        condition: service_healthy
    environment:
      - POSTGRES_URL=jdbc:postgresql://db:5432/petclinic
  db:
    image: postgres
    restart: always
    volumes:
      - db-data://var/lib/postgresql/data
    environment:
      - POSTGRES_DB=petclinic
      - POSTGRES_USER=petclinic
      - POSTGRES_PASSWORD=petclinic
    ports:
      - 5432:5432
    healthcheck:
      test: [ "CMD", "pg_isready", "-U", "petclinic" ]
      interval: 10s
      timeout: 5s
      retries: 5
volumes:
  db-data:
```

`Dockerfile`在 IDE 或文本编辑器中打开。在`ENTRYPOINT`指令中，更新指令以传入 `spring-petclinic/src/resources/db/postgres/petclinic_db_setup_postgres.txt` 文件中指定的系统属性。

```diff
- ENTRYPOINT [ "java", "org.springframework.boot.loader.launch.JarLauncher" ]
+ ENTRYPOINT [ "java", "-Dspring.profiles.active=postgres", "org.springframework.boot.loader.launch.JarLauncher" ]
```

保存并关闭所有文件。

现在，运行以下`docker compose up`命令来启动您的应用程序。

```console
docker compose up --build
```

打开浏览器并通过 [http://localhost:8080](http://localhost:8080/)查看应用程序。您应该看到一个宠物诊所的简单应用程序。

在终端中，按`ctrl`+`c`停止应用程序。

## 用于开发的 Dockerfile

您现在拥有的 Dockerfile 非常适合小型、安全的生产映像，其中仅包含运行应用程序所需的组件。在开发时，您可能需要具有不同环境的其他映像。

例如，在开发图像中，您可能希望设置图像来启动应用程序，以便您可以将调试器连接到正在运行的 Java 进程。

您无需管理多个 Dockerfile，只需添加一个新阶段即可。然后，您的 Dockerfile 可以生成可用于生产的最终映像以及开发映像。

将 Dockerfile 的内容替换为以下内容。

```dockerfile
# syntax=docker/dockerfile:1

# https://docs.docker.com/reference/dockerfile/
# https://docs.docker.com/build/guide/multi-stage/

FROM maven:3-eclipse-temurin-21-alpine AS base
WORKDIR /build
COPY ./src src/
RUN sed -i -E "159a <mirror>\n<id>aliyun</id>\n<name>Aliyun Mirror</name>\n<url>http://maven.aliyun.com/nexus/content/groups/public/</url>\n<mirrorOf>central</mirrorOf>\n</mirror>" /usr/share/maven/conf/settings.xml

FROM base AS package
WORKDIR /build
RUN --mount=type=bind,source=pom.xml,target=pom.xml \
    --mount=type=cache,target=/root/.m2 \
    mvn package -DskipTests && \
    mv target/$(mvn help:evaluate -Dexpression=project.artifactId -q -DforceStdout)-$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout).jar target/app.jar

FROM package AS extract
WORKDIR /build
RUN java -Djarmode=layertools -jar target/app.jar extract --destination target/extracted

FROM eclipse-temurin:21-jre-jammy AS final
WORKDIR /app
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
USER appuser
COPY --from=extract /build/target/extracted/dependencies/ ./
COPY --from=extract /build/target/extracted/spring-boot-loader/ ./
COPY --from=extract /build/target/extracted/snapshot-dependencies/ ./
COPY --from=extract /build/target/extracted/application/ ./
EXPOSE 8080
ENTRYPOINT [ "java", "-Dspring.profiles.active=postgres", "org.springframework.boot.loader.launch.JarLauncher" ]
```

保存并关闭`Dockerfile`。

## 使用 Compose 进行本地开发

当前 Compose 文件无法启动您的开发容器。为此，您必须更新 Compose 文件以定位开发阶段。此外，更新服务器服务的端口映射以提供对调试器的访问权限。

`petclinic`在 IDE 或文本编辑器中 打开并创建一个名为 `docker-compose.dev.yml` 的新文件。

```yaml
services:
  server:
    build:
      context: tech
      target: development
    ports:
      - 8080:8080
      - 8000:8000
    depends_on:
      db:
        condition: service_healthy
    environment:
      - POSTGRES_URL=jdbc:postgresql://db:5432/petclinic
  db:
    image: postgres
    restart: always
    volumes:
      - db-data://var/lib/postgresql/data
    environment:
      - POSTGRES_DB=petclinic
      - POSTGRES_USER=petclinic
      - POSTGRES_PASSWORD=petclinic
    ports:
      - 5432:5432
    healthcheck:
      test: [ "CMD", "pg_isready", "-U", "petclinic" ]
      interval: 10s
      timeout: 5s
      retries: 5
volumes:
  db-data:
```

现在，启动您的应用程序并确认它正在运行。

```bash
docker compose up --build
```

最后，测试您的 API 端点。运行以下 curl 命令：

```bash
$ curl  --request GET \
  --url http://localhost:8080/vets \
  --header "content-type: application/json"
```

您应该收到以下回复：

```json
{"vetList":[{"id":1,"firstName":"James","lastName":"Carter","specialties":[],"nrOfSpecialties":0,"new":false},{"id":2,"firstName":"Helen","lastName":"Leary","specialties":[{"id":1,"name":"radiology","new":false}],"nrOfSpecialties":1,"new":false},{"id":3,"firstName":"Linda","lastName":"Douglas","specialties":[{"id":3,"name":"dentistry","new":false},{"id":2,"name":"surgery","new":false}],"nrOfSpecialties":2,"new":false},{"id":4,"firstName":"Rafael","lastName":"Ortega","specialties":[{"id":2,"name":"surgery","new":false}],"nrOfSpecialties":1,"new":false},{"id":5,"firstName":"Henry","lastName":"Stevens","specialties":[{"id":1,"name":"radiology","new":false}],"nrOfSpecialties":1,"new":false},{"id":6,"firstName":"Sharon","lastName":"Jenkins","specialties":[],"nrOfSpecialties":0,"new":false}]}
```

## 连接调试器

您将使用 IntelliJ IDEA 自带的调试器。您可以使用此 IDE 的社区版本。在 IntelliJ IDEA 中打开您的项目，转到**“运行”**菜单，然后**转到“编辑配置”**。添加类似于以下内容的新远程 JVM 调试配置：

![Java 连接调试器](docker-for-spring-boot/01.webp)

设置断点。

打开`src/main/java/org/springframework/samples/petclinic/vet/VetController.java`并在函数内部添加断点`showResourcesVetList`。

要启动调试会话，请选择**运行**菜单，然后**选择调试\*NameOfYourConfiguration\***。

![调试菜单](docker-for-spring-boot/02.webp)

您现在应该可以在 Compose 应用程序的日志中看到该连接。

![撰写日志文件](docker-for-spring-boot/03.webp)

您现在可以调用服务器端点。

```bash
curl --request GET --url http://localhost:8080/vets
```

您应该已经看到代码在标记的行上中断，现在您可以像平常一样使用调试器。您还可以检查和观察变量、设置条件断点、查看堆栈跟踪以及执行许多其他操作。

![调试器代码断点](docker-for-spring-boot/04.webp)

按下`ctrl+c`终端即可停止您的应用程序。

## 自动更新服务

使用 Compose Watch 可在您编辑和保存代码时自动更新正在运行的 Compose 服务。有关 Compose Watch 的更多详细信息，请参阅 [使用 Compose Watch](https://docs.docker.com/compose/file-watch/)。

在 IDE 或文本编辑器中打开您的`docker-compose.yaml`文件，然后添加 Compose Watch 指令。以下是更新后的`docker-compose.yaml` 文件。

```yaml
services:
  server:
    build:
      context: .
      target: development
    ports:
      - 8080:8080
      - 8000:8000
    depends_on:
      db:
        condition: service_healthy
    environment:
      - POSTGRES_URL=jdbc:postgresql://db:5432/petclinic
    develop:
      watch:
        - action: rebuild
          path: .
  db:
    image: postgres
    restart: always
    volumes:
      - db-data://var/lib/postgresql/data
    environment:
      - POSTGRES_DB=petclinic
      - POSTGRES_USER=petclinic
      - POSTGRES_PASSWORD=petclinic
    ports:
      - 5432:5432
    healthcheck:
      test: [ "CMD", "pg_isready", "-U", "petclinic" ]
      interval: 10s
      timeout: 5s
      retries: 5
volumes:
  db-data:
```

运行以下命令以使用 Compose Watch 运行您的应用程序。

```bash
docker compose watch
```

打开 Web 浏览器并通过 <http://localhost:8080> 查看应用程序 。您应该会看到 Spring Pet Clinic 主页。

现在，对本地计算机上应用程序源文件的任何更改都将自动反映在正在运行的容器中。

`spring-petclinic/src/main/resources/templates/fragments/layout.html`在 IDE 或文本编辑器中打开并`Home`通过添加感叹号来更新导航字符串。

```diff
-   <li th:replace="~{::menuItem ("/","home","home page","home","Home")}">
+   <li th:replace="~{::menuItem ("/","home","home page","home","Home!")}">
```

保存更改`layout.html`，然后您可以在容器自动重建时继续开发。

容器重建并运行后，刷新 [http://localhost:8080](http://localhost:8080/)，然后验证 **Home！**现在是否出现在菜单中。

按下`ctrl+c`终端即可停止 Compose Watch。

## 概括

在本部分中，您了解了如何在本地运行数据库并持久保存数据。您还创建了一个包含 JDK 的开发映像，并允许您附加调试器。最后，您设置了 Compose 文件以公开调试端口，并配置了 Compose Watch 以实时重新加载您的更改。

相关信息：

- [Compose file reference](https://docs.docker.com/compose/compose-file/)
- [Compose Watch](https://docs.docker.com/compose/file-watch/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)

# 运行 Java 测试

## 概述

测试是现代软件开发的重要组成部分。测试对不同的开发团队来说可能意味着很多事情。有单元测试、集成测试和端到端测试。在本指南中，您将了解如何在 Docker 中运行单元测试。

## 用于测试的多阶段 Dockerfile

在以下示例中，您将把测试命令拉入 Dockerfile。将 Dockerfile 的内容替换为以下内容。

```dockerfile
# syntax=docker/dockerfile:1

# https://docs.docker.com/reference/dockerfile/
# https://docs.docker.com/build/guide/multi-stage/

FROM maven:3-eclipse-temurin-21-alpine AS base
WORKDIR /build
COPY ./src src/
RUN sed -i -E "159a <mirror>\n<id>aliyun</id>\n<name>Aliyun Mirror</name>\n<url>http://maven.aliyun.com/nexus/content/groups/public/</url>\n<mirrorOf>central</mirrorOf>\n</mirror>" /usr/share/maven/conf/settings.xml

FROM base AS test
WORKDIR /build
RUN --mount=type=bind,source=pom.xml,target=pom.xml \
    --mount=type=cache,target=/root/.m2 \
    mvn test

FROM base AS package
WORKDIR /build
RUN --mount=type=bind,source=pom.xml,target=pom.xml \
    --mount=type=cache,target=/root/.m2 \
    mvn package -DskipTests && \
    mv target/$(mvn help:evaluate -Dexpression=project.artifactId -q -DforceStdout)-$(mvn help:evaluate -Dexpression=project.version -q -DforceStdout).jar target/app.jar

FROM package AS extract
WORKDIR /build
RUN java -Djarmode=layertools -jar target/app.jar extract --destination target/extracted

FROM extract AS development
WORKDIR /build
RUN cp -r /build/target/extracted/dependencies/. ./
RUN cp -r /build/target/extracted/spring-boot-loader/. ./
RUN cp -r /build/target/extracted/snapshot-dependencies/. ./
RUN cp -r /build/target/extracted/application/. ./
CMD [ "java", "-Dspring-boot.run.jvmArguments="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:8000"", "org.springframework.boot.loader.launch.JarLauncher" ]

FROM eclipse-temurin:21-jre-jammy AS final
WORKDIR /app
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
USER appuser
COPY --from=extract /build/target/extracted/dependencies/ ./
COPY --from=extract /build/target/extracted/spring-boot-loader/ ./
COPY --from=extract /build/target/extracted/snapshot-dependencies/ ./
COPY --from=extract /build/target/extracted/application/ ./
EXPOSE 8080
ENTRYPOINT [ "java", "-Dspring.profiles.active=postgres", "org.springframework.boot.loader.launch.JarLauncher" ]
```

现在，构建您的映像并运行测试。您将运行命令`docker build`并添加`--target test`标志，以便专门运行测试构建阶段。

```bash
docker build -t java-docker-image-test --progress=plain --no-cache --target=test .
```

您应该看到包含以下内容的输出

```console
...

#15 101.3 [WARNING] Tests run: 45, Failures: 0, Errors: 0, Skipped: 2
#15 101.3 [INFO]
#15 101.3 [INFO] ------------------------------------------------------------------------
#15 101.3 [INFO] BUILD SUCCESS
#15 101.3 [INFO] ------------------------------------------------------------------------
#15 101.3 [INFO] Total time:  01:39 min
#15 101.3 [INFO] Finished at: 2024-02-01T23:24:48Z
#15 101.3 [INFO] ------------------------------------------------------------------------
#15 DONE 101.4s
```

## 概括

在本节中，您学习了如何在构建图像时运行测试。

相关信息：

- [使用 Docker 指南进行构建](https://docs.docker.com/build/guide/)

# 为 Java 应用程序配置 CI/CD

## 先决条件

完成本指南的前面部分，从 [容器化您的应用](https://docs.docker.com/guides/java/containerize/)开始。您必须拥有 [GitHub](https://github.com/signup)帐户和 [Docker](https://hub.docker.com/signup)帐户才能完成此部分。

## 概述

在本部分中，您将了解如何设置和使用 GitHub Actions 构建 Docker 映像并将其推送到 Docker Hub。您将完成以下步骤：

1. 在 GitHub 上创建一个新的存储库。
2. 定义 GitHub Actions 工作流程。
3. 运行工作流程。

## 第一步：创建存储库

创建 GitHub 存储库，配置 Docker Hub 凭据并推送源代码。

1. 在 GitHub 上[创建一个新的存储库](https://github.com/new)。

2. 打开存储库**设置**，然后转到**机密和变量**> **操作**。

3. 创建一个名为的新**Repository 变量**`DOCKER_USERNAME`，并以您的 Docker ID 作为值。

4. 为 Docker Hub创建一个新的 [个人访问令牌 (PAT)](https://docs.docker.com/security/for-developers/access-tokens/#create-an-access-token)。您可以将此令牌命名为  `docker-tutorial` 。确保访问权限包括读取和写入。

5. 将 PAT 作为**存储库机密**添加到您的 GitHub 存储库中，名称为 `DOCKER_TOKEN`。

6. 在您机器上的本地存储库中，运行以下命令将源更改为您刚刚创建的存储库。确保更改 `your-username`为您的 GitHub 用户名和`your-repository`您创建的存储库的名称。

   ```bash
   git remote set-url origin https://github.com/your-username/your-repository.git
   ```

7. 运行以下命令将本地存储库暂存、提交并推送到 GitHub。

   ```bash
   git add -A
   git commit -m "my commit"
   git push -u origin main
   ```

## 第二步：设置工作流程

设置 GitHub Actions 工作流程以构建、测试和将映像推送到 Docker Hub。

1. 转到 GitHub 上的存储库，然后选择“操作”选项卡。该项目已经具有`maven-build`使用 Maven 构建和测试 Java 应用程序的工作流程。如果需要，您可以选择禁用此工作流程，因为您不会在本指南中使用它。您将创建一个新的替代工作流程来构建、测试和推送您的映像。

2. 选择**新工作流程**。

3. 选择**自己设置工作流程**。

   `.github/workflows/docker`默认情况下，这将带您进入一个在存储库中创建新的 GitHub 操作工作流文件的页面。

4. 在编辑器窗口中，复制并粘贴以下 YAML 配置。

   ```yaml
   # https://github.com/docker/metadata-action
   
   name: Build Docker Image
   
   on:
     push:
       branches: [ "main" ]
       tags: ["spring-boot", "java", "backend", "tutorial", "docker", "kubernetes", "security", "javascript"]
     release:
       types: [ created ]
   
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - name: Docker meta
           id: meta
           uses: docker/metadata-action@v5
           with:
             images: |
               ${{ secrets.DOCKER_USERNAME }}/${{ github.event.repository.name }}
             tags: |
               type=ref,event=tag
               type=semver,pattern={{version}}
               type=semver,pattern={{major}}.{{minor}}
               type=semver,pattern={{major}}
               type=raw,latest
   
         - name: Set up Docker Buildx
           uses: docker/setup-buildx-action@v3
   
         - name: Set up QEMU
           uses: docker/setup-qemu-action@v3
   
         - name: Set up Docker Buildx
           uses: docker/setup-buildx-action@v3
   
         - name: Login to Docker Hub
           if: github.event_name != "pull_request"
           uses: docker/login-action@v3
           with:
             username: ${{ secrets.DOCKER_USERNAME }}
             password: ${{ secrets.DOCKER_TOKEN }}
   
         - name: Build and push
           uses: docker/build-push-action@v6
           with:
             file: Dockerfile
             platforms: linux/amd64,linux/arm64
             target: final
             tags: ${{ steps.meta.outputs.tags }}
             push: ${{ github.event_name != "pull_request" }}
             labels: ${{ steps.meta.outputs.labels }}
   ```

   有关的 YAML 语法的更多信息`docker/build-push-action`，请参阅 [GitHub Action README](https://github.com/docker/build-push-action/blob/master/README.md)。

## 第三步：运行工作流程

保存工作流文件并运行作业。

1. 选择**提交更改...**并将更改推送到`main`分支。

   推送提交后，工作流程将自动启动。

2. 转到**“操作”**选项卡。它显示工作流程。

   选择工作流程可以显示所有步骤的细目。

3. 工作流程完成后，转到 [Docker Hub 上的存储库](https://hub.docker.com/repositories)。

   如果您在该列表中看到新的存储库，则表示 GitHub Actions 已成功将映像推送到 Docker Hub。

## 概括

在本节中，您学习了如何为您的应用程序设置 GitHub Actions 工作流程。

相关信息：

- [GitHub Actions 简介](https://docs.docker.com/build/ci/github-actions/)
- [GitHub Actions 的工作流程语法](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

# 测试 Kubernetes 部署

## 先决条件

- 完成本指南前面的所有部分，从 [“容器化你的应用”](https://docs.docker.com/guides/java/containerize/)开始。
- 在 Docker Desktop 中[打开 Kubernetes](https://docs.docker.com/desktop/kubernetes/#install-and-turn-on-kubernetes)。

## 概述

在本部分中，您将了解如何使用 Docker Desktop 将应用程序部署到开发机器上功能齐全的 Kubernetes 环境。这样，您可以在部署之前在本地测试和调试 Kubernetes 上的工作负载。

## 创建 Kubernetes YAML 文件

在您的`spring-petclinic`目录中，创建一个名为 的文件 `docker-java-kubernetes.yaml`。在 IDE 或文本编辑器中打开该文件并添加以下内容。将其替换为您的 Docker 用户名和您在[为 Java 应用程序配置 CI/CD](https://docs.docker.com/guides/java/configure-ci-cd/)`DOCKER_USERNAME/REPO_NAME`中创建的存储库的名称 。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docker-java-demo
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      service: server
  template:
    metadata:
      labels:
        service: server
    spec:
      containers:
       - name: server-service
         image: DOCKER_USERNAME/REPO_NAME
         imagePullPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: service-entrypoint
  namespace: default
spec:
  type: NodePort
  selector:
    service: server
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30001
```

在此 Kubernetes YAML 文件中，有两个对象，由以下字符分隔`---`：

- 部署，描述一组可扩展的相同 Pod。在这种情况下，您将只获得一个副本或 Pod 的副本。该 Pod（如下所述）中只有一个容器。该容器是根据 GitHub Actions 在[为 Java 应用程序配置 CI/CD](https://docs.docker.com/guides/java/configure-ci-cd/)`template`中构建的映像创建的 。
- NodePort 服务会将流量从主机上的端口 30001 路由到其路由到的 pod 内的端口 8080，从而允许您从网络访问您的应用程序。

要了解有关 Kubernetes 对象的更多信息，请参阅 [Kubernetes 文档](https://kubernetes.io/docs/home/)。

## 部署并检查您的应用程序

1. 在终端中，导航到 Kubernetes`spring-petclinic`并将其部署到 Kubernetes。

   ```console
   kubectl apply -f docker-java-kubernetes.yaml
   ```

   您应该看到如下所示的输出，表明您的 Kubernetes 对象已成功创建。

   ```shell
   deployment.apps/docker-java-demo created
   service/service-entrypoint created
   ```

2. 通过列出您的部署来确保一切正常。

   ```bash
   kubectl get deployments
   ```

   您的部署应列出如下：

   ```shell
   NAME                 READY   UP-TO-DATE   AVAILABLE   AGE
   docker-java-demo     1/1     1            1           15s
   ```

   这表明您在 YAML 中请求的所有 pod 均已启动并正在运行。对您的服务执行相同的检查。

   ```bash
   kubectl get services
   ```

   您应该获得如下输出。

   ```shell
   NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
   kubernetes           ClusterIP   10.96.0.1       <none>        443/TCP          23h
   service-entrypoint   NodePort    10.99.128.230   <none>        8080:30001/TCP   75s
   ```

   除了默认`kubernetes`服务之外，您还可以看到您的`service-entrypoint`服务在端口 30001/TCP 上接受流量。

3. 在终端中，curl 服务。请注意，此示例中未部署数据库。

   ```bash
   $ curl --request GET \
     --url http://localhost:30001/actuator/health \
     --header "content-type: application/json"
   ```

   您应该获得如下输出。

   ```json
   {"status":"UP","groups":["liveness","readiness"]}
   ```

4. 运行以下命令来关闭您的应用程序。

   ```bash
   kubectl delete -f docker-java-kubernetes.yaml
   ```

## 概括

在本节中，您学习了如何使用 Docker Desktop 将应用程序部署到开发机器上功能齐全的 Kubernetes 环境。

相关信息：

- [Kubernetes 文档](https://kubernetes.io/docs/home/)
- [使用 Docker Desktop 在 Kubernetes 上部署](https://docs.docker.com/desktop/kubernetes/)
- [Swarm 模式概述](https://docs.docker.com/engine/swarm/)

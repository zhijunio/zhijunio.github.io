---
title: "Maven 站点发布到 GitHub Pages 完整教程"
date: 2024-07-18 08:00:00+08:00
slug: publishing-a-maven-site-to-github-pages
categories: [ "tech" ]
tags: [ "maven", "github" ]
description: "记录如何将 Maven 生成的站点发布到 GitHub Pages，包括项目创建、站点生成和发布流程配置。"
---

本文源代码：[https://github.com/zhijunio/maven-site-github-example/](https://github.com/zhijunio/maven-site-github-example/) 。

## 创建 Java Maven 项目

让我们使用 Maven 创建一个简单的 Java 项目

```bash
mvn archetype:generate \
    -DgroupId=com.mycompany.app \
    -DartifactId=maven-site-github-example \
    -DarchetypeArtifactId=maven-archetype-quickstart \
    -DarchetypeVersion=1.4 \
    -DinteractiveMode=false
```

这将创建包含 Maven 项目的*my-app*文件夹。让我们进入该文件夹并确保它编译正常：

```bash
cd maven-site-github-example
mvn clean verify
```

我们还可以生成该项目的站点：

```bash
mvn clean site
```

*该站点将在target/site*文件夹中生成，可以使用浏览器打开；例如，让我们打开它的 *index.html*：

```bash
chrome target/site/index.html
```

![maven-my-app-index](publishing-a-maven-site-to-github-pages/01.webp)

## 创建 github 项目

在你的 github 上创建一个项目 maven-site-github-example，然后在本地的 maven-site-github-example 目录提交代码：

```bash
echo "# maven-site-github-example" >> README.md
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:zhijunio/maven-site-github-example.git
git push -u origin main
```

## GitHub Page 设置

现在我们必须在 Git 存储库上创建 **gh-pages**分支。

```bash
git checkout --orphan gh-pages 
rm .git/index ; git clean -fdx 
echo "It works" > index.html 
git add . && git commit -m "initial site content" && git push origin gh-pages 
```

相应的网站将发布在你的 GitHub 项目的相应 URL 中；访问地址：<https://zhijunio.github.io/maven-site-github-example：>

![maven-my-app-github-page-index](publishing-a-maven-site-to-github-pages/02.webp)

现在我们可以回到 **主**分支：

```bash
git checkout main
```

## Maven POM 配置

让我们看看如何配置我们的 POM 以自动将 Maven 站点发布到 GitHub 页面。

在 pluginManagement 部分中添加 maven-scm-publish-plugin：

```xml
<build>
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-scm-publish-plugin</artifactId>
                <version>3.0.0</version>
                <configuration>
                    <scmBranch>gh-pages</scmBranch>
                   <tryUpdate>true</tryUpdate>
                </configuration>
            </plugin>
        </plugins>
    </pluginManagement>
</build>
```

maven-scm-publish-plugin 插件需要以下参数，参考 <https://maven.apache.org/plugins/maven-scm-publish-plugin/publish-scm-mojo.html：>

- **tryUpdate**： 参数用于指定是否尝试更新源代码管理（SCM）提供商中的项目文件。

  > 当你运行 `mvn scm-publish:publish-scm` 命令来发布 Maven 项目时，插件会检查 SCM 提供商中的项目文件是否与本地生成的网站内容一致。如果存在差异，插件默认情况下会拒绝发布，并显示错误消息。
  >
  > 通过将 `tryUpdate` 参数设置为 `true`，你可以告诉插件尝试更新 SCM 提供商中的项目文件，以使其与本地生成的网站内容保持一致。如果更新成功，插件将继续发布网站。否则，插件将显示错误消息。
  >
  > 以下是使用 `tryUpdate` 参数的示例命令：
  >
  > ```bash
  > mvn scm-publish:publish-scm -Dscmpublish.tryUpdate=true
  > ```
  >
  > 请注意，使用 `tryUpdate` 参数时，插件将直接修改 SCM 提供商中的项目文件。因此，在使用此参数之前，请确保你对 SCM 提供商中的项目文件进行了适当的备份，并且了解潜在的风险。

- **pubScmUrl**：必须，用于指定发布到源代码管理（SCM）提供商的网站的URL。

  - 格式：`scm:<scm_provider><delimiter><provider_specific_part>`
  - 默认值：`${project.distributionManagement.site.url}`，可以通过 `scmpublish.pubScmUrl` 属性设置。

- **scmBranch**：非必须，scm分支用于指定源代码管理（SCM）分支的名称。例如：对应 github，应该是 gh-pages

  - 没有默认值，可以通过 `scmpublish.scm.branch` 设置

- **serverId**：非必须，是 Maven 中用于标识服务器配置的标识符

  - 默认值：`${project.distributionManagement.site.id}`，可以通过 `scmpublish.serverId` 属性设置。

  >下面是一个示例的服务器配置段落：
  >
  >```xml
  ><settings>
  >  <servers>
  >    <server>
  >      <id>my-server</id>
  >      <username>my-username</username>
  >      <password>my-password</password>
  >    </server>
  >    <!-- Additional server configurations -->
  >  </servers>
  >  <!-- Other Maven settings -->
  ></settings>
  >```
  >
  >在上述示例中，`my-server` 是 `serverId`，用于标识服务器配置。你可以根据需要添加多个服务器配置，每个配置都应该有唯一的 `serverId`。
  >
  >当你在 Maven 项目中引用这些服务器配置时，可以使用相应的 `serverId` 来指定要应用的服务器配置。
  >
  >例如，当你需要在 Maven 项目中使用某个服务器配置时，可以在项目的 `pom.xml` 文件中配置如下：
  >
  >```xml
  ><project>
  >  <!-- Other project configurations -->
  >
  >  <build>
  >    <plugins>
  >      <plugin>
  >        <groupId>...</groupId>
  >        <artifactId>...</artifactId>
  >        <configuration>
  >          <serverId>my-server</serverId>
  >          <!-- Other plugin configurations -->
  >        </configuration>
  >      </plugin>
  >    </plugins>
  >  </build>
  >
  >  <!-- Other project configurations -->
  ></project>
  >```
  >
  >在上述示例中，`<serverId>my-server</serverId>` 指定了要应用的服务器配置。这样，Maven 在构建过程中将使用相应的服务器配置。
  >
  >请注意，`serverId` 的值必须与 `settings.xml` 文件中配置的服务器配置的 `id` 保持一致。

- **username**：非必须，SCM 用户名
  - 默认从 serverId 指定的 settings.xml 中的 username 读取，可以通过 `username` 设置
- **password**：非必须，SCM 密码
  - 默认从 serverId 指定的 settings.xml 中的 password 读取，可以通过 `password` 设置

从上面的参数说明，可以看出：

- maven-scm-publish-plugin 插件优先读取 `project.distributionManagement.site` 节点，所以可以在 pom.xml 中配置一个 site 节点，比如：

  ```xml
  <distributionManagement>
      <site>
          <id>github</id>
          <url>scm:git:git@github.com:zhijunio/maven-site-github-example.git</url>
      </site>
  </distributionManagement>
  ```

- 其次，读取 `scmpublish.serverId` 属性，然后去 settings.xml 中获取 username 和密码，这时候需要配置 settings.xml：

  ```xml
  <servers>
      <server>
          <id>github</id>
          <username>zhijunio</username>
          <password>ghp_XXXXXXXXXXXXXXXXXX</password>
      </server>
  </servers>
  ```

## 发布网站

在配置了 `project.distributionManagement.site` 之后，将 Maven 站点发布到 GitHub 页面只需运行以下命令：

```bash
mvn clean site scm-publish:publish-scm
```

- `clean`：删除 target 目录

- `site`：命令用于生成 Maven 项目的网站

- `scm-publish:publish-scm`：用于将 Maven 项目发布到源代码管理（SCM）提供商

  >要使用 `mvn scm-publish:publish-scm` 命令发布 Maven 项目，请按照以下步骤进行操作：
  >
  >1. 确保你的 Maven 项目已经配置了适当的 SCM 插件，以便与你使用的源代码管理系统进行集成。在项目的 `pom.xml` 文件中，你需要添加 SCM 配置，包括 SCM URL、连接信息和凭据等。例如，对于 Git，你可以添加以下配置：
  >
  > ```xml
  > <scm>
  >   <connection>scm:git:git@github.com:<username>/<repository>.git</connection>
  >   <developerConnection>scm:git:git@github.com:<username>/<repository>.git</developerConnection>
  >   <url>https://github.com/<username>/<repository></url>
  > </scm>
  >   ```
  >
  > 请将 `<username>` 替换为你的 GitHub 用户名，`<repository>` 替换为你的仓库名称。
  >
  >1. 打开终端或命令提示符。
  >
  >2. 使用 `cd` 命令导航到 Maven 项目的根目录。
  >
  >3. 运行以下命令：
  >
  > ```bash
  > mvn scm-publish:publish-scm
  >   ```
  >
  > Maven 将执行 SCM Publish 插件，将项目发布到指定的 SCM 提供商。

从日志可以看出 git 推送提交的命令：`"git" "push" "git@github.com:zhijunio/maven-site-github-example.git" "refs/heads/gh-pages:refs/heads/gh-pages"`

```bash
[INFO] Executing: /bin/sh -c cd "/Users/zhijunio/Codes/github/maven-site-github-example/target/scmpublish-checkout" && "git" "push" "git@github.com:zhijunio/maven-site-github-example.git" "refs/heads/gh-pages:refs/heads/gh-pages"
[INFO] Working directory: /Users/zhijunio/Codes/github/maven-site-github-example/target/scmpublish-checkout
[INFO] Checked in 24 file(s) to revision null in 0 h 0 m 4 s
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  21.115 s
[INFO] Finished at: 2024-07-18T10:25:58+08:00
[INFO] ------------------------------------------------------------------------
```

这里使用的是通过 ssh 协议提交，能够提交成功，是因为我已将本地的 ssh 公钥配置到 [github](https://github.com/settings/keys)。

现在该网站位于 GitHub Pages 上：

![maven-my-app-github-index](publishing-a-maven-site-to-github-pages/03.webp)

如果不配置  `project.distributionManagement.site` ，注释 distributionManagement 节点，这需要配置 scmpublish.pubScmUrl，可以在 pom.xml 中设置：

```xml
<properties>
  <scmpublish.content>${project.reporting.outputDirectory}</scmpublish.content>
  <scmpublish.pubScmUrl>scm:git:git@github.com:zhijunio/maven-site-github-example.git</scmpublish.pubScmUrl>
  <scmpublish.scm.branch>gh-pages</scmpublish.scm.branch>
</properties>

<!--    <distributionManagement>-->
<!--        <site>-->
<!--            <id>github</id>-->
<!--            <url>scm:git:git@github.com:zhijunio/maven-site-github-example.git</url>-->
<!--        </site>-->
<!--    </distributionManagement>-->
```

再次运行：

```bash
mvn clean site scm-publish:publish-scm
```

## 美化网站

使用 [maven-archetype-site](https://maven.apache.org/archetypes/maven-archetype-site/) 美化网站：

```bash
mvn archetype:generate \
    -DgroupId=com.mycompany.app \
    -DartifactId=maven-site-github-example \
    -DarchetypeGroupId=org.apache.maven.archetypes \
    -DarchetypeArtifactId=maven-archetype-site \
    -DarchetypeVersion=1.4 \
    -DinteractiveMode=false
```

执行成功之后，src 目录下新增了一个 site 目录，并且POM中添加了 maven-project-info-reports-plugin 和 i18n 本地化的一些配置。

```xml
<build>
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-scm-publish-plugin</artifactId>
                <version>3.0.0</version>
                <configuration>
                    <scmBranch>gh-pages</scmBranch>
                </configuration>
            </plugin>
        </plugins>
    </pluginManagement>

    <plugins>
        <plugin>
            <artifactId>maven-site-plugin</artifactId>
            <configuration>
                <locales>en,fr</locales>
            </configuration>
        </plugin>
    </plugins>
</build>

<reporting>
    <plugins>
        <plugin>
            <artifactId>maven-project-info-reports-plugin</artifactId>
        </plugin>
    </plugins>
</reporting>
```

此外，最终网站将使用新皮肤 maven-fluido-skin。src/site/site.xml 内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>

<project name="${artifactId}"
  xmlns="http://maven.apache.org/DECORATION/1.8.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/DECORATION/1.8.0 http://maven.apache.org/xsd/decoration-1.8.0.xsd">
  <bannerLeft>
    <name>${artifactId}</name>
    <src>https://maven.apache.org/images/apache-maven-project.webp</src>
    <href>https://www.apache.org/</href>
  </bannerLeft>

  <bannerRight>
    <src>https://maven.apache.org/images/maven-logo-black-on-white.webp</src>
    <href>https://maven.apache.org/</href>
  </bannerRight>

  <skin>
    <groupId>org.apache.maven.skins</groupId>
    <artifactId>maven-fluido-skin</artifactId>
    <version>1.7</version>
  </skin>

  <body>
    <links>
      <item name="Apache" href="http://www.apache.org/" />
      <item name="Maven" href="https://maven.apache.org/"/>
    </links>

    <menu name="Examples">
      <item name="APT Format" href="format.html"/>
      <item name="FAQ" href="faq.html"/>
      <item name="Markdown Example" href="markdown.html"/>
      <item name="Markdown with Velocity Example" href="markdown-velocity.html"/>
      <item name="Xdoc Example" href="xdoc.html"/>
    </menu>

    <menu ref="reports" />
  </body>
</project>
```

让我们再次运行以下命令来发布新网站：

```bash
mvn clean site scm-publish:publish-scm
```

稍等片刻，等待 github page 部署成功之后，可以看到网站：

![maven-my-app-github-skin-index](publishing-a-maven-site-to-github-pages/04.webp)

可以在 <https://github.com/zhijunio/maven-site-github-example/actions> 查看网站的部署：

![maven-my-app-github-page-deploy](publishing-a-maven-site-to-github-pages/05.webp)

现在，可以通过添加/更改/删除目录 src/site 的内容，然后通过 Maven 再次发布该网站。

例如，删除 src/site/apt/index.apt，添加  src/site/apt/index.md.vm ，引入项目中 README.md 内容作为网站首页内容：

```markdown
#include("/README.md")
```

## Github Action配置

修改 Aciton 的 Workflow  权限，选中 `Read and write permissions`。

创建 .github/workflows 目录，并在该目录创建 site.yml：

```bash
name: Publish Site with Maven

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        java: [ "8" ]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Java ${{ matrix.Java }}
        uses: actions/setup-java@v4
        with:
          distribution: "temurin"
          java-version: ${{ matrix.java }}
          cache: maven
          server-id: github
          server-username: GITHUB_ACTOR
          server-password: GITHUB_TOKEN

      - name: Publish site to github pages
        run: |
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git config --global user.name "github-actions[bot]"
          mvn -ntp -B -U clean site scm-publish:publish-scm -Dscmpublish.serverId=github
        env:
          GITHUB_ACTOR: ${{ secrets.GITHUB_ACTOR }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

在 github action 中，需要设置 github 的 username 和 password 用于提交代码带 gh-pages 分支，所以需要设置 scmpublish.serverId 并且删除 distributionManagement 下的 site 配置：

```bash
mvn --ntp --batch-mode --update-snapshots clean site scm-publish:publish-scm -Dscmpublish.serverId=github
```

server-id 相关信息可以在 actions/setup-java@v4 中设置，参考 [actions/setup-java](https://github.com/actions/setup-java?tab=readme-ov-file#maven-options) 的文档：

```bash
      - name: Java ${{ matrix.Java }}
        uses: actions/setup-java@v4
        with:
          distribution: "temurin"
          java-version: ${{ matrix.java }}
          cache: maven
          server-id: github
          server-username: GITHUB_ACTOR
          server-password: GITHUB_TOKEN
```

- server-username：从环境变量 GITHUB_ACTOR 中读取值，故 在 Publish site to github pages 步骤里面需要设置 env 环境变量：`GITHUB_ACTOR: ${{ secrets.GITHUB_ACTOR }}`
- server-password：从环境变量 GITHUB_TOKEN 中读取值，故 在 Publish site to github pages 步骤里面需要设置 env 环境变量：`GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`

另外，git 提交代码时，需要设置用户名和邮箱：

```bash
git config --global user.email "github-actions[bot]@users.noreply.github.com"
git config --global user.name "github-actions[bot]"
```

提交代码之后，Github Action 可以看到一个部署，稍等片刻，部署失败：

```bash
[INFO] --- maven-clean-plugin:2.5:clean (default-clean) @ maven-site-github-example ---
[INFO] 
[INFO] --- maven-site-plugin:3.3:site (default-site) @ maven-site-github-example ---
Warning:  Report plugin org.apache.maven.plugins:maven-project-info-reports-plugin has an empty version.
Warning:  
Warning:  It is highly recommended to fix these problems because they threaten the stability of your build.
Warning:  
Warning:  For this reason, future Maven versions might no longer support building such malformed projects.
[INFO] configuring report plugin org.apache.maven.plugins:maven-project-info-reports-plugin:3.6.2
Warning:  Error injecting: org.apache.maven.report.projectinfo.CiManagementReport
java.lang.NoClassDefFoundError: org/apache/maven/doxia/siterenderer/DocumentContent
```

从日志可以看到 maven-clean-plugin 版本是 2.5，maven-site-plugin 版本是 3.3 ，maven-project-info-reports-plugin 版本是 3.6.2

修改 pom.xml ，给 maven-site-plugin 设置版本为 4.0.0-M15：

```xml
<plugin>
    <artifactId>maven-site-plugin</artifactId>
    <version>4.0.0-M15</version>
    <configuration>
        <locales>default,en,fr</locales>
    </configuration>
</plugin>
```

再次提交代码，发现 Github action 还是运行失败，异常日志：

```bash
[INFO] Executing: /bin/sh -c cd "/home/runner/work/maven-site-github-example/maven-site-github-example/target" && "git" "clone" "--branch" "gh-pages" "git@github.com:zhijunio/maven-site-github-example.git" "/home/runner/work/maven-site-github-example/maven-site-github-example/target/scmpublish-checkout"
[INFO] Working directory: /home/runner/work/maven-site-github-example/maven-site-github-example/target
Error:  Failed to check out from SCM: The git-clone command failed. Cloning into "/home/runner/work/maven-site-github-example/maven-site-github-example/target/scmpublish-checkout"...
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

从日志可以看到 git 从 `git@github.com:zhijunio/maven-site-github-example.git`下载代码，没有权限，原因是没有配置 ssh。故需要修改  scmpublish.pubScmUrl 为 https 协议，将 `<scmpublish.pubScmUrl>scm:git:git@github.com:zhijunio/maven-site-github-example.git</scmpublish.pubScmUrl>`改为：

```xml
<scmpublish.pubScmUrl>scm:git:https://github.com/zhijunio/maven-site-github-example.git</scmpublish.pubScmUrl>
```

再次提交代码，action 运行成功。

再次打开网站，发现存在 I18N 没有替换成功的问题。

![maven-my-app-github-i18n-index](publishing-a-maven-site-to-github-pages/06.webp)

解决办法：

- 修改 src/site/site.xml 和 src/site/site_fr.xml 文件中 maven-fluido-skin 的版本为当前最新版本：2.0.0-M9

  ```xml
  <skin>
      <groupId>org.apache.maven.skins</groupId>
      <artifactId>maven-fluido-skin</artifactId>
      <version>2.0.0-M9</version>
  </skin>
  ```

- 修改 src/site/site.xml 和 src/site/site_fr.xml 文件中 `${artifactId}` 为 `${this.artifactId}`

  ```xml
  <bannerLeft>
      <name>${this.artifactId}</name>
      <src>https://maven.apache.org/images/apache-maven-project.webp</src>
      <href>https://www.apache.org/</href>
  </bannerLeft>
  ```
  
再次发布并打开网站，则正常显示：

![maven-my-app-github-i18n-index-ok](publishing-a-maven-site-to-github-pages/07.webp)

---
title: "GitHub Action 发布 Jar 到 Maven 中央仓库"
date: 2024-08-01 08:00:00+08:00
slug: publishing-a-jar-to-maven-repository-with-github-action
categories: [ "tech" ]
tags: ["github","maven"]
description: "介绍如何通过 GitHub Action 自动发布 Jar 包到 Maven 中央仓库，减少手工发布流程并提升发布效率。"
---

作为一名 Java 开发者,将自己的项目发布到 Maven 中央仓库是一个非常重要的步骤。这不仅可以让更多的开发者发现和使用您的项目,也可以提高项目的知名度和影响力。

<!--more-->

在过去，发布 Jar 到 Maven 中央仓库通常需要手动完成一系列繁琐的步骤，比如：申请 JIRA 账号、创建 Sonatype JIRA Issure、上传 Jar 包、签名 Jar 包等。但是随着 Github Action 的出现，这个过程变得更加自动化和简单。

下面我将以一个简单的 Maven 项目为例，介绍如何使用 Github Action 实现自动发布 Jar 到 Maven 中央仓库。

## 前提条件

1. 在 Github 创建一个 Maven 项目
2. 安装 gpg 并创建 gpg 秘钥和公钥，参考 [How to Publish Artifacts to Maven Central](https://dzone.com/articles/how-to-publish-artifacts-to-maven-central)
3. 创建 OSSRH 账号，参考 [Generate a Token on OSSRH Sonatype Nexus Repository Manager servers](https://central.sonatype.org/publish/generate-token/#generate-a-token-on-ossrh-sonatype-nexus-repository-manager-servers)

## 创建 Maven 项目

首先在Github上面创建项目：[https://github.com/zhijunio/maven-hello-world](https://github.com/zhijunio/maven-hello-world)

增加两个 Maven 插件：

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-gpg-plugin</artifactId>
  <version>3.2.2</version>
  <executions>
    <execution>
      <goals>
        <goal>sign</goal>
      </goals>
      <phase>verify</phase>
    </execution>
  </executions>
</plugin>
<plugin>
  <groupId>org.sonatype.plugins</groupId>
  <artifactId>nexus-staging-maven-plugin</artifactId>
  <version>1.7.0</version>
  <extensions>true</extensions>
  <configuration>
    <serverId>ossrh</serverId>
    <nexusUrl>https://s01.oss.sonatype.org/</nexusUrl>
    <autoReleaseAfterClose>true</autoReleaseAfterClose>
    <keepStagingRepositoryOnCloseRuleFailure>false</keepStagingRepositoryOnCloseRuleFailure>
  </configuration>
</plugin>
```

可以将上面的两个插件加入到 pom.xml 的 build 节点下面，也可以配置到 profile 节点下。[https://github.com/zhijunio/maven-hello-world](https://github.com/zhijunio/maven-hello-world) 项目中使用的是第二种方式，具体见 <https://github.com/zhijunio/chensoul-parent> 的 pom.xml 文件。

```xml
<profiles>
    <profile>
      <id>release</id>
      <build>
        <plugins>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-source-plugin</artifactId>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-javadoc-plugin</artifactId>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-enforcer-plugin</artifactId>
          </plugin>
          <plugin>
            <groupId>pl.project13.maven</groupId>
            <artifactId>git-commit-id-plugin</artifactId>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-release-plugin</artifactId>
            <version>${maven-release-plugin.version}</version>
            <configuration>
              <scmCommentPrefix>[CI Skip]</scmCommentPrefix>
              <autoVersionSubmodules>true</autoVersionSubmodules>
              <useReleaseProfile>false</useReleaseProfile>
              <releaseProfiles>release</releaseProfiles>
              <goals>deploy</goals>
            </configuration>
          </plugin>
          <!-- https://blog.sonatype.com/2010/01/how-to-generate-pgp-signatures-with-maven/ -->
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-gpg-plugin</artifactId>
            <version>${maven-gpg-plugin.version}</version>
            <executions>
              <execution>
                <goals>
                  <goal>sign</goal>
                </goals>
                <phase>verify</phase>
              </execution>
            </executions>
          </plugin>
          <plugin>
            <groupId>org.sonatype.plugins</groupId>
            <artifactId>nexus-staging-maven-plugin</artifactId>
            <version>${nexus-staging-maven-plugin.version}</version>
            <extensions>true</extensions>
            <configuration>
              <serverId>ossrh</serverId>
              <nexusUrl>https://s01.oss.sonatype.org/</nexusUrl>
              <autoReleaseAfterClose>true</autoReleaseAfterClose>
              <keepStagingRepositoryOnCloseRuleFailure>false</keepStagingRepositoryOnCloseRuleFailure>
            </configuration>
          </plugin>
        </plugins>
      </build>
    </profile>
  
  </profiles>
```

nexus-staging-maven-plugin 插件配置的 serverId 是 ossrh ，需要和 distributionManagement 中的配置一致：

```xml
<distributionManagement>
  <snapshotRepository>
    <id>ossrh</id>
    <url>https://s01.oss.sonatype.org/content/repositories/snapshots</url>
  </snapshotRepository>
  <repository>
    <id>ossrh</id>
    <url>https://s01.oss.sonatype.org/service/local/staging/deploy/maven2/</url>
  </repository>
</distributionManagement>
```

您需要在 [Sonatype JIRA](https://issues.sonatype.org/secure/Dashboard.jspa) 上注册一个帐户并为此创建一个[Issure](https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134)。

将您的 Sonatype JIRA 凭证添加到您的`~/.m2/settings.xml`文件中，如下所示：

```xml
<server>
  <id>ossrh</id>
  <username>LSJkOqOi</username>
  <password>3oJOIO5+ah7LIcRSmDC2YDGjE9PRbgxoE2UbXjOrSzC1</password>
</server>
```

## 安装 GPG 并创建公秘钥

macos 上安装 gpg：

```bash
brew install gpg
```

参考 [Generating a Key Pair](https://central.sonatype.org/publish/requirements/gpg/#generating-a-key-pair) 生成 GPG 密钥。

```bash
$ gpg --gen-key
gpg (GnuPG) 2.4.5; Copyright (C) 2024 g10 Code GmbH
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

注意：使用 “gpg --full-generate-key” 以获得一个全功能的密钥生成对话框。

GnuPG 需要构建用户标识以辨认您的密钥。

真实姓名： chensoul
电子邮件地址： zhijun.lab@gmail.com
您选定了此用户标识：
    “chensoul <zhijun.lab@gmail.com>”
```

按提示输入两次密码，这里我使用 chensoul 作为密码 。

查看生成的 key：

```bash
# gpg --list-secret-keys --keyid-format=long
[keyboxd]
---------
sec   ed25519/93C5993B9F7B43EE 2024-05-08 [SC] [有效至：2027-05-08]
      C83119F1B90238633D766D4B93C5993B9F7B43EE
uid                   [ 绝对 ] chensoul <zhijun.lab@gmail.com>
ssb   cv25519/116B95FF0068A7E8 2024-05-08 [E] [有效至：2027-05-08]
```

上传公开的 key：

```bash
# keyserver.ubuntu.com
# keys.openpgp.org
# pgp.mit.edu
gpg --keyserver keys.openpgp.org --send-keys C83119F1B90238633D766D4B93C5993B9F7B43EE
```

修改 `~/.m2/settings.xml` 文件，添加：

```xml
<server>
    <id>gpg.passphrase</id>
    <passphrase><PASSPHRASE_GPG></passphrase>
</server>
```

将 `<PASSPHRASE_GPG>` 替换为创建 gpg key 时设置的密码。

## 使用 Maven 发布 jar

使用下面命令发布 jar 到 sonatype 仓库：

```bash
mvn -P release clean deploy

mvn -P release clean deploy
```

如果当前项目的版本为快照版，则发布后的 jar 在 [https://s01.oss.sonatype.org/content/repositories/snapshots/com/chensoul/maven-hello-world/](https://s01.oss.sonatype.org/content/repositories/snapshots/com/chensoul/maven-hello-world/)

如果当前项目的版本为正式版，稍等几分钟，可以在以下仓库查看发布的 jar:

- <https://central.sonatype.com/artifact/com.chensoul/maven-hello-world>
- <https://s01.oss.sonatype.org/service/local/repositories/releases/content/com/chensoul/maven-hello-world>
- <https://repo.maven.apache.org/maven2/com/chensoul/maven-hello-world>

## 配置Github Actions

使用 Github Actions 发布 jar 到 maven 仓库，目前发现有两个 action 可以实现该目的：

- [actions/setup-java](https://github.com/actions/setup-java)

- [qcastel/github-actions-maven-release](https://github.com/qcastel/github-actions-maven-release)

- [action-maven-publish](https://github.com/marketplace/actions/action-maven-publish)

### actions/setup-java

使用 [actions/setup-java](https://github.com/actions/setup-java) ，参考使用文档，在项目的 .github/workflows 目录下创建 maven-release.yml文件：

```yaml
name: Maven Release

on:
  push:
    branches: [ "main" ]
    tags: ["java", "backend", "tutorial", "redis", "docker", "javascript", "git", "maven"]
  release:
    types: [ created ]

jobs:
  build:
    runs-on: ubuntu-latest
    if: "!contains(github.event.head_commit.message, "[CI Skip]")"

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK 8
        uses: actions/setup-java@v4
        with:
          distribution: "temurin"
          java-version: 8
          cache: maven
          server-id: ossrh # Value of the distributionManagement/repository/id field of the pom.xml
          server-username: MAVEN_USERNAME # 变量
          server-password: MAVEN_TOKEN # 变量
          gpg-passphrase: GPG_PASSPHRASE # 变量
          gpg-private-key: ${{ secrets.MAVEN_GPG_PRIVATE_KEY }}

      - name: Java Maven Release
        run: mvn -ntp -B -U clean deploy -P release -DskipTests
        env:
          MAVEN_USERNAME: ${{ secrets.OSSRH_USERNAME }}
          MAVEN_TOKEN: ${{ secrets.OSSRH_TOKEN }}
          GPG_PASSPHRASE: ${{ secrets.MAVEN_GPG_PASSPHRASE }}
```

根据上面的 yaml 文件，需要在当前项目的 Settings-->Secrets-->Actions 创建以下 Secrets：

- **OSSRH_TOKEN**：您在 Sonatype 上的密码
- **OSSRH_USERNAME**：您在 Sonatype 上的用户名
- **MAVEN_GPG_PRIVATE_KEY**：用于签名 Jar 包的 GPG 密钥
- **MAVEN_GPG_PASSPHRASE**：用于签名的 GPG 密钥密码

**MAVEN_GPG_PRIVATE_KEY** 通过如下命令获取：

```bash
$ gpg --list-keys
[keyboxd]
---------
pub   ed25519 2024-05-08 [SC] [有效至：2027-05-08]
      C83119F1B90238633D766D4B93C5993B9F7B43EE
uid             [ 绝对 ] chensoul <zhijun.lab@gmail.com>
sub   cv25519 2024-05-08 [E] [有效至：2027-05-08]


$ gpg --armor --export-secret-keys C83119F1B90238633D766D4B93C5993B9F7B43EE
-----BEGIN PGP PRIVATE KEY BLOCK-----

lIYEZjrnpBYJKwYBBAHaRw8BAQdAmMtUf7k2poUBYhlca7U7le2vGPEHgAtHZ1MH
DGOSZR3+BwMCiYrT2G14W736nwBjZvOLsJKjxsSqVN9bRLATEg3veHW/59Jw4DaI
QN5DX8ier7D2rXM9fkJfYyLg3wNVAcT7dmcQOVM5wkgL1B7EEz3/aLQeY2hlbnNv
dWwgPGljaGVuc291bEBnbWFpbC5jb20+iJkEExYKAEEWIQTIMRnxuQI4Yz12bUuT
xZk7n3tD7gUCZjrnpAIbAwUJBaOagAULCQgHAgIiAgYVCgkICwIEFgIDAQIeBwIX
gAAKCRCTxZk7n3tD7sgGAQCBRsbdVDn1NuVYXOPEAKAFUFWgowb0tkH7w5VzWWD2
hwD+IHR5JiegnI376upOLiUzQ5cZN8gJ3fn0oau5ELp1lQSciwRmOuekEgorBgEE
AZdVAQUBAQdAnfkcIuOOyU+ihUX/Z8nU9634MbTG0OHfEZCbm9pgdH4DAQgH/gcD
AqPKEqB6fGQq+u4+7gYGW2vgkeiTjWJCwVw8VJEwn53+gdQ0q7irfnOOqYNXJbye
n2NM9IucSZpcVk8gKhJmc8hJR4uNifh0i820vEjyszeIfgQYFgoAJhYhBMgxGfG5
AjhjPXZtS5PFmTufe0PuBQJmOuekAhsMBQkFo5qAAAoJEJPFmTufe0PubSkA/R6I
/7+oavy/FP9r6PfV1oI5yiAy7RMue1BuIcbRMoabAPkBBQq/ms9DZ5GA25ZpSuOH
S3ee7QZPNjtkA2s/eQsPAQ==
```

### qcastel/github-actions-maven-release

使用 [qcastel/github-actions-maven-release](https://github.com/qcastel/github-actions-maven-release) ，参考使用文档，在项目的 .github/workflows 目录下创建 maven-release.yml文件：

```yaml
name: Maven Release

on:
  push:
    branches: [ "main" ]
    tags: ["java", "backend", "tutorial", "redis", "docker", "javascript", "git", "maven"]
  release:
    types: [ created ]

jobs:
  build:
    runs-on: ubuntu-latest
    if: "!contains(github.event.head_commit.message, "[CI Skip]")"

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Java Maven Release
        uses: qcastel/github-actions-maven-release@master
        env:
          JAVA_HOME: /usr/lib/jvm/java-1.8-openjdk/
        with:
          git-release-bot-name: "release-bot"
          git-release-bot-email: "release-bot@chensoul.cc"
          release-branch-name: "main"
  
          maven-args: "-ntp -B -U -P release"
          maven-servers: ${{ secrets.MVN_REPO_SERVERS }}
  
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
  
          gpg-enabled: true
          gpg-key-id: ${{ secrets.MAVEN_GPG_ID }}
          gpg-key: ${{ secrets.MAVEN_GPG_KEY }}
          gpg-passphrase: ${{ secrets.MAVEN_GPG_PASSPHRASE }}
```

根据上面的 yaml 文件，需要在当前项目的 Settings-->Secrets-->Actions 创建以下 Secrets：

- **MVN_REPO_SERVERS**
- **SSH_PRIVATE_KEY**
- **MAVEN_GPG_ID**
- **MAVEN_GPG_KEY**
- **MAVEN_GPG_PASSPHRASE**

**MVN_REPO_SERVERS** 如下：

```bash
[
  {
    "id": "ossrh",
    "username": "LSJkOqOi",
    "password": "3oJOIO5+ah7LIcRSmDC2YDGjE9PRbgxoE2UbXjOrSzC1"
  },
  {
    "id": "gpg.passphrase",
    "passphrase": "chensoul"
  }
]
```

**SSH_PRIVATE_KEY** 通过下面命令获取：

1、在 docker 容器中生成

```bash
docker run -it qcastel/maven-release:latest  bash
```

 ssh 公钥和秘钥

```bash
ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""

echo -e "Copy the following SSH private key and add it to your repo secrets under the name "SSH_PRIVATE_KEY":"
base64 ~/.ssh/id_rsa

echo -e " "

echo -e "Copy the encoded SSH public key and add it as one of your repo deploy keys with write access:"
cat ~/.ssh/id_rsa.pub
```

输出内容如下：

```bash
Copy the following SSH private key and add it to your repo secrets under the name "SSH_PRIVATE_KEY":
LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFB QUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUJGd0FBQUFkemMyZ3RjbgpOaEFBQUFB d0VBQVFBQUFRRUExQUFBclFpZFNRS25pY3g5VmNaQVdtTlI1ZWY0Q2tSbEJCZTdVdk5QNGNMMlAv eDRReXJpCmdWcGV2Um8wVHE0eUptWFN2L3hnclByNk5CQmk0STlXRmp6Q2l0a3phcTg3OGwyNVdt UUt5cTUyang5TWJ0MmhCZzVrdUsKZ05pRGxvMWNaY1VpZHd4ak9sNzVlVHpWaHpoSGZ4ZnphZTZY N0QybE1jeFUrd2d3MFJHZlpITjUvRUZWQ3JHRUhKdHlGSQpReFd1VDY0c3RNMElrVjA3azBPRlQy SHhYNlB6OUpvRjhRRm9SZmVjU0RUM2tPRk5rTVVicDVTNkkxNWxtTjB0YnNHVGNsClYxWFpwWUkr NHRFWWphN1EwWnlWaVBCVUJnWnBuUlpQNFRmOEIwRzhsVDdqSlNPWDM0YkRFWkFoMVM4bnRCQzc3 aFUyMUIKWGJDZHV6ZlpXUUFBQThoN29jU3VlNkhFcmdBQUFBZHpjMmd0Y25OaEFBQUJBUURVQUFD dENKMUpBcWVKekgxVnhrQmFZMQpIbDUvZ0tSR1VFRjd0UzgwL2h3dlkvL0hoREt1S0JXbDY5R2pS T3JqSW1aZEsvL0dDcyt2bzBFR0xnajFZV1BNS0syVE5xCnJ6dnlYYmxhWkFyS3JuYVBIMHh1M2FF R0RtUzRxQTJJT1dqVnhseFNKM0RHTTZYdmw1UE5XSE9FZC9GL05wN3Bmc1BhVXgKekZUN0NERFJF WjlrYzNuOFFWVUtzWVFjbTNJVWhERmE1UHJpeTB6UWlSWFR1VFE0VlBZZkZmby9QMG1nWHhBV2hG OTV4SQpOUGVRNFUyUXhSdW5sTG9qWG1XWTNTMXV3Wk55VlhWZG1sZ2o3aTBSaU5ydERSbkpXSThG UUdCbW1kRmsvaE4vd0hRYnlWClB1TWxJNWZmaHNNUmtDSFZMeWUwRUx2dUZUYlVGZHNKMjdOOWxa QUFBQUF3RUFBUUFBQVFCSzBqMXExSEYraFJ0UVBRVzMKTWlNZ1E1RnlETzZ6NFBPdUFCb3k2b0Mw OHpRcDNSY3N6WVBubDFkOGNqVW4xNzhIWWtTQlViZGxGYWNjblBQb3dXM21wMApjWjdoS0JncHNy clB4djlJTUNpWlI2YXRkMUFXK0ZUYXNxcU5VdDBPVTVIYXNUcTZ2WHAvN1drcTZ0ZUp3OGtvQi9I MjN5CmhyVGs1eFJ1WnZPckxGcS9vdXBQeXhVS1M0SzRVOG5JYjBnZjVjT3RXeUlWZFdKQ05EdU9R ZW1sdDBRajN3RjZPWkNpcU8KRGxaMFd3MWwrRzJpUWZFLzM2ODR0UXpKemVKeFgybEJaN0tmQStP bEcyZENPeXZwY01Ic1J4TE5ITy85aWpqUmNXWUVtMgp4SDVYQmRkZldlKzBkYkxxZFhoWHJHTnpx QjlSbjBTWGZ1QVRnSzZENjBsSkFBQUFnUUN6VmhONUh1YXVvOExzVVR1dkNRCkNibVhnakhuS1hB NDBqV1pyVmlucEgvbmcxNkNudlE5UmJhb041am1JWURUZEJ3TVp4dXZSck9JUTloeUZnUDVCSHRL dTgKQlhvZ08ybERySDFVRzA4bzN6ZHNhUTJaaGp0aEE5TFlMcXpvYkVtSEpndkwxemJjRVBWMHJC cm1SMXArL0trN3Y5OHd0eQpPT2VnYXVqK0djUXdBQUFJRUE5ZklKc0t2SGdsQVp1eS9sMzJWS3Q4 cTN4UFl4SUlrMVJKczV4bDRJUGFTZ0xsR0pzVFgwCll2bll1THcrb2NCMlVaazRxUUlML3I5bTRt cVhEOTF6bXhxZTNUKzZqOHk0ODBvbS91UWRma3h6MWdNWkljdDlkR2Z3RE8KczRBckNPSkx0TVI4 WG53emxXM1VLZnJhTDFRUFZMVUs3OWpSM29kN2k2VmNWMlpnY0FBQUNCQU55cXRMZk85NUhkU3Mz RwpyMWYvOStVRUJjV0xMSnpHMEl2OEZtd3J6ci9ZbksrbXpmR2dMVHNPeUgwV1pMZkVnYlJkUGxC aVJmTjFXQk1oWHZKRWhaCkp4YTY1N0IxTUExano1eEE2OElCcEJxUlhvNWZ6QmdHNFg0UGVNZkQz dXR5M0NENVR4Y2sxL0c1L2krUXpXNFhlR2RLNkkKaml1OGg5TXo3YkUxZHUyZkFBQUFFWEp2YjNS QVlqa3dZelJtWWpKbE9HVmxBUT09Ci0tLS0tRU5EIE9QRU5TU0ggUFJJVkFURSBLRVktLS0tLQo=

Copy the encoded SSH public key and add it as one of your repo deploy keys with write access:
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDUAACtCJ1JAqeJzH1VxkBaY1Hl5/gKRGUEF7tS80/hwvY/HhDKuKBWl69GjROrjImZdK/GCs+vo0EGLgj1YWPMKK2TNqrzvyXblaZArKrnaPH0xu3aEGDmS4qA2IOWjVxlxSJ3DGM6Xvl5PNWHOEd/F/Np7pfsPaUxzFT7CDDREZ9kc3n8QVUKsYQcm3IUhDFa5Priy0zQiRXTuTQ4VPYfFfo/P0mgXxAWhF95xINPeQ4U2QxRunlLojXmWY3S1uwZNyVXVdmlgj7i0RiNrtDRnJWI8FQGBmmdFk/hN/wHQbyVPuMlI5ffhsMRkCHVLye0ELvuFTbUFdsJ27N9lZ root@b90c4fb2e8ee
```

2、或者直接使用本地的 ssh

macos 系统上执行命令：

```bash
echo -e "Copy the following SSH private key and add it to your repo secrets under the name "SSH_PRIVATE_KEY":"
base64 -i ~/.ssh/id_rsa

echo -e " "

echo -e "Copy the encoded SSH public key and add it as one of your repo deploy keys with write access:"
cat ~/.ssh/id_rsa.pub
```

将私钥粘贴到 Secrets 中 **SSH_PRIVATE_KEY** 的值内，将公钥添加到你的 github 账号的 [SSH keys](https://github.com/settings/ssh/new) 中。

获取 **MAVEN_GPG_ID**：

```bash
$ gpg --list-secret-keys --keyid-format LONG
[keyboxd]
---------
sec   ed25519/93C5993B9F7B43EE 2024-05-08 [SC] [有效至：2027-05-08]
      C83119F1B90238633D766D4B93C5993B9F7B43EE
uid                   [ 绝对 ] chensoul <zhijun.lab@gmail.com>
ssb   cv25519/116B95FF0068A7E8 2024-05-08 [E] [有效至：2027-05-08]
```

> 这里 **MAVEN_GPG_ID** 对应 93C5993B9F7B43EE

获取 **MAVEN_GPG_KEY**，运行下面命令，输入密码，即 **MAVEN_GPG_PASSPHRASE** 对应的内容

```bash
echo "Public key to add in your bot github account:"
gpg --armor --export 93C5993B9F7B43EE

echo "Private key to add to the CI secrets under GITHUB_GPG_KEY:"
gpg --export-secret-keys --armor 93C5993B9F7B43EE | base64
```

输出内容：

公钥：

```bash
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEZjrnpBYJKwYBBAHaRw8BAQdAmMtUf7k2poUBYhlca7U7le2vGPEHgAtHZ1MH
DGOSZR20HmNoZW5zb3VsIDxpY2hlbnNvdWxAZ21haWwuY29tPoiZBBMWCgBBFiEE
yDEZ8bkCOGM9dm1Lk8WZO597Q+4FAmY656QCGwMFCQWjmoAFCwkIBwICIgIGFQoJ
CAsCBBYCAwECHgcCF4AACgkQk8WZO597Q+7IBgEAgUbG3VQ59TblWFzjxACgBVBV
oKMG9LZB+8OVc1lg9ocA/iB0eSYnoJyN++rqTi4lM0OXGTfICd359KGruRC6dZUE
uDgEZjrnpBIKKwYBBAGXVQEFAQEHQJ35HCLjjslPooVF/2fJ1Pet+DG0xtDh3xGQ
m5vaYHR+AwEIB4h+BBgWCgAmFiEEyDEZ8bkCOGM9dm1Lk8WZO597Q+4FAmY656QC
GwwFCQWjmoAACgkQk8WZO597Q+5tKQD9Hoj/v6hq/L8U/2vo99XWgjnKIDLtEy57
UG4hxtEyhpsA+QEFCr+az0NnkYDblmlK44dLd57tBk82O2QDaz95Cw8B
=YFZg
-----END PGP PUBLIC KEY BLOCK-----
```

私钥：

```bash
LS0tLS1CRUdJTiBQR1AgUFJJVkFURSBLRVkgQkxPQ0stLS0tLQoKbElZRVpqcm5wQllKS3dZQkJBSGFSdzhCQVFkQW1NdFVmN2sycG9VQllobGNhN1U3bGUydkdQRUhnQXRIWjFNSApER09TWlIzK0J3TUNwOTJOaVVIQnU0VDZ3UHRFSWt1cGtTM2M0c21WOWZUUXRtRDM3bTJuOTlzbnRWNmllYU8vCi9TKzUvR2FyWDNMTUhoTmtkdnVpOHZSMk1hNDNhNFdzVmFpR1RiZWF6eHNHbVE1TGo4ZXUvTFFlWTJobGJuTnYKZFd3Z1BHbGphR1Z1YzI5MWJFQm5iV0ZwYkM1amIyMCtpSmtFRXhZS0FFRVdJUVRJTVJueHVRSTRZejEyYlV1VAp4Wms3bjN0RDdnVUNaanJucEFJYkF3VUpCYU9hZ0FVTENRZ0hBZ0lpQWdZVkNna0lDd0lFRmdJREFRSWVCd0lYCmdBQUtDUkNUeFprN24zdEQ3c2dHQVFDQlJzYmRWRG4xTnVWWVhPUEVBS0FGVUZXZ293YjB0a0g3dzVWeldXRDIKaHdEK0lIUjVKaWVnbkkzNzZ1cE9MaVV6UTVjWk44Z0ozZm4wb2F1NUVMcDFsUVNjaXdSbU91ZWtFZ29yQmdFRQpBWmRWQVFVQkFRZEFuZmtjSXVPT3lVK2loVVgvWjhuVTk2MzRNYlRHME9IZkVaQ2JtOXBnZEg0REFRZ0gvZ2NECkFtYllUMStNNjB6bStna1lyMk54Yys1U3hqYmd6bTA1ajFURW42TnUwVTUyUmRoMzJvTVRYU2ZIa2RlakdiVmkKMDNKemRkVnZ6Kzl6U2FzQVpMMVA1ZytBa0dGbTBHYVFLTldnOUVRQzVBK0lmZ1FZRmdvQUpoWWhCTWd4R2ZHNQpBamhqUFhadFM1UEZtVHVmZTBQdUJRSm1PdWVrQWhzTUJRa0ZvNXFBQUFvSkVKUEZtVHVmZTBQdWJTa0EvUjZJCi83K29hdnkvRlA5cjZQZl
```

将上面输出私钥的内容添加到 Secrets 中 **MAVEN_GPG_KEY** 的值里面，将公钥内容添加到你的 github 账号的 [GPG keys](https://github.com/settings/gpg/new) 中。

修改代码，提交到 github，会触发一个 github action ，查看日志，可以看到：

```bash
Not using access token authentication, as no access token (via env GITREPO_ACCESS_TOKEN) defined or because an SSH key is defined and setup (via env SSH_PRIVATE_KEY)
Do mvn release:prepare with options  -DdevelopmentVersion=${parsedVersion.majorVersion}.${parsedVersion.minorVersion}.${parsedVersion.nextIncrementalVersion}-SNAPSHOT and arguments -ntp -B -U -P release
```

从日志可以看到，qcastel/github-actions-maven-release 使用了 maven 的 maven-release-plugin 插件，会发布正式版的 jar 到 maven 中央仓库。为了 避免在开发阶段每次提交都发布一个正式版本到中央仓库，可以修改 release-branch-name 为 release 分支，即限定提交到指定分支时候，从触发 maven 发布。

可以添加下面参数，跳过 release:perform ，即不会发布 jar 到 maven 中央仓库，**但是 maven-release-plugin 插件还是会修改项目的版本，并创建 tag。**

```bash
with:
    skip-perform: true
```

创建的 tag 名称格式为：项目名称-版本。tag 名称格式可以在 maven-release-plugin 插件中配置：

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-release-plugin</artifactId>
  <version>${maven-release-plugin.version}</version>
  <configuration>
    <scmCommentPrefix>[CI Skip]</scmCommentPrefix>
    <autoVersionSubmodules>true</autoVersionSubmodules>
    <useReleaseProfile>false</useReleaseProfile>
    <releaseProfiles>release</releaseProfiles>
    <tagNameFormat>v@{version}</tagNameFormat>
    <goals>deploy</goals>
  </configuration>
</plugin>
```

### action-maven-publish

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:

  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 8
      uses: actions/setup-java@v4
      with:
        java-version: "8"
        distribution: "temurin"
        
    - name: Build with Maven
      run: mvn clean install
        
    - name: Publish to Maven Central
      uses: samuelmeuli/action-maven-publish@v1
      with:
        gpg_private_key: ${{ secrets.MAVEN_GPG_PRIVATE_KEY }}
        gpg_passphrase: ${{ secrets.MAVEN_GPG_PASSPHRASE }}
        nexus_username: ${{ secrets.OSSRH_USERNAME }}
        nexus_password: ${{ secrets.OSSRH_TOKEN }}
```

## 总结

如果使用 [qcastel/github-actions-maven-release](https://github.com/qcastel/github-actions-maven-release) ，maven-release-plugin 插件会修改版本，并且创建 tag ，但是并不会创建 github release。

使用 <https://github.com/release-drafter/release-drafter> 这个 actions 可以更加 pull request 自动创建 github releae，基于此，更倾向于使用 [actions/setup-java](https://github.com/actions/setup-java) 来发布 jar 到 Maven 仓库。

---
title: "搭建本地 Maven 仓库：Artifactory 开源版安装部署"
date: 2024-06-25 08:00:00+08:00
slug: install-artifactory-oss
tags: [ "maven" ]
description: "介绍 Artifactory 开源版的安装与部署方式，适合作为搭建本地 Maven 仓库和制品管理服务的入门参考。"
---

## 安装 Artifactory

官方下载安装地址：[https://jfrog.com/community/download-artifactory-oss/](https://jfrog.com/community/download-artifactory-oss/) ，支持三种安装方式：

- Windows Installer
- Linux Installers
  - tar.gz
  - RPM
  - Debian
  - Docker Compose
  - Docker
- Helm

### 手动下载并安装

安装包文件地址在 [https://releases.jfrog.io/artifactory/bintray-artifactory/org/artifactory/oss/jfrog-artifactory-oss/](https://releases.jfrog.io/artifactory/bintray-artifactory/org/artifactory/oss/jfrog-artifactory-oss/) 。以当前最新版本 7.84.15 为例，在 linux 服务器上下载：

```bash
wget https://releases.jfrog.io/artifactory/bintray-artifactory/org/artifactory/oss/jfrog-artifactory-oss/7.84.15/jfrog-artifactory-oss-7.84.15-linux.tar.gz

 tar -zxvf jfrog-artifactory-oss-7.84.15-linux.tar.gz
 cd jfrog-artifactory-oss-7.84.15/app/bin
 nohup ./artifactory.sh 
```

### 通过 docker 安装

设置 JFROG_HOME 并创建目录：

```bash
export JFROG_HOME=~/.jfrog
mkdir -p $JFROG_HOME/artifactory/var/etc/

sudo chown -R 1030:1030 $JFROG_HOME/artifactory/var
sudo chmod -R 777 $JFROG_HOME/artifactory/var

touch $JFROG_HOME/artifactory/var/etc/system.yaml
```

配置数据库。参考 [JFrog Recommends Using PostgreSQL](https://jfrog.com/help/r/jfrog-installation-setup-documentation/database-configuration) ，Artifactory 7.84.7 之后，默认使用 postgresql 数据库。

```bash
cat <<EOF > $JFROG_HOME/artifactory/var/etc/system.yaml
shared:
    database:
        type: postgresql
        driver: org.postgresql.Driver
        url: jdbc:postgresql://192.168.2.39:5432/artifactory
        username: artifactory
        password: password
EOF
```

如果需要使用其他数据库，需要修改配置文件，并添加 jdbc 驱动。例如，使用 mysql 数据库：

```bash
cat <<EOF > $JFROG_HOME/artifactory/var/etc/system.yaml
shared:
    database:
        allowNonPostgresql: true
        type: mysql
        driver: com.mysql.jdbc.Driver
        url: "jdbc:mysql://192.168.2.214:3306/artifactory?characterEncoding=UTF-8&elideSetAutoCommits=true&useSSL=false"
        username: artifactory
        password: password
EOF
```

> 注意：
>
> - 在 mysql 数据库创建 artifactory 数据库，并设置用户名和密码：artifactory/password。
>
>   ```sql
>   CREATE USER "artifactory"@"%" IDENTIFIED BY "password";
>   GRANT all ON *.* TO "artifactory"@"%";
>   ```
>
> - 使用 mysql 数据库，需要下载 mysql 驱动
>
>   ```bash
>   mkdir -p $JFROG_HOME/artifactory/var/bootstrap/artifactory/tomcat/lib
>         
>   wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.49/mysql-connector-java-5.1.49.jar -P $JFROG_HOME/artifactory/var/bootstrap/artifactory/tomcat/lib
>   ```

下载镜像并运行容器：

```bash
docker run --name artifactory-oss -v $JFROG_HOME/artifactory/var/://var/opt/jfrog/artifactory -d -p 8081:8081 -p 8082:8082 releases-docker.jfrog.io/jfrog/artifactory-pro:7.84.15
```

查看日志，稍等片刻，可以看到应用启动成功：

```bash
docker logs -f artifactory-oss
```

卸载：

```bash
docker rm -f artifactory-oss
rm -rf ~/.jfrog
```

### 通过 docker-compose 安装

这里使用 postgresql 数据库：

```yaml
services:
    postgres:
        image: postgres:15.6-alpine
        container_name: postgresql
        environment:
            - POSTGRES_DB=artifactory
            - POSTGRES_USER=artifactory
            - POSTGRES_PASSWORD=password
        ports:
            - "5432:5432"
        volumes:
            - postgres_data://var/lib/postgresql/data
            - /etc/localtime://etc/localtime:ro

    artifactory-oss:
        image: releases-docker.jfrog.io/jfrog/artifactory-oss:7.84.15
        environment:
            - JF_SHARED_DATABASE_TYPE=postgresql
            # The following must match the POSTGRES_USER and POSTGRES_PASSWORD values passed to PostgreSQL
            - JF_SHARED_DATABASE_USERNAME=artifactory
            - JF_SHARED_DATABASE_PASSWORD=password
            - JF_SHARED_DATABASE_URL=jdbc:postgresql://postgresql:5432/artifactory
            - JF_SHARED_DATABASE_DRIVER=org.postgresql.Driver
        ports:
            - "8081:8081"
            - "8082:8082"
        volumes:
            - artifactory_data://var/opt/jfrog/artifactory
            - /etc/localtime://etc/localtime:ro
```

## 访问 artifactory

通过浏览器访问 <http://127.0.0.1:8082> ，用户名和密码为：admin/password 。

登录成功之后：

- 1、提示修改密码（必须）。密码改为 Admin123.
- 2、设置项目访问地址（可选）。例如：<http://127.0.0.1:8082> ，或者 <http://artifactory.local。如果设置了域名，则需要配反向代理，将域名代理到> 127.0.0.1:8082

- 3、设置默认代理（可选）。
- 4、创建仓库（可选）。选择 Maven

## 创建本地仓库、远程仓库、虚拟仓库

### 创建本地仓库

artifactory 默认有两个本地仓库，可以不用再创建本地仓库。

- libs-release-local
- libs-snapshot-local

如果还想创建本地仓库，步骤如下：

1. 点击  "Create a Repository" --> "Add Repositories" --> "Local Repository"
2. 包类型选择 maven。
3. 填入仓库Key。

### 创建远程仓库

1. 点击  "Create a Repository" --> "Add Repositories" --> "Remote Repository"

2. 包类型选择 maven
3. 填入仓库Key。例如：jcenter
4. URL 填入：https://*jcenter*.bintray.com/

### 创建虚拟仓库

artifactory 默认创建了两个虚拟仓库：libs-release 和 libs-snapshot，可以直接编辑将新创建的远程仓库 jcenter 加入他们。

也可以创建新的虚拟仓库，步骤如下：

1. 点击  "Create a Repository" --> "Add Repositories" --> "Virtual Repository"

2. 包类型选择 maven
3. 填入仓库Key。例如：libs-virtual
4. 将本地仓库 libs-release-local 和远程仓库 jcenter、maven-remote 加入到我们创建的虚拟仓库中，同时设置Default Deployment Repositor为我们的本地仓库 libs-release-local

## Maven 配置

### 设置 settings.xml 文件

点击"菜单" --> “Artifactory” --> "Artifacts" --> “libs-release” --> “Set Me Up”， 选择Repository 为libs-release， 在configure中输入密码，点击 "    Generate Token & Create Instructions" 生成 Token。

点击"Generate Settings" 生成 settings.xml 文件，下载该文件，并修改 username 为 admin ，修改 password 为生成的 token。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0 http://maven.apache.org/xsd/settings-1.2.0.xsd" xmlns="http://maven.apache.org/SETTINGS/1.2.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <servers>
    <server>
      <username>admin</username>
      <password>XXXXXXXXXX</password>
      <id>central</id>
    </server>
    <server>
      <username>admin</username>
      <password>XXXXXXXXXXX</password>
      <id>snapshots</id>
    </server>
  </servers>
  
  <profiles>
    <profile>
      <repositories>
        <repository>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
          <id>central</id>
          <name>libs-release</name>
          <url>http://127.0.0.1:8081/artifactory/libs-release</url>
        </repository>
        <repository>
          <snapshots />
          <id>snapshots</id>
          <name>libs-snapshot</name>
          <url>http://127.0.0.1:8081/artifactory/libs-snapshot</url>
        </repository>
      </repositories>
      <pluginRepositories>
        <pluginRepository>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
          <id>central</id>
          <name>libs-release</name>
          <url>http://127.0.0.1:8081/artifactory/libs-release</url>
        </pluginRepository>
        <pluginRepository>
          <snapshots />
          <id>snapshots</id>
          <name>libs-snapshot</name>
          <url>http://127.0.0.1:8081/artifactory/libs-snapshot</url>
        </pluginRepository>
      </pluginRepositories>
      <id>artifactory</id>
    </profile>
  </profiles>
  <activeProfiles>
    <activeProfile>artifactory</activeProfile>
  </activeProfiles>
</settings>
```

将该文件放置到 MAVEN 的安装目录下面。

找一个 maven 项目，运行 mvn clean package 命令，可以发现 maven 会从artifactory 服务器中拉取依赖。

默认情况，从 artifactory 下载 jar 文件是需要 用户名和密码的，例如，通过 wget 下载文件，会提示需要登录。这时候，需要指定用户名和密码。

如果不想使用用户名和密码的话，也可以在 Adminstration --> User Management --> Settings 中设置允许匿名用户访问。

### 设置 pom.xml 文件

打开上面步骤中使用过得Set Me Up 界面，选择Deploy ，我们只需要在自己的项目pom文件中加入下面的设置之后，我们就可以直接使用`mvn deploy` 想打包好的jar文件发布到artifactory的本地仓库中。

```xml
<distributionManagement>
    <repository>
        <id>central</id>
        <name>c42aa455c510-releases</name>
        <url>http://127.0.0.1:8081/artifactory/libs-release</url>
    </repository>
    <snapshotRepository>
        <id>snapshots</id>
        <name>c42aa455c510-snapshots</name>
        <url>http://127.0.0.1:8081/artifactory/libs-snapshot</url>
    </snapshotRepository>
</distributionManagement>
```

说明：

- repository 和 snapshotRepository 的 ID 节点的值需要和 settings.xml 文件中相对应。
- repository 和 snapshotRepository 的 ID 节点的值可以为任意值。

也可以将上面配置放到 settigns.xml 文件中：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0 http://maven.apache.org/xsd/settings-1.2.0.xsd" xmlns="http://maven.apache.org/SETTINGS/1.2.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <servers>
    <server>
      <username>admin</username>
      <password>XXXXXXXXXXXXX</password>
      <id>central</id>
    </server>
    <server>
      <username>admin</username>
      <password>XXXXXXXXXXXXXX</password>
      <id>snapshots</id>
    </server>
  </servers>
  
  <profiles>
    <profile>
      <properties>
          <altReleaseDeploymentRepository>
              central::http://127.0.0.1:8081/artifactory/libs-release
          </altReleaseDeploymentRepository>
          <altSnapshotDeploymentRepository>
              snapshots::http://127.0.0.1:8081/artifactory/libs-snapshot
          </altSnapshotDeploymentRepository>
      </properties>
      
      <repositories>
        <repository>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
          <id>central</id>
          <name>libs-release</name>
          <url>http://127.0.0.1:8081/artifactory/libs-release</url>
        </repository>
        <repository>
          <snapshots />
          <id>snapshots</id>
          <name>libs-snapshot</name>
          <url>http://127.0.0.1:8081/artifactory/libs-snapshot</url>
        </repository>
      </repositories>
      <pluginRepositories>
        <pluginRepository>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
          <id>central</id>
          <name>libs-release</name>
          <url>http://127.0.0.1:8081/artifactory/libs-release</url>
        </pluginRepository>
        <pluginRepository>
          <snapshots />
          <id>snapshots</id>
          <name>libs-snapshot</name>
          <url>http://127.0.0.1:8081/artifactory/libs-snapshot</url>
        </pluginRepository>
      </pluginRepositories>
      <id>artifactory</id>
    </profile>
  </profiles>
  <activeProfiles>
    <activeProfile>artifactory</activeProfile>
  </activeProfiles>
</settings>
```

## 参考文章

- [手把手教你用artifactory搭建maven私有仓库](https://blog.csdn.net/u013515980/article/details/120927392)
- [JFrog Artifactory 和 Maven 包类型](https://medium.com/@vniranjan251203/jfrog-artifactory-and-maven-package-type-2fe0af1765b0)
- [Artifactory Jfrog与Nexus](https://blog.csdn.net/jianghuafeng0/article/details/109518353)

- [从 Nexus 迁移到 JFrog Artifactory](https://blog.csdn.net/2301_76601027/article/details/130646586)
- [如何从Nexus迁移到Artifactory](https://cloud.tencent.com/developer/article/1616310?from=15425)

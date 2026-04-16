---
title: "Jenkins 安装与部署指南：使用 Docker"
date: 2024-06-26 09:00:00+08:00
slug: install-jenkins
categories: [ "tech" ]
tags: [ "docker" ]
description: "记录使用 Docker 安装和启动 Jenkins 的基本步骤，包括数据卷、容器运行参数和首次启动初始化说明。"
---

## 使用 Docker 安装

```bash
docker volume create --name jenkins_data

docker run -p 8080:8080 -p 50000:50000 -v jenkins_data://var/jenkins_home jenkins/jenkins:jdk21
```

第一次启动 Jenkins 时，Docker 日志将包含如下消息：

```bash
Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

1883c809f01b4ed585fb5c3e0156543a

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword
```

那串随机的数字和字母是初始管理员密码，这是完成 Jenkins 配置所必需的。

## 使用 Docker Compose 安装

```yaml
services:
   jenkins:
        image: jenkins/jenkins:jdk21
        ports:
            - "8080:8080"
            - "50000:50000"
        volumes:
            - jenkins_data://var/jenkins_home
            - /var/run/docker.sock://var/run/docker.sock
            - /etc/localtime://etc/localtime:ro

volumes:
    jenkins_data:
```

## 在 Docker 中下载并运行 Jenkins

参考 [在 Docker 中下载并运行 Jenkins](https://www.jenkins.io/doc/book/installing/docker/)。

定制官方 Jenkins Docker 镜像，例如，安装 curl、maven、docker-ce-cli

```dockerfile
FROM jenkins/jenkins:jdk21
USER root
RUN apt-get update && apt-get install -y curl maven lsb-release
RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
  https://download.docker.com/linux/debian/gpg
RUN echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
RUN apt-get update && apt-get install -y docker-ce-cli
USER jenkins
RUN jenkins-plugin-cli --plugins "blueocean docker-workflow"
```

> 更多定制，可以参考 <https://github.com/taypo/jenkins/blob/master/Dockerfile>

从该 Dockerfile 构建一个新的 Docker 镜像，并为该镜像分配一个有意义的名称，例如“myjenkins-blueocean：2.452.2-1”：

```
docker build -t myjenkins-blueocean:2.452.2-1 .
```

创建一个 docker-compose 文件：

```yaml
services:
    jenkins-docker:
        image: docker:dind
        environment:
            - DOCKER_TLS_CERTDIR=/certs
        ports:
            - "2376:2376"
        volumes:
            - jenkins_docker_certs://certs/client
            - jenkins_data://var/jenkins_home

    jenkins-blueocean:
        image: myjenkins-blueocean:2.452.2-1
        environment:
            - DOCKER_HOST=tcp://jenkins-docker:2376
            - DOCKER_CERT_PATH=/certs/client
            - DOCKER_TLS_VERIFY=1
        ports:
            - "8080:8080"
            - "50000:50000"
        volumes:
            - jenkins_docker_certs://certs/client:ro
            - jenkins_data://var/jenkins_home

volumes:
    jenkins_data:
    jenkins_docker_certs:
```

## Jenkins 设置

登录之后，修改默认默默，安装插件，并创建第一个用户。

### 配置 JDK 和 Maven

JDK 可以使用 jenkins 镜像自带的，jenkins 默认使用 JDK17，如果需要指定 JDK 版本，可以使用 `jenkins/jenkins:xx-jdk8` 镜像。JAVA_HOME 地址 **/opt/java/openjdk**

Maven 可以进入容器安装，或者在 jenkins 配置通过命令自动安装。

### 配置镜像加速

打开宿主机 Jenkins 工作目录下的hudson.model.UpdateCenter.xml文件。url 修改为国内的清华大学官方镜像地址，最终内容如下：

```xml
<?xml version="1.1" encoding="UTF-8"?>
<sites>
  <site>
    <id>default</id>
    <url>https://mirrors.tuna.tsinghua.edu.cn/jenkins/updates/update-center.json</url>
  </site>
</sites>
```

### 配置Github SSH key

在Jenkins用户下，生成一对ssh key，将公钥放到github，私钥配置到上面docker token同样的位置即可。这样在job中可以使用ssh从github clone code。注意如果首次连接提示：

```bash
No ECDSA host key is known for github.houston.softwaregrp.net and you have requested strict checking.
```

可以采用下面的方法解决：

![img](install-jenkins/01.webp)

### 配置SSH登录

如果在Jenkins Pipeline中需要ssh到远程server，需要配置下ssh key，把生成好的public key放到远端server的authorized keys里面就行了。

### 配置反向代理

参考 《[CI：如何使用 Docker Compose 在 arm64 macOS 中为 Jenkins 创建 Nginx 反向代理？](https://akarshseggemu.medium.com/ci-how-to-create-a-nginx-reverse-proxy-for-jenkins-in-arm64-macos-using-docker-compose-4f79c2c6013c)》。

1. 准备好 SSL 文件，放置 /etc/nginx/ssl 目录
2. 安装 nginx。

3. 创建一个 nginx conf 文件 jenkins.conf 放到 nginx 的相应目录下。

```nginx
# Required for Jenkins websocket agents
map $http_upgrade $connection_upgrade {
  default upgrade;
  '' close;
}

server {
    listen 80;
    server_name jenkins.zhijun.io;
    rewrite ^ https://$http_host$request_uri? permanent;
}

server {
    listen 443 ssl;
    server_name jenkins.zhijun.io;
    ssl_certificate /etc/nginx/ssl/all.crt;
    ssl_certificate_key /etc/nginx/ssl/all.key;
    ssl_session_timeout 5m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
    ssl_prefer_server_ciphers on;

    client_max_body_size 1g;
    
    access_log /var/log/nginx/jenkins.log;

    # pass through headers from Jenkins that Nginx considers invalid
    ignore_invalid_headers off;

    location ~ "^/static/[0-9a-fA-F]{8}\/(.*)$" {
     # rewrite all static files into requests to the root
     # E.g /static/12345678/css/something.css will become /css/something.css
     rewrite "^/static/[0-9a-fA-F]{8}\/(.*)" /$1 last;
    }

    location / {
        proxy_pass http://192.168.1.107:8080;
        proxy_redirect     default;
        proxy_http_version 1.1;

        # Required for Jenkins websocket agents
        proxy_set_header   Connection        $connection_upgrade;
        proxy_set_header   Upgrade           $http_upgrade;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto http;
        proxy_max_temp_file_size 0;

        proxy_connect_timeout 150;
        proxy_send_timeout 100;
        proxy_read_timeout 100;

        proxy_buffer_size 8k;
        proxy_buffers 4 32k;
        proxy_busy_buffers_size 64k;
        proxy_temp_file_write_size 64k;
    }
}
```

- 192.168.1.107 为宿主机的 IP 地址。

## 向 Jenkins 镜像添加其他软件

创建一个 Dockerfile 文件

```dockerfile
FROM jenkins/jenkins:lts
USER root
RUN apt update && \
    apt install -y --no-install-recommends gnupg curl ca-certificates apt-transport-https
USER jenkins
```

安装新插件的最简单方法是使用 Jenkins Web UI，另外也可以使用 jenkins-plugin-cli，Jenkins 插件可以从 [Jenkins 插件网站](https://plugins.jenkins.io/) 查找。

比如，下面 Dockerfile 文件安装了 Git 插件：

```dockerfile
FROM jenkins/jenkins:lts
USER root
RUN apt update && \
    apt install -y --no-install-recommends gnupg curl ca-certificates apt-transport-https

USER jenkins

RUN jenkins-plugin-cli --plugins git:5.2.2
```

## 备份

```bash
docker run --rm -v jenkins_data://var/jenkins_home -v $(pwd)://backup ubuntu tar cvf /backup/backup.tar /var/jenkins_home
```

## 将 Docker 镜像作为服务运行

要创建新的 systemd 服务，请将以下内容保存到文件`/etc/systemd/system/docker-jenkins.service`：

```
[Unit]
Description=Jenkins

[Service]
SyslogIdentifier=docker-jenkins
ExecStartPre=-/usr/bin/docker create -m 0b -p 8080:8080 -p 50000:50000 --restart=always --name jenkins jenkins/jenkins:lts
ExecStart=/usr/bin/docker start -a jenkins
ExecStop=-/usr/bin/docker stop --time=0 jenkins

[Install]
WantedBy=multi-user.target
```

要加载新的服务文件，请运行以下命令：

```bash
sudo systemctl daemon-reload
```

要启动该服务，请运行以下命令：

```bash
sudo systemctl start docker-jenkins
```

要使服务在重新启动时运行，请运行以下命令：

```bash
sudo systemctl enable docker-jenkins
```

要查看服务日志，请运行以下命令：

```bash
sudo journalctl -u docker-jenkins -f
```

## 参考文章

- [Docker 安装 Jenkins 并实现项目自动化部署](https://cloud.tencent.com/developer/article/2347137)

- [How to install Jenkins using Docker Compose?](https://www.czerniga.it/2021/11/07/how-to-install-jenkins-using-docker-compose/)

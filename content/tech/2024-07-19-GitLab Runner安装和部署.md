---
title: "GitLab Runner 安装与配置：搭建 CI/CD 执行环境"
date: 2024-07-19 08:00:00+08:00
slug: gitlab-runner-install
tags: [ "gitlab" ]
description: "介绍 GitLab Runner 的基本概念、核心作用以及安装部署方式，帮助搭建可执行 GitLab CI/CD 作业的运行环境。"
---

## 介绍

GitLab Runner 是一个用于在 GitLab CI/CD（持续集成/持续交付）流水线中运行作业（Jobs）的开源工具。它充当了 GitLab CI/CD 系统中的代理，负责接收作业请求、执行作业脚本并报告结果。

下面是 GitLab Runner 的一些关键特点和功能：

1. 多平台支持：GitLab Runner 可在多种操作系统上运行，包括 Linux、macOS 和 Windows，使其适用于各种开发环境和需求。
2. 作业执行器：Runner 接收来自 GitLab CI/CD 的作业请求，并在指定的环境中执行作业。它可以运行各种类型的作业，如构建、测试、部署等。
3. 并发执行：GitLab Runner 可以同时运行多个作业，以提高整体流水线的处理能力和效率。
4. 弹性扩展：你可以配置多个 GitLab Runner 实例，以满足不同项目和流水线的需求。每个 Runner 实例都可以在不同的环境中运行，比如在不同的物理或虚拟机器上，或者在云服务提供商的容器中。
5. 配置灵活性：Runner 的配置相对灵活，你可以根据项目、分支或标签等条件来指定不同的执行规则。这使得你可以针对不同的场景和需求进行定制化配置。
6. 日志和报告：Runner 会生成详细的日志和报告，用于记录作业的执行过程和结果。这些信息对于故障排除、问题追踪和流水线性能分析非常有帮助。
7. 安全和身份验证：GitLab Runner 可与 GitLab CI/CD 系统集成，并通过访问令牌或其他身份验证机制来确保安全的通信和访问权限控制。

## 安装

GitLab Runner 的版本需要和 GitLab 保持一致。

查看当前 Gitlab 版本：

```bash
root@gitlab://# gitlab-rake gitlab:env:info

System information
System:  
Current User: git
Using RVM: no
Ruby Version: 3.1.5p253
Gem Version: 3.5.11
Bundler Version:2.5.11
Rake Version: 13.0.6
Redis Version: 7.0.15
Sidekiq Version:7.1.6
Go Version: unknown

GitLab information
Version: 17.1.1
Revision: a1c9a43d543
Directory: /opt/gitlab/embedded/service/gitlab-rails
DB Adapter: PostgreSQL
DB Version: 14.11
URL:  https://gitlab.wesine.com.cn
HTTP Clone URL: https://gitlab.wesine.com.cn/some-group/some-project.git
SSH Clone URL: ssh://git@gitlab.wesine.com.cn:3122/some-group/some-project.git
Using LDAP: no
Using Omniauth: yes
Omniauth Providers:

GitLab Shell
Version: 14.36.0
Repository storages:
- default:  unix://var/opt/gitlab/gitaly/gitaly.socket
GitLab Shell path:  /opt/gitlab/embedded/service/gitlab-shell

Gitaly
- default Address:  unix://var/opt/gitlab/gitaly/gitaly.socket
- default Version:  17.1.1
- default Git Version:  2.45.1
```

当前 Gitlab 安装的版本为 17.1.1，所以 Gitlab Runner 也需要安装 17.1.1 版本。

### yum安装

参考 <https://docs.gitlab.com/runner/install/linux-repository.html> ，CentOS 上安装：

```bash
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh" | sudo bash

yum list gitlab-runner --showduplicates | sort -r
sudo yum install gitlab-runner-17.1.1
```

### rpm包安装

在 <https://mirrors.tuna.tsinghua.edu.cn/gitlab-runner/yum/el7-x86_64/> 查找合适版本的软件包并下载

```bash
wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-runner/yum/el7-x86_64/gitlab-runner-17.1.0-1.x86_64.rpm
rpm -ivh gitlab-runner-17.1.0-1.x86_64.rpm
```

### docker安装

使用 docker 安装

```bash
mkdir /srv/gitlab-runner

docker run --name gitlab-runner -itd -v /srv/gitlab-runner://etc/gitlab-runner --restart always gitlab/gitlab-runner:v17.1.0
```

或者使用 docker-compse 安装：

```yaml
 services: 
  gitlab-runner:
    image: gitlab/gitlab-runner
    container_name: gitlab-runner
    restart: always
    volumes:
      - "/srv/gitlab-runner://etc/gitlab-runner"
```

## 注册

Gitlab Runner类型有三种，注册方法如下：

- shared：运行整个平台项目的作业（gitlab）。依次点击主页——>管理中心——>CI/CD——>Runner——>新建实例runner
- group：运行特定group下的所有项目的作业（group）。依次点击主页——>群组——>指定组——>设置——>构建——>runner——>新建群组runner
- specific：运行指定的项目作业（project）。依次点击主页——>项目——>指定项目——>设置——>CI/CD——>Runner——>新建项目runner

生成注册命令：

```bash
gitlab-runner register --url https://gitlab.example.com --token glrt-JhEv5bxs4ezxY53uyYiz
```

Runner 执行器的类型有：

```bash
docker, docker-windows, instance, virtualbox, docker+machine, kubernetes, docker-autoscaler, custom, shell, ssh, parallels
```

注册一个 shell 类型的执行器：

```bash
gitlab-runner register \
 --url https://gitlab.example.com \
 --token glrt-JhEv5bxs4ezxY53uyYiz \
 --executor "shell" 
```

注册一个 docker 类型的执行器：

```bash
gitlab-runner register \
  --non-interactive \
  --executor "docker" \
 --url https://gitlab.example.com \
 --token glrt-JhEv5bxs4ezxY53uyYiz \
  --docker-privileged
```

docker 类型的执行器的有两种：

1、使用 sock，需要挂载 /var/run/docker.sock

```yaml
 services: 
  gitlab-runner:
    image: gitlab/gitlab-runner
    container_name: gitlab-runner
    restart: always
    volumes:
      - "/srv/gitlab-runner://etc/gitlab-runner"
      - /var/run/docker.sock://var/run/docker.sock
      - /etc/hosts://etc/hosts 
      - /etc/docker/daemon.json://etc/docker/daemon.json
```

注册执行器命令：

```bash
sudo gitlab-runner register \
 --url https://gitlab.example.com \
 --token glrt-JhEv5bxs4ezxY53uyYiz
  --executor "docker" \
  --docker-image docker:latest \
  --docker-volumes /var/run/docker.sock://var/run/docker.sock
```

/srv/gitlab/gitlab-runner/config.toml  文件：

```yaml
concurrent = 10 # 并行执行作业数
check_interval = 0
shutdown_timeout = 0
connection_max_age = "15m0s"

[session_server]
  session_timeout = 1800

[[runners]]
  name = "runner"
  url = "http://192.168.1.107:8000/"
  token = "glrt-bEe2isyLds2kaxxS74hP"
  executor = "docker"
  [runners.cache]
    MaxUploadedArchiveSize = 0
  [runners.docker]
    tls_verify = false
    image = "docker:latest" # 配置默认镜像
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    allowed_pull_policies = ["always", "if-not-present"]
    volumes = ["/var/run/docker.sock","/root/.m2","/cache"] # 配置挂载路径
    shm_size = 0
    network_mtu = 0
```

2、使用 docker in docker

注册执行器命令：

```bash
sudo gitlab-runner register \
 --url https://gitlab.example.com \
 --token glrt-JhEv5bxs4ezxY53uyYiz
  --executor "docker" \
  --docker-image docker:latest 
```

/srv/gitlab/gitlab-runner/config.toml  文件：

```yaml
concurrent = 10 # 并行执行作业数
check_interval = 0
shutdown_timeout = 0
connection_max_age = "15m0s"

[session_server]
  session_timeout = 1800

[[runners]]
  name = "runner"
  url = "http://192.168.1.107:8000/"
  token = "glrt-bEe2isyLds2kaxxS74hP"
  executor = "docker"
  [runners.cache]
    MaxUploadedArchiveSize = 0
  [runners.docker]
    tls_verify = false
    image = "docker:latest" # 配置默认镜像
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    allowed_pull_policies = ["always", "if-not-present"]
    volumes = ["/etc/docker/daemon.json ","/root/.m2","/cache"] # 配置挂载路径
    shm_size = 0
    network_mtu = 0
    extra_hosts = ["https://gitlab.example.com:192.168.1.107"]
    network_mode = "host"
```

说明：

- 在 docker 执行器内是无法访问没有通过 DNS 解析的 gitlab 域名的。需要配置 host 文件，一种方式是挂载 /etc/hosts 文件，另一种方式是添加下面配置：

  ```bash
      extra_hosts = ["https://gitlab.example.com:192.168.1.107"]
      network_mode = "host"
  ```

- 配置 docker 镜像加速。将 github runner 容器中的 /etc/docker/daemon.json 挂载到 docker-in-docker 中，/etc/docker/daemon.json 内容如下：

```json
{
   "registry-mirrors" : [
    "https://docker.1panel.live"
   ]
}
```

- Maven 缓存。在 docker 容器挂载 /root/.m2目录。

- Maven 镜像加速。在宿主机的 /root/.m2 目录下创建 settings.xml，使用阿里云 Maven 仓库。

  ```xml
  <settings xmlns="http://maven.apache.org/SETTINGS/1.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 https://maven.apache.org/xsd/settings-1.0.0.xsd">
    <mirrors>
      <mirror>
        <id>alimaven</id>
        <name>aliyun maven</name>
        <url>http://maven.aliyun.com/nexus/content/groups/public/</url>
        <mirrorOf>central</mirrorOf>
      </mirror>
    </mirrors>
  </settings>
  ```

## 配置

### 常见配置

修改最大并行作业数、镜像拉取策略、挂载路径。

/etc/gitlab-runner/config.toml：

```toml
concurrent = 10 # 并行执行作业数
check_interval = 0 
connection_max_age = "15m0s"
shutdown_timeout = 0 

[session_server]
  session_timeout = 1800

[[runners]]
  name = "runner"
  url = "https://gitlab.example.com"
  id = 1 
  token = "glrt-JhEv5bxs4ezxY53uyYiz"
  executor = "docker"
  [runners.cache]
    MaxUploadedArchiveSize = 0 
  [runners.docker]
    pull_policy = "if-not-present" # 配置镜像拉取策略
    tls_verify = false
    image = "alpine:latest" # 配置默认镜像
   
```

### 修改runner为特权用户

参考文档：<https://docs.gitlab.com/runner/commands/index.html#gitlab-runner-run> ，以rpm方式安装的runner为例。

```bash
$ vim /etc/systemd/system/gitlab-runner.service
ExecStart=/usr/bin/gitlab-runner "run" "--working-directory" "/home/gitlab-runner" "--config" "/etc/gitlab-runner/config.toml" "--service" "gitlab-runner" "--user" "root"

$ systemctl daemon-reload 
$ systemctl restart gitlab-runner.service
```

## 常用命令

启动命令：

```bash
gitlab-runner --debug <command>   #调试模式排查错误特别有用。
gitlab-runner <command> --help    #获取帮助信息
gitlab-runner run       #普通用户模式  配置文件位置 ~/.gitlab-runner/config.toml
sudo gitlab-runner run  # 超级用户模式  配置文件位置/etc/gitlab-runner/config.toml
```

注册命令：

```bash
gitlab-runner register  #默认交互模式下使用，非交互模式添加 --non-interactive
gitlab-runner list      #此命令列出了保存在配置文件中的所有运行程序
gitlab-runner verify    #此命令检查注册的runner是否可以连接，但不验证GitLab服务是否正在使用runner。 --delete 删除
gitlab-runner unregister   #该命令使用GitLab取消已注册的runner。

#使用令牌注销
gitlab-runner unregister --url http://gitlab.example.com/ --token t0k3n

#使用名称注销（同名删除第一个）
gitlab-runner unregister --name test-runner

#注销所有
gitlab-runner unregister --all-runners
```

服务管理：

```bash
gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner

# --user指定将用于执行构建的用户
#`--working-directory  指定将使用**Shell** executor 运行构建时所有数据将存储在其中的根目录

gitlab-runner uninstall #该命令停止运行并从服务中卸载GitLab Runner。

gitlab-runner start     #该命令启动GitLab Runner服务。

gitlab-runner stop      #该命令停止GitLab Runner服务。

gitlab-runner restart   #该命令将停止，然后启动GitLab Runner服务。

gitlab-runner status #此命令显示GitLab Runner服务的状态。当服务正在运行时，退出代码为零；而当服务未运行时，退出代码为非零。
```

## 执行器

CI/CD的流水线真正的执行环境是GitLab Runner提供的执行器，为了满足各种各样的需求，GitLab CI/CD支持的执行器有很多种，最常用的是Docker， shell，Kubernets三种。

GitLab Runner支持的执行器有以下几种：

- SSH
- Shell
- Parallels
- VirtualBox
- Docker
- Docker Machine (auto-scaling)
- Kubernetes
- Custom

GitLab Runner 支持的执行器有GitLab Runner的安装方式有关也和宿主机环境有关。

执行器功能对比，可参考文档：<https://docs.gitlab.com/runner/executors/#selecting-the-executor> 。

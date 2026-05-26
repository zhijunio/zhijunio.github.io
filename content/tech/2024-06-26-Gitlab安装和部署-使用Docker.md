---
title: "Docker 部署 GitLab：完整安装与配置指南"
date: 2024-06-26 08:00:00+08:00
slug: install-gitlab
tags: [ "docker", "gitlab" ]
description: "记录使用 Docker 部署 GitLab 的基本流程，包括镜像选择、external_url 配置和基础运行方式。"
---

## 安装 Gitlab

安装 gitlab-ce  版本，当前最新版本为  17.2.0

### 配置 external_url

参考 <https://docs.gitlab.com/ee/install/docker.html#install-gitlab-using-docker-compose>

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce
    container_name: gitlab
    restart: always
    hostname: "gitlab.example.com"
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url "https://gitlab.example.com"
    ports:
      - "80:80"
      - "443:443"
      - "22:22"
    volumes:
      - "/srv/gitlab/config://etc/gitlab"
      - "/srv/gitlab/logs://var/log/gitlab"
      - "/srv/gitlab/data://var/opt/gitlab"
    shm_size: "256m"
```

停止本地的 sshd 和 nginx 服务，避免 22 、80、443端口备占用：

```bash
systemctl stop nginx
systemctl stop sshd
```

启动 gitlab：

```bash
export GITLAB_HOME=/srv/gitlab && docker compose up -d
```

查看日志：

```bash
docker logs -f gitlab
```

本地配置 /etc/host 文件：

```bash
127.0.0.1 gitlab.example.com
```

打开浏览器访问：<https://gitlab.example.com/> ，用户名 root，密码通过下面命令查看：

```bash
cat /srv/gitlab/config/initial_root_password
```

### 修改默认端口

参考 <https://github.com/hutchgrant/gitlab-docker-local/，>

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce
    container_name: gitlab
    restart: always
    hostname: "gitlab.example.com"
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url "https://gitlab.example.com:3143"
        gitlab_rails["gitlab_shell_ssh_port"] = 3122
    ports:
      - "3143:443"
      - "3122:22"
    volumes:
      - "/srv/gitlab/config://etc/gitlab"
      - "/srv/gitlab/logs://var/log/gitlab"
      - "/srv/gitlab/data://var/opt/gitlab"
    shm_size: "256m"
```

### 配置时区

进入容器，修改配置  /etc/gitlab/gitlab.rb：

```bash
# 时区
gitlab_rails["time_zone"] = "Asia/Shanghai"
```

### 解决头像显示异常问题

```toml
# 解决头像显示异常问题
gitlab_rails["gravatar_plain_url"] = "http://cravatar.cn/avatar/%{hash}?s=%{size}&d=identicon"
gitlab_rails["gravatar_ssl_url"] = "https://cravatar.cn/avatar/%{hash}?s=%{size}&d=identicon"
```

### 关闭不需要的服务

GitLab 默认提供了软件包仓库、容器仓库、软件依赖管理，这些可以使用 Nexus 代替

```toml
# 关闭容器仓库功能
gitlab_rails["gitlab_default_projects_features_container_registry"] = false
gitlab_rails["registry_enabled"] = false
registry["enable"] = false
registry_nginx["enable"] = false

# 关闭包仓库、依赖管理
gitlab_rails["packages_enabled"] = false
gitlab_rails["dependency_proxy_enabled"] = false
```

关闭GitLab Pages：

```toml
# 关闭GitLab Pages
gitlab_pages["enable"] = false
pages_nginx["enable"] = false
```

关闭监控和性能基准相关功能：

```toml
#关闭监控和性能基准相关功能
prometheus_monitoring["enable"] = false
alertmanager["enable"] = false
node_exporter["enable"] = false
redis_exporter["enable"] = false
postgres_exporter["enable"] = false
pgbouncer_exporter["enable"] = false
gitlab_exporter["enable"] = false
sidekiq["metrics_enabled"] = false

# 关闭使用统计
gitlab_rails["usage_ping_enabled"] = false
gitlab_rails["sentry_enabled"] = false
```

关闭 KAS、Terraform、Mattermost：

```toml
# GitLab KAS
gitlab_kas["enable"] = false
gitlab_rails["gitlab_kas_enabled"] = false

# Terraform
gitlab_rails["terraform_state_enabled"] = false
        
# Mattermost
mattermost["enable"] = false
mattermost_nginx["enable"] = false

# Kerberos
gitlab_rails["kerberos_enabled"] = false
sentinel["enable"] = false
```

关闭电子邮件相关功能：

```toml
# 关闭电子邮件相关功能
gitlab_rails["smtp_enable"] = false
gitlab_rails["gitlab_email_enabled"] = false
gitlab_rails["incoming_email_enabled"] = false
```

### 优化 PUMA 和  sidekiq

```yaml
# 禁用 PUMA 集群模式
puma["worker_processes"] = 0
puma["min_threads"] = 1
puma["max_threads"] = 2

# 降低后台守护进程并发数
sidekiq["concurrency"] = 5
```

### 优化 postgresql

```toml
# 减少 postgresql 数据库缓存
postgresql["shared_buffers"] = "128MB"
# 减少 postgresql 数据库并发数量
postgresql["max_connections"] = 60
```

### 使用自签名证书（不建议）

参考 <https://github.com/danieleagle/gitlab-https-docker#generating-a-self-signed-certificate> ，生成服务端 key：

```bash
sudo openssl genrsa -out server-key.pem 4096
```

生成服务端 csr：

```bash
sudo openssl req -new -key server-key.pem -out server.csr
```

生成服务端证书：

```bash
sudo openssl x509 -req -days 365 -in server.csr -signkey server-key.pem -out server-cert.pem
```

删除 csr 文件：

```bash
sudo rm server.csr
```

拷贝证书文件：

```bash
sudo mkdir -p /srv/gitlab/ssl
sudo cp server-*.pem /srv/gitlab/ssl/
```

修改 docker-compose 文件，添加证书相关配置：

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce
    container_name: gitlab
    restart: always
    hostname: "gitlab.example.com"
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url "https://gitlab.example.com:3143"
        gitlab_rails["gitlab_shell_ssh_port"] = 3122
        nginx["listen_port"] = 443
        nginx["redirect_http_to_https"] = true
        nginx["ssl_certificate"] = "/etc/ssl/certs/gitlab/server-cert.pem"
        nginx["ssl_certificate_key"] = "/etc/ssl/certs/gitlab/server-key.pem"
    ports:
      - "3143:443"
      - "3122:22"
    volumes:
      - "/srv/gitlab/config://etc/gitlab"
      - "/srv/gitlab/logs://var/log/gitlab"
      - "/srv/gitlab/data://var/opt/gitlab"
    shm_size: "256m"
```

为了从主机或网络上的其他地方的 gitlab 克隆，我们需要告诉 git 接受我们的自签名证书。

```bash
git config --global http."https://gitlab.example.com:3143/".sslCAInfo /srv/gitlab/ssl/server-cert.pem
```

### 使用外部 Nginx（建议）

修改配置，禁用 nginx：

```bash
services:
  gitlab:
    image: gitlab/gitlab-ce
    container_name: gitlab
    restart: always
    hostname: "gitlab.example.com"
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url "https://gitlab.example.com"
        gitlab_rails["gitlab_shell_ssh_port"] = 3122

        gitlab_workhorse["listen_network"] = "tcp"
        gitlab_workhorse["listen_addr"] = "0.0.0.0:8000"
        nginx["enable"] = false
        unicorn["enable"] = false
    ports:
      - "8000:8000"
      - "3122:22"
    volumes:
      - "/srv/gitlab/config://etc/gitlab"
      - "/srv/gitlab/logs://var/log/gitlab"
      - "/srv/gitlab/data://var/opt/gitlab"
    shm_size: "256m"
```

本地配置 /etc/host 文件：

```bash
127.0.0.1 gitlab.example.com
127.0.0.1 gitlab-registry.example.com
```

安装 nginx ，为 gitlab.example.com 配置反向代理：

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 80;
    server_name gitlab.example.com;
    rewrite ^ https://$http_host$request_uri? permanent;
}

server {
     listen 443 ssl;
     server_name gitlab.example.com;
     ssl_certificate /etc/nginx/ssl/server-cert.pem;
     ssl_certificate_key /etc/nginx/ssl/server-key.pem;
     ssl_session_timeout 5m;
     ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
     ssl_prefer_server_ciphers on;

     client_max_body_size 1g;
     access_log /var/log/nginx/gitlab.log;

     location / {
        proxy_pass     http://127.0.0.1:8000;
    proxy_read_timeout  90;
      proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    
      # Websocket connection
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
     }
}
```

拷贝证书文件到 /etc/nginx/ssl/ 目录：

```bash
sudo mkdir -p /etc/nginx/ssl/
sudo cp server-*.pem /etc/nginx/ssl/
```

### 使用外部 Redis（可选）

参考 [Using a non-packaged Redis instance](https://github.com/shamithmc/gitlab-docker/blob/master/doc/settings/redis.md#using-a-non-packaged-redis-instance)，进入容器，修改 /etc/gitlab/gitlab.rb

```bash
redis["enable"] = false
gitlab_rails["redis_host"] = "x.x.x.x"
gitlab_rails["redis_port"] = 6379
```

### 使用外部 Postgres（可选）

参考 [Using a non-packaged PostgreSQL database management server](https://github.com/shamithmc/gitlab-docker/blob/master/doc/settings/database.md#using-a-non-packaged-postgresql-database-management-server)

在 Postgres 修改 `/var/lib/pgsql/data/pg_hba.conf` 令其支持密码登录

```diff
 # "local" is for Unix domain socket connections only
 local   all             all                                     peer
 # IPv4 local connections:
-host    all             all             127.0.0.1/32            ident
+host    all             all             127.0.0.1/32            md5
 # IPv6 local connections:
-host    all             all             ::1/128                 ident
+host    all             all             ::1/128                 md5
 # Allow replication connections from localhost, by a user with the
 # replication privilege.
 local   replication     all                                     peer
```

数据库执行以下 sql 命令：

```sql
-- 重新加载 pg_hba.conf
SELECT pg_reload_conf();

-- 创建 gitlab 角色
CREATE ROLE gitlab WITH LOGIN SUPERUSER;
ALTER ROLE gitlab PASSWORD "your-db-passwd";

-- 创建 gitlabhq_production 数据库
CREATE DATABASE gitlabhq_production OWNER gitlab;
```

其中，在 gitlab 安装阶段需要赋予其 `SUPERUSER` 权限，安装完成后可以将该权限去除:

```sql
ALTER ROLE gitlab WITH NOSUPERUSER;
```

进入容器，修改 /etc/gitlab/gitlab.rb

```bash
postgresql["enable"] = false

gitlab_rails["db_adapter"] = "postgresql"
gitlab_rails["db_database"] = "gitlabhq_production"
gitlab_rails["db_encoding"] = "utf8"
gitlab_rails["db_host"] = "x.x.x.x"
gitlab_rails["db_port"] = "5432"
gitlab_rails["db_username"] = "USERNAME"
gitlab_rails["db_password"] = "PASSWORD"
```

> 数据库名称：gitlabhq_production

使配置生效：

```bash
gitlab-ctl reconfigure
```

设置数据库：

```bash
# Remove "sudo" if you are the "git" user
sudo gitlab-rake gitlab:setup
```

### 完整配置

修改默认端口，配置时区，关闭不需要的服务，优化数据库，使用外部 Nginx：

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce
    container_name: gitlab
    restart: always
    hostname: "gitlab.wesine.com.cn"
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url "https://gitlab.wesine.com.cn"
        gitlab_rails["gitlab_shell_ssh_port"] = 3122
        
    # 使用外部 Niginx
        gitlab_workhorse["listen_network"] = "tcp"
        gitlab_workhorse["listen_addr"] = "0.0.0.0:8000"
        nginx["enable"] = false
        unicorn["enable"] = false
       
        # 时区
        gitlab_rails["time_zone"] = "Asia/Shanghai"
        # 解决头像显示异常问题
        gitlab_rails["gravatar_plain_url"] = "http://gravatar.loli.net/avatar/%{hash}?s=%{size}&d=identicon"
        gitlab_rails["gravatar_ssl_url"] = "https://gravatar.loli.net/avatar/%{hash}?s=%{size}&d=identicon"
        
        # 关闭容器仓库功能
        gitlab_rails["gitlab_default_projects_features_container_registry"] = false
        gitlab_rails["registry_enabled"] = false
        registry["enable"] = false
        registry_nginx["enable"] = false

        # 关闭包仓库、依赖管理
        gitlab_rails["packages_enabled"] = false
        gitlab_rails["dependency_proxy_enabled"] = false
        
        # 关闭GitLab Pages
        gitlab_pages["enable"] = false
        pages_nginx["enable"] = false
        
        #关闭监控和性能基准相关功能
        prometheus_monitoring["enable"] = false
        alertmanager["enable"] = false
        node_exporter["enable"] = false
        redis_exporter["enable"] = false
        postgres_exporter["enable"] = false
        pgbouncer_exporter["enable"] = false
        gitlab_exporter["enable"] = false
        sidekiq["metrics_enabled"] = false

        # 关闭使用统计
        gitlab_rails["usage_ping_enabled"] = false
        gitlab_rails["sentry_enabled"] = false
        
        # 关闭电子邮件相关功能
        gitlab_rails["smtp_enable"] = false
        gitlab_rails["gitlab_email_enabled"] = false
        gitlab_rails["incoming_email_enabled"] = false
        
        # GitLab KAS
        gitlab_kas["enable"] = false
        gitlab_rails["gitlab_kas_enabled"] = false

        # Terraform
        gitlab_rails["terraform_state_enabled"] = false

        # Mattermost
        mattermost["enable"] = false
        mattermost_nginx["enable"] = false

        # Kerberos
        gitlab_rails["kerberos_enabled"] = false
        sentinel["enable"] = false
        
        # 减少 postgresql 数据库缓存
        postgresql["shared_buffers"] = "128MB"
        # 减少 postgresql 数据库并发数量
        postgresql["max_connections"] = 60
        
        # 禁用 PUMA 集群模式
        puma["worker_processes"] = 0
        puma["min_threads"] = 1
        puma["max_threads"] = 2

        # 降低后台守护进程并发数
        sidekiq["concurrency"] = 5
        
    ports:
      - "8000:8000"
      - "3122:22"
    volumes:
      - "/srv/config://etc/gitlab"
      - "/srv/logs://var/log/gitlab"
      - "/srv/data://var/opt/gitlab"
    shm_size: "256m"

  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner
    restart: always
    volumes:
      - "/srv/gitlab-runner://etc/gitlab-runner"
      - "/var/run/docker.sock://var/run/docker.sock"
```

将上面文件保存为 gitlab.yaml，然后执行安装命令：

```bash
docker compose -f gitlab.yaml up -d
```

启动成功之后，查看容器资源使用情况：

```bash
docker stats
```

结果如下：

```bash
CONTAINER ID   NAME            CPU %     MEM USAGE / LIMIT     MEM %     NET I/O          BLOCK I/O        PIDS
f384149bfeab   gitlab          0.21%     2.028GiB / 31.26GiB   6.49%     756kB / 4.66MB   246kB / 12.2MB   123
febd4b504da8   gitlab-runner   0.00%     21.61MiB / 31.26GiB   0.07%     54kB / 330kB     0B / 0B          10
```

## 安装 Gitlab Runner

参考 [部署gitlab-runner](https://xubiaosunny.top/post/gitlab_container_registry_and_auto_build_images_pfkb.html#%E9%83%A8%E7%BD%B2gitlab-runner)，在 docker-compose.yaml 文件中添加：

```yaml
  gitlab-runner:
    image: gitlab/gitlab-runner
    container_name: gitlab-runner
    restart: always
    volumes:
      - "/srv/gitlab-runner://etc/gitlab-runner"
```

在 管理中心 -> CICD -> Runner ，新建实例 Runner，标签名称设置为 docker-runner，记住 Runner 身份验证令牌

进入 github-runner：

```bash
docker exec -it gitlab-runner bash
```

复制并粘贴以下命令到您的命令行中，注册 runner。

```bash
gitlab-runner register --url https://gitlab.example.com --token glrt-JhEv5bxs4ezxY53uyYiz
```

- `glrt-JhEv5bxs4ezxY53uyYiz` 为新建 Runner 实例时的 Runner 身份验证令牌

如果提示：`couldn't execute POST against https://gitlab.example.com/api/v4/runners/verify: Post "https://gitlab.example.com/api/v4/runners/verify": dial tcp 172.28.0.2:443: connect: connection refused`，原因是 gitlab.example.com 这个域名无法通过 DNS 解析。

解决办法两种：

- 给该域名进行 DNS 解析，这个需要自己注册域名

- 通过 extra_hosts 添加域名映射，可以参考 <https://gitee.com/xuxiaowei-com-cn/GitLab/blob/main/docker-compose.yml>

- 自定义网络并添加别名，参考：<https://github.com/hutchgrant/gitlab-docker-local/blob/master/docker-compose.yml>

  ```yaml
  services:
    gitlab:
      image: gitlab/gitlab-ce
      container_name: gitlab
      restart: always
      hostname: "gitlab.example.com"
      environment:
        GITLAB_OMNIBUS_CONFIG: |
          external_url "https://gitlab.example.com"
          gitlab_rails["gitlab_shell_ssh_port"] = 3122
  
          gitlab_workhorse["listen_network"] = "tcp"
          gitlab_workhorse["listen_addr"] = "0.0.0.0:8000"
          nginx["enable"] = false
          unicorn["enable"] = false
  
          registry_external_url "https://gitlab.example.com:4567"
          registry_nginx["enable"] = false
      ports:
        - "8000:8000"
        - "3122:22"
        - "4567:4567"
      networks:
        dev-net:
          aliases:
            - gitlab.example.com
      volumes:
        - "/srv/gitlab/config://etc/gitlab"
        - "/srv/gitlab/logs://var/log/gitlab"
        - "/srv/gitlab/data://var/opt/gitlab"
      shm_size: "256m"
  
    gitlab-runner:
      image: gitlab/gitlab-runner
      container_name: gitlab-runner
      restart: always
      volumes:
        - "/srv/gitlab-runner://etc/gitlab-runner"
      networks:
        - dev-net
  
  networks:
    dev-net:
      external:
        name: development
  ```
  
- 不使用域名，而是使用 IP:Port，例如：<http://192.168.1.107:8000/>

### 注册一个使用 Docker executor 的 runner

参考 [使用 Docker 构建 Docker 镜像](https://docs.gitlab.cn/jh/ci/docker/using_docker_build.html) 。要为 CI/CD 作业启用 Docker 命令，您可以使用：

- [Shell executor](https://docs.gitlab.cn/jh/ci/docker/using_docker_build.html#使用-shell-executor)
- [Docker-in-Docker](https://docs.gitlab.cn/jh/ci/docker/using_docker_build.html#使用-docker-in-docker)
- [Docker 套接字绑定](https://docs.gitlab.cn/jh/ci/docker/using_docker_build.html#使用-docker-套接字绑定)

#### 使用 Docker-in-Docker

```bash
sudo gitlab-runner register \
 --url https://gitlab.example.com \
 --token glrt-JhEv5bxs4ezxY53uyYiz
  --executor "docker" \
  --docker-privileged \
  --docker-image docker:stable 
```

编辑 /srv/gitlab/gitlab-runner/config.toml ，或者进入容器：

```bash
docker exec -it gitlab-runner nano /etc/gitlab-runner/config.toml
```

修改 gitlab url 为 IP:Port，添加 maven 缓存，docker 缓存：

```toml
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
    volumes = ["/root/.m2://root/.m2"] # 配置挂载路径
    shm_size = 0
    network_mtu = 0
```

重启 gitlab-runner：

```bash
docker exec -it gitlab-runner gitlab-runner restart
```

#### 使用 Docker Socket

要使 Docker 在镜像上下文中可用，您需要将 `/var/run/docker.sock` 挂载到启动的容器中。要使用 Docker executor 执行此操作，您需要将 `"/var/run/docker.sock://var/run/docker.sock"` 添加到 `[runners.docker]` 部分的卷中。

```bash
sudo gitlab-runner register \
 --url https://gitlab.example.com \
 --token glrt-JhEv5bxs4ezxY53uyYiz
  --executor "docker" \
  --docker-image docker:latest \
  --docker-volumes /var/run/docker.sock://var/run/docker.sock
```

修改 /srv/gitlab/gitlab-runner/config.toml ：

```toml
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
    image = "alpine:latest" # 配置默认镜像
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    pull_policy = "if-not-present"
    volumes = ["/etc/docker/daemon.json:ro","/var/run/docker.sock","/root/.m2://root/.m2"]
    shm_size = 0
    network_mtu = 0
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

## 配置 Gitlab

### 实例配置

#### 默认语言【实例】

- `管理中心` -> `设置` -> `偏好设置` -> `本地化` -> `默认语言` -> `Chinese, Simplified - 简体中文`
- `Admin Area` -> `Settings` -> `Preferences` -> `Localization` -> `Default language` -> `Chinese, Simplified - 简体中文`

1. 仅对修改此配置后创建的新用户有效

#### 默认语言【用户】

- `偏好设置` -> `本地化` -> `语言` -> `Chinese, Simplified - 简体中文`
- `Preferences` -> `Localization` -> `Language` -> `Chinese, Simplified - 简体中文`

#### 启用/禁用允许用户注册

- `管理中心` -> `设置` -> `通用` -> `注册限制` -> `已启用注册功能`
- `Admin Area` -> `Settings` -> `General` -> `Sign-up restrictions` -> `Sign-up enabled`

#### 未登录用户重定向地址

- `管理中心` -> `设置` -> `通用` -> `登录限制` -> `首页URL`
- `Admin Area` -> `Settings` -> `General` -> `Sign-in restrictions` -> `Home page URL`

1. 将未经身份验证的用户定向到此页面。

#### 限制新建项目可见性

- `管理中心` -> `设置` -> `通用` -> `可见性与访问控制` -> `限制可见性级别` -> `公开`
- `Admin Area` -> `Settings` -> `General` -> `Visibility and access controls` -> `Restricted visibility levels` -> `Public`

1. Private 私有：如果选中，只有管理员能够创建私有群组、项目和代码片段。
2. Internal 内部：如果选中，则只有管理员能够创建内部群组、项目和代码片段。
3. Public 公开：如果选中，则只有管理员能够创建公开群组、项目和片段。此外，个人资料仅对经过身份验证的用户可见。

#### 自定义 Git 访问协议

- `管理中心` -> `设置` -> `通用` -> `可见性与访问控制` -> `启用 Git 访问协议` -> `Only HTTP(S)`
- `Admin Area` -> `Settings` -> `General` -> `Visibility and access controls` -> `Enabled Git access protocols` -> `Only HTTP(S)`

1. Both SSH and HTTP(S)：可以使用 HTTP(S) 或 SSH 检出、推送代码
2. Only SSH：只能使用 SSH 检出、推送代码
3. Only HTTP(S)：只能使用 HTTP(S) 检出、推送代码

#### 导入和导出设置

- `管理中心` -> `设置` -> `通用` -> `导入源` -> `GitHub、Bitbucket Cloud、Bitbucket Server、FogBugz、Repository by URL、GitLab export、Gitea、Manifest file、Gitee`
- `Admin Area` -> `Settings` -> `General` -> `Import and export settings` -> `GitHub、Bitbucket Cloud、Bitbucket Server、FogBugz、Repository by URL、GitLab export、Gitea、Manifest file、Gitee`

#### 流水线计划的最大数量

- `管理中心` -> `设置` -> `CI/CD` -> `持续集成和部署` -> `CI/CD 限制` -> `流水线计划的最大数量`
- `Admin Area` -> `Settings` -> `CI/CD` -> `Continuous Integration and Deployment` -> `CI/CD limits` -> `Maximum number of pipeline schedules`

#### 实例级别环境变量

- `管理中心` -> `设置` -> `CI/CD` -> `变量` -> `添加变量`
- `Admin Area` -> `Settings` -> `CI/CD` -> `Variables` -> `Add variable`

| 键                 | 值                                                      | 描述                                    | 说明                                                         |
| ------------------ | ------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------ |
| `SETTINGS_RAW_URL` | `http://172.25.25.14:48081/repository/raw/settings.xml` | 自建 Maven 私库的 settings.xml 配置文件 | 使用 Nexus 搭建了一个 Maven 私库，包含了众多 Maven (镜像)仓库 ，用于加速依赖下载 |

### 修改初始密码

进入容器：

```bash
docker exec -it gitlab bash
```

获取root用户密码：

```bash
cat /etc/gitlab/initial_root_password | grep Password
```

运行下面命令修改root默认密码为 `abcd1234!`：

```bash
$ gitlab-rails console
u=User.where(id:1).first
new_password="abcd1234!"
u.password=new_password
u.password_confirmation=new_password
u.save!
exit
```

### 配置系统服务

脚本：

``` bash
#!/bin/bash

# Create gitlab systemd service
# First parameter is the linux account username you want the service run under
# Second parameter is the location of your gitlab docker-compose.yml
# Example:  $ sudo sh gitlab_service.sh LINUXUSER /home/youruser/gitlab-docker-local

echo "
[Unit]
Description=Gitlab Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=$1
WorkingDirectory=$2
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/gitlab.service

systemctl start gitlab
systemctl enable gitlab
```

> 注意：该脚本依赖 Docker Service，所有需要先创建 Docker 系统服务。

运行命令：

```bash
# sudo sh gitlab_service.sh LINUXUSER PATH_REPO_FOLDER
sudo sh gitlab_service.sh root /opt/docker/gitlab.yaml
```

## 测试

### 访问

访问 <https://gitlab.example.com，修改默认密码，创建一个测试用户：test>

### 添加 SSH Key

[Add](https://docs.gitlab.com/ce/ssh/README.html#generating-a-new-ssh-key-pair) / [generate](https://docs.gitlab.com/ce/ssh/README.html#generating-a-new-ssh-key-pair) a ssh key

```
tail ~/.ssh/id_rsa.pub
```

拷贝并保存到 <https://gitlab.example.com/profile/keys>

### 创建新项目

创建一个项目 example ，克隆项目：

```bash
git clone ssh://git@gitlab.example.com:3122/root/example.git
```

测试添加文件并提交：

```bash
cd example
git add .
git commit -m "Initial commit"
git push -u origin main
```

## 备份

### 备份数据

参考 [Official Docs](https://docs.gitlab.com/ee/raketasks/backup_restore.html)，备份：

```bash
docker exec -it gitlab gitlab-rake gitlab:backup:create
```

备份后的文件在 /srv/gitlab/data/backups/ ：

```bash
$ ls -l --color=auto /srv/gitlab/data/backups/
总用量 532
-rw------- 1 chrony polkitd 542720 7月  12 08:57 1720745862_2024_07_12_17.1.1_gitlab_backup.tar
```

### 备份 Gitlab 配置

参考 [recommends storing the configuration backups seperate from your application backups](https://docs.gitlab.com/omnibus/settings/backups.html)：

```bash
sudo sh -c "umask 0077; tar cfz /data/backups/$(date "+%s-gitlab-config.tgz") -C /srv/gitlab config ssl"
```

### 备份 Gitlab Runner 配置

```bash
sudo sh -c "umask 0077; tar cfz /data/backups/$(date "+%s-gitlab-runner-ssl.tgz") -C /srv/gitlab-runner ."
```

### 定时备份

参考 [gitlab_backup.sh](https://github.com/hutchgrant/gitlab-docker-local/blob/master/gitlab_backup.sh)，备份脚本：

```bash
CONTAINER="gitlab"
TARGET_DIR="/data/backups"
GITLAB_DIR="/srv/gitlab"
RUNNER_DIR="/srv/gitlab-runner"
REMOVE_DAYS=1

mkdir -p $TARGET_DIR

# Backup Application DATA
echo "Backing up GitLab application data"
docker exec -t $CONTAINER gitlab-rake gitlab:backup:create
cp -u $GITLAB_DIR/backups/. $TARGET_DIR/ -a

# Backup configurations, SSH keys, and SSL certs
echo "Backing up GitLab configurations, ssh keys, and ssl certs"
sh -c "umask 0077; tar cf $TARGET_DIR/$(date "+%s-gitlab-config.tar") -C $GITLAB_DIR config ssl" 
sh -c "umask 0077; tar cf $TARGET_DIR/$(date "+%s-gitlab-runner.tar") -C $RUNNER_DIR ."

# Remove files older than x days 
echo "Removing files older than $REMOVE_DAYS days"
find $TARGET_DIR/*.tar -mtime $REMOVE_DAYS -exec rm {} \;
```

添加定时任务：

```bash
sudo crontab -e
```

添加脚本，每天早上 2 点定时执行：

```bash
0 2 * * * sh /your/directory/gitlab_backup.sh
```

## 还原

还原应用数据：

```bash
sudo cp /data/backups/1720746362_2024_07_12_17.1.1_gitlab_backup.tar /srv/gitlab/data/backups/
docker exec -it gitlab sh -c "chown git.git /var/opt/gitlab/backups/*.tar"
docker exec -it gitlab gitlab-rake gitlab:backup:restore
```

还原配置文件：

```bash
sudo tar -xvf /data/backups/1720746535-gitlab-config.tar -C /srv/gitlab
docker exec -it gitlab gitlab-ctl reconfigure
```

还原 Runner 配置文件：

```bash
sudo tar -xvf /data/backups/1720746535-gitlab-runner.tar -C /srv/gitlab-runner
docker exec -it gitlab-runner gitlab-runner restart
```

重启：

``` bash
docker-compose restart
```

完整脚本：

```bash
#!/bin/bash

CONTAINER="gitlab"
TARGET_DIR="/srv/gitlab"
RUNNER="gitlab-runner"
RUNNER_DIR="/srv/gitlab-runner"
BACKUP_DIR="/data/backups"

# Restore application data
cp $BACKUP_DIR/*_gitlab_backup.tar $TARGET_DIR/data/backups/
docker exec -it $CONTAINER sh -c "chown git.git /var/opt/gitlab/backups/*.tar"
docker exec -it $CONTAINER gitlab-rake gitlab:backup:restore

# Restore configurations, ssh keys, SSL
tar -xvf $BACKUP_DIR/*-gitlab-config.tar -C $TARGET_DIR
docker exec -it $CONTAINER gitlab-ctl reconfigure

# Restore Gitlab Runner 
tar -xvf $BACKUP_DIR/*-gitlab-runner.tar -C $RUNNER_DIR
docker exec -it $RUNNER gitlab-runner restart

# Restart all containers
docker-compose restart
```

## 升级

1、先备份相关文件，特别是数据库

2、修改 docker-compose 文件中 gitlab 版本

3、执行下面命令

```bash
docker compose pull
docker compose up -d
```

##

## 参考文章

- [Running Gitlab CE Via Docker Behind A Reverse Proxy On Ubuntu](https://techoverflow.net/2018/12/17/running-gitlab-ce-via-docker-behind-a-reverse-proxy-on-ubuntu/)
- <https://github.com/hutchgrant/gitlab-docker-local/>
- <https://gitee.com/xuxiaowei-com-cn/GitLab>
- [Gitlab系列（3）—— 基于Gitlab-runner 的CI/CD集成](https://blog.csdn.net/tergou/article/details/120397845)

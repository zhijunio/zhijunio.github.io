---
title: "使用 Docker 安装 Gitea"
date: 2025-04-08 08:00:00+08:00
slug: install-gitea-using-docker
tags: [ "docker" ]
categories: [ "tech" ]
description: "记录如何使用 Docker 安装和运行 Gitea，包括目录准备、权限设置和基础部署步骤。"
---

## 安装 Gitea

创建目录：

```bash
rm -rf /data/gitea
mkdir -p /data/gitea/{data,config}
sudo chown 1000:1000 /data/gitea/config/ /data/gitea/data/
```

使用 docker 命令安装：

```bash
docker run -d --name=gitea -p 2222:2222 -p 3000:3000 -v /data/gitea/data://var/lib/gitea -v /data/gitea/config://etc/gitea --restart=always gitea/gitea:1.23.7-rootless
```

注意：

- Gitea 的 SSH 服务端口，默认为 2222 。具体可以参考 [gitea/gitea:1.23-rootless dockerfile](https://hub.docker.com/layers/gitea/gitea/1.23-rootless/images/sha256-5436192de9b42c7a1b3f456a3b19d58855a5c7959077258901f2f6a3b593af95)
- Gitea 的 HTTP 服务端口，默认为 3000

启动成功之后，可以通过 <http://ip:3000/> 访问。

## 配置反向代理

使用 nginx 配置：

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name gitea.zhijun.io;

    return 301 https://$host$request_uri;
}

server {
    listen          443 ssl;
    server_name     gitea.zhijun.io;

    ssl_certificate      /etc/nginx/ssl/fullchain.cer;
    ssl_certificate_key  /etc/nginx/ssl/chensoul.cc.key;

    ssl_session_cache    shared:SSL:1m;
    ssl_session_timeout  5m;

    ssl_ciphers  HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers  on;

    location / {
        proxy_pass http://127.0.0.1:3000;
    client_max_body_size 512M;
        proxy_set_header Connection $http_connection;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

注意：

- ssl 证书需要提前生成，并放到指定目录，我这里是 /etc/nginx/ssl

执行 `nginx -s reload` 之后，需要在 dns 服务商配置域名解析，gitea.zhijun.io 指定到你的 VPS IP。

然后，就可以通过域名访问 <https://gitea.zhijun.io/> 了

## SSH 容器直通

如果主机的 22 端口已被使用，使用 `Docker` 安装 `Gitea` 时只能把容器的 2222 端口映射到主机的其它端口（如：2222），这是没有任何问题的。但是以 `SSH` 方式 `clone` 项目时，`URL` 长这样
`ssh://git@git.example.com:2222:username/project.git`

如果我们想要类似以下这样的 `URL` 时就需要把 `Gitea` 容器的和主机共享 22 端口
`git@git.example.com:username/project.git`

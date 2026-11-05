---
title: "macOS 上用 Colima 跑 Docker：安装、日常用法与 DNS 踩坑"
date: 2026-11-05 13:35:00+08:00
slug: colima-macos-docker
category: ops
tags: [ "docker", "colima", "macos", "lima" ]
description: "在 Mac 上用 Colima（Lima + Docker）替代 OrbStack，含 profile、context 切换，以及拉镜像 [::1]:53 DNS 故障的修复。"
---

在 macOS 上跑容器，常见选择是 Docker Desktop 或 OrbStack。若更在意**开源、CLI 可控、不用时关掉 VM**，[Colima](https://colima.run) 通过 [Lima](https://github.com/lima-vm/lima) 起 Linux 虚拟机，在 VM 里跑 Docker，本机仍用 `docker` / `docker compose`。

Colima 与 OrbStack、Docker Desktop **不要同时开**；切换前退出其它引擎，再 `docker context use colima`。

<!--more-->

## 安装与启动

```bash
brew install colima docker docker-compose
colima start --dns 114.114.114.114 --dns 1.1.1.1
# 资源不够时：colima start --cpu 4 --memory 8 --dns 114.114.114.114 --dns 1.1.1.1
```

`colima start` 默认**后台**运行；配置落在 **`~/.colima/default/colima.yaml`**，改过的 flags 会持久化。

## Profile

**Profile** 是实例名：每个 profile 有独立 VM、目录 `~/.colima/<名字>/` 和 Docker socket。不写名字时用 **`default`**。

```bash
colima start dev --cpu 2 --memory 4
colima start heavy --cpu 8 --memory 16
colima list
docker context use colima-dev   # 以 docker context ls 为准
colima stop dev
```

多套可同时运行；换项目切 `docker context`。

## 日常

```bash
colima status | stop | ssh
docker context use colima
docker compose up -d
docker run --rm hello-world
```

切回 OrbStack：`colima stop` → `docker context use orbstack`。

**Colima** 偏开源与脚本化；**OrbStack** 偏 GUI 与 Mac 集成。二者留一个即可。

## DNS：`[::1]:53 connection refused`

拉镜像若报 `lookup registry-1.docker.io on [::1]:53 ... connection refused`，是 VM 内 DNS 指向坏的 systemd stub。在 **`~/.colima/default/colima.yaml`**（或对应 profile 目录）加上：

```yaml
network:
  dns:
    - 114.114.114.114
    - 1.1.1.1

provision:
  - mode: after-boot
    script: |
      if [ -L /etc/resolv.conf ] && [ ! -e /etc/resolv.conf ]; then
        rm -f /etc/resolv.conf
        printf 'nameserver 114.114.114.114\nnameserver 1.1.1.1\noptions edns0\n' > /etc/resolv.conf
      fi
```

然后 `colima stop && colima start`（或 `colima start --dns 114.114.114.114 --dns 1.1.1.1`）。用 `docker run --rm hello-world` 验证。

## 其它

- **连不上 daemon**：`colima start` + `docker context use colima`
- **仍走 OrbStack**：`docker context ls` 后切换
- **拉取慢**：检查本机代理是否对 VM 可达（Colima 常把 `127.0.0.1:7890` 映射到网关）

参考：[Colima 文档](https://colima.run/docs/) · [Lima](https://github.com/lima-vm/lima)

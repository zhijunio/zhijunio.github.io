---
title: "macOS 上用 Colima 跑 Docker：安装、日常用法与 DNS 踩坑"
date: 2026-11-05 13:35:00+08:00
slug: colima-macos-docker
category: ops
tags: [ "docker", "colima", "macos", "lima" ]
description: "在 Apple Silicon Mac 上用 Colima 替代 OrbStack 跑 Docker Compose，含默认参数、context 切换，以及 registry-1.docker.io [::1]:53 DNS 故障的修复。"
---

在 macOS 上跑容器，常见选择是 Docker Desktop 或 OrbStack。若更在意**开源、CLI 可控、不用时关掉 VM**，[Colima](https://colima.run) 是很实用的一层：它通过 [Lima](https://github.com/lima-vm/lima) 起 Linux 虚拟机，在 VM 里跑 Docker，本机继续用熟悉的 `docker` 和 `docker compose`。

本文记录我在本机从 OrbStack 切到 Colima 时的安装方式、默认行为，以及一次真实的 **DNS 拉镜像失败** 排查。

<!--more-->

## Colima 是什么

- **Lima**：在 Mac 上跑 Linux VM（Apple Silicon 上常用 Virtualization.framework / `vz`）。
- **Colima**：在 Lima 之上配好 Docker，并帮你接好 Docker context。

Colima 与 OrbStack、Docker Desktop **不要同时开**。切换前先退出其它引擎，再 `docker context use colima`。

## 安装

```bash
brew install colima docker docker-compose
```

日常优先用 **`docker compose`**（Docker CLI 子命令），与 Homebrew 单独的 `docker-compose` 二选一即可。

## 启动与默认参数

推荐首次启动（避免默认 DNS 为空、资源过紧）：

```bash
colima start --dns 114.114.114.114 --dns 1.1.1.1
```

需要更多资源时：

```bash
colima start --cpu 4 --memory 8 --dns 114.114.114.114 --dns 1.1.1.1
```

只执行 `colima start` 时，Colima 0.10.x 在 Apple Silicon 上常见默认如下：

| 项 | 默认 |
| --- | --- |
| Profile | `default` |
| 运行时 | Docker（Kubernetes 默认关） |
| CPU / 内存 / 数据盘 | 2 / 2 GiB / 100 GiB |
| VM 类型 | `vz` |
| 挂载 / 网络 | `virtiofs` / `shared` |
| 前台还是后台 | **后台**；只有 `-f` / `--foreground` 才占着当前终端 |

通过命令行传入的 flags 会写入 **`~/.colima/default/colima.yaml`**，下次只 `colima start` 会沿用已保存配置。

## 日常使用

```bash
colima status
colima stop            # 停 VM，保留磁盘
colima ssh             # 进 VM 排查
```

Docker：

```bash
docker context ls
docker context use colima
docker run --rm hello-world
docker compose up -d
```

切回 OrbStack：`colima stop` → `docker context use orbstack`。

## 和 OrbStack 怎么选

- **Colima**：开源、可 `colima stop` 省资源、适合脚本化；挂载和网络有时要自己调。
- **OrbStack**：GUI 和 Mac 集成更顺，不少场景 I/O 更省心。

能力重叠，留一个即可。

## DNS 踩坑：`[::1]:53 connection refused`

执行 `docker run --rm hello-world` 时若出现：

```text
lookup registry-1.docker.io on [::1]:53: read udp ... connection refused
```

说明 **VM 内 DNS 坏了**：`/etc/resolv.conf` 指向 systemd-resolved 的 stub，但 resolved 未运行。本机若还有 Tailscale、自定义解析等，Colima 默认 **`network.dns: []`** 时更容易踩坑。

在 **`~/.colima/default/colima.yaml`** 中建议配置：

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

然后：

```bash
colima stop && colima start
```

也可用命令行写入 DNS（会合并进 yaml）：

```bash
colima stop
colima start --dns 114.114.114.114 --dns 1.1.1.1
```

验证：

```bash
docker run --rm hello-world
colima ssh -- cat /etc/resolv.conf
```

## 其它常见问题

| 现象 | 处理 |
| --- | --- |
| `Cannot connect to the Docker daemon` | `colima start`；`docker context use colima` |
| 仍连到 OrbStack | `docker context ls`，退出 OrbStack 后切换 |
| 拉取慢 | 检查本机代理（如 `127.0.0.1:7890`）；Colima 可能把代理改写到 VM 网关，需保证 VM 能访问 |

## 参考

- [Colima 文档](https://colima.run/docs/)
- [Lima 项目](https://github.com/lima-vm/lima)

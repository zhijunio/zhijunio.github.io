---
title: "ThingsBoard TBMQ 本地运行与 Docker 部署实践"
date: 2024-04-17 08:00:00+08:00
slug: thingsboard-tbmq-local-docker-run
tags: [ "thingsboard" ]
description: "记录 ThingsBoard TBMQ 在本地和 Docker 环境中的运行方式，包括源码下载、docker-compose 启动和基础验证步骤。"
---

## docker-compose 运行

参考：[https://thingsboard.io/docs/mqtt-broker/install/cluster/docker-compose-setup/](https://thingsboard.io/docs/mqtt-broker/install/cluster/docker-compose-setup/)

<!--more-->

1. 下载源代码

   ```bash
   git clone -b release-1.3.0 https://github.com/thingsboard/tbmq.git
   cd tbmq/docker
   ```

2. 创建逻辑卷并执行安装程序

   ```bash
   ./scripts/docker-create-volumes.sh
   ./scripts/docker-install-tbmq.sh
   ```

3. 运行服务

   ```bash
   ./scripts/docker-start-services.sh
   ```

   浏览器访问：[http://localhost:8083](http://localhost:8083)，用户名/密码：<sysadmin@thingsboard.org> / sysadmin

   查看 HaProxy 日志，发现出现异常：`Error: Specified qdisc kind is unknown.` 。

   目前，尚未找到解决办法，只能不使用 HaProxy 而是直接访问 tbmq1，修改 docker-compose.yml ，暴露容器端口 8083 到本地的 8083：

   ```yaml
     tbmq1:
       restart: always
       container_name: "${TBMQ_1_NAME}"
       image: "${DOCKER_REPO}/${DOCKER_NAME}:${TBMQ_VERSION}"
       ports:
         - "1883"
         - "8083:8083" #修改这里
         - "8084"
   ```

   然后，通过浏览器访问 浏览器访问：**<http://localhost:8081>**

## 源码编译并运行

1. 安装好 JDK 17+ 和 Maven3.6.3+

2. 下载源代码

   ```bash
   git clone -b release-1.3.0 https://github.com/thingsboard/tbmq.git
   cd tbmq
   ```

3. 编译代码

   ``` bash
   mvn clean install -DskipTests
   ```

4. 通过 docker-compose 本地安装 postgres、kafka、redis

   参考 docker 目录下的文件新建 docker-compose.postgres.yml 文件：

   ```yaml
   version: "3.0"
   
   services:
     postgres:
       restart: always
       image: postgres:15
       ports:
         - "5432:5432"
       environment:
         POSTGRES_DB: thingsboard_mqtt_broker
         POSTGRES_PASSWORD: postgres
       volumes:
         - postgres-data://var/lib/postgresql/data
   
   
   volumes:
     postgres-data:
   ```

   新建 docker-compose.redis.yml 文件：

   ```yaml
   version: "3.0"
   
   services:
     # Redis standalone
     redis:
       restart: always
       image: bitnami/redis:7.2
       ports:
         - "6379:6379"
       volumes:
         - redis-data://bitnami/redis/data
       command: redis-server --requirepass 123456
       healthcheck:
         test: [ "CMD", "redis-cli","-a","123456","--raw", "incr","ping" ]
         interval: 5s
         timeout: 2s
         retries: 10
   
   volumes:
     redis-data:
   ```

   新建 docker-compose.kafka.yml 文件：

   ```yml
   version: "3.0"
   
   services:
    kafka:
       restart: always
       image: bitnami/kafka:3.7.0
       ports:
         - "9092:9092"
       env_file:
         - kafka.env
   ```

   新建  kafka.env ：

   ```bash
   KAFKA_CFG_NODE_ID=0
   KAFKA_CFG_PROCESS_ROLES=controller,broker
   KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093
   KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
   KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://:9092
   KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
   KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
   KAFKA_CFG_INTER_BROKER_LISTENER_NAME=PLAINTEXT
   KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=false
   KAFKA_CFG_LOG_RETENTION_BYTES=1073741824
   KAFKA_CFG_LOG_SEGMENT_BYTES=268435456
   KAFKA_CFG_LOG_RETENTION_MS=300000
   KAFKA_CFG_LOG_CLEANUP_POLICY=delete
   ```

   本地 hosts 文件添加一行：

   ```bash
   localhost kafka
   ```

5. 导入 IDE 运行

   先运行 `ThingsboardMqttBrokerInstallApplication` 类执行安装程序。然后，运行 `ThingsboardMqttBrokerApplication` 类，启动应用。

   启动成功之后，浏览器访问：[http://localhost:8083](http://localhost:8083)，用户名/密码：<sysadmin@thingsboard.org> / sysadmin

---
title: "ThingsBoard 领域模型详解：租户、设备、资产与数据关系"
date: 2024-05-07 08:00:00+08:00
slug: thingsboard-domain
categories: [ "tech" ]
tags: [ "thingsboard" ]
description: "梳理 ThingsBoard 中租户、客户、用户、设备、资产等核心领域对象，帮助理解平台的数据组织方式与业务模型。"
---



ThingsBoard是一个开源的物联网平台，用于管理和监控物联网设备和数据。它提供了一个可扩展的架构，可以连接各种设备，并实时收集、处理和分析设备生成的数据。

## 领域模型

在ThingsBoard中，领域模型是一个关键概念，用于描述物联网系统中的物理实体、属性和行为。以下是ThingsBoard中的主要领域模型组件：

1. 租户（Tenant）：租户是ThingsBoard中的顶级组织单位。它代表了一个独立的实体，可以是一个用户、组织或公司。租户拥有和管理自己的设备、客户、规则和仪表板等资源。租户之间的数据和配置是相互隔离的，每个租户都有自己的独立环境。租户由系统管理员创建和管理。
2. 租户配置（TenantProfile）：用于定义租户级别的配置和属性。
3. 客户（Customer）：客户是租户下的子级实体，代表了物联网系统中的用户或组织。一个租户可以包含多个客户，每个客户都有自己的访问权限和角色。客户可以访问和监控租户下的设备和数据。客户可以有自己的设备、规则和仪表板等资源，但这些资源受到租户级别的限制。客户由租户管理员创建和管理。
4. 用户（User）：保存用户的基本信息
   1. 用户的角色（Authority）：SYS_ADMIN、TENANT_ADMIN、CUSTOMER_USER、REFRESH_TOKEN、PRE_VERIFICATION_TOKEN
   2. 用户凭证（UserCredentials）：保存用户的密码、激活用户 Token、重置密码 Token、密码使用历史
   3. 用户认证设置（UserAuthSettings）：保存用户 2FA 认证设置
   4. 用户设置（UserSettings）：保存用户的设置，包括：通用设置、通知、访问过的仪表盘等等
5. 系统设置（AdminSettings）：是用于配置和管理整个系统的全局设置和参数，包括：通用设置、邮件、JWT、连接设置等等。
6. 审计日志（AuditLog）

7. 资产（Asset）：指在系统中表示和管理的物理或虚拟实体。资产可以是设备、传感器、设施、车辆、建筑物、人员或其他实体，其状态、属性和行为可以被监测、控制和管理。
8. 资产配置（AssetProfile）：配置资产使用的默认规则链、队列、移动端仪表盘
9. 设备（Device）：
   1. 遥测数据（TsKV）：
   2. 最新遥测数据：
   3. 属性（AttributeKvEntry）：属性类型分为客户端、服务端、共享
   4. 远程调用（Rpc）
   5. 设备凭证（DeviceCredentials）：
   6. OTA：
10. 设备配置（DeviceProfile）：配置设备使用的默认规则链、队列、移动端仪表盘、边缘网关默认规则链、分配的固件、分配的软件、传输方式、告警规则、设置预配置
11. 告警（Alarm）：包括字段：租户、客户、类型、明细、发起者、告警级别（严重、重要、次要、警告、不确定）、是否应答、是否清除、受理人、开始时间、结束时间、应答时间、清除时间、受理时间、是否传播、是否传播给所有者、是否传播给租户
12. 告警评论（AlarmComment）：
13. 实体告警（EntityAlarm）：
14. 事件（Event）：分为异常事件、组件生命周期事件、规则链调试事件、规则节点事件、统计事件
15. 通知（Notification）:
    1. 通知请求（NotificationRequest）
    2. 通知模版（NotificationTemplate）：
    3. 通知规则（NotificationRule）
    4. 通知对象（NotificationTarget）

## 流程

### 上报遥测数据

1. 设备配置启用告警规则。温度大于 20 时，产生告警。温度小于 20 时，清除告警。

2. 创建一个设备，设备凭证使用 AccessToken

3. 使用 http api 发送遥测数据

   ```bash
   curl -v -X POST http://localhost:8080/api/v1/gs76dj5m47yd3lm1wurd/telemetry --header Content-Type:application/json --data "{temperature:25}"
   ```

4. 查看告警
5. 再次发送遥测数据，可以清除告警

源码分析：

1. 使用 http api 发送数据，入口类在 common/transport/http 模块下的 DeviceApiController 类。这个类提供了以下几个接口：

   ```bash
   GET /api/v1/{deviceToken}/attributes
   POST /api/v1/{deviceToken}/attributes
   GET /api/v1/{deviceToken}/telemetry
   POST /api/v1/{deviceToken}/telemetry
   GET /api/v1/{deviceToken}/rpc
   POST /api/v1/{deviceToken}/rpc
   POST /api/v1/{deviceToken}/rpc/{requestId}
   POST /api/v1/{deviceToken}/claim
   GET /api/v1/{deviceToken}/firmware
   POST /api/v1/{deviceToken}/firmware
   GET /api/v1/{deviceToken}/software
   POST /api/v1/{deviceToken}/software
   POST /api/v1/provision
   ```

   POST /api/v1/{deviceToken}/telemetry 处理逻辑：

   ```
   HttpTransportContext
   TransportService
    DefaultTransportService
      TbQueueProducer<TbProtoQueueMsg<ToRuleEngineMsg>> ruleEngineMsgProducer
   
      TbRuleEngineQueueConsumerManager
       TbRuleEngineConsumerContext
        ActorSystemContext
         TbActorRef
          TbActorMailbox
           AppActor
            TenantActor
             RuleChainActor 
              RuleChainActorMessageProcessor
               RuleNodeActor
                RuleNodeActorMessageProcessor
                 TbDeviceProfileNode
                  DeviceState
                   AlarmState
                    DefaultTbContext
                     DefaultTbClusterService
                      TbRuleEngineProducerProvider
                       TbQueueProducer<TbProtoQueueMsg<ToRuleEngineMsg>> toRuleEngine
   ```

这里面用到了 Transport 、Queue、Actor ，调用链非常长。

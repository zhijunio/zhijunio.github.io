---
title: "ThingsBoard 接口设计大全：REST、MQTT、HTTP 协议"
date: 2025-07-24 09:00:00+08:00
slug: thingsboard-api
categories: [ "tech" ]
tags: ["docker","thingsboard"]
description: "系统整理 ThingsBoard 平台的 REST、MQTT、HTTP 等协议接口设计，适合作为 IoT 平台开发与对接时的参考资料。"
---

本文档整理了ThingsBoard平台的各种协议接口设计，作为IoT平台开发的参考。

<!--more-->

## 1. REST API接口

### 1.1 认证接口

```bash
POST /api/auth/login
POST /api/auth/token
POST /api/auth/logout
```

### 1.2 设备管理接口

```bash
# 设备CRUD
POST   /api/device
GET    /api/device/{deviceId}
PUT    /api/device/{deviceId}
DELETE /api/device/{deviceId}

# 设备属性
GET    /api/device/{deviceId}/attributes
POST   /api/device/{deviceId}/attributes
DELETE /api/device/{deviceId}/attributes/{scope}/{attributeKey}

# 设备关系
GET    /api/device/{deviceId}/relations
POST   /api/device/{deviceId}/relation
DELETE /api/device/{deviceId}/relation
```

### 1.3 遥测数据接口

```bash
# 时间序列数据
POST   /api/plugins/telemetry/DEVICE/{deviceId}/values/timeseries
GET    /api/plugins/telemetry/DEVICE/{deviceId}/values/timeseries
DELETE /api/plugins/telemetry/DEVICE/{deviceId}/values/timeseries

# 属性数据
POST   /api/plugins/telemetry/DEVICE/{deviceId}/values/attributes
GET    /api/plugins/telemetry/DEVICE/{deviceId}/values/attributes
DELETE /api/plugins/telemetry/DEVICE/{deviceId}/values/attributes

# 聚合数据
GET    /api/plugins/telemetry/DEVICE/{deviceId}/values/aggregation
```

### 1.4 租户管理接口

```bash
# 租户CRUD
POST   /api/tenant
GET    /api/tenant/{tenantId}
PUT    /api/tenant/{tenantId}
DELETE /api/tenant/{tenantId}

# 租户信息
GET    /api/tenant/info
```

### 1.5 客户管理接口

```bash
# 客户CRUD
POST   /api/customer
GET    /api/customer/{customerId}
PUT    /api/customer/{customerId}
DELETE /api/customer/{customerId}

# 客户设备
GET    /api/customer/{customerId}/devices
POST   /api/customer/{customerId}/device/{deviceId}
DELETE /api/customer/{customerId}/device/{deviceId}
```

### 1.6 用户管理接口

```bash
# 用户CRUD
POST   /api/user
GET    /api/user/{userId}
PUT    /api/user/{userId}
DELETE /api/user/{userId}

# 用户权限
GET    /api/user/{userId}/authority
POST   /api/user/{userId}/authority
```

### 1.7 规则引擎接口

```bash
# 规则链
POST   /api/ruleChain
GET    /api/ruleChain/{ruleChainId}
PUT    /api/ruleChain/{ruleChainId}
DELETE /api/ruleChain/{ruleChainId}

# 规则节点
POST   /api/ruleNode
GET    /api/ruleNode/{ruleNodeId}
PUT    /api/ruleNode/{ruleNodeId}
DELETE /api/ruleNode/{ruleNodeId}
```

## 2. MQTT接口

### 2.1 设备连接

```bash
# 设备认证
POST /v1/devices/me/telemetry
POST /v1/devices/me/attributes
GET  /v1/devices/me/attributes
POST /v1/devices/me/attributes/request
POST /v1/devices/me/attributes/response
```

### 2.2 遥测数据

```bash
# 发布遥测数据
Topic: v1/devices/me/telemetry
Payload: {"temperature": 25.5, "humidity": 60.2}

# 发布属性
Topic: v1/devices/me/attributes
Payload: {"firmware_version": "1.0.0"}
```

### 2.3 命令下发

```bash
# 订阅命令
Topic: v1/devices/me/commands/request/+

# 响应命令
Topic: v1/devices/me/commands/response/{requestId}
Payload: {"status": "SUCCESS", "data": {...}}
```

### 2.4 属性请求

```bash
# 请求属性
Topic: v1/devices/me/attributes/request/{requestId}
Payload: {"clientKeys": ["key1", "key2"], "sharedKeys": ["sharedKey1"]}

# 响应属性
Topic: v1/devices/me/attributes/response/{requestId}
Payload: {"key1": "value1", "key2": "value2"}
```

## 3. WebSocket接口

### 3.1 连接URL

```bash
# 设备连接
ws://thingsboard:8080/api/ws/plugins/telemetry?token={deviceToken}

# 用户连接
ws://thingsboard:8080/api/ws/plugins/telemetry?token={userToken}
```

### 3.2 消息格式

#### 3.2.1 订阅消息

```json
{
  "deviceId": "device_001",
  "keys": ["temperature", "humidity"],
  "startTs": 1640995200000,
  "endTs": 1641081600000,
  "interval": 1000,
  "limit": 100,
  "agg": "AVG"
}
```

#### 3.2.2 实时数据推送

```json
{
  "subscriptionId": 1,
  "errorCode": 0,
  "errorMsg": null,
  "data": {
    "temperature": 25.5,
    "humidity": 60.2,
    "ts": 1640995200000
  }
}
```

#### 3.2.3 命令下发

```json
{
  "deviceId": "device_001",
  "command": "setTemperature",
  "params": {
    "temperature": 26.0
  }
}
```

## 4. CoAP接口

### 4.1 设备连接

```bash
# 设备认证
POST /api/v1/{deviceToken}/telemetry
POST /api/v1/{deviceToken}/attributes
GET  /api/v1/{deviceToken}/attributes
```

### 4.2 数据上报

```bash
# 遥测数据
POST /api/v1/{deviceToken}/telemetry
Content-Type: application/json
Payload: {"temperature": 25.5, "humidity": 60.2}

# 属性数据
POST /api/v1/{deviceToken}/attributes
Content-Type: application/json
Payload: {"firmware_version": "1.0.0"}
```

## 5. HTTP接口

### 5.1 设备数据接口

```bash
# 遥测数据上报
POST /api/v1/{deviceToken}/telemetry
Content-Type: application/json
Payload: {"temperature": 25.5, "humidity": 60.2}

# 属性上报
POST /api/v1/{deviceToken}/attributes
Content-Type: application/json
Payload: {"firmware_version": "1.0.0"}

# 获取属性
GET /api/v1/{deviceToken}/attributes
```

### 5.2 命令接口

```bash
# 获取命令
GET /api/v1/{deviceToken}/commands?timeout={timeout}

# 响应命令
POST /api/v1/{deviceToken}/commands/{commandId}
Content-Type: application/json
Payload: {"status": "SUCCESS", "data": {...}}
```

## 6. 接口设计特点

### 6.1 统一认证

- **JWT Token**: REST API和WebSocket使用JWT Token认证
- **设备Token**: MQTT、CoAP、HTTP设备接口使用设备Token认证
- **Token刷新**: 支持Token自动刷新机制

### 6.2 数据格式

- **JSON格式**: 所有接口使用JSON作为数据交换格式
- **时间戳**: 使用毫秒级时间戳
- **错误码**: 统一的错误码和错误信息格式

### 6.3 版本控制

- **URL版本**: 使用 `/api/v1/` 进行版本控制
- **向后兼容**: 新版本保持对旧版本的兼容性
- **版本弃用**: 提供版本弃用通知和迁移指南

### 6.4 权限控制

- **租户隔离**: 多租户数据隔离
- **角色权限**: 基于角色的权限控制
- **资源权限**: 细粒度资源权限控制

## 7. 最佳实践

### 7.1 设备连接

- 使用设备Token进行设备认证
- 实现断线重连机制
- 支持心跳保活

### 7.2 数据上报

- 批量上报减少网络开销
- 使用压缩减少数据传输量
- 实现数据缓存和重传机制

### 7.3 命令下发

- 使用唯一命令ID
- 实现命令超时处理
- 支持命令状态跟踪

### 7.4 错误处理

- 统一的错误码定义
- 详细的错误信息
- 错误重试机制

## 8. 接口测试

### 8.1 测试环境准备

#### 8.1.1 ThingsBoard环境搭建

```bash
# 使用Docker快速搭建ThingsBoard环境
docker run -it -p 9090:9090 -p 1883:1883 -p 5683:5683/udp \
  --name thingsboard \
  --restart always \
  thingsboard/tb-postgres
```

#### 8.1.2 测试工具准备

- **Postman**: REST API测试
- **MQTT.fx**: MQTT协议测试
- **WebSocket客户端**: WebSocket测试
- **CoAP客户端**: CoAP协议测试
- **curl**: 命令行HTTP测试

### 8.2 REST API测试

#### 8.2.1 认证测试

```bash
# 用户登录获取Token
curl -X POST http://localhost:9090/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "tenant@thingsboard.org",
    "password": "tenant"
  }' | jq

# 响应示例
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiJ9...",
  "expiresIn": 86400
}
```

#### 8.2.2 设备管理测试

```bash
# 创建设备
curl -X POST http://localhost:9090/api/device \
  -H "Content-Type: application/json" \
  -H "X-Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Test Device",
    "type": "default",
    "additionalInfo": {
      "description": "Test device for API testing"
    }
  }'

# 查询设备
curl -X GET http://localhost:9090/api/device/{deviceId} \
  -H "X-Authorization: Bearer YOUR_TOKEN"

# 更新设备
curl -X PUT http://localhost:9090/api/device/{deviceId} \
  -H "Content-Type: application/json" \
  -H "X-Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Updated Test Device",
    "type": "default"
  }'

# 删除设备
curl -X DELETE http://localhost:9090/api/device/{deviceId} \
  -H "X-Authorization: Bearer YOUR_TOKEN"
```

#### 8.2.3 设备预注册测试

##### 8.2.3.1 设备预注册API

```bash
# 设备预注册（创建设备并获取访问令牌）
curl -X POST http://localhost:9090/api/device \
  -H "Content-Type: application/json" \
  -H "X-Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "PreRegisteredDevice_001",
    "type": "default",
    "additionalInfo": {
      "description": "Pre-registered device for testing",
      "manufacturer": "TestManufacturer",
      "model": "TestModel",
      "firmwareVersion": "1.0.0"
    }
  }'

# 获取设备访问令牌
curl -X GET http://localhost:9090/api/device/{deviceId}/credentials \
  -H "X-Authorization: Bearer YOUR_TOKEN"

# 更新设备访问令牌
curl -X POST http://localhost:9090/api/device/{deviceId}/credentials \
  -H "Content-Type: application/json" \
  -H "X-Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "credentialsType": "ACCESS_TOKEN",
    "credentialsId": "NEW_DEVICE_TOKEN_001"
  }'
```

##### 8.2.3.2 Python设备预注册测试脚本

```python
#!/usr/bin/env python3
"""
ThingsBoard设备预注册测试脚本
支持批量设备预注册、令牌管理和连接测试
"""

import requests
import json
import time
import uuid
import csv
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DevicePreRegistrationTester:
    def __init__(self, host: str = "localhost", port: int = 9090, user_token: str = None):
        self.host = host
        self.port = port
        self.user_token = user_token
        self.base_url = f"http://{host}:{port}"
        self.headers = {
            "Content-Type": "application/json"
        }
        if user_token:
            self.headers["X-Authorization"] = f"Bearer {user_token}"
        
        self.registered_devices = []
    
    def login(self, username: str, password: str) -> bool:
        """用户登录获取Token"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                headers={"Content-Type": "application/json"},
                json=login_data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.user_token = token_data["token"]
                self.headers["X-Authorization"] = f"Bearer {self.user_token}"
                logger.info("登录成功，获取到Token")
                return True
            else:
                logger.error(f"登录失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"登录异常: {e}")
            return False
    
    def create_device(self, device_name: str, device_type: str = "default", 
                     additional_info: Dict = None) -> Optional[Dict]:
        """创建设备"""
        try:
            device_data = {
                "name": device_name,
                "type": device_type
            }
            
            if additional_info:
                device_data["additionalInfo"] = additional_info
            
            response = requests.post(
                f"{self.base_url}/api/device",
                headers=self.headers,
                json=device_data
            )
            
            if response.status_code == 200:
                device_info = response.json()
                logger.info(f"设备创建成功: {device_name} (ID: {device_info["id"]["id"]})")
                return device_info
            else:
                logger.error(f"设备创建失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"创建设备异常: {e}")
            return None
    
    def get_device_credentials(self, device_id: str) -> Optional[Dict]:
        """获取设备访问令牌"""
        try:
            response = requests.get(
                f"{self.base_url}/api/device/{device_id}/credentials",
                headers=self.headers
            )
            
            if response.status_code == 200:
                credentials = response.json()
                logger.info(f"获取设备令牌成功: {device_id}")
                return credentials
            else:
                logger.error(f"获取设备令牌失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"获取设备令牌异常: {e}")
            return None
    
    def update_device_credentials(self, device_id: str, credentials_id: str) -> bool:
        """更新设备访问令牌"""
        try:
            credentials_data = {
                "credentialsType": "ACCESS_TOKEN",
                "credentialsId": credentials_id
            }
            
            response = requests.post(
                f"{self.base_url}/api/device/{device_id}/credentials",
                headers=self.headers,
                json=credentials_data
            )
            
            if response.status_code == 200:
                logger.info(f"更新设备令牌成功: {device_id} -> {credentials_id}")
                return True
            else:
                logger.error(f"更新设备令牌失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"更新设备令牌异常: {e}")
            return False
    
    def batch_create_devices(self, device_count: int, prefix: str = "TestDevice", 
                           device_type: str = "default") -> List[Dict]:
        """批量创建设备"""
        logger.info(f"开始批量创建设备，数量: {device_count}")
        
        created_devices = []
        for i in range(device_count):
            device_name = f"{prefix}_{i+1:03d}"
            additional_info = {
                "description": f"Batch created device {i+1}",
                "manufacturer": "TestManufacturer",
                "model": "TestModel",
                "firmwareVersion": "1.0.0",
                "batchId": f"batch_{int(time.time())}",
                "createdAt": int(time.time() * 1000)
            }
            
            device_info = self.create_device(device_name, device_type, additional_info)
            if device_info:
                created_devices.append(device_info)
                # 添加延迟避免请求过快
                time.sleep(0.1)
            else:
                logger.warning(f"设备 {device_name} 创建失败")
        
        logger.info(f"批量创建设备完成，成功: {len(created_devices)}/{device_count}")
        return created_devices
    
    def generate_device_tokens(self, devices: List[Dict]) -> List[Dict]:
        """为设备生成访问令牌"""
        logger.info(f"开始为 {len(devices)} 个设备生成令牌")
        
        devices_with_tokens = []
        for device in devices:
            device_id = device["id"]["id"]
            device_name = device["name"]
            
            # 生成唯一令牌
            token = f"DEVICE_TOKEN_{device_name}_{uuid.uuid4().hex[:8].upper()}"
            
            # 更新设备令牌
            if self.update_device_credentials(device_id, token):
                device["accessToken"] = token
                devices_with_tokens.append(device)
                logger.info(f"设备 {device_name} 令牌生成成功: {token}")
            else:
                logger.error(f"设备 {device_name} 令牌生成失败")
        
        logger.info(f"令牌生成完成，成功: {len(devices_with_tokens)}/{len(devices)}")
        return devices_with_tokens
    
    def test_device_connection(self, device_token: str, protocol: str = "mqtt") -> bool:
        """测试设备连接"""
        try:
            if protocol.lower() == "mqtt":
                return self._test_mqtt_connection(device_token)
            elif protocol.lower() == "http":
                return self._test_http_connection(device_token)
            else:
                logger.error(f"不支持的协议: {protocol}")
                return False
        except Exception as e:
            logger.error(f"设备连接测试异常: {e}")
            return False
    
    def _test_mqtt_connection(self, device_token: str) -> bool:
        """测试MQTT连接"""
        try:
            import paho.mqtt.client as mqtt
            
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    logger.info(f"MQTT连接成功: {device_token}")
                    client.disconnect()
                else:
                    logger.error(f"MQTT连接失败: {rc}")
            
            client = mqtt.Client()
            client.username_pw_set(device_token, "")
            client.on_connect = on_connect
            
            client.connect(self.host, 1883, 10)
            client.loop_start()
            
            # 等待连接结果
            time.sleep(2)
            client.loop_stop()
            
            return True
        except Exception as e:
            logger.error(f"MQTT连接测试异常: {e}")
            return False
    
    def _test_http_connection(self, device_token: str) -> bool:
        """测试HTTP连接"""
        try:
            # 发送测试遥测数据
            telemetry_data = {
                "test": "connection_test",
                "timestamp": int(time.time() * 1000)
            }
            
            response = requests.post(
                f"http://{self.host}:8080/api/v1/{device_token}/telemetry",
                headers={"Content-Type": "application/json"},
                json=telemetry_data
            )
            
            if response.status_code == 200:
                logger.info(f"HTTP连接测试成功: {device_token}")
                return True
            else:
                logger.error(f"HTTP连接测试失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"HTTP连接测试异常: {e}")
            return False
    
    def export_devices_to_csv(self, devices: List[Dict], filename: str = "devices.csv"):
        """导出设备信息到CSV文件"""
        try:
            with open(filename, "w", newline='", encoding="utf-8') as csvfile:
                fieldnames = ["device_id", "device_name", "device_type", "access_token", 
                             "manufacturer", "model", "firmware_version", "created_time"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for device in devices:
                    additional_info = device.get("additionalInfo", {})
                    writer.writerow({
                        "device_id": device["id"]["id"],
                        "device_name": device["name"],
                        "device_type": device["type"],
                        "access_token": device.get("accessToken", ''),
                        "manufacturer": additional_info.get("manufacturer", ''),
                        "model": additional_info.get("model", ''),
                        "firmware_version": additional_info.get("firmwareVersion", ''),
                        "created_time": additional_info.get("createdAt", '')
                    })
            
            logger.info(f"设备信息已导出到: {filename}")
            
        except Exception as e:
            logger.error(f"导出CSV文件异常: {e}")
    
    def cleanup_devices(self, devices: List[Dict]) -> int:
        """清理测试设备"""
        logger.info(f"开始清理 {len(devices)} 个测试设备")
        
        cleaned_count = 0
        for device in devices:
            device_id = device["id"]["id"]
            device_name = device["name"]
            
            try:
                response = requests.delete(
                    f"{self.base_url}/api/device/{device_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"设备删除成功: {device_name}")
                    cleaned_count += 1
                else:
                    logger.error(f"设备删除失败: {device_name} - {response.status_code}")
                
                time.sleep(0.1)  # 添加延迟
                
            except Exception as e:
                logger.error(f"删除设备异常: {device_name} - {e}")
        
        logger.info(f"设备清理完成，成功: {cleaned_count}/{len(devices)}")
        return cleaned_count
    
    def run_comprehensive_test(self, device_count: int = 10, test_connection: bool = True):
        """运行完整的设备预注册测试"""
        logger.info("开始运行设备预注册综合测试")
        
        # 1. 批量创建设备
        devices = self.batch_create_devices(device_count)
        if not devices:
            logger.error("设备创建失败，测试终止")
            return
        
        # 2. 生成设备令牌
        devices_with_tokens = self.generate_device_tokens(devices)
        if not devices_with_tokens:
            logger.error("令牌生成失败，测试终止")
            return
        
        # 3. 测试设备连接
        if test_connection:
            connection_results = []
            for device in devices_with_tokens:
                token = device.get("accessToken")
                if token:
                    mqtt_result = self.test_device_connection(token, "mqtt")
                    http_result = self.test_device_connection(token, "http")
                    connection_results.append({
                        "device_name": device["name"],
                        "mqtt_connection": mqtt_result,
                        "http_connection": http_result
                    })
            
            # 统计连接结果
            mqtt_success = sum(1 for r in connection_results if r["mqtt_connection"])
            http_success = sum(1 for r in connection_results if r["http_connection"])
            logger.info(f"连接测试结果 - MQTT: {mqtt_success}/{len(connection_results)}, HTTP: {http_success}/{len(connection_results)}")
        
        # 4. 导出设备信息
        self.export_devices_to_csv(devices_with_tokens)
        
        # 5. 保存测试结果
        self.registered_devices = devices_with_tokens
        
        logger.info("设备预注册综合测试完成")
        return devices_with_tokens

# 使用示例
if __name__ == "__main__":
    # 创建测试器实例
    tester = DevicePreRegistrationTester(host="localhost", port=9090)
    
    # 登录（可选，如果已有Token）
    # tester.login("tenant@thingsboard.org", "tenant")
    
    # 运行综合测试
    devices = tester.run_comprehensive_test(device_count=5, test_connection=True)
    
    # 查看结果
    if devices:
        print(f"\n成功预注册 {len(devices)} 个设备:")
        for device in devices:
            print(f"  - {device["name"]}: {device.get("accessToken", "N/A")}")
    
    # 清理测试设备（可选）
    # tester.cleanup_devices(devices)
```

##### 8.2.3.3 Shell脚本版本

```bash
#!/bin/bash
# ThingsBoard设备预注册测试脚本

# 配置参数
THINGSBOARD_HOST="localhost"
THINGSBOARD_PORT="9090"
USER_TOKEN="YOUR_USER_TOKEN"
DEVICE_COUNT=10
DEVICE_PREFIX="TestDevice"

# 颜色输出
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m" # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 创建设备函数
create_device() {
    local device_name=$1
    local device_type=${2:-"default"}
    
    log_info "创建设备: $device_name"
    
    response=$(curl -s -X POST "http://$THINGSBOARD_HOST:$THINGSBOARD_PORT/api/device" \
        -H "Content-Type: application/json" \
        -H "X-Authorization: Bearer $USER_TOKEN" \
        -d "{
            \"name\": \"$device_name\",
            \"type\": \"$device_type\",
            \"additionalInfo\": {
                \"description\": \"Pre-registered device for testing\",
                \"manufacturer\": \"TestManufacturer\",
                \"model\": \"TestModel\",
                \"firmwareVersion\": \"1.0.0\",
                \"createdAt\": $(date +%s)000
            }
        }")
    
    if [ $? -eq 0 ]; then
        device_id=$(echo "$response" | jq -r ".id.id")
        if [ "$device_id" != "null" ] && [ "$device_id" != "" ]; then
            log_info "设备创建成功: $device_name (ID: $device_id)"
            echo "$device_id"
        else
            log_error "设备创建失败: $device_name"
            echo ""
        fi
    else
        log_error "设备创建请求失败: $device_name"
        echo ""
    fi
}

# 生成设备令牌函数
generate_device_token() {
    local device_id=$1
    local device_name=$2
    
    log_info "为设备生成令牌: $device_name"
    
    # 生成唯一令牌
    token="DEVICE_TOKEN_${device_name}_$(date +%s)_$(openssl rand -hex 4)"
    
    response=$(curl -s -X POST "http://$THINGSBOARD_HOST:$THINGSBOARD_PORT/api/device/$device_id/credentials" \
        -H "Content-Type: application/json" \
        -H "X-Authorization: Bearer $USER_TOKEN" \
        -d "{
            \"credentialsType\": \"ACCESS_TOKEN\",
            \"credentialsId\": \"$token\"
        }")
    
    if [ $? -eq 0 ]; then
        log_info "令牌生成成功: $device_name -> $token"
        echo "$token"
    else
        log_error "令牌生成失败: $device_name"
        echo ""
    fi
}

# 测试设备连接函数
test_device_connection() {
    local device_token=$1
    local device_name=$2
    
    log_info "测试设备连接: $device_name"
    
    # 测试HTTP连接
    response=$(curl -s -X POST "http://$THINGSBOARD_HOST:8080/api/v1/$device_token/telemetry" \
        -H "Content-Type: application/json" \
        -d "{
            \"test\": \"connection_test\",
            \"timestamp\": $(date +%s)000
        }")
    
    if [ $? -eq 0 ]; then
        log_info "HTTP连接测试成功: $device_name"
        return 0
    else
        log_error "HTTP连接测试失败: $device_name"
        return 1
    fi
}

# 主函数
main() {
    log_info "开始设备预注册测试，设备数量: $DEVICE_COUNT"
    
    # 创建结果文件
    result_file="device_registration_$(date +%Y%m%d_%H%M%S).csv"
    echo "device_id,device_name,device_type,access_token,created_time" > "$result_file"
    
    success_count=0
    
    for i in $(seq 1 $DEVICE_COUNT); do
        device_name="${DEVICE_PREFIX}_$(printf "%03d" $i)"
        
        # 创建设备
        device_id=$(create_device "$device_name")
        if [ -z "$device_id" ]; then
            continue
        fi
        
        # 生成令牌
        device_token=$(generate_device_token "$device_id" "$device_name")
        if [ -z "$device_token" ]; then
            continue
        fi
        
        # 测试连接
        if test_device_connection "$device_token" "$device_name"; then
            success_count=$((success_count + 1))
        fi
        
        # 保存结果
        echo "$device_id,$device_name,default,$device_token,$(date +%s)000" >> "$result_file"
        
        # 添加延迟
        sleep 0.5
    done
    
    log_info "设备预注册测试完成"
    log_info "成功注册设备: $success_count/$DEVICE_COUNT"
    log_info "结果文件: $result_file"
}

# 运行主函数
main "$@"
```

#### 8.2.3 遥测数据测试

```bash
# 上报遥测数据
curl -X POST http://localhost:9090/api/plugins/telemetry/DEVICE/{deviceId}/values/timeseries \
  -H "Content-Type: application/json" \
  -H "X-Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "temperature": 25.5,
    "humidity": 60.2,
    "pressure": 1013.25
  }'

# 查询遥测数据
curl -X GET "http://localhost:9090/api/plugins/telemetry/DEVICE/{deviceId}/values/timeseries?keys=temperature,humidity&startTs=1640995200000&endTs=1641081600000" \
  -H "X-Authorization: Bearer YOUR_TOKEN"
```

#### 8.2.4 Postman测试集合

```json
{
  "info": {
    "name": "ThingsBoard API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"tenant@thingsboard.org\",\n  \"password\": \"tenant\"\n}"
            },
            "url": {
              "raw": "http://localhost:9090/api/auth/login",
              "protocol": "http",
              "host": ["localhost"],
              "port": "9090",
              "path": ["api", "auth", "login"]
            }
          }
        }
      ]
    },
    {
      "name": "Device Management",
      "item": [
        {
          "name": "Create Device",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "X-Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Test Device\",\n  \"type\": \"default\"\n}"
            },
            "url": {
              "raw": "http://localhost:9090/api/device",
              "protocol": "http",
              "host": ["localhost"],
              "port": "9090",
              "path": ["api", "device"]
            }
          }
        }
      ]
    }
  ]
}
```

### 8.3 MQTT协议测试

#### 8.3.1 MQTT.fx配置

1. **连接配置**
   - Broker: `localhost`
   - Port: `1883`
   - Client ID: `test_device_001`
   - Username: `{deviceToken}` (设备Token)
   - Password: 留空

2. **测试脚本**

```python
# 使用Python paho-mqtt库测试
import paho.mqtt.client as mqtt
import json
import time

# 设备Token
DEVICE_TOKEN = "YOUR_DEVICE_TOKEN"
BROKER = "localhost"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # 订阅命令主题
    client.subscribe("v1/devices/me/commands/request/+")

def on_message(client, userdata, msg):
    print(f"Received command: {msg.topic} {str(msg.payload)}")
    # 解析命令并响应
    try:
        command_data = json.loads(msg.payload)
        request_id = msg.topic.split("/")[-1]
        
        # 发送命令响应
        response = {
            "status": "SUCCESS",
            "data": {"result": "Command executed successfully"}
        }
        client.publish(f"v1/devices/me/commands/response/{request_id}", 
                      json.dumps(response))
    except Exception as e:
        print(f"Error processing command: {e}")

def on_publish(client, userdata, mid):
    print(f"Message published with mid: {mid}")

# 创建客户端
client = mqtt.Client()
client.username_pw_set(DEVICE_TOKEN, "")
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# 连接MQTT Broker
client.connect(BROKER, PORT, 60)

# 发布遥测数据
telemetry_data = {
    "temperature": 25.5,
    "humidity": 60.2,
    "timestamp": int(time.time() * 1000)
}

client.publish("v1/devices/me/telemetry", json.dumps(telemetry_data))

# 发布属性数据
attributes_data = {
    "firmware_version": "1.0.0",
    "device_model": "TestDevice"
}

client.publish("v1/devices/me/attributes", json.dumps(attributes_data))

# 保持连接
client.loop_forever()
```

#### 8.3.2 命令下发测试

```bash
# 使用mosquitto_pub发送命令
mosquitto_pub -h localhost -p 1883 -u "YOUR_DEVICE_TOKEN" \
  -t "v1/devices/me/commands/request/1" \
  -m "{"method": "setTemperature", "params": {"temperature": 26.0}}"

# 监听命令响应
mosquitto_sub -h localhost -p 1883 -u "YOUR_DEVICE_TOKEN" \
  -t "v1/devices/me/commands/response/+"
```

### 8.4 WebSocket测试

#### 8.4.1 JavaScript WebSocket客户端

```html
<!DOCTYPE html>
<html>
<head>
    <title>ThingsBoard WebSocket Test</title>
</head>
<body>
    <h2>ThingsBoard WebSocket Test</h2>
    <div id="messages"></div>
    <script>
        const token = "YOUR_USER_TOKEN";
        const ws = new WebSocket(`ws://localhost:8080/api/ws/plugins/telemetry?token=${token}`);
        
        ws.onopen = function(event) {
            console.log("WebSocket connected");
            document.getElementById("messages").innerHTML += "<p>Connected to ThingsBoard</p>";
            
            // 订阅设备数据
            const subscribeMessage = {
                deviceId: "device_001",
                keys: ["temperature", "humidity"],
                startTs: Date.now() - 3600000, // 1小时前
                endTs: Date.now(),
                interval: 1000,
                limit: 100,
                agg: "AVG"
            };
            
            ws.send(JSON.stringify(subscribeMessage));
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log("Received:", data);
            document.getElementById("messages").innerHTML += 
                `<p>Received: ${JSON.stringify(data)}</p>`;
        };
        
        ws.onerror = function(error) {
            console.error("WebSocket error:", error);
            document.getElementById("messages").innerHTML += 
                `<p style="color: red;">Error: ${error}</p>`;
        };
        
        ws.onclose = function(event) {
            console.log("WebSocket closed");
            document.getElementById("messages").innerHTML += 
                "<p>Connection closed</p>";
        };
    </script>
</body>
</html>
```

#### 8.4.2 Python WebSocket客户端

```python
import asyncio
import websockets
import json

async def test_websocket():
    token = "YOUR_USER_TOKEN"
    uri = f"ws://localhost:8080/api/ws/plugins/telemetry?token={token}"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to ThingsBoard WebSocket")
        
        # 订阅设备数据
        subscribe_message = {
            "deviceId": "device_001",
            "keys": ["temperature", "humidity"],
            "startTs": int(time.time() * 1000) - 3600000,
            "endTs": int(time.time() * 1000),
            "interval": 1000,
            "limit": 100,
            "agg": "AVG"
        }
        
        await websocket.send(json.dumps(subscribe_message))
        print(f"Sent subscription: {subscribe_message}")
        
        # 接收消息
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received: {data}")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed")
                break
            except Exception as e:
                print(f"Error: {e}")
                break

# 运行测试
asyncio.run(test_websocket())
```

### 8.5 CoAP协议测试

#### 8.5.1 使用coap-client测试

```bash
# 安装coap-client
sudo apt-get install libcoap2-bin

# 上报遥测数据
coap-client -m POST \
  -H "Content-Type: application/json" \
  -e "{"temperature": 25.5, "humidity": 60.2}" \
  coap://localhost:5683/api/v1/YOUR_DEVICE_TOKEN/telemetry

# 上报属性数据
coap-client -m POST \
  -H "Content-Type: application/json" \
  -e "{"firmware_version": "1.0.0"}" \
  coap://localhost:5683/api/v1/YOUR_DEVICE_TOKEN/attributes

# 获取属性
coap-client -m GET \
  coap://localhost:5683/api/v1/YOUR_DEVICE_TOKEN/attributes
```

#### 8.5.2 Python CoAP客户端

```python
import asyncio
from aiocoap import Context, Message
import json

async def test_coap():
    context = await Context.create_client_context()
    
    device_token = "YOUR_DEVICE_TOKEN"
    
    # 上报遥测数据
    telemetry_data = {
        "temperature": 25.5,
        "humidity": 60.2,
        "timestamp": int(time.time() * 1000)
    }
    
    payload = json.dumps(telemetry_data).encode("utf-8")
    
    request = Message(
        code=1,  # POST
        uri=f"coap://localhost:5683/api/v1/{device_token}/telemetry",
        payload=payload,
        opt=Message.opt.ContentFormat(50)  # application/json
    )
    
    try:
        response = await context.request(request).response
        print(f"Telemetry response: {response.code}")
        print(f"Response payload: {response.payload.decode()}")
    except Exception as e:
        print(f"Error sending telemetry: {e}")
    
    await context.shutdown()

# 运行测试
asyncio.run(test_coap())
```

### 8.6 HTTP设备接口测试

#### 8.6.1 设备数据上报测试

```bash
# 上报遥测数据
curl -X POST "http://localhost:8080/api/v1/YOUR_DEVICE_TOKEN/telemetry" \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 25.5,
    "humidity": 60.2,
    "pressure": 1013.25
  }'

# 上报属性
curl -X POST "http://localhost:8080/api/v1/YOUR_DEVICE_TOKEN/attributes" \
  -H "Content-Type: application/json" \
  -d '{
    "firmware_version": "1.0.0",
    "device_model": "TestDevice"
  }'

# 获取属性
curl -X GET "http://localhost:8080/api/v1/YOUR_DEVICE_TOKEN/attributes"
```

#### 8.6.2 命令处理测试

```bash
# 获取命令（长轮询）
curl -X GET "http://localhost:8080/api/v1/YOUR_DEVICE_TOKEN/commands?timeout=10000"

# 响应命令
curl -X POST "http://localhost:8080/api/v1/YOUR_DEVICE_TOKEN/commands/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "SUCCESS",
    "data": {
      "result": "Temperature set to 26.0"
    }
  }'
```

### 8.7 自动化测试脚本

#### 8.7.1 综合测试脚本

```python
#!/usr/bin/env python3
"""
ThingsBoard接口综合测试脚本
"""

import requests
import json
import time
import paho.mqtt.client as mqtt
import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor

class ThingsBoardTester:
    def __init__(self, host="localhost", port=9090, device_token=None, user_token=None):
        self.host = host
        self.port = port
        self.device_token = device_token
        self.user_token = user_token
        self.base_url = f"http://{host}:{port}"
        
    def test_rest_api(self):
        """测试REST API接口"""
        print("=== Testing REST API ===")
        
        # 测试设备创建
        device_data = {
            "name": f"TestDevice_{int(time.time())}",
            "type": "default"
        }
        
        headers = {"Content-Type": "application/json"}
        if self.user_token:
            headers["X-Authorization"] = f"Bearer {self.user_token}"
        
        response = requests.post(
            f"{self.base_url}/api/device",
            headers=headers,
            json=device_data
        )
        
        if response.status_code == 200:
            device_id = response.json()["id"]["id"]
            print(f"✓ Device created: {device_id}")
            
            # 测试遥测数据上报
            telemetry_data = {
                "temperature": 25.5,
                "humidity": 60.2
            }
            
            response = requests.post(
                f"{self.base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries",
                headers=headers,
                json=telemetry_data
            )
            
            if response.status_code == 200:
                print("✓ Telemetry data sent successfully")
            else:
                print(f"✗ Failed to send telemetry: {response.status_code}")
        else:
            print(f"✗ Failed to create device: {response.status_code}")
    
    def test_mqtt(self):
        """测试MQTT协议"""
        print("=== Testing MQTT ===")
        
        if not self.device_token:
            print("✗ Device token required for MQTT test")
            return
        
        def on_connect(client, userdata, flags, rc):
            print(f"✓ MQTT connected with result code {rc}")
            
        def on_publish(client, userdata, mid):
            print(f"✓ Message published with mid: {mid}")
            
        client = mqtt.Client()
        client.username_pw_set(self.device_token, "")
        client.on_connect = on_connect
        client.on_publish = on_publish
        
        try:
            client.connect(self.host, 1883, 60)
            client.loop_start()
            
            # 发布遥测数据
            telemetry_data = {
                "temperature": 25.5,
                "humidity": 60.2,
                "timestamp": int(time.time() * 1000)
            }
            
            client.publish("v1/devices/me/telemetry", json.dumps(telemetry_data))
            time.sleep(1)
            
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            print(f"✗ MQTT test failed: {e}")
    
    def test_http_device_api(self):
        """测试HTTP设备接口"""
        print("=== Testing HTTP Device API ===")
        
        if not self.device_token:
            print("✗ Device token required for HTTP device API test")
            return
        
        # 上报遥测数据
        telemetry_data = {
            "temperature": 25.5,
            "humidity": 60.2
        }
        
        response = requests.post(
            f"http://{self.host}:8080/api/v1/{self.device_token}/telemetry",
            headers={"Content-Type": "application/json"},
            json=telemetry_data
        )
        
        if response.status_code == 200:
            print("✓ HTTP telemetry data sent successfully")
        else:
            print(f"✗ HTTP telemetry failed: {response.status_code}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("Starting ThingsBoard interface tests...")
        
        # 并行运行测试
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.test_rest_api)
            executor.submit(self.test_mqtt)
            executor.submit(self.test_http_device_api)
        
        print("All tests completed!")

# 使用示例
if __name__ == "__main__":
    # 配置测试参数
    tester = ThingsBoardTester(
        host="localhost",
        port=9090,
        device_token="YOUR_DEVICE_TOKEN",
        user_token="YOUR_USER_TOKEN"
    )
    
    # 运行测试
    tester.run_all_tests()
```

#### 8.7.2 性能测试脚本

```python
#!/usr/bin/env python3
"""
ThingsBoard接口性能测试脚本
"""

import time
import threading
import statistics
import requests
import paho.mqtt.client as mqtt
import json

class PerformanceTester:
    def __init__(self, host="localhost", device_token=None):
        self.host = host
        self.device_token = device_token
        self.results = []
        
    def test_rest_api_performance(self, num_requests=100):
        """测试REST API性能"""
        print(f"Testing REST API performance with {num_requests} requests...")
        
        times = []
        for i in range(num_requests):
            start_time = time.time()
            
            # 发送遥测数据
            telemetry_data = {
                "temperature": 25.5 + (i % 10),
                "humidity": 60.2 + (i % 5),
                "timestamp": int(time.time() * 1000)
            }
            
            response = requests.post(
                f"http://{self.host}:9090/api/plugins/telemetry/DEVICE/test_device/values/timeseries",
                headers={"Content-Type": "application/json"},
                json=telemetry_data
            )
            
            end_time = time.time()
            times.append(end_time - start_time)
            
            if (i + 1) % 10 == 0:
                print(f"Completed {i + 1}/{num_requests} requests")
        
        # 计算统计信息
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        
        print(f"REST API Performance Results:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print(f"  95th percentile: {p95_time:.3f}s")
        
        return {
            "protocol": "REST",
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "p95_time": p95_time
        }
    
    def test_mqtt_performance(self, num_messages=100):
        """测试MQTT性能"""
        print(f"Testing MQTT performance with {num_messages} messages...")
        
        if not self.device_token:
            print("Device token required for MQTT test")
            return None
        
        times = []
        messages_sent = 0
        
        def on_connect(client, userdata, flags, rc):
            print("MQTT connected")
            
        def on_publish(client, userdata, mid):
            nonlocal messages_sent
            messages_sent += 1
            if messages_sent == num_messages:
                client.disconnect()
        
        client = mqtt.Client()
        client.username_pw_set(self.device_token, "")
        client.on_connect = on_connect
        client.on_publish = on_publish
        
        client.connect(self.host, 1883, 60)
        client.loop_start()
        
        # 发送消息
        for i in range(num_messages):
            start_time = time.time()
            
            telemetry_data = {
                "temperature": 25.5 + (i % 10),
                "humidity": 60.2 + (i % 5),
                "timestamp": int(time.time() * 1000)
            }
            
            client.publish("v1/devices/me/telemetry", json.dumps(telemetry_data))
            times.append(time.time() - start_time)
        
        # 等待所有消息发送完成
        while messages_sent < num_messages:
            time.sleep(0.1)
        
        client.loop_stop()
        
        # 计算统计信息
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        p95_time = statistics.quantiles(times, n=20)[18]
        
        print(f"MQTT Performance Results:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print(f"  95th percentile: {p95_time:.3f}s")
        
        return {
            "protocol": "MQTT",
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "p95_time": p95_time
        }
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("Starting ThingsBoard performance tests...")
        
        # 测试REST API性能
        rest_results = self.test_rest_api_performance(100)
        
        # 测试MQTT性能
        mqtt_results = self.test_mqtt_performance(100)
        
        # 比较结果
        if rest_results and mqtt_results:
            print("\nPerformance Comparison:")
            print(f"REST API avg: {rest_results["avg_time"]:.3f}s")
            print(f"MQTT avg: {mqtt_results["avg_time"]:.3f}s")
            
            if rest_results["avg_time"] < mqtt_results["avg_time"]:
                print("REST API is faster")
            else:
                print("MQTT is faster")

# 使用示例
if __name__ == "__main__":
    tester = PerformanceTester(
        host="localhost",
        device_token="YOUR_DEVICE_TOKEN"
    )
    
    tester.run_performance_tests()
```

## 9. 参考资源

- [ThingsBoard官方文档](https://thingsboard.io/docs/)
- [ThingsBoard API参考](https://thingsboard.io/docs/reference/rest-api/)
- [ThingsBoard MQTT API](https://thingsboard.io/docs/reference/mqtt-api/)
- [ThingsBoard WebSocket API](https://thingsboard.io/docs/reference/websocket-api/)
- [ThingsBoard测试工具](https://thingsboard.io/docs/user-guide/contribution/testing/)

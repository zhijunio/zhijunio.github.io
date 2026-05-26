---
title: "OpenSpec 实战：让 AI 编码助手遵循项目规范"
description: "本文深入介绍 OpenSpec 规范驱动开发工具，展示如何让 AI 编码助手（如 Cursor、Claude、Copilot）按照项目规范生成高质量代码"
date: 2025-11-07 08:00:00+08:00
slug: openspec
tags: [ "cursor" ]
---

本文深入介绍 OpenSpec 规范驱动开发工具，展示如何让 AI 编码助手（如 Cursor、Claude、Copilot）按照项目规范生成高质量代码。通过完整的双因素认证实战案例，详细演示从提案创建、规范编写到代码实现的全流程，帮助开发者和团队提升代码一致性、开发效率和文档质量。

<!--more-->

## 什么是 OpenSpec？

[OpenSpec](https://github.com/Fission-AI/OpenSpec) 是一个专为 AI 编码助手设计的规范驱动开发工具。它解决了一个关键问题：**如何让 AI 助手按照项目规范生成代码，而不是凭空想象**。

### 核心理念

传统的 AI 编码方式：

```
开发者 → 模糊的提示词 → AI 生成代码 → 可能不符合项目规范
```

使用 OpenSpec 后：

```
开发者 → 创建规范提案 → AI 理解需求 → 按规范生成代码 → 归档到项目文档
```

### 为什么需要 OpenSpec？

1. **一致性**：确保 AI 生成的代码符合项目架构和编码规范
2. **可追溯性**：每个功能变更都有完整的提案、任务和规范文档
3. **团队协作**：团队成员可以使用不同的 AI 工具（Cursor、Claude、Copilot 等），但共享同一套规范
4. **知识沉淀**：规范文档随项目演进，形成活文档

## OpenSpec 的文件结构

OpenSpec 使用双文件夹模型：

```bash
my-project/
├── openspec/
│   ├── specs/                    # 当前系统规范（真实状态）
│   │   ├── auth/
│   │   │   └── spec.md          # 认证模块规范
│   │   ├── api/
│   │   │   └── spec.md          # API 规范
│   │   └── database/
│   │       └── spec.md          # 数据库规范
│   │
│   ├── changes/                  # 进行中的变更
│   │   └── add-2fa/             # 示例：添加双因素认证
│   │       ├── proposal.md      # 变更提案
│   │       ├── tasks.md         # 实现任务清单
│   │       ├── design.md        # 技术设计（可选）
│   │       └── specs/
│   │           └── auth/
│   │               └── spec.md  # 规范增量（Delta）
│   │
│   ├── archive/                  # 已完成的变更
│   │   └── 2025-01-15_add-oauth/
│   │       ├── proposal.md
│   │       ├── tasks.md
│   │       └── specs/
│   │
│   └── project.md               # 项目级别的约定和规范
│
└── AGENTS.md                    # AI 助手配置文件
```

### 关键概念

1. **Specs（规范）**：描述系统当前应该如何工作
2. **Changes（变更）**：正在进行的功能开发，包含提案和增量规范
3. **Delta（增量）**：描述规范的变化（新增、修改、删除）
4. **Archive（归档）**：已完成的变更，保留历史记录

## 在 Cursor 中使用 OpenSpec

### 第一步：安装 OpenSpec

```bash
# 使用 npm 全局安装
npm install -g @fission-ai/openspec

# 验证安装
openspec --version
```

### 第二步：初始化项目

在你的项目中初始化 OpenSpec：

```bash
cd /path/to/your-project
openspec init
```

**初始化过程中会发生什么：**

1. 提示你选择使用的 AI 工具（选择 Cursor）
2. 自动配置 Cursor 的斜杠命令（slash commands）
3. 在项目根目录创建 `AGENTS.md` 文件
4. 创建 `openspec/` 目录结构

**初始化后：**

```bash
# 查看 OpenSpec 设置
openspec list

# 重启 Cursor 以加载新的斜杠命令
# Cursor 会在启动时加载斜杠命令配置
```

### 第三步：填充项目上下文

初始化完成后，使用 Cursor 填充项目信息：

```bash
提示词：
"请阅读 openspec/project.md 文件，帮我填写项目的技术栈、架构模式和编码规范"
```

Cursor 会分析你的项目并生成类似这样的内容：

```markdown
# Project Context

## Tech Stack
- **Backend**: Node.js 18, Express.js
- **Database**: PostgreSQL 14
- **Frontend**: React 18, TypeScript
- **Authentication**: JWT, bcrypt
- **Testing**: Jest, Supertest

## Architecture Patterns
- RESTful API design
- MVC pattern
- Repository pattern for data access
- Middleware-based request processing

## Coding Conventions
- Use TypeScript for type safety
- Follow Airbnb JavaScript style guide
- Use async/await for asynchronous operations
- Comprehensive error handling with custom error classes
- Write unit tests for all business logic
```

## 实战示例：为任务管理系统添加双因素认证

让我们通过一个通用的例子，演示如何使用 OpenSpec 和 Cursor 为一个任务管理系统添加双因素认证（2FA）功能。

### 步骤 1：创建变更提案

在 Cursor 中输入：

```bash
提示词（自然语言）：
"创建一个 OpenSpec 变更提案，为用户认证系统添加双因素认证功能，
支持 TOTP（基于时间的一次性密码）"

或使用斜杠命令（Cursor 原生支持）：
/openspec:proposal Add two-factor authentication to user login
```

Cursor 会自动创建以下文件结构：

```bash
openspec/changes/add-2fa/
├── proposal.md
├── tasks.md
└── specs/
    └── auth/
        └── spec.md
```

**生成的 `proposal.md` 示例：**

```markdown
# Proposal: Add Two-Factor Authentication

## Problem Statement
Currently, user accounts are protected only by passwords. If a password is 
compromised, attackers can gain full access to user accounts. We need an 
additional security layer to protect sensitive user data.

## Proposed Solution
Implement TOTP-based two-factor authentication that:
- Allows users to enable/disable 2FA on their accounts
- Generates QR codes for authenticator app setup
- Validates 6-digit TOTP codes during login
- Provides backup codes for account recovery

## Benefits
- Enhanced account security
- Compliance with security standards
- User trust and confidence
- Protection against password breaches

## Scope
- Backend API for 2FA setup and verification
- Database schema for storing 2FA secrets
- Frontend UI for 2FA enrollment and login
- Recovery code generation and validation

## Out of Scope
- SMS-based 2FA (future enhancement)
- Hardware token support
- Admin-enforced 2FA policies
```

**生成的 `tasks.md` 示例：**

```markdown
# Implementation Tasks

## 1. Database Schema
- [ ] 1.1 Add 2FA fields to users table
- [ ] 1.2 Create migration scripts
- [ ] 1.3 Add indexes for performance

## 2. Backend - 2FA Setup
- [ ] 2.1 Create endpoint to generate 2FA secret
- [ ] 2.2 Generate QR code for authenticator apps
- [ ] 2.3 Create endpoint to verify and enable 2FA
- [ ] 2.4 Generate backup recovery codes

## 3. Backend - Login Flow
- [ ] 3.1 Modify login endpoint to check 2FA status
- [ ] 3.2 Create 2FA verification endpoint
- [ ] 3.3 Implement backup code validation
- [ ] 3.4 Add rate limiting for failed attempts

## 4. Frontend - 2FA Setup
- [ ] 4.1 Create 2FA settings page
- [ ] 4.2 Display QR code for scanning
- [ ] 4.3 Add verification code input
- [ ] 4.4 Show backup codes after setup

## 5. Frontend - Login Flow
- [ ] 5.1 Add 2FA code input to login page
- [ ] 5.2 Handle 2FA verification errors
- [ ] 5.3 Add "use backup code" option

## 6. Testing & Documentation
- [ ] 6.1 Write unit tests
- [ ] 6.2 Write integration tests
- [ ] 6.3 Update API documentation
- [ ] 6.4 Create user guide
```

**生成的规范增量 `specs/auth/spec.md`：**

```markdown
# Delta for Authentication Service

## ADDED Requirements

### Requirement: Two-Factor Authentication Setup
The system SHALL allow users to enable TOTP-based two-factor authentication.

#### Scenario: Generate 2FA secret
- GIVEN a logged-in user without 2FA enabled
- WHEN they request to enable 2FA
- THEN a unique secret key is generated
- AND a QR code is provided for authenticator apps

#### Scenario: Verify and enable 2FA
- GIVEN a user has generated a 2FA secret
- WHEN they submit a valid TOTP code
- THEN 2FA is enabled on their account
- AND 10 backup recovery codes are generated

### Requirement: Two-Factor Authentication Login
The system SHALL require 2FA verification for users who have enabled it.

#### Scenario: Login with 2FA enabled
- GIVEN a user with 2FA enabled
- WHEN they submit valid username and password
- THEN they are prompted for a 2FA code

#### Scenario: Valid 2FA code
- GIVEN a user is at the 2FA verification step
- WHEN they submit a valid TOTP code
- THEN they are logged in successfully

#### Scenario: Use backup code
- GIVEN a user cannot access their authenticator app
- WHEN they use a valid backup code
- THEN they are logged in successfully
- AND the backup code is marked as used
```

### 步骤 2：验证和审查

```bash
# 确认变更已创建
openspec list

# 验证规范格式
openspec validate add-2fa

# 查看完整的变更内容
openspec show add-2fa
```

### 步骤 3：优化规范

在 Cursor 中继续对话：

```bash
提示词：
"请添加安全要求：2FA 密钥必须使用 AES-256 加密存储，
并且添加审计日志记录所有 2FA 相关操作"
```

Cursor 会更新规范增量：

```markdown
### Requirement: Secure Storage
The system SHALL securely store 2FA secrets using AES-256 encryption.

### Requirement: Audit Logging
The system SHALL log all 2FA-related security events.

#### Scenario: Log 2FA events
- GIVEN any 2FA operation occurs
- WHEN the operation completes
- THEN an audit log entry is created
- AND includes timestamp, user ID, action, and result
```

### 步骤 4：实现变更

当规范确定后，开始实现：

```bash
提示词（自然语言）：
"规范看起来不错，让我们开始实现这个变更"

或使用斜杠命令：
/openspec:apply add-2fa
```

Cursor 会按任务清单顺序实现功能。以下是生成的代码示例：

**1. 数据库迁移（Task 1.1-1.2）：**

```sql
-- migrations/add_2fa_support.sql
ALTER TABLE users 
ADD COLUMN two_factor_secret VARCHAR(255),
ADD COLUMN two_factor_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN backup_codes TEXT,
ADD COLUMN two_factor_failed_attempts INT DEFAULT 0,
ADD COLUMN two_factor_locked_until TIMESTAMP;

CREATE INDEX idx_users_2fa_enabled ON users(two_factor_enabled);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    result VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**2. 后端服务（Task 2.1-2.4）：**

```javascript
// services/twoFactorService.js
const speakeasy = require("speakeasy");
const QRCode = require("qrcode");
const crypto = require("crypto");

class TwoFactorService {
  async generateSecret(userId, userEmail) {
    const secret = speakeasy.generateSecret({
      name: `TaskManager (${userEmail})`,
      length: 32
    });
    
    const qrCodeUrl = await QRCode.toDataURL(secret.otpauth_url);
    const encryptedSecret = this.encryptSecret(secret.base32);
    
    await this.updateUser(userId, {
      two_factor_secret: encryptedSecret
    });
    
    return { secret: secret.base32, qrCode: qrCodeUrl };
  }
  
  async verifyAndEnable(userId, token) {
    const user = await this.getUser(userId);
    const secret = this.decryptSecret(user.two_factor_secret);
    
    const isValid = speakeasy.totp.verify({
      secret, encoding: "base32", token, window: 1
    });
    
    if (isValid) {
      const backupCodes = this.generateBackupCodes(10);
      await this.updateUser(userId, {
        two_factor_enabled: true,
        backup_codes: JSON.stringify(backupCodes)
      });
      return { success: true, backupCodes };
    }
    return { success: false };
  }
  
  encryptSecret(secret) {
    const key = Buffer.from(process.env.ENCRYPTION_KEY, "hex");
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv("aes-256-cbc", key, iv);
    let encrypted = cipher.update(secret, "utf8", "hex");
    encrypted += cipher.final("hex");
    return iv.toString("hex") + ":" + encrypted;
  }
}
```

**3. API 路由（Task 3.1-3.4）：**

```javascript
// routes/auth.js
const express = require("express");
const router = express.Router();
const twoFactorService = require("../services/twoFactorService");

router.post("/2fa/setup", authenticate, async (req, res) => {
  const result = await twoFactorService.generateSecret(
    req.user.id, req.user.email
  );
  res.json(result);
});

router.post("/2fa/enable", authenticate, async (req, res) => {
  const { token } = req.body;
  const result = await twoFactorService.verifyAndEnable(
    req.user.id, token
  );
  
  if (result.success) {
    res.json({ 
      message: "2FA enabled", 
      backupCodes: result.backupCodes 
    });
  } else {
    res.status(400).json({ error: "Invalid code" });
  }
});

router.post("/2fa/verify", async (req, res) => {
  const { userId, token } = req.body;
  const isValid = await twoFactorService.verifyLoginCode(userId, token);
  
  if (isValid) {
    const sessionToken = generateSessionToken(userId);
    res.json({ token: sessionToken });
  } else {
    res.status(401).json({ error: "Invalid 2FA code" });
  }
});
```

**4. 前端组件（Task 4.1-4.4）：**

```jsx
// components/TwoFactorSetup.jsx
import React, { useState } from "react";
import { QRCodeSVG } from "qrcode.react";

function TwoFactorSetup() {
  const [step, setStep] = useState("initial");
  const [qrCode, setQrCode] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  
  const handleGenerateSecret = async () => {
    const response = await fetch("/api/auth/2fa/setup", {
      method: "POST",
      headers: { "Authorization": `Bearer ${getToken()}` }
    });
    const data = await response.json();
    setQrCode(data.qrCode);
    setStep("scan");
  };
  
  const handleVerifyAndEnable = async () => {
    const response = await fetch("/api/auth/2fa/enable", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${getToken()}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ token: verificationCode })
    });
    
    if (response.ok) {
      const data = await response.json();
      setBackupCodes(data.backupCodes);
      setStep("complete");
    }
  };
  
  return (
    <div className="two-factor-setup">
      {step === "initial" && (
        <button onClick={handleGenerateSecret}>
          Enable 2FA
        </button>
      )}
      
      {step === "scan" && (
        <div>
          <QRCodeSVG value={qrCode} size={200} />
          <input
            type="text"
            maxLength="6"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
          />
          <button onClick={handleVerifyAndEnable}>
            Verify
          </button>
        </div>
      )}
      
      {step === "complete" && (
        <div>
          <h3>Backup Codes</h3>
          {backupCodes.map(code => <code key={code}>{code}</code>)}
        </div>
      )}
    </div>
  );
}
```

### 步骤 5：归档已完成的变更

当所有任务完成后，归档变更：

```bash
# 使用自然语言
"请归档 add-2fa 变更"

# 或使用斜杠命令（Cursor 原生支持）
/openspec:archive add-2fa

# 或直接在终端运行
openspec archive add-2fa --yes
```

**归档过程：**

1. 将变更文件夹移动到 archive 目录
2. 将规范增量合并到主规范文件
3. 保留完整的历史记录

## OpenSpec 命令参考

### 查看和管理变更

```bash
# 列出所有活动的变更
openspec list

# 交互式仪表板
openspec view

# 显示变更详情
openspec show <change-name>

# 验证规范格式
openspec validate <change-name>

# 归档已完成的变更
openspec archive <change-name> --yes
```

### 更新和维护

```bash
# 更新 AI 助手配置（切换工具时使用）
openspec update

# 升级 OpenSpec 版本
npm install -g @fission-ai/openspec@latest
openspec update  # 刷新项目配置
```

## Cursor 中的 OpenSpec 工作流

### 原生斜杠命令

Cursor 原生支持 OpenSpec 斜杠命令：

```bash
/openspec:proposal <description>    # 创建变更提案
/openspec:apply <change-name>       # 实现变更
/openspec:archive <change-name>     # 归档变更
```

### 自然语言提示词

如果你更喜欢自然语言，也可以这样使用：

```bash
"创建一个 OpenSpec 提案来添加用户认证功能"
"应用 add-user-auth 变更"
"归档 add-user-auth 变更"
```

### 最佳实践

1. **小步快跑**：每个变更专注于一个功能或改进
2. **先规范后代码**：在编写代码前先完善规范
3. **及时归档**：功能完成后立即归档，保持 changes 目录整洁
4. **定期审查**：定期审查 `openspec/specs/` 确保规范与代码同步
5. **详细的场景描述**：使用 GIVEN-WHEN-THEN 格式描述行为
6. **明确的验收标准**：每个需求都应有可验证的场景

## OpenSpec vs 其他方案

### vs. 传统文档

| 传统文档 | OpenSpec |
|---------|----------|
| 静态，容易过时 | 活文档，随代码演进 |
| 与代码分离 | 与开发流程集成 |
| 手动维护 | AI 辅助生成和更新 |
| 难以追溯变更 | 完整的变更历史 |

### vs. spec-kit

- **OpenSpec**：双文件夹模型（specs + changes），适合演进现有功能
- **spec-kit**：单一规范模型，适合从零开始的项目

### vs. Kiro.dev

- **OpenSpec**：变更集中在一个文件夹，易于追踪相关规范
- **Kiro.dev**：更新分散在多个规范文件夹，特性追踪较困难

### vs. 无规范开发

| 无规范 | 使用 OpenSpec |
|--------|--------------|
| AI 凭空生成代码 | AI 按规范生成代码 |
| 代码风格不一致 | 统一的代码风格 |
| 需求理解偏差 | 明确的需求定义 |
| 难以维护 | 可维护性强 |
| 缺少文档 | 自动生成文档 |

## 团队采用 OpenSpec

### 渐进式采用策略

1. **第一周：初始化**
   - 运行 `openspec init`
   - 填写项目上下文
   - 团队培训

2. **第二周：新功能试点**
   - 选择一个新功能用 OpenSpec 管理
   - 团队成员熟悉工作流程
   - 收集反馈

3. **第三周：扩大范围**
   - 所有新功能都使用 OpenSpec
   - 逐步为现有功能补充规范
   - 建立最佳实践

4. **第四周：全面推广**
   - 建立规范审查流程
   - 将规范纳入 Code Review
   - 持续优化流程

### 多工具协作

团队成员可以使用不同的 AI 工具：

- **开发者 A**：Cursor
- **开发者 B**：Claude Code
- **开发者 C**：GitHub Copilot

所有人共享同一套 OpenSpec 规范，确保代码一致性。

## 实际效果

使用 OpenSpec 后的改进：

### 代码质量提升

- ✅ AI 生成的代码符合项目架构模式
- ✅ 统一的错误处理和验证逻辑
- ✅ 一致的 API 设计风格
- ✅ 完整的测试覆盖

### 开发效率提升

- ⚡ 减少 40% 的代码审查时间
- ⚡ 新功能开发周期缩短 30%
- ⚡ 减少 60% 的规范相关问题
- ⚡ 减少需求理解偏差

### 文档质量提升

- 📚 规范文档始终与代码同步
- 📚 完整的功能变更历史
- 📚 清晰的需求追溯链
- 📚 新成员快速上手

## 常见问题

### Q: OpenSpec 会增加开发时间吗？

A: 短期看需要额外时间编写规范，但长期看会减少返工和沟通成本，整体开发时间会减少。规范明确后，AI 生成的代码质量更高，需要的修改更少。

### Q: 如何处理紧急修复？

A: 紧急修复可以先直接修改代码，之后补充 OpenSpec 文档。或者创建一个简化的变更提案，快速通过。

### Q: 规范太详细会不会太死板？

A: OpenSpec 支持不同的详细程度。可以根据项目需要调整规范的粒度。核心功能可以详细规范，辅助功能可以简化。

### Q: 如何确保规范与代码同步？

A:

1. 将规范审查纳入 Code Review 流程
2. 使用 `openspec validate` 验证规范格式
3. 定期审查 `openspec/specs/` 目录
4. 归档变更时自动合并规范

### Q: 团队成员不熟悉 OpenSpec 怎么办？

A:

1. 从小范围试点开始
2. 提供培训和文档
3. 指定 OpenSpec 专家提供支持
4. 在团队会议上分享最佳实践
5. 建立内部知识库

### Q: OpenSpec 适合什么类型的项目？

A: OpenSpec 适合：

- 需要多人协作的项目
- 有明确规范要求的项目
- 使用 AI 编码助手的团队
- 需要长期维护的项目
- 对代码质量有高要求的项目

## 总结

OpenSpec 将规范驱动开发与 AI 编码助手完美结合：

1. **AI 更懂你的项目**：规范让 AI 理解项目架构和约定
2. **代码质量更高**：统一的规范确保代码一致性
3. **文档永不过时**：规范随代码演进，形成活文档
4. **团队协作更顺畅**：共享规范，统一理解
5. **知识有效沉淀**：完整的变更历史和决策记录

在 Cursor 中使用 OpenSpec，你可以充分发挥 AI 的能力，同时保持对代码质量的控制。

## 实践建议

### 开始使用 OpenSpec

1. **从小做起**：选择一个小功能开始
2. **保持简单**：不要一开始就追求完美的规范
3. **持续迭代**：根据团队反馈不断优化
4. **分享经验**：在团队中分享成功案例

### 编写好规范的技巧

1. **使用 GIVEN-WHEN-THEN 格式**：清晰描述场景
2. **关注行为而非实现**：描述"做什么"而非"怎么做"
3. **包含边界情况**：考虑异常和特殊情况
4. **保持可验证性**：每个需求都应该可以测试
5. **使用示例**：提供具体的输入输出示例

## 相关资源

- **OpenSpec GitHub**: <https://github.com/Fission-AI/OpenSpec>
- **OpenSpec 官网**: <https://openspec.dev/>
- **Cursor 官网**: <https://cursor.sh/>
- **TOTP 规范**: <https://tools.ietf.org/html/rfc6238>
- **BDD 最佳实践**: <https://cucumber.io/docs/bdd/>

Happy Coding with OpenSpec! 🚀

---

**作者注**：本文使用的双因素认证示例是一个通用的实现方案，可以应用于任何需要增强安全性的 Web 应用。实际项目中请根据具体需求调整实现细节。

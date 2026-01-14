# AURIX 跨境哨兵 - 风险检查系统文档

## 系统概述

AURIX 跨境哨兵是一个自动化的企业风险监控系统，用于监测跨境贸易公司的风险评分变化，并在风险发生显著变化时自动通知订阅用户。

## 核心功能

### 1. 风险评估引擎

系统通过多维度因素计算企业风险评分（0-100分）：

- **行业风险系数**：根据不同行业的固有风险特征
- **地区风险系数**：基于国家/地区的经营环境
- **市场波动因素**：实时市场变化对风险的影响
- **合规风险评估**：企业合规状况评估

### 2. 自动监控与通知

- 每日自动检查所有订阅公司的风险状况
- 对比历史风险评分，识别风险变化
- 当风险评分变化超过阈值（默认10分）时，自动发送邮件通知
- 提供详细的风险因素分析和建议措施

### 3. 日志记录系统

完整记录所有检查活动：

- 风险检查日志：`logs/risk-check.log`
- 邮件通知日志：`logs/email-notifications.log`
- 邮件内容存档：`logs/emails/`

## 技术架构

### 技术栈

- **后端框架**：Node.js + Express + TypeScript
- **API 框架**：tRPC (类型安全的 RPC 框架)
- **数据存储**：JSON 文件数据库（可扩展为 MySQL/PostgreSQL）
- **邮件服务**：Nodemailer（当前为模拟模式）
- **运行时**：tsx (TypeScript 执行器)

### 项目结构

```
aurixai-website/
├── src/
│   ├── server/
│   │   ├── api/
│   │   │   ├── routers/
│   │   │   │   └── riskChecker.ts    # 风险检查路由器
│   │   │   └── root.ts                # tRPC 主路由
│   │   ├── services/
│   │   │   ├── riskAssessment.ts      # 风险评估服务
│   │   │   └── emailService.ts        # 邮件通知服务
│   │   └── index.ts                   # Express 服务器
│   ├── lib/
│   │   └── database.ts                # 数据库服务
│   ├── types/
│   │   └── index.ts                   # TypeScript 类型定义
│   └── scripts/
│       └── dailyRiskCheck.ts          # 每日检查脚本
├── data/
│   ├── companies.json                 # 公司数据
│   └── subscriptions.json             # 订阅数据
├── logs/
│   ├── risk-check.log                 # 风险检查日志
│   ├── email-notifications.log        # 邮件通知日志
│   └── emails/                        # 邮件内容存档
├── package.json
├── tsconfig.json
└── README.md
```

## API 接口

### 1. 运行风险检查

**端点**：`POST /trpc/riskChecker.runCheck`

**请求参数**：

```typescript
{
  companyIds?: string[];      // 可选：指定要检查的公司ID列表
  forceNotify?: boolean;      // 可选：强制发送通知（忽略阈值）
}
```

**响应示例**：

```json
{
  "success": true,
  "summary": {
    "totalCompanies": 5,
    "totalNotifications": 1,
    "successfulNotifications": 1,
    "failedNotifications": 0,
    "duration": 773
  },
  "results": [
    {
      "companyId": "comp-004",
      "companyName": "杭州电子商务科技",
      "previousScore": 80,
      "currentScore": 99,
      "scoreChange": 19,
      "timestamp": "2026-01-14T10:30:46.041Z",
      "riskFactors": [
        "重大风险预警：风险评分大幅上升",
        "汇率波动加剧"
      ]
    }
  ],
  "notifications": [
    {
      "email": "manager1@example.com",
      "companyName": "杭州电子商务科技",
      "success": true
    }
  ]
}
```

### 2. 获取公司风险历史

**端点**：`GET /trpc/riskChecker.getCompanyRiskHistory`

**请求参数**：

```typescript
{
  companyId: string;  // 公司ID
}
```

## 数据模型

### Company（公司）

```typescript
interface Company {
  id: string;                    // 公司唯一标识
  name: string;                  // 公司名称
  country: string;               // 国家代码
  industry: string;              // 行业类别
  currentRiskScore: number;      // 当前风险评分 (0-100)
  previousRiskScore: number;     // 上次风险评分
  lastCheckedAt: Date;           // 最后检查时间
}
```

### Subscription（订阅）

```typescript
interface Subscription {
  id: string;                    // 订阅唯一标识
  userId: string;                // 用户ID
  companyId: string;             // 公司ID
  email: string;                 // 通知邮箱
  alertThreshold: number;        // 风险变化阈值（默认10分）
  isActive: boolean;             // 是否激活
}
```

### RiskCheckResult（检查结果）

```typescript
interface RiskCheckResult {
  companyId: string;             // 公司ID
  companyName: string;           // 公司名称
  previousScore: number;         // 之前评分
  currentScore: number;          // 当前评分
  scoreChange: number;           // 评分变化
  timestamp: Date;               // 检查时间
  riskFactors: string[];         // 风险因素列表
}
```

## 使用指南

### 安装依赖

```bash
cd /home/ubuntu/aurixai-website
pnpm install
```

### 运行服务器

```bash
# 开发模式（热重载）
pnpm run dev

# 生产模式
pnpm run build
pnpm start
```

### 执行风险检查

```bash
# 方式1：使用 npm script
pnpm run check

# 方式2：直接运行脚本
tsx src/scripts/dailyRiskCheck.ts
```

### 配置定时任务

使用 cron 配置每日自动执行：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上 9:00 执行）
0 9 * * * cd /home/ubuntu/aurixai-website && pnpm run check >> /home/ubuntu/aurixai-website/logs/cron.log 2>&1
```

## 风险评分说明

### 评分范围

- **0-30分**：低风险 - 经营状况良好，风险可控
- **31-60分**：中等风险 - 需要关注，建议加强监控
- **61-80分**：较高风险 - 需要采取风险管理措施
- **81-100分**：高风险 - 需要立即采取行动

### 风险变化阈值

- **变化 < 5分**：正常波动，无需特别关注
- **变化 5-10分**：轻微变化，持续监控
- **变化 10-15分**：显著变化，发送通知提醒
- **变化 > 15分**：重大变化，紧急通知并建议立即行动

## 邮件通知内容

邮件通知包含以下信息：

1. **风险等级变化**：显著/重大风险上升或下降
2. **公司基本信息**：公司名称、风险评分变化
3. **风险因素分析**：导致风险变化的主要因素
4. **建议措施**：根据风险等级提供针对性建议
5. **检测时间**：风险检查的具体时间

## 日志格式

### 风险检查日志

```json
{
  "timestamp": "2026-01-14T10:30:46.409Z",
  "duration": 773,
  "summary": {
    "totalCompanies": 5,
    "totalNotifications": 1,
    "successfulNotifications": 1,
    "failedNotifications": 0
  },
  "results": [...],
  "notifications": [...]
}
```

### 邮件通知日志

```json
{
  "timestamp": "2026-01-14T10:30:46.307Z",
  "email": "manager1@example.com",
  "companyId": "comp-004",
  "companyName": "杭州电子商务科技",
  "scoreChange": 19,
  "status": "success"
}
```

## 扩展建议

### 1. 数据库升级

当前使用 JSON 文件存储，建议升级为关系型数据库：

- MySQL / PostgreSQL：适合结构化数据
- MongoDB：适合灵活的文档存储
- 使用 Prisma 或 Drizzle ORM 简化数据库操作

### 2. 真实邮件服务

集成真实的邮件服务提供商：

- **SendGrid**：企业级邮件服务
- **AWS SES**：Amazon 简单邮件服务
- **阿里云邮件推送**：国内邮件服务
- **腾讯云邮件服务**：国内邮件服务

### 3. 风险数据源

接入真实的风险数据源：

- 企业征信 API（如天眼查、企查查）
- 海关数据 API
- 金融风险评估服务
- 供应链数据平台

### 4. 用户管理系统

添加完整的用户管理功能：

- 用户注册和登录
- 订阅管理界面
- 自定义风险阈值
- 历史数据查询

### 5. 实时监控

升级为实时监控系统：

- WebSocket 实时推送
- 移动端推送通知
- 微信/钉钉/企业微信集成
- 短信通知

### 6. 数据分析与可视化

添加数据分析功能：

- 风险趋势图表
- 行业风险对比
- 预测性分析
- 自定义报表

## 故障排查

### 常见问题

1. **依赖安装失败**
   ```bash
   # 清理缓存重新安装
   rm -rf node_modules pnpm-lock.yaml
   pnpm install
   ```

2. **TypeScript 编译错误**
   ```bash
   # 检查 TypeScript 版本
   pnpm list typescript
   # 重新编译
   pnpm run build
   ```

3. **邮件发送失败**
   - 检查邮件服务配置
   - 查看 `logs/email-notifications.log` 错误信息
   - 确认网络连接正常

4. **数据文件损坏**
   ```bash
   # 备份当前数据
   cp data/companies.json data/companies.json.bak
   # 重新初始化数据
   rm data/*.json
   pnpm run check
   ```

## 安全建议

1. **环境变量**：敏感信息（如 API 密钥）存储在环境变量中
2. **访问控制**：添加 API 认证和授权机制
3. **数据加密**：敏感数据加密存储
4. **日志脱敏**：日志中不记录敏感信息
5. **定期备份**：定期备份数据和日志文件

## 性能优化

1. **批量处理**：大量公司检查时使用批量处理
2. **缓存机制**：缓存频繁访问的数据
3. **异步处理**：邮件发送使用异步队列
4. **数据库索引**：升级数据库后添加适当索引
5. **监控告警**：添加性能监控和告警机制

## 联系支持

- **项目仓库**：https://github.com/dtt9696/aurixai-website
- **官方网站**：https://aurix.ai
- **技术支持**：support@aurix.ai

---

**版本**：1.0.0  
**最后更新**：2026-01-14  
**维护者**：AURIX 技术团队

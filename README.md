# AURIX 跨境哨兵

> 智能化跨境贸易企业风险监控系统

## 🎯 项目简介

AURIX 跨境哨兵是一个自动化的企业风险监控系统，专为跨境贸易企业设计。系统通过多维度风险评估模型，实时监测企业风险状况，并在风险发生显著变化时自动通知订阅用户，帮助企业及时发现和应对潜在风险。

## ✨ 核心功能

- 🔍 **智能风险评估**：基于行业、地区、市场波动等多维度因素计算企业风险评分
- 📊 **自动监控**：每日自动检查所有订阅公司的风险状况
- 📧 **智能通知**：风险变化超过阈值时自动发送邮件通知
- 📝 **完整日志**：记录所有检查活动和通知发送情况
- 🔌 **API 接口**：基于 tRPC 的类型安全 API 接口
- 📈 **风险分析**：提供详细的风险因素分析和建议措施

## 🚀 快速开始

### 安装依赖

```bash
pnpm install
```

### 运行服务器

```bash
# 开发模式
pnpm run dev

# 生产模式
pnpm run build
pnpm start
```

### 执行风险检查

```bash
# 执行每日风险检查
pnpm run check
```

## 📊 执行结果示例

```
╔═══════════════════════════════════════════════════════════╗
║         AURIX 跨境哨兵 - 每日风险检查任务                 ║
╚═══════════════════════════════════════════════════════════╝

🚀 开始执行风险检查任务...
============================================================
📊 发现 5 个活跃订阅
🏢 需要检查 5 家公司

🔍 检查公司: 杭州电子商务科技 (comp-004)
   当前风险评分: 80
   新风险评分: 99
   评分变化: +19
   📧 风险变化达到阈值，准备发送通知...
   ✅ 通知已发送: manager1@example.com

============================================================
✅ 风险检查任务完成
⏱️  耗时: 773ms
📊 检查公司数: 5
📧 发送通知数: 1
✅ 成功通知数: 1
❌ 失败通知数: 0
============================================================
```

## 📁 项目结构

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
├── data/                              # 数据存储
├── logs/                              # 日志文件
├── SYSTEM_DOCUMENTATION.md            # 系统文档
├── EXECUTION_REPORT.md                # 执行报告
└── README.md
```

## 🔌 API 接口

### 运行风险检查

```typescript
POST /trpc/riskChecker.runCheck

// 请求参数
{
  companyIds?: string[];      // 可选：指定要检查的公司ID
  forceNotify?: boolean;      // 可选：强制发送通知
}

// 响应
{
  success: boolean;
  summary: {
    totalCompanies: number;
    totalNotifications: number;
    successfulNotifications: number;
    failedNotifications: number;
    duration: number;
  };
  results: RiskCheckResult[];
  notifications: Notification[];
}
```

### 获取公司风险历史

```typescript
GET /trpc/riskChecker.getCompanyRiskHistory

// 请求参数
{
  companyId: string;
}
```

## 📈 风险评分说明

| 评分范围 | 风险等级 | 说明 |
|---------|---------|------|
| 0-30 | 低风险 | 经营状况良好，风险可控 |
| 31-60 | 中等风险 | 需要关注，建议加强监控 |
| 61-80 | 较高风险 | 需要采取风险管理措施 |
| 81-100 | 高风险 | 需要立即采取行动 |

## 📧 邮件通知

当风险评分变化超过阈值（默认 10 分）时，系统会自动发送邮件通知，包含：

- 风险等级变化警告
- 公司基本信息
- 风险因素分析
- 建议措施
- 检测时间

## 📝 日志记录

系统完整记录所有活动：

- **风险检查日志**：`logs/risk-check.log`
- **邮件通知日志**：`logs/email-notifications.log`
- **邮件内容存档**：`logs/emails/`

## ⚙️ 配置定时任务

使用 cron 配置每日自动执行：

```bash
# 每天早上 9:00 执行
0 9 * * * cd /home/ubuntu/aurixai-website && pnpm run check >> logs/cron.log 2>&1
```

## 🛠️ 技术栈

- **后端框架**：Node.js + Express + TypeScript
- **API 框架**：tRPC (类型安全的 RPC 框架)
- **数据存储**：JSON 文件数据库（可扩展为 MySQL/PostgreSQL）
- **邮件服务**：Nodemailer
- **运行时**：tsx (TypeScript 执行器)

## 📚 文档

- [系统文档](./SYSTEM_DOCUMENTATION.md) - 完整的系统架构和使用指南
- [执行报告](./EXECUTION_REPORT.md) - 最新的执行结果报告

## 🔒 安全建议

1. 敏感信息存储在环境变量中
2. 添加 API 认证和授权机制
3. 敏感数据加密存储
4. 日志中不记录敏感信息
5. 定期备份数据和日志文件

## 🚀 扩展建议

- 升级为关系型数据库（MySQL/PostgreSQL）
- 集成真实的邮件服务（SendGrid/AWS SES）
- 接入真实的风险数据源（企业征信 API）
- 添加用户管理系统
- 升级为实时监控系统
- 添加数据分析与可视化功能

## 📄 License

MIT

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系我们

- **官方网站**：https://aurix.ai
- **技术支持**：support@aurix.ai
- **GitHub**：https://github.com/dtt9696/aurixai-website

---

**版本**：1.0.0  
**最后更新**：2026-01-14

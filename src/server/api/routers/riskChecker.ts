import { z } from 'zod';
import { initTRPC } from '@trpc/server';
import { db } from '../../../lib/database';
import { riskAssessmentService } from '../../services/riskAssessment';
import { emailService } from '../../services/emailService';
import { trackingService } from '../../services/trackingService';
import { RiskCheckResult } from '../../../types';
import * as fs from 'fs';
import * as path from 'path';

const t = initTRPC.create();

const logCheckResults = (
  results: RiskCheckResult[],
  notifications: Array<{ email: string; companyName: string; success: boolean }>,
  duration: number
) => {
  const logDir = path.join(process.cwd(), 'logs');
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const logFile = path.join(logDir, 'risk-check.log');
  const timestamp = new Date().toISOString();

  const logEntry = {
    timestamp,
    duration,
    summary: {
      totalCompanies: results.length,
      totalNotifications: notifications.length,
      successfulNotifications: notifications.filter(n => n.success).length,
      failedNotifications: notifications.filter(n => !n.success).length,
    },
    results: results.map(r => ({
      companyId: r.companyId,
      companyName: r.companyName,
      previousScore: r.previousScore,
      currentScore: r.currentScore,
      scoreChange: r.scoreChange,
      riskFactors: r.riskFactors,
    })),
    notifications: notifications.map(n => ({
      email: n.email,
      companyName: n.companyName,
      status: n.success ? 'success' : 'failed',
    })),
  };

  const logLine = JSON.stringify(logEntry, null, 2) + '\n' + '-'.repeat(80) + '\n';
  fs.appendFileSync(logFile, logLine);
};

export const riskCheckerRouter = t.router({
  /**
   * 运行风险检查
   * 对所有已订阅的公司进行风险评估
   * 已集成埋点：自动上报风险检查、告警发送事件到仪表盘
   */
  runCheck: t.procedure
    .input(
      z.object({
        companyIds: z.array(z.string()).optional(),
        forceNotify: z.boolean().optional().default(false),
      })
    )
    .mutation(async ({ input }) => {
      const startTime = Date.now();
      const results: RiskCheckResult[] = [];
      const notifications: Array<{
        email: string;
        companyName: string;
        success: boolean;
      }> = [];

      console.log('🚀 开始执行风险检查任务...');
      console.log('=' .repeat(60));

      // 📊 追踪 API 调用
      trackingService.trackApiCall(
        "riskChecker.runCheck",
        "mutation",
        0,
        true,
        { companyIds: input.companyIds, forceNotify: input.forceNotify }
      );

      // 获取所有活跃订阅
      const subscriptions = db.getActiveSubscriptions();
      console.log(`📊 发现 ${subscriptions.length} 个活跃订阅`);

      // 获取需要检查的公司列表
      const companyIds = input.companyIds || 
        [...new Set(subscriptions.map(s => s.companyId))];

      console.log(`🏢 需要检查 ${companyIds.length} 家公司\n`);

      // 逐个检查公司风险
      for (const companyId of companyIds) {
        const company = db.getCompany(companyId);
        if (!company) {
          console.log(`⚠️  公司 ${companyId} 不存在，跳过`);
          continue;
        }

        console.log(`\n🔍 检查公司: ${company.name} (${companyId})`);
        console.log(`   当前风险评分: ${company.currentRiskScore}`);

        // 计算新的风险评分
        const newScore = await riskAssessmentService.calculateRiskScore(company);
        const scoreChange = newScore - company.currentRiskScore;

        console.log(`   新风险评分: ${newScore}`);
        console.log(`   评分变化: ${scoreChange > 0 ? '+' : ''}${scoreChange}`);

        // 分析风险因素
        const riskFactors = await riskAssessmentService.analyzeRiskFactors(
          company,
          newScore
        );

        // 更新数据库中的风险评分
        db.updateCompanyRiskScore(companyId, newScore);

        // 创建检查结果
        const result: RiskCheckResult = {
          companyId: company.id,
          companyName: company.name,
          previousScore: company.currentRiskScore,
          currentScore: newScore,
          scoreChange,
          timestamp: new Date(),
          riskFactors,
        };

        results.push(result);

        // 📊 追踪每次风险检查
        trackingService.trackRiskCheck(
          company.id,
          company.name,
          company.currentRiskScore,
          newScore,
          scoreChange
        );

        // 检查是否需要发送通知
        const companySubscriptions = db.getSubscriptionsByCompany(companyId);
        const shouldNotify = input.forceNotify || 
          Math.abs(scoreChange) >= 10;

        if (shouldNotify && companySubscriptions.length > 0) {
          console.log(`   📧 风险变化达到阈值，准备发送通知...`);

          for (const subscription of companySubscriptions) {
            const notificationResult = await emailService.sendRiskChangeNotification(
              subscription.email,
              result
            );

            notifications.push({
              email: subscription.email,
              companyName: company.name,
              success: notificationResult.success,
            });

            // 📊 追踪告警发送
            trackingService.trackAlert(
              subscription.email,
              company.name,
              notificationResult.success,
              scoreChange
            );

            if (notificationResult.success) {
              console.log(`   ✅ 通知已发送: ${subscription.email}`);
            } else {
              console.log(`   ❌ 通知发送失败: ${subscription.email}`);
            }
          }
        } else {
          console.log(`   ℹ️  风险变化未达到阈值，不发送通知`);
        }
      }

      const duration = Date.now() - startTime;

      // 记录检查日志
      logCheckResults(results, notifications, duration);

      // 📊 追踪定时任务完成
      trackingService.trackCronJob(
        "daily_risk_check",
        duration,
        results.length,
        notifications.filter(n => n.success).length
      );

      console.log('\n' + '='.repeat(60));
      console.log('✅ 风险检查任务完成');
      console.log(`⏱️  耗时: ${duration}ms`);
      console.log(`📊 检查公司数: ${results.length}`);
      console.log(`📧 发送通知数: ${notifications.length}`);
      console.log(`✅ 成功通知数: ${notifications.filter(n => n.success).length}`);
      console.log(`❌ 失败通知数: ${notifications.filter(n => !n.success).length}`);
      console.log('='.repeat(60));

      return {
        success: true,
        summary: {
          totalCompanies: results.length,
          totalNotifications: notifications.length,
          successfulNotifications: notifications.filter(n => n.success).length,
          failedNotifications: notifications.filter(n => !n.success).length,
          duration,
        },
        results,
        notifications,
      };
    }),

  /**
   * 获取公司风险历史
   * 已集成埋点：自动上报 API 调用事件
   */
  getCompanyRiskHistory: t.procedure
    .input(z.object({ companyId: z.string() }))
    .query(({ input }) => {
      const queryStart = Date.now();

      // 📊 追踪 API 调用
      trackingService.trackApiCall(
        "riskChecker.getCompanyRiskHistory",
        "query",
        0,
        true,
        { companyId: input.companyId }
      );

      const company = db.getCompany(input.companyId);
      if (!company) {
        trackingService.trackApiCall(
          "riskChecker.getCompanyRiskHistory",
          "query",
          Date.now() - queryStart,
          false,
          { companyId: input.companyId, error: "company_not_found" }
        );
        throw new Error(`公司 ${input.companyId} 不存在`);
      }

      trackingService.trackApiCall(
        "riskChecker.getCompanyRiskHistory",
        "query",
        Date.now() - queryStart,
        true,
        { companyId: input.companyId, companyName: company.name }
      );

      return company;
    }),
});

export type RiskCheckerRouter = typeof riskCheckerRouter;

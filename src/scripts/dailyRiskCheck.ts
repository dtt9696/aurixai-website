#!/usr/bin/env node

/**
 * AURIX 跨境哨兵 - 每日风险检查脚本
 * 
 * 功能：
 * 1. 调用风险检查 API 接口 /trpc/riskChecker.runCheck
 * 2. 检查所有已订阅风险监控的公司
 * 3. 对比历史风险评分，检测风险变化
 * 4. 如果风险评分变化超过10分，发送邮件通知给订阅用户
 * 5. 记录检查结果到日志
 * 
 * 使用方法：
 * - 直接运行: tsx src/scripts/dailyRiskCheck.ts
 * - 通过 npm: npm run check
 * - 定时任务: 配置 cron 定时执行
 */

import { appRouter } from '../server/api/root';

async function main() {
  console.log('\n');
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║         AURIX 跨境哨兵 - 每日风险检查任务                 ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');
  console.log('\n');

  try {
    // 创建 tRPC 调用者
    const caller = appRouter.createCaller({});

    // 执行风险检查
    const result = await caller.riskChecker.runCheck({
      forceNotify: false, // 只在风险变化超过阈值时发送通知
    });

    if (result.success) {
      console.log('\n✅ 任务执行成功！\n');
      
      // 显示详细结果
      console.log('📊 执行摘要:');
      console.log(`   - 检查公司数: ${result.summary.totalCompanies}`);
      console.log(`   - 发送通知数: ${result.summary.totalNotifications}`);
      console.log(`   - 成功通知数: ${result.summary.successfulNotifications}`);
      console.log(`   - 失败通知数: ${result.summary.failedNotifications}`);
      console.log(`   - 执行耗时: ${result.summary.duration}ms`);

      // 显示风险变化详情
      if (result.results.length > 0) {
        console.log('\n📈 风险变化详情:');
        result.results.forEach((r, index) => {
          const arrow = r.scoreChange > 0 ? '📈' : r.scoreChange < 0 ? '📉' : '➡️';
          const changeStr = r.scoreChange > 0 ? `+${r.scoreChange}` : r.scoreChange.toString();
          console.log(`   ${index + 1}. ${r.companyName}`);
          console.log(`      ${arrow} ${r.previousScore} → ${r.currentScore} (${changeStr})`);
          if (r.riskFactors.length > 0) {
            console.log(`      因素: ${r.riskFactors.join(', ')}`);
          }
        });
      }

      // 显示通知发送详情
      if (result.notifications.length > 0) {
        console.log('\n📧 通知发送详情:');
        result.notifications.forEach((n, index) => {
          const status = n.success ? '✅' : '❌';
          console.log(`   ${index + 1}. ${status} ${n.email} - ${n.companyName}`);
        });
      }

      console.log('\n');
      process.exit(0);
    } else {
      console.error('\n❌ 任务执行失败\n');
      process.exit(1);
    }
  } catch (error) {
    console.error('\n❌ 任务执行出错:');
    console.error(error);
    console.log('\n');
    process.exit(1);
  }
}

// 执行主函数
main();

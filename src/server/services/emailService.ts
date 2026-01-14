import { RiskCheckResult } from '../../types';
import * as fs from 'fs';
import * as path from 'path';

/**
 * 邮件服务
 * 在实际应用中会使用 nodemailer 发送真实邮件
 * 这里模拟邮件发送并记录到文件
 */
export class EmailService {
  private emailLogDir: string;

  constructor() {
    this.emailLogDir = path.join(process.cwd(), 'logs', 'emails');
    if (!fs.existsSync(this.emailLogDir)) {
      fs.mkdirSync(this.emailLogDir, { recursive: true });
    }
  }

  /**
   * 发送风险变化通知邮件
   */
  async sendRiskChangeNotification(
    email: string,
    result: RiskCheckResult
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const emailContent = this.generateEmailContent(result);
      
      // 模拟邮件发送（实际应用中使用 nodemailer）
      await this.simulateEmailSend(email, emailContent);

      // 记录邮件发送日志
      this.logEmail(email, result, 'success');

      console.log(`✅ 邮件已发送至: ${email}`);
      return { success: true };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '未知错误';
      console.error(`❌ 邮件发送失败 (${email}):`, errorMsg);
      this.logEmail(email, result, 'failed', errorMsg);
      return { success: false, error: errorMsg };
    }
  }

  /**
   * 生成邮件内容
   */
  private generateEmailContent(result: RiskCheckResult): string {
    const direction = result.scoreChange > 0 ? '上升' : '下降';
    const severity = Math.abs(result.scoreChange) > 15 ? '重大' : 
                     Math.abs(result.scoreChange) > 10 ? '显著' : '轻微';

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>AURIX 风险变化通知</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
  <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
      🔔 AURIX 跨境哨兵 - 风险变化通知
    </h2>
    
    <div style="background-color: ${result.scoreChange > 0 ? '#fff3cd' : '#d1ecf1'}; 
                padding: 15px; border-radius: 5px; margin: 20px 0;">
      <h3 style="margin-top: 0; color: ${result.scoreChange > 0 ? '#856404' : '#0c5460'};">
        ${severity}风险${direction}警告
      </h3>
      <p><strong>公司名称：</strong>${result.companyName}</p>
      <p><strong>风险评分变化：</strong>
        ${result.previousScore} → ${result.currentScore} 
        (${result.scoreChange > 0 ? '+' : ''}${result.scoreChange} 分)
      </p>
      <p><strong>检测时间：</strong>${result.timestamp.toLocaleString('zh-CN')}</p>
    </div>

    <div style="margin: 20px 0;">
      <h4 style="color: #2c3e50;">风险因素分析：</h4>
      <ul>
        ${result.riskFactors.map(factor => `<li>${factor}</li>`).join('')}
      </ul>
    </div>

    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
      <h4 style="margin-top: 0; color: #2c3e50;">建议措施：</h4>
      ${this.generateRecommendations(result.scoreChange)}
    </div>

    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; 
                font-size: 12px; color: #666; text-align: center;">
      <p>此邮件由 AURIX 跨境哨兵自动发送，请勿直接回复。</p>
      <p>如需帮助，请访问 <a href="https://aurix.ai">AURIX 官网</a></p>
    </div>
  </div>
</body>
</html>
    `.trim();
  }

  /**
   * 生成建议措施
   */
  private generateRecommendations(scoreChange: number): string {
    if (scoreChange > 15) {
      return `
        <ul>
          <li>立即审查公司财务状况和合规情况</li>
          <li>加强供应链风险管理</li>
          <li>咨询专业风险管理顾问</li>
          <li>考虑购买贸易信用保险</li>
        </ul>
      `;
    } else if (scoreChange > 10) {
      return `
        <ul>
          <li>密切关注市场动态和政策变化</li>
          <li>检查合规文件和资质有效期</li>
          <li>优化供应链管理流程</li>
          <li>加强内部风险控制</li>
        </ul>
      `;
    } else if (scoreChange > 0) {
      return `
        <ul>
          <li>持续监控风险指标变化</li>
          <li>保持与合作伙伴的良好沟通</li>
          <li>定期更新风险评估报告</li>
        </ul>
      `;
    } else if (scoreChange < -10) {
      return `
        <ul>
          <li>继续保持良好的经营状况</li>
          <li>巩固现有风险管理措施</li>
          <li>考虑拓展业务范围</li>
        </ul>
      `;
    } else {
      return `
        <ul>
          <li>保持当前风险管理策略</li>
          <li>定期进行风险评估</li>
        </ul>
      `;
    }
  }

  /**
   * 模拟邮件发送
   */
  private async simulateEmailSend(email: string, content: string): Promise<void> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 200));

    // 保存邮件内容到文件（模拟发送）
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${timestamp}_${email.replace('@', '_at_')}.html`;
    const filepath = path.join(this.emailLogDir, filename);
    
    fs.writeFileSync(filepath, content);
  }

  /**
   * 记录邮件发送日志
   */
  private logEmail(
    email: string,
    result: RiskCheckResult,
    status: 'success' | 'failed',
    error?: string
  ): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      email,
      companyId: result.companyId,
      companyName: result.companyName,
      scoreChange: result.scoreChange,
      status,
      error
    };

    const logFile = path.join(process.cwd(), 'logs', 'email-notifications.log');
    const logLine = JSON.stringify(logEntry) + '\n';
    
    fs.appendFileSync(logFile, logLine);
  }
}

export const emailService = new EmailService();

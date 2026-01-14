import { Company } from '../../types';

/**
 * 风险评估服务
 * 模拟真实的风险评分计算逻辑
 */
export class RiskAssessmentService {
  /**
   * 计算公司的新风险评分
   * 在实际应用中，这里会调用外部API或复杂的评估模型
   */
  async calculateRiskScore(company: Company): Promise<number> {
    // 模拟API调用延迟
    await this.delay(100);

    // 基于多个因素计算风险评分
    const factors = {
      // 行业风险系数
      industryRisk: this.getIndustryRisk(company.industry),
      // 地区风险系数
      countryRisk: this.getCountryRisk(company.country),
      // 随机市场波动 (-15 到 +15)
      marketVolatility: Math.floor(Math.random() * 31) - 15,
      // 合规风险 (0-10)
      complianceRisk: Math.floor(Math.random() * 11),
    };

    // 计算新的风险评分
    let newScore = company.currentRiskScore;
    newScore += factors.marketVolatility;
    newScore += (factors.industryRisk - 5); // 标准化到 -5 到 +5
    newScore += (factors.complianceRisk - 5); // 标准化到 -5 到 +5

    // 确保评分在 0-100 范围内
    newScore = Math.max(0, Math.min(100, newScore));

    return Math.round(newScore);
  }

  /**
   * 获取行业风险系数 (0-10)
   */
  private getIndustryRisk(industry: string): number {
    const riskMap: { [key: string]: number } = {
      '跨境电商': 7,
      '国际贸易': 6,
      '进出口': 5,
      '电子商务': 8,
      '物流': 4,
    };
    return riskMap[industry] || 5;
  }

  /**
   * 获取国家风险系数 (0-10)
   */
  private getCountryRisk(country: string): number {
    const riskMap: { [key: string]: number } = {
      'CN': 4,
      'US': 3,
      'EU': 3,
      'UK': 3,
    };
    return riskMap[country] || 5;
  }

  /**
   * 分析风险变化因素
   */
  async analyzeRiskFactors(company: Company, newScore: number): Promise<string[]> {
    const factors: string[] = [];
    const scoreDiff = newScore - company.currentRiskScore;

    if (Math.abs(scoreDiff) < 5) {
      factors.push('市场环境稳定');
    } else if (scoreDiff > 0) {
      if (scoreDiff > 15) {
        factors.push('重大风险预警：风险评分大幅上升');
      } else if (scoreDiff > 10) {
        factors.push('风险等级提升：需要关注');
      } else {
        factors.push('风险轻微上升');
      }
      
      // 添加可能的风险因素
      const possibleFactors = [
        '国际贸易政策变化',
        '汇率波动加剧',
        '供应链不稳定',
        '合规要求提高',
        '市场竞争加剧'
      ];
      factors.push(possibleFactors[Math.floor(Math.random() * possibleFactors.length)]);
    } else {
      if (scoreDiff < -15) {
        factors.push('风险显著降低：经营状况改善');
      } else if (scoreDiff < -10) {
        factors.push('风险等级下降：积极信号');
      } else {
        factors.push('风险轻微下降');
      }

      // 添加积极因素
      const positiveFactors = [
        '合规体系完善',
        '供应链优化',
        '市场份额增长',
        '财务状况改善',
        '风险管理加强'
      ];
      factors.push(positiveFactors[Math.floor(Math.random() * positiveFactors.length)]);
    }

    return factors;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export const riskAssessmentService = new RiskAssessmentService();

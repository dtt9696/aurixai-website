export interface Company {
  id: string;
  name: string;
  country: string;
  industry: string;
  currentRiskScore: number;
  previousRiskScore: number;
  lastCheckedAt: Date;
}

export interface Subscription {
  id: string;
  userId: string;
  companyId: string;
  email: string;
  alertThreshold: number; // 风险变化阈值
  isActive: boolean;
}

export interface RiskCheckResult {
  companyId: string;
  companyName: string;
  previousScore: number;
  currentScore: number;
  scoreChange: number;
  timestamp: Date;
  riskFactors: string[];
}

export interface NotificationLog {
  id: string;
  subscriptionId: string;
  companyId: string;
  email: string;
  scoreChange: number;
  sentAt: Date;
  status: 'success' | 'failed';
  error?: string;
}

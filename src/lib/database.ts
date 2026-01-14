import { Company, Subscription } from '../types';
import * as fs from 'fs';
import * as path from 'path';

const DATA_DIR = path.join(process.cwd(), 'data');
const COMPANIES_FILE = path.join(DATA_DIR, 'companies.json');
const SUBSCRIPTIONS_FILE = path.join(DATA_DIR, 'subscriptions.json');

// 确保数据目录存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

export class Database {
  private companies: Company[] = [];
  private subscriptions: Subscription[] = [];

  constructor() {
    this.loadData();
  }

  private loadData() {
    // 加载公司数据
    if (fs.existsSync(COMPANIES_FILE)) {
      const data = fs.readFileSync(COMPANIES_FILE, 'utf-8');
      this.companies = JSON.parse(data);
    } else {
      // 初始化模拟数据
      this.companies = this.generateMockCompanies();
      this.saveCompanies();
    }

    // 加载订阅数据
    if (fs.existsSync(SUBSCRIPTIONS_FILE)) {
      const data = fs.readFileSync(SUBSCRIPTIONS_FILE, 'utf-8');
      this.subscriptions = JSON.parse(data);
    } else {
      // 初始化模拟订阅
      this.subscriptions = this.generateMockSubscriptions();
      this.saveSubscriptions();
    }
  }

  private generateMockCompanies(): Company[] {
    return [
      {
        id: 'comp-001',
        name: '深圳跨境电商有限公司',
        country: 'CN',
        industry: '跨境电商',
        currentRiskScore: 65,
        previousRiskScore: 65,
        lastCheckedAt: new Date()
      },
      {
        id: 'comp-002',
        name: '广州国际贸易集团',
        country: 'CN',
        industry: '国际贸易',
        currentRiskScore: 72,
        previousRiskScore: 72,
        lastCheckedAt: new Date()
      },
      {
        id: 'comp-003',
        name: '上海进出口公司',
        country: 'CN',
        industry: '进出口',
        currentRiskScore: 58,
        previousRiskScore: 58,
        lastCheckedAt: new Date()
      },
      {
        id: 'comp-004',
        name: '杭州电子商务科技',
        country: 'CN',
        industry: '电子商务',
        currentRiskScore: 80,
        previousRiskScore: 80,
        lastCheckedAt: new Date()
      },
      {
        id: 'comp-005',
        name: '北京国际物流',
        country: 'CN',
        industry: '物流',
        currentRiskScore: 45,
        previousRiskScore: 45,
        lastCheckedAt: new Date()
      }
    ];
  }

  private generateMockSubscriptions(): Subscription[] {
    return [
      {
        id: 'sub-001',
        userId: 'user-001',
        companyId: 'comp-001',
        email: 'manager1@example.com',
        alertThreshold: 10,
        isActive: true
      },
      {
        id: 'sub-002',
        userId: 'user-002',
        companyId: 'comp-002',
        email: 'manager2@example.com',
        alertThreshold: 10,
        isActive: true
      },
      {
        id: 'sub-003',
        userId: 'user-003',
        companyId: 'comp-003',
        email: 'manager3@example.com',
        alertThreshold: 10,
        isActive: true
      },
      {
        id: 'sub-004',
        userId: 'user-001',
        companyId: 'comp-004',
        email: 'manager1@example.com',
        alertThreshold: 10,
        isActive: true
      },
      {
        id: 'sub-005',
        userId: 'user-004',
        companyId: 'comp-005',
        email: 'manager4@example.com',
        alertThreshold: 10,
        isActive: true
      }
    ];
  }

  private saveCompanies() {
    fs.writeFileSync(COMPANIES_FILE, JSON.stringify(this.companies, null, 2));
  }

  private saveSubscriptions() {
    fs.writeFileSync(SUBSCRIPTIONS_FILE, JSON.stringify(this.subscriptions, null, 2));
  }

  // 获取所有公司
  getAllCompanies(): Company[] {
    return this.companies;
  }

  // 获取单个公司
  getCompany(id: string): Company | undefined {
    return this.companies.find(c => c.id === id);
  }

  // 更新公司风险评分
  updateCompanyRiskScore(id: string, newScore: number): Company | undefined {
    const company = this.companies.find(c => c.id === id);
    if (company) {
      company.previousRiskScore = company.currentRiskScore;
      company.currentRiskScore = newScore;
      company.lastCheckedAt = new Date();
      this.saveCompanies();
    }
    return company;
  }

  // 获取所有活跃订阅
  getActiveSubscriptions(): Subscription[] {
    return this.subscriptions.filter(s => s.isActive);
  }

  // 根据公司ID获取订阅
  getSubscriptionsByCompany(companyId: string): Subscription[] {
    return this.subscriptions.filter(s => s.companyId === companyId && s.isActive);
  }
}

export const db = new Database();

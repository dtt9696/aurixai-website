#!/usr/bin/env python3
"""
iRobot (IRBT) 风险预测模型
基于财务指标、股价波动率、舆情分数等多维度数据构建综合风险评分模型
"""
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

DATA_DIR = '/home/ubuntu/aurixai-website/data'

# ============================================================
# 1. 财务风险评分模型
# ============================================================
def calculate_financial_risk_score():
    """基于关键财务指标计算财务风险评分 (0-100, 100为最高风险)"""
    
    with open(f'{DATA_DIR}/irbt_financial_summary.json', 'r') as f:
        fin = json.load(f)
    
    scores = {}
    
    # 1.1 收入趋势风险 (权重: 20%)
    revenue_change = fin['q3_2025']['revenue_yoy_change']  # -24.6%
    if revenue_change < -30:
        scores['revenue_trend'] = 95
    elif revenue_change < -20:
        scores['revenue_trend'] = 85
    elif revenue_change < -10:
        scores['revenue_trend'] = 70
    elif revenue_change < 0:
        scores['revenue_trend'] = 50
    else:
        scores['revenue_trend'] = 20
    
    # 1.2 盈利能力风险 (权重: 20%)
    eps = fin['q3_2025']['eps']  # -0.23 (Non-GAAP)
    gaap_loss_per_share = -0.62  # GAAP
    if gaap_loss_per_share < -0.5:
        scores['profitability'] = 90
    elif gaap_loss_per_share < -0.2:
        scores['profitability'] = 75
    elif gaap_loss_per_share < 0:
        scores['profitability'] = 55
    else:
        scores['profitability'] = 20
    
    # 1.3 流动性风险 (权重: 25%)
    # 现金仅2480万美元，无额外资本来源
    cash = 24.8  # 百万美元
    debt = 190   # 百万美元（破产时约1.9亿债务）
    cash_ratio = cash / debt if debt > 0 else 0
    if cash_ratio < 0.15:
        scores['liquidity'] = 98
    elif cash_ratio < 0.3:
        scores['liquidity'] = 85
    elif cash_ratio < 0.5:
        scores['liquidity'] = 65
    else:
        scores['liquidity'] = 30
    
    # 1.4 毛利率风险 (权重: 15%)
    gross_margin = 31.0  # Q3 2025 GAAP
    if gross_margin < 25:
        scores['gross_margin'] = 85
    elif gross_margin < 35:
        scores['gross_margin'] = 60
    elif gross_margin < 45:
        scores['gross_margin'] = 40
    else:
        scores['gross_margin'] = 20
    
    # 1.5 持续经营风险 (权重: 20%)
    # 公司已申请破产
    scores['going_concern'] = 100  # 已破产
    
    # 加权计算
    weights = {
        'revenue_trend': 0.20,
        'profitability': 0.20,
        'liquidity': 0.25,
        'gross_margin': 0.15,
        'going_concern': 0.20
    }
    
    financial_risk = sum(scores[k] * weights[k] for k in weights)
    
    return {
        'total_score': round(financial_risk, 1),
        'sub_scores': scores,
        'weights': weights,
        'risk_level': classify_risk(financial_risk)
    }

# ============================================================
# 2. 市场风险评分模型
# ============================================================
def calculate_market_risk_score():
    """基于股价波动率和市场表现计算市场风险评分"""
    
    try:
        prices_df = pd.read_csv(f'{DATA_DIR}/irbt_stock_prices.csv')
        prices_df['date'] = pd.to_datetime(prices_df['date'])
        prices_df = prices_df.sort_values('date')
        prices_df = prices_df.dropna(subset=['close'])
    except Exception as e:
        print(f"  [WARN] 无法读取股价数据: {e}")
        return {'total_score': 95, 'risk_level': '极高风险'}
    
    scores = {}
    
    # 2.1 价格跌幅 (权重: 30%)
    if len(prices_df) > 1:
        start_price = prices_df.iloc[0]['close']
        end_price = prices_df.iloc[-1]['close']
        price_change_pct = ((end_price - start_price) / start_price) * 100
        
        if price_change_pct < -80:
            scores['price_decline'] = 100
        elif price_change_pct < -50:
            scores['price_decline'] = 90
        elif price_change_pct < -30:
            scores['price_decline'] = 75
        elif price_change_pct < -10:
            scores['price_decline'] = 55
        else:
            scores['price_decline'] = 25
    else:
        scores['price_decline'] = 95
    
    # 2.2 波动率 (权重: 25%)
    if len(prices_df) > 20:
        returns = prices_df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # 年化波动率
        
        if volatility > 150:
            scores['volatility'] = 95
        elif volatility > 100:
            scores['volatility'] = 80
        elif volatility > 60:
            scores['volatility'] = 60
        elif volatility > 30:
            scores['volatility'] = 40
        else:
            scores['volatility'] = 20
    else:
        scores['volatility'] = 80
    
    # 2.3 退市风险 (权重: 25%)
    latest_price = prices_df.iloc[-1]['close'] if len(prices_df) > 0 else 0.05
    if latest_price < 1.0:
        scores['delisting_risk'] = 100  # 已退市
    elif latest_price < 5.0:
        scores['delisting_risk'] = 75
    else:
        scores['delisting_risk'] = 20
    
    # 2.4 成交量萎缩 (权重: 20%)
    if len(prices_df) > 60:
        recent_vol = prices_df.tail(30)['volume'].mean()
        earlier_vol = prices_df.head(30)['volume'].mean()
        if earlier_vol > 0:
            vol_change = (recent_vol - earlier_vol) / earlier_vol
            # 对于破产公司，成交量可能激增也可能萎缩
            scores['volume_trend'] = 70
        else:
            scores['volume_trend'] = 70
    else:
        scores['volume_trend'] = 70
    
    weights = {
        'price_decline': 0.30,
        'volatility': 0.25,
        'delisting_risk': 0.25,
        'volume_trend': 0.20
    }
    
    market_risk = sum(scores[k] * weights[k] for k in weights)
    
    return {
        'total_score': round(market_risk, 1),
        'sub_scores': scores,
        'weights': weights,
        'risk_level': classify_risk(market_risk),
        'metrics': {
            'price_change_pct': round(price_change_pct, 2) if 'price_change_pct' in dir() else None,
            'latest_price': round(latest_price, 4),
        }
    }

# ============================================================
# 3. 舆情风险评分模型
# ============================================================
def calculate_sentiment_risk_score():
    """基于新闻舆情数据计算舆情风险评分"""
    
    with open(f'{DATA_DIR}/irbt_news_sentiment.json', 'r') as f:
        sentiment = json.load(f)
    
    scores = {}
    
    # 3.1 整体情感分数 (权重: 30%)
    overall_score = sentiment['sentiment_score']  # -0.85
    # 映射: -1 -> 100, 0 -> 50, 1 -> 0
    scores['overall_sentiment'] = round(max(0, min(100, 50 - overall_score * 50)), 1)
    
    # 3.2 负面事件密度 (权重: 25%)
    events = sentiment['key_events']
    negative_events = sum(1 for e in events if e['score'] < -0.3)
    total_events = len(events)
    neg_ratio = negative_events / total_events if total_events > 0 else 0
    scores['negative_density'] = round(neg_ratio * 100, 1)
    
    # 3.3 极端风险事件 (权重: 25%)
    extreme_events = sum(1 for e in events if e.get('risk_level') in ['极高', '高'])
    if extreme_events >= 4:
        scores['extreme_events'] = 95
    elif extreme_events >= 2:
        scores['extreme_events'] = 80
    elif extreme_events >= 1:
        scores['extreme_events'] = 60
    else:
        scores['extreme_events'] = 25
    
    # 3.4 媒体关注度 (权重: 20%)
    coverage = sentiment.get('media_coverage_volume', '高')
    if coverage == '高':
        # 高关注度 + 负面情感 = 高风险
        if overall_score < -0.5:
            scores['media_attention'] = 85
        else:
            scores['media_attention'] = 50
    else:
        scores['media_attention'] = 40
    
    weights = {
        'overall_sentiment': 0.30,
        'negative_density': 0.25,
        'extreme_events': 0.25,
        'media_attention': 0.20
    }
    
    sentiment_risk = sum(scores[k] * weights[k] for k in weights)
    
    return {
        'total_score': round(sentiment_risk, 1),
        'sub_scores': scores,
        'weights': weights,
        'risk_level': classify_risk(sentiment_risk)
    }

# ============================================================
# 4. 运营风险评分模型
# ============================================================
def calculate_operational_risk_score():
    """基于运营指标计算运营风险评分"""
    
    scores = {}
    
    # 4.1 管理层变动 (权重: 20%)
    # CEO于2024年5月更换，大规模裁员
    scores['management_change'] = 80
    
    # 4.2 员工流失/裁员 (权重: 25%)
    # 从约1400人裁至约450人
    layoff_pct = (1400 - 450) / 1400 * 100  # ~68%
    if layoff_pct > 50:
        scores['workforce_reduction'] = 95
    elif layoff_pct > 30:
        scores['workforce_reduction'] = 80
    elif layoff_pct > 15:
        scores['workforce_reduction'] = 60
    else:
        scores['workforce_reduction'] = 30
    
    # 4.3 供应链风险 (权重: 20%)
    # 主要制造商Picea现在是收购方
    scores['supply_chain'] = 60  # 中等（收购后可能改善）
    
    # 4.4 竞争压力 (权重: 20%)
    # 面临中国品牌激烈竞争
    scores['competition'] = 90
    
    # 4.5 监管/合规风险 (权重: 15%)
    # 数据隐私、中国收购的地缘政治风险
    scores['regulatory'] = 65
    
    weights = {
        'management_change': 0.20,
        'workforce_reduction': 0.25,
        'supply_chain': 0.20,
        'competition': 0.20,
        'regulatory': 0.15
    }
    
    operational_risk = sum(scores[k] * weights[k] for k in weights)
    
    return {
        'total_score': round(operational_risk, 1),
        'sub_scores': scores,
        'weights': weights,
        'risk_level': classify_risk(operational_risk)
    }

# ============================================================
# 5. 综合风险评分
# ============================================================
def classify_risk(score):
    """根据分数分类风险等级"""
    if score >= 85:
        return '极高风险'
    elif score >= 70:
        return '高风险'
    elif score >= 50:
        return '中等风险'
    elif score >= 30:
        return '低风险'
    else:
        return '极低风险'

def calculate_comprehensive_risk():
    """计算综合风险评分"""
    
    print("=" * 60)
    print("iRobot (IRBT) 综合风险评估模型")
    print(f"评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 计算各维度风险
    print("\n[1] 计算财务风险...")
    financial = calculate_financial_risk_score()
    print(f"    财务风险评分: {financial['total_score']}/100 ({financial['risk_level']})")
    
    print("\n[2] 计算市场风险...")
    market = calculate_market_risk_score()
    print(f"    市场风险评分: {market['total_score']}/100 ({market['risk_level']})")
    
    print("\n[3] 计算舆情风险...")
    sentiment = calculate_sentiment_risk_score()
    print(f"    舆情风险评分: {sentiment['total_score']}/100 ({sentiment['risk_level']})")
    
    print("\n[4] 计算运营风险...")
    operational = calculate_operational_risk_score()
    print(f"    运营风险评分: {operational['total_score']}/100 ({operational['risk_level']})")
    
    # 综合评分（加权平均）
    dimension_weights = {
        'financial': 0.30,
        'market': 0.25,
        'sentiment': 0.25,
        'operational': 0.20
    }
    
    comprehensive_score = (
        financial['total_score'] * dimension_weights['financial'] +
        market['total_score'] * dimension_weights['market'] +
        sentiment['total_score'] * dimension_weights['sentiment'] +
        operational['total_score'] * dimension_weights['operational']
    )
    
    comprehensive_result = {
        'company': 'iRobot Corporation',
        'ticker': 'IRBT',
        'assessment_date': datetime.now().strftime('%Y-%m-%d'),
        'comprehensive_score': round(comprehensive_score, 1),
        'risk_level': classify_risk(comprehensive_score),
        'dimensions': {
            'financial': {
                'score': financial['total_score'],
                'weight': dimension_weights['financial'],
                'level': financial['risk_level'],
                'sub_scores': financial['sub_scores']
            },
            'market': {
                'score': market['total_score'],
                'weight': dimension_weights['market'],
                'level': market['risk_level'],
                'sub_scores': market['sub_scores']
            },
            'sentiment': {
                'score': sentiment['total_score'],
                'weight': dimension_weights['sentiment'],
                'level': sentiment['risk_level'],
                'sub_scores': sentiment['sub_scores']
            },
            'operational': {
                'score': operational['total_score'],
                'weight': dimension_weights['operational'],
                'level': operational['risk_level'],
                'sub_scores': operational['sub_scores']
            }
        },
        'key_findings': [
            '公司已于2025年12月申请Chapter 11破产保护',
            '2026年1月被深圳Picea Robotics收购，完成重组',
            '股价从历史高点约150美元跌至不足0.05美元，投资者面临全额损失',
            '收入连续多季度大幅下滑，2025Q3同比下降24.6%',
            '现金储备严重不足（仅2480万美元），无额外资本来源',
            '大规模裁员（从1400人降至450人），核心人才流失严重',
            '面临中国品牌在扫地机器人市场的激烈竞争',
            '亚马逊14亿美元收购交易因欧盟反垄断审查于2024年1月失败'
        ],
        'risk_outlook': '极度悲观',
        'recommendation': '极高风险警告：iRobot已完成破产重组，原有股东权益归零。作为风险诊断案例，该公司展示了从行业先驱到破产被收购的完整风险演化路径。'
    }
    
    # 保存结果
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'w', encoding='utf-8') as f:
        json.dump(comprehensive_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"综合风险评分: {comprehensive_score:.1f}/100")
    print(f"风险等级: {classify_risk(comprehensive_score)}")
    print(f"{'=' * 60}")
    print(f"\n风险评估结果已保存至 {DATA_DIR}/irbt_risk_assessment.json")
    
    return comprehensive_result

if __name__ == "__main__":
    result = calculate_comprehensive_risk()

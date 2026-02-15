#!/usr/bin/env python3
"""
iRobot 供应链风险模型 + 竞争对手对比分析
"""
import os, json, numpy as np
from datetime import datetime

DATA_DIR = '/home/ubuntu/aurixai-website/data'

def calculate_supply_chain_risk():
    """计算供应链综合风险评分"""
    with open(f'{DATA_DIR}/irbt_supply_chain_data.json', 'r') as f:
        sc = json.load(f)
    
    risks = sc['supply_chain_analysis']['key_risks']
    sub_scores = {k: v['score'] for k, v in risks.items()}
    
    weights = {
        'single_source_dependency': 0.25,
        'geopolitical_risk': 0.20,
        'tariff_exposure': 0.15,
        'inventory_management': 0.15,
        'logistics_disruption': 0.15,
        'quality_control': 0.10
    }
    
    total = sum(sub_scores[k] * weights[k] for k in weights)
    
    def classify(s):
        if s >= 85: return '极高风险'
        elif s >= 70: return '高风险'
        elif s >= 50: return '中等风险'
        elif s >= 30: return '低风险'
        else: return '极低风险'
    
    result = {
        'total_score': round(total, 1),
        'risk_level': classify(total),
        'sub_scores': sub_scores,
        'weights': weights,
        'key_findings': [
            '超过70%的生产外包给单一制造商Picea，供应链集中度极高',
            '核心制造基地位于中国，面临关税和地缘政治双重风险',
            '2024年因制造转型产生2660万美元库存减记',
            '2025Q3因生产延迟和运输中断导致收入严重不及预期',
            '库存周转天数（95天）远高于行业平均（60天），资金占用严重',
            '破产后Picea成为母公司，供应链关系发生根本性转变'
        ]
    }
    
    print(f"供应链风险评分: {result['total_score']}/100 ({result['risk_level']})")
    return result

def competitor_benchmark():
    """竞争对手基准对比分析"""
    with open(f'{DATA_DIR}/irbt_supply_chain_data.json', 'r') as f:
        data = json.load(f)
    
    competitors = data['competitor_comparison']['competitors']
    industry_avg = data['competitor_comparison']['industry_average']
    
    benchmark = {
        'comparison_metrics': [],
        'irobot_vs_industry': {},
        'competitive_position': '极度劣势'
    }
    
    for comp in competitors:
        benchmark['comparison_metrics'].append({
            'name': comp['name'],
            'revenue_usd_m': comp['revenue_2024_usd'],
            'revenue_growth': comp['revenue_growth_2024'],
            'gross_margin': comp['gross_margin_2024'],
            'net_margin': comp['net_margin_2024'],
            'market_share': comp['market_share_2025q1'],
            'inventory_days': comp['inventory_turnover_days'],
            'supply_chain_model': comp['supply_chain_model']
        })
    
    irobot = next(c for c in competitors if c['name'] == 'iRobot')
    benchmark['irobot_vs_industry'] = {
        'gross_margin_gap': round(irobot['gross_margin_2024'] - industry_avg['gross_margin'], 1),
        'net_margin_gap': round(irobot['net_margin_2024'] - industry_avg['net_margin'], 1),
        'growth_gap': round(irobot['revenue_growth_2024'] - industry_avg['revenue_growth'], 1),
        'inventory_days_gap': round(irobot['inventory_turnover_days'] - industry_avg['inventory_turnover_days'], 1),
        'summary': 'iRobot在所有关键指标上均大幅落后于行业平均水平和主要竞争对手'
    }
    
    print(f"竞争对比分析完成: iRobot竞争地位 — {benchmark['competitive_position']}")
    return benchmark

def update_risk_assessment():
    """更新综合风险评估，加入供应链维度"""
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'r') as f:
        risk = json.load(f)
    
    sc_risk = calculate_supply_chain_risk()
    benchmark = competitor_benchmark()
    
    # 更新综合评分（加入供应链维度）
    risk['dimensions']['supply_chain'] = {
        'score': sc_risk['total_score'],
        'weight': 0.15,
        'level': sc_risk['risk_level'],
        'sub_scores': sc_risk['sub_scores']
    }
    
    # 重新计算综合评分（5维度）
    new_weights = {
        'financial': 0.25,
        'market': 0.20,
        'sentiment': 0.20,
        'operational': 0.15,
        'supply_chain': 0.20
    }
    
    for dim_key, w in new_weights.items():
        risk['dimensions'][dim_key]['weight'] = w
    
    new_score = sum(
        risk['dimensions'][k]['score'] * new_weights[k] 
        for k in new_weights
    )
    
    risk['comprehensive_score'] = round(new_score, 1)
    
    def classify(s):
        if s >= 85: return '极高风险'
        elif s >= 70: return '高风险'
        elif s >= 50: return '中等风险'
        elif s >= 30: return '低风险'
        else: return '极低风险'
    
    risk['risk_level'] = classify(new_score)
    risk['competitor_benchmark'] = benchmark
    risk['assessment_date'] = datetime.now().strftime('%Y-%m-%d')
    
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'w', encoding='utf-8') as f:
        json.dump(risk, f, ensure_ascii=False, indent=2)
    
    print(f"\n更新后综合风险评分: {risk['comprehensive_score']}/100 ({risk['risk_level']})")
    print("各维度评分:")
    for k, v in new_weights.items():
        dim = risk['dimensions'][k]
        print(f"  {k}: {dim['score']} (权重{v:.0%}, {dim['level']})")
    
    return risk

if __name__ == "__main__":
    print("=" * 60)
    print("iRobot 供应链风险模型 + 竞争对手对比分析")
    print("=" * 60)
    result = update_risk_assessment()

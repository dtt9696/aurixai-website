#!/usr/bin/env python3
"""
新增可视化图表：供应链风险、竞争对手对比、五维雷达图
"""
import os, json, numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = '/home/ubuntu/aurixai-website/data'
CHART_DIR = '/home/ubuntu/aurixai-website/data/charts'
os.makedirs(CHART_DIR, exist_ok=True)

COLORS = {
    'irobot': '#dc3545', 'roborock': '#1a73e8', 'ecovacs': '#28a745',
    'dreame': '#ff8c00', 'industry': '#6c757d',
    'extreme_risk': '#8B0000', 'high_risk': '#dc3545',
    'medium_risk': '#ffc107', 'low_risk': '#28a745',
}

def chart_supply_chain_risk():
    """供应链风险评分水平条形图"""
    print("  → 生成供应链风险评分图...")
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'r') as f:
        risk = json.load(f)
    
    sc = risk['dimensions']['supply_chain']['sub_scores']
    name_map = {
        'single_source_dependency': '单一供应商依赖',
        'geopolitical_risk': '地缘政治风险',
        'tariff_exposure': '关税敞口风险',
        'inventory_management': '库存管理风险',
        'logistics_disruption': '物流中断风险',
        'quality_control': '质量控制风险',
    }
    
    labels = [name_map.get(k, k) for k in sc.keys()]
    values = list(sc.values())
    
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#8B0000' if v >= 85 else '#dc3545' if v >= 70 else '#ffc107' if v >= 50 else '#28a745' for v in values]
    bars = ax.barh(labels, values, color=colors, alpha=0.85, height=0.55, edgecolor='white', linewidth=1.5)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2.,
                f'{val}', ha='left', va='center', fontsize=12, fontweight='bold')
    
    ax.axvline(x=70, color='red', linestyle='--', alpha=0.4, label='高风险线')
    ax.axvline(x=85, color='darkred', linestyle='--', alpha=0.4, label='极高风险线')
    ax.set_xlim(0, 110)
    ax.set_xlabel('风险评分 (0-100)', fontsize=11)
    ax.set_title(f'iRobot 供应链风险评分: {risk["dimensions"]["supply_chain"]["score"]}/100',
                 fontsize=14, fontweight='bold', pad=15)
    ax.legend(fontsize=9)
    ax.grid(True, axis='x', alpha=0.2)
    ax.invert_yaxis()
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/08_supply_chain_risk.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK]")

def chart_competitor_revenue():
    """竞争对手收入与增长率对比"""
    print("  → 生成竞争对手收入对比图...")
    
    companies = ['石头科技', '科沃斯', '追觅科技', 'iRobot']
    revenue = [1637, 2267, 1096, 682]
    growth = [38.03, 6.71, 55.0, -19.8]
    bar_colors = [COLORS['roborock'], COLORS['ecovacs'], COLORS['dreame'], COLORS['irobot']]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    x = np.arange(len(companies))
    bars = ax1.bar(x, revenue, color=bar_colors, alpha=0.8, width=0.5, edgecolor='white', linewidth=1.5)
    
    for bar, val in zip(bars, revenue):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 20,
                f'${val}M', ha='center', fontsize=11, fontweight='bold')
    
    ax2 = ax1.twinx()
    ax2.plot(x, growth, color='#333', linewidth=2.5, marker='D', markersize=8, zorder=5)
    for i, g in enumerate(growth):
        color = '#dc3545' if g < 0 else '#28a745'
        ax2.annotate(f'{g:+.1f}%', xy=(i, g), xytext=(i + 0.15, g + 3),
                    fontsize=10, fontweight='bold', color=color)
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax2.set_ylabel('收入同比增长率 (%)', fontsize=11)
    
    ax1.set_xlabel('公司', fontsize=11)
    ax1.set_ylabel('2024年收入（百万美元）', fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(companies, fontsize=12)
    ax1.set_title('扫地机器人行业主要竞争对手收入与增长率对比（2024年）', fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, axis='y', alpha=0.2)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/09_competitor_revenue.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK]")

def chart_competitor_margins():
    """竞争对手毛利率与净利率对比"""
    print("  → 生成竞争对手利润率对比图...")
    
    companies = ['石头科技', '科沃斯', '追觅科技', 'iRobot', '行业平均']
    gross_margin = [51.5, 48.2, 45.0, 20.9, 41.4]
    net_margin = [18.2, 5.8, 8.0, -22.0, 2.5]
    bar_colors = [COLORS['roborock'], COLORS['ecovacs'], COLORS['dreame'], COLORS['irobot'], COLORS['industry']]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(companies))
    
    # 毛利率
    bars1 = ax1.bar(x, gross_margin, color=bar_colors, alpha=0.8, width=0.55)
    for bar, val in zip(bars1, gross_margin):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.8,
                f'{val}%', ha='center', fontsize=10, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(companies, fontsize=10, rotation=15)
    ax1.set_ylabel('毛利率 (%)', fontsize=11)
    ax1.set_title('毛利率对比', fontsize=13, fontweight='bold')
    ax1.axhline(y=41.4, color='gray', linestyle='--', alpha=0.5, label='行业平均')
    ax1.legend(fontsize=9)
    ax1.grid(True, axis='y', alpha=0.2)
    
    # 净利率
    bars2 = ax2.bar(x, net_margin, color=bar_colors, alpha=0.8, width=0.55)
    for bar, val in zip(bars2, net_margin):
        offset = 1.5 if val >= 0 else -3
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + offset,
                f'{val}%', ha='center', fontsize=10, fontweight='bold',
                color='#dc3545' if val < 0 else '#333')
    ax2.set_xticks(x)
    ax2.set_xticklabels(companies, fontsize=10, rotation=15)
    ax2.set_ylabel('净利率 (%)', fontsize=11)
    ax2.set_title('净利率对比', fontsize=13, fontweight='bold')
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax2.axhline(y=2.5, color='gray', linestyle='--', alpha=0.5, label='行业平均')
    ax2.legend(fontsize=9)
    ax2.grid(True, axis='y', alpha=0.2)
    
    fig.suptitle('扫地机器人行业利润率对比分析（2024年）', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/10_competitor_margins.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK]")

def chart_market_share():
    """全球市场份额饼图"""
    print("  → 生成市场份额图...")
    
    labels = ['石头科技\n19.3%', '科沃斯\n13.6%', '追觅科技\n11.3%', 'iRobot\n8.5%', '其他\n47.3%']
    sizes = [19.3, 13.6, 11.3, 8.5, 47.3]
    colors = [COLORS['roborock'], COLORS['ecovacs'], COLORS['dreame'], COLORS['irobot'], '#d3d3d3']
    explode = (0, 0, 0, 0.08, 0)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, explode=explode,
                                       autopct='', startangle=140, pctdistance=0.85,
                                       textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    centre_circle = plt.Circle((0, 0), 0.55, fc='white')
    ax.add_artist(centre_circle)
    ax.text(0, 0.05, '全球扫地机器人\n市场份额', ha='center', va='center', fontsize=13, fontweight='bold')
    ax.text(0, -0.15, '2025年Q1', ha='center', va='center', fontsize=10, color='gray')
    
    ax.set_title('全球智能扫地机器人市场份额分布', fontsize=14, fontweight='bold', pad=20)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/11_market_share.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK]")

def chart_inventory_comparison():
    """库存周转天数对比"""
    print("  → 生成库存周转对比图...")
    
    companies = ['追觅科技', '石头科技', '科沃斯', '行业平均', 'iRobot']
    days = [40, 45, 58, 60, 95]
    bar_colors = [COLORS['dreame'], COLORS['roborock'], COLORS['ecovacs'], COLORS['industry'], COLORS['irobot']]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(companies, days, color=bar_colors, alpha=0.85, height=0.5, edgecolor='white', linewidth=1.5)
    
    for bar, val in zip(bars, days):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2.,
                f'{val}天', ha='left', va='center', fontsize=12, fontweight='bold')
    
    ax.axvline(x=60, color='gray', linestyle='--', alpha=0.5, label='行业平均 (60天)')
    ax.set_xlabel('库存周转天数', fontsize=11)
    ax.set_title('扫地机器人行业库存周转天数对比（2024年）', fontsize=13, fontweight='bold', pad=15)
    ax.legend(fontsize=9)
    ax.grid(True, axis='x', alpha=0.2)
    ax.set_xlim(0, 115)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/12_inventory_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK]")

def chart_five_dimension_radar():
    """五维度风险雷达图（更新版）"""
    print("  → 生成五维度风险雷达图...")
    
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'r') as f:
        risk = json.load(f)
    
    categories = ['财务风险', '市场风险', '舆情风险', '运营风险', '供应链风险']
    scores = [
        risk['dimensions']['financial']['score'],
        risk['dimensions']['market']['score'],
        risk['dimensions']['sentiment']['score'],
        risk['dimensions']['operational']['score'],
        risk['dimensions']['supply_chain']['score']
    ]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    scores_plot = scores + [scores[0]]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    ax.fill(angles, scores_plot, color='#dc3545', alpha=0.2)
    ax.plot(angles, scores_plot, color='#dc3545', linewidth=2.5, marker='o', markersize=10)
    
    for angle, score in zip(angles[:-1], scores):
        ax.annotate(f'{score}', xy=(angle, score), xytext=(angle, score + 8),
                    fontsize=13, fontweight='bold', ha='center', color='#8B0000')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
    
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 70, 100, alpha=0.06, color='red')
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 50, 70, alpha=0.04, color='orange')
    
    ax.set_title(f'iRobot 五维度综合风险评分: {risk["comprehensive_score"]}/100\n风险等级: {risk["risk_level"]}',
                 fontsize=15, fontweight='bold', pad=25, color='#8B0000')
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/02_risk_radar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK]")

def chart_supply_chain_flow():
    """供应链结构图（简化版）"""
    print("  → 生成供应链结构图...")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # 节点
    nodes = [
        (1.5, 3, '原材料供应商\n（芯片、电池、马达）', '#6c757d', 0.9),
        (5, 4.5, 'Picea Robotics\n（深圳/越南）\n主要制造商', '#dc3545', 1.1),
        (5, 1.5, 'BYD 等\n其他供应商', '#ffc107', 0.8),
        (8.5, 3, 'iRobot\n（美国贝德福德）\n品牌/设计/销售', '#1a73e8', 1.0),
        (12, 4.5, '北美市场', '#28a745', 0.7),
        (12, 3, 'EMEA市场', '#28a745', 0.7),
        (12, 1.5, '日本市场', '#28a745', 0.7),
    ]
    
    for x, y, text, color, size in nodes:
        bbox = dict(boxstyle=f'round,pad=0.5', facecolor=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold', bbox=bbox)
    
    # 箭头
    arrows = [
        (2.5, 3.3, 3.8, 4.2, '零部件供应'),
        (2.5, 2.7, 3.8, 1.8, '零部件供应'),
        (6.2, 4.2, 7.3, 3.5, '成品交付\n$1亿债务'),
        (6.2, 1.8, 7.3, 2.5, '部件交付\n$270万债务'),
        (9.7, 3.4, 11, 4.3, '美国 (-33%)'),
        (9.7, 3, 11, 3, 'EMEA (-13%)'),
        (9.7, 2.6, 11, 1.7, '日本 (-9%)'),
    ]
    
    for x1, y1, x2, y2, label in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.5))
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.2, label, ha='center', va='bottom', fontsize=7, color='#555')
    
    # 风险标注
    ax.text(5, 5.5, '⚠ 单一供应商集中度 >70%', ha='center', fontsize=10, color='#dc3545', fontweight='bold')
    ax.text(5, 0.5, '⚠ 关税风险: 欠美国海关$340万', ha='center', fontsize=9, color='#dc3545')
    
    ax.set_title('iRobot 供应链结构与风险分布', fontsize=14, fontweight='bold', pad=15)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/13_supply_chain_flow.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK]")

def main():
    print("=" * 60)
    print("生成新增可视化图表...")
    print("=" * 60)
    chart_five_dimension_radar()
    chart_supply_chain_risk()
    chart_supply_chain_flow()
    chart_competitor_revenue()
    chart_competitor_margins()
    chart_market_share()
    chart_inventory_comparison()
    print(f"\n所有新增图表已生成完毕！")

if __name__ == "__main__":
    main()

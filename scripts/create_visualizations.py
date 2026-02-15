#!/usr/bin/env python3
"""
iRobot (IRBT) 风险诊断可视化图表
生成：股价走势图、风险评分雷达图、风险热力图、收入趋势图、舆情时间线
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = '/home/ubuntu/aurixai-website/data'
CHART_DIR = '/home/ubuntu/aurixai-website/data/charts'
os.makedirs(CHART_DIR, exist_ok=True)

# 颜色方案
COLORS = {
    'primary': '#1a73e8',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#28a745',
    'dark': '#343a40',
    'light_bg': '#f8f9fa',
    'extreme_risk': '#8B0000',
    'high_risk': '#dc3545',
    'medium_risk': '#ffc107',
    'low_risk': '#28a745',
}

def chart1_stock_price_history():
    """图表1: iRobot股价走势图（5年周线）"""
    print("  → 生成股价走势图...")
    
    df = pd.read_csv(f'{DATA_DIR}/irbt_stock_prices_5y.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df = df.dropna(subset=['close'])
    
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    # 股价线
    ax1.plot(df['date'], df['close'], color=COLORS['primary'], linewidth=1.5, label='收盘价')
    ax1.fill_between(df['date'], df['close'], alpha=0.1, color=COLORS['primary'])
    
    # 标注关键事件
    events = [
        ('2022-08-05', '亚马逊宣布\n收购iRobot', 60),
        ('2024-01-29', '亚马逊放弃\n收购', 15),
        ('2025-12-14', '申请Chapter 11\n破产保护', 1),
    ]
    
    for date_str, label, y_pos in events:
        date = pd.to_datetime(date_str)
        if date >= df['date'].min() and date <= df['date'].max():
            ax1.annotate(label,
                xy=(date, y_pos),
                xytext=(date, y_pos + 15),
                fontsize=8,
                ha='center',
                arrowprops=dict(arrowstyle='->', color=COLORS['danger'], lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor=COLORS['danger'], alpha=0.9))
    
    # 成交量（副轴）
    ax2 = ax1.twinx()
    if 'volume' in df.columns:
        ax2.bar(df['date'], df['volume'] / 1e6, alpha=0.15, color='gray', width=5, label='成交量')
        ax2.set_ylabel('成交量（百万股）', fontsize=10, color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')
    
    ax1.set_xlabel('日期', fontsize=11)
    ax1.set_ylabel('股价（美元）', fontsize=11, color=COLORS['primary'])
    ax1.set_title('iRobot (IRBT) 股价走势图（2021-2026）', fontsize=14, fontweight='bold', pad=15)
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(bottom=0)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/01_stock_price_history.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK] 股价走势图已保存")

def chart2_risk_radar():
    """图表2: 综合风险评分雷达图"""
    print("  → 生成风险雷达图...")
    
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'r') as f:
        risk = json.load(f)
    
    categories = ['财务风险', '市场风险', '舆情风险', '运营风险']
    scores = [
        risk['dimensions']['financial']['score'],
        risk['dimensions']['market']['score'],
        risk['dimensions']['sentiment']['score'],
        risk['dimensions']['operational']['score']
    ]
    
    # 雷达图
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    scores_plot = scores + [scores[0]]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # 填充区域
    ax.fill(angles, scores_plot, color=COLORS['danger'], alpha=0.25)
    ax.plot(angles, scores_plot, color=COLORS['danger'], linewidth=2, marker='o', markersize=8)
    
    # 添加分数标签
    for angle, score, cat in zip(angles[:-1], scores, categories):
        ax.annotate(f'{score}',
            xy=(angle, score),
            xytext=(angle, score + 8),
            fontsize=12, fontweight='bold', ha='center',
            color=COLORS['extreme_risk'])
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=13, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
    
    # 风险区域颜色
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 0, 30, alpha=0.05, color='green')
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 30, 50, alpha=0.05, color='yellow')
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 50, 70, alpha=0.05, color='orange')
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 70, 100, alpha=0.08, color='red')
    
    ax.set_title(f'iRobot 综合风险评分: {risk["comprehensive_score"]}/100\n风险等级: {risk["risk_level"]}',
                 fontsize=15, fontweight='bold', pad=25, color=COLORS['extreme_risk'])
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/02_risk_radar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK] 风险雷达图已保存")

def chart3_risk_heatmap():
    """图表3: 风险维度热力图"""
    print("  → 生成风险热力图...")
    
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'r') as f:
        risk = json.load(f)
    
    # 构建子维度矩阵
    dimensions = {
        '财务风险': risk['dimensions']['financial']['sub_scores'],
        '市场风险': risk['dimensions']['market']['sub_scores'],
        '舆情风险': risk['dimensions']['sentiment']['sub_scores'],
        '运营风险': risk['dimensions']['operational']['sub_scores'],
    }
    
    # 翻译子维度名称
    name_map = {
        'revenue_trend': '收入趋势',
        'profitability': '盈利能力',
        'liquidity': '流动性',
        'gross_margin': '毛利率',
        'going_concern': '持续经营',
        'price_decline': '价格跌幅',
        'volatility': '波动率',
        'delisting_risk': '退市风险',
        'volume_trend': '成交量趋势',
        'overall_sentiment': '整体情感',
        'negative_density': '负面密度',
        'extreme_events': '极端事件',
        'media_attention': '媒体关注',
        'management_change': '管理层变动',
        'workforce_reduction': '裁员规模',
        'supply_chain': '供应链',
        'competition': '竞争压力',
        'regulatory': '监管合规',
    }
    
    # 收集所有子维度
    all_subs = set()
    for dim_scores in dimensions.values():
        all_subs.update(dim_scores.keys())
    all_subs = sorted(all_subs)
    
    # 构建矩阵
    matrix_data = []
    row_labels = []
    for dim_name, dim_scores in dimensions.items():
        row = []
        for sub in sorted(dim_scores.keys()):
            row.append(dim_scores[sub])
        matrix_data.append(row)
        row_labels.append(dim_name)
    
    # 为每个维度创建独立热力图
    fig, axes = plt.subplots(4, 1, figsize=(10, 12))
    
    for idx, (dim_name, dim_scores) in enumerate(dimensions.items()):
        ax = axes[idx]
        sub_names = [name_map.get(k, k) for k in dim_scores.keys()]
        sub_values = list(dim_scores.values())
        
        data = np.array([sub_values])
        
        sns.heatmap(data, annot=True, fmt='.0f', cmap='RdYlGn_r',
                    xticklabels=sub_names, yticklabels=[dim_name],
                    linewidths=2, linecolor='white', ax=ax,
                    vmin=0, vmax=100, cbar_kws={'label': '风险分数'},
                    annot_kws={'fontsize': 12, 'fontweight': 'bold'})
        ax.set_title(f'{dim_name}', fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=0)
    
    fig.suptitle('iRobot 多维度风险评分热力图', fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/03_risk_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK] 风险热力图已保存")

def chart4_revenue_trend():
    """图表4: 收入趋势与同比变化"""
    print("  → 生成收入趋势图...")
    
    # iRobot季度收入数据
    quarters = ['2023Q1', '2023Q2', '2023Q3', '2023Q4', '2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3']
    revenue = [189.2, 186.2, 186.2, 120.3, 166.4, 166.4, 193.4, 120.8, 150.5, 145.0, 145.8]
    yoy_change = [None, None, None, None, -12.0, -10.6, 3.9, 0.4, -9.6, -12.9, -24.6]
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(quarters))
    bars = ax1.bar(x, revenue, color=[COLORS['danger'] if (y is not None and y < 0) else COLORS['primary'] for y in yoy_change],
                   alpha=0.7, width=0.6)
    
    # 添加数值标签
    for bar, val in zip(bars, revenue):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                f'${val:.0f}M', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # 同比变化线
    ax2 = ax1.twinx()
    valid_x = [i for i, y in enumerate(yoy_change) if y is not None]
    valid_y = [y for y in yoy_change if y is not None]
    ax2.plot(valid_x, valid_y, color=COLORS['extreme_risk'], linewidth=2, marker='D', markersize=6, label='同比变化')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax2.set_ylabel('同比变化（%）', fontsize=11, color=COLORS['extreme_risk'])
    ax2.tick_params(axis='y', labelcolor=COLORS['extreme_risk'])
    
    ax1.set_xlabel('季度', fontsize=11)
    ax1.set_ylabel('收入（百万美元）', fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(quarters, rotation=45, ha='right')
    ax1.set_title('iRobot 季度收入趋势与同比变化', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(True, axis='y', alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/04_revenue_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK] 收入趋势图已保存")

def chart5_risk_pie():
    """图表5: 风险等级分布饼图"""
    print("  → 生成风险等级分布图...")
    
    with open(f'{DATA_DIR}/irbt_risk_assessment.json', 'r') as f:
        risk = json.load(f)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 左图：四维度风险分数对比
    dims = ['财务风险', '市场风险', '舆情风险', '运营风险']
    dim_scores = [
        risk['dimensions']['financial']['score'],
        risk['dimensions']['market']['score'],
        risk['dimensions']['sentiment']['score'],
        risk['dimensions']['operational']['score']
    ]
    dim_weights = [0.30, 0.25, 0.25, 0.20]
    
    colors = [COLORS['extreme_risk'], COLORS['danger'], '#e74c3c', COLORS['warning']]
    bars = ax1.barh(dims, dim_scores, color=colors, alpha=0.8, height=0.5)
    
    for bar, score in zip(bars, dim_scores):
        ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2.,
                f'{score}', ha='left', va='center', fontsize=12, fontweight='bold')
    
    ax1.set_xlim(0, 110)
    ax1.axvline(x=70, color='red', linestyle='--', alpha=0.5, label='高风险线')
    ax1.axvline(x=85, color='darkred', linestyle='--', alpha=0.5, label='极高风险线')
    ax1.set_xlabel('风险评分', fontsize=11)
    ax1.set_title('各维度风险评分', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, axis='x', alpha=0.3)
    
    # 右图：权重分布饼图
    weight_labels = [f'{d}\n(权重{w:.0%})' for d, w in zip(dims, dim_weights)]
    wedges, texts, autotexts = ax2.pie(dim_weights, labels=weight_labels, colors=colors,
                                        autopct='%1.0f%%', startangle=90, pctdistance=0.75,
                                        textprops={'fontsize': 10})
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
        autotext.set_color('white')
    
    ax2.set_title('风险维度权重分布', fontsize=13, fontweight='bold')
    
    fig.suptitle(f'iRobot 综合风险评分: {risk["comprehensive_score"]}/100 — {risk["risk_level"]}',
                 fontsize=15, fontweight='bold', color=COLORS['extreme_risk'], y=1.02)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/05_risk_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK] 风险等级分布图已保存")

def chart6_sentiment_timeline():
    """图表6: 舆情事件时间线"""
    print("  → 生成舆情时间线...")
    
    with open(f'{DATA_DIR}/irbt_news_sentiment.json', 'r') as f:
        sentiment = json.load(f)
    
    events = sentiment['key_events']
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    dates = [pd.to_datetime(e['date']) for e in events]
    scores = [e['score'] for e in events]
    titles = [e['title'][:20] + '...' if len(e['title']) > 20 else e['title'] for e in events]
    risk_levels = [e.get('risk_level', '中') for e in events]
    
    # 颜色映射
    color_map = {'极高': COLORS['extreme_risk'], '高': COLORS['danger'], 
                 '中': COLORS['warning'], '低': COLORS['success']}
    point_colors = [color_map.get(rl, 'gray') for rl in risk_levels]
    
    # 绘制情感分数线
    ax.plot(dates, scores, color='gray', linewidth=1, alpha=0.5, linestyle='--')
    ax.scatter(dates, scores, c=point_colors, s=150, zorder=5, edgecolors='white', linewidth=2)
    
    # 添加事件标签
    for i, (date, score, title, rl) in enumerate(zip(dates, scores, titles, risk_levels)):
        offset = 0.12 if i % 2 == 0 else -0.12
        ax.annotate(title,
            xy=(date, score),
            xytext=(date, score + offset),
            fontsize=7.5,
            ha='center',
            va='bottom' if offset > 0 else 'top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor=color_map.get(rl, 'gray'), alpha=0.9),
            arrowprops=dict(arrowstyle='->', color=color_map.get(rl, 'gray'), lw=1))
    
    # 参考线
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax.axhline(y=-0.3, color=COLORS['warning'], linestyle='--', alpha=0.3, label='中等风险阈值')
    ax.axhline(y=-0.7, color=COLORS['danger'], linestyle='--', alpha=0.3, label='高风险阈值')
    
    ax.fill_between(dates, -1, -0.7, alpha=0.05, color='red')
    ax.fill_between(dates, -0.7, -0.3, alpha=0.03, color='orange')
    
    ax.set_xlabel('日期', fontsize=11)
    ax.set_ylabel('舆情分数', fontsize=11)
    ax.set_title('iRobot 舆情事件时间线与情感分析', fontsize=14, fontweight='bold', pad=15)
    ax.set_ylim(-1.1, 0.3)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/06_sentiment_timeline.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK] 舆情时间线已保存")

def chart7_macro_context():
    """图表7: 宏观经济背景"""
    print("  → 生成宏观经济背景图...")
    
    with open(f'{DATA_DIR}/macro_snapshot.json', 'r') as f:
        macro = json.load(f)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # GDP增长率趋势
    ax = axes[0, 0]
    quarters = ['2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2', '2025Q3']
    gdp_growth = [1.6, 3.0, 3.1, 2.3, 2.4, 2.8, 4.4]
    colors_gdp = [COLORS['success'] if g >= 2.0 else COLORS['warning'] for g in gdp_growth]
    ax.bar(quarters, gdp_growth, color=colors_gdp, alpha=0.8)
    ax.set_title('美国GDP增长率（年化季度，%）', fontsize=11, fontweight='bold')
    ax.set_ylabel('%')
    ax.axhline(y=2.0, color='gray', linestyle='--', alpha=0.5)
    ax.tick_params(axis='x', rotation=45)
    for i, v in enumerate(gdp_growth):
        ax.text(i, v + 0.1, f'{v}%', ha='center', fontsize=8)
    
    # 失业率趋势
    ax = axes[0, 1]
    months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月']
    unrate = [4.0, 4.1, 4.1, 4.2, 4.2, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6]
    ax.plot(months, unrate, color=COLORS['danger'], linewidth=2, marker='o', markersize=5)
    ax.fill_between(months, unrate, alpha=0.1, color=COLORS['danger'])
    ax.set_title('美国失业率趋势（2025年，%）', fontsize=11, fontweight='bold')
    ax.set_ylabel('%')
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylim(3.8, 4.8)
    ax.grid(True, alpha=0.3)
    
    # 关键指标仪表盘
    ax = axes[1, 0]
    indicators = ['GDP\n(万亿$)', '失业率\n(%)', '通胀率\n(%)', '联邦基金\n利率(%)']
    values = [31.1, 4.6, 2.5, 4.4]
    bar_colors = [COLORS['success'], COLORS['warning'], COLORS['primary'], COLORS['primary']]
    bars = ax.bar(indicators, values, color=bar_colors, alpha=0.8, width=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
               f'{val}', ha='center', fontsize=11, fontweight='bold')
    ax.set_title('美国关键经济指标（最新值）', fontsize=11, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.3)
    
    # 经济展望文字
    ax = axes[1, 1]
    ax.axis('off')
    outlook_text = (
        "2026年美国经济展望\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "GDP增长预测: 2.1%\n"
        "失业率预测: 4.5%\n"
        "联邦预算赤字: 1.9万亿美元\n"
        "联邦债务/GDP: 预计2036年达120%\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "宏观环境评估: 温和增长\n"
        "对消费电子行业影响: 中性偏负面\n"
        "（失业率上升抑制消费支出）"
    )
    ax.text(0.1, 0.95, outlook_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor=COLORS['light_bg'], edgecolor='gray', alpha=0.8))
    
    fig.suptitle('美国宏观经济背景分析', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(f'{CHART_DIR}/07_macro_context.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("    [OK] 宏观经济背景图已保存")

def main():
    print("=" * 60)
    print("开始生成可视化图表...")
    print("=" * 60)
    
    chart1_stock_price_history()
    chart2_risk_radar()
    chart3_risk_heatmap()
    chart4_revenue_trend()
    chart5_risk_pie()
    chart6_sentiment_timeline()
    chart7_macro_context()
    
    print(f"\n{'=' * 60}")
    print(f"所有图表已生成完毕！保存目录: {CHART_DIR}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()

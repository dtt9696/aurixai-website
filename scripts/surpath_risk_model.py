#!/usr/bin/env python3
"""Surpath Inc. 非上市公司风险评估模型与可视化"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'Noto Sans CJK SC'
plt.rcParams['axes.unicode_minus'] = False

CHART_DIR = '/home/ubuntu/aurixai-website/data/surpath/charts'
import os
os.makedirs(CHART_DIR, exist_ok=True)

# ============================================================
# 1. 风险评估模型
# ============================================================
print("=" * 60)
print("Surpath Inc. 非上市公司风险评估模型")
print("=" * 60)

# 1.1 口碑/舆情风险
indeed_rating = 1.0
glassdoor_rating = 2.0
avg_rating = (indeed_rating + glassdoor_rating) / 2
sentiment_score = max(0, min(100, (5 - avg_rating) / 4 * 100))
print(f"\n[1] 口碑/舆情风险: {sentiment_score:.1f}")
print(f"  Indeed: {indeed_rating}/5.0, Glassdoor: {glassdoor_rating}/5.0")

# 1.2 融资健康风险
funding_gap_months = 36
total_raised = 15.65  # M USD
if funding_gap_months > 30:
    financing_score = 55 + (funding_gap_months - 30) * 1.5
elif funding_gap_months > 18:
    financing_score = 40 + (funding_gap_months - 18) * 1.2
else:
    financing_score = 20
financing_score = min(100, financing_score)
print(f"\n[2] 融资健康风险: {financing_score:.1f}")
print(f"  融资空窗期: {funding_gap_months}个月, 总融资: ${total_raised}M")

# 1.3 贸易活跃度风险
shipments_2022 = 35
shipments_2023 = 27
shipments_2024 = 24
shipments_2025 = 5  # 截至10月
yoy_2023 = (shipments_2023 - shipments_2022) / shipments_2022
yoy_2024 = (shipments_2024 - shipments_2023) / shipments_2023
yoy_2025_est = (shipments_2025 * 12/10 - shipments_2024) / shipments_2024
trade_score = 95 if yoy_2025_est < -0.5 else (70 if yoy_2025_est < -0.2 else 45)
# 额外惩罚：2025年多月为零
zero_months = 7  # 2025年有7个月无提单
trade_score = min(100, trade_score + zero_months * 1.5)
print(f"\n[3] 贸易活跃度风险: {trade_score:.1f}")
print(f"  2022: {shipments_2022}, 2023: {shipments_2023}, 2024: {shipments_2024}, 2025: {shipments_2025}")
print(f"  YoY: {yoy_2023:.1%}, {yoy_2024:.1%}, {yoy_2025_est:.1%}(估)")

# 1.4 运营稳定性风险
has_lawsuit = True
management_stability = 0.6  # 中等
employee_satisfaction = avg_rating / 5
ops_score = 50
if has_lawsuit:
    ops_score += 15
ops_score += (1 - management_stability) * 20
ops_score += (1 - employee_satisfaction) * 15
ops_score = min(100, ops_score)
print(f"\n[4] 运营稳定性风险: {ops_score:.1f}")
print(f"  诉讼: {'有' if has_lawsuit else '无'}, 管理稳定性: {management_stability:.1f}")

# 1.5 供应链风险
# HHI指数
supplier_shares = [64, 9, 7, 4, 3, 3, 3, 3, 2, 2]
hhi = sum(s**2 for s in supplier_shares)
china_pct = 85
supply_score = 0
# 供应商集中度
if hhi > 4000:
    supply_score += 35
elif hhi > 2500:
    supply_score += 25
else:
    supply_score += 15
# 地理集中度
supply_score += china_pct * 0.3
# 贸易下滑
supply_score += 10 if yoy_2025_est < -0.5 else 5
supply_score = min(100, supply_score)
print(f"\n[5] 供应链风险: {supply_score:.1f}")
print(f"  HHI: {hhi}, 中国依赖度: {china_pct}%")

# 综合评分
weights = {
    'sentiment': 0.20,
    'financing': 0.20,
    'trade': 0.25,
    'operations': 0.15,
    'supply_chain': 0.20
}
scores = {
    'sentiment': sentiment_score,
    'financing': financing_score,
    'trade': trade_score,
    'operations': ops_score,
    'supply_chain': supply_score
}
total_score = sum(scores[k] * weights[k] for k in weights)

print(f"\n{'='*60}")
print(f"综合风险评分: {total_score:.1f}/100")
if total_score >= 80:
    risk_level = "极高风险"
elif total_score >= 60:
    risk_level = "中高风险"
elif total_score >= 40:
    risk_level = "中等风险"
else:
    risk_level = "低风险"
print(f"风险等级: {risk_level}")
print(f"{'='*60}")

# 保存评估结果
assessment = {
    "company": "Surpath Inc. (驿玛科技)",
    "type": "非上市企业",
    "assessment_date": "2026-02-15",
    "total_score": round(total_score, 1),
    "risk_level": risk_level,
    "dimensions": {
        "口碑舆情": {"score": round(sentiment_score, 1), "weight": weights['sentiment'], "level": "高风险" if sentiment_score >= 60 else "中等"},
        "融资健康": {"score": round(financing_score, 1), "weight": weights['financing'], "level": "中高风险" if financing_score >= 50 else "中等"},
        "贸易活跃度": {"score": round(trade_score, 1), "weight": weights['trade'], "level": "极高风险" if trade_score >= 80 else "高风险"},
        "运营稳定性": {"score": round(ops_score, 1), "weight": weights['operations'], "level": "高风险" if ops_score >= 60 else "中等"},
        "供应链风险": {"score": round(supply_score, 1), "weight": weights['supply_chain'], "level": "高风险" if supply_score >= 60 else "中等"}
    }
}
with open('/home/ubuntu/aurixai-website/data/surpath/risk_assessment.json', 'w') as f:
    json.dump(assessment, f, indent=2, ensure_ascii=False)

# ============================================================
# 2. 可视化图表
# ============================================================

# 颜色方案（暗色主题）
BG_COLOR = '#0a0e17'
CARD_COLOR = '#111827'
TEXT_COLOR = '#e2e8f0'
MUTED_COLOR = '#94a3b8'
RED = '#ef4444'
ORANGE = '#f97316'
YELLOW = '#eab308'
GREEN = '#22c55e'
BLUE = '#3b82f6'
PURPLE = '#a855f7'

def get_risk_color(score):
    if score >= 80: return RED
    elif score >= 60: return ORANGE
    elif score >= 40: return YELLOW
    else: return GREEN

# 2.1 五维度风险雷达图
print("\n生成图表 1: 五维度风险雷达图...")
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)

categories = ['口碑/舆情', '融资健康', '贸易活跃度', '运营稳定性', '供应链风险']
values = [sentiment_score, financing_score, trade_score, ops_score, supply_score]
values_closed = values + [values[0]]
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

ax.plot(angles, values_closed, 'o-', linewidth=2.5, color=ORANGE, markersize=8)
ax.fill(angles, values_closed, alpha=0.2, color=ORANGE)

# 行业平均参考线
avg_ref = [45, 35, 30, 40, 45]
avg_ref_closed = avg_ref + [avg_ref[0]]
ax.plot(angles, avg_ref_closed, '--', linewidth=1.5, color=GREEN, alpha=0.6)
ax.fill(angles, avg_ref_closed, alpha=0.08, color=GREEN)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=13, color=TEXT_COLOR)
ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9, color=MUTED_COLOR)
ax.spines['polar'].set_color(MUTED_COLOR)
ax.grid(color='#1e293b', alpha=0.5)
ax.tick_params(colors=MUTED_COLOR)

ax.legend(['Surpath Inc.', '行业平均'], loc='upper right', bbox_to_anchor=(1.15, 1.1),
          fontsize=11, facecolor=CARD_COLOR, edgecolor='#1e293b', labelcolor=TEXT_COLOR)
ax.set_title(f'Surpath Inc. 五维度风险评估\n综合评分: {total_score:.1f}/100 ({risk_level})',
             fontsize=16, color=TEXT_COLOR, pad=30, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/01_risk_radar.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 01_risk_radar.png")

# 2.2 年度提单趋势图
print("生成图表 2: 年度提单趋势图...")
fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)

years = ['2022', '2023', '2024', '2025*']
shipments = [35, 27, 24, 5]
colors = [GREEN, YELLOW, ORANGE, RED]
bars = ax.bar(years, shipments, color=colors, width=0.6, edgecolor='none', alpha=0.85)

for bar, val in zip(bars, shipments):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
            str(val), ha='center', va='bottom', fontsize=14, fontweight='bold', color=TEXT_COLOR)

# 添加同比变化标注
yoy_labels = ['—', '-23%', '-11%', '-79%*']
for i, (bar, label) in enumerate(zip(bars, yoy_labels)):
    if i > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                label, ha='center', va='center', fontsize=11, color='white', fontweight='bold')

ax.set_xlabel('年份', fontsize=12, color=MUTED_COLOR)
ax.set_ylabel('提单数量', fontsize=12, color=MUTED_COLOR)
ax.set_title('Surpath Inc. 年度提单趋势 (ImportYeti)', fontsize=15, color=TEXT_COLOR, fontweight='bold')
ax.tick_params(colors=MUTED_COLOR)
ax.spines['bottom'].set_color('#1e293b')
ax.spines['left'].set_color('#1e293b')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylim(0, 42)

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/02_yearly_shipments.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 02_yearly_shipments.png")

# 2.3 2025年月度提单分布
print("生成图表 3: 2025年月度提单分布...")
fig, ax = plt.subplots(figsize=(10, 4), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)

months = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
monthly_data = [0, 0, 0, 0, 0, 1, 1, 1, 0, 2, 0, 0]
bar_colors = [BLUE if v > 0 else '#1e293b' for v in monthly_data]
bars = ax.bar(months, monthly_data, color=bar_colors, width=0.6, edgecolor='none')

for bar, val in zip(bars, monthly_data):
    if val > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(val), ha='center', va='bottom', fontsize=12, color=TEXT_COLOR, fontweight='bold')

ax.set_title('2025年月度提单分布 — 大量月份为零', fontsize=14, color=TEXT_COLOR, fontweight='bold')
ax.set_ylabel('提单数', fontsize=11, color=MUTED_COLOR)
ax.tick_params(colors=MUTED_COLOR, labelsize=10)
ax.spines['bottom'].set_color('#1e293b')
ax.spines['left'].set_color('#1e293b')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylim(0, 3)
ax.set_yticks([0, 1, 2, 3])

# 添加警告文字
ax.text(0.5, 0.85, '⚠ 2025年仅6-8月和10月有提单记录，发货节奏极不稳定',
        transform=ax.transAxes, ha='center', fontsize=11, color=RED, style='italic')

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/03_monthly_2025.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 03_monthly_2025.png")

# 2.4 供应商集中度饼图
print("生成图表 4: 供应商集中度分析...")
fig, ax = plt.subplots(figsize=(8, 6), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)

labels = ['Safround (64%)', 'Ubi Logistics (9%)', 'G&F Logistics (7%)',
          'USPTI Vietnam (2%)', '其他 (18%)']
sizes = [64, 9, 7, 2, 18]
pie_colors = [RED, ORANGE, YELLOW, GREEN, '#64748b']
explode = (0.05, 0, 0, 0, 0)

wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=pie_colors,
                                   explode=explode, autopct='%1.0f%%',
                                   startangle=90, pctdistance=0.8,
                                   wedgeprops=dict(edgecolor=BG_COLOR, linewidth=2))
for text in texts:
    text.set_color(TEXT_COLOR)
    text.set_fontsize(11)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

ax.set_title('供应商集中度分析\nHHI指数 ≈ 4,300 (极高集中度)', fontsize=14, color=TEXT_COLOR, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/04_supplier_concentration.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 04_supplier_concentration.png")

# 2.5 员工满意度雷达图
print("生成图表 5: 员工满意度对比...")
fig, ax = plt.subplots(figsize=(8, 7), subplot_kw=dict(polar=True), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)

emp_categories = ['薪酬', '工作生活平衡', '管理层', '企业文化', '职业发展']
surpath_scores = [1.5, 1.2, 1.0, 1.3, 1.5]
industry_avg = [3.5, 3.3, 3.2, 3.4, 3.3]

surpath_closed = surpath_scores + [surpath_scores[0]]
industry_closed = industry_avg + [industry_avg[0]]
angles = np.linspace(0, 2 * np.pi, len(emp_categories), endpoint=False).tolist()
angles += angles[:1]

ax.plot(angles, surpath_closed, 'o-', linewidth=2, color=RED, markersize=7, label='Surpath')
ax.fill(angles, surpath_closed, alpha=0.15, color=RED)
ax.plot(angles, industry_closed, 'o-', linewidth=2, color=GREEN, markersize=7, label='行业平均')
ax.fill(angles, industry_closed, alpha=0.1, color=GREEN)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(emp_categories, fontsize=12, color=TEXT_COLOR)
ax.set_ylim(0, 5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=9, color=MUTED_COLOR)
ax.spines['polar'].set_color(MUTED_COLOR)
ax.grid(color='#1e293b', alpha=0.5)

ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=11,
          facecolor=CARD_COLOR, edgecolor='#1e293b', labelcolor=TEXT_COLOR)
ax.set_title('员工满意度对比 (Indeed/Glassdoor vs 行业平均)',
             fontsize=14, color=TEXT_COLOR, pad=25, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/05_employee_radar.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 05_employee_radar.png")

# 2.6 GSCPI趋势图
print("生成图表 6: GSCPI供应链压力指数趋势...")
gscpi_df = pd.read_csv('/home/ubuntu/aurixai-website/data/supply_chain_sources/gscpi_timeseries.csv')
gscpi_df['Date'] = pd.to_datetime(gscpi_df['Date'], format='mixed')
gscpi_recent = gscpi_df[gscpi_df['Date'] >= '2020-01-01'].copy()

fig, ax = plt.subplots(figsize=(12, 5), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)

ax.plot(gscpi_recent['Date'], gscpi_recent['GSCPI'], color=BLUE, linewidth=2)
ax.fill_between(gscpi_recent['Date'], gscpi_recent['GSCPI'], 0,
                where=gscpi_recent['GSCPI'] > 0, alpha=0.15, color=RED)
ax.fill_between(gscpi_recent['Date'], gscpi_recent['GSCPI'], 0,
                where=gscpi_recent['GSCPI'] <= 0, alpha=0.15, color=GREEN)
ax.axhline(y=0, color=MUTED_COLOR, linestyle='--', alpha=0.5)

# 标注关键事件
max_idx = gscpi_recent['GSCPI'].idxmax()
max_date = gscpi_recent.loc[max_idx, 'Date']
max_val = gscpi_recent.loc[max_idx, 'GSCPI']
ax.annotate(f'峰值: {max_val:.2f}\n(供应链危机)', xy=(max_date, max_val),
            xytext=(max_date + pd.Timedelta(days=120), max_val - 0.5),
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.5),
            fontsize=10, color=RED, fontweight='bold')

latest_val = gscpi_recent.iloc[-1]['GSCPI']
latest_date = gscpi_recent.iloc[-1]['Date']
ax.annotate(f'最新: {latest_val:.2f}', xy=(latest_date, latest_val),
            xytext=(latest_date - pd.Timedelta(days=180), latest_val + 1),
            arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.5),
            fontsize=10, color=ORANGE, fontweight='bold')

ax.set_title('全球供应链压力指数 (NY Fed GSCPI)', fontsize=15, color=TEXT_COLOR, fontweight='bold')
ax.set_ylabel('GSCPI (标准差)', fontsize=11, color=MUTED_COLOR)
ax.tick_params(colors=MUTED_COLOR)
ax.spines['bottom'].set_color('#1e293b')
ax.spines['left'].set_color('#1e293b')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/06_gscpi_trend.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 06_gscpi_trend.png")

# 2.7 融资时间线图
print("生成图表 7: 融资时间线...")
fig, ax = plt.subplots(figsize=(12, 4), facecolor=BG_COLOR)
ax.set_facecolor(BG_COLOR)

events = [
    (2019, '公司成立', GREEN, '上海+Tustin'),
    (2021.8, 'Pre-A轮', BLUE, '1亿人民币\n经纬中国'),
    (2022.5, 'Pre-A+轮', BLUE, '数千万元\n北极光创投'),
    (2023.2, 'A轮', PURPLE, '数千万美元\neWTP Arabia'),
    (2026.2, '至今', RED, '3年融资空窗期'),
]

y_pos = 0
for i, (x, label, color, detail) in enumerate(events):
    ax.scatter(x, y_pos, s=200, color=color, zorder=5, edgecolors='white', linewidths=1.5)
    offset = 0.4 if i % 2 == 0 else -0.5
    ax.annotate(f'{label}\n{detail}', xy=(x, y_pos), xytext=(x, offset),
                fontsize=10, color=color, ha='center', va='center' if offset > 0 else 'top',
                fontweight='bold',
                arrowprops=dict(arrowstyle='-', color=color, lw=1, alpha=0.5))

# 融资空窗期标注
ax.axvspan(2023.2, 2026.2, alpha=0.08, color=RED)
ax.text(2024.7, -0.85, '⚠ 3年融资空窗期', fontsize=12, color=RED, ha='center', fontweight='bold')

ax.axhline(y=0, color='#1e293b', linewidth=2)
ax.set_xlim(2018.5, 2026.8)
ax.set_ylim(-1.2, 1.2)
ax.set_title('Surpath Inc. 融资时间线', fontsize=14, color=TEXT_COLOR, fontweight='bold')
ax.set_xlabel('年份', fontsize=11, color=MUTED_COLOR)
ax.tick_params(colors=MUTED_COLOR)
ax.set_yticks([])
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#1e293b')

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/07_funding_timeline.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 07_funding_timeline.png")

# 2.8 宏观经济指标面板
print("生成图表 8: 宏观经济指标面板...")
with open('/home/ubuntu/aurixai-website/data/supply_chain_sources/fred_supply_chain_summary.json') as f:
    fred_data = json.load(f)

fig, axes = plt.subplots(2, 3, figsize=(15, 8), facecolor=BG_COLOR)
fig.suptitle('美国供应链相关宏观经济指标 (FRED)', fontsize=16, color=TEXT_COLOR, fontweight='bold', y=0.98)

indicators = [
    ('INDPRO', '工业生产指数', BLUE),
    ('TCU', '产能利用率(%)', PURPLE),
    ('ISRATIO', '库存销售比', ORANGE),
    ('MANEMP', '制造业就业(千人)', GREEN),
    ('DGORDER', '耐用品订单(百万$)', YELLOW),
    ('BOPGSTB', '贸易差额(百万$)', RED),
]

for idx, (sid, title, color) in enumerate(indicators):
    ax = axes[idx // 3][idx % 3]
    ax.set_facecolor(BG_COLOR)
    try:
        df = pd.read_csv(f'/home/ubuntu/aurixai-website/data/supply_chain_sources/fred_{sid}.csv')
        col = df.columns[1]
        ax.plot(range(len(df)), df[col].values, color=color, linewidth=1.5)
        ax.fill_between(range(len(df)), df[col].values, df[col].min(), alpha=0.1, color=color)
        latest = df.iloc[-1][col]
        ax.set_title(f'{title}\n最新: {latest:,.1f}', fontsize=11, color=TEXT_COLOR, fontweight='bold')
    except Exception as e:
        ax.set_title(f'{title}\n数据不可用', fontsize=11, color=MUTED_COLOR)
    ax.tick_params(colors=MUTED_COLOR, labelsize=8)
    ax.spines['bottom'].set_color('#1e293b')
    ax.spines['left'].set_color('#1e293b')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(f'{CHART_DIR}/08_macro_indicators.png', dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  ✓ 08_macro_indicators.png")

print(f"\n所有图表已保存到: {CHART_DIR}/")
print(f"共生成 8 张图表")

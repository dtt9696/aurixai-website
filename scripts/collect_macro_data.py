#!/usr/bin/env python3
"""
FRED 宏观经济数据采集脚本
获取美国关键宏观经济指标：GDP、CPI、失业率、利率等
"""
import os
import requests
import pandas as pd
import json
from datetime import datetime

API_KEY = os.getenv("FRED_API_KEY", "")
BASE_URL = "https://api.stlouisfed.org/fred"

# 关键经济指标
SERIES_MAP = {
    'GDP': '国内生产总值（季度，十亿美元）',
    'GDPC1': '实际GDP（季度，十亿美元）',
    'UNRATE': '失业率（月度，%）',
    'CPIAUCSL': '消费者价格指数（月度）',
    'FEDFUNDS': '联邦基金利率（月度，%）',
    'DGS10': '10年期国债收益率（日度，%）',
    'PAYEMS': '非农就业人数（月度，千人）',
    'INDPRO': '工业生产指数（月度）',
    'UMCSENT': '消费者信心指数（月度）',
}

def fetch_fred_series(series_id, limit=60):
    """获取FRED时间序列数据"""
    try:
        response = requests.get(
            f"{BASE_URL}/series/observations",
            params={
                "api_key": API_KEY,
                "series_id": series_id,
                "file_type": "json",
                "sort_order": "desc",
                "limit": limit
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('observations', [])
        else:
            print(f"  [WARN] 获取 {series_id} 失败: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"  [ERROR] 获取 {series_id} 异常: {e}")
        return []

def get_latest_value(series_id):
    """获取某个指标的最新值"""
    obs = fetch_fred_series(series_id, limit=5)
    for o in obs:
        if o.get('value') and o['value'] != '.':
            return {'date': o['date'], 'value': float(o['value'])}
    return None

def main():
    print("=" * 60)
    print("开始获取FRED宏观经济数据...")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    os.makedirs('/home/ubuntu/aurixai-website/data', exist_ok=True)

    # 1. 获取最新经济快照
    snapshot = {}
    for series_id, description in SERIES_MAP.items():
        latest = get_latest_value(series_id)
        if latest:
            snapshot[series_id] = {
                'description': description,
                'value': latest['value'],
                'date': latest['date']
            }
            print(f"  [OK] {series_id}: {description} = {latest['value']} ({latest['date']})")
        else:
            print(f"  [FAIL] {series_id}: {description}")

    # 保存快照
    with open('/home/ubuntu/aurixai-website/data/macro_snapshot.json', 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"\n经济快照已保存，共 {len(snapshot)} 个指标。")

    # 2. 获取时间序列数据（用于趋势分析）
    all_data = []
    key_series = ['GDP', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS', 'DGS10']
    for series_id in key_series:
        observations = fetch_fred_series(series_id, limit=60)
        if observations:
            for obs in observations:
                if obs.get('value') and obs['value'] != '.':
                    all_data.append({
                        'series_id': series_id,
                        'description': SERIES_MAP[series_id],
                        'date': obs['date'],
                        'value': float(obs['value'])
                    })

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv('/home/ubuntu/aurixai-website/data/macro_timeseries.csv', index=False)
        print(f"时间序列数据已保存，共 {len(df)} 条记录。")

    return snapshot

if __name__ == "__main__":
    main()

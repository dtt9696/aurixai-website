#!/usr/bin/env python3
"""
iRobot (IRBT) 财务数据与股价历史采集脚本
使用 Yahoo Finance API 获取股价图表和公司洞察
"""
import sys
import json
import os
import pandas as pd
from datetime import datetime

sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

DATA_DIR = '/home/ubuntu/aurixai-website/data'
os.makedirs(DATA_DIR, exist_ok=True)

def get_stock_chart(symbol='IRBT', range_period='1y', interval='1d'):
    """获取股价历史数据"""
    client = ApiClient()
    print(f"  → 获取 {symbol} 股价数据 (范围: {range_period}, 间隔: {interval})...")
    
    try:
        response = client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'region': 'US',
            'interval': interval,
            'range': range_period,
            'includeAdjustedClose': True,
            'events': 'div,split'
        })
        
        if response and 'chart' in response and 'result' in response['chart']:
            result = response['chart']['result'][0]
            meta = result.get('meta', {})
            timestamps = result.get('timestamp', [])
            quotes = result.get('indicators', {}).get('quote', [{}])[0]
            adj_close = result.get('indicators', {}).get('adjclose', [{}])
            
            # 保存元数据
            meta_info = {
                'symbol': meta.get('symbol'),
                'longName': meta.get('longName', 'iRobot Corporation'),
                'currency': meta.get('currency'),
                'exchange': meta.get('exchangeName'),
                'regularMarketPrice': meta.get('regularMarketPrice'),
                'regularMarketDayHigh': meta.get('regularMarketDayHigh'),
                'regularMarketDayLow': meta.get('regularMarketDayLow'),
                'regularMarketVolume': meta.get('regularMarketVolume'),
                'fiftyTwoWeekHigh': meta.get('fiftyTwoWeekHigh'),
                'fiftyTwoWeekLow': meta.get('fiftyTwoWeekLow'),
                'previousClose': meta.get('previousClose'),
                'chartPreviousClose': meta.get('chartPreviousClose'),
            }
            
            with open(f'{DATA_DIR}/irbt_meta.json', 'w', encoding='utf-8') as f:
                json.dump(meta_info, f, ensure_ascii=False, indent=2)
            print(f"    [OK] 元数据已保存: 当前价格 ${meta.get('regularMarketPrice', 'N/A')}")
            
            # 构建价格DataFrame
            price_data = []
            for i, ts in enumerate(timestamps):
                date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                row = {
                    'date': date,
                    'open': quotes.get('open', [None])[i] if i < len(quotes.get('open', [])) else None,
                    'high': quotes.get('high', [None])[i] if i < len(quotes.get('high', [])) else None,
                    'low': quotes.get('low', [None])[i] if i < len(quotes.get('low', [])) else None,
                    'close': quotes.get('close', [None])[i] if i < len(quotes.get('close', [])) else None,
                    'volume': quotes.get('volume', [None])[i] if i < len(quotes.get('volume', [])) else None,
                }
                if adj_close and len(adj_close) > 0:
                    adj = adj_close[0].get('adjclose', [])
                    row['adj_close'] = adj[i] if i < len(adj) else None
                price_data.append(row)
            
            df = pd.DataFrame(price_data)
            df = df.dropna(subset=['close'])
            df.to_csv(f'{DATA_DIR}/irbt_stock_prices.csv', index=False)
            print(f"    [OK] 股价数据已保存: {len(df)} 个交易日")
            
            return meta_info, df
        else:
            print("    [FAIL] 无法获取股价数据")
            return None, None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None, None

def get_stock_insights(symbol='IRBT'):
    """获取股票洞察和分析数据"""
    client = ApiClient()
    print(f"  → 获取 {symbol} 股票洞察...")
    
    try:
        response = client.call_api('YahooFinance/get_stock_insights', query={
            'symbol': symbol
        })
        
        if response:
            with open(f'{DATA_DIR}/irbt_insights.json', 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            print(f"    [OK] 股票洞察数据已保存")
            return response
        else:
            print("    [FAIL] 无法获取洞察数据")
            return None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None

def build_financial_summary():
    """
    基于公开搜索结果构建iRobot财务摘要
    数据来源：iRobot Q3 2025财报、SEC文件、公开报道
    """
    financial_summary = {
        'company_info': {
            'name': 'iRobot Corporation',
            'ticker': 'IRBT',
            'exchange': 'NASDAQ',
            'industry': '消费电子/智能家居机器人',
            'founded': '1990年',
            'headquarters': '美国马萨诸塞州贝德福德',
            'ceo': 'Gary Cohen（2024年5月起任CEO）',
            'employees': '约450人（2025年，大幅裁员后）',
            'main_products': 'Roomba扫地机器人、Braava拖地机器人',
        },
        'q3_2025': {
            'revenue': 145.8,  # 百万美元
            'revenue_yoy_change': -24.6,  # %
            'eps': -0.23,
            'eps_estimate': -0.65,
            'eps_beat': True,
            'us_revenue_change': -33,  # %
            'emea_revenue_change': -13,  # %
            'japan_revenue_change': -9,  # %
            'gross_margin': None,
            'note': '收入持续下滑，但EPS好于预期'
        },
        'annual_2024': {
            'revenue': 546.997,  # 百万美元
            'cost_of_revenue': 426.722,
            'gross_profit': 120.275,
            'operating_expense': 269.744,
            'operating_loss': -149.469,
            'note': '全年亏损严重，毛利率仅22%'
        },
        'annual_2023': {
            'revenue': 681.849,
            'cost_of_revenue': 539.492,
            'gross_profit': 142.357,
            'note': '亚马逊收购失败后收入大幅下滑'
        },
        'stock_performance': {
            'current_price': 0.22,  # 截至2025年12月
            'price_date': '2025-12-22',
            'ytd_change_pct': -86.2,  # 2025年8月至12月
            'fifty_two_week_high': None,
            'fifty_two_week_low': None,
            'market_cap_millions': None,
            'note': '股价跌至不足1美元，面临退市风险'
        },
        'key_risks': {
            'going_concern': '公司在Q3财报中表示"没有额外资本来源"，存在持续经营风险',
            'revenue_decline': '收入连续多个季度大幅下滑，美国市场下降33%',
            'competition': '面临中国品牌（如石头科技、科沃斯）的激烈竞争',
            'amazon_deal_failure': '2024年1月亚马逊14亿美元收购交易因欧盟反垄断审查失败',
            'restructuring': '大规模裁员，员工从约1400人减至约450人',
            'delisting_risk': '股价低于1美元，面临NASDAQ退市风险',
            'debt_burden': '重组费用和持续亏损加重财务负担'
        }
    }
    
    with open(f'{DATA_DIR}/irbt_financial_summary.json', 'w', encoding='utf-8') as f:
        json.dump(financial_summary, f, ensure_ascii=False, indent=2)
    print(f"  [OK] 财务摘要已保存")
    
    return financial_summary

def main():
    print("=" * 60)
    print("开始获取 iRobot (IRBT) 财务数据...")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 获取股价历史
    print("\n[1] 获取股价历史数据...")
    meta, prices_df = get_stock_chart('IRBT', '1y', '1d')
    
    # 也获取更长期的数据用于趋势分析
    print("\n[2] 获取长期股价数据...")
    meta_5y, prices_5y = get_stock_chart('IRBT', '5y', '1wk')
    if prices_5y is not None:
        prices_5y.to_csv(f'{DATA_DIR}/irbt_stock_prices_5y.csv', index=False)
        print(f"    [OK] 5年周线数据已保存: {len(prices_5y)} 条")
    
    # 2. 获取股票洞察
    print("\n[3] 获取股票洞察...")
    insights = get_stock_insights('IRBT')
    
    # 3. 构建财务摘要
    print("\n[4] 构建财务摘要...")
    summary = build_financial_summary()
    
    print("\n" + "=" * 60)
    print("iRobot 财务数据采集完成！")
    print("=" * 60)
    
    return meta, prices_df, insights, summary

if __name__ == "__main__":
    main()

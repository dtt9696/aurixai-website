#!/usr/bin/env python3
"""修复版数据源接入脚本"""
import json, os, sys, time, requests
import pandas as pd
from io import StringIO
from datetime import datetime

DATA_DIR = '/home/ubuntu/aurixai-website/data/supply_chain_sources'
os.makedirs(DATA_DIR, exist_ok=True)
results = {}

# 1. 修复GSCPI - 用openpyxl引擎
print("[1] 修复 GSCPI...")
try:
    df = pd.read_excel(os.path.join(DATA_DIR, 'gscpi_data.xlsx'), engine='openpyxl')
    # 清理数据
    # 找到实际数据开始的位置
    for i, row in df.iterrows():
        val = str(row.iloc[0]).strip().lower()
        if 'date' in val or '199' in val or '200' in val or '202' in val:
            break
    
    # 重新读取，跳过头部
    df_all = pd.read_excel(os.path.join(DATA_DIR, 'gscpi_data.xlsx'), engine='openpyxl', header=None)
    print(f"  原始数据形状: {df_all.shape}")
    print(f"  前5行:\n{df_all.head()}")
    
    # 找到header行
    header_row = None
    for idx, row in df_all.iterrows():
        if any('date' in str(v).lower() for v in row.values if pd.notna(v)):
            header_row = idx
            break
    
    if header_row is not None:
        df_data = pd.read_excel(os.path.join(DATA_DIR, 'gscpi_data.xlsx'), engine='openpyxl', header=header_row)
    else:
        df_data = df_all
    
    csv_path = os.path.join(DATA_DIR, 'gscpi_timeseries.csv')
    df_data.to_csv(csv_path, index=False)
    print(f"  ✓ GSCPI: {len(df_data)}行, 列: {list(df_data.columns)}")
    print(f"  最新数据: {df_data.iloc[-1].to_dict()}")
    results['gscpi'] = {'status': 'success', 'rows': len(df_data)}
except Exception as e:
    print(f"  ✗ GSCPI错误: {e}")
    results['gscpi'] = {'status': 'failed', 'error': str(e)}

# 2. 修复FRED - 直接用CSV下载端点
print("\n[2] 修复 FRED 供应链数据...")
series_map = {
    'MANEMP': '制造业就业人数(千人)',
    'DGORDER': '耐用品新订单(百万美元)',
    'ISRATIO': '库存销售比',
    'INDPRO': '工业生产指数',
    'TCU': '产能利用率(%)',
    'BOPGSTB': '贸易差额(十亿美元)',
    'PCUOMFG': '制造业PPI',
    'CPIAUCSL': 'CPI消费者价格指数',
}

fred_data = {}
success = 0
for sid, desc in series_map.items():
    try:
        # 使用FRED Graph CSV端点（无需API Key）
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id={sid}&scale=left&cosd=2020-01-01&coed=2026-02-01&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2026-02-14&revision_date=2026-02-14&nd=2020-01-01"
        resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200 and 'DATE' in resp.text[:50]:
            df = pd.read_csv(StringIO(resp.text))
            # 替换 "." 为 NaN
            df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce')
            df = df.dropna()
            csv_path = os.path.join(DATA_DIR, f'fred_{sid}.csv')
            df.to_csv(csv_path, index=False)
            latest = df.iloc[-1] if len(df) > 0 else None
            fred_data[sid] = {
                'description': desc,
                'rows': len(df),
                'latest_date': str(latest.iloc[0]) if latest is not None else 'N/A',
                'latest_value': float(latest.iloc[1]) if latest is not None else None
            }
            success += 1
            print(f"  ✓ {sid} ({desc}): {len(df)}行, 最新={fred_data[sid]['latest_value']}")
        else:
            print(f"  ✗ {sid}: HTTP {resp.status_code}")
        time.sleep(0.5)
    except Exception as e:
        print(f"  ✗ {sid}: {e}")
        fred_data[sid] = {'description': desc, 'error': str(e)}

filepath = os.path.join(DATA_DIR, 'fred_supply_chain_summary.json')
with open(filepath, 'w') as f:
    json.dump(fred_data, f, indent=2, ensure_ascii=False)
print(f"  FRED总计: {success}/{len(series_map)}个系列成功")
results['fred'] = {'status': 'success' if success > 0 else 'failed', 'count': success}

# 3. 验证World Bank LPI
print("\n[3] 验证 World Bank LPI...")
try:
    df_lpi = pd.read_csv(os.path.join(DATA_DIR, 'world_bank_lpi.csv'))
    print(f"  ✓ LPI数据: {len(df_lpi)}行, {df_lpi['country'].nunique()}个国家")
    # 显示美国数据
    us_data = df_lpi[df_lpi['country_code'] == 'USA']
    if len(us_data) > 0:
        print(f"  美国LPI数据: {len(us_data)}条")
        for _, row in us_data.iterrows():
            print(f"    {row['indicator_name']} ({row['year']}): {row['value']}")
    results['world_bank_lpi'] = {'status': 'success', 'rows': len(df_lpi)}
except Exception as e:
    print(f"  ✗ LPI验证失败: {e}")
    results['world_bank_lpi'] = {'status': 'failed', 'error': str(e)}

# 4. Census Bureau - 使用替代端点
print("\n[4] 获取 Census Bureau 贸易数据...")
try:
    # 使用简化的API端点
    url = "https://api.census.gov/data/timeseries/intltrade/imports/hs?get=I_COMMODITY,I_COMMODITY_LDESC,GEN_VAL_MO&COMM_LVL=HS2&time=2024-12"
    resp = requests.get(url, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        if data and len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            csv_path = os.path.join(DATA_DIR, 'census_imports_hs2.csv')
            df.to_csv(csv_path, index=False)
            print(f"  ✓ Census贸易数据: {len(df)}条记录")
            results['census'] = {'status': 'success', 'rows': len(df)}
        else:
            results['census'] = {'status': 'empty'}
    else:
        print(f"  ⚠ Census API: HTTP {resp.status_code}")
        # 尝试贸易差额数据
        url2 = "https://api.census.gov/data/timeseries/intltrade/imports/enduse?get=I_ENDUSE,I_ENDUSE_LDESC,GEN_VAL_MO&time=2024-12"
        resp2 = requests.get(url2, timeout=15)
        if resp2.status_code == 200:
            data2 = resp2.json()
            if data2 and len(data2) > 1:
                df2 = pd.DataFrame(data2[1:], columns=data2[0])
                csv_path = os.path.join(DATA_DIR, 'census_imports_enduse.csv')
                df2.to_csv(csv_path, index=False)
                print(f"  ✓ Census End-Use贸易数据: {len(df2)}条记录")
                results['census'] = {'status': 'success', 'rows': len(df2)}
        else:
            results['census'] = {'status': 'partial', 'note': '需要免费注册API Key'}
except Exception as e:
    print(f"  ✗ Census: {e}")
    results['census'] = {'status': 'failed', 'error': str(e)}

# 5. DataBank API - 物流指标
print("\n[5] 获取 DataBank 物流指标...")
try:
    sys.path.append('/opt/.manus/.sandbox-runtime')
    from data_api import ApiClient
    client = ApiClient()
    
    all_inds = []
    for kw in ['logistics', 'freight', 'trade', 'container', 'port', 'transport', 'shipping', 'supply chain']:
        try:
            r = client.call_api('DataBank/indicator_list', query={'q': kw, 'pageSize': 30})
            if r and 'data' in r:
                for ind in r['data']:
                    ind_id = ind.get('id', '')
                    if ind_id not in [x['id'] for x in all_inds]:
                        all_inds.append({
                            'id': ind_id,
                            'name': ind.get('name', ''),
                            'source': ind.get('source', {}).get('value', ''),
                            'keyword': kw
                        })
        except:
            pass
    
    filepath = os.path.join(DATA_DIR, 'databank_logistics_indicators.json')
    with open(filepath, 'w') as f:
        json.dump(all_inds, f, indent=2)
    print(f"  ✓ DataBank物流指标: {len(all_inds)}个")
    results['databank'] = {'status': 'success', 'count': len(all_inds)}
except Exception as e:
    print(f"  ✗ DataBank: {e}")
    results['databank'] = {'status': 'failed', 'error': str(e)}

# 6. LMI物流经理指数 - 爬取
print("\n[6] 获取 LMI 物流经理指数...")
try:
    url = "https://www.the-lmi.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        text_path = os.path.join(DATA_DIR, 'lmi_homepage.txt')
        with open(text_path, 'w') as f:
            f.write(text[:5000])
        print(f"  ✓ LMI页面已保存")
        results['lmi'] = {'status': 'success'}
    else:
        results['lmi'] = {'status': 'failed', 'error': f'HTTP {resp.status_code}'}
except Exception as e:
    print(f"  ✗ LMI: {e}")
    results['lmi'] = {'status': 'failed', 'error': str(e)}

# 保存汇总
summary_path = os.path.join(DATA_DIR, 'connector_results.json')
with open(summary_path, 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print("最终结果汇总:")
for src, res in results.items():
    s = res.get('status', '?')
    icon = '✓' if s == 'success' else ('⚠' if s == 'partial' else '✗')
    print(f"  {icon} {src}: {s}")
print(f"\n数据目录: {DATA_DIR}")

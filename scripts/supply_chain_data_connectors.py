#!/usr/bin/env python3
"""
供应链数据源接入脚本
接入多个免费公开的美国物流供应链数据源
"""

import json
import os
import sys
import time
import csv
from datetime import datetime, timedelta
from io import StringIO

import requests
import pandas as pd

# 输出目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'supply_chain_sources')
os.makedirs(DATA_DIR, exist_ok=True)

results = {}

# ============================================================
# 1. NY Fed GSCPI - 全球供应链压力指数
# ============================================================
def fetch_gscpi():
    """从纽约联储下载GSCPI全球供应链压力指数数据"""
    print("\n[1/6] 获取 NY Fed GSCPI 全球供应链压力指数...")
    url = "https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            filepath = os.path.join(DATA_DIR, 'gscpi_data.xlsx')
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            
            # 解析Excel
            df = pd.read_excel(filepath, header=None)
            # 找到数据起始行
            data_start = None
            for i, row in df.iterrows():
                if str(row.iloc[0]).strip().lower() in ['date', 'month']:
                    data_start = i
                    break
            
            if data_start is not None:
                df_data = pd.read_excel(filepath, header=data_start)
                csv_path = os.path.join(DATA_DIR, 'gscpi_timeseries.csv')
                df_data.to_csv(csv_path, index=False)
                print(f"  ✓ GSCPI数据已保存: {len(df_data)}行")
                print(f"  ✓ 列名: {list(df_data.columns)}")
                # 获取最新值
                last_row = df_data.iloc[-1]
                results['gscpi'] = {
                    'status': 'success',
                    'rows': len(df_data),
                    'columns': list(df_data.columns),
                    'latest_date': str(last_row.iloc[0]),
                    'file': csv_path
                }
            else:
                # 尝试直接读取
                df_data = pd.read_excel(filepath)
                csv_path = os.path.join(DATA_DIR, 'gscpi_timeseries.csv')
                df_data.to_csv(csv_path, index=False)
                print(f"  ✓ GSCPI数据已保存: {len(df_data)}行")
                results['gscpi'] = {
                    'status': 'success',
                    'rows': len(df_data),
                    'columns': list(df_data.columns),
                    'file': csv_path
                }
        else:
            print(f"  ✗ 下载失败: HTTP {resp.status_code}")
            results['gscpi'] = {'status': 'failed', 'error': f'HTTP {resp.status_code}'}
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        results['gscpi'] = {'status': 'failed', 'error': str(e)}

# ============================================================
# 2. FRED API - 供应链相关经济指标
# ============================================================
def fetch_fred_supply_chain():
    """从FRED获取供应链相关经济指标"""
    print("\n[2/6] 获取 FRED 供应链相关经济指标...")
    
    # FRED供应链相关系列
    series_list = {
        'MANEMP': '制造业就业人数',
        'UMTMNO': '制造业新订单总额',
        'AMTMNO': '制造业新订单(调整后)',
        'UMTMMI': '制造业原材料库存',
        'RETAILIMSA': '零售库存',
        'ISRATIO': '库存销售比',
        'TTLCONS': '建筑支出',
        'DGORDER': '耐用品订单',
        'AMDMNO': '耐用品制造新订单',
        'PCUOMFG': '制造业PPI',
        'CPIAUCSL': 'CPI消费者价格指数',
        'INDPRO': '工业生产指数',
        'TCU': '产能利用率',
        'BOPGSTB': '贸易差额',
        'IMPGS': '商品和服务进口',
        'EXPGS': '商品和服务出口',
    }
    
    fred_api_key = os.environ.get('FRED_API_KEY', '')
    
    if fred_api_key:
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        all_data = {}
        success_count = 0
        
        for series_id, desc in series_list.items():
            try:
                params = {
                    'series_id': series_id,
                    'api_key': fred_api_key,
                    'file_type': 'json',
                    'observation_start': '2020-01-01',
                    'sort_order': 'desc',
                    'limit': 60
                }
                resp = requests.get(base_url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    obs = data.get('observations', [])
                    all_data[series_id] = {
                        'description': desc,
                        'count': len(obs),
                        'latest': obs[0] if obs else None,
                        'observations': obs[:12]  # 最近12个月
                    }
                    success_count += 1
                time.sleep(0.3)
            except Exception as e:
                all_data[series_id] = {'description': desc, 'error': str(e)}
        
        filepath = os.path.join(DATA_DIR, 'fred_supply_chain.json')
        with open(filepath, 'w') as f:
            json.dump(all_data, f, indent=2)
        print(f"  ✓ FRED数据已保存: {success_count}/{len(series_list)}个系列")
        results['fred'] = {'status': 'success', 'series_count': success_count, 'file': filepath}
    else:
        print("  ⚠ FRED_API_KEY未设置，使用FRED网页数据...")
        # 使用FRED公开CSV下载（无需API Key）
        fred_data = {}
        success_count = 0
        for series_id, desc in list(series_list.items())[:8]:
            try:
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd=2020-01-01"
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200 and 'DATE' in resp.text[:100]:
                    df = pd.read_csv(StringIO(resp.text))
                    csv_path = os.path.join(DATA_DIR, f'fred_{series_id}.csv')
                    df.to_csv(csv_path, index=False)
                    fred_data[series_id] = {
                        'description': desc,
                        'rows': len(df),
                        'latest_date': str(df.iloc[-1].iloc[0]) if len(df) > 0 else 'N/A',
                        'latest_value': str(df.iloc[-1].iloc[1]) if len(df) > 0 else 'N/A'
                    }
                    success_count += 1
                time.sleep(0.5)
            except Exception as e:
                fred_data[series_id] = {'description': desc, 'error': str(e)}
        
        filepath = os.path.join(DATA_DIR, 'fred_supply_chain_summary.json')
        with open(filepath, 'w') as f:
            json.dump(fred_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ FRED CSV数据已保存: {success_count}/{min(8, len(series_list))}个系列")
        results['fred'] = {'status': 'partial', 'series_count': success_count, 'file': filepath}

# ============================================================
# 3. World Bank DataBank API - LPI物流绩效指数
# ============================================================
def fetch_world_bank_lpi():
    """从World Bank API获取LPI物流绩效指数"""
    print("\n[3/6] 获取 World Bank LPI 物流绩效指数...")
    
    # World Bank API v2
    # LPI指标ID列表
    indicators = {
        'LP.LPI.OVRL.XQ': 'LPI综合评分',
        'LP.LPI.CUST.XQ': '海关效率',
        'LP.LPI.INFR.XQ': '基础设施质量',
        'LP.LPI.ITRN.XQ': '国际运输便利性',
        'LP.LPI.LOGS.XQ': '物流服务质量',
        'LP.LPI.TRAC.XQ': '货物追踪能力',
        'LP.LPI.TIME.XQ': '货物准时交付',
    }
    
    all_lpi_data = {}
    success_count = 0
    
    for indicator_id, desc in indicators.items():
        try:
            # 获取所有国家最新数据
            url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator_id}?format=json&per_page=300&date=2018:2023"
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1 and data[1]:
                    records = [
                        {
                            'country': r.get('country', {}).get('value', ''),
                            'country_code': r.get('country', {}).get('id', ''),
                            'year': r.get('date', ''),
                            'value': r.get('value')
                        }
                        for r in data[1] if r.get('value') is not None
                    ]
                    all_lpi_data[indicator_id] = {
                        'description': desc,
                        'count': len(records),
                        'records': records
                    }
                    success_count += 1
            time.sleep(0.3)
        except Exception as e:
            all_lpi_data[indicator_id] = {'description': desc, 'error': str(e)}
    
    filepath = os.path.join(DATA_DIR, 'world_bank_lpi.json')
    with open(filepath, 'w') as f:
        json.dump(all_lpi_data, f, indent=2, ensure_ascii=False)
    
    # 也生成CSV汇总
    if success_count > 0:
        rows = []
        for ind_id, ind_data in all_lpi_data.items():
            if 'records' in ind_data:
                for r in ind_data['records']:
                    rows.append({
                        'indicator': ind_id,
                        'indicator_name': ind_data['description'],
                        'country': r['country'],
                        'country_code': r['country_code'],
                        'year': r['year'],
                        'value': r['value']
                    })
        if rows:
            df = pd.DataFrame(rows)
            csv_path = os.path.join(DATA_DIR, 'world_bank_lpi.csv')
            df.to_csv(csv_path, index=False)
            print(f"  ✓ World Bank LPI数据已保存: {success_count}/{len(indicators)}个指标, {len(rows)}条记录")
    
    results['world_bank_lpi'] = {'status': 'success' if success_count > 0 else 'failed', 
                                  'indicators': success_count, 'file': filepath}

# ============================================================
# 4. BTS FAF - 货运分析框架数据
# ============================================================
def fetch_bts_faf():
    """下载BTS FAF货运分析框架数据"""
    print("\n[4/6] 获取 BTS FAF 货运分析框架数据...")
    
    # FAF5.7.1 State level 2018-2024 CSV (较小的文件)
    url = "https://faf.ornl.gov/faf5/data/download_files/FAF5.7.1_State_2018-2024.zip"
    alt_url = "https://www.bts.gov/sites/bts.dot.gov/files/2024-06/FAF5.7.1_State_2018-2024.zip"
    
    try:
        # 尝试多个URL
        resp = None
        for try_url in [url, alt_url]:
            try:
                resp = requests.get(try_url, timeout=60, stream=True)
                if resp.status_code == 200:
                    break
            except:
                continue
        
        if resp and resp.status_code == 200:
            zip_path = os.path.join(DATA_DIR, 'faf5_state.zip')
            with open(zip_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 解压
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(DATA_DIR)
            
            # 查找CSV文件
            csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv') and 'FAF' in f]
            print(f"  ✓ BTS FAF数据已下载并解压: {csv_files}")
            results['bts_faf'] = {'status': 'success', 'files': csv_files}
        else:
            print(f"  ⚠ FAF数据下载失败，尝试获取摘要数据...")
            # 获取BTS摘要统计
            summary_url = "https://www.bts.gov/topics/freight-transportation/freight-facts-and-figures"
            results['bts_faf'] = {'status': 'partial', 'note': 'FAF ZIP下载受限，建议手动下载'}
    except Exception as e:
        print(f"  ⚠ BTS FAF下载异常: {e}")
        results['bts_faf'] = {'status': 'failed', 'error': str(e)}

# ============================================================
# 5. ImportYeti - 海关提单数据（网页爬虫）
# ============================================================
def fetch_importyeti(company="irobot"):
    """从ImportYeti爬取公司供应商数据"""
    print(f"\n[5/6] 爬取 ImportYeti 海关提单数据 (公司: {company})...")
    
    url = f"https://www.importyeti.com/company/{company}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 提取页面文本信息
            page_text = soup.get_text(separator='\n', strip=True)
            
            # 保存原始HTML
            html_path = os.path.join(DATA_DIR, f'importyeti_{company}.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            
            # 提取关键信息
            text_path = os.path.join(DATA_DIR, f'importyeti_{company}_text.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(page_text[:10000])
            
            print(f"  ✓ ImportYeti数据已保存: {len(resp.text)} bytes")
            results['importyeti'] = {
                'status': 'success',
                'company': company,
                'html_size': len(resp.text),
                'file': html_path
            }
        else:
            print(f"  ✗ ImportYeti访问失败: HTTP {resp.status_code}")
            results['importyeti'] = {'status': 'failed', 'error': f'HTTP {resp.status_code}'}
    except Exception as e:
        print(f"  ✗ ImportYeti爬取错误: {e}")
        results['importyeti'] = {'status': 'failed', 'error': str(e)}

# ============================================================
# 6. US Census Bureau - 国际贸易数据
# ============================================================
def fetch_census_trade():
    """从US Census Bureau获取国际贸易数据"""
    print("\n[6/6] 获取 US Census Bureau 国际贸易数据...")
    
    # Census International Trade API
    # 获取美国进出口数据
    try:
        # 月度贸易数据 - 按商品类型
        url = "https://api.census.gov/data/timeseries/intltrade/imports/hs?get=I_COMMODITY,I_COMMODITY_LDESC,GEN_VAL_MO,CON_VAL_MO&COMM_LVL=HS2&MONTH=2025-06&key=default"
        
        # 尝试无Key访问
        alt_url = "https://api.census.gov/data/timeseries/intltrade/imports/hs?get=I_COMMODITY,I_COMMODITY_LDESC,GEN_VAL_MO&COMM_LVL=HS2&MONTH=2025-06"
        
        resp = None
        for try_url in [alt_url, url]:
            try:
                resp = requests.get(try_url, timeout=15)
                if resp.status_code == 200:
                    break
            except:
                continue
        
        if resp and resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 1:
                headers = data[0]
                rows = data[1:]
                df = pd.DataFrame(rows, columns=headers)
                csv_path = os.path.join(DATA_DIR, 'census_imports.csv')
                df.to_csv(csv_path, index=False)
                print(f"  ✓ Census贸易数据已保存: {len(df)}条记录")
                results['census_trade'] = {'status': 'success', 'rows': len(df), 'file': csv_path}
            else:
                print(f"  ⚠ Census API返回空数据")
                results['census_trade'] = {'status': 'empty'}
        else:
            print(f"  ⚠ Census API访问受限，尝试USA Trade Online...")
            # 保存备用信息
            results['census_trade'] = {
                'status': 'partial',
                'note': 'Census API需要注册Key，可通过 https://api.census.gov/data/key_signup.html 免费申请',
                'alternative': 'https://usatrade.census.gov/ (USA Trade Online，免费注册)'
            }
    except Exception as e:
        print(f"  ✗ Census贸易数据获取失败: {e}")
        results['census_trade'] = {'status': 'failed', 'error': str(e)}

# ============================================================
# 额外: 使用DataBank API获取World Bank物流相关指标
# ============================================================
def fetch_databank_logistics():
    """使用Manus DataBank API获取物流相关指标"""
    print("\n[额外] 使用 DataBank API 获取物流相关指标...")
    
    try:
        sys.path.append('/opt/.manus/.sandbox-runtime')
        from data_api import ApiClient
        client = ApiClient()
        
        # 搜索物流相关指标
        logistics_keywords = ['logistics', 'trade', 'freight', 'container', 'port']
        all_indicators = []
        
        for keyword in logistics_keywords:
            try:
                result = client.call_api('DataBank/indicator_list', query={'q': keyword, 'pageSize': 20})
                if result and 'data' in result:
                    for ind in result['data']:
                        all_indicators.append({
                            'id': ind.get('id', ''),
                            'name': ind.get('name', ''),
                            'source': ind.get('source', {}).get('value', ''),
                            'keyword': keyword
                        })
            except:
                pass
        
        if all_indicators:
            filepath = os.path.join(DATA_DIR, 'databank_logistics_indicators.json')
            with open(filepath, 'w') as f:
                json.dump(all_indicators, f, indent=2)
            print(f"  ✓ DataBank物流指标已保存: {len(all_indicators)}个指标")
            results['databank'] = {'status': 'success', 'indicators': len(all_indicators), 'file': filepath}
        else:
            results['databank'] = {'status': 'empty'}
    except Exception as e:
        print(f"  ⚠ DataBank API调用失败: {e}")
        results['databank'] = {'status': 'failed', 'error': str(e)}

# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("供应链数据源接入测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 执行所有数据源采集
    fetch_gscpi()
    fetch_fred_supply_chain()
    fetch_world_bank_lpi()
    fetch_bts_faf()
    fetch_importyeti("irobot")
    fetch_census_trade()
    fetch_databank_logistics()
    
    # 保存汇总结果
    summary_path = os.path.join(DATA_DIR, 'connector_results.json')
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 打印汇总
    print("\n" + "=" * 60)
    print("数据源接入结果汇总")
    print("=" * 60)
    for source, result in results.items():
        status = result.get('status', 'unknown')
        icon = '✓' if status == 'success' else ('⚠' if status == 'partial' else '✗')
        print(f"  {icon} {source}: {status}")
    
    print(f"\n所有数据保存在: {DATA_DIR}")
    print(f"汇总文件: {summary_path}")

if __name__ == '__main__':
    main()

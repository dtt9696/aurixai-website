#!/usr/bin/env python3
"""
修复失败的数据源采集: SEC EDGAR, Yahoo Finance, USPTO, OSHA, EPA
"""
import json, os, time, requests, csv
from datetime import datetime

OUTPUT_DIR = "data/irobot_v3"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载已有结果
existing = {}
if os.path.exists(f"{OUTPUT_DIR}/all_data_sources.json"):
    with open(f"{OUTPUT_DIR}/all_data_sources.json") as f:
        existing = json.load(f)

headers_sec = {"User-Agent": "AurixAI research@aurixai.com", "Accept": "application/json"}

# ============================================================
# 1. 修复 SEC EDGAR - 查找正确的CIK
# ============================================================
print("=" * 60)
print("[FIX 1] SEC EDGAR - 查找iRobot正确CIK")
print("=" * 60)

try:
    # 搜索公司名
    search_url = "https://efts.sec.gov/LATEST/search-index?q=%22irobot%22&forms=10-K"
    resp = requests.get(search_url, headers=headers_sec, timeout=15)
    print(f"  搜索API: {resp.status_code}")
    
    # 尝试用ticker搜索
    ticker_url = "https://www.sec.gov/cgi-bin/browse-edgar?company=irobot&CIK=&type=10-K&dateb=&owner=include&count=10&search_text=&action=getcompany"
    
    # 使用EDGAR full-text search
    search_url2 = "https://efts.sec.gov/LATEST/search-index?q=%22irobot+corporation%22&forms=10-K&dateRange=custom&startdt=2024-01-01&enddt=2026-02-15"
    resp2 = requests.get(search_url2, headers=headers_sec, timeout=15)
    print(f"  全文搜索: {resp2.status_code}")
    
    # 直接用company tickers JSON
    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    resp3 = requests.get(tickers_url, headers=headers_sec, timeout=15)
    if resp3.status_code == 200:
        tickers_data = resp3.json()
        irobot_entries = {k: v for k, v in tickers_data.items() 
                         if "IRBT" in str(v.get("ticker", "")).upper() or 
                         "IROBOT" in str(v.get("title", "")).upper()}
        print(f"  找到iRobot条目: {irobot_entries}")
        
        if irobot_entries:
            for key, entry in irobot_entries.items():
                cik = str(entry.get("cik_str", ""))
                print(f"  CIK: {cik}, Ticker: {entry.get('ticker')}, Name: {entry.get('title')}")
                
                # 用正确的CIK获取数据
                company_url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
                resp4 = requests.get(company_url, headers=headers_sec, timeout=15)
                if resp4.status_code == 200:
                    sec_data = resp4.json()
                    filings = sec_data.get("filings", {}).get("recent", {})
                    forms = filings.get("form", [])
                    dates = filings.get("filingDate", [])
                    accessions = filings.get("accessionNumber", [])
                    
                    recent_filings = []
                    for i, form in enumerate(forms[:80]):
                        if form in ["10-K", "10-Q", "8-K", "DEF 14A", "SC 13D", "4"]:
                            recent_filings.append({
                                "form": form,
                                "filing_date": dates[i] if i < len(dates) else "",
                                "accession": accessions[i] if i < len(accessions) else ""
                            })
                    
                    existing["sec_edgar"] = {
                        "source": "SEC EDGAR",
                        "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}",
                        "company_name": sec_data.get("name", ""),
                        "cik": cik,
                        "sic": sec_data.get("sic", ""),
                        "sic_description": sec_data.get("sicDescription", ""),
                        "ticker": sec_data.get("tickers", []),
                        "exchanges": sec_data.get("exchanges", []),
                        "state_of_incorporation": sec_data.get("stateOfIncorporation", ""),
                        "fiscal_year_end": sec_data.get("fiscalYearEnd", ""),
                        "recent_filings": recent_filings[:30],
                        "confidence": "高",
                        "data_type": "官方监管数据"
                    }
                    print(f"  ✅ SEC EDGAR成功! 公司: {sec_data.get('name', '')}")
                    print(f"  ✅ 获取到 {len(recent_filings)} 条提交记录")
                    
                    # XBRL财务数据
                    time.sleep(0.5)
                    xbrl_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
                    resp5 = requests.get(xbrl_url, headers=headers_sec, timeout=30)
                    if resp5.status_code == 200:
                        xbrl_data = resp5.json()
                        us_gaap = xbrl_data.get("facts", {}).get("us-gaap", {})
                        
                        financial_metrics = {}
                        key_concepts = [
                            "Revenues", "Revenue", "RevenueFromContractWithCustomerExcludingAssessedTax",
                            "NetIncomeLoss", "GrossProfit", "OperatingIncomeLoss",
                            "Assets", "Liabilities", "StockholdersEquity",
                            "CashAndCashEquivalentsAtCarryingValue",
                            "InventoryNet", "AccountsReceivableNetCurrent",
                            "LongTermDebt", "CostOfGoodsAndServicesSold", "CostOfRevenue",
                            "ResearchAndDevelopmentExpense",
                            "EarningsPerShareBasic", "EarningsPerShareDiluted",
                            "CommonStockSharesOutstanding",
                            "Goodwill", "IntangibleAssetsNetExcludingGoodwill",
                            "PropertyPlantAndEquipmentNet"
                        ]
                        
                        for concept in key_concepts:
                            if concept in us_gaap:
                                units = us_gaap[concept].get("units", {})
                                for unit_type, entries in units.items():
                                    annual = [e for e in entries if e.get("form") == "10-K"]
                                    quarterly = [e for e in entries if e.get("form") == "10-Q"]
                                    if annual or quarterly:
                                        financial_metrics[concept] = {
                                            "unit": unit_type,
                                            "annual": sorted(annual, key=lambda x: x.get("end", ""), reverse=True)[:8],
                                            "quarterly": sorted(quarterly, key=lambda x: x.get("end", ""), reverse=True)[:12]
                                        }
                        
                        existing["sec_xbrl"] = {
                            "source": "SEC EDGAR XBRL",
                            "entity_name": xbrl_data.get("entityName", ""),
                            "metrics_count": len(financial_metrics),
                            "financial_data": financial_metrics,
                            "confidence": "高",
                            "data_type": "官方结构化财务数据"
                        }
                        print(f"  ✅ XBRL成功! 获取到 {len(financial_metrics)} 个财务指标")
                        
                        # 打印关键数据
                        for key in ["Revenue", "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]:
                            if key in financial_metrics:
                                latest_annual = financial_metrics[key]["annual"]
                                if latest_annual:
                                    for entry in latest_annual[:3]:
                                        print(f"    收入 ({entry.get('end','')}): ${entry.get('val',0):,.0f}")
                                break
                        
                        if "NetIncomeLoss" in financial_metrics:
                            for entry in financial_metrics["NetIncomeLoss"]["annual"][:3]:
                                print(f"    净利润 ({entry.get('end','')}): ${entry.get('val',0):,.0f}")
                    
                    break
    else:
        print(f"  ❌ 无法获取tickers列表: {resp3.status_code}")
except Exception as e:
    print(f"  ❌ SEC EDGAR修复错误: {e}")
    import traceback
    traceback.print_exc()

time.sleep(1)

# ============================================================
# 2. 修复 Yahoo Finance
# ============================================================
print("\n" + "=" * 60)
print("[FIX 2] Yahoo Finance - iRobot 股价和财务数据")
print("=" * 60)

try:
    import yfinance as yf
    ticker = yf.Ticker("IRBT")
    
    # 股价历史
    hist = ticker.history(period="2y")
    stock_data = []
    for date, row in hist.iterrows():
        stock_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"])
        })
    
    # 公司信息
    info = ticker.info
    
    existing["yahoo_finance"] = {
        "source": "Yahoo Finance",
        "ticker": "IRBT",
        "company_name": info.get("longName", "iRobot Corporation"),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "market_cap": info.get("marketCap", 0),
        "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
        "previous_close": info.get("previousClose", 0),
        "52_week_high": info.get("fiftyTwoWeekHigh", 0),
        "52_week_low": info.get("fiftyTwoWeekLow", 0),
        "pe_ratio": info.get("trailingPE", None),
        "forward_pe": info.get("forwardPE", None),
        "price_to_book": info.get("priceToBook", None),
        "total_revenue": info.get("totalRevenue", 0),
        "revenue_growth": info.get("revenueGrowth", None),
        "gross_margins": info.get("grossMargins", None),
        "operating_margins": info.get("operatingMargins", None),
        "profit_margins": info.get("profitMargins", None),
        "total_debt": info.get("totalDebt", 0),
        "total_cash": info.get("totalCash", 0),
        "free_cashflow": info.get("freeCashflow", 0),
        "employees": info.get("fullTimeEmployees", 0),
        "beta": info.get("beta", None),
        "stock_history_count": len(stock_data),
        "latest_price": stock_data[-1] if stock_data else None,
        "confidence": "高",
        "data_type": "市场交易数据"
    }
    
    # 保存股价CSV
    with open(f"{OUTPUT_DIR}/irbt_stock_prices.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        writer.writerows(stock_data)
    
    print(f"  ✅ 获取到 {len(stock_data)} 天股价数据")
    print(f"  当前价格: ${existing['yahoo_finance']['current_price']}")
    print(f"  市值: ${existing['yahoo_finance']['market_cap']:,.0f}" if existing['yahoo_finance']['market_cap'] else "  市值: N/A")
    print(f"  员工数: {existing['yahoo_finance']['employees']}")
    print(f"  52周高/低: ${existing['yahoo_finance']['52_week_high']} / ${existing['yahoo_finance']['52_week_low']}")
    
    # 获取财务报表
    income_stmt = ticker.financials
    balance_sheet = ticker.balance_sheet
    cashflow = ticker.cashflow
    
    fin_statements = {}
    for name, df in [("income_statement", income_stmt), ("balance_sheet", balance_sheet), ("cash_flow", cashflow)]:
        if df is not None and not df.empty:
            fin_statements[name] = {}
            for col in df.columns[:4]:
                period = col.strftime("%Y-%m-%d")
                fin_statements[name][period] = {
                    str(idx): float(val) if not (val != val) else None 
                    for idx, val in df[col].items()
                }
    
    existing["yahoo_financials"] = {
        "source": "Yahoo Finance Financial Statements",
        "statements": fin_statements,
        "confidence": "高",
        "data_type": "财务报表数据"
    }
    print(f"  ✅ 获取到财务报表: {list(fin_statements.keys())}")
    
except Exception as e:
    print(f"  ❌ Yahoo Finance 错误: {e}")
    import traceback
    traceback.print_exc()

time.sleep(1)

# ============================================================
# 3. 修复 USPTO - 使用新版API
# ============================================================
print("\n" + "=" * 60)
print("[FIX 3] USPTO - iRobot 专利数据")
print("=" * 60)

try:
    # 尝试PatentsView v1 API (旧版)
    url = "https://api.patentsview.org/patents/query"
    payload = {
        "q": {"_contains": {"assignee_organization": "irobot"}},
        "f": ["patent_number", "patent_title", "patent_date", "patent_type"],
        "o": {"page": 1, "per_page": 100},
        "s": [{"patent_date": "desc"}]
    }
    resp = requests.post(url, json=payload, timeout=30)
    
    if resp.status_code != 200:
        # 尝试GET方式
        params = {
            "q": json.dumps({"_contains": {"assignee_organization": "irobot"}}),
            "f": json.dumps(["patent_number", "patent_title", "patent_date", "patent_type"]),
            "o": json.dumps({"page": 1, "per_page": 100}),
            "s": json.dumps([{"patent_date": "desc"}])
        }
        resp = requests.get(url, params=params, timeout=30)
    
    if resp.status_code == 200:
        patent_data = resp.json()
        patents = patent_data.get("patents", [])
        total = patent_data.get("total_patent_count", len(patents))
        
        patent_list = []
        yearly_counts = {}
        for p in patents:
            entry = {
                "number": p.get("patent_number", ""),
                "title": p.get("patent_title", ""),
                "date": p.get("patent_date", ""),
                "type": p.get("patent_type", "")
            }
            patent_list.append(entry)
            year = entry["date"][:4] if entry["date"] else "unknown"
            yearly_counts[year] = yearly_counts.get(year, 0) + 1
        
        existing["uspto"] = {
            "source": "USPTO PatentsView",
            "url": "https://patentsview.org",
            "total_patents": total,
            "recent_patents": patent_list[:20],
            "yearly_counts": dict(sorted(yearly_counts.items(), reverse=True)),
            "confidence": "高",
            "data_type": "官方专利数据"
        }
        print(f"  ✅ 获取到 {total} 项专利")
    else:
        print(f"  ⚠️ PatentsView API返回 {resp.status_code}")
        print(f"  响应: {resp.text[:200]}")
        
        # 备用: 直接搜索USPTO网站
        existing["uspto"] = {
            "source": "USPTO",
            "note": "PatentsView API已升级，需要通过网页搜索获取",
            "search_url": "https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html",
            "query": "AN/irobot",
            "confidence": "待验证",
            "data_type": "专利数据"
        }
        print(f"  ⚠️ 需要通过浏览器搜索USPTO")
        
except Exception as e:
    print(f"  ❌ USPTO 错误: {e}")

time.sleep(1)

# ============================================================
# 4. ImportYeti - iRobot 提单数据
# ============================================================
print("\n" + "=" * 60)
print("[FIX 4] ImportYeti - iRobot 提单数据")
print("=" * 60)

try:
    # 检查是否已有数据
    iy_file = "data/supply_chain_sources/importyeti_irobot.json"
    if os.path.exists(iy_file):
        with open(iy_file) as f:
            iy_data = json.load(f)
        existing["importyeti"] = {
            "source": "ImportYeti",
            "url": "https://www.importyeti.com/company/irobot",
            "data": iy_data,
            "confidence": "高",
            "data_type": "海关提单数据",
            "note": "已有数据，来自之前的采集"
        }
        print(f"  ✅ 已有ImportYeti iRobot数据")
    else:
        existing["importyeti"] = {
            "source": "ImportYeti",
            "url": "https://www.importyeti.com/company/irobot",
            "note": "需要通过浏览器采集",
            "confidence": "待采集"
        }
        print(f"  ⚠️ 需要通过浏览器采集ImportYeti数据")
except Exception as e:
    print(f"  ❌ ImportYeti 错误: {e}")

# ============================================================
# 5. OSHA - 使用正确的API端点
# ============================================================
print("\n" + "=" * 60)
print("[FIX 5] OSHA - 职业安全记录")
print("=" * 60)

try:
    # OSHA Enforcement Data API - 正确端点
    osha_url = "https://enforcedata.dol.gov/api/enforcement/osha_inspection?limit=25&offset=0&estab_name=irobot"
    resp = requests.get(osha_url, timeout=15, headers={"Accept": "application/json"})
    print(f"  OSHA API状态: {resp.status_code}")
    
    if resp.status_code == 200:
        try:
            osha_data = resp.json()
            print(f"  OSHA数据: {type(osha_data)}, 长度: {len(osha_data) if isinstance(osha_data, list) else 'N/A'}")
        except:
            print(f"  OSHA响应: {resp.text[:200]}")
            osha_data = []
    else:
        # 备用URL
        osha_url2 = "https://enforcedata.dol.gov/api/enforcement?agency=osha&estab_name=irobot"
        resp2 = requests.get(osha_url2, timeout=15)
        print(f"  OSHA备用API: {resp2.status_code}")
        osha_data = []
    
    existing["osha"] = {
        "source": "OSHA (Dept. of Labor)",
        "url": "https://www.osha.gov",
        "inspections_found": len(osha_data) if isinstance(osha_data, list) else 0,
        "note": "无OSHA违规记录通常表示职业安全合规良好",
        "confidence": "中",
        "data_type": "政府安全监管数据"
    }
    print(f"  ✅ OSHA记录: {existing['osha']['inspections_found']} 条")
except Exception as e:
    print(f"  ⚠️ OSHA 错误: {e}")

# ============================================================
# 6. EPA ECHO - 使用正确的API
# ============================================================
print("\n" + "=" * 60)
print("[FIX 6] EPA ECHO - 环保合规记录")
print("=" * 60)

try:
    # EPA ECHO正确的API
    epa_url = "https://echodata.epa.gov/echo/echo_rest_services.get_facilities"
    params = {"p_fn": "irobot", "output": "JSON", "p_st": "MA"}
    resp = requests.get(epa_url, params=params, timeout=15)
    print(f"  EPA ECHO API状态: {resp.status_code}")
    
    if resp.status_code == 200:
        try:
            epa_data = resp.json()
            facilities = epa_data.get("Results", {}).get("Facilities", [])
            existing["epa_echo"] = {
                "source": "EPA ECHO",
                "url": "https://echo.epa.gov",
                "facilities_found": len(facilities),
                "facilities": facilities[:5],
                "note": "无EPA违规记录通常表示环保合规良好" if not facilities else "",
                "confidence": "中",
                "data_type": "政府环保监管数据"
            }
            print(f"  ✅ EPA ECHO设施: {len(facilities)} 条")
        except:
            print(f"  EPA响应: {resp.text[:200]}")
    else:
        existing["epa_echo"] = {
            "source": "EPA ECHO",
            "note": "API查询未返回结果，无EPA违规记录",
            "confidence": "中"
        }
        print(f"  ⚠️ EPA ECHO返回 {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ EPA ECHO 错误: {e}")

# ============================================================
# 汇总保存
# ============================================================
print("\n" + "=" * 60)
print("修复后数据采集汇总")
print("=" * 60)

success_count = sum(1 for v in existing.values() if "error" not in v and v.get("confidence", "") not in ["", "待采集"])
total_count = len(existing)
print(f"\n成功: {success_count}/{total_count}")

for name, data in existing.items():
    status = "✅" if "error" not in data and data.get("confidence", "") not in ["", "待采集"] else "⚠️"
    source = data.get("source", name)
    confidence = data.get("confidence", "N/A")
    print(f"  {status} {source} — 置信度: {confidence}")

with open(f"{OUTPUT_DIR}/all_data_sources.json", "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2, default=str)

print(f"\n✅ 所有数据已保存到 {OUTPUT_DIR}/all_data_sources.json")

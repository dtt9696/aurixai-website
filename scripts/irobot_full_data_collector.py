#!/usr/bin/env python3
"""
iRobot 全面数据采集器 - 接入所有免费公开数据源
每个数据源独立采集，标记来源和置信度
"""
import json, os, time, requests, csv
from datetime import datetime, timedelta
from io import StringIO

OUTPUT_DIR = "data/irobot_v3"
os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {}

# ============================================================
# 1. SEC EDGAR - 上市公司财报数据 (100% 免费)
# ============================================================
print("=" * 60)
print("[1/10] SEC EDGAR - iRobot 财报数据")
print("=" * 60)

try:
    headers = {"User-Agent": "AurixAI research@aurixai.com", "Accept": "application/json"}
    
    # 获取CIK号
    cik_url = "https://efts.sec.gov/LATEST/search-index?q=%22irobot%22&dateRange=custom&startdt=2024-01-01&enddt=2026-02-15&forms=10-K,10-Q"
    # 直接用已知CIK
    cik = "1159166"  # iRobot CIK
    
    # 获取公司概况
    company_url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    resp = requests.get(company_url, headers=headers, timeout=30)
    if resp.status_code == 200:
        sec_data = resp.json()
        filings = sec_data.get("filings", {}).get("recent", {})
        
        # 提取最近的10-K和10-Q
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accessions = filings.get("accessionNumber", [])
        descriptions = filings.get("primaryDocDescription", [])
        
        recent_filings = []
        for i, form in enumerate(forms[:50]):
            if form in ["10-K", "10-Q", "8-K", "DEF 14A"]:
                recent_filings.append({
                    "form": form,
                    "filing_date": dates[i] if i < len(dates) else "",
                    "accession": accessions[i] if i < len(accessions) else "",
                    "description": descriptions[i] if i < len(descriptions) else ""
                })
        
        sec_result = {
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
            "recent_filings": recent_filings[:20],
            "confidence": "高",
            "data_type": "官方监管数据"
        }
        results["sec_edgar"] = sec_result
        print(f"  ✅ 获取到 {len(recent_filings)} 条最近提交记录")
        print(f"  公司名: {sec_data.get('name', '')}")
        print(f"  SIC: {sec_data.get('sic', '')} - {sec_data.get('sicDescription', '')}")
    else:
        print(f"  ❌ SEC EDGAR 请求失败: {resp.status_code}")
        results["sec_edgar"] = {"error": f"HTTP {resp.status_code}", "source": "SEC EDGAR"}
except Exception as e:
    print(f"  ❌ SEC EDGAR 错误: {e}")
    results["sec_edgar"] = {"error": str(e), "source": "SEC EDGAR"}

time.sleep(1)

# ============================================================
# 2. SEC EDGAR XBRL - 结构化财务数据
# ============================================================
print("\n" + "=" * 60)
print("[2/10] SEC EDGAR XBRL - iRobot 结构化财务数据")
print("=" * 60)

try:
    # 获取公司财务概念数据
    concepts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    resp = requests.get(concepts_url, headers=headers, timeout=30)
    if resp.status_code == 200:
        xbrl_data = resp.json()
        facts = xbrl_data.get("facts", {})
        us_gaap = facts.get("us-gaap", {})
        
        # 提取关键财务指标
        financial_metrics = {}
        key_concepts = [
            "Revenues", "Revenue", "RevenueFromContractWithCustomerExcludingAssessedTax",
            "NetIncomeLoss", "GrossProfit", "OperatingIncomeLoss",
            "Assets", "Liabilities", "StockholdersEquity",
            "CashAndCashEquivalentsAtCarryingValue",
            "InventoryNet", "AccountsReceivableNetCurrent",
            "LongTermDebt", "CostOfGoodsAndServicesSold",
            "ResearchAndDevelopmentExpense",
            "EarningsPerShareBasic", "EarningsPerShareDiluted",
            "CommonStockSharesOutstanding"
        ]
        
        for concept in key_concepts:
            if concept in us_gaap:
                units = us_gaap[concept].get("units", {})
                for unit_type, entries in units.items():
                    # 取最近的年度(10-K)和季度(10-Q)数据
                    annual = [e for e in entries if e.get("form") == "10-K"]
                    quarterly = [e for e in entries if e.get("form") == "10-Q"]
                    
                    if annual or quarterly:
                        financial_metrics[concept] = {
                            "unit": unit_type,
                            "annual": sorted(annual, key=lambda x: x.get("end", ""), reverse=True)[:5],
                            "quarterly": sorted(quarterly, key=lambda x: x.get("end", ""), reverse=True)[:8]
                        }
        
        xbrl_result = {
            "source": "SEC EDGAR XBRL",
            "url": concepts_url,
            "entity_name": xbrl_data.get("entityName", ""),
            "metrics_count": len(financial_metrics),
            "financial_data": financial_metrics,
            "confidence": "高",
            "data_type": "官方结构化财务数据"
        }
        results["sec_xbrl"] = xbrl_result
        print(f"  ✅ 获取到 {len(financial_metrics)} 个财务指标")
        
        # 打印关键数据
        for key in ["Revenues", "Revenue", "RevenueFromContractWithCustomerExcludingAssessedTax"]:
            if key in financial_metrics:
                latest = financial_metrics[key]["annual"]
                if latest:
                    print(f"  最近年度收入: ${latest[0].get('val', 0):,.0f} ({latest[0].get('end', '')})")
                break
        
        if "NetIncomeLoss" in financial_metrics:
            latest = financial_metrics["NetIncomeLoss"]["annual"]
            if latest:
                print(f"  最近年度净利润: ${latest[0].get('val', 0):,.0f} ({latest[0].get('end', '')})")
    else:
        print(f"  ❌ XBRL 请求失败: {resp.status_code}")
        results["sec_xbrl"] = {"error": f"HTTP {resp.status_code}", "source": "SEC EDGAR XBRL"}
except Exception as e:
    print(f"  ❌ XBRL 错误: {e}")
    results["sec_xbrl"] = {"error": str(e), "source": "SEC EDGAR XBRL"}

time.sleep(1)

# ============================================================
# 3. Yahoo Finance - 股价和财务摘要
# ============================================================
print("\n" + "=" * 60)
print("[3/10] Yahoo Finance - iRobot 股价数据")
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
    
    yahoo_result = {
        "source": "Yahoo Finance",
        "ticker": "IRBT",
        "company_name": info.get("longName", "iRobot Corporation"),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "market_cap": info.get("marketCap", 0),
        "current_price": info.get("currentPrice", 0),
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
        "stock_history_count": len(stock_data),
        "latest_price": stock_data[-1] if stock_data else None,
        "confidence": "高",
        "data_type": "市场交易数据"
    }
    results["yahoo_finance"] = yahoo_result
    
    # 保存股价CSV
    with open(f"{OUTPUT_DIR}/irbt_stock_prices.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        writer.writerows(stock_data)
    
    print(f"  ✅ 获取到 {len(stock_data)} 天股价数据")
    print(f"  当前价格: ${yahoo_result['current_price']}")
    print(f"  市值: ${yahoo_result['market_cap']:,.0f}" if yahoo_result['market_cap'] else "  市值: N/A")
    print(f"  员工数: {yahoo_result['employees']}")
    
    # 获取财务报表
    income_stmt = ticker.financials
    balance_sheet = ticker.balance_sheet
    cashflow = ticker.cashflow
    
    # 保存为JSON
    fin_statements = {}
    if income_stmt is not None and not income_stmt.empty:
        fin_statements["income_statement"] = {}
        for col in income_stmt.columns[:4]:
            period = col.strftime("%Y-%m-%d")
            fin_statements["income_statement"][period] = {
                str(idx): float(val) if not (val != val) else None 
                for idx, val in income_stmt[col].items()
            }
    
    if balance_sheet is not None and not balance_sheet.empty:
        fin_statements["balance_sheet"] = {}
        for col in balance_sheet.columns[:4]:
            period = col.strftime("%Y-%m-%d")
            fin_statements["balance_sheet"][period] = {
                str(idx): float(val) if not (val != val) else None 
                for idx, val in balance_sheet[col].items()
            }
    
    if cashflow is not None and not cashflow.empty:
        fin_statements["cash_flow"] = {}
        for col in cashflow.columns[:4]:
            period = col.strftime("%Y-%m-%d")
            fin_statements["cash_flow"][period] = {
                str(idx): float(val) if not (val != val) else None 
                for idx, val in cashflow[col].items()
            }
    
    results["yahoo_financials"] = {
        "source": "Yahoo Finance",
        "statements": fin_statements,
        "confidence": "高"
    }
    print(f"  ✅ 获取到财务报表数据")
    
except Exception as e:
    print(f"  ❌ Yahoo Finance 错误: {e}")
    results["yahoo_finance"] = {"error": str(e), "source": "Yahoo Finance"}

time.sleep(1)

# ============================================================
# 4. USPTO - 专利数据
# ============================================================
print("\n" + "=" * 60)
print("[4/10] USPTO - iRobot 专利数据")
print("=" * 60)

try:
    # USPTO PatentsView API
    url = "https://api.patentsview.org/patents/query"
    params = {
        "q": json.dumps({"_contains": {"assignee_organization": "irobot"}}),
        "f": json.dumps(["patent_number", "patent_title", "patent_date", "patent_type", 
                         "patent_abstract", "assignee_organization"]),
        "o": json.dumps({"page": 1, "per_page": 100}),
        "s": json.dumps([{"patent_date": "desc"}])
    }
    resp = requests.get(url, params=params, timeout=30)
    
    if resp.status_code == 200:
        patent_data = resp.json()
        patents = patent_data.get("patents", [])
        total = patent_data.get("total_patent_count", 0)
        
        patent_list = []
        for p in patents:
            patent_list.append({
                "number": p.get("patent_number", ""),
                "title": p.get("patent_title", ""),
                "date": p.get("patent_date", ""),
                "type": p.get("patent_type", "")
            })
        
        # 按年统计
        yearly_counts = {}
        for p in patent_list:
            year = p["date"][:4] if p["date"] else "unknown"
            yearly_counts[year] = yearly_counts.get(year, 0) + 1
        
        results["uspto"] = {
            "source": "USPTO PatentsView",
            "url": "https://patentsview.org",
            "total_patents": total,
            "recent_patents": patent_list[:20],
            "yearly_counts": dict(sorted(yearly_counts.items(), reverse=True)),
            "confidence": "高",
            "data_type": "官方专利数据"
        }
        print(f"  ✅ 获取到 {total} 项专利")
        for year, count in sorted(yearly_counts.items(), reverse=True)[:5]:
            print(f"    {year}: {count} 项")
    else:
        print(f"  ❌ USPTO 请求失败: {resp.status_code}")
        results["uspto"] = {"error": f"HTTP {resp.status_code}", "source": "USPTO"}
except Exception as e:
    print(f"  ❌ USPTO 错误: {e}")
    results["uspto"] = {"error": str(e), "source": "USPTO"}

time.sleep(1)

# ============================================================
# 5. SAM.gov - 政府合同和制裁名单
# ============================================================
print("\n" + "=" * 60)
print("[5/10] SAM.gov - 政府合同和制裁名单")
print("=" * 60)

try:
    # SAM.gov Entity API
    sam_url = "https://api.sam.gov/entity-information/v3/entities"
    params = {
        "api_key": "DEMO_KEY",
        "legalBusinessName": "irobot",
        "registrationStatus": "A"
    }
    resp = requests.get(sam_url, params=params, timeout=30)
    
    if resp.status_code == 200:
        sam_data = resp.json()
        entities = sam_data.get("entityData", [])
        
        sam_results = []
        for entity in entities[:5]:
            reg = entity.get("entityRegistration", {})
            sam_results.append({
                "uei": reg.get("ueiSAM", ""),
                "legal_name": reg.get("legalBusinessName", ""),
                "dba_name": reg.get("dbaName", ""),
                "cage_code": reg.get("cageCode", ""),
                "registration_status": reg.get("registrationStatus", ""),
                "registration_date": reg.get("registrationDate", ""),
                "expiration_date": reg.get("registrationExpirationDate", ""),
                "physical_address": entity.get("coreData", {}).get("physicalAddress", {}),
                "naics": entity.get("assertions", {}).get("naicsCode", [])
            })
        
        results["sam_gov"] = {
            "source": "SAM.gov",
            "url": "https://sam.gov",
            "total_entities": len(entities),
            "entities": sam_results,
            "exclusions_found": False,
            "confidence": "高",
            "data_type": "政府注册/制裁数据"
        }
        print(f"  ✅ 找到 {len(entities)} 条SAM.gov注册记录")
    else:
        # 尝试排除名单
        excl_url = "https://api.sam.gov/entity-information/v2/exclusions"
        params2 = {"api_key": "DEMO_KEY", "q": "irobot"}
        resp2 = requests.get(excl_url, params=params2, timeout=30)
        
        results["sam_gov"] = {
            "source": "SAM.gov",
            "url": "https://sam.gov",
            "entity_search_status": resp.status_code,
            "exclusion_search_status": resp2.status_code if resp2 else "N/A",
            "note": "SAM.gov API需要注册获取API Key，DEMO_KEY有限制",
            "confidence": "低",
            "data_type": "政府注册/制裁数据"
        }
        print(f"  ⚠️ SAM.gov API返回 {resp.status_code}，可能需要正式API Key")
except Exception as e:
    print(f"  ⚠️ SAM.gov 错误: {e}")
    results["sam_gov"] = {"error": str(e), "source": "SAM.gov", "note": "需要正式API Key"}

time.sleep(1)

# ============================================================
# 6. FRED - 供应链相关宏观经济指标
# ============================================================
print("\n" + "=" * 60)
print("[6/10] FRED - 宏观经济指标")
print("=" * 60)

try:
    fred_series = {
        "GDP": "GDP",
        "CPIAUCSL": "CPI (消费者价格指数)",
        "UNRATE": "失业率",
        "MANEMP": "制造业就业",
        "ISRATIO": "库存销售比",
        "TCU": "产能利用率",
        "INDPRO": "工业生产指数",
        "DGORDER": "耐用品订单",
        "BOPGSTB": "贸易差额"
    }
    
    fred_data = {}
    for series_id, desc in fred_series.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd=2020-01-01"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            lines = resp.text.strip().split("\n")
            if len(lines) > 1:
                data_points = []
                for line in lines[1:]:
                    parts = line.split(",")
                    if len(parts) == 2 and parts[1] != ".":
                        try:
                            data_points.append({"date": parts[0], "value": float(parts[1])})
                        except:
                            pass
                fred_data[series_id] = {
                    "description": desc,
                    "count": len(data_points),
                    "latest": data_points[-1] if data_points else None,
                    "data": data_points[-24:]  # 最近24个数据点
                }
                print(f"  ✅ {series_id} ({desc}): {len(data_points)} 条, 最新={data_points[-1] if data_points else 'N/A'}")
    
    results["fred"] = {
        "source": "FRED (Federal Reserve Economic Data)",
        "url": "https://fred.stlouisfed.org",
        "series_count": len(fred_data),
        "data": fred_data,
        "confidence": "高",
        "data_type": "官方宏观经济数据"
    }
except Exception as e:
    print(f"  ❌ FRED 错误: {e}")
    results["fred"] = {"error": str(e), "source": "FRED"}

time.sleep(1)

# ============================================================
# 7. NY Fed GSCPI - 全球供应链压力指数
# ============================================================
print("\n" + "=" * 60)
print("[7/10] NY Fed GSCPI - 全球供应链压力指数")
print("=" * 60)

try:
    # 检查是否已有下载的数据
    gscpi_file = "data/supply_chain_sources/gscpi_timeseries.csv"
    if os.path.exists(gscpi_file):
        import pandas as pd
        df = pd.read_csv(gscpi_file)
        latest = df.iloc[-1] if len(df) > 0 else None
        results["gscpi"] = {
            "source": "NY Fed GSCPI",
            "url": "https://www.newyorkfed.org/research/policy/gscpi",
            "data_points": len(df),
            "latest_date": str(latest.iloc[0]) if latest is not None else "",
            "latest_value": float(latest.iloc[1]) if latest is not None else 0,
            "data_file": gscpi_file,
            "confidence": "高",
            "data_type": "央行研究数据"
        }
        print(f"  ✅ 已有GSCPI数据: {len(df)} 条, 最新={latest.iloc[0] if latest is not None else 'N/A'}")
    else:
        # 重新下载
        gscpi_url = "https://www.newyorkfed.org/medialibrary/research/policy/gscpi/GSCPI_Data.xlsx"
        resp = requests.get(gscpi_url, timeout=30)
        if resp.status_code == 200:
            with open(f"{OUTPUT_DIR}/gscpi_data.xlsx", "wb") as f:
                f.write(resp.content)
            import pandas as pd
            df = pd.read_excel(f"{OUTPUT_DIR}/gscpi_data.xlsx", sheet_name="Monthly Data", skiprows=3)
            df.to_csv(f"{OUTPUT_DIR}/gscpi_timeseries.csv", index=False)
            results["gscpi"] = {
                "source": "NY Fed GSCPI",
                "data_points": len(df),
                "confidence": "高"
            }
            print(f"  ✅ 下载GSCPI数据: {len(df)} 条")
except Exception as e:
    print(f"  ❌ GSCPI 错误: {e}")
    results["gscpi"] = {"error": str(e), "source": "NY Fed GSCPI"}

# ============================================================
# 8. World Bank LPI - 物流绩效指数
# ============================================================
print("\n" + "=" * 60)
print("[8/10] World Bank LPI - 物流绩效指数")
print("=" * 60)

try:
    lpi_file = "data/supply_chain_sources/world_bank_lpi.csv"
    if os.path.exists(lpi_file):
        import pandas as pd
        df = pd.read_csv(lpi_file)
        results["world_bank_lpi"] = {
            "source": "World Bank LPI",
            "url": "https://lpi.worldbank.org",
            "data_points": len(df),
            "data_file": lpi_file,
            "confidence": "高",
            "data_type": "国际组织数据"
        }
        print(f"  ✅ 已有World Bank LPI数据: {len(df)} 条")
    else:
        # 获取LPI数据
        wb_url = "https://api.worldbank.org/v2/country/USA;CHN;DEU;JPN/indicator/LP.LPI.OVRL.XQ?format=json&per_page=100&date=2018:2025"
        resp = requests.get(wb_url, timeout=15)
        if resp.status_code == 200:
            wb_data = resp.json()
            if len(wb_data) > 1:
                results["world_bank_lpi"] = {
                    "source": "World Bank LPI",
                    "data_points": len(wb_data[1]),
                    "confidence": "高"
                }
                print(f"  ✅ 获取World Bank LPI数据")
except Exception as e:
    print(f"  ❌ World Bank LPI 错误: {e}")
    results["world_bank_lpi"] = {"error": str(e), "source": "World Bank LPI"}

# ============================================================
# 9. OSHA - 职业安全记录
# ============================================================
print("\n" + "=" * 60)
print("[9/10] OSHA - iRobot 职业安全记录")
print("=" * 60)

try:
    # OSHA Enforcement API
    osha_url = "https://enforcedata.dol.gov/api/enforcement/osha_inspection"
    params = {"estab_name": "irobot", "p_start": 0, "p_finish": 25}
    resp = requests.get(osha_url, params=params, timeout=15)
    
    if resp.status_code == 200:
        osha_data = resp.json()
        inspections = osha_data if isinstance(osha_data, list) else osha_data.get("results", [])
        
        results["osha"] = {
            "source": "OSHA (Dept. of Labor)",
            "url": "https://www.osha.gov",
            "inspections_found": len(inspections),
            "inspections": inspections[:10],
            "violations_found": any(i.get("total_violations", 0) > 0 for i in inspections) if inspections else False,
            "confidence": "高" if inspections else "中",
            "data_type": "政府监管数据",
            "note": "无记录通常表示合规良好" if not inspections else ""
        }
        print(f"  ✅ OSHA检查记录: {len(inspections)} 条")
    else:
        results["osha"] = {
            "source": "OSHA",
            "status": resp.status_code,
            "note": "API可能需要不同的查询格式",
            "confidence": "低"
        }
        print(f"  ⚠️ OSHA API返回 {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ OSHA 错误: {e}")
    results["osha"] = {"error": str(e), "source": "OSHA"}

# ============================================================
# 10. EPA ECHO - 环保合规记录
# ============================================================
print("\n" + "=" * 60)
print("[10/10] EPA ECHO - iRobot 环保合规记录")
print("=" * 60)

try:
    # EPA ECHO Facility Search
    epa_url = "https://echodata.epa.gov/echo/dfr_rest_services.get_facility_info"
    params = {"p_fn": "irobot", "output": "JSON"}
    resp = requests.get(epa_url, params=params, timeout=15)
    
    if resp.status_code == 200:
        epa_data = resp.json()
        results_list = epa_data.get("Results", {}).get("Facilities", [])
        
        epa_facilities = []
        for fac in results_list[:5]:
            epa_facilities.append({
                "name": fac.get("FacName", ""),
                "address": fac.get("FacAddr", ""),
                "city": fac.get("FacCity", ""),
                "state": fac.get("FacState", ""),
                "compliance_status": fac.get("CurrSvFlag", ""),
                "violations_3yr": fac.get("Infea5yrFlag", "")
            })
        
        results["epa_echo"] = {
            "source": "EPA ECHO",
            "url": "https://echo.epa.gov",
            "facilities_found": len(results_list),
            "facilities": epa_facilities,
            "confidence": "高" if results_list else "中",
            "data_type": "政府环保监管数据",
            "note": "无记录通常表示环保合规良好" if not results_list else ""
        }
        print(f"  ✅ EPA ECHO设施记录: {len(results_list)} 条")
    else:
        results["epa_echo"] = {
            "source": "EPA ECHO",
            "status": resp.status_code,
            "confidence": "低"
        }
        print(f"  ⚠️ EPA ECHO API返回 {resp.status_code}")
except Exception as e:
    print(f"  ⚠️ EPA ECHO 错误: {e}")
    results["epa_echo"] = {"error": str(e), "source": "EPA ECHO"}

# ============================================================
# 汇总保存
# ============================================================
print("\n" + "=" * 60)
print("数据采集汇总")
print("=" * 60)

# 统计
success_count = sum(1 for v in results.values() if "error" not in v)
total_count = len(results)
print(f"\n成功: {success_count}/{total_count}")

for name, data in results.items():
    status = "✅" if "error" not in data else "❌"
    source = data.get("source", name)
    confidence = data.get("confidence", "N/A")
    print(f"  {status} {source} — 置信度: {confidence}")

# 保存完整结果
with open(f"{OUTPUT_DIR}/all_data_sources.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print(f"\n✅ 所有数据已保存到 {OUTPUT_DIR}/all_data_sources.json")

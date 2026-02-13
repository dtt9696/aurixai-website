# 构建美国企业风险诊断预警系统：一份基于Agent Skills的实战教程

**作者**: Manus AI
**日期**: 2026年2月13日
**版本**: v1.0

---

## 目录

1.  [引言](#1-引言)
2.  [准备工作](#2-准备工作)
3.  [系统核心架构](#3-系统核心架构)
4.  [模块一：全方位数据采集层](#4-模块一全方位数据采集层)
5.  [模块二：智能化数据处理与分析层](#5-模块二智能化数据处理与分析层)
6.  [模块三：深度风险建模与预测层](#6-模块三深度风险建模与预测层)
7.  [模块四：可视化报告与预警呈现层](#7-模块四可视化报告与预警呈现层)
8.  [实战案例：以特斯拉(Tesla, Inc.)为例](#8-实战案例以特斯拉tesla-inc为例)
9.  [附录：30个Skills速查表](#9-附录30个skills速查表)
10. [结语与展望](#10-结语与展望)

---

## 1. 引言

### 1.1 教程目标

本教程旨在为您提供一份详尽的指南，指导您如何利用我们为AURIX产品精心筛选和部署的30个Agent Skills，从零开始构建一个功能完备的**美国企业风险诊断与预警系统**。通过本教程，您将学会如何协同运用这些模块化的Skills，实现从数据采集、处理、分析到最终报告呈现的全流程自动化。

该系统能够覆盖以下核心能力：

| 能力维度 | 具体功能 | 涉及的核心Skills |
|---|---|---|
| 宏观经济监测 | GDP、CPI、利率、就业等指标追踪 | `fred-economic-data` |
| 公司财务分析 | 股价、财报、基本面数据获取与分析 | `alpha-vantage-automation`, `polygon-io-automation`, `twelve-data-automation` |
| 舆情新闻监控 | 全球新闻抓取、情感分析、实体识别 | `news-api-automation`, `rosette-text-analytics-automation` |
| 网络信息采集 | 网站深度爬取、结构化数据提取 | `firecrawl-automation`, `apify-automation`, `webscraping-ai-automation` |
| 风险预测建模 | 统计分析、机器学习、时间序列预测 | `statsmodels`, `scikit-learn`, `statistical-analysis` |
| 报告与可视化 | 交互式图表、Web报告、PDF报告 | `scientific-visualization`, `web-artifacts-builder`, `market-research-reports` |

### 1.2 Skill-Based架构的优势

传统的软件开发模式通常需要编写大量底层代码。而基于Agent Skills的模块化构建方式，如同使用乐高积木，让您能够聚焦于业务逻辑本身，而非繁琐的技术实现。每个Skill都是一个独立的功能单元，可以独立升级和维护；可以快速组合、替换或新增Skills，以应对不断变化的业务需求；并且利用了社区中经过验证的、口碑最好的开源工具和API，确保了系统的稳定性和功能的前沿性。

---

## 2. 准备工作

### 2.1 环境要求

在开始之前，请确保您的开发环境满足以下条件：

| 项目 | 要求 | 说明 |
|---|---|---|
| Skills目录 | `skills/` 子目录 | 所有30个Skills已推送至您的GitHub仓库 `dtt9696/aurixai-website` 的 `skills/` 目录 |
| Python | 3.8+ | 建议使用3.11版本 |
| Node.js | 18+ | 部分前端Skills需要 |
| 操作系统 | Linux / macOS | 推荐Ubuntu 22.04 |

### 2.2 API密钥与认证配置

本系统涉及多个外部数据源，需要获取对应的API密钥。下表汇总了所有需要的密钥及其用途：

| 服务 | 环境变量名 | 用途 | 免费额度 | 申请地址 |
|---|---|---|---|---|
| FRED | `FRED_API_KEY` | 美联储宏观经济数据 | 无限制 | [fredaccount.stlouisfed.org](https://fredaccount.stlouisfed.org) |
| Alpha Vantage | `ALPHA_VANTAGE_API_KEY` | 股票和公司基本面数据 | 25次/天 | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |
| News API | `NEWS_API_KEY` | 全球新闻文章 | 100次/天 | [newsapi.org](https://newsapi.org/) |
| Gemini | `GEMINI_API_KEY` | deep-research深度研究 | 有限免费 | [aistudio.google.com](https://aistudio.google.com/) |
| Firecrawl | 通过Rube MCP认证 | 网页爬取与数据提取 | 500页/月 | [firecrawl.dev](https://firecrawl.dev/) |

**配置方式**：在项目根目录下创建 `.env` 文件：

```bash
# .env 文件
FRED_API_KEY="YOUR_FRED_API_KEY"
ALPHA_VANTAGE_API_KEY="YOUR_ALPHA_VANTAGE_API_KEY"
NEWS_API_KEY="YOUR_NEWS_API_KEY"
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

> **提示**：对于 `ComposioHQ` 系列的 `automation` Skills（如 `alpha-vantage-automation`, `polygon-io-automation` 等），它们通过 **Rube MCP**（模型上下文协议）进行连接。首次使用时，Skill会自动引导您在浏览器中完成OAuth认证，无需手动配置密钥。只需将 `https://rube.app/mcp` 添加为MCP服务器即可。

### 2.3 安装Python依赖

```bash
# 安装核心依赖
pip install pandas numpy matplotlib seaborn plotly scikit-learn statsmodels
pip install requests beautifulsoup4 trafilatura httpx
pip install tabula-py  # 用于PDF表格提取
pip install python-dotenv  # 用于加载.env文件
```

---

## 3. 系统核心架构

本预警系统采用**四层分层架构**设计，将复杂任务分解为四个独立的层次。这种设计确保了系统的高度模块化和可扩展性。

### 3.1 架构概览图

下图展示了系统各层之间的关系以及数据如何在不同模块的Skills之间流动：

![系统核心架构图](https://files.manuscdn.com/user_upload_by_module/session_file/310519663244598621/eXDHuyJCIPDFvZaO.png)

### 3.2 数据流详解

下图从数据源到最终输出，展示了完整的数据处理流水线：

![数据流图](https://files.manuscdn.com/user_upload_by_module/session_file/310519663244598621/tzwmBtNdIOwClisC.png)

**第一层：数据采集层 (Data Acquisition Layer)** 负责从多个维度获取原始数据。`fred-economic-data` 获取宏观经济背景，`alpha-vantage-automation` 和 `polygon-io-automation` 负责公司财务和股价数据，而 `news-api-automation` 和 `firecrawl-automation` 则用于抓取新闻舆情和网络信息。

**第二层：数据处理与分析层 (Data Processing & Analysis Layer)** 对采集到的原始数据进行清洗、转换和初步分析。`article-extractor` 从网页中提取正文，`rosette-text-analytics-automation` 进行情感分析和实体识别，`exploratory-data-analysis` 和 `xlsx` 处理结构化数据。

**第三层：风险建模与预测层 (Risk Modeling & Prediction Layer)** 是系统的核心智能所在。`statistical-analysis`, `statsmodels`, 和 `scikit-learn` 用于构建统计和机器学习模型。`deep-research` 和 `market-research-reports` 用于进行更宏观和深入的定性与定量研究。

**第四层：报告与预警呈现层 (Presentation & Alerting Layer)** 是最终的价值输出。`scientific-visualization` 负责生成图表，`web-artifacts-builder` 和 `frontend-design` 将所有信息整合为交互式Web报告。

---

## 4. 模块一：全方位数据采集层

数据是任何分析系统的生命线。这一层我们将协同使用多个Skills，构建一个强大的自动化数据采集管道。

### 4.1 宏观经济与市场数据

**核心Skill**：`fred-economic-data`

FRED（Federal Reserve Economic Data）是美联储圣路易斯分行维护的数据库，包含超过80万个经济时间序列 [1]。通过 `fred-economic-data` Skill，我们可以方便地查询GDP、失业率、CPI等关键宏观指标。

**步骤一：配置API密钥**

确保 `FRED_API_KEY` 已在 `.env` 文件中正确设置。

**步骤二：编写数据采集脚本**

```python
# scripts/collect_macro_data.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
import pandas as pd

API_KEY = os.getenv("FRED_API_KEY")
BASE_URL = "https://api.stlouisfed.org/fred"

# 定义需要监控的关键经济指标
SERIES_MAP = {
    'GDP': '国内生产总值 (季度)',
    'GDPC1': '实际GDP (季度)',
    'UNRATE': '失业率 (月度)',
    'CPIAUCSL': '消费者价格指数 (月度)',
    'FEDFUNDS': '联邦基金利率 (月度)',
    'DGS10': '10年期国债收益率 (日度)',
    'HOUST': '新屋开工数 (月度)',
    'PAYEMS': '非农就业人数 (月度)',
    'INDPRO': '工业生产指数 (月度)',
    'SP500': '标普500指数 (日度)',
}

def fetch_fred_series(series_id, limit=120):
    """获取FRED时间序列数据"""
    response = requests.get(
        f"{BASE_URL}/series/observations",
        params={
            "api_key": API_KEY,
            "series_id": series_id,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit
        }
    )
    if response.status_code == 200:
        return response.json().get('observations', [])
    else:
        print(f"获取 {series_id} 失败: HTTP {response.status_code}")
        return []

def main():
    print("=" * 60)
    print("开始获取FRED宏观经济数据...")
    print("=" * 60)

    all_data = []
    for series_id, description in SERIES_MAP.items():
        observations = fetch_fred_series(series_id)
        if observations:
            df = pd.DataFrame(observations)
            df['series_id'] = series_id
            df['description'] = description
            all_data.append(df)
            print(f"  [OK] {series_id}: {description} ({len(observations)} 条记录)")
        else:
            print(f"  [FAIL] {series_id}: {description}")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        os.makedirs('data', exist_ok=True)
        final_df.to_csv('data/macro_economic_data.csv', index=False)
        print(f"\n宏观经济数据已保存，共 {len(final_df)} 条记录。")

if __name__ == "__main__":
    main()
```

**步骤三：执行脚本**

```bash
python3 scripts/collect_macro_data.py
```

**产出**：CSV文件 `data/macro_economic_data.csv`，包含所有关键宏观经济指标的时间序列数据。

### 4.2 公司财务与股价数据

**核心Skills**：`alpha-vantage-automation`, `polygon-io-automation`, `twelve-data-automation`

这三个Skills均通过Rube MCP连接，提供了丰富的公司财务和市场数据接口。以下以 `alpha-vantage-automation` 为例演示获取流程。

**步骤一：通过MCP认证**

```
# 在Agent环境中执行
RUBE_MANAGE_CONNECTIONS
toolkits: ["alpha_vantage"]
session_id: "risk_system_session"
```

**步骤二：探索可用工具**

```
RUBE_SEARCH_TOOLS
queries: [{use_case: "get company financial statements and stock prices", known_fields: "symbol"}]
session: {id: "risk_system_session"}
```

**步骤三：获取数据**

```python
# 获取公司概览（市值、行业、PE比率等）
overview = RUBE_MULTI_EXECUTE_TOOL(tools=[{
    'tool_slug': 'alpha_vantage_get_company_overview',
    'arguments': {'symbol': 'TSLA'}
}], memory={}, session_id="risk_system_session")

# 获取利润表（年度和季度）
income = RUBE_MULTI_EXECUTE_TOOL(tools=[{
    'tool_slug': 'alpha_vantage_get_income_statement',
    'arguments': {'symbol': 'TSLA'}
}], memory={}, session_id="risk_system_session")

# 获取资产负债表
balance = RUBE_MULTI_EXECUTE_TOOL(tools=[{
    'tool_slug': 'alpha_vantage_get_balance_sheet',
    'arguments': {'symbol': 'TSLA'}
}], memory={}, session_id="risk_system_session")

# 获取日线股价（完整历史）
prices = RUBE_MULTI_EXECUTE_TOOL(tools=[{
    'tool_slug': 'alpha_vantage_get_daily_adjusted',
    'arguments': {'symbol': 'TSLA', 'outputsize': 'full'}
}], memory={}, session_id="risk_system_session")
```

> **重要提示**：Alpha Vantage免费版每天限制25次API调用。如果需要更高频率的数据，建议使用 `polygon-io-automation` 或 `twelve-data-automation` 作为备用数据源。这正是我们部署多个金融数据Skills的原因——实现**API配额的分级回退策略**。

### 4.3 新闻舆情与网络信息

**核心Skills**：`news-api-automation`, `firecrawl-automation`, `article-extractor`, `hackernews-automation`

新闻舆情是企业风险预警的重要信号源。我们将通过多个渠道采集新闻数据。

**方式一：通过News API获取主流新闻**

```python
# 使用 news-api-automation 通过MCP调用
news = RUBE_MULTI_EXECUTE_TOOL(tools=[{
    'tool_slug': 'news_api_get_everything',
    'arguments': {
        'q': '"Tesla" OR "TSLA" OR "Elon Musk"',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 100,
        'from': '2026-01-13'  # 过去30天
    }
}], memory={}, session_id="risk_system_session")
```

**方式二：通过Firecrawl深度爬取**

对于需要深度分析的网站（如公司官网、行业报告网站），使用 `firecrawl-automation` 进行结构化数据提取：

```python
# 爬取SEC EDGAR的公司文件列表
sec_data = RUBE_MULTI_EXECUTE_TOOL(tools=[{
    'tool_slug': 'firecrawl_extract',
    'arguments': {
        'urls': ['https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=TSLA&type=10-K&dateb=&owner=include&count=10'],
        'prompt': 'Extract all filing dates, document types, and download links for SEC filings'
    }
}], memory={}, session_id="risk_system_session")
```

**方式三：通过Article Extractor清洗文章**

```bash
# 安装依赖
pip install trafilatura

# 提取文章正文
trafilatura --URL "https://example.com/news-article" --output-format json
```

**方式四：通过HackerNews获取科技圈讨论**

```python
# 使用 hackernews-automation 获取与公司相关的技术社区讨论
hn_results = RUBE_MULTI_EXECUTE_TOOL(tools=[{
    'tool_slug': 'hackernews_search_stories',
    'arguments': {'query': 'Tesla autonomous driving'}
}], memory={}, session_id="risk_system_session")
```

### 4.4 SEC公告与财报文件

**核心Skills**：`firecrawl-automation` (下载), `pdf` (提取)

对于PDF格式的SEC财报文件，我们需要先下载，再提取文本内容：

```python
# scripts/extract_sec_filing.py
import subprocess
from pypdf import PdfReader

# 步骤1：下载10-K报告
pdf_url = "https://www.sec.gov/Archives/edgar/data/1318605/..."
subprocess.run(['wget', '-q', pdf_url, '-O', 'data/tsla_10k.pdf'])

# 步骤2：提取文本
reader = PdfReader("data/tsla_10k.pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"

# 步骤3：保存提取的文本
with open("data/tsla_10k_text.txt", "w") as f:
    f.write(full_text)

print(f"已提取 {len(reader.pages)} 页，共 {len(full_text)} 字符。")
```

---

## 5. 模块二：智能化数据处理与分析层

原始数据是嘈杂的。这一层我们将利用AI和文本处理Skills，将原始数据转化为可供模型使用的、干净且结构化的信息。

### 5.1 文本数据清洗与提取

**核心Skills**：`article-extractor`, `pdf`, `exploratory-data-analysis`

对于从网页和PDF中获取的原始文本，我们需要进行系统性的清洗。`article-extractor` 内部集成了Mozilla的Readability库，可以有效地从HTML中剥离出文章主体。对于PDF中的表格数据，可以结合 `tabula-py` 进行精确提取：

```python
# scripts/extract_pdf_tables.py
import tabula
import pandas as pd

pdf_path = "data/tsla_10k.pdf"
tables = tabula.read_pdf(pdf_path, pages="all", guess=True, multiple_tables=True)

if tables:
    print(f"在PDF中找到 {len(tables)} 个表格。")
    for i, table in enumerate(tables):
        table.to_csv(f"data/financial_table_{i+1}.csv", index=False)
        print(f"  表格 {i+1}: {table.shape[0]} 行 x {table.shape[1]} 列")
```

### 5.2 舆情情感分析

**核心Skill**：`rosette-text-analytics-automation`

Rosette API提供了企业级的文本分析功能，包括情感分析、实体识别和语言检测。通过对所有新闻文章运行情感分析，我们可以得到一个量化的舆情分数时间序列：

```python
# 对每篇新闻文章进行情感分析
sentiment_results = []
for article in cleaned_articles:
    result = RUBE_MULTI_EXECUTE_TOOL(tools=[{
        'tool_slug': 'rosette_sentiment_analysis',
        'arguments': {
            'content': article['text'],
            'language': 'eng'
        }
    }], memory={}, session_id="risk_system_session")

    sentiment_results.append({
        'date': article['published_at'],
        'title': article['title'],
        'sentiment_label': result['sentiment']['label'],  # positive/negative/neutral
        'sentiment_confidence': result['sentiment']['confidence'],
        'source': article['source']
    })

# 转换为DataFrame并计算每日平均情感分数
sentiment_df = pd.DataFrame(sentiment_results)
sentiment_df['sentiment_score'] = sentiment_df['sentiment_label'].map({
    'positive': 1, 'neutral': 0, 'negative': -1
}) * sentiment_df['sentiment_confidence']

daily_sentiment = sentiment_df.groupby('date')['sentiment_score'].mean().reset_index()
daily_sentiment.to_csv('data/daily_sentiment.csv', index=False)
```

### 5.3 财务指标计算

**核心Skill**：`xlsx`, `exploratory-data-analysis`

利用 `xlsx` Skill处理和计算关键财务风险指标：

```python
# scripts/calculate_financial_ratios.py
import pandas as pd

# 假设已从Alpha Vantage获取了财务数据
# income_df = pd.read_json('data/income_statement.json')
# balance_df = pd.read_json('data/balance_sheet.json')

# 计算关键风险指标
def calculate_risk_ratios(income, balance):
    ratios = {}

    # 偿债能力指标
    ratios['current_ratio'] = balance['totalCurrentAssets'] / balance['totalCurrentLiabilities']
    ratios['debt_to_equity'] = balance['totalLiabilities'] / balance['totalShareholderEquity']

    # 盈利能力指标
    ratios['gross_margin'] = income['grossProfit'] / income['totalRevenue']
    ratios['net_margin'] = income['netIncome'] / income['totalRevenue']
    ratios['roe'] = income['netIncome'] / balance['totalShareholderEquity']

    # 增长指标 (需要多期数据)
    ratios['revenue_growth'] = income['totalRevenue'].pct_change()

    return ratios

# 定义风险阈值
RISK_THRESHOLDS = {
    'current_ratio': {'low': 2.0, 'medium': 1.5, 'high': 1.0},
    'debt_to_equity': {'low': 0.5, 'medium': 1.0, 'high': 2.0},
    'net_margin': {'low': 0.10, 'medium': 0.05, 'high': 0.0},
}
```

---

## 6. 模块三：深度风险建模与预测层

这是将数据转化为洞察的核心环节。我们将使用统计学和机器学习模型来识别风险因子并进行预测。

### 6.1 时间序列分析与预测

**核心Skill**：`statsmodels`

使用ARIMA/SARIMAX模型对股价波动率或财务指标进行时间序列预测：

```python
# scripts/time_series_forecast.py
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt

# 加载股价数据
prices = pd.read_csv('data/stock_prices.csv', parse_dates=['date'], index_col='date')
returns = prices['close'].pct_change().dropna()

# 计算已实现波动率（20日滚动标准差）
volatility = returns.rolling(window=20).std() * np.sqrt(252)  # 年化

# ADF平稳性检验
adf_result = adfuller(volatility.dropna())
print(f"ADF统计量: {adf_result[0]:.4f}")
print(f"P值: {adf_result[1]:.4f}")

# 拟合ARIMA模型
model = ARIMA(volatility.dropna(), order=(2, 1, 2))
results = model.fit()
print(results.summary())

# 预测未来30天的波动率
forecast = results.forecast(steps=30)
print("\n未来30天波动率预测:")
print(forecast)

# 可视化
fig, ax = plt.subplots(figsize=(15, 6))
volatility.tail(252).plot(ax=ax, label='历史波动率')
forecast.plot(ax=ax, label='预测波动率', color='red', linestyle='--')
ax.set_title('Tesla股价波动率预测 (ARIMA)')
ax.set_ylabel('年化波动率')
ax.legend()
plt.savefig('data/volatility_forecast.png', dpi=150, bbox_inches='tight')
```

### 6.2 机器学习风险分类

**核心Skill**：`scikit-learn`

使用随机森林等集成学习方法，构建企业风险等级分类模型：

```python
# scripts/risk_classification_model.py
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import numpy as np

# 特征矩阵（整合宏观、财务、舆情数据）
# features: GDP增长率, CPI变化, 利率, 流动比率, 负债率, 净利润率, 舆情分数, 波动率
# X = pd.read_csv('data/combined_features.csv')
# y = pd.read_csv('data/risk_labels.csv')  # 0=低风险, 1=中风险, 2=高风险

# 构建Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    ))
])

# 训练与评估
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
pipeline.fit(X_train, y_train)

# 交叉验证
cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='f1_weighted')
print(f"交叉验证F1分数: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# 特征重要性分析
feature_names = ['GDP增长率', 'CPI变化', '利率', '流动比率', '负债率', '净利润率', '舆情分数', '波动率']
importances = pipeline.named_steps['classifier'].feature_importances_
for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
    print(f"  {name}: {imp:.4f}")
```

### 6.3 深度市场研究

**核心Skills**：`deep-research`, `market-research-reports`

当需要对特定行业趋势、技术变革或竞争格局进行深入的开放式研究时，`deep-research` Skill可以自动规划、执行多步研究并生成详细报告：

```bash
# 启动深度研究任务
python3 skills/deep-research/scripts/research.py \
    --query "Analyze the competitive landscape and regulatory risks for Tesla's autonomous driving technology (FSD). Include comparison with Waymo, Cruise, and Chinese competitors. Assess NHTSA investigation impacts and potential liability risks." \
    --stream

# 研究完成后，报告会以Markdown格式输出
# 预计耗时: 2-10分钟
# 预计成本: $2-5
```

`market-research-reports` Skill则可以生成50页以上的专业级市场研究报告，采用McKinsey/BCG风格的排版：

```bash
# 生成完整的市场研究报告（需要LaTeX环境）
# 报告将包含: Porter五力分析、PESTLE分析、SWOT分析、TAM/SAM/SOM市场规模等
```

---

## 7. 模块四：可视化报告与预警呈现层

最后一步是将所有分析结果以清晰、直观的方式呈现给用户。

### 7.1 数据可视化

**核心Skill**：`scientific-visualization`

```python
# scripts/create_risk_dashboard.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np

sns.set_theme(style="whitegrid", font_scale=1.2)

def create_price_sentiment_chart(stock_df, sentiment_df, output_path):
    """创建股价与舆情分数对比图"""
    fig, ax1 = plt.subplots(figsize=(16, 8))

    # 绘制股价
    ax1.plot(stock_df['date'], stock_df['close'], color='#2196F3', linewidth=2, label='Stock Price')
    ax1.fill_between(stock_df['date'], stock_df['close'], alpha=0.1, color='#2196F3')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Stock Price (USD)', color='#2196F3', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#2196F3')

    # 创建第二个Y轴绘制情感分数
    ax2 = ax1.twinx()
    sentiment_ma = sentiment_df['sentiment_score'].rolling(window=7).mean()
    ax2.plot(sentiment_df['date'], sentiment_ma, color='#FF5722', linewidth=2, linestyle='--', label='Sentiment (7-day MA)')
    ax2.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
    ax2.set_ylabel('Sentiment Score', color='#FF5722', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='#FF5722')

    # 标注高风险区域（情感分数低于-0.3）
    risk_zones = sentiment_df[sentiment_ma < -0.3]
    for _, row in risk_zones.iterrows():
        ax1.axvspan(row['date'], row['date'] + pd.Timedelta(days=1), alpha=0.15, color='red')

    plt.title('Tesla: Stock Price vs. News Sentiment Analysis', fontsize=16, fontweight='bold')
    fig.legend(loc='upper left', bbox_to_anchor=(0.12, 0.95))
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"图表已保存至 {output_path}")


def create_risk_heatmap(risk_data, output_path):
    """创建风险热力图"""
    fig, ax = plt.subplots(figsize=(12, 8))

    risk_categories = ['财务风险', '市场风险', '舆情风险', '监管风险', '运营风险']
    time_periods = ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026']

    # 模拟风险评分矩阵 (1-5, 5为最高风险)
    risk_matrix = np.array([
        [2, 3, 2, 3, 2],
        [3, 4, 3, 2, 3],
        [2, 2, 4, 3, 3],
        [3, 3, 3, 4, 4],
        [2, 2, 2, 3, 2],
    ])

    sns.heatmap(risk_matrix, annot=True, fmt='d', cmap='RdYlGn_r',
                xticklabels=time_periods, yticklabels=risk_categories,
                linewidths=1, linecolor='white', ax=ax,
                vmin=1, vmax=5, cbar_kws={'label': '风险等级 (1-5)'})

    ax.set_title('Tesla 风险热力图', fontsize=16, fontweight='bold')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"风险热力图已保存至 {output_path}")
```

### 7.2 构建Web前端报告

**核心Skills**：`web-artifacts-builder`, `frontend-design`, `react-best-practices`

`web-artifacts-builder` 让我们可以使用React和Tailwind CSS来构建现代化的Web报告界面。`frontend-design` 提供了设计规范和最佳实践，而 `react-best-practices` 确保代码质量。

> **设计原则**：根据AURIX产品的定位，Web报告应遵循**移动端优先 (Mobile-First)** 的设计理念，确保在手机端和微信公众号内嵌页面中也能完美展示。

报告页面应包含以下核心组件：

| 组件 | 功能 | 数据来源 |
|---|---|---|
| 风险评分卡 | 显示综合风险等级（低/中/高） | 机器学习模型输出 |
| 股价走势图 | 交互式K线图 + 舆情叠加 | Alpha Vantage + 情感分析 |
| 财务摘要表 | 关键财务指标和同比变化 | SEC财报数据 |
| 风险热力图 | 多维度风险时间演变 | 综合分析结果 |
| 新闻时间线 | 按时间排列的关键新闻 | News API |
| 深度研究摘要 | AI生成的行业分析 | deep-research |

---

## 8. 实战案例：以特斯拉(Tesla, Inc.)为例

现在，我们将把以上所有模块串联起来，完成一个对特斯拉公司（股票代码：TSLA）的端到端风险诊断流程。

### 8.1 案例目标

生成一份关于特斯拉的综合风险报告，包含过去一年的股价与新闻舆情对比图、最新的财务摘要关键指标、一份关于其在自动驾驶领域竞争格局的深度研究报告，以及一个包含以上所有信息的可视化Web页面。

### 8.2 分步执行流程

```bash
#!/bin/bash
# scripts/run_tesla_diagnosis.sh
# Tesla企业风险诊断预警 - 自动化执行脚本

set -e
COMPANY="Tesla"
TICKER="TSLA"
WORK_DIR="data/tesla_diagnosis_$(date +%Y%m%d)"

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "=========================================="
echo " $COMPANY ($TICKER) 风险诊断预警"
echo " 执行时间: $(date)"
echo "=========================================="

# ---- 第一阶段：数据采集 ----
echo ""
echo "[阶段 1/4] 数据采集..."

echo "  → 获取宏观经济数据..."
python3 ../../scripts/collect_macro_data.py

echo "  → 获取公司财务数据... (通过MCP)"
# alpha-vantage-automation: 获取财报和股价
# polygon-io-automation: 获取实时行情（备用）

echo "  → 获取新闻舆情数据... (通过MCP)"
# news-api-automation: 获取最近30天新闻
# firecrawl-automation: 深度爬取关键文章

echo "  → 下载SEC财报文件..."
# firecrawl + pdf: 下载并提取10-K/10-Q

# ---- 第二阶段：数据处理 ----
echo ""
echo "[阶段 2/4] 数据处理与分析..."

echo "  → 清洗新闻文本..."
# article-extractor: 提取正文

echo "  → 运行情感分析..."
# rosette-text-analytics-automation: 情感分析

echo "  → 计算财务指标..."
python3 ../../scripts/calculate_financial_ratios.py

# ---- 第三阶段：风险建模 ----
echo ""
echo "[阶段 3/4] 风险建模与预测..."

echo "  → 时间序列预测..."
python3 ../../scripts/time_series_forecast.py

echo "  → 风险分类..."
python3 ../../scripts/risk_classification_model.py

echo "  → 启动深度研究..."
python3 ../../skills/deep-research/scripts/research.py \
    --query "Comprehensive risk assessment for $COMPANY ($TICKER): autonomous driving regulatory risks, competition from Chinese EV makers, battery supply chain vulnerabilities, and Elon Musk key-person risk." \
    --stream

# ---- 第四阶段：报告生成 ----
echo ""
echo "[阶段 4/4] 生成可视化报告..."

echo "  → 生成图表..."
python3 ../../scripts/create_risk_dashboard.py

echo "  → 构建Web报告..."
# web-artifacts-builder: 生成交互式HTML报告

echo ""
echo "=========================================="
echo " 诊断完成！"
echo " 报告位置: $WORK_DIR/final_report.html"
echo "=========================================="
```

**执行**：

```bash
chmod +x scripts/run_tesla_diagnosis.sh
./scripts/run_tesla_diagnosis.sh
```

---

## 9. 附录：30个Skills速查表

以下是本系统使用的全部30个Skills的分类速查表，方便您在开发过程中快速定位所需功能。

### 9.1 数据源管理与金融数据

| Skill名称 | 功能 | 数据源 | 认证方式 |
|---|---|---|---|
| `fred-economic-data` | 80万+经济时间序列 | 美联储FRED | API Key |
| `alpha-vantage-automation` | 股票、外汇、加密货币数据 | Alpha Vantage | Rube MCP |
| `polygon-io-automation` | 实时/历史市场数据 | Polygon.io | Rube MCP |
| `twelve-data-automation` | 股票、ETF、外汇数据 | Twelve Data | Rube MCP |

### 9.2 网页爬虫与数据采集

| Skill名称 | 功能 | 特点 | 认证方式 |
|---|---|---|---|
| `firecrawl-automation` | 网页爬取、结构化提取 | 支持AI提取、批量爬取 | Rube MCP |
| `apify-automation` | 通用网页爬虫平台 | 500+预制Actor | Rube MCP |
| `webscraping-ai-automation` | AI驱动的网页抓取 | 自动处理反爬 | Rube MCP |
| `article-extractor` | 文章正文提取 | 基于Mozilla Readability | 本地运行 |

### 9.3 数据分析与预测

| Skill名称 | 功能 | 适用场景 | 依赖 |
|---|---|---|---|
| `exploratory-data-analysis` | 自动化EDA | 数据探索、质量检查 | Python |
| `statistical-analysis` | 统计分析 | 假设检验、回归分析 | Python |
| `statsmodels` | 统计建模与计量经济学 | 时间序列、ARIMA | Python |
| `scikit-learn` | 机器学习 | 分类、回归、聚类 | Python |
| `scientific-visualization` | 科学可视化 | 出版级图表 | Python |
| `xlsx` | Excel处理 | 财务模型、数据表 | Python |

### 9.4 舆情新闻分析

| Skill名称 | 功能 | 数据源 | 认证方式 |
|---|---|---|---|
| `news-api-automation` | 全球新闻搜索 | NewsAPI | Rube MCP |
| `hackernews-automation` | 科技社区讨论 | Hacker News | Rube MCP |
| `rosette-text-analytics-automation` | 文本分析/情感分析 | Rosette API | Rube MCP |
| `research-lookup` | 学术/研究资料检索 | 多源 | 本地运行 |
| `market-research-reports` | 专业市场研究报告 | AI生成 | 本地运行 |
| `deep-research` | 自主深度研究 | Gemini | API Key |
| `content-research-writer` | 内容研究与写作 | AI辅助 | 本地运行 |

### 9.5 网页设计与前端

| Skill名称 | 功能 | 技术栈 | 用途 |
|---|---|---|---|
| `web-artifacts-builder` | Web应用构建 | React + Tailwind | 报告页面 |
| `web-design-guidelines` | 设计规范 | 通用 | 设计参考 |
| `react-best-practices` | React最佳实践 | React | 代码质量 |
| `frontend-design` | 前端设计 | HTML/CSS/JS | UI设计 |
| `webapp-testing` | Web应用测试 | Playwright等 | 质量保证 |

### 9.6 综合辅助

| Skill名称 | 功能 | 用途 |
|---|---|---|
| `-21risk-automation` | 风险自动化 | 风险评估流程 |
| `linkedin-automation` | LinkedIn自动化 | 公司信息、人员变动 |
| `pdf` | PDF处理 | 财报提取、报告生成 |

---

## 10. 结语与展望

通过本教程，您已经掌握了如何利用Agent Skills这一模块化方式，构建一个复杂而强大的企业风险诊断系统。您所构建的不仅是一个应用，更是一个灵活、可扩展、可持续进化的智能系统。

**未来可扩展方向**：

| 方向 | 描述 | 潜在Skills |
|---|---|---|
| 社交媒体监控 | 接入Twitter/X、Reddit等社交平台 | 新增social-media类Skills |
| 供应链风险 | 追踪供应商和物流风险 | 整合供应链数据API |
| ESG评估 | 环境、社会和治理风险评估 | 整合ESG数据源 |
| 自动化预警 | 定时运行 + 阈值触发通知 | 结合schedule定时任务 |
| 多语言支持 | 中文舆情分析 | 扩展NLP模型 |

> **数据采集策略建议**：首次调用API时应提取最大时间范围的完整数据并保存，后续调用仅采集增量更新数据。这种"全量初始化 + 增量更新"的策略可以显著降低API调用成本。

> **上市公司 vs 非上市公司**：对于上市公司，预警报告应优先展示负面舆情和财报数据；对于非上市公司，由于缺乏公开财务数据，应聚焦于负面舆情分析。制裁名单、专利质押、司法诉讼等特殊数据项如果被发现，应优先突出显示。

---

## 参考资料

[1]: [FRED - Federal Reserve Economic Data](https://fred.stlouisfed.org/) - 美联储圣路易斯分行经济数据库
[2]: [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/) - 股票和金融数据API
[3]: [Composio Rube MCP](https://rube.app/mcp) - 模型上下文协议集成平台
[4]: [Firecrawl Documentation](https://docs.firecrawl.dev/) - 网页爬取与数据提取
[5]: [scikit-learn Documentation](https://scikit-learn.org/stable/) - 机器学习库
[6]: [statsmodels Documentation](https://www.statsmodels.org/) - 统计建模库
[7]: [SEC EDGAR](https://www.sec.gov/edgar/searchedgar/companysearch) - 美国证券交易委员会电子数据库

# 供应链Skills和数据源调研结果

## 一、现有Manus平台Skills搜索结果

### 直接相关的已有Skills
1. **zoho-inventory-automation** (ComposioHQ) - Zoho库存管理自动化
2. **census-bureau-automation** (ComposioHQ) - 美国人口普查局数据自动化（含贸易数据）
3. **simpy** (K-Dense-AI) - 离散事件仿真库（可用于供应链仿真）

### 间接相关的已有Skills（数据采集/爬虫）
4. **apify-automation** - 网页爬虫自动化
5. **firecrawl-automation** - 网页抓取和数据提取
6. **scrapingant-automation** - 爬虫自动化
7. **scrapingbee-automation** - 爬虫自动化
8. **webscraping-ai-automation** - AI网页抓取

### 间接相关的已有Skills（数据分析）
9. **fred-economic-data** - FRED经济数据（含供应链相关指标）
10. **alpha-vantage-automation** - 金融数据
11. **scikit-learn** - 机器学习（可用于需求预测）
12. **statsmodels** - 统计模型（可用于时间序列预测）
13. **scientific-visualization** - 科学可视化

### 结论：现有Skills库中没有专门的供应链管理Skills

---

## 二、推荐创建的供应链Skills体系（6个独立可协作Skills）

### Skill 1: supply-chain-data-hub（供应链数据中心）
- **领域**: 数据采集与整合
- **功能**: 从多个免费公开数据源采集供应链数据
- **数据源**: FRED GSCPI、BTS FAF、USITC DataWeb、World Bank LPI、ImportYeti、CBP
- **不重叠**: 专注数据采集，不做分析

### Skill 2: demand-forecasting（需求预测）
- **领域**: 供应链计划与预测
- **功能**: 时间序列预测、需求规划、销售预测
- **核心库**: statsmodels (ARIMA/SARIMA), Prophet, scikit-learn
- **参考**: samirsaci/ml-forecast-features-eng (⭐68)
- **不重叠**: 专注预测，不做库存优化

### Skill 3: inventory-optimization（库存优化）
- **领域**: 库存管理
- **功能**: EOQ、安全库存、ABC分析、库存周转优化
- **核心库**: stockpyl, scipy, PuLP
- **参考**: LarrySnyder/stockpyl, samirsaci/inventory-stochastic (⭐18)
- **不重叠**: 专注库存决策，不做预测

### Skill 4: logistics-network-optimization（物流网络优化）
- **领域**: 物流管理
- **功能**: 路线优化、仓库选址、运输成本最小化、装箱优化
- **核心库**: OR-Tools, PuLP, NetworkX
- **参考**: samirsaci/picking-route (⭐132), hzjken/multimodal-transportation-optimization (⭐292)
- **不重叠**: 专注物流网络，不做库存

### Skill 5: supply-chain-risk-monitor（供应链风险监控）
- **领域**: 风险管理
- **功能**: 供应商风险评估、地缘政治风险、GSCPI监控、供应链中断预警
- **核心库**: pandas, scikit-learn, networkx
- **数据源**: NY Fed GSCPI, ISM PMI, ImportYeti供应商数据
- **不重叠**: 专注风险评估，不做优化

### Skill 6: supply-chain-simulation（供应链仿真）
- **领域**: 供应链仿真与策略评估
- **功能**: 蒙特卡洛仿真、离散事件仿真、What-if分析
- **核心库**: SimPy, numpy, scipy
- **参考**: samirsaci/monte-carlo (⭐35)
- **不重叠**: 专注仿真模拟，不做实际优化决策

---

## 三、免费公开数据源清单

### A. 可直接API接入的免费数据源

| 数据源 | 类型 | 接入方式 | 更新频率 | 数据内容 |
|--------|------|----------|----------|----------|
| NY Fed GSCPI | 供应链压力指数 | Excel下载 | 月度 | 全球供应链压力指数 |
| FRED (St. Louis Fed) | 经济指标 | REST API (免费Key) | 日/月/季 | ISM PMI、制造业库存、供应商交付等 |
| World Bank DataBank | 物流绩效 | REST API (免费) | 年度 | LPI物流绩效指数、贸易数据 |
| US Census Bureau | 贸易数据 | REST API (免费) | 月度 | 进出口贸易统计 |
| USITC DataWeb | 关税贸易 | Web下载 | 月度 | 美国关税和贸易数据 |
| BTS FAF | 货运数据 | CSV下载 | 年度 | 美国货运流量（重量、价值、模式） |
| CBP Public Data | 海关数据 | Web下载 | 月度 | 海关和边境保护统计 |

### B. 可通过爬虫获取的免费数据源

| 数据源 | 类型 | 接入方式 | 数据内容 |
|--------|------|----------|----------|
| ImportYeti | 海运提单 | 网页爬虫 | 7000万+美国海关海运记录，供应商信息 |
| LMI (the-lmi.com) | 物流经理指数 | 网页爬虫 | 月度物流经理调查（库存、运输、仓储） |
| Trading Economics | 经济指标 | 网页爬虫 | ISM PMI、供应商交付指数等 |
| Freightos Baltic Index | 运费指数 | 网页爬虫 | 全球集装箱运费指数 |

### C. GitHub开源数据集

| 数据集 | Stars | 内容 |
|--------|-------|------|
| ciol-researchlab/SupplyGraph | 80 | 供应链图神经网络基准数据集 |
| hoshigan/Supply-Chain-Analytic | - | JIT公司供应链分析数据集 |

---

## 四、GitHub热门供应链开源工具

| 仓库 | Stars | 语言 | 功能 |
|------|-------|------|------|
| samirsaci/picking-route | 132 | Python | 仓库拣货路线优化 |
| samirsaci/supply-chain-optimization | 108 | Python | 供应链网络优化(线性规划) |
| hzjken/multimodal-transportation-optimization | 292 | Python | 多式联运成本优化 |
| LarrySnyder/stockpyl | ~100 | Python | 库存优化和仿真 |
| KevinFasusi/supplychainpy | ~500 | Python | 供应链分析建模仿真库 |
| samirsaci/ml-forecast-features-eng | 68 | Python | 零售需求预测特征工程 |
| samirsaci/monte-carlo | 35 | Python | 蒙特卡洛供应链仿真 |
| samirsaci/container-optimization | 34 | Python | 集装箱装载优化 |
| samirsaci/last-mile | 33 | Python | 最后一公里配送优化 |
| samirsaci/production-planning | 31 | Python | 生产计划优化 |
| samirsaci/supply-planning | 14 | Python | 供应计划(线性规划) |
| samirsaci/inventory-stochastic | 18 | Python | 随机需求库存管理 |
| samirsaci/procurement-management | 9 | Python | 采购流程优化 |

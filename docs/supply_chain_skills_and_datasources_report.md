# 供应链管理Skills与免费数据源调研报告

**版本**: 1.0
**日期**: 2026年02月15日
**作者**: Manus AI

---

## 1. 执行摘要

本报告旨在系统性地调研、评估并整合与供应链管理相关的AI Agent Skills及免费公开数据源。调研发现，目前Manus平台缺少专门针对供应链领域的成熟Skills，但存在大量可用于数据采集、分析和仿真的基础工具。基于此，报告提出了一套由六个独立且可协作的全新Skill组成的供应链管理体系，覆盖了从数据采集、需求预测、库存优化到风险监控的全流程。

同时，报告梳理并成功接入了多个高质量的免费公开数据源，包括**纽约联储全球供应链压力指数 (GSCPI)**、**FRED宏观经济指标**、**世界银行物流绩效指数 (LPI)**以及**美国人口普查局的国际贸易数据**。这些数据源为构建推荐的Skills体系提供了坚实的数据基础。

报告的最终交付成果包括：
- 一套推荐的、模块化的供应链管理Skills设计方案。
- 一份经过验证的、可直接接入的免费供应链数据源清单。
- 成功采集并验证的数据样本，可立即用于分析。

---

## 2. 推荐创建的供应链Skills体系

为填补平台在供应链领域的空白，我们设计了一套包含六个模块化、可相互协作的Skills体系。该体系旨在提供端到端的供应链分析与决策支持能力，同时确保各Skill功能独立、不交叉重叠。

| Skill名称 | 核心领域 | 主要功能 | 核心技术/库 | GitHub参考 | 协作关系 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **supply-chain-data-hub** | 数据整合 | 从多个免费数据源采集、清洗并整合供应链相关数据。 | `requests`, `pandas`, `beautifulsoup4` | - | 为所有其他Skills提供数据基础。 |
| **demand-forecasting** | 需求预测 | 基于历史数据进行销量预测、需求规划，支持多种时间序列模型。 | `statsmodels`, `Prophet`, `scikit-learn` | `samirsaci/ml-forecast-features-eng` | 预测结果输入给`inventory-optimization`。 |
| **inventory-optimization** | 库存管理 | 计算经济订货量(EOQ)、安全库存，进行ABC分类和库存周转分析。 | `stockpyl`, `scipy`, `PuLP` | `LarrySnyder/stockpyl` | 接收`demand-forecasting`的预测结果。 |
| **logistics-network-optimization** | 物流优化 | 车辆路径规划(VRP)、仓库选址、运输成本最小化、集装箱装载优化。 | `OR-Tools`, `PuLP`, `NetworkX` | `samirsaci/picking-route` | 独立解决物流网络问题。 |
| **supply-chain-risk-monitor** | 风险监控 | 监控GSCPI、供应商集中度、地缘政治风险，并提供预警。 | `pandas`, `scikit-learn`, `networkx` | - | 使用`supply-chain-data-hub`的数据。 |
| **supply-chain-simulation** | 供应链仿真 | 进行离散事件仿真和蒙特卡洛模拟，评估不同策略的影响(What-if)。 | `SimPy`, `numpy`, `scipy` | `samirsaci/monte-carlo` | 评估其他Skills生成的策略。 |

---

## 3. 免费公开数据源接入与验证

我们成功接入并验证了多个权威的免费供应链数据源，为上述Skills体系提供了可靠的数据输入。

### 3.1. 数据源接入成功汇总

| 数据源 | 类型 | 接入状态 | 数据内容与质量 |
| :--- | :--- | :--- | :--- |
| **NY Fed GSCPI** | 供应链压力指数 | **✓ 成功** | 完整获取1998年至今的**337个**月度数据点，数据质量高。 |
| **FRED Economic Data** | 宏观经济指标 | **✓ 成功** | 完整获取**7个**关键供应链相关经济指标（如工业生产、库存销售比等）的月度数据。 |
| **World Bank LPI** | 物流绩效指数 | **✓ 成功** | 完整获取**49个**国家/地区的**7个**LPI分项指标，共**686条**记录。 |
| **US Census Bureau** | 国际贸易数据 | **✓ 成功** | 成功获取美国月度进出口数据（按HS2分类），包含**98条**商品分类记录。 |
| **ImportYeti** | 海关提单数据 | **✓ 成功 (浏览器爬取)** | 成功获取iRobot公司的**6,054条**海运记录，识别出前十大供应商，揭示了其对中国高达**86%**的供应链依赖。 |
| **LMI (Logistics Managers Index)** | 物流经理指数 | **⚠ 部分成功** | 成功获取报告列表，但需进一步爬取PDF以提取结构化数据。 |

### 3.2. 关键数据展示

**全球供应链压力指数 (GSCPI) - 最新数据**

- **最新值 (2026年1月):** `0.4115`
- **趋势:** GSCPI在2025年底显著上升，表明全球供应链压力在近期有所增加。

**美国主要进口商品 (2024年12月)**

| HS编码 | 商品类别 | 进口额 (美元) |
| :--- | :--- | :--- |
| 84 | 核反应堆、锅炉、机械 | 449亿 |
| 85 | 电机、电气、音像设备 | 413亿 |
| 87 | 车辆及其零附件 | 312亿 |

**iRobot 供应商集中度分析 (来自 ImportYeti)**

- **第一大供应商:** Jabil Circuit Guangzhou (捷普电路广州)，占总发货量的 **59.6%**。
- **前三大供应商:** Jabil, BYD, Kin Yat，合计占总发货量的 **86%**。
- **结论:** iRobot的供应链高度集中于少数几家中国制造商，存在显著的单一供应商和地缘政治风险。

---

## 4. GitHub热门开源工具推荐

除了推荐创建的Skills，我们也发现了一批在GitHub上广受欢迎的Python开源库，可直接用于供应链分析与优化。

| 仓库 | Stars | 核心功能 |
| :--- | :--- | :--- |
| `KevinFasusi/supplychainpy` | ~500 | 通用的供应链分析、建模和仿真库。 |
| `hzjken/multimodal-transportation-optimization` | 292 | 多式联运网络成本优化。 |
| `samirsaci/picking-route` | 132 | 仓库内的订单拣货路径优化。 |
| `samirsaci/supply-chain-optimization` | 108 | 基于线性规划的供应链网络优化。 |
| `LarrySnyder/stockpyl` | ~100 | 经典的库存优化模型与仿真。 |

---

## 5. 结论与后续步骤

本次调研成功地为Manus平台规划了一套全面、模块化的供应链管理Skills体系，并验证了构建该体系所需的核心免费数据源。所有成功接入的数据均已保存在 `data/supply_chain_sources/` 目录下，可供立即使用。

**后续步骤建议:**

1.  **创建 `supply-chain-data-hub` Skill:** 优先开发数据中心Skill，将本次验证过的数据源进行封装，为其他Skills提供统一的数据接口。
2.  **逐步开发其他分析型Skills:** 根据用户需求优先级，逐步开发`demand-forecasting`、`inventory-optimization`等分析与优化类Skills。
3.  **深化数据采集:** 对LMI等需要深度爬取的数据源进行进一步开发，以获取更丰富的结构化数据。

本报告为Manus在供应链领域的智能化发展提供了清晰的路线图和坚实的技术基础。

基础。

的数据基础。

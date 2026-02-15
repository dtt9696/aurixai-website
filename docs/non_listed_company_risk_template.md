# 非上市公司风险诊断报告模版设计

## 模版设计理念

非上市公司缺乏财报、股价等公开财务数据，因此需要通过替代数据源（Alternative Data）来构建风险画像。本模版采用"五维度+替代数据"框架，结合Mulerun报告的设计优势和AURIX系统的分析方法论。

## 报告结构

### 1. 报告头部
- 风险等级徽章（CRITICAL / HIGH / MEDIUM-HIGH / MEDIUM / LOW）
- 供应链聚焦标签（如适用）
- 公司名称（中英文）
- 副标题：非上市企业 · 行业 · AI全球企业风险预警AGENT
- 元信息：报告日期、总部地址、NON-LISTED标签

### 2. 综合风险评分环
- SVG环形图展示综合评分（0-100）
- 五维度评分卡（适配非上市公司）：
  - 口碑/舆情 Sentiment（Indeed/Glassdoor/新闻）
  - 融资健康 Financing（融资轮次/空窗期/投资人）
  - 贸易活跃度 Trade Activity（提单量/发货频率）
  - 运营稳定性 Operations（团队/注册/合规）
  - 供应链风险 Supply Chain（供应商集中度/地缘风险）

### 3. 风险预警区
- 分级预警：CRITICAL(红) / HIGH(橙) / MEDIUM(黄) / INFO(蓝)
- 每条预警包含：级别、描述、数据来源

### 4. 企业概况
- 成立时间、融资阶段、总融资额
- 员工规模、自报营收、注册地
- 业务描述、管理层、投资人

### 5. 供应链风险分析（核心模块）
- 供应链风险指标矩阵（交通灯标识）
- 年度提单趋势图（ImportYeti数据）
- 月度提单分布图
- 供应商集中度分析（HHI指数 + 饼图）
- 到港分布
- 产品品类 & HS编码
- 最近提单记录
- 全球供应链压力指数（GSCPI）趋势
- 宏观经济背景指标（FRED数据）

### 6. 竞争格局分析
- 竞品对比表（公司/成立/总部/融资/特色）
- 竞争力评估文字

### 7. 员工口碑分析
- 员工满意度雷达图（vs 行业平均）
- 维度对比表
- 关键评论摘要

### 8. 融资时间线
- 时间线展示融资历程
- 融资空窗期标注

### 9. 司法诉讼（如有）
- 案件列表
- 案件详情

### 10. 风控建议
- 三栏式建议卡：前期尽调 / 事中监控 / 事后风控

### 11. 数据来源
- 数据来源徽章列表
- 数据置信度标注

### 12. 免责声明

## 非上市公司 vs 上市公司数据源对比

| 数据维度 | 上市公司数据源 | 非上市公司替代数据源 |
|---------|-------------|-----------------|
| 财务数据 | SEC EDGAR, Yahoo Finance | Crunchbase融资额, 自报营收 |
| 股价 | Yahoo Finance, Alpha Vantage | N/A（无股价） |
| 贸易活动 | ImportYeti | ImportYeti（核心数据源） |
| 舆情 | 新闻API, Google News | Indeed, Glassdoor, 新闻搜索 |
| 供应链 | ImportYeti, 财报供应商披露 | ImportYeti（唯一来源） |
| 合规 | SEC EDGAR | FMCSA, CA SOS, SAM.gov |
| 竞争 | Yahoo Finance行业对比 | Tracxn, Crunchbase |
| 法律 | SEC诉讼披露 | PACER, Justia, CourtListener |

## 免费数据源清单

### 已接入（直接API/下载）
1. NY Fed GSCPI — 全球供应链压力指数
2. FRED — 宏观经济指标（7个系列）
3. World Bank LPI — 物流绩效指数
4. US Census Bureau — 国际贸易数据

### 已接入（浏览器爬取）
5. ImportYeti — 海关提单数据
6. Indeed — 员工评价
7. Glassdoor — 员工评价
8. Justia — 司法诉讼

### 可扩展接入
9. FMCSA SAFER — 运输公司安全记录
10. CA Secretary of State — 公司注册信息
11. SAM.gov — 政府合同和制裁名单
12. USPTO — 专利数据
13. EPA ECHO — 环保合规记录
14. OSHA — 职业安全记录
15. BBB — 商业信用评级
16. LinkedIn — 公司规模和员工信息

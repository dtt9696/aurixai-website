# Surpath报告数据真实性审查 + Mulerun数据源差异分析

## 一、Surpath报告数据真实性审查

### ✅ 真实接入的数据（有实际API/爬虫采集）
1. **ImportYeti提单数据** — 通过浏览器爬虫采集，数据真实
   - 年度提单量: 2022(35), 2023(27), 2024(24), 2025(3-5) ✅
   - 供应商列表和占比 ✅
   - 最近提单记录 ✅
   - HHI指数计算 ✅
2. **NY Fed GSCPI** — 通过Excel下载接入 ✅
3. **FRED经济数据** — 通过CSV API接入 ✅
4. **World Bank LPI** — 通过API接入 ✅
5. **US Census贸易数据** — 通过API接入 ✅
6. **Indeed员工评价** — 通过浏览器采集 ✅ (评分1.0/5.0)
7. **Justia司法诉讼** — 通过浏览器采集 ✅ (案号8:2023cv02080)

### ⚠️ 部分照搬/推测的数据（来自Mulerun报告或网络搜索，未直接API接入）
1. **Crunchbase/Tracxn融资数据** — 从搜索结果和Mulerun报告中获取，未直接API接入
   - 融资轮次、金额、投资人信息 — 来自网络搜索结果
   - 总融资额$15.65M — 与Mulerun报告一致
2. **Glassdoor评分** — 报告中写2.0/5.0，未实际爬取验证
3. **LinkedIn员工规模** — 报告中写11-50人，来自搜索结果
4. **CBInsights Mosaic Score** — Mulerun报告提到"30天下跌43点"，我的报告未使用此数据
5. **FMCSA DOT号** — 来自surpath_company_data.json中记录，但未实际查询验证
6. **California Secretary of State** — 列为数据源但未实际查询

### ❌ Mulerun报告中有但我未接入的数据源
1. **ImportKey** — 付费海关数据平台（Mulerun用于2025月度提单）
2. **CBInsights** — 付费（Mosaic Score等）
3. **Tracxn** — 付费（竞争对手数据）
4. **Surpath Official Website** — 未爬取官网内容

### 📊 我的报告vs Mulerun报告的关键数据差异
| 数据项 | Mulerun报告 | 我的报告 | 差异说明 |
|--------|------------|---------|---------|
| 综合评分 | 62 (MEDIUM-HIGH) | 81.9 (极高风险) | 评分体系不同 |
| 2025提单数 | 3票(截至10月) | 5票 | 我的数据包含更多月份 |
| 员工薪酬评分 | 1.5 | 1.0 | Mulerun可能综合了Glassdoor |
| 工作生活平衡 | 1.2 | 1.0 | 同上 |
| 职业发展 | 1.5 | 3.0 | 差异较大，Indeed原始数据为3.0 |
| 融资时间线 | 只有Series A一轮 | 3轮(Pre-A/Pre-A+/A) | 我的更详细 |
| 投资人 | 含招商创投 | 未含招商创投 | 需验证 |

## 二、Mulerun报告中所有数据源清单及接入状态

| 数据源 | 类型 | 费用 | 接入状态 | 备注 |
|--------|------|------|---------|------|
| ImportYeti | 提单 | 免费 | ✅ 已接入 | |
| ImportKey | 海关 | 付费 | ❌ 未接入 | 需付费订阅 |
| CBInsights | 商业智能 | 付费 | ❌ 未接入 | Mosaic Score等 |
| Tracxn | 创投数据 | 付费 | ❌ 未接入 | 竞争对手数据 |
| Crunchbase | 融资 | 部分免费 | ⚠️ 未直接API | 通过搜索获取 |
| Indeed | 员工评价 | 免费 | ✅ 已接入 | |
| Glassdoor | 员工评价 | 免费 | ⚠️ 部分 | 未深度爬取 |
| LinkedIn | 公司信息 | 免费 | ⚠️ 部分 | 未API接入 |
| Surpath Official | 官网 | 免费 | ❌ 未接入 | |

## 三、可新增的免费数据源（尚未接入）

1. **SEC EDGAR** — 上市公司财报（iRobot适用）✅ 免费
2. **USPTO** — 专利数据 ✅ 免费
3. **PACER/CourtListener** — 司法诉讼详情 ✅ 部分免费
4. **BBB (Better Business Bureau)** — 商业信用 ✅ 免费
5. **SAM.gov** — 政府合同和制裁名单 ✅ 免费
6. **OSHA** — 职业安全记录 ✅ 免费
7. **EPA ECHO** — 环保合规 ✅ 免费
8. **Yahoo Finance API** — 上市公司财务数据 ✅ 免费
9. **OpenCorporates** — 企业注册信息 ✅ 免费
10. **Google News** — 新闻舆情 ✅ 免费

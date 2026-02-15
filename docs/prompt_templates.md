# AURIX项目多窗口协作提示词模板

**版本**: 1.0
**日期**: 2026年2月15日
**作者**: Manus AI

---

## 1. 使用说明

本模板旨在帮助您在开启新的Manus对话窗口时，快速、高效地加载AURIX项目的完整上下文，实现多窗口协同工作。每个模板都遵循一个标准结构，确保Manus能够准确理解您的意图。

**使用步骤**：

1.  **开启新对话窗口**：在Manus中创建一个新的对话。
2.  **选择GitHub仓库**：在对话开始的GitHub集成选项中，**务必勾选 `dtt9696/aurixai-website` 仓库**。这是让Manus访问您代码的关键一步。
3.  **选择并复制模板**：根据您的任务目标，从下方选择最匹配的模板，复制其内容。
4.  **填写具体任务**：将模板中 `[具体任务]` 部分替换为您本次窗口需要完成的具体工作描述。
5.  **发送提示词**：将修改后的完整提示词发送给Manus。

---

## 2. 提示词模板库

### 模板一：通用项目上下文加载

**使用场景**：适用于任何与AURIX项目相关，但未被特定模板覆盖的任务，或作为所有任务的起点。

```text
# AURIX项目任务：通用上下文加载

**目标**：[在这里填写您的总体任务目标]

**第一步：加载项目上下文**
1.  我的项目代码和文档都在GitHub仓库 `dtt9696/aurixai-website` 中，请先完整克隆该仓库。
2.  请快速浏览仓库的整体结构，特别是 `src/`、`skills/` 和 `docs/` 目录，以了解项目概况。
3.  阅读 `docs/corporate_risk_system_tutorial.md` 和 `docs/agent_distribution_strategy.md`，这是我们项目的核心业务逻辑和战略规划。

**第二步：执行具体任务**
[在这里详细描述您需要Manus完成的具体任务，例如：“帮我研究一下如何将项目与钉钉机器人集成，并提供一个初步的技术方案。”]
```

---

### 模板二：前端开发与UI/UX

**使用场景**：所有与前端界面开发、修改、调试、设计相关的工作。

```text
# AURIX项目任务：前端开发

**目标**：[在这里填写您的前端开发目标，例如：“为风险报告页面增加一个新的数据可视化图表。”]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  本项目前端技术栈为 `Vite + React + TypeScript + TailwindCSS`，请重点关注 `src/` 目录下的前端代码。
3.  同时，请查阅 `skills/frontend-design/SKILL.md` 和 `skills/web-design-guidelines/SKILL.md`，在开发过程中遵循这些设计规范。

**第二步：执行具体任务**
[在这里详细描述您的前端任务，例如：“我需要在风险报告页面（假设路径为 src/pages/Report.tsx）的财务分析部分，使用Chart.js或D3.js添加一个展示公司近五年营收和净利润变化的柱状图和折线图的组合图表。”]
```

---

### 模板三：后端开发与API

**使用场景**：所有与后端API、数据库、服务器逻辑、MCP/A2A服务开发相关的工作。

```text
# AURIX项目任务：后端开发

**目标**：[在这里填写您的后端开发目标，例如：“开发一个新的API用于批量查询公司风险评分。”]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  本项目后端技术栈为 `TypeScript + Drizzle + MySQL/TiDB`，API服务位于 `src/server/` 目录下。
3.  请重点阅读 `docs/agent_distribution_strategy.md` 中关于MCP Server和A2A Agent的部分，我希望新的API也遵循这些标准。

**第二步：执行具体任务**
[在这里详细描述您的后端任务，例如：“请在 `src/server/api/routers/` 目录下新增一个API路由，支持通过POST请求接收一个公司列表（`string[]`），并并发调用 `riskAssessment` 服务，最终返回一个包含每个公司风险评分的JSON数组。”]
```

---

### 模板四：云服务部署

**使用场景**：将项目的前端或后端部署到阿里云、AWS、Vercel等云平台。

```text
# AURIX项目任务：云服务部署

**目标**：将AURIX项目前端部署到阿里云OSS并使用CDN加速。

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  这是一个 `Vite + React` 的前端项目，构建命令是 `pnpm build`，产物会生成在 `dist/` 目录下。

**第二步：执行部署任务**
1.  请指导我完成将前端应用部署到阿里云的完整流程。
2.  我倾向于使用 **OSS作为静态文件存储**，并配合 **CDN进行全球加速** 的方案。
3.  请提供详细的步骤，包括：
    *   如何安装和配置阿里云CLI。
    *   如何构建前端生产环境的静态文件。
    *   如何创建和配置OSS Bucket。
    *   如何将构建产物上传到OSS。
    *   如何配置CDN并绑定自定义域名。
4.  在需要我提供AccessKey或进行手动操作时，请明确提示。
```

---

### 模板五：文档撰写与策略更新

**使用场景**：撰写新的项目文档、更新现有文档或迭代商业/技术策略。

```text
# AURIX项目任务：文档与策略

**目标**：[在这里填写您的文档或策略目标，例如：“为新开发的批量查询API撰写一份API文档。”]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  我所有的文档都存放在 `docs/` 目录下，请先熟悉现有文档的风格和结构。

**第二步：执行具体任务**
[在这里详细描述您的文档任务，例如：“请在 `docs/` 目录下创建一个名为 `api_reference.md` 的新文件。为我刚刚开发的批量风险评分查询API撰写技术文档，需要包含：API路径、请求方法、请求体格式（含示例）、响应体格式（含示例）以及错误码说明。”]
```

---

### 模板六：Agent Skill开发与优化

**使用场景**：为AURIX项目创建新的Agent Skill，或优化现有的30个Skill。

```text
# AURIX项目任务：Agent Skill开发

**目标**：[在这里填写您的Skill开发目标，例如：“创建一个新的Skill，用于从Glassdoor上爬取企业评价信息。”]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  我所有的Skills都存放在 `skills/` 目录下，请先浏览现有Skills的结构，特别是 `SKILL.md` 的写法。
3.  我希望新的Skill也遵循类似的结构，包含清晰的描述、使用方法和代码示例。

**第二步：执行具体任务**
[在这里详细描述您的Skill开发任务，例如：“请在 `skills/` 目录下创建一个名为 `glassdoor-scraper` 的新Skill。这个Skill需要：
1.  定义一个函数，输入公司名称，输出该公司在Glassdoor上的总体评分、CEO支持率和推荐给朋友的比例。
2.  使用 `firecrawl-automation` 或其他爬虫Skill来实现数据获取。
3.  编写完整的 `SKILL.md` 文件，描述其功能和用法。”]
```


---

### 模板七：数据分析与风险建模

**使用场景**：使用已安装的数据分析类Skills（FRED、Alpha Vantage、scikit-learn、statsmodels等）进行数据获取、分析和建模。

```text
# AURIX项目任务：数据分析与风险建模

**目标**：[在这里填写您的数据分析目标，例如："对特斯拉进行一次完整的风险诊断分析。"]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  请阅读 `docs/corporate_risk_system_tutorial.md`，这是我们的风险诊断系统教程，包含了完整的分析流程和代码示例。
3.  请查阅 `skills/` 目录下的相关Skills，特别是 `fred-economic-data`、`alpha-vantage-automation`、`scikit-learn`、`statsmodels` 和 `scientific-visualization`。

**第二步：执行具体任务**
请对 [目标公司名称] 执行以下分析流程：
1.  使用 `fred-economic-data` 获取最新的美国宏观经济数据（GDP、CPI、失业率）作为背景。
2.  使用 `alpha-vantage-automation` 获取该公司的财务数据和股价历史。
3.  使用 `news-api-automation` 获取该公司近30天的新闻舆情。
4.  使用 `statsmodels` 或 `scikit-learn` 建立风险预测模型。
5.  使用 `scientific-visualization` 生成可视化图表。
6.  将所有分析结果整合为一份中文风险诊断报告，保存到 `docs/` 目录并推送到GitHub。
```

---

### 模板八：MCP Server / A2A Agent 开发

**使用场景**：将AURIX的能力封装为MCP Server或A2A Agent，实现Agent间互操作。

```text
# AURIX项目任务：MCP Server / A2A Agent 开发

**目标**：[在这里填写您的Agent互操作开发目标，例如："将AURIX的风险评分功能封装为一个MCP Server。"]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  请阅读 `docs/agent_distribution_strategy.md`，特别是第2节关于MCP和A2A技术标准的内容，其中包含了AgentCard的JSON模板和MCP Server的工具定义。
3.  请查阅 `src/server/services/riskAssessment.ts`，这是我们现有的风险评估服务核心逻辑。

**第二步：执行具体任务**
[在这里详细描述您的开发任务，例如："请基于现有的 `riskAssessment` 服务，创建一个符合MCP规范的Server。需要暴露以下工具：
1.  `get_company_risk_report` — 输入公司名称和国家，输出完整风险报告。
2.  `get_risk_score` — 输入公司名称，输出0-100的风险评分。
3.  `search_sanctions_list` — 输入实体名称，输出制裁名单匹配结果。
请将代码放在 `src/mcp-server/` 目录下，并提供本地测试方法。"]
```

---

### 模板九：微信小程序 / 公众号集成

**使用场景**：将AURIX的功能集成到微信小程序或公众号中，面向中国用户。

```text
# AURIX项目任务：微信生态集成

**目标**：[在这里填写您的微信集成目标，例如："开发一个微信小程序页面，让用户输入公司名称即可获取风险评分。"]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  我的产品需要同时支持PC端和移动端（H5/小程序），请确保所有界面设计采用移动优先（Mobile-First）的响应式方案。
3.  设计需要支持集成到微信公众号生态中。

**第二步：执行具体任务**
[在这里详细描述您的微信集成任务，例如："请帮我设计并开发一个微信小程序的风险查询页面，功能包括：
1.  一个搜索框，用户输入公司名称。
2.  搜索结果展示公司的风险评分（0-100分）、风险等级（低/中/高）和关键风险信号摘要。
3.  点击公司可查看完整的风险报告详情。
4.  界面风格与AURIX品牌一致，简洁专业。"]
```

---

### 模板十：竞品分析与市场研究

**使用场景**：对竞品、目标市场或行业趋势进行深入研究。

```text
# AURIX项目任务：竞品分析与市场研究

**目标**：[在这里填写您的研究目标，例如："分析全球企业风险管理SaaS市场的主要竞品。"]

**第一步：加载项目上下文**
1.  克隆我的GitHub仓库 `dtt9696/aurixai-website`。
2.  请阅读 `docs/agent_distribution_strategy.md`，了解AURIX的战略定位和目标用户群体。
3.  请使用 `deep-research`、`content-research-writer` 和 `research-lookup` 等Skills来进行深度研究。

**第二步：执行具体任务**
[在这里详细描述您的研究任务，例如："请对以下5家企业风险管理领域的竞品进行全面分析：
1.  邓白氏 (Dun & Bradstreet)
2.  Moody's Analytics
3.  Refinitiv (LSEG)
4.  Bureau van Dijk (Orbis)
5.  CreditSafe
分析维度包括：产品功能对比、定价策略、目标客户群、技术架构（是否有Agent/API能力）、市场份额。
最终生成一份对比报告，保存到 `docs/` 目录并推送到GitHub。"]
```

---

## 3. 仓库结构速查表

在使用上述模板时，以下仓库结构速查表可帮助您快速定位文件：

| 目录/文件 | 说明 |
|---|---|
| `src/` | 项目源代码（前端+后端） |
| `src/server/` | 后端API服务和业务逻辑 |
| `src/server/services/riskAssessment.ts` | 风险评估核心服务 |
| `src/server/services/emailService.ts` | 邮件通知服务 |
| `src/server/api/routers/` | API路由定义 |
| `src/scripts/dailyRiskCheck.ts` | 每日风险检查定时任务 |
| `skills/` | 30个Agent Skills（含SKILL.md和脚本） |
| `docs/corporate_risk_system_tutorial.md` | 风险诊断系统构建教程 |
| `docs/agent_distribution_strategy.md` | Agent生态分发与增长策略 |
| `docs/architecture.png` | 系统架构图 |
| `docs/dataflow.png` | 数据流图 |
| `docs/agent_ecosystem.png` | Agent生态分发架构图 |
| `docs/growth_flywheel.png` | 增长飞轮图 |
| `data/companies.json` | 公司数据 |
| `data/subscriptions.json` | 订阅数据 |
| `package.json` | 项目依赖配置 |
| `tsconfig.json` | TypeScript配置 |

---

## 4. 多窗口协作最佳实践

**规则一：始终选择GitHub仓库**。每次开启新对话窗口时，务必在GitHub集成选项中勾选 `dtt9696/aurixai-website`。这是所有模板能够生效的前提。

**规则二：任务完成后推送代码**。每个窗口完成工作后，提醒Manus将所有代码和文档变更推送到GitHub。可以在提示词末尾加上一句："任务完成后，请将所有变更提交并推送到GitHub仓库。"

**规则三：新窗口先拉取最新代码**。如果多个窗口同时工作，在开始新任务前，可以在提示词中加上："请先执行 `git pull` 确保代码是最新版本。"

**规则四：用分支管理并行开发**。如果多个窗口同时修改代码，建议在提示词中指定分支名，避免冲突。例如："请在 `feature/batch-api` 分支上进行开发，完成后创建Pull Request到main分支。"

**规则五：善用Skills**。如果您已在Manus技能菜单中导入了Skills，可以在提示词中直接提及Skill名称（如"请使用 `fred-economic-data` Skill获取数据"），Manus会自动读取并调用对应的Skill。

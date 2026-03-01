---
name: fund-advisor
description: |
  基金投资全流程顾问工具。整合盈米且慢MCP服务，提供基金数据查询、持仓管理、投资组合分析、财务规划、市场分析等专业金融服务。
  
  核心能力包括：
  - 基金信息查询（净值、业绩、持仓、经理等）
  - 投资组合诊断与优化建议
  - 资产配置方案规划
  - 家庭财务健康分析
  - 基金筛选与对比分析
  - 持仓管理与数据导入导出
  
  当用户询问基金投资、资产配置、财务规划、持仓分析等相关问题时激活此技能。
license: MIT
compatibility: 需要 mcporter CLI 和 qieman-mcp MCP 服务配置
metadata:
  author: fund-tools
  version: "1.0.0"
  mcp_servers: qieman-mcp
allowed-tools: Bash(mcporter:*) Bash(python:*) Bash(bash*) Read(*.csv) Write(*.csv) Read(*.md) Write(*.md)
---

# 基金顾投 Skill (fund-advisor)

整合盈米且慢MCP服务与本地持仓管理功能，提供专业的基金投资咨询服务。

## 触发场景

当用户需要：
- 查询基金信息（净值、业绩、持仓、经理等）
- 诊断分析投资组合
- 制定资产配置方案
- 进行家庭财务规划
- 筛选和对比基金产品
- 管理和导入持仓数据

## 能力范围

本技能整合且慢MCP的五大核心能力模块：

| 模块 | 能力说明 |
|------|----------|
| 金融数据 | 基金基础信息、净值历史、持仓明细、风险指标、业绩表现等 |
| 投研服务 | 基金筛选、基金诊断、回测分析、相关性分析、风险评估等 |
| 投顾服务 | 资产配置方案、投资规划、风险匹配、财务分析等 |
| 投顾内容 | 实时资讯解读、热点话题、基金经理观点、财经新闻等 |
| 通用服务 | 交易日查询、图表渲染、PDF生成、时间查询等 |

完整工具清单见 [references/mcp-tools-full.md](references/mcp-tools-full.md)

## 核心功能

### 1. 基金投资咨询

直接通过 MCP 服务查询任意基金信息，无需本地数据库：

```bash
# 查询单只基金详情
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["004137"]}' --output json

# 批量查询多只基金
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["004137","000001","110022"]}' --output json

# 查询基金持仓明细
mcporter call qieman-mcp.BatchGetFundsHolding --args '{"fundCodes":["004137"]}' --output json
```

### 2. 持仓管理

管理用户的基金持仓数据：

```bash
# 初始化环境（检查 mcporter 和 qieman-mcp 配置）
scripts/fund-cli.sh init

# 导入 CSV 持仓文件
scripts/fund-cli.sh import-csv tools/data/holdings.csv

# 查看持仓列表
scripts/fund-cli.sh holdings

# 查看投资组合总览
scripts/fund-cli.sh overview
```

### 3. 数据同步

从 MCP 服务同步基金数据到本地数据库：

```bash
# 同步所有数据（基础信息 + 持仓详情）
scripts/fund-cli.sh sync --all

# 仅同步基金基础信息
scripts/fund-cli.sh sync --info

# 仅同步基金持仓详情
scripts/fund-cli.sh sync --detail
```

### 4. 持仓分析

```bash
# 查看基金详情
scripts/fund-cli.sh detail 004137

# 查看管理人分布
scripts/fund-cli.sh managers

# 查看销售机构分布
scripts/fund-cli.sh agencies

# 显示所有统计
scripts/fund-cli.sh stats

# 导出统计报告
scripts/fund-cli.sh export --output report.txt
```

## MCP 工具整合

通过 `mcporter` CLI 调用 `qieman-mcp` 服务：

### BatchGetFundsDetail

批量获取基金详细信息，包括：
- 基金名称、代码、类型
- 净值、净值日期
- 基金规模、成立日期
- 基金经理、风险等级
- 资产配置比例（股票/债券/现金）
- 收益率指标

### BatchGetFundsHolding

批量获取基金持仓详情，包括：
- 报告日期
- 股票投资比例
- 债券投资比例
- 十大重仓股
- 十大重仓债

详细参数和返回格式见 [references/mcp-tools.md](references/mcp-tools.md)

## 数据模型

### FundHolding - 用户持仓

| 字段 | 说明 |
|------|------|
| fund_code | 基金代码 |
| fund_name | 基金名称 |
| holding_shares | 持有份额 |
| nav | 净值 |
| asset_value | 资产市值 |

### FundInfo - 基金信息

| 字段 | 说明 |
|------|------|
| fund_code | 基金代码 |
| fund_name | 基金名称 |
| fund_invest_type | 投资类型 |
| risk_5_level | 风险等级(1-5) |
| net_asset | 基金规模(亿) |
| manager_names | 基金经理 |

详见 [references/reference.md](references/reference.md)

## CSV 导入格式

支持中文列名，必需字段：

- 基金代码, 基金名称, 基金账户, 交易账户
- 持有份额, 份额日期, 基金净值, 净值日期
- 资产情况（结算币种）

示例文件见 [assets/sample.csv](assets/sample.csv)

详细规范见 [references/csv-format.md](references/csv-format.md)

## 使用示例

### 示例1：查询基金信息

用户："帮我查一下易方达蓝筹精选的信息"

执行：
```bash
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["005827"]}' --output json
```

### 示例2：分析用户持仓

用户："分析一下我的基金持仓"

执行：
```bash
scripts/fund-cli.sh overview
scripts/fund-cli.sh stats
```

### 示例3：导入新持仓

用户："我有个CSV文件要导入"

执行：
```bash
scripts/fund-cli.sh import-csv /path/to/holdings.csv
```

### 示例4：同步最新数据

用户："更新一下基金数据"

执行：
```bash
scripts/fund-cli.sh sync --all
```

## 注意事项

1. **环境要求**：需要先运行 `init` 命令确保 mcporter 和 qieman-mcp 配置正确
2. **批量限制**：MCP 服务单次最多查询 10 只基金
3. **数据时效**：基金净值和持仓数据有延迟，注意查看净值日期
4. **CSV 编码**：支持 utf-8, utf-8-sig, gbk, gb18030 编码
5. **目录结构**：工程代码位于 `tools/` 目录下

## 高级功能场景

### 场景1：投资组合诊断分析

用户持有基金组合，需要诊断分析：

```bash
# 1. 查询基金信息
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes":["005094","320007","001003","040046"]}' \
  --output json

# 2. 基金相关性分析
mcporter call qieman-mcp.GetFundsCorrelation \
  --args '{"fundCodes":["005094","320007","001003","040046"]}' \
  --output json

# 3. 组合回测分析
mcporter call qieman-mcp.GetFundsBackTest \
  --args '{"fundCodes":["005094","320007","001003","040046"],"weights":[0.47,0.23,0.17,0.13]}' \
  --output json
```

### 场景2：资产配置方案规划

用户希望制定投资方案：

```bash
# 1. 获取资产配置方案
mcporter call qieman-mcp.GetAssetAllocationPlan \
  --args '{"expectedAnnualReturn":0.08}' \
  --output json

# 2. 蒙特卡洛模拟
mcporter call qieman-mcp.MonteCarloSimulate \
  --args '{"weights":[0.3,0.3,0.2,0.2],"years":3}' \
  --output json
```

### 场景3：家庭财务分析

用户需要进行财务规划：

```bash
# 1. 家庭成员分析
mcporter call qieman-mcp.AnalyzeFamilyMembers \
  --args '{"members":[{"role":"本人","age":30},{"role":"配偶","age":28},{"role":"子女","age":5}]}' \
  --output json

# 2. 资产负债分析
mcporter call qieman-mcp.AnalyzeAssetLiability \
  --args '{"totalAsset":5000000,"totalLiability":2000000}' \
  --output json

# 3. 现金流分析
mcporter call qieman-mcp.AnalyzeCashFlow \
  --args '{"currentAsset":500000,"expectedReturn":0.08}' \
  --output json
```

### 场景4：基金筛选与对比

用户希望筛选符合特定条件的基金：

```bash
# 1. 基金搜索
mcporter call qieman-mcp.SearchFunds \
  --args '{"keyword":"红利","sortBy":"oneYearReturn","limit":10}' \
  --output json

# 2. 基金业绩对比
mcporter call qieman-mcp.GetBatchFundPerformance \
  --args '{"fundCodes":["005827","000001","110022"]}' \
  --output json

# 3. 基金诊断
mcporter call qieman-mcp.GetFundDiagnosis \
  --args '{"fundCode":"005827"}' \
  --output json
```

### 场景5：市场分析

用户希望了解市场情况：

```bash
# 1. 市场温度计
mcporter call qieman-mcp.GetLatestQuotations \
  --args '{"date":"2025-03-01"}' \
  --output json

# 2. 热点话题
mcporter call qieman-mcp.SearchHotTopic \
  --args '{"limit":10}' \
  --output json

# 3. 基金经理观点
mcporter call qieman-mcp.SearchManagerViewpoint \
  --args '{"industry":"科技","limit":5}' \
  --output json
```

## 报告生成

支持生成可视化报告：

```bash
# ECharts图表渲染
mcporter call qieman-mcp.RenderEchart \
  --args '{"option":{...}}' \
  --output json

# HTML转PDF
mcporter call qieman-mcp.RenderHtmlToPdf \
  --args '{"html":"..."}' \
  --output json
```

## 环境配置

### 1. 安装 mcporter

```bash
# NPM
npm install -g mcporter

# 或 Homebrew
brew tap steipete/tap
brew install mcporter
```

### 2. 配置 qieman-mcp

编辑 `~/.mcporter/mcporter.json`：

```json
{
  "mcpServers": {
    "qieman-mcp": {
      "baseUrl": "https://stargate.yingmi.com/mcp/sse?apiKey=YOUR_API_KEY",
      "description": "基金投资工具包"
    }
  }
}
```

### 3. 获取 API Key

访问 [且慢MCP官网](https://qieman.com/mcp/account) 申请免费 API Key。

## 参考文档

- [MCP工具完整清单](references/mcp-tools-full.md)
- [MCP工具基础文档](references/mcp-tools.md)
- [CSV导入格式规范](references/csv-format.md)
- [项目架构说明](references/REFERENCE.md)
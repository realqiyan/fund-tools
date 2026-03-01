# Fund Advisor - 基金投资顾问工具

整合盈米且慢 MCP 服务与本地持仓管理，提供专业的基金投资咨询服务。

## 核心能力

| 模块 | 能力说明 |
|------|----------|
| 金融数据 | 基金基础信息、净值历史、持仓明细、风险指标、业绩表现等 |
| 投研服务 | 基金筛选、基金诊断、回测分析、相关性分析、风险评估等 |
| 投顾服务 | 资产配置方案、投资规划、风险匹配、财务分析等 |
| 持仓管理 | CSV导入、数据同步、统计分析、报告导出 |

## 快速开始

```bash
# 初始化环境
bash scripts/fund-cli.sh init

# 导入持仓
bash scripts/fund-cli.sh import-csv tools/data/holdings.csv

# 查看总览
bash scripts/fund-cli.sh overview

# 同步数据
bash scripts/fund-cli.sh sync --all
```

## 常用命令

### 持仓管理

```bash
bash scripts/fund-cli.sh holdings          # 持仓列表
bash scripts/fund-cli.sh overview          # 投资组合总览
bash scripts/fund-cli.sh detail 004137     # 基金详情
bash scripts/fund-cli.sh stats             # 全部统计
```

### 数据同步

```bash
bash scripts/fund-cli.sh sync --info       # 同步基金信息
bash scripts/fund-cli.sh sync --detail    # 同步持仓详情
bash scripts/fund-cli.sh sync --all       # 同步全部
```

### MCP 查询

```bash
# 查询基金详情
mcporter call qieman-mcp.BatchGetFundsDetail --args '{"fundCodes":["004137"]}' --output json

# 查询持仓明细
mcporter call qieman-mcp.BatchGetFundsHolding --args '{"fundCodes":["004137"]}' --output json

# 基金筛选
mcporter call qieman-mcp.SearchFunds --args '{"keyword":"红利","limit":10}' --output json

# 相关性分析
mcporter call qieman-mcp.GetFundsCorrelation --args '{"fundCodes":["005094","320007"]}' --output json
```

## 环境要求

- Python 3.10+
- mcporter CLI
- qieman-mcp API Key ([申请地址](https://qieman.com/mcp/account))

配置文件 `~/.mcporter/mcporter.json`:

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

## 参考文档

- [MCP工具完整清单](references/mcp-tools-full.md)
- [MCP工具基础文档](references/mcp-tools.md)
- [CSV导入格式规范](references/csv-format.md)
- [项目架构说明](references/REFERENCE.md)

## 许可证

MIT License
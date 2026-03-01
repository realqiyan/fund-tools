# Fund Tools - 基金持仓管理系统

一个基于 Python CLI 的基金持仓管理工具，支持 CSV 导入、MCP 数据同步和统计分析。

## 功能特性

- **CSV 导入**：从 CSV 文件导入基金持仓数据
- **MCP 数据同步**：通过 qieman-mcp 服务同步基金基础信息和持仓详情
- **统计分析**：支持多种维度统计分析（投资类型、管理人、销售机构、币种等）
- **丰富的 CLI 命令**：查看持仓、基金详情、投资组合总览等

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd fund-tools

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 环境准备

本工具依赖 [mcporter](https://github.com/anthropics/mcporter) 和 qieman-mcp 服务。

```bash
# 初始化环境（检查并配置 mcporter 和 qieman-mcp）
python main.py init

# 仅检查环境状态
python main.py init --check
```

> **注意**：qieman-mcp 的 API Key 需要自行申请并配置到 `~/.mcporter/mcporter.json`。

## 使用方法

### 数据导入

```bash
# 从 CSV 文件导入持仓数据
python main.py import-csv data/sample.csv
```

CSV 文件需要包含以下列（支持中文列名）：
- 基金代码、基金名称、基金账户、交易账户
- 持有份额、份额日期、基金净值、净值日期
- 资产情况（结算币种）、结算币种、分红方式

### 持仓查看

```bash
# 查看持仓列表
python main.py holdings

# 按基金账户筛选
python main.py holdings --account <基金账户>

# 查看单只基金详情
python main.py detail <基金代码>

# 查看投资组合总览
python main.py overview

# 查看基金账户列表
python main.py accounts
```

### 数据同步

```bash
# 同步基金基础信息
python main.py sync --info

# 同步基金持仓详情
python main.py sync --detail

# 同步所有信息
python main.py sync --all
```

### 统计分析

```bash
# 显示所有统计视图
python main.py stats

# 投资类型分布
python main.py invest-type

# 币种分布
python main.py currency

# 基金管理人分布
python main.py managers

# 销售机构分布
python main.py agencies

# 导出统计报告
python main.py export --output report.txt
```

### 持仓管理

```bash
# 手动添加持仓记录
python main.py add \
  --fund-code <基金代码> \
  --fund-name <基金名称> \
  --fund-account <基金账户> \
  --trade-account <交易账户> \
  --shares <持有份额> \
  --nav <净值> \
  --asset-value <资产价值>

# 删除持仓记录
python main.py delete \
  --fund-account <基金账户> \
  --trade-account <交易账户> \
  --fund-code <基金代码>
```

## 项目结构

```
fund-tools/
├── main.py              # CLI 入口
├── src/
│   ├── models.py        # 数据模型定义
│   ├── database.py      # SQLite 数据库操作
│   ├── csv_importer.py  # CSV 导入功能
│   ├── mcp_service.py   # MCP 服务集成
│   ├── statistics.py    # 统计视图
│   └── env_checker.py   # 环境检查
├── data/
│   └── sample.csv       # 示例数据
├── tests/               # 测试目录
├── requirements.txt     # 依赖列表
└── pyproject.toml       # 项目配置
```

## 数据库设计

系统使用 SQLite 数据库，包含三个主要表：

- **fund_holdings**：用户持仓记录
- **fund_info**：基金基础信息（投资类型、风险等级、基金经理等）
- **fund_holdings_detail**：基金持仓详情（重仓股、重仓债等）

## 依赖

- Python >= 3.10
- click >= 8.1.0
- rich >= 13.0.0
- python-dateutil >= 2.8.0

## License

MIT
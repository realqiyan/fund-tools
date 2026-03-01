#!/usr/bin/env python3
"""
基金持仓管理系统 - CLI主程序
"""
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

from src.database import Database
from src.csv_importer import CSVImporter
from src.mcp_service import MCPService
from src.statistics import Statistics
from src.env_checker import EnvChecker


console = Console()


@click.group()
@click.option("--db", default="fund_portfolio.db", help="数据库文件路径")
@click.pass_context
def cli(ctx, db):
    """基金持仓管理系统 - 管理您的基金投资组合"""
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db
    ctx.obj["database"] = Database(db)


# ==================== 环境初始化命令 ====================

@cli.command()
@click.option("--check", is_flag=True, help="仅检查环境状态")
@click.option("--force", is_flag=True, help="强制重新配置")
@click.pass_context
def init(ctx, check, force):
    """初始化环境（检查并配置mcporter和qieman-mcp）"""
    env_checker = EnvChecker()

    if check:
        results = env_checker.check_environment()
    else:
        results = env_checker.init_environment(force)

    console.print(env_checker.get_report())

    if results.get("status") == "error":
        sys.exit(1)


# ==================== 数据导入命令 ====================

@cli.command()
@click.argument("csv_path", type=click.Path(exists=True))
@click.pass_context
def import_csv(ctx, csv_path):
    """从CSV文件导入持仓数据"""
    database = ctx.obj["database"]
    importer = CSVImporter(database)

    console.print(f"[cyan]正在导入: {csv_path}[/]")

    # 验证CSV
    is_valid, errors = importer.validate_csv(csv_path)
    if not is_valid:
        for error in errors:
            console.print(f"[red]错误: {error}[/]")
        return

    # 导入数据
    success, fail, errors = importer.import_from_csv(csv_path)

    console.print(f"\n[green]导入完成![/]")
    console.print(f"  成功: {success} 条")
    if fail > 0:
        console.print(f"  失败: {fail} 条")
        for error in errors[:10]:  # 只显示前10条错误
            console.print(f"  [red]{error}[/]")


# ==================== 持仓管理命令 ====================

@cli.command()
@click.option("--account", help="按基金账户筛选")
@click.pass_context
def holdings(ctx, account):
    """查看持仓列表"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_holdings_list(account)


@cli.command()
@click.argument("fund_code")
@click.pass_context
def detail(ctx, fund_code):
    """查看基金详情"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_fund_detail(fund_code)


@cli.command()
@click.pass_context
def overview(ctx):
    """显示投资组合总览"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_overview()


@cli.command()
@click.pass_context
def currency(ctx):
    """显示币种分布"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_currency_distribution()


@cli.command()
@click.option("--limit", default=10, help="显示数量")
@click.pass_context
def managers(ctx, limit):
    """显示基金管理人分布"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_manager_distribution(limit)


@cli.command()
@click.option("--limit", default=10, help="显示数量")
@click.pass_context
def agencies(ctx, limit):
    """显示销售机构分布"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_sales_agency_distribution(limit)


@cli.command()
@click.pass_context
def invest_type(ctx):
    """显示投资类型分布"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_invest_type_distribution()


@cli.command()
@click.pass_context
def accounts(ctx):
    """显示基金账户列表"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_fund_accounts()


# ==================== 数据同步命令 ====================

@cli.command()
@click.option("--info", is_flag=True, help="同步基金基础信息")
@click.option("--detail", is_flag=True, help="同步基金持仓详情")
@click.option("--all", "sync_all", is_flag=True, help="同步所有信息")
@click.pass_context
def sync(ctx, info, detail, sync_all):
    """同步基金数据（从MCP服务获取）"""
    database = ctx.obj["database"]

    # 先检查环境
    env_checker = EnvChecker()
    if not env_checker.check_mcporter_installed():
        console.print("[red]错误: mcporter未安装，请先运行 'fund-tools init' 初始化环境[/]")
        return

    if not env_checker.check_qieman_mcp_configured():
        console.print("[yellow]qieman-mcp未配置，正在自动配置...[/]")
        env_checker.setup_qieman_mcp_config()

    mcp = MCPService()

    # 获取需要同步的基金代码
    fund_codes = database.get_fund_codes_from_holdings()

    if not fund_codes:
        console.print("[yellow]没有找到持仓基金代码，请先导入持仓数据[/]")
        return

    console.print(f"[cyan]发现 {len(fund_codes)} 只基金需要同步[/]")

    if sync_all or info:
        # 同步基金基础信息
        console.print("\n[cyan]正在同步基金基础信息...[/]")
        missing_codes = database.get_missing_fund_info_codes()
        codes_to_sync = missing_codes if missing_codes else fund_codes
        console.print(f"  需要同步: {len(codes_to_sync)} 只")

        if codes_to_sync:
            success, fail = mcp.sync_fund_info(codes_to_sync, database)
            console.print(f"  [green]成功: {success}[/], [red]失败: {fail}[/]")

    if sync_all or detail:
        # 同步基金持仓详情
        console.print("\n[cyan]正在同步基金持仓详情...[/]")
        missing_codes = database.get_missing_fund_detail_codes()
        codes_to_sync = missing_codes if missing_codes else fund_codes
        console.print(f"  需要同步: {len(codes_to_sync)} 只")

        if codes_to_sync:
            success, fail = mcp.sync_fund_holdings(codes_to_sync, database)
            console.print(f"  [green]成功: {success}[/], [red]失败: {fail}[/]")

    if not info and not detail and not sync_all:
        console.print("[yellow]请指定同步类型: --info, --detail, 或 --all[/]")


# ==================== 统计和导出命令 ====================

@cli.command()
@click.pass_context
def stats(ctx):
    """显示所有统计视图"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.show_all_stats()


@cli.command()
@click.option("--output", default="report.txt", help="输出文件路径")
@click.pass_context
def export(ctx, output):
    """导出统计报告"""
    database = ctx.obj["database"]
    stats = Statistics(database)
    stats.export_report(output)


# ==================== 持仓记录管理命令 ====================

@cli.command()
@click.option("--fund-code", required=True, help="基金代码")
@click.option("--fund-name", required=True, help="基金名称")
@click.option("--fund-account", required=True, help="基金账户")
@click.option("--trade-account", required=True, help="交易账户")
@click.option("--shares", required=True, type=float, help="持有份额")
@click.option("--nav", required=True, type=float, help="基金净值")
@click.option("--asset-value", required=True, type=float, help="资产价值")
@click.pass_context
def add(ctx, fund_code, fund_name, fund_account, trade_account, shares, nav, asset_value):
    """手动添加持仓记录"""
    from datetime import date
    from src.models import FundHolding, FundType

    database = ctx.obj["database"]

    holding = FundHolding(
        fund_code=fund_code,
        fund_name=fund_name,
        fund_account=fund_account,
        trade_account=trade_account,
        holding_shares=shares,
        nav=nav,
        asset_value=asset_value,
        share_date=date.today(),
        nav_date=date.today(),
        share_class="",
        fund_manager="",
        sales_agency="",
        settlement_currency="人民币",
        dividend_method="红利转投",
        fund_type=FundType.PUBLIC_FUND
    )

    database.upsert_fund_holding(holding)
    console.print(f"[green]成功添加/更新持仓: {fund_code}[/]")


@cli.command()
@click.option("--fund-account", required=True, help="基金账户")
@click.option("--trade-account", required=True, help="交易账户")
@click.option("--fund-code", required=True, help="基金代码")
@click.pass_context
def delete(ctx, fund_account, trade_account, fund_code):
    """删除持仓记录"""
    database = ctx.obj["database"]

    if Confirm.ask(f"确认删除 {fund_code} 的持仓记录?"):
        if database.delete_fund_holding(fund_account, trade_account, fund_code):
            console.print(f"[green]已删除: {fund_code}[/]")
        else:
            console.print(f"[red]删除失败: 未找到记录[/]")


if __name__ == "__main__":
    cli(obj={})
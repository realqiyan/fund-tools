"""
基金持仓管理系统 - 统计视图功能
"""
from typing import Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.database import Database
from src.models import FundHolding, GroupColumn


class Statistics:
    """统计视图类"""

    def __init__(self, database: Database):
        self.database = database
        self.console = Console()

    def show_group_statistics(self, column: GroupColumn):
        """显示分组统计

        Args:
            column: 分组列名（GroupColumn 枚举）
        """
        data = self.database.get_group_statistics(column.value)

        if not data:
            self.console.print(f"[yellow]暂无{GroupColumn.get_display_name(column)}分布数据[/]")
            return

        display_name = GroupColumn.get_display_name(column)
        table = Table(title=f"{display_name}分布", show_header=True, header_style="bold cyan")
        table.add_column(display_name, style="cyan")
        table.add_column("持仓数", justify="right", style="blue")
        table.add_column("资产价值", justify="right", style="green")
        table.add_column("占比", justify="right", style="yellow")

        total = sum(item['total'] or 0 for item in data)

        for item in data:
            item_total = item['total'] or 0
            percentage = (item_total / total * 100) if total > 0 else 0
            table.add_row(
                str(item['name'] or "未知"),
                str(item['count']),
                f"¥{item_total:,.2f}",
                f"{percentage:.2f}%"
            )

        self.console.print(table)

    def show_query_result(self, column: GroupColumn, value: str):
        """显示查询结果（展示所有导入字段）

        Args:
            column: 查询列名（GroupColumn 枚举）
            value: 查询值
        """
        holdings = self.database.query_holdings(column.value, value)

        if not holdings:
            self.console.print(f"[yellow]未找到匹配 '{value}' 的持仓记录[/]")
            return

        display_name = GroupColumn.get_display_name(column)
        table = Table(
            title=f"查询结果: {display_name} 包含 '{value}' (共{len(holdings)}条)",
            show_header=True,
            header_style="bold cyan",
            expand=False,
        )

        # 添加所有导入字段列
        table.add_column("基金代码", style="cyan", width=8)
        table.add_column("基金名称", style="white", width=20)
        table.add_column("份额类别", style="blue", width=8)
        table.add_column("基金管理人", style="magenta", width=12)
        table.add_column("基金账户", style="green", width=12)
        table.add_column("交易账户", style="yellow", width=12)
        table.add_column("销售机构", style="blue", width=12)
        table.add_column("持有份额", justify="right", style="green", width=12)
        table.add_column("份额日期", justify="center", style="white", width=10)
        table.add_column("净值", justify="right", style="yellow", width=8)
        table.add_column("净值日期", justify="center", style="white", width=10)
        table.add_column("资产价值", justify="right", style="green", width=12)
        table.add_column("结算币种", justify="center", style="blue", width=8)
        table.add_column("分红方式", style="cyan", width=8)

        # 限制显示条数以保证性能
        max_display = 30
        for holding in holdings[:max_display]:
            table.add_row(
                holding.fund_code,
                holding.fund_name[:20] if len(holding.fund_name) > 20 else holding.fund_name,
                holding.share_class[:8] if holding.share_class and len(holding.share_class) > 8 else (holding.share_class or ""),
                holding.fund_manager[:12] if holding.fund_manager and len(holding.fund_manager) > 12 else (holding.fund_manager or ""),
                holding.fund_account[:12] if holding.fund_account and len(holding.fund_account) > 12 else (holding.fund_account or ""),
                holding.trade_account[:12] if holding.trade_account and len(holding.trade_account) > 12 else (holding.trade_account or ""),
                holding.sales_agency[:12] if holding.sales_agency and len(holding.sales_agency) > 12 else (holding.sales_agency or ""),
                f"{holding.holding_shares:,.2f}",
                str(holding.share_date) if holding.share_date else "",
                f"{holding.nav:.4f}" if holding.nav else "",
                str(holding.nav_date) if holding.nav_date else "",
                f"¥{holding.asset_value:,.2f}",
                holding.settlement_currency or "",
                holding.dividend_method[:8] if holding.dividend_method and len(holding.dividend_method) > 8 else (holding.dividend_method or ""),
            )

        self.console.print(table)

        if len(holdings) > max_display:
            self.console.print(f"[dim]... 还有 {len(holdings) - max_display} 条记录未显示[/]")

        # 显示汇总信息
        total_value = sum(h.asset_value for h in holdings)
        self.console.print(f"\n[green]总计: {len(holdings)} 条记录, 资产价值: ¥{total_value:,.2f}[/]")

    def _get_column_value(self, holding: FundHolding, column: GroupColumn) -> Any:
        """获取持仓记录中指定列的值"""
        if column == GroupColumn.FUND_CODE:
            return holding.fund_code
        elif column == GroupColumn.FUND_NAME:
            return holding.fund_name
        elif column == GroupColumn.FUND_MANAGER:
            return holding.fund_manager
        elif column == GroupColumn.FUND_ACCOUNT:
            return holding.fund_account
        elif column == GroupColumn.TRADE_ACCOUNT:
            return holding.trade_account
        elif column == GroupColumn.SALES_AGENCY:
            return holding.sales_agency
        elif column == GroupColumn.CURRENCY:
            return holding.settlement_currency
        elif column == GroupColumn.DIVIDEND_METHOD:
            return holding.dividend_method
        elif column == GroupColumn.INVEST_TYPE:
            # 投资类型需要从 fund_info 获取
            fund_info = self.database.get_fund_info(holding.fund_code)
            return fund_info.fund_invest_type if fund_info else "未知"
        return None

    def show_fund_detail(self, fund_code: str):
        """显示单个基金的详细信息"""
        # 获取基础信息
        fund_info = self.database.get_fund_info(fund_code)
        # 获取持仓详情
        holdings_detail = self.database.get_fund_holdings_detail(fund_code)
        # 获取用户持仓
        user_holdings = []
        all_holdings = self.database.get_fund_holdings()
        for h in all_holdings:
            if h.fund_code == fund_code:
                user_holdings.append(h)

        if not fund_info and not user_holdings:
            self.console.print(f"[red]未找到基金: {fund_code}[/]")
            return

        # 显示基金基础信息
        if fund_info:
            info_text = f"""
[bold cyan]基金代码:[/] {fund_info.fund_code}
[bold cyan]基金名称:[/] {fund_info.fund_name}
[bold cyan]投资类型:[/] {fund_info.fund_invest_type or '未知'}
[bold cyan]风险等级:[/] {fund_info.risk_5_level or '未知'}
[bold cyan]最新净值:[/] {fund_info.nav or '未知'} ({fund_info.nav_date or '未知'})
[bold cyan]基金规模:[/] {fund_info.net_asset}亿 ({fund_info.fund_invest_type or ''})
[bold cyan]成立日期:[/] {fund_info.setup_date or '未知'}
"""
            if fund_info.yearly_roe:
                info_text += f"[bold cyan]七日年化:[/] {fund_info.yearly_roe}%\n"
            if fund_info.one_year_return:
                info_text += f"[bold cyan]近一年收益:[/] {fund_info.one_year_return}%\n"
            if fund_info.manager_names:
                info_text += f"[bold cyan]基金经理:[/] {fund_info.manager_names}\n"

            self.console.print(Panel(info_text, title="[bold green]基金基础信息[/]", border_style="green"))

        # 显示用户持仓
        if user_holdings:
            table = Table(title="我的持仓", show_header=True, header_style="bold cyan")
            table.add_column("基金账户", style="cyan")
            table.add_column("交易账户", style="blue")
            table.add_column("持有份额", justify="right", style="green")
            table.add_column("资产价值", justify="right", style="yellow")

            for h in user_holdings:
                table.add_row(
                    h.fund_account,
                    h.trade_account,
                    f"{h.holding_shares:,.2f}",
                    f"¥{h.asset_value:,.2f}"
                )

            self.console.print(table)

        # 显示持仓详情
        if holdings_detail:
            detail_text = f"\n[bold cyan]报告日期:[/] {holdings_detail.report_date or '未知'}\n"
            if holdings_detail.stock_invest_ratio:
                detail_text += f"[bold cyan]股票仓位:[/] {holdings_detail.stock_invest_ratio}%\n"
            if holdings_detail.bond_invest_ratio:
                detail_text += f"[bold cyan]债券仓位:[/] {holdings_detail.bond_invest_ratio}%\n"

            self.console.print(Panel(detail_text, title="[bold green]持仓分析[/]", border_style="green"))

            # 显示十大重仓股
            if holdings_detail.top_stocks:
                stock_table = Table(title="十大重仓股", show_header=True, header_style="bold cyan")
                stock_table.add_column("代码", style="cyan", width=12)
                stock_table.add_column("名称", style="white", width=20)
                stock_table.add_column("占比", justify="right", style="green")
                stock_table.add_column("金额(亿)", justify="right", style="yellow")

                for stock in holdings_detail.top_stocks[:10]:
                    stock_table.add_row(
                        stock.stock_code,
                        stock.stock_name,
                        f"{stock.holding_ratio}%" if stock.holding_ratio else "-",
                        f"{stock.holding_amount}" if stock.holding_amount else "-"
                    )

                self.console.print(stock_table)

            # 显示十大重仓债
            if holdings_detail.top_bonds:
                bond_table = Table(title="十大重仓债", show_header=True, header_style="bold cyan")
                bond_table.add_column("代码", style="cyan", width=12)
                bond_table.add_column("名称", style="white", width=20)
                bond_table.add_column("占比", justify="right", style="green")
                bond_table.add_column("金额(亿)", justify="right", style="yellow")

                for bond in holdings_detail.top_bonds[:10]:
                    bond_table.add_row(
                        bond.bond_code,
                        bond.bond_name,
                        f"{bond.holding_ratio}%" if bond.holding_ratio else "-",
                        f"{bond.holding_amount}" if bond.holding_amount else "-"
                    )

                self.console.print(bond_table)
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from costslash.models import ScanReport

# Ensure safe UTF-8 terminal encoding on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(force_terminal=True)


def render_banner():
    """Renders the CostSlash CLI header banner."""
    banner = Text()
    banner.append("[+] CostSlash ", style="bold green")
    banner.append("v0.1.0", style="dim white")
    banner.append(" - Instant AWS Cloud Cost & Waste Optimization Scanner", style="italic white")
    console.print(Panel(banner, border_style="green", box=box.ROUNDED))


def render_scan_report(report: ScanReport, show_commands: bool = False):
    """Renders the complete visual scan report in terminal."""
    # 1. Executive Summary Panel
    summary_table = Table(show_header=False, box=None, padding=(0, 1))
    summary_table.add_row("[bold white]AWS Account:[/]", f"[cyan]{report.account_id}[/]")
    summary_table.add_row("[bold white]Region:[/]", f"[yellow]{report.region}[/]")
    summary_table.add_row("[bold white]Scan Timestamp:[/]", f"[dim]{report.scan_timestamp}[/]")
    summary_table.add_row("[bold white]Total Items Found:[/]", f"[bold]{len(report.items)} waste opportunities[/]")
    summary_table.add_row(
        "[bold white]Monthly Savings:[/]",
        f"[bold green]${report.total_monthly_savings:,.2f} / month[/]",
    )
    summary_table.add_row(
        "[bold white]Yearly Savings:[/]",
        f"[bold green,underline]${report.total_yearly_savings:,.2f} / year[/]",
    )

    console.print(
        Panel(
            summary_table,
            title="[bold green]💰 Executive Savings Summary[/]",
            border_style="green",
            box=box.ROUNDED,
        )
    )

    # 2. Detailed Findings Table
    table = Table(
        title="[bold]Detected Waste & Optimization Levers[/]",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Category", style="magenta", width=24)
    table.add_column("Resource ID / Name", style="cyan", width=26)
    table.add_column("Details", style="white")
    table.add_column("Monthly Savings", justify="right", style="bold green", width=16)

    for item in report.items:
        table.add_row(
            item.category.value,
            f"[bold]{item.resource_id}[/]\n[dim]{item.resource_name}[/]",
            item.details,
            f"${item.monthly_waste_usd:,.2f}/mo",
        )

    console.print(table)

    # 3. Category Breakdown
    cat_table = Table(title="[bold]Savings Breakdown by Category[/]", box=box.SIMPLE)
    cat_table.add_column("Category", style="bold white")
    cat_table.add_column("Monthly Savings", justify="right", style="green")
    cat_table.add_column("Yearly Impact", justify="right", style="bold green")

    for cat, amount in report.waste_by_category.items():
        cat_table.add_row(cat, f"${amount:,.2f}/mo", f"${amount * 12:,.2f}/yr")

    console.print(cat_table)

    # 4. CLI Remediation Commands if requested
    if show_commands:
        console.print("\n[bold yellow]🛠️ 1-Click AWS CLI Remediation Commands:[/]")
        for idx, item in enumerate(report.items, 1):
            if item.cli_command_fix:
                console.print(f"[dim]{idx}.[/] [cyan]{item.cli_command_fix}[/]")


def render_success(title: str, msg: str):
    """Renders a success confirmation box."""
    console.print(Panel(f"[bold green]{title}[/]\n{msg}", border_style="green", box=box.ROUNDED))

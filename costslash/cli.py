import time
import typer
from typing import Optional
from costslash.collectors.mock_collector import run_mock_scan
from costslash.collectors.aws_collector import run_live_aws_scan
from costslash.ui import (
    console,
    render_banner,
    render_scan_report,
    render_success,
)

app = typer.Typer(
    name="costslash",
    help="Instant AWS Cloud Cost & Waste Optimization Scanner",
    no_args_is_help=True,
)


@app.command(name="scan")
def scan(
    region: str = typer.Option(
        "us-east-1", "--region", "-r", help="AWS region to scan"
    ),
    all_regions: bool = typer.Option(
        False, "--all-regions", "-a", help="Scan ALL active AWS regions in parallel"
    ),
    live: bool = typer.Option(
        False, "--live", "-l", help="Perform live scan using active AWS credentials"
    ),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS CLI profile name (for live scan)"
    ),
    fix: bool = typer.Option(
        False, "--fix", "-f", help="Print exact AWS CLI commands to remediate and clean up waste"
    ),
    export_json: Optional[str] = typer.Option(
        None, "--export-json", "-o", help="Export report to JSON file path"
    ),
):
    """Scan an AWS account for unattached disks, idle NAT gateways, and unused IPs."""
    render_banner()

    target_label = "ALL AWS regions" if all_regions else f"region '{region}'"
    status_msg = (
        f"[bold cyan]Scanning live AWS account across {target_label} in parallel..."
        if live
        else f"[bold green]Running instant diagnostic scan on test AWS account ({target_label})..."
    )

    with console.status(status_msg, spinner="dots"):
        time.sleep(0.8)
        if live:
            try:
                report = run_live_aws_scan(
                    region=region,
                    all_regions=all_regions,
                    profile=profile,
                )
            except Exception as e:
                console.print(f"[bold red]Live Scan Error:[/] {e}")
                console.print("[yellow]Tip: Run with mock data using: [bold]costslash scan[/]")
                raise typer.Exit(code=1)
        else:
            report = run_mock_scan(region=region)

    render_scan_report(report, show_commands=fix)

    if export_json:
        with open(export_json, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))
        render_success("Report Exported", f"Saved scan results to: [cyan]{export_json}[/]")

    console.print(
        "\n[dim italic]💡 Want automated weekly scans and Slack alerts? Visit [/][bold cyan]https://costslash.dev[/]"
    )


@app.command(name="demo")
def demo():
    """Run an instant demonstration scan."""
    scan(region="us-east-1", all_regions=False, live=False, profile=None, fix=True, export_json=None)


if __name__ == "__main__":
    app()

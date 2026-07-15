"""Command-line entry point for the deterministic ForgetOps demo."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from forgetops.models import ErasurePlan, ErasureRequest, GraphSnapshot
from forgetops.planner import ErasurePlanner
from forgetops.reporting import render_markdown
from forgetops.sandbox import (
    SandboxExecutor,
    bootstrap_sandbox,
    load_scenario,
    render_execution_markdown,
    write_execution_receipt,
)

app = typer.Typer(no_args_is_help=True, help="Lineage-aware privacy operations.")
console = Console()


@app.callback()
def main() -> None:
    """Run ForgetOps workflows."""


@app.command()
def plan(
    graph: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    subject_id: Annotated[str, typer.Option(help="Raw ID; hashed in memory and never persisted.")],
    request_id: Annotated[str, typer.Option(help="Case identifier, for example DSR-2026-0042.")],
    output_dir: Annotated[Path, typer.Option()] = Path("artifacts/runtime"),
) -> None:
    """Generate a dry-run erasure plan from a DataHub-shaped graph snapshot."""

    snapshot = GraphSnapshot.model_validate_json(graph.read_text(encoding="utf-8"))
    request = ErasureRequest.from_subject_id(request_id=request_id, subject_id=subject_id)
    erasure_plan = ErasurePlanner().plan(request, snapshot)

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "erasure-plan.json"
    markdown_path = output_dir / "erasure-plan.md"
    json_path.write_text(erasure_plan.model_dump_json(indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(erasure_plan), encoding="utf-8")

    console.print(f"[bold green]Plan generated:[/bold green] {request_id}")
    console.print(f"Status: [bold]{erasure_plan.status.value}[/bold]")
    console.print(f"JSON: {json_path}")
    console.print(f"Report: {markdown_path}")


@app.command("sandbox-init")
def sandbox_init(
    scenario: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    database: Annotated[Path, typer.Option()],
    approve: Annotated[bool, typer.Option("--approve")] = False,
    overwrite: Annotated[bool, typer.Option("--overwrite")] = False,
) -> None:
    """Create the synthetic DuckDB warehouse; dry-run unless explicitly approved."""

    receipt = bootstrap_sandbox(
        load_scenario(scenario),
        database,
        approved=approve,
        overwrite=overwrite,
    )
    mode = "created" if receipt.applied else "dry_run"
    console.print(f"Sandbox: [bold]{mode}[/bold]")
    console.print(f"Tables: {receipt.table_count}; rows: {receipt.row_count}")
    console.print(f"Database: {receipt.database_path}")


@app.command("sandbox-execute")
def sandbox_execute(
    plan_path: Annotated[Path, typer.Option("--plan", exists=True, dir_okay=False, readable=True)],
    scenario: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    database: Annotated[Path, typer.Option(exists=True, dir_okay=False, readable=True)],
    subject_id: Annotated[str, typer.Option(help="Synthetic ID; never persisted in evidence.")],
    idempotency_key: Annotated[str, typer.Option()],
    output_dir: Annotated[Path, typer.Option()] = Path("artifacts/runtime/sandbox-execution"),
    approve: Annotated[bool, typer.Option("--approve")] = False,
) -> None:
    """Preview or execute the approved plan against the isolated synthetic warehouse."""

    erasure_plan = ErasurePlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    receipt = SandboxExecutor().execute(
        erasure_plan,
        load_scenario(scenario),
        database,
        subject_id=subject_id,
        idempotency_key=idempotency_key,
        approved=approve,
    )
    json_path = output_dir / "execution-receipt.json"
    markdown_path = output_dir / "execution-evidence.md"
    write_execution_receipt(receipt, json_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_execution_markdown(receipt), encoding="utf-8")
    console.print(f"Execution: [bold]{receipt.status.value}[/bold]")
    console.print(
        f"Approved: {str(receipt.approved).lower()}; replayed: {str(receipt.replayed).lower()}"
    )
    console.print(f"Verified actions: {receipt.verified_actions}/{len(receipt.actions)}")
    console.print(f"JSON: {json_path}")
    console.print(f"Report: {markdown_path}")


if __name__ == "__main__":
    app()

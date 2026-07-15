"""Command-line entry point for the deterministic ForgetOps demo."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from forgetops.models import ErasureRequest, GraphSnapshot
from forgetops.planner import ErasurePlanner
from forgetops.reporting import render_markdown

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


if __name__ == "__main__":
    app()

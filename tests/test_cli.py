from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from forgetops.cli import app

runner = CliRunner()
FIXTURE = Path("examples/input/ecommerce-privacy-graph.json").resolve()


def test_plan_command_writes_private_evidence_bundle(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "plan",
            "--graph",
            str(FIXTURE),
            "--subject-id",
            "customer-0042",
            "--request-id",
            "DSR-2026-0042",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "review_required" in result.output
    json_output = (tmp_path / "erasure-plan.json").read_text(encoding="utf-8")
    markdown_output = (tmp_path / "erasure-plan.md").read_text(encoding="utf-8")
    assert "customer-0042" not in json_output
    assert "customer-0042" not in markdown_output
    assert "sha256:" in json_output

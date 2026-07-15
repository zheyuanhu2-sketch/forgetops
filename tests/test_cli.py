from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from forgetops.cli import app

runner = CliRunner()
FIXTURE = Path("examples/input/ecommerce-privacy-graph.json").resolve()
PLAN_FIXTURE = Path("examples/output/erasure-plan.json").resolve()
SANDBOX_FIXTURE = Path("examples/input/ecommerce-sandbox.json").resolve()


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


def test_sandbox_cli_preserves_dry_run_and_explicit_approval_boundary(tmp_path: Path) -> None:
    database = tmp_path / "demo.duckdb"
    preview_init = runner.invoke(
        app,
        [
            "sandbox-init",
            "--scenario",
            str(SANDBOX_FIXTURE),
            "--database",
            str(database),
        ],
    )
    assert preview_init.exit_code == 0, preview_init.output
    assert "dry_run" in preview_init.output
    assert not database.exists()

    approved_init = runner.invoke(
        app,
        [
            "sandbox-init",
            "--scenario",
            str(SANDBOX_FIXTURE),
            "--database",
            str(database),
            "--approve",
        ],
    )
    assert approved_init.exit_code == 0, approved_init.output
    assert "created" in approved_init.output
    assert database.exists()

    preview_output = tmp_path / "preview"
    preview = runner.invoke(
        app,
        [
            "sandbox-execute",
            "--plan",
            str(PLAN_FIXTURE),
            "--scenario",
            str(SANDBOX_FIXTURE),
            "--database",
            str(database),
            "--subject-id",
            "customer-0042",
            "--idempotency-key",
            "cli-preview-0042",
            "--output-dir",
            str(preview_output),
        ],
    )
    assert preview.exit_code == 0, preview.output
    assert "dry_run" in preview.output
    assert "customer-0042" not in (preview_output / "execution-receipt.json").read_text(
        encoding="utf-8"
    )

    approved_output = tmp_path / "approved"
    approved = runner.invoke(
        app,
        [
            "sandbox-execute",
            "--plan",
            str(PLAN_FIXTURE),
            "--scenario",
            str(SANDBOX_FIXTURE),
            "--database",
            str(database),
            "--subject-id",
            "customer-0042",
            "--idempotency-key",
            "cli-execute-0042",
            "--output-dir",
            str(approved_output),
            "--approve",
        ],
    )
    assert approved.exit_code == 0, approved.output
    assert "partial_verified" in approved.output
    assert (approved_output / "execution-evidence.md").exists()

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pytest

from forgetops.models import ErasureRequest, GraphSnapshot
from forgetops.planner import ErasurePlanner
from forgetops.sandbox import (
    ActionOutcome,
    ExecutionStatus,
    SandboxExecutionError,
    SandboxExecutor,
    SubjectReferenceMismatch,
    bootstrap_sandbox,
    load_scenario,
    render_execution_markdown,
)

GRAPH_PATH = Path("examples/input/ecommerce-privacy-graph.json")
SCENARIO_PATH = Path("examples/input/ecommerce-sandbox.json")
SUBJECT_ID = "customer-0042"


def _plan():
    graph = GraphSnapshot.model_validate_json(GRAPH_PATH.read_text(encoding="utf-8"))
    request = ErasureRequest.from_subject_id(request_id="DSR-TEST-0042", subject_id=SUBJECT_ID)
    return ErasurePlanner(now=lambda: datetime(2026, 7, 15, tzinfo=UTC)).plan(request, graph)


def _database(tmp_path: Path) -> Path:
    path = tmp_path / "sandbox.duckdb"
    receipt = bootstrap_sandbox(load_scenario(SCENARIO_PATH), path, approved=True)
    assert receipt.applied is True
    return path


def _count(path: Path, relation: str, subject_id: str = SUBJECT_ID) -> int:
    with duckdb.connect(str(path), read_only=True) as connection:
        row = connection.execute(
            f'SELECT COUNT(*) FROM "{relation}" WHERE customer_id = ?', [subject_id]
        ).fetchone()
    assert row is not None
    return int(row[0])


def test_bootstrap_defaults_to_dry_run(tmp_path: Path) -> None:
    database = tmp_path / "dry-run.duckdb"
    receipt = bootstrap_sandbox(load_scenario(SCENARIO_PATH), database)

    assert receipt.applied is False
    assert receipt.table_count == 6
    assert receipt.row_count == 12
    assert not database.exists()


def test_execution_defaults_to_non_mutating_preview(tmp_path: Path) -> None:
    database = _database(tmp_path)
    receipt = SandboxExecutor().execute(
        _plan(),
        load_scenario(SCENARIO_PATH),
        database,
        subject_id=SUBJECT_ID,
        idempotency_key="preview-0042",
    )

    assert receipt.status is ExecutionStatus.DRY_RUN
    assert receipt.approved is False
    assert _count(database, "ecommerce_customers") == 1
    assert any(action.outcome is ActionOutcome.WOULD_EXECUTE for action in receipt.actions)
    assert any(action.outcome is ActionOutcome.RETAINED for action in receipt.actions)


def test_approved_execution_is_atomic_verified_and_privacy_safe(tmp_path: Path) -> None:
    database = _database(tmp_path)
    receipt = SandboxExecutor(now=lambda: datetime(2026, 7, 15, tzinfo=UTC)).execute(
        _plan(),
        load_scenario(SCENARIO_PATH),
        database,
        subject_id=SUBJECT_ID,
        idempotency_key="execute-0042-v1",
        approved=True,
    )

    assert receipt.status is ExecutionStatus.PARTIAL_VERIFIED
    assert receipt.verified_actions == 7
    assert receipt.exception_actions == 2
    assert _count(database, "ecommerce_customers") == 0
    assert _count(database, "marketing_customer_export") == 0
    assert _count(database, "support_tickets") == 0
    assert _count(database, "analytics_customer_360") == 0
    assert _count(database, "finance_invoices") == 1
    assert _count(database, "ml_customer_churn_features") == 1
    assert _count(database, "ecommerce_customers", "customer-control") == 1
    assert SUBJECT_ID not in receipt.model_dump_json()
    assert SUBJECT_ID not in render_execution_markdown(receipt)
    assert "partial_verified" in render_execution_markdown(receipt)

    with duckdb.connect(str(database), read_only=True) as connection:
        anonymized = connection.execute(
            "SELECT requester_email, message_body FROM support_tickets "
            "WHERE customer_id LIKE 'anon_%'"
        ).fetchone()
    assert anonymized == ("[REDACTED]", "[REDACTED]")


def test_idempotent_replay_does_not_mutate_twice(tmp_path: Path) -> None:
    database = _database(tmp_path)
    executor = SandboxExecutor()
    arguments = {
        "plan": _plan(),
        "scenario": load_scenario(SCENARIO_PATH),
        "database_path": database,
        "subject_id": SUBJECT_ID,
        "idempotency_key": "execute-0042-replay",
        "approved": True,
    }

    first = executor.execute(**arguments)
    second = executor.execute(**arguments)

    assert first.replayed is False
    assert second.replayed is True
    assert first.actions == second.actions
    assert _count(database, "finance_invoices") == 1


def test_idempotency_key_cannot_be_reused_for_a_different_plan(tmp_path: Path) -> None:
    database = _database(tmp_path)
    executor = SandboxExecutor()
    plan = _plan()
    executor.execute(
        plan,
        load_scenario(SCENARIO_PATH),
        database,
        subject_id=SUBJECT_ID,
        idempotency_key="bound-plan-0042",
        approved=True,
    )
    changed_plan = plan.model_copy(update={"actions": list(reversed(plan.actions))})

    with pytest.raises(SandboxExecutionError, match="another plan or scenario"):
        executor.execute(
            changed_plan,
            load_scenario(SCENARIO_PATH),
            database,
            subject_id=SUBJECT_ID,
            idempotency_key="bound-plan-0042",
            approved=True,
        )


def test_subject_mismatch_is_rejected_before_mutation(tmp_path: Path) -> None:
    database = _database(tmp_path)

    with pytest.raises(SubjectReferenceMismatch):
        SandboxExecutor().execute(
            _plan(),
            load_scenario(SCENARIO_PATH),
            database,
            subject_id="different-synthetic-subject",
            idempotency_key="wrong-subject",
            approved=True,
        )

    assert _count(database, "ecommerce_customers") == 1


def test_late_failure_rolls_back_earlier_actions(tmp_path: Path) -> None:
    database = _database(tmp_path)
    plan = _plan()
    support_action = next(
        action for action in plan.actions if action.asset_name == "support.tickets"
    )
    support_action.fields.append("missing_planned_field")

    with pytest.raises(SandboxExecutionError, match="missing planned fields"):
        SandboxExecutor().execute(
            plan,
            load_scenario(SCENARIO_PATH),
            database,
            subject_id=SUBJECT_ID,
            idempotency_key="rollback-0042",
            approved=True,
        )

    assert _count(database, "ecommerce_customers") == 1
    assert _count(database, "support_tickets") == 1

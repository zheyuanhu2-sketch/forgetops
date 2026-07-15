from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from forgetops.models import ErasureRequest, GraphSnapshot, HandlingRule, PlanStatus
from forgetops.planner import ErasurePlanner
from forgetops.reporting import render_markdown

FIXTURE = Path("examples/input/ecommerce-privacy-graph.json")
NOW = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)


def load_graph() -> GraphSnapshot:
    return GraphSnapshot.model_validate_json(FIXTURE.read_text(encoding="utf-8"))


def build_plan():  # type: ignore[no-untyped-def]
    request = ErasureRequest.from_subject_id(request_id="DSR-2026-0042", subject_id="customer-0042")
    return ErasurePlanner(now=lambda: NOW).plan(request, load_graph())


def test_plan_maps_full_graph_and_requires_retention_review() -> None:
    plan = build_plan()

    assert plan.status is PlanStatus.REVIEW_REQUIRED
    assert plan.coverage.discovered_assets == 7
    assert plan.coverage.lineage_edges == 6
    assert plan.coverage.owner_coverage_pct == 100.0
    assert plan.coverage.held_assets == 1
    assert plan.coverage.actionable_assets == 6


def test_legal_hold_is_never_converted_to_a_mutation() -> None:
    plan = build_plan()
    invoice_action = next(
        action for action in plan.actions if action.asset_name == "finance.invoices"
    )

    assert invoice_action.action is HandlingRule.RETAIN
    assert invoice_action.blocked is True
    assert any("legal-hold" in gate for gate in plan.review_gates)


def test_action_order_respects_datahub_lineage() -> None:
    plan = build_plan()
    positions = {action.asset_name: action.sequence for action in plan.actions}

    assert positions["ecommerce.customers"] < positions["analytics.customer_360"]
    assert positions["support.tickets"] < positions["analytics.customer_360"]
    assert positions["analytics.customer_360"] < positions["ml.customer_churn_features"]
    assert positions["analytics.customer_360"] < positions["Customer Retention Overview"]


def test_report_contains_datahub_evidence_but_not_raw_subject_id() -> None:
    report = render_markdown(build_plan())

    assert "get_lineage" in report
    assert "save_document" in report
    assert "customer-0042" not in report
    assert "sha256:" in report

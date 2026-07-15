"""Judge-readable report rendering."""

from __future__ import annotations

from forgetops.models import ErasurePlan


def render_markdown(plan: ErasurePlan) -> str:
    """Render an evidence-first report without exposing a raw subject identifier."""

    coverage = plan.coverage
    held_noun = "asset is" if coverage.held_assets == 1 else "assets are"
    lines = [
        f"# Erasure plan {plan.request.request_id}",
        "",
        f"- Status: **{plan.status.value}**",
        f"- Subject reference: `{plan.request.subject_ref}`",
        f"- DataHub snapshot: `{plan.graph_snapshot_id}`",
        f"- Generated: `{plan.generated_at.isoformat()}`",
        "",
        "## Coverage",
        "",
        f"- {coverage.discovered_assets} assets discovered across "
        f"{coverage.lineage_edges} lineage edges",
        f"- {coverage.pii_fields} PII-bearing fields mapped",
        f"- {coverage.actionable_assets} assets have actionable handling rules",
        f"- {coverage.held_assets} {held_noun} protected by review gates",
        f"- Owner coverage: {coverage.owner_coverage_pct}%",
        "",
        "## Planned actions",
        "",
        "| # | Asset | Action | Fields | Owner | Gate |",
        "|---:|---|---|---|---|---|",
    ]
    for action in plan.actions:
        owners = ", ".join(action.owners) if action.owners else "Missing"
        gate = "Blocked" if action.blocked else "Approval required"
        lines.append(
            f"| {action.sequence} | {action.asset_name} | {action.action.value} | "
            f"{', '.join(action.fields)} | {owners} | {gate} |"
        )

    lines.extend(["", "## Review gates", ""])
    if plan.review_gates:
        lines.extend(f"- {gate}" for gate in plan.review_gates)
    else:
        lines.append("- No blocking review gates. Explicit mutation approval is still required.")

    lines.extend(
        [
            "",
            "## DataHub evidence loop",
            "",
            f"- Read tools: {', '.join(plan.datahub.read_tools)}",
            f"- Planned write-back: {', '.join(plan.datahub.planned_write_tools)}",
            "",
            "> This plan is a dry run. It records organization-defined policy metadata and "
            "does not constitute legal advice.",
            "",
        ]
    )
    return "\n".join(lines)

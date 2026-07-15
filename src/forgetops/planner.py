"""Deterministic, policy-bound planning logic.

The planner is intentionally not an LLM. An LLM can later explain or format the plan,
but it cannot override DataHub policy signals or safety gates.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from heapq import heapify, heappop, heappush

from forgetops.models import (
    AssetContext,
    CoverageSummary,
    DataHubEvidence,
    ErasurePlan,
    ErasureRequest,
    GraphSnapshot,
    HandlingRule,
    PlannedAction,
    PlanStatus,
)


class ErasurePlanner:
    """Build a reviewable plan from a DataHub-shaped graph snapshot."""

    def __init__(self, now: Callable[[], datetime] | None = None) -> None:
        self._now = now or (lambda: datetime.now(UTC))

    def plan(self, request: ErasureRequest, graph: GraphSnapshot) -> ErasurePlan:
        actions: list[PlannedAction] = []
        review_gates: list[str] = []

        ordered_assets = self._topological_assets(graph)
        for sequence, asset in enumerate(ordered_assets, start=1):
            blocked = asset.legal_hold
            evidence = [
                f"DataHub asset: {asset.urn}",
                f"PII fields: {', '.join(sorted(asset.pii_fields))}",
                f"Policy source: {asset.policy_source}",
            ]
            if asset.owners:
                evidence.append(f"Owners: {', '.join(sorted(asset.owners))}")
            else:
                evidence.append("Owners: missing in DataHub")
                review_gates.append(f"Assign an accountable owner for {asset.name}")

            if blocked:
                review_gates.append(
                    f"Resolve or confirm the legal-hold gate for {asset.name}; "
                    "ForgetOps will not mutate this asset."
                )

            actions.append(
                PlannedAction(
                    sequence=sequence,
                    asset_urn=asset.urn,
                    asset_name=asset.name,
                    action=asset.handling_rule,
                    owners=sorted(asset.owners),
                    fields=sorted(asset.pii_fields),
                    policy_reason=asset.policy_reason,
                    policy_source=asset.policy_source,
                    evidence=evidence,
                    blocked=blocked,
                )
            )

        assets_with_owners = sum(bool(asset.owners) for asset in graph.assets)
        coverage = CoverageSummary(
            discovered_assets=len(graph.assets),
            lineage_edges=len(graph.edges),
            pii_fields=sum(len(asset.pii_fields) for asset in graph.assets),
            actionable_assets=sum(action.action is not HandlingRule.RETAIN for action in actions),
            held_assets=sum(action.blocked for action in actions),
            owner_coverage_pct=round(assets_with_owners / len(graph.assets) * 100, 1),
        )

        status = PlanStatus.REVIEW_REQUIRED if review_gates else PlanStatus.READY_FOR_APPROVAL
        return ErasurePlan(
            request=request,
            graph_snapshot_id=graph.snapshot_id,
            generated_at=self._now(),
            status=status,
            actions=actions,
            review_gates=review_gates,
            coverage=coverage,
            datahub=DataHubEvidence(
                read_tools=[
                    "search",
                    "list_schema_fields",
                    "get_entities",
                    "get_lineage",
                ],
                planned_write_tools=[
                    "add_tags",
                    "add_structured_properties",
                    "update_description",
                    "save_document",
                ],
            ),
        )

    @staticmethod
    def _topological_assets(graph: GraphSnapshot) -> list[AssetContext]:
        """Order upstream assets before downstream consumers with stable tie-breaking."""

        assets_by_urn = {asset.urn: asset for asset in graph.assets}
        indegree = dict.fromkeys(assets_by_urn, 0)
        downstream: dict[str, list[str]] = {urn: [] for urn in assets_by_urn}
        for edge in graph.edges:
            downstream[edge.upstream_urn].append(edge.downstream_urn)
            indegree[edge.downstream_urn] += 1

        ready = [urn for urn, degree in indegree.items() if degree == 0]
        heapify(ready)
        ordered: list[AssetContext] = []
        while ready:
            urn = heappop(ready)
            ordered.append(assets_by_urn[urn])
            for child in sorted(downstream[urn]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    heappush(ready, child)

        if len(ordered) != len(graph.assets):
            raise ValueError("lineage graph contains a cycle; safe action ordering is impossible")
        return ordered

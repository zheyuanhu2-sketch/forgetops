"""Domain models for deterministic erasure planning.

The model deliberately keeps raw subject identifiers out of persisted state. Policy
metadata is supplied by an organization through DataHub; ForgetOps does not infer law.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    """Base model that rejects unknown fields in policy and evidence payloads."""

    model_config = ConfigDict(extra="forbid")


class AssetKind(StrEnum):
    DATASET = "dataset"
    DASHBOARD = "dashboard"
    FEATURE_TABLE = "feature_table"
    ML_MODEL = "ml_model"


class HandlingRule(StrEnum):
    DELETE = "delete"
    ANONYMIZE = "anonymize"
    RETAIN = "retain"
    REFRESH = "refresh"
    REVIEW = "review"


class PlanStatus(StrEnum):
    READY_FOR_APPROVAL = "ready_for_approval"
    REVIEW_REQUIRED = "review_required"


class ErasureRequest(StrictModel):
    request_id: str = Field(min_length=3, max_length=80)
    subject_ref: str = Field(pattern=r"^sha256:[0-9a-f]{16}$")
    request_type: str = "right_to_erasure"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_subject_id(cls, *, request_id: str, subject_id: str) -> ErasureRequest:
        normalized = subject_id.strip()
        if not normalized:
            raise ValueError("subject_id must not be empty")
        digest = sha256(normalized.encode("utf-8")).hexdigest()[:16]
        return cls(request_id=request_id, subject_ref=f"sha256:{digest}")


class AssetContext(StrictModel):
    urn: str = Field(min_length=10)
    name: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    kind: AssetKind
    owners: list[str] = Field(default_factory=list)
    pii_fields: list[str] = Field(min_length=1)
    subject_keys: list[str] = Field(min_length=1)
    handling_rule: HandlingRule
    policy_reason: str = Field(min_length=3)
    legal_hold: bool = False
    policy_source: str = Field(min_length=3)

    @model_validator(mode="after")
    def legal_hold_requires_retain(self) -> AssetContext:
        if self.legal_hold and self.handling_rule is not HandlingRule.RETAIN:
            raise ValueError("assets under legal hold must use the retain handling rule")
        return self


class LineageEdge(StrictModel):
    upstream_urn: str
    downstream_urn: str
    field_mapping: dict[str, list[str]] = Field(default_factory=dict)


class GraphSnapshot(StrictModel):
    snapshot_id: str
    source: str = "datahub_mcp"
    assets: list[AssetContext] = Field(min_length=1)
    edges: list[LineageEdge] = Field(default_factory=list)

    @model_validator(mode="after")
    def edges_reference_known_assets(self) -> GraphSnapshot:
        urns = {asset.urn for asset in self.assets}
        unknown = {
            urn
            for edge in self.edges
            for urn in (edge.upstream_urn, edge.downstream_urn)
            if urn not in urns
        }
        if unknown:
            raise ValueError(f"lineage edges reference unknown assets: {sorted(unknown)}")
        return self


class PlannedAction(StrictModel):
    sequence: int = Field(ge=1)
    asset_urn: str
    asset_name: str
    action: HandlingRule
    owners: list[str]
    fields: list[str]
    policy_reason: str
    policy_source: str
    evidence: list[str] = Field(min_length=1)
    requires_approval: bool = True
    blocked: bool = False


class CoverageSummary(StrictModel):
    discovered_assets: int = Field(ge=0)
    lineage_edges: int = Field(ge=0)
    pii_fields: int = Field(ge=0)
    actionable_assets: int = Field(ge=0)
    held_assets: int = Field(ge=0)
    owner_coverage_pct: float = Field(ge=0, le=100)


class DataHubEvidence(StrictModel):
    read_tools: list[str]
    planned_write_tools: list[str]


class ErasurePlan(StrictModel):
    request: ErasureRequest
    graph_snapshot_id: str
    generated_at: datetime
    status: PlanStatus
    actions: list[PlannedAction]
    review_gates: list[str]
    coverage: CoverageSummary
    datahub: DataHubEvidence

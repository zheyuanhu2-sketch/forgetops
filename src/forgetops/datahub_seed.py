"""Idempotent synthetic DataHub seed for the ForgetOps demonstration.

The module keeps mutation behind an explicit approval flag and writes a receipt for every
approved run. The synthetic graph contains metadata only; it never contains subject rows or
real personal data.
"""

from __future__ import annotations

import json
import os
import re
import warnings
from collections import defaultdict
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import Field

from forgetops.models import AssetContext, AssetKind, GraphSnapshot, StrictModel

LOCAL_GMS_HOSTS = {"127.0.0.1", "localhost"}
STRUCTURED_PROPERTY_URNS = {
    "handling_rule": "urn:li:structuredProperty:forgetops.handlingRule",
    "legal_hold": "urn:li:structuredProperty:forgetops.legalHold",
    "policy_source": "urn:li:structuredProperty:forgetops.policySource",
    "subject_keys": "urn:li:structuredProperty:forgetops.subjectKeys",
}


class SeedManifest(StrictModel):
    snapshot_id: str
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    entity_urns: list[str]
    tags: list[str]
    owner_groups: list[str]
    structured_property_urns: list[str]
    dataset_count: int = Field(ge=0)
    dashboard_count: int = Field(ge=0)
    schema_field_count: int = Field(ge=0)
    lineage_edge_count: int = Field(ge=0)


class SeedReceipt(SeedManifest):
    applied: bool
    gms_url: str
    completed_at: datetime


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("owner name must contain at least one alphanumeric character")
    return slug


def _tag_urn(name: str) -> str:
    return f"urn:li:tag:{name}"


def _asset_tags(asset: AssetContext) -> list[str]:
    tags = ["ForgetOps.Demo", f"ForgetOps.Action.{asset.handling_rule.value}"]
    if asset.legal_hold:
        tags.append("ForgetOps.LegalHold")
    return sorted(_tag_urn(tag) for tag in tags)


def _owner_group_urn(owner: str) -> str:
    return f"urn:li:corpGroup:{_slug(owner)}"


def build_seed_manifest(graph_path: Path) -> tuple[GraphSnapshot, SeedManifest]:
    payload = graph_path.read_bytes()
    graph = GraphSnapshot.model_validate_json(payload)
    tags = {
        "ForgetOps.Demo",
        "ForgetOps.PII",
        "ForgetOps.SubjectKey",
        *(f"ForgetOps.Action.{asset.handling_rule.value}" for asset in graph.assets),
    }
    if any(asset.legal_hold for asset in graph.assets):
        tags.add("ForgetOps.LegalHold")

    manifest = SeedManifest(
        snapshot_id=graph.snapshot_id,
        graph_sha256=sha256(payload).hexdigest(),
        entity_urns=sorted(asset.urn for asset in graph.assets),
        tags=sorted(_tag_urn(tag) for tag in tags),
        owner_groups=sorted(
            {_owner_group_urn(owner) for asset in graph.assets for owner in asset.owners}
        ),
        structured_property_urns=sorted(STRUCTURED_PROPERTY_URNS.values()),
        dataset_count=sum(asset.kind is not AssetKind.DASHBOARD for asset in graph.assets),
        dashboard_count=sum(asset.kind is AssetKind.DASHBOARD for asset in graph.assets),
        schema_field_count=sum(
            len(asset.pii_fields) for asset in graph.assets if asset.kind is not AssetKind.DASHBOARD
        ),
        lineage_edge_count=len(graph.edges),
    )
    return graph, manifest


def _assert_safe_target(gms_url: str, *, allow_remote: bool) -> None:
    parsed = urlparse(gms_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("gms_url must be an absolute HTTP(S) URL")
    if not allow_remote and parsed.hostname.lower() not in LOCAL_GMS_HOSTS:
        raise ValueError("remote DataHub mutation requires allow_remote=True")


def _reverse_field_mapping(field_mapping: dict[str, list[str]]) -> dict[str, list[str]]:
    downstream_to_upstream: dict[str, list[str]] = defaultdict(list)
    for upstream_field, downstream_fields in field_mapping.items():
        for downstream_field in downstream_fields:
            downstream_to_upstream[downstream_field].append(upstream_field)
    return {
        field: sorted(upstream_fields)
        for field, upstream_fields in sorted(downstream_to_upstream.items())
    }


def seed_datahub(
    graph: GraphSnapshot,
    manifest: SeedManifest,
    *,
    approved: bool,
    gms_url: str = "http://localhost:8080",
    token: str | None = None,
    allow_remote: bool = False,
    now: datetime | None = None,
) -> SeedReceipt:  # pragma: no cover - exercised by the live DataHub smoke test
    """Upsert a synthetic graph into DataHub and return non-secret audit evidence."""

    _assert_safe_target(gms_url, allow_remote=allow_remote)
    if not approved:
        return SeedReceipt(
            **manifest.model_dump(),
            applied=False,
            gms_url=gms_url,
            completed_at=now or datetime.now(UTC),
        )

    warnings.filterwarnings("ignore", message="The new datahub SDK.*")
    warnings.filterwarnings("ignore", message="The entity urn:li:.*already exists.*")
    try:
        from datahub.api.entities.structuredproperties.structuredproperties import (
            AllowedValue,
            StructuredProperties,
        )
        from datahub.emitter.mcp import MetadataChangeProposalWrapper
        from datahub.metadata.schema_classes import CorpGroupInfoClass
        from datahub.metadata.urns import CorpGroupUrn, DatasetUrn
        from datahub.sdk.dashboard import Dashboard
        from datahub.sdk.dataset import Dataset
        from datahub.sdk.main_client import DataHubClient
        from datahub.sdk.tag import Tag
    except ImportError as error:  # pragma: no cover - depends on optional install
        raise RuntimeError(
            "Install the DataHub integration with `uv sync --extra datahub`"
        ) from error

    client = DataHubClient(server=gms_url, token=token)
    client.test_connection()

    tag_descriptions = {
        "ForgetOps.Demo": "Synthetic metadata created for the ForgetOps hackathon demo.",
        "ForgetOps.PII": "Synthetic field marked as personally identifiable information.",
        "ForgetOps.SubjectKey": "Synthetic field used to locate a verified subject reference.",
        "ForgetOps.LegalHold": "Mutation is blocked pending human retention review.",
    }
    for action in {asset.handling_rule.value for asset in graph.assets}:
        tag_descriptions[f"ForgetOps.Action.{action}"] = f"ForgetOps policy action: {action}."
    for tag_urn in manifest.tags:
        name = tag_urn.removeprefix("urn:li:tag:")
        client.entities.upsert(
            Tag(
                name=name,
                display_name=name.replace("ForgetOps.", "ForgetOps / ").replace(".", " / "),
                description=tag_descriptions[name],
                color="#8257E5",
            )
        )

    # The public SDK does not yet expose low-level structured-property proposals.
    # This boundary is pinned to DataHub 1.6 and covered by the live smoke test.
    graph_client = client._graph
    owners_by_urn = {
        _owner_group_urn(owner): owner for asset in graph.assets for owner in asset.owners
    }
    for owner_urn, display_name in sorted(owners_by_urn.items()):
        graph_client.emit_mcp(
            MetadataChangeProposalWrapper(
                entityUrn=owner_urn,
                aspect=CorpGroupInfoClass(
                    admins=[],
                    members=[],
                    groups=[],
                    displayName=display_name,
                    description="Synthetic ForgetOps demo owner group.",
                ),
            )
        )

    property_definitions = [
        StructuredProperties(
            id="forgetops.handlingRule",
            urn=None,
            type="string",
            display_name="ForgetOps handling rule",
            description="Deterministic privacy handling action selected by organization policy.",
            entity_types=["dataset"],
            cardinality="SINGLE",
            allowed_values=[
                AllowedValue(value=value)
                for value in ("delete", "anonymize", "retain", "refresh", "review")
            ],
        ),
        StructuredProperties(
            id="forgetops.legalHold",
            urn=None,
            type="string",
            display_name="ForgetOps legal hold",
            description="Whether mutation is blocked pending human retention review.",
            entity_types=["dataset"],
            cardinality="SINGLE",
            allowed_values=[AllowedValue(value="true"), AllowedValue(value="false")],
        ),
        StructuredProperties(
            id="forgetops.policySource",
            urn=None,
            type="string",
            display_name="ForgetOps policy source",
            description="Human-configured DataHub evidence that selected the handling rule.",
            entity_types=["dataset"],
            cardinality="SINGLE",
        ),
        StructuredProperties(
            id="forgetops.subjectKeys",
            urn=None,
            type="string",
            display_name="ForgetOps subject keys",
            description="Schema fields used to locate the verified synthetic subject reference.",
            entity_types=["dataset"],
            cardinality="MULTIPLE",
        ),
    ]
    for definition in property_definitions:
        for proposal in definition.generate_mcps():
            graph_client.emit_mcp(proposal)

    assets_by_urn = {asset.urn: asset for asset in graph.assets}
    incoming_edges: dict[str, list[tuple[str, dict[str, list[str]]]]] = defaultdict(list)
    for edge in graph.edges:
        incoming_edges[edge.downstream_urn].append(
            (edge.upstream_urn, _reverse_field_mapping(edge.field_mapping))
        )

    datasets: dict[str, Any] = {}
    for asset in graph.assets:
        if asset.kind is AssetKind.DASHBOARD:
            continue
        upstreams: dict[str | DatasetUrn, dict[str, list[str]]] = {}
        for upstream_urn, mapping in incoming_edges.get(asset.urn, []):
            if assets_by_urn[upstream_urn].kind is not AssetKind.DASHBOARD:
                upstreams[DatasetUrn.from_string(upstream_urn)] = mapping
        dataset = Dataset(
            platform=asset.platform,
            name=_dataset_name_from_urn(asset.urn),
            env="PROD",
            display_name=asset.name,
            description=asset.policy_reason,
            subtype="Feature Table" if asset.kind is AssetKind.FEATURE_TABLE else "Table",
            owners=[CorpGroupUrn.from_string(_owner_group_urn(owner)) for owner in asset.owners],
            tags=_asset_tags(asset),
            schema=[
                (field, "varchar", "Synthetic ForgetOps privacy field")
                for field in asset.pii_fields
            ],
            structured_properties={
                STRUCTURED_PROPERTY_URNS["handling_rule"]: [asset.handling_rule.value],
                STRUCTURED_PROPERTY_URNS["legal_hold"]: [str(asset.legal_hold).lower()],
                STRUCTURED_PROPERTY_URNS["policy_source"]: [asset.policy_source],
                STRUCTURED_PROPERTY_URNS["subject_keys"]: asset.subject_keys,
            },
            custom_properties={
                "forgetops.snapshot_id": graph.snapshot_id,
                "forgetops.policy_reason": asset.policy_reason,
            },
        )
        dataset.set_upstreams(upstreams)
        if str(dataset.urn) != asset.urn:
            raise ValueError(f"generated dataset URN does not match fixture: {dataset.urn}")
        for field in asset.pii_fields:
            field_tags = [_tag_urn("ForgetOps.PII")]
            if field in asset.subject_keys:
                field_tags.append(_tag_urn("ForgetOps.SubjectKey"))
            dataset[field].set_tags(field_tags)
        datasets[asset.urn] = dataset

    for dataset in datasets.values():
        client.entities.upsert(dataset)

    for asset in graph.assets:
        if asset.kind is not AssetKind.DASHBOARD:
            continue
        input_datasets = [
            upstream_urn
            for upstream_urn, _mapping in incoming_edges.get(asset.urn, [])
            if upstream_urn in datasets
        ]
        dashboard = Dashboard(
            name=_dashboard_name_from_urn(asset.urn),
            platform=asset.platform,
            display_name=asset.name,
            description=asset.policy_reason,
            subtype="Dashboard",
            input_datasets=input_datasets,
            owners=[CorpGroupUrn.from_string(_owner_group_urn(owner)) for owner in asset.owners],
            tags=_asset_tags(asset),
            custom_properties={
                "forgetops.snapshot_id": graph.snapshot_id,
                "forgetops.handling_rule": asset.handling_rule.value,
                "forgetops.legal_hold": str(asset.legal_hold).lower(),
                "forgetops.pii_fields": ",".join(asset.pii_fields),
                "forgetops.policy_source": asset.policy_source,
                "forgetops.subject_keys": ",".join(asset.subject_keys),
            },
        )
        if str(dashboard.urn) != asset.urn:
            raise ValueError(f"generated dashboard URN does not match fixture: {dashboard.urn}")
        client.entities.upsert(dashboard)

    return SeedReceipt(
        **manifest.model_dump(),
        applied=True,
        gms_url=gms_url,
        completed_at=now or datetime.now(UTC),
    )


def _dataset_name_from_urn(urn: str) -> str:
    match = re.fullmatch(r"urn:li:dataset:\(urn:li:dataPlatform:[^,]+,(.+),PROD\)", urn)
    if not match:
        raise ValueError(f"unsupported synthetic dataset URN: {urn}")
    return match.group(1)


def _dashboard_name_from_urn(urn: str) -> str:
    match = re.fullmatch(r"urn:li:dashboard:\([^,]+,(.+)\)", urn)
    if not match:
        raise ValueError(f"unsupported synthetic dashboard URN: {urn}")
    return match.group(1)


def write_seed_receipt(receipt: SeedReceipt, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(receipt.model_dump_json(indent=2), encoding="utf-8")


def default_token() -> str | None:
    """Read the local DataHub token without exposing it in receipts or logs."""

    return os.environ.get("DATAHUB_GMS_TOKEN") or None


def receipt_json(receipt: SeedReceipt) -> str:
    return json.dumps(receipt.model_dump(mode="json"), indent=2, sort_keys=True)

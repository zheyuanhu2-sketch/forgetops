from __future__ import annotations

import pytest

from forgetops.datahub_mcp import GraphDiscoveryEvidence
from forgetops.datahub_normalizer import (
    DataHubNormalizationError,
    normalize_graph_discovery,
)
from forgetops.models import AssetKind, HandlingRule

CUSTOMERS = "urn:li:dataset:(urn:li:dataPlatform:postgres,ecommerce.customers,PROD)"
ANALYTICS = "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_360,PROD)"
DASHBOARD = "urn:li:dashboard:(looker,customer_retention_overview)"


def _entity(
    urn: str,
    *,
    name: str,
    platform: str,
    action: str,
    legal_hold: str = "false",
    subtype: str = "Table",
) -> dict[str, object]:
    entity_type = "DASHBOARD" if urn.startswith("urn:li:dashboard:") else "DATASET"
    entity: dict[str, object] = {
        "urn": urn,
        "type": entity_type,
        "name": name,
        "platform": {"name": platform},
        "properties": {
            "name": name,
            "description": f"Policy reason for {name}",
            "customProperties": [
                {"key": "forgetops.snapshot_id", "value": "live-test-snapshot"},
                {"key": "forgetops.policy_reason", "value": f"Policy reason for {name}"},
            ],
        },
        "subTypes": {"typeNames": [subtype]},
        "ownership": {"owners": [{"owner": {"info": {"displayName": f"{name} owner"}}}]},
        "tags": {"tags": [{"tag": {"urn": f"urn:li:tag:ForgetOps.Action.{action}"}}]},
    }
    if entity_type == "DATASET":
        entity["structuredProperties"] = {
            "properties": [
                _structured("forgetops.handlingRule", action),
                _structured("forgetops.legalHold", legal_hold),
                _structured("forgetops.policySource", "DataHub test policy"),
                _structured("forgetops.subjectKeys", "customer_id"),
            ]
        }
    return entity


def _structured(name: str, value: str) -> dict[str, object]:
    return {
        "structuredProperty": {"definition": {"qualifiedName": name}},
        "values": [{"stringValue": value}],
    }


def _schema(*fields: str) -> dict[str, object]:
    return {
        "fields": [
            {
                "fieldPath": field,
                "editedTags": [
                    "ForgetOps / PII",
                    *(["ForgetOps / SubjectKey"] if field == "customer_id" else []),
                ],
            }
            for field in fields
        ]
    }


def _lineage(*targets: tuple[str, list[str] | None]) -> dict[str, object]:
    return {
        "downstreams": {
            "searchResults": [
                {
                    "degree": 1,
                    "entity": {"urn": urn},
                    **({"lineageColumns": columns} if columns is not None else {}),
                }
                for urn, columns in targets
            ]
        }
    }


def _evidence() -> GraphDiscoveryEvidence:
    return GraphDiscoveryEvidence(
        query="customer_id",
        seed_urn=CUSTOMERS,
        search={"total": 2},
        entities=[
            _entity(CUSTOMERS, name="ecommerce.customers", platform="postgres", action="delete"),
            _entity(
                ANALYTICS,
                name="analytics.customer_360",
                platform="snowflake",
                action="anonymize",
                subtype="Feature Table",
            ),
            _entity(
                DASHBOARD,
                name="Customer Retention Overview",
                platform="looker",
                action="refresh",
                subtype="Dashboard",
            ),
        ],
        schema_fields_by_urn={
            CUSTOMERS: _schema("customer_id", "email"),
            ANALYTICS: _schema("customer_id", "email_hash"),
        },
        lineage_by_urn={
            CUSTOMERS: _lineage((ANALYTICS, None)),
            ANALYTICS: _lineage((DASHBOARD, None)),
        },
        column_lineage_by_urn={
            CUSTOMERS: {"customer_id": _lineage((ANALYTICS, ["customer_id"]))},
            ANALYTICS: {"customer_id": _lineage()},
        },
        tool_calls=["search", "get_entities", "list_schema_fields", "get_lineage"],
    )


def test_normalizer_builds_a_policy_bound_multitype_graph() -> None:
    graph = normalize_graph_discovery(_evidence())

    assert graph.snapshot_id == "live-test-snapshot"
    assert graph.source == "datahub_mcp_live"
    assert [asset.urn for asset in graph.assets] == sorted([CUSTOMERS, ANALYTICS, DASHBOARD])
    analytics = next(asset for asset in graph.assets if asset.urn == ANALYTICS)
    dashboard = next(asset for asset in graph.assets if asset.urn == DASHBOARD)
    assert analytics.kind is AssetKind.FEATURE_TABLE
    assert analytics.handling_rule is HandlingRule.ANONYMIZE
    assert dashboard.kind is AssetKind.DASHBOARD
    assert dashboard.subject_keys == ["customer_id"]
    assert dashboard.policy_source == "DataHub tag: urn:li:tag:ForgetOps.Action.refresh"
    assert graph.edges[0].field_mapping == {"customer_id": ["customer_id"]}
    assert graph.edges[1].field_mapping == {"customer_id": ["customer_id"]}


def test_normalizer_fails_closed_on_inconsistent_legal_hold() -> None:
    evidence = _evidence()
    evidence.entities[0] = _entity(
        CUSTOMERS,
        name="ecommerce.customers",
        platform="postgres",
        action="delete",
        legal_hold="true",
    )

    with pytest.raises(DataHubNormalizationError, match="legal hold"):
        normalize_graph_discovery(evidence)


def test_normalizer_rejects_missing_seed_evidence() -> None:
    evidence = _evidence()
    evidence.entities = [entity for entity in evidence.entities if entity["urn"] != CUSTOMERS]

    with pytest.raises(DataHubNormalizationError, match="seed entity"):
        normalize_graph_discovery(evidence)

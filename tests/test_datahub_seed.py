from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from forgetops.datahub_seed import (
    _assert_safe_target,
    _dashboard_name_from_urn,
    _dataset_name_from_urn,
    _reverse_field_mapping,
    build_seed_manifest,
    default_token,
    receipt_json,
    seed_datahub,
    write_seed_receipt,
)

GRAPH_PATH = Path("examples/input/ecommerce-privacy-graph.json")


def test_manifest_describes_the_full_synthetic_datahub_graph() -> None:
    graph, manifest = build_seed_manifest(GRAPH_PATH)

    assert manifest.snapshot_id == graph.snapshot_id
    assert manifest.dataset_count == 6
    assert manifest.dashboard_count == 1
    assert manifest.lineage_edge_count == 6
    assert manifest.schema_field_count == 18
    assert len(manifest.owner_groups) == 7
    assert "urn:li:tag:ForgetOps.PII" in manifest.tags
    assert "urn:li:tag:ForgetOps.LegalHold" in manifest.tags
    assert len(manifest.structured_property_urns) == 4


def test_seed_defaults_to_a_non_mutating_receipt() -> None:
    graph, manifest = build_seed_manifest(GRAPH_PATH)
    completed_at = datetime(2026, 7, 15, tzinfo=UTC)

    receipt = seed_datahub(
        graph,
        manifest,
        approved=False,
        now=completed_at,
    )

    assert receipt.applied is False
    assert receipt.completed_at == completed_at
    assert receipt.entity_urns == manifest.entity_urns


@pytest.mark.parametrize(
    "url",
    ["datahub.internal:8080", "ftp://localhost:8080", "https://datahub.example.com"],
)
def test_seed_rejects_unsafe_targets_without_remote_opt_in(url: str) -> None:
    with pytest.raises(ValueError):
        _assert_safe_target(url, allow_remote=False)


def test_remote_target_still_requires_explicit_allow_remote() -> None:
    _assert_safe_target("https://datahub.example.com", allow_remote=True)


def test_field_mapping_is_reversed_for_datahub_sdk_lineage() -> None:
    assert _reverse_field_mapping(
        {"customer_id": ["customer_id"], "email": ["email_hash", "contact_hash"]}
    ) == {
        "contact_hash": ["email"],
        "customer_id": ["customer_id"],
        "email_hash": ["email"],
    }


def test_fixture_urn_parsers_preserve_entity_identity() -> None:
    assert (
        _dataset_name_from_urn(
            "urn:li:dataset:(urn:li:dataPlatform:postgres,ecommerce.customers,PROD)"
        )
        == "ecommerce.customers"
    )
    assert (
        _dashboard_name_from_urn("urn:li:dashboard:(looker,customer_retention_overview)")
        == "customer_retention_overview"
    )


@pytest.mark.parametrize(
    "parser,urn",
    [
        (_dataset_name_from_urn, "urn:li:dashboard:(looker,demo)"),
        (_dashboard_name_from_urn, "urn:li:dataset:(urn:li:dataPlatform:postgres,demo,PROD)"),
    ],
)
def test_fixture_urn_parsers_reject_the_wrong_entity_type(parser: object, urn: str) -> None:
    assert callable(parser)
    with pytest.raises(ValueError):
        parser(urn)


def test_receipt_helpers_write_only_non_secret_audit_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    graph, manifest = build_seed_manifest(GRAPH_PATH)
    receipt = seed_datahub(graph, manifest, approved=False)
    output = tmp_path / "audit" / "receipt.json"
    monkeypatch.setenv("DATAHUB_GMS_TOKEN", "local-token-not-written")

    write_seed_receipt(receipt, output)

    assert default_token() == "local-token-not-written"
    assert receipt_json(receipt).startswith("{")
    assert "local-token-not-written" not in output.read_text(encoding="utf-8")

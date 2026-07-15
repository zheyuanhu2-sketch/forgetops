from __future__ import annotations

import pytest
from pydantic import ValidationError

from forgetops.models import AssetContext, AssetKind, ErasureRequest, HandlingRule


def test_subject_identifier_is_hashed_before_persistence() -> None:
    request = ErasureRequest.from_subject_id(request_id="DSR-2026-0042", subject_id="customer-0042")

    assert request.subject_ref.startswith("sha256:")
    assert "customer-0042" not in request.model_dump_json()


def test_legal_hold_cannot_be_configured_with_a_mutating_rule() -> None:
    with pytest.raises(ValidationError, match="legal hold"):
        AssetContext(
            urn="urn:li:dataset:test",
            name="finance.invoices",
            platform="snowflake",
            kind=AssetKind.DATASET,
            owners=["Finance"],
            pii_fields=["customer_id"],
            subject_keys=["customer_id"],
            handling_rule=HandlingRule.DELETE,
            policy_reason="Retention review required.",
            legal_hold=True,
            policy_source="DataHub policy",
        )

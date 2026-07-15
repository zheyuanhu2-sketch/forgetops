from __future__ import annotations

import json
from collections.abc import Callable
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import cast

import pytest

DOCUMENT_URN = "urn:li:document:shared-forgetops-0042"

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "smoke_datahub_writeback.py"
SPEC = spec_from_file_location("forgetops_writeback_smoke", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
existing_document_urn = cast(Callable[..., str | None], MODULE.existing_document_urn)


def _write_receipt(path: Path, **overrides: object) -> None:
    payload: dict[str, object] = {
        "case_id": "DSR-2026-0042",
        "idempotency_key": "execute-0042:datahub-v1",
        "document_urn": DOCUMENT_URN,
    }
    payload.update(overrides)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_existing_document_urn_is_bound_to_case_and_operation(tmp_path: Path) -> None:
    path = tmp_path / "writeback.json"
    _write_receipt(path)

    result = existing_document_urn(
        path,
        case_id="DSR-2026-0042",
        idempotency_key="execute-0042:datahub-v1",
    )

    assert result == DOCUMENT_URN


@pytest.mark.parametrize(
    "overrides",
    [
        {"case_id": "DSR-OTHER"},
        {"idempotency_key": "other:datahub-v1"},
        {"document_urn": "not-a-document-urn"},
    ],
)
def test_existing_document_urn_rejects_mismatched_audit_receipts(
    tmp_path: Path,
    overrides: dict[str, object],
) -> None:
    path = tmp_path / "writeback.json"
    _write_receipt(path, **overrides)

    with pytest.raises(ValueError):
        existing_document_urn(
            path,
            case_id="DSR-2026-0042",
            idempotency_key="execute-0042:datahub-v1",
        )

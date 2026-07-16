"""Fail-closed verification for the judge-facing ForgetOps evidence bundle."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "examples" / "output"
HASHED_SUBJECT = re.compile(r"^sha256:[0-9a-f]{16}$")
RAW_SUBJECT_MARKERS = ("customer-0042", "customer@example.com")


def load_json(name: str) -> dict[str, Any]:
    """Load one checked-in evidence object."""
    value = json.loads((OUTPUT / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain a JSON object")
    return value


def require(condition: bool, message: str) -> None:
    """Raise an actionable verification error when a claim no longer holds."""
    if not condition:
        raise AssertionError(message)


def verify() -> list[str]:
    """Verify the public evidence bundle and return human-readable checks."""
    live = load_json("datahub-live-smoke.json")
    plan = load_json("erasure-plan.json")
    execution = load_json("sandbox-execution-summary.json")
    writeback = load_json("datahub-writeback-summary.json")

    coverage = plan["coverage"]
    expected_counts = {
        "assets": 7,
        "edges": 6,
        "pii_fields": 19,
        "held_assets": 1,
    }
    for key, expected in expected_counts.items():
        require(live[key] == expected, f"live {key} must remain {expected}")
    require(live["datahub_tool_calls"] == 21, "live MCP call count must remain 21")
    require(live["mutations_enabled"] is False, "discovery session must remain read-only")
    require(HASHED_SUBJECT.fullmatch(live["subject_ref"]) is not None, "subject must be hashed")
    require(coverage["discovered_assets"] == live["assets"], "asset counts must agree")
    require(coverage["lineage_edges"] == live["edges"], "lineage counts must agree")
    require(coverage["pii_fields"] == live["pii_fields"], "PII counts must agree")
    require(coverage["owner_coverage_pct"] == 100.0, "owner coverage must remain complete")
    require(
        set(live["read_tools"]) == {"search", "list_schema_fields", "get_entities", "get_lineage"},
        "live evidence must retain all four official MCP read tools",
    )

    actions = plan["actions"]
    require(len(actions) == 7, "plan must retain seven evidence-backed outcomes")
    require(all(action["owners"] for action in actions), "every outcome must retain an owner")
    require(
        all(action["policy_source"].startswith("DataHub") for action in actions),
        "every decision must cite a DataHub policy source",
    )
    require(
        sum(action["blocked"] for action in actions) == 1, "legal-hold gate must remain visible"
    )

    require(execution["approved"] is True, "checked-in execution must be explicitly approved")
    require(execution["status"] == "partial_verified", "result must remain truthfully partial")
    require(execution["idempotent_replay_verified"] is True, "replay must remain verified")
    require(execution["transaction_rollback_verified"] is True, "rollback must remain verified")
    require(execution["raw_subject_in_audit_evidence"] is False, "receipt must exclude raw subject")
    exceptions = {"retained", "review_pending"}
    permitted = [item for item in execution["actions"] if item["outcome"] not in exceptions]
    require(all(item["remaining"] == 0 for item in permitted), "permitted residuals must be zero")
    require(len(execution["actions"]) - len(permitted) == 2, "two exceptions must remain explicit")

    require(writeback["approved"] is True, "write-back must retain separate approval evidence")
    require(writeback["execution_status"] == "partial_verified", "write-back status must agree")
    require(writeback["entity_count"] == 7, "write-back must cover all seven entities")
    require(
        set(writeback["mutation_tools"])
        == {"add_tags", "add_structured_properties", "save_document"},
        "write-back must retain all three official MCP mutation tools",
    )
    verification = writeback["verification"]
    require(verification["verified_entity_count"] == 7, "fresh read-back must cover seven entities")
    require(verification["document_found"] is True, "evidence document must be found")
    require(verification["document_content_verified"] is True, "document body must be verified")
    require(writeback["reuses_document_urn"] is True, "retries must reuse the evidence document")

    for path in sorted(OUTPUT.glob("*.json")):
        text = path.read_text(encoding="utf-8").lower()
        require(
            not any(marker in text for marker in RAW_SUBJECT_MARKERS),
            f"raw demo subject material found in {path.name}",
        )

    return [
        "21 bounded official MCP calls verified",
        "7 assets / 6 lineage edges / 19 PII fields / 100% owner coverage verified",
        "dry-run discovery, legal-hold gate, and DataHub policy provenance verified",
        "transaction rollback, idempotent replay, and zero permitted residuals verified",
        "separate write-back approval and fresh-session read-back verified",
        "judge-facing JSON evidence contains no raw demo subject material",
    ]


def main() -> None:
    """Run the evidence gate and print a compact receipt."""
    checks = verify()
    print(f"ForgetOps judging evidence: PASS ({len(checks)} checks)")
    for check in checks:
        print(f"- {check}")


if __name__ == "__main__":
    main()

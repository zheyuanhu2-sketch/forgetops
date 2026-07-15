"""Dry-run or explicitly approve an auditable ForgetOps receipt write-back to DataHub."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import warnings
from pathlib import Path

from forgetops.datahub_mcp import connect_local_datahub
from forgetops.sandbox import ExecutionReceipt, ExecutionStatus, render_execution_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("artifacts/runtime/sandbox-execution/execution-receipt.json"),
    )
    parser.add_argument("--approve", action="store_true")
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path("artifacts/runtime/datahub-writeback-receipt.json"),
    )
    return parser.parse_args()


def existing_document_urn(
    path: Path,
    *,
    case_id: str,
    idempotency_key: str,
) -> str | None:
    """Read the server-assigned document URN from a prior successful receipt."""
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"existing audit receipt is not a JSON object: {path}")
    if payload.get("case_id") != case_id or payload.get("idempotency_key") != idempotency_key:
        raise ValueError(f"existing audit receipt belongs to another case or operation: {path}")
    value = payload.get("document_urn")
    if not isinstance(value, str) or not value.startswith("urn:li:document:"):
        raise ValueError(f"existing audit receipt has no valid document URN: {path}")
    return value


async def run(args: argparse.Namespace) -> dict[str, object]:
    receipt = ExecutionReceipt.model_validate_json(args.receipt.read_text(encoding="utf-8"))
    entity_urns = sorted({action.asset_urn for action in receipt.actions})
    idempotency_key = f"{receipt.idempotency_key}:datahub-v1"
    document_urn = existing_document_urn(
        args.audit_output,
        case_id=receipt.request_id,
        idempotency_key=idempotency_key,
    )
    eligible_for_writeback = (
        receipt.approved
        and receipt.status is not ExecutionStatus.DRY_RUN
        and receipt.verified_actions == len(receipt.actions)
    )
    tag_name = (
        "ForgetOps.Case.Verified"
        if receipt.status is ExecutionStatus.VERIFIED
        else "ForgetOps.Case.PartialVerified"
    )
    preview: dict[str, object] = {
        "approved": args.approve,
        "case_id": receipt.request_id,
        "entity_count": len(entity_urns),
        "eligible_for_writeback": eligible_for_writeback,
        "execution_status": receipt.status.value,
        "idempotency_key": idempotency_key,
        "mutation_tools": ["add_tags", "add_structured_properties", "save_document"],
        "reuses_document_urn": document_urn is not None,
        "tag_urn": f"urn:li:tag:{tag_name}" if eligible_for_writeback else None,
    }
    if not args.approve:
        return preview
    if not eligible_for_writeback:
        raise ValueError(
            "DataHub write-back requires an approved, fully verified execution receipt"
        )

    os.environ.setdefault("DATAHUB_GMS_URL", "http://localhost:8080")
    os.environ["TOOLS_IS_MUTATION_ENABLED"] = "true"
    os.environ["SAVE_DOCUMENT_TOOL_ENABLED"] = "true"
    warnings.filterwarnings("ignore")
    logging.disable(logging.CRITICAL)

    from loguru import logger

    logger.remove()
    async with connect_local_datahub() as gateway:
        writeback = await gateway.write_case_evidence(
            approved=True,
            case_id=receipt.request_id,
            idempotency_key=idempotency_key,
            entity_urns=entity_urns,
            case_tag_urn=str(preview["tag_urn"]),
            case_property_urn="urn:li:structuredProperty:forgetops.caseId",
            document_title=f"ForgetOps execution evidence — {receipt.request_id}",
            document_content=render_execution_markdown(receipt),
            document_urn=document_urn,
        )
    os.environ["TOOLS_IS_MUTATION_ENABLED"] = "false"
    os.environ["SAVE_DOCUMENT_TOOL_ENABLED"] = "false"
    async with connect_local_datahub() as gateway:
        verification = await gateway.verify_case_evidence(
            case_id=receipt.request_id,
            entity_urns=entity_urns,
            case_tag_urn=str(preview["tag_urn"]),
            case_property_urn="urn:li:structuredProperty:forgetops.caseId",
            document_urn=writeback.document_urn,
        )
    output = {
        **preview,
        "document_urn": writeback.document_urn,
        "results": writeback.model_dump(),
        "verification": verification.model_dump(),
    }
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    return output


def main() -> None:
    print(json.dumps(asyncio.run(run(parse_args())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

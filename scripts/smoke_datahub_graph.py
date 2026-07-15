"""Run the live DataHub MCP discovery-to-plan path without enabling mutations."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import warnings
from pathlib import Path

from forgetops.datahub_mcp import connect_local_datahub
from forgetops.datahub_normalizer import normalize_graph_discovery
from forgetops.models import ErasureRequest
from forgetops.planner import ErasurePlanner
from forgetops.reporting import render_markdown

DEFAULT_SEED = "urn:li:dataset:(urn:li:dataPlatform:postgres,ecommerce.customers,PROD)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="customer_id")
    parser.add_argument("--seed-urn", default=DEFAULT_SEED)
    parser.add_argument("--max-assets", type=int, default=20)
    parser.add_argument("--request-id", default="DSR-LIVE-SMOKE")
    parser.add_argument("--subject-id", default="synthetic-live-subject")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/runtime/datahub-live"),
    )
    return parser.parse_args()


async def run(args: argparse.Namespace) -> dict[str, object]:
    os.environ.setdefault("DATAHUB_GMS_URL", "http://localhost:8080")
    os.environ["TOOLS_IS_MUTATION_ENABLED"] = "false"
    os.environ["SAVE_DOCUMENT_TOOL_ENABLED"] = "false"
    warnings.filterwarnings("ignore")
    logging.disable(logging.CRITICAL)

    from loguru import logger

    logger.remove()
    async with connect_local_datahub() as gateway:
        evidence = await gateway.discover_graph(
            query=args.query,
            seed_urn=args.seed_urn,
            pii_keywords=["customer_id", "email", "name", "phone", "address"],
            max_assets=args.max_assets,
        )

    graph = normalize_graph_discovery(evidence)
    request = ErasureRequest.from_subject_id(
        request_id=args.request_id,
        subject_id=args.subject_id,
    )
    plan = ErasurePlanner().plan(request, graph)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "graph-snapshot.json").write_text(
        graph.model_dump_json(indent=2), encoding="utf-8"
    )
    (args.output_dir / "erasure-plan.json").write_text(
        plan.model_dump_json(indent=2), encoding="utf-8"
    )
    (args.output_dir / "erasure-plan.md").write_text(render_markdown(plan), encoding="utf-8")

    return {
        "assets": len(graph.assets),
        "datahub_tool_calls": len(evidence.tool_calls),
        "edges": len(graph.edges),
        "held_assets": plan.coverage.held_assets,
        "mutations_enabled": False,
        "output_dir": str(args.output_dir),
        "pii_fields": plan.coverage.pii_fields,
        "plan_status": plan.status.value,
        "read_tools": sorted(set(evidence.tool_calls)),
        "subject_ref": plan.request.subject_ref,
    }


def main() -> None:
    print(json.dumps(asyncio.run(run(parse_args())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

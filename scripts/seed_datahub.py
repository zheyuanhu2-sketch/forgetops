"""Seed the synthetic ForgetOps graph into an explicitly approved DataHub target."""

from __future__ import annotations

import argparse
from pathlib import Path

from forgetops.datahub_seed import (
    build_seed_manifest,
    default_token,
    receipt_json,
    seed_datahub,
    write_seed_receipt,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graph",
        type=Path,
        default=Path("examples/input/ecommerce-privacy-graph.json"),
    )
    parser.add_argument("--gms-url", default="http://localhost:8080")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--allow-remote", action="store_true")
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path("artifacts/runtime/datahub-seed-receipt.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    graph, manifest = build_seed_manifest(args.graph)
    receipt = seed_datahub(
        graph,
        manifest,
        approved=args.approve,
        gms_url=args.gms_url,
        token=default_token(),
        allow_remote=args.allow_remote,
    )
    print(receipt_json(receipt))
    if receipt.applied:
        write_seed_receipt(receipt, args.audit_output)


if __name__ == "__main__":
    main()

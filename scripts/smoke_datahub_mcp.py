"""Smoke-test the official DataHub MCP server against the local live runtime."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import warnings
from typing import Any

READ_TOOLS = {"get_entities", "get_lineage", "list_schema_fields", "search"}
MUTATION_TOOLS = {"add_structured_properties", "add_tags", "save_document"}


async def smoke() -> dict[str, Any]:
    os.environ.setdefault("DATAHUB_GMS_URL", "http://localhost:8080")
    os.environ.setdefault("TOOLS_IS_MUTATION_ENABLED", "false")
    warnings.filterwarnings("ignore", message="The new datahub SDK.*")
    logging.disable(logging.INFO)

    from fastmcp import Client
    from loguru import logger
    from mcp_server_datahub.__main__ import create_app

    logger.remove()

    async with Client(create_app()) as client:
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools}
        missing = sorted(READ_TOOLS - tool_names)
        if missing:
            raise RuntimeError(f"DataHub MCP is missing required read tools: {missing}")

        result = await client.call_tool(
            "search",
            arguments={"query": "*", "num_results": 1, "offset": 0},
        )
        if bool(getattr(result, "is_error", False)):
            raise RuntimeError("DataHub MCP search returned an error")

        mutations_enabled = bool(MUTATION_TOOLS & tool_names)
        if os.environ["TOOLS_IS_MUTATION_ENABLED"].lower() == "false" and mutations_enabled:
            raise RuntimeError("Mutation tools are exposed while mutations are disabled")

        return {
            "gms_url": os.environ["DATAHUB_GMS_URL"],
            "mutation_tools_exposed": mutations_enabled,
            "read_tools_verified": sorted(READ_TOOLS),
            "search_ok": True,
        }


def main() -> None:
    print(json.dumps(asyncio.run(smoke()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

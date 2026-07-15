"""Typed boundary around the official DataHub MCP server.

The gateway keeps MCP transport details out of the planning core and makes the mutation
approval boundary directly testable. It intentionally returns evidence-shaped payloads;
normalization into the ForgetOps domain graph is a separate step.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any, Protocol, cast

from pydantic import Field

from forgetops.models import StrictModel


class MutationApprovalRequired(PermissionError):
    """Raised when a caller attempts DataHub mutation without explicit approval."""


class MCPToolError(RuntimeError):
    """Raised when the MCP server returns an error or a non-JSON payload."""


class DiscoveryScopeExceeded(RuntimeError):
    """Raised rather than silently truncating a privacy discovery result."""


class ToolSession(Protocol):
    async def call_tool(self, name: str, *, arguments: dict[str, Any]) -> object: ...


class DiscoveryEvidence(StrictModel):
    query: str
    seed_urn: str
    search: dict[str, Any]
    entity: dict[str, Any]
    schema_fields: dict[str, Any]
    downstream_lineage: dict[str, Any]
    tool_calls: list[str] = Field(min_length=4)


class GraphDiscoveryEvidence(StrictModel):
    query: str
    seed_urn: str
    search: dict[str, Any]
    entities: list[dict[str, Any]] = Field(min_length=1)
    schema_fields_by_urn: dict[str, dict[str, Any]]
    lineage_by_urn: dict[str, dict[str, Any]]
    column_lineage_by_urn: dict[str, dict[str, dict[str, Any]]]
    tool_calls: list[str] = Field(min_length=4)


class WriteBackReceipt(StrictModel):
    case_id: str
    idempotency_key: str
    document_urn: str
    entity_urns: list[str] = Field(min_length=1)
    tag_result: dict[str, Any]
    property_result: dict[str, Any]
    document_result: dict[str, Any]
    tool_calls: list[str] = Field(min_length=3)


class WriteBackVerification(StrictModel):
    case_id: str
    document_urn: str
    entity_urns: list[str] = Field(min_length=1)
    verified_entity_urns: list[str] = Field(min_length=1)
    document_found: bool
    document_content_verified: bool
    tool_calls: list[str] = Field(min_length=3)


class DataHubMCPGateway:
    """Call official DataHub MCP tools through any compatible FastMCP session."""

    def __init__(self, session: ToolSession) -> None:
        self._session = session

    async def discover(
        self,
        *,
        query: str,
        seed_urn: str,
        pii_keywords: list[str],
        max_hops: int = 2,
    ) -> DiscoveryEvidence:
        if not query.strip():
            raise ValueError("query must not be empty")
        if not seed_urn.startswith("urn:li:"):
            raise ValueError("seed_urn must be a DataHub URN")
        if not pii_keywords:
            raise ValueError("at least one PII keyword is required")
        if max_hops not in (1, 2):
            raise ValueError("max_hops must be 1 or 2 for bounded discovery")

        search = await self._call_json(
            "search",
            {
                "query": query,
                "filter": "entity_type = DATASET",
                "num_results": 50,
                "offset": 0,
            },
        )
        # The official tool returns an object for one URN and an array for a URN list.
        # Discovery models one seed entity, so use the single-URN contract explicitly.
        entity = await self._call_json("get_entities", {"urns": seed_urn})
        schema = await self._call_json(
            "list_schema_fields",
            {
                "urn": seed_urn,
                "keywords": pii_keywords,
                "limit": 100,
                "offset": 0,
            },
        )
        downstream_lineage = await self._call_json(
            "get_lineage",
            {
                "urn": seed_urn,
                "column": None,
                "upstream": False,
                "max_hops": max_hops,
                "max_results": 100,
                "offset": 0,
            },
        )
        return DiscoveryEvidence(
            query=query,
            seed_urn=seed_urn,
            search=search,
            entity=entity,
            schema_fields=schema,
            downstream_lineage=downstream_lineage,
            tool_calls=["search", "get_entities", "list_schema_fields", "get_lineage"],
        )

    async def discover_graph(
        self,
        *,
        query: str,
        seed_urn: str,
        pii_keywords: list[str],
        max_assets: int = 20,
    ) -> GraphDiscoveryEvidence:
        """Discover all matching roots and their direct downstream edges.

        Privacy scope must never be silently truncated. Search results above ``max_assets``
        therefore stop the workflow for a human to narrow or explicitly expand the bound.
        """

        if not query.strip():
            raise ValueError("query must not be empty")
        if not seed_urn.startswith("urn:li:dataset:"):
            raise ValueError("seed_urn must be a DataHub dataset URN")
        if not pii_keywords:
            raise ValueError("at least one PII keyword is required")
        if not 1 <= max_assets <= 50:
            raise ValueError("max_assets must be between 1 and 50")

        tool_calls: list[str] = []
        search = await self._call_json(
            "search",
            {
                "query": query,
                "filter": "entity_type = DATASET",
                "num_results": max_assets,
                "offset": 0,
            },
        )
        tool_calls.append("search")
        total = search.get("total", 0)
        if not isinstance(total, int):
            raise MCPToolError("DataHub MCP search returned a non-integer total")
        if total > max_assets:
            raise DiscoveryScopeExceeded(
                f"DataHub search matched {total} assets, above the safe bound of {max_assets}"
            )

        dataset_urns = {seed_urn}
        search_results = search.get("searchResults", [])
        if not isinstance(search_results, list):
            raise MCPToolError("DataHub MCP search returned invalid searchResults")
        for result in search_results:
            if not isinstance(result, Mapping):
                continue
            entity = result.get("entity")
            if not isinstance(entity, Mapping):
                continue
            urn = entity.get("urn")
            if isinstance(urn, str) and urn.startswith("urn:li:dataset:"):
                dataset_urns.add(urn)
        if len(dataset_urns) > max_assets:
            raise DiscoveryScopeExceeded(
                f"DataHub search plus the verified seed produced {len(dataset_urns)} assets, "
                f"above the safe bound of {max_assets}"
            )
        ordered_dataset_urns = sorted(dataset_urns)

        entities = await self._call_json_array("get_entities", {"urns": ordered_dataset_urns})
        tool_calls.append("get_entities")
        self._raise_on_entity_errors(entities)

        entities_by_urn = {
            str(entity["urn"]): entity for entity in entities if isinstance(entity.get("urn"), str)
        }
        missing = sorted(set(ordered_dataset_urns) - entities_by_urn.keys())
        if missing:
            raise MCPToolError(f"DataHub MCP omitted discovered entities: {missing}")

        schema_fields_by_urn: dict[str, dict[str, Any]] = {}
        lineage_by_urn: dict[str, dict[str, Any]] = {}
        column_lineage_by_urn: dict[str, dict[str, dict[str, Any]]] = {}
        for urn in ordered_dataset_urns:
            schema_fields_by_urn[urn] = await self._call_json(
                "list_schema_fields",
                {"urn": urn, "keywords": pii_keywords, "limit": 100, "offset": 0},
            )
            tool_calls.append("list_schema_fields")
            lineage_by_urn[urn] = await self._call_json(
                "get_lineage",
                {
                    "urn": urn,
                    "column": None,
                    "upstream": False,
                    "max_hops": 1,
                    "max_results": 100,
                    "offset": 0,
                },
            )
            tool_calls.append("get_lineage")

            subject_keys = self._structured_property_strings(
                entities_by_urn[urn], "forgetops.subjectKeys"
            )
            column_lineage_by_urn[urn] = {}
            for subject_key in subject_keys:
                column_lineage_by_urn[urn][subject_key] = await self._call_json(
                    "get_lineage",
                    {
                        "urn": urn,
                        "column": subject_key,
                        "upstream": False,
                        "max_hops": 1,
                        "max_results": 100,
                        "offset": 0,
                    },
                )
                tool_calls.append("get_lineage")

        related_urns = set(ordered_dataset_urns)
        for lineage in lineage_by_urn.values():
            related_urns.update(self._downstream_entity_urns(lineage))
        if len(related_urns) > max_assets:
            raise DiscoveryScopeExceeded(
                f"DataHub lineage expanded to {len(related_urns)} assets, "
                f"above the safe bound of {max_assets}"
            )

        extra_urns = sorted(related_urns - set(ordered_dataset_urns))
        if extra_urns:
            extra_entities = await self._call_json_array("get_entities", {"urns": extra_urns})
            tool_calls.append("get_entities")
            self._raise_on_entity_errors(extra_entities)
            entities.extend(extra_entities)

        return GraphDiscoveryEvidence(
            query=query,
            seed_urn=seed_urn,
            search=search,
            entities=entities,
            schema_fields_by_urn=schema_fields_by_urn,
            lineage_by_urn=lineage_by_urn,
            column_lineage_by_urn=column_lineage_by_urn,
            tool_calls=tool_calls,
        )

    async def verify_case_evidence(
        self,
        *,
        case_id: str,
        entity_urns: list[str],
        case_tag_urn: str,
        case_property_urn: str,
        document_urn: str,
    ) -> WriteBackVerification:
        """Read evidence back through official MCP tools and fail closed on any mismatch."""
        if not case_id.strip():
            raise ValueError("case_id must not be empty")
        if not entity_urns or any(not urn.startswith("urn:li:") for urn in entity_urns):
            raise ValueError("entity_urns must contain DataHub URNs")
        if not case_tag_urn.startswith("urn:li:tag:"):
            raise ValueError("case_tag_urn must be a DataHub tag URN")
        if not case_property_urn.startswith("urn:li:structuredProperty:"):
            raise ValueError("case_property_urn must be a DataHub structured property URN")
        if not document_urn.startswith("urn:li:document:"):
            raise ValueError("document_urn must be a DataHub document URN")

        entities = await self._call_json_array("get_entities", {"urns": entity_urns})
        self._raise_on_entity_errors(entities)
        entities_by_urn = {
            str(entity["urn"]): entity for entity in entities if isinstance(entity.get("urn"), str)
        }
        missing_entities = sorted(set(entity_urns) - entities_by_urn.keys())
        if missing_entities:
            raise MCPToolError(f"DataHub MCP omitted write-back entities: {missing_entities}")

        evidence_mismatches: list[str] = []
        for urn in entity_urns:
            entity = entities_by_urn[urn]
            if case_tag_urn not in self._tag_urns(entity):
                evidence_mismatches.append(f"{urn}: missing case tag")
            if case_id not in self._structured_property_strings_by_urn(entity, case_property_urn):
                evidence_mismatches.append(f"{urn}: missing case ID property")
        if evidence_mismatches:
            raise MCPToolError(
                "DataHub write-back verification failed: " + "; ".join(evidence_mismatches)
            )

        document_search = await self._call_json(
            "search_documents",
            {
                "query": f'"{case_id}"',
                "semantic_query": None,
                "filter": None,
                "num_results": 50,
                "offset": 0,
            },
        )
        search_results = document_search.get("searchResults")
        document_found = False
        if isinstance(search_results, list):
            for result in search_results:
                if not isinstance(result, Mapping):
                    continue
                document_entity = result.get("entity")
                if (
                    isinstance(document_entity, Mapping)
                    and document_entity.get("urn") == document_urn
                ):
                    document_found = True
                    break
        if not document_found:
            raise MCPToolError("DataHub document search did not return the evidence document")

        document_content = await self._call_json(
            "grep_documents",
            {
                "urns": [document_urn],
                "pattern": case_id,
                "context_chars": 120,
                "max_matches_per_doc": 3,
                "start_offset": 0,
            },
        )
        content_results = document_content.get("results")
        document_content_verified = False
        if isinstance(content_results, list):
            for result in content_results:
                if (
                    isinstance(result, Mapping)
                    and result.get("urn") == document_urn
                    and isinstance(result.get("matches"), list)
                    and bool(result["matches"])
                ):
                    document_content_verified = True
                    break
        if not document_content_verified:
            raise MCPToolError("DataHub evidence document did not contain the case ID")

        return WriteBackVerification(
            case_id=case_id,
            document_urn=document_urn,
            entity_urns=entity_urns,
            verified_entity_urns=sorted(entities_by_urn),
            document_found=document_found,
            document_content_verified=document_content_verified,
            tool_calls=["get_entities", "search_documents", "grep_documents"],
        )

    async def write_case_evidence(
        self,
        *,
        approved: bool,
        case_id: str,
        idempotency_key: str,
        entity_urns: list[str],
        case_tag_urn: str,
        case_property_urn: str,
        document_title: str,
        document_content: str,
        document_urn: str | None = None,
    ) -> WriteBackReceipt:
        if not approved:
            raise MutationApprovalRequired("DataHub write-back requires explicit case approval")
        if not case_id.strip():
            raise ValueError("case_id must not be empty")
        if not idempotency_key.strip():
            raise ValueError("idempotency_key must not be empty")
        if not entity_urns:
            raise ValueError("at least one entity URN is required")
        if any(not urn.startswith("urn:li:") for urn in entity_urns):
            raise ValueError("all entity identifiers must be DataHub URNs")
        if not case_tag_urn.startswith("urn:li:tag:"):
            raise ValueError("case_tag_urn must be a DataHub tag URN")
        if not case_property_urn.startswith("urn:li:structuredProperty:"):
            raise ValueError("case_property_urn must be a DataHub structured property URN")
        if not document_title.strip() or not document_content.strip():
            raise ValueError("document title and content must not be empty")
        if document_urn is not None and not document_urn.startswith("urn:li:document:"):
            raise ValueError("document_urn must be a DataHub document URN")

        tag_result = await self._call_json(
            "add_tags",
            {"tag_urns": [case_tag_urn], "entity_urns": entity_urns},
        )
        property_result = await self._call_json(
            "add_structured_properties",
            {
                "property_values": {case_property_urn: [case_id]},
                "entity_urns": entity_urns,
            },
        )
        document_arguments: dict[str, Any] = {
            "document_type": "Context",
            "title": document_title,
            "content": document_content,
            "topics": ["forgetops", "privacy-operations", "right-to-erasure"],
            "related_assets": entity_urns,
        }
        if document_urn is not None:
            document_arguments["urn"] = document_urn
        document_result = await self._call_json("save_document", document_arguments)
        returned_document_urn = document_result.get("urn")
        if not isinstance(returned_document_urn, str) or not returned_document_urn.startswith(
            "urn:li:document:"
        ):
            raise MCPToolError("DataHub MCP save_document returned no document URN")
        return WriteBackReceipt(
            case_id=case_id,
            idempotency_key=idempotency_key,
            document_urn=returned_document_urn,
            entity_urns=entity_urns,
            tag_result=tag_result,
            property_result=property_result,
            document_result=document_result,
            tool_calls=["add_tags", "add_structured_properties", "save_document"],
        )

    async def _call_json(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = await self._session.call_tool(tool_name, arguments=arguments)
        if isinstance(result, Mapping):
            payload = dict(result)
            self._raise_on_failed_payload(tool_name, payload)
            return payload
        if bool(getattr(result, "is_error", False)):
            detail = getattr(result, "data", None)
            raise MCPToolError(f"DataHub MCP tool {tool_name} failed: {detail!r}")

        data = getattr(result, "data", None)
        parsed = self._parse_json_object(data)
        if parsed is not None:
            self._raise_on_failed_payload(tool_name, parsed)
            return parsed

        content = getattr(result, "content", None)
        if isinstance(content, list) and content:
            parsed = self._parse_json_object(getattr(content[0], "text", None))
            if parsed is not None:
                self._raise_on_failed_payload(tool_name, parsed)
                return parsed
        raise MCPToolError(f"DataHub MCP tool {tool_name} returned no JSON object")

    async def _call_json_array(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> list[dict[str, Any]]:
        result = await self._session.call_tool(tool_name, arguments=arguments)
        if bool(getattr(result, "is_error", False)):
            detail = getattr(result, "data", None)
            raise MCPToolError(f"DataHub MCP tool {tool_name} failed: {detail!r}")

        value: object = result if isinstance(result, list) else getattr(result, "data", None)
        parsed = self._parse_json_array(value)
        if parsed is None:
            content = getattr(result, "content", None)
            if isinstance(content, list) and content:
                parsed = self._parse_json_array(getattr(content[0], "text", None))
        if parsed is None:
            raise MCPToolError(f"DataHub MCP tool {tool_name} returned no JSON array")
        return parsed

    @staticmethod
    def _raise_on_failed_payload(tool_name: str, payload: dict[str, Any]) -> None:
        if payload.get("success") is False:
            detail = payload.get("message", "operation reported success=false")
            raise MCPToolError(f"DataHub MCP tool {tool_name} failed: {detail}")

    @staticmethod
    def _parse_json_object(value: object) -> dict[str, Any] | None:
        if isinstance(value, Mapping):
            return dict(value)
        if not isinstance(value, str):
            return None
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict):
            return None
        return cast(dict[str, Any], parsed)

    @staticmethod
    def _parse_json_array(value: object) -> list[dict[str, Any]] | None:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return None
        if not isinstance(value, list) or any(not isinstance(item, Mapping) for item in value):
            return None
        return [dict(item) for item in value]

    @staticmethod
    def _raise_on_entity_errors(entities: list[dict[str, Any]]) -> None:
        errors = [str(entity["error"]) for entity in entities if "error" in entity]
        if errors:
            raise MCPToolError(f"DataHub MCP entity lookup failed: {'; '.join(errors)}")

    @staticmethod
    def _downstream_entity_urns(lineage: dict[str, Any]) -> set[str]:
        urns: set[str] = set()
        downstreams = lineage.get("downstreams")
        if not isinstance(downstreams, Mapping):
            return urns
        results = downstreams.get("searchResults")
        if not isinstance(results, list):
            return urns
        for result in results:
            if not isinstance(result, Mapping):
                continue
            entity = result.get("entity")
            if not isinstance(entity, Mapping):
                continue
            urn = entity.get("urn")
            if isinstance(urn, str):
                urns.add(urn)
        return urns

    @staticmethod
    def _structured_property_strings(entity: dict[str, Any], qualified_name: str) -> list[str]:
        structured = entity.get("structuredProperties")
        if not isinstance(structured, Mapping):
            return []
        properties = structured.get("properties")
        if not isinstance(properties, list):
            return []
        values: list[str] = []
        for item in properties:
            if not isinstance(item, Mapping):
                continue
            property_entity = item.get("structuredProperty")
            if not isinstance(property_entity, Mapping):
                continue
            definition = property_entity.get("definition")
            if (
                not isinstance(definition, Mapping)
                or definition.get("qualifiedName") != qualified_name
            ):
                continue
            raw_values = item.get("values")
            if not isinstance(raw_values, list):
                continue
            for raw_value in raw_values:
                if isinstance(raw_value, Mapping) and isinstance(raw_value.get("stringValue"), str):
                    values.append(str(raw_value["stringValue"]))
        return values

    @staticmethod
    def _structured_property_strings_by_urn(entity: dict[str, Any], property_urn: str) -> list[str]:
        structured = entity.get("structuredProperties")
        if not isinstance(structured, Mapping):
            return []
        properties = structured.get("properties")
        if not isinstance(properties, list):
            return []
        values: list[str] = []
        for item in properties:
            if not isinstance(item, Mapping):
                continue
            property_entity = item.get("structuredProperty")
            if (
                not isinstance(property_entity, Mapping)
                or property_entity.get("urn") != property_urn
            ):
                continue
            raw_values = item.get("values")
            if not isinstance(raw_values, list):
                continue
            for raw_value in raw_values:
                if isinstance(raw_value, Mapping) and isinstance(raw_value.get("stringValue"), str):
                    values.append(str(raw_value["stringValue"]))
        return values

    @staticmethod
    def _tag_urns(entity: dict[str, Any]) -> set[str]:
        tags = entity.get("tags")
        if not isinstance(tags, Mapping) or not isinstance(tags.get("tags"), list):
            return set()
        urns: set[str] = set()
        for item in tags["tags"]:
            if not isinstance(item, Mapping):
                continue
            tag = item.get("tag")
            if isinstance(tag, Mapping) and isinstance(tag.get("urn"), str):
                urns.add(str(tag["urn"]))
        return urns


@asynccontextmanager
async def connect_local_datahub() -> AsyncIterator[DataHubMCPGateway]:
    """Connect to DataHub through the official in-process MCP server.

    DataHub connection settings are read by the official server from
    `DATAHUB_GMS_URL` and `DATAHUB_GMS_TOKEN`.
    """

    try:
        from fastmcp import Client
        from mcp_server_datahub.__main__ import create_app
    except ImportError as error:  # pragma: no cover - depends on optional install
        raise RuntimeError(
            "Install the DataHub integration with `uv sync --extra datahub`"
        ) from error

    async with Client(create_app()) as client:
        yield DataHubMCPGateway(client)

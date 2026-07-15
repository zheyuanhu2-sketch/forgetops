from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from forgetops.datahub_mcp import (
    DataHubMCPGateway,
    DiscoveryScopeExceeded,
    MCPToolError,
    MutationApprovalRequired,
)

SEED_URN = "urn:li:dataset:(urn:li:dataPlatform:postgres,ecommerce.customers,PROD)"
ANALYTICS_URN = "urn:li:dataset:(urn:li:dataPlatform:snowflake,analytics.customer_360,PROD)"
DASHBOARD_URN = "urn:li:dashboard:(looker,customer_retention_overview)"
IDEMPOTENCY_KEY = "DSR-2026-0042:writeback:v1"


@dataclass
class FakeResult:
    data: object
    is_error: bool = False


@dataclass
class FakeTextContent:
    text: str


@dataclass
class FakeContentResult:
    data: object
    content: list[FakeTextContent]
    is_error: bool = False


class FakeSession:
    def __init__(self, responses: dict[str, object] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call_tool(self, name: str, *, arguments: dict[str, Any]) -> object:
        self.calls.append((name, arguments))
        return self.responses.get(name, FakeResult({"tool": name, "ok": True}))


def _graph_entity(urn: str) -> dict[str, object]:
    entity: dict[str, object] = {"urn": urn}
    if urn.startswith("urn:li:dataset:"):
        entity["structuredProperties"] = {
            "properties": [
                {
                    "structuredProperty": {
                        "definition": {"qualifiedName": "forgetops.subjectKeys"}
                    },
                    "values": [{"stringValue": "customer_id"}],
                }
            ]
        }
    return entity


class GraphSession:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call_tool(self, name: str, *, arguments: dict[str, Any]) -> object:
        self.calls.append((name, arguments))
        if name == "search":
            return {
                "total": 2,
                "searchResults": [
                    {"entity": {"urn": SEED_URN}},
                    {"entity": {"urn": ANALYTICS_URN}},
                ],
            }
        if name == "get_entities":
            urns = arguments["urns"]
            assert isinstance(urns, list)
            return FakeResult([_graph_entity(str(urn)) for urn in urns])
        if name == "list_schema_fields":
            return {"urn": arguments["urn"], "fields": []}
        if name == "get_lineage":
            urn = arguments["urn"]
            column = arguments["column"]
            if urn == SEED_URN:
                target = ANALYTICS_URN
            elif column is None:
                target = DASHBOARD_URN
            else:
                return {"downstreams": {"searchResults": []}}
            result: dict[str, object] = {"degree": 1, "entity": {"urn": target}}
            if column is not None:
                result["lineageColumns"] = ["customer_id"]
            return {"downstreams": {"searchResults": [result]}}
        raise AssertionError(f"unexpected tool: {name}")


def test_discovery_uses_bounded_official_read_tools() -> None:
    session = FakeSession()
    gateway = DataHubMCPGateway(session)

    evidence = asyncio.run(
        gateway.discover(
            query="/q tag:PII customer",
            seed_urn=SEED_URN,
            pii_keywords=["customer_id", "email"],
            max_hops=2,
        )
    )

    assert evidence.tool_calls == [
        "search",
        "get_entities",
        "list_schema_fields",
        "get_lineage",
    ]
    assert [name for name, _ in session.calls] == evidence.tool_calls
    assert session.calls[1][1] == {"urns": SEED_URN}
    lineage_args = session.calls[-1][1]
    assert lineage_args["upstream"] is False
    assert lineage_args["max_hops"] == 2
    assert lineage_args["max_results"] == 100


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"query": " "}, "query must not be empty"),
        ({"seed_urn": "customers"}, "seed_urn must be a DataHub URN"),
        ({"pii_keywords": []}, "at least one PII keyword"),
        ({"max_hops": 3}, "max_hops must be 1 or 2"),
    ],
)
def test_discovery_rejects_unbounded_or_incomplete_inputs(
    overrides: dict[str, Any], message: str
) -> None:
    session = FakeSession()
    gateway = DataHubMCPGateway(session)
    arguments: dict[str, Any] = {
        "query": "customer",
        "seed_urn": SEED_URN,
        "pii_keywords": ["customer_id"],
        "max_hops": 2,
    }
    arguments.update(overrides)

    with pytest.raises(ValueError, match=message):
        asyncio.run(gateway.discover(**arguments))

    assert session.calls == []


def test_graph_discovery_collects_all_roots_direct_edges_and_subject_lineage() -> None:
    session = GraphSession()
    evidence = asyncio.run(
        DataHubMCPGateway(session).discover_graph(
            query="customer_id",
            seed_urn=SEED_URN,
            pii_keywords=["customer_id", "email"],
            max_assets=10,
        )
    )

    assert {entity["urn"] for entity in evidence.entities} == {
        SEED_URN,
        ANALYTICS_URN,
        DASHBOARD_URN,
    }
    assert set(evidence.schema_fields_by_urn) == {SEED_URN, ANALYTICS_URN}
    assert evidence.column_lineage_by_urn[SEED_URN]["customer_id"]["downstreams"]
    assert evidence.lineage_by_urn[ANALYTICS_URN]["downstreams"]
    assert len(evidence.tool_calls) == 9
    lineage_calls = [arguments for name, arguments in session.calls if name == "get_lineage"]
    assert all(arguments["max_hops"] == 1 for arguments in lineage_calls)


@pytest.mark.parametrize(
    "overrides",
    [
        {"query": " "},
        {"seed_urn": "urn:li:dashboard:(looker,demo)"},
        {"pii_keywords": []},
        {"max_assets": 0},
        {"max_assets": 51},
    ],
)
def test_graph_discovery_validates_safety_bounds(overrides: dict[str, Any]) -> None:
    arguments: dict[str, Any] = {
        "query": "customer_id",
        "seed_urn": SEED_URN,
        "pii_keywords": ["customer_id"],
        "max_assets": 20,
    }
    arguments.update(overrides)
    session = FakeSession()

    with pytest.raises(ValueError):
        asyncio.run(DataHubMCPGateway(session).discover_graph(**arguments))
    assert session.calls == []


def test_graph_discovery_refuses_to_truncate_search_scope() -> None:
    session = FakeSession(responses={"search": {"total": 21, "searchResults": []}})

    with pytest.raises(DiscoveryScopeExceeded, match="21 assets"):
        asyncio.run(
            DataHubMCPGateway(session).discover_graph(
                query="customer_id",
                seed_urn=SEED_URN,
                pii_keywords=["customer_id"],
                max_assets=20,
            )
        )

    assert [name for name, _ in session.calls] == ["search"]


def test_graph_discovery_counts_verified_seed_inside_scope_bound() -> None:
    session = FakeSession(
        responses={
            "search": {
                "total": 1,
                "searchResults": [{"entity": {"urn": ANALYTICS_URN}}],
            }
        }
    )

    with pytest.raises(DiscoveryScopeExceeded, match="verified seed"):
        asyncio.run(
            DataHubMCPGateway(session).discover_graph(
                query="customer_id",
                seed_urn=SEED_URN,
                pii_keywords=["customer_id"],
                max_assets=1,
            )
        )


def test_mutations_are_impossible_without_explicit_approval() -> None:
    session = FakeSession()
    gateway = DataHubMCPGateway(session)

    with pytest.raises(MutationApprovalRequired):
        asyncio.run(
            gateway.write_case_evidence(
                approved=False,
                case_id="DSR-2026-0042",
                idempotency_key=IDEMPOTENCY_KEY,
                entity_urns=[SEED_URN],
                case_tag_urn="urn:li:tag:ForgetOps.Verified",
                case_property_urn="urn:li:structuredProperty:forgetops.caseId",
                document_title="ForgetOps case DSR-2026-0042",
                document_content="Verified synthetic evidence.",
            )
        )

    assert session.calls == []


@pytest.mark.parametrize(
    ("entity_urns", "message"),
    [
        ([], "at least one entity URN"),
        (["customers"], "must be DataHub URNs"),
    ],
)
def test_approved_writeback_still_validates_entity_urns(
    entity_urns: list[str], message: str
) -> None:
    session = FakeSession()
    gateway = DataHubMCPGateway(session)

    with pytest.raises(ValueError, match=message):
        asyncio.run(
            gateway.write_case_evidence(
                approved=True,
                case_id="DSR-2026-0042",
                idempotency_key=IDEMPOTENCY_KEY,
                entity_urns=entity_urns,
                case_tag_urn="urn:li:tag:ForgetOps.Verified",
                case_property_urn="urn:li:structuredProperty:forgetops.caseId",
                document_title="ForgetOps case DSR-2026-0042",
                document_content="Verified synthetic evidence.",
            )
        )

    assert session.calls == []


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"case_id": " "}, "case_id"),
        ({"idempotency_key": " "}, "idempotency_key"),
        ({"case_tag_urn": "PII"}, "tag URN"),
        ({"case_property_urn": "caseId"}, "structured property URN"),
        ({"document_title": " "}, "title and content"),
        ({"document_content": " "}, "title and content"),
    ],
)
def test_approved_writeback_validates_audit_contract(
    overrides: dict[str, Any], message: str
) -> None:
    arguments: dict[str, Any] = {
        "approved": True,
        "case_id": "DSR-2026-0042",
        "idempotency_key": IDEMPOTENCY_KEY,
        "entity_urns": [SEED_URN],
        "case_tag_urn": "urn:li:tag:ForgetOps.Verified",
        "case_property_urn": "urn:li:structuredProperty:forgetops.caseId",
        "document_title": "ForgetOps case DSR-2026-0042",
        "document_content": "Verified synthetic evidence.",
    }
    arguments.update(overrides)
    session = FakeSession()

    with pytest.raises(ValueError, match=message):
        asyncio.run(DataHubMCPGateway(session).write_case_evidence(**arguments))
    assert session.calls == []


def test_approved_write_back_uses_three_auditable_mutation_tools() -> None:
    session = FakeSession()
    gateway = DataHubMCPGateway(session)

    receipt = asyncio.run(
        gateway.write_case_evidence(
            approved=True,
            case_id="DSR-2026-0042",
            idempotency_key=IDEMPOTENCY_KEY,
            entity_urns=[SEED_URN],
            case_tag_urn="urn:li:tag:ForgetOps.Verified",
            case_property_urn="urn:li:structuredProperty:forgetops.caseId",
            document_title="ForgetOps case DSR-2026-0042",
            document_content="Verified synthetic evidence.",
        )
    )

    assert receipt.tool_calls == [
        "add_tags",
        "add_structured_properties",
        "save_document",
    ]
    assert [name for name, _ in session.calls] == receipt.tool_calls
    assert session.calls[0][1]["entity_urns"] == [SEED_URN]
    assert session.calls[1][1]["property_values"] == {
        "urn:li:structuredProperty:forgetops.caseId": ["DSR-2026-0042"]
    }
    assert session.calls[2][1]["related_assets"] == [SEED_URN]
    assert session.calls[2][1]["urn"] == receipt.document_urn
    assert receipt.document_urn.startswith("urn:li:document:forgetops-")
    assert receipt.idempotency_key == IDEMPOTENCY_KEY


def test_write_back_retry_reuses_the_same_document_urn() -> None:
    first_session = FakeSession()
    second_session = FakeSession()

    arguments = {
        "approved": True,
        "case_id": "DSR-2026-0042",
        "idempotency_key": IDEMPOTENCY_KEY,
        "entity_urns": [SEED_URN],
        "case_tag_urn": "urn:li:tag:ForgetOps.Verified",
        "case_property_urn": "urn:li:structuredProperty:forgetops.caseId",
        "document_title": "ForgetOps case DSR-2026-0042",
        "document_content": "Verified synthetic evidence.",
    }
    first = asyncio.run(DataHubMCPGateway(first_session).write_case_evidence(**arguments))
    second = asyncio.run(DataHubMCPGateway(second_session).write_case_evidence(**arguments))

    assert first.document_urn == second.document_urn
    assert first_session.calls[2][1]["urn"] == second_session.calls[2][1]["urn"]


def test_mcp_error_result_is_not_silently_accepted() -> None:
    session = FakeSession(responses={"search": FakeResult("permission denied", is_error=True)})
    gateway = DataHubMCPGateway(session)

    with pytest.raises(MCPToolError, match="permission denied"):
        asyncio.run(
            gateway.discover(
                query="customer",
                seed_urn=SEED_URN,
                pii_keywords=["customer_id"],
            )
        )


def test_mcp_success_false_payload_is_not_silently_accepted() -> None:
    session = FakeSession(responses={"search": {"success": False, "message": "query rejected"}})
    gateway = DataHubMCPGateway(session)

    with pytest.raises(MCPToolError, match="query rejected"):
        asyncio.run(
            gateway.discover(
                query="customer",
                seed_urn=SEED_URN,
                pii_keywords=["customer_id"],
            )
        )


def test_mcp_text_content_fallback_requires_a_json_object() -> None:
    session = FakeSession(
        responses={
            "search": FakeContentResult(
                data=None,
                content=[FakeTextContent('{"source": "content"}')],
            )
        }
    )
    gateway = DataHubMCPGateway(session)

    evidence = asyncio.run(
        gateway.discover(
            query="customer",
            seed_urn=SEED_URN,
            pii_keywords=["customer_id"],
        )
    )

    assert evidence.search == {"source": "content"}


def test_mcp_non_json_result_is_rejected() -> None:
    session = FakeSession(responses={"search": FakeResult("not-json")})
    gateway = DataHubMCPGateway(session)

    with pytest.raises(MCPToolError, match="returned no JSON object"):
        asyncio.run(
            gateway.discover(
                query="customer",
                seed_urn=SEED_URN,
                pii_keywords=["customer_id"],
            )
        )


def test_mcp_json_array_parser_accepts_only_object_arrays() -> None:
    assert DataHubMCPGateway._parse_json_array('[{"urn": "urn:li:dataset:test"}]') == [
        {"urn": "urn:li:dataset:test"}
    ]
    assert DataHubMCPGateway._parse_json_array("not-json") is None
    assert DataHubMCPGateway._parse_json_array('["not-an-object"]') is None

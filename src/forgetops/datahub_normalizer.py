"""Normalize official DataHub MCP responses into the deterministic domain graph."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from hashlib import sha256
from typing import Any

from forgetops.datahub_mcp import GraphDiscoveryEvidence
from forgetops.models import (
    AssetContext,
    AssetKind,
    GraphSnapshot,
    HandlingRule,
    LineageEdge,
)


class DataHubNormalizationError(ValueError):
    """Raised when DataHub evidence is incomplete or internally inconsistent."""


def normalize_graph_discovery(evidence: GraphDiscoveryEvidence) -> GraphSnapshot:
    """Build a strict graph without inventing policy that is absent from DataHub."""

    entities_by_urn = {
        str(entity["urn"]): entity
        for entity in evidence.entities
        if isinstance(entity.get("urn"), str)
    }
    if evidence.seed_urn not in entities_by_urn:
        raise DataHubNormalizationError("seed entity is missing from DataHub evidence")

    edge_mappings = _extract_edge_mappings(evidence)
    asset_by_urn: dict[str, AssetContext] = {}

    for urn, entity in sorted(entities_by_urn.items()):
        if _asset_kind(entity, urn) is AssetKind.DASHBOARD:
            continue
        schema = evidence.schema_fields_by_urn.get(urn)
        if schema is None:
            raise DataHubNormalizationError(f"schema evidence is missing for {urn}")
        asset_by_urn[urn] = _normalize_entity(entity, urn=urn, schema=schema)

    for urn, entity in sorted(entities_by_urn.items()):
        if _asset_kind(entity, urn) is not AssetKind.DASHBOARD:
            continue
        upstreams = [
            asset_by_urn[source]
            for source, target in edge_mappings
            if target == urn and source in asset_by_urn
        ]
        inherited_keys = sorted({key for asset in upstreams for key in asset.subject_keys})
        if not inherited_keys:
            raise DataHubNormalizationError(
                f"dashboard {urn} has no subject key evidence from direct DataHub lineage"
            )
        asset_by_urn[urn] = _normalize_entity(
            entity,
            urn=urn,
            schema=None,
            inherited_subject_keys=inherited_keys,
        )

    unknown_edge_urns = {urn for edge in edge_mappings for urn in edge if urn not in asset_by_urn}
    if unknown_edge_urns:
        raise DataHubNormalizationError(
            f"lineage references entities without evidence: {sorted(unknown_edge_urns)}"
        )

    edges: list[LineageEdge] = []
    for (upstream_urn, downstream_urn), field_mapping in sorted(edge_mappings.items()):
        if not field_mapping and asset_by_urn[downstream_urn].kind is AssetKind.DASHBOARD:
            field_mapping = {key: [key] for key in asset_by_urn[upstream_urn].subject_keys}
        edges.append(
            LineageEdge(
                upstream_urn=upstream_urn,
                downstream_urn=downstream_urn,
                field_mapping=field_mapping,
            )
        )

    snapshot_id = _snapshot_id(evidence)
    return GraphSnapshot(
        snapshot_id=snapshot_id,
        source="datahub_mcp_live",
        assets=[asset_by_urn[urn] for urn in sorted(asset_by_urn)],
        edges=edges,
    )


def _normalize_entity(
    entity: dict[str, Any],
    *,
    urn: str,
    schema: dict[str, Any] | None,
    inherited_subject_keys: list[str] | None = None,
) -> AssetContext:
    structured = _structured_property_values(entity)
    custom = _custom_properties(entity)
    tags = _tag_urns(entity)
    handling_rule = _handling_rule(structured, tags)
    legal_hold = _legal_hold(structured, tags)

    if schema is not None:
        pii_fields, tagged_subject_keys = _privacy_fields(schema)
        subject_keys = structured.get("forgetops.subjectKeys", tagged_subject_keys)
    else:
        subject_keys = inherited_subject_keys or []
        pii_fields = list(subject_keys)

    pii_fields = sorted(set(pii_fields) | set(subject_keys))
    subject_keys = sorted(set(subject_keys))
    if not pii_fields:
        raise DataHubNormalizationError(f"no PII field evidence found for {urn}")
    if not subject_keys:
        raise DataHubNormalizationError(f"no subject key evidence found for {urn}")

    action_tag = next((tag for tag in tags if ":ForgetOps.Action." in tag), None)
    policy_source = _first(structured.get("forgetops.policySource"))
    if policy_source is None:
        policy_source = (
            f"DataHub tag: {action_tag}"
            if action_tag is not None
            else "DataHub normalization safety gate"
        )
    policy_reason = custom.get("forgetops.policy_reason") or _description(entity)
    if not policy_reason:
        policy_reason = "Missing policy reason in DataHub; human review is required."
        handling_rule = HandlingRule.REVIEW

    try:
        return AssetContext(
            urn=urn,
            name=_entity_name(entity, urn),
            platform=_platform_name(entity),
            kind=_asset_kind(entity, urn),
            owners=_owners(entity),
            pii_fields=pii_fields,
            subject_keys=subject_keys,
            handling_rule=handling_rule,
            policy_reason=policy_reason,
            legal_hold=legal_hold,
            policy_source=policy_source,
        )
    except ValueError as error:
        raise DataHubNormalizationError(
            f"invalid DataHub policy evidence for {urn}: {error}"
        ) from error


def _extract_edge_mappings(
    evidence: GraphDiscoveryEvidence,
) -> dict[tuple[str, str], dict[str, list[str]]]:
    mappings: dict[tuple[str, str], dict[str, list[str]]] = {}
    for upstream_urn, lineage in evidence.lineage_by_urn.items():
        for result in _downstream_results(lineage):
            entity = _mapping(result.get("entity"))
            downstream_urn = entity.get("urn")
            degree = result.get("degree")
            if isinstance(downstream_urn, str) and degree == 1:
                mappings[(upstream_urn, downstream_urn)] = {}

    field_values: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for upstream_urn, by_field in evidence.column_lineage_by_urn.items():
        for upstream_field, lineage in by_field.items():
            for result in _downstream_results(lineage):
                entity = _mapping(result.get("entity"))
                downstream_urn = entity.get("urn")
                if not isinstance(downstream_urn, str):
                    continue
                edge_key = (upstream_urn, downstream_urn)
                if edge_key not in mappings:
                    continue
                columns = result.get("lineageColumns")
                if isinstance(columns, list):
                    field_values[edge_key][upstream_field].update(
                        str(column) for column in columns if isinstance(column, str)
                    )

    for edge_key, field_sets in field_values.items():
        mappings[edge_key] = {
            field: sorted(columns) for field, columns in sorted(field_sets.items())
        }
    return mappings


def _downstream_results(lineage: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    downstreams = _mapping(lineage.get("downstreams"))
    results = downstreams.get("searchResults")
    if not isinstance(results, list):
        return []
    return [item for item in results if isinstance(item, Mapping)]


def _structured_property_values(entity: Mapping[str, Any]) -> dict[str, list[str]]:
    values_by_name: dict[str, list[str]] = {}
    structured = _mapping(entity.get("structuredProperties"))
    properties = structured.get("properties")
    if not isinstance(properties, list):
        return values_by_name
    for item in properties:
        entry = _mapping(item)
        property_entity = _mapping(entry.get("structuredProperty"))
        definition = _mapping(property_entity.get("definition"))
        qualified_name = definition.get("qualifiedName")
        if not isinstance(qualified_name, str):
            continue
        raw_values = entry.get("values")
        if not isinstance(raw_values, list):
            continue
        values: list[str] = []
        for raw_value in raw_values:
            value = _mapping(raw_value)
            string_value = value.get("stringValue")
            if isinstance(string_value, str):
                values.append(string_value)
        values_by_name[qualified_name] = values
    return values_by_name


def _custom_properties(entity: Mapping[str, Any]) -> dict[str, str]:
    properties = _mapping(entity.get("properties"))
    entries = properties.get("customProperties")
    if not isinstance(entries, list):
        return {}
    output: dict[str, str] = {}
    for entry in entries:
        item = _mapping(entry)
        key = item.get("key")
        value = item.get("value")
        if isinstance(key, str) and isinstance(value, str):
            output[key] = value
    return output


def _privacy_fields(schema: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    fields = schema.get("fields")
    if not isinstance(fields, list):
        raise DataHubNormalizationError("schema field response is not a list")
    pii_fields: list[str] = []
    subject_keys: list[str] = []
    for raw_field in fields:
        field = _mapping(raw_field)
        field_path = field.get("fieldPath")
        if not isinstance(field_path, str):
            continue
        tags = _field_tags(field)
        if any(tag.endswith("ForgetOps.PII") or tag.endswith("/ PII") for tag in tags):
            pii_fields.append(field_path)
        if any(
            tag.endswith("ForgetOps.SubjectKey") or tag.endswith("/ SubjectKey") for tag in tags
        ):
            subject_keys.append(field_path)
    return sorted(pii_fields), sorted(subject_keys)


def _field_tags(field: Mapping[str, Any]) -> list[str]:
    output = [str(tag) for tag in field.get("editedTags", []) if isinstance(tag, str)]
    tags = _mapping(field.get("tags")).get("tags")
    if isinstance(tags, list):
        for association in tags:
            tag = _mapping(_mapping(association).get("tag"))
            urn = tag.get("urn")
            if isinstance(urn, str):
                output.append(urn)
    return output


def _tag_urns(entity: Mapping[str, Any]) -> list[str]:
    tags = _mapping(entity.get("tags")).get("tags")
    if not isinstance(tags, list):
        return []
    output: list[str] = []
    for association in tags:
        tag = _mapping(_mapping(association).get("tag"))
        urn = tag.get("urn")
        if isinstance(urn, str):
            output.append(urn)
    return output


def _handling_rule(structured: Mapping[str, list[str]], tags: list[str]) -> HandlingRule:
    value = _first(structured.get("forgetops.handlingRule"))
    if value is None:
        action_tag = next((tag for tag in tags if ":ForgetOps.Action." in tag), None)
        value = action_tag.rsplit(".", 1)[-1] if action_tag else HandlingRule.REVIEW.value
    try:
        return HandlingRule(value)
    except ValueError as error:
        raise DataHubNormalizationError(f"unknown handling rule in DataHub: {value}") from error


def _legal_hold(structured: Mapping[str, list[str]], tags: list[str]) -> bool:
    value = _first(structured.get("forgetops.legalHold"))
    if value is None:
        return any(tag.endswith(":ForgetOps.LegalHold") for tag in tags)
    if value not in {"true", "false"}:
        raise DataHubNormalizationError(f"invalid legal-hold value in DataHub: {value}")
    return value == "true"


def _owners(entity: Mapping[str, Any]) -> list[str]:
    ownership = _mapping(entity.get("ownership"))
    entries = ownership.get("owners")
    if not isinstance(entries, list):
        return []
    owners: list[str] = []
    for entry in entries:
        owner = _mapping(_mapping(entry).get("owner"))
        info = _mapping(owner.get("info"))
        properties = _mapping(owner.get("properties"))
        display = info.get("displayName") or properties.get("displayName") or owner.get("name")
        if isinstance(display, str) and display:
            owners.append(display)
    return sorted(set(owners))


def _entity_name(entity: Mapping[str, Any], urn: str) -> str:
    properties = _mapping(entity.get("properties"))
    for value in (properties.get("name"), entity.get("name"), entity.get("dashboardId")):
        if isinstance(value, str) and value:
            return value
    raise DataHubNormalizationError(f"entity name is missing for {urn}")


def _platform_name(entity: Mapping[str, Any]) -> str:
    platform = _mapping(entity.get("platform"))
    name = platform.get("name")
    if not isinstance(name, str) or not name:
        raise DataHubNormalizationError("entity platform name is missing")
    return name


def _asset_kind(entity: Mapping[str, Any], urn: str) -> AssetKind:
    if urn.startswith("urn:li:dashboard:") or entity.get("type") == "DASHBOARD":
        return AssetKind.DASHBOARD
    subtypes = _mapping(entity.get("subTypes")).get("typeNames")
    if isinstance(subtypes, list) and "Feature Table" in subtypes:
        return AssetKind.FEATURE_TABLE
    return AssetKind.DATASET


def _description(entity: Mapping[str, Any]) -> str | None:
    editable = _mapping(entity.get("editableProperties")).get("description")
    if isinstance(editable, str) and editable:
        return editable
    description = _mapping(entity.get("properties")).get("description")
    return description if isinstance(description, str) and description else None


def _snapshot_id(evidence: GraphDiscoveryEvidence) -> str:
    for asset in evidence.entities:
        snapshot = _custom_properties(asset).get("forgetops.snapshot_id")
        if snapshot:
            return snapshot
    digest = sha256(f"{evidence.query}:{evidence.seed_urn}".encode()).hexdigest()[:16]
    return f"datahub-mcp-{digest}"


def _first(values: list[str] | None) -> str | None:
    return values[0] if values else None


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

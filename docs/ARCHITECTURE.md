# Architecture

## Control loop

```text
verified request
      |
      v
subject reference hashing
      |
      v
DataHub MCP discovery ---- search / schema / entities / lineage
      |
      v
policy-bound planner ----- handling rules / owners / legal holds
      |
      v
approval gate ------------ dry-run by default
      |
      v
sandbox executor --------- delete / anonymize / refresh / review artifact
      |
      v
verification ------------- subject coverage and post-action checks
      |
      v
DataHub write-back -------- tags / structured properties / description / document
```

## Planned components

- `forgetops-core`: deterministic models, graph normalization, policy engine, safety gates, and evidence generation.
- `forgetops-datahub`: adapter for the official DataHub MCP server plus narrowly scoped SDK ingestion for the synthetic scenario.
- `forgetops-executor`: idempotent DuckDB demo actions and generated SQL artifacts. No production connector is enabled by default.
- `forgetops-api`: FastAPI endpoints and an event stream for a visible agent trace.
- `forgetops-web`: a focused React interface for case intake, lineage evidence, approvals, execution, and verification.

## DataHub calls

Read path:

- `search` finds assets using PII tags, glossary terms, and subject-key metadata.
- `list_schema_fields` confirms exact fields rather than relying on truncated search results.
- `get_entities` obtains owners, descriptions, tags, terms, domains, and structured properties.
- `get_lineage` traverses bounded downstream impact.

Write-back path (mutations disabled unless explicitly approved):

- `add_tags` marks case lifecycle state.
- `add_structured_properties` records case ID, verification status, and timestamp.
- `update_description` appends a concise operational note where configured.
- `save_document` stores the final evidence summary so future people and agents inherit it.

## Safety invariants

1. Raw subject identifiers are never persisted in plans, logs, DataHub, or demo artifacts.
2. DataHub policy metadata is authoritative; an LLM cannot invent or override policy.
3. Legal holds and missing owners produce blocking review gates.
4. Every mutation requires explicit approval and an idempotency key.
5. A case cannot be marked verified without post-action evidence for every non-retained target.

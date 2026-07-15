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

## Components

- `forgetops-core` (implemented): deterministic models, graph normalization, policy engine, safety gates, and evidence generation.
- `forgetops-datahub` (implemented): adapter for the official DataHub MCP server plus narrowly scoped, idempotent SDK ingestion for the synthetic scenario.
- `forgetops-executor`: idempotent DuckDB demo actions and generated SQL artifacts. No production connector is enabled by default.
- `forgetops-api`: FastAPI endpoints and an event stream for a visible agent trace.
- `forgetops-web`: a focused React interface for case intake, lineage evidence, approvals, execution, and verification.

## DataHub calls

Read path:

- `search` finds assets using PII tags, glossary terms, and subject-key metadata.
- `list_schema_fields` confirms exact fields rather than relying on truncated search results.
- `get_entities` obtains owners, descriptions, tags, terms, domains, and structured properties.
- `get_lineage` traverses bounded downstream impact.

Discovery first searches all matching subject-key roots, then reads direct downstream and column-level lineage for each one. If search or lineage would exceed the configured asset bound, ForgetOps fails closed instead of presenting a partial privacy scope.

Write-back path (mutations disabled unless explicitly approved):

- `add_tags` marks case lifecycle state.
- `add_structured_properties` records case ID, verification status, and timestamp.
- `save_document` upserts the final evidence summary at a deterministic case URN so future people and agents inherit it without duplicate documents on retry.

## Runtime isolation

- A dedicated WSL distribution named `forgetops-runtime` is registered at the ignored repository path `.runtime-wsl`; its Docker root therefore lives on the repository drive.
- Linux integration dependencies live in `.venv-wsl`, while DataHub CLI state and recoverable runtime archives live in `.runtime-home`.
- Docker Compose resources use the fixed project name and explicit network/volume prefix `forgetops-datahub`.
- The quickstart version map and Compose file are pinned in `infra/datahub`, so startup performs no GitHub version lookup and can reuse preloaded images offline.
- The runtime wrapper verifies the WSL registration path and never connects to Docker Desktop, enumerates unrelated containers, or reuses another project's volumes.
- DataHub mutation tools remain disabled unless an approved workflow explicitly enables them.

## Safety invariants

1. Raw subject identifiers are never persisted in plans, logs, DataHub, or demo artifacts.
2. DataHub policy metadata is authoritative; an LLM cannot invent or override policy.
3. Legal holds and missing owners produce blocking review gates.
4. Every mutation requires explicit approval and an idempotency key.
5. A case cannot be marked verified without post-action evidence for every non-retained target.

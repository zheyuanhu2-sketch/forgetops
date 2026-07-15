# ForgetOps

**A lineage-aware right-to-erasure agent powered by DataHub.**

ForgetOps turns a privacy deletion request into a safe, reviewable, and verifiable data operation. It uses DataHub's context graph to find where a subject identifier and related PII travel, applies organization-defined retention policies, generates a bounded action plan, and records evidence back in DataHub.

> Current status: the end-to-end agent core is complete. ForgetOps discovers and normalizes a live DataHub graph, plans policy-aware actions, executes approved work transactionally in a deterministic sandbox, verifies outcomes, writes evidence back through official MCP tools, and reads it back through a fresh mutation-disabled session. The demo web experience is next.

## Why this matters

Deleting one customer row is easy. Proving that the same person's data was handled across source tables, warehouse copies, support systems, derived features, and downstream consumers is not. Spreadsheets cannot reliably follow column-level lineage, ownership, policy signals, and later transformations.

ForgetOps makes DataHub the source of truth for that workflow:

1. **Discover** PII-bearing assets and subject keys through DataHub search and schema metadata.
2. **Trace** column and asset lineage to build a bounded erasure map.
3. **Decide** using explicit retention, legal-hold, ownership, and handling metadata—not model guesswork.
4. **Act** through dry-run-first delete, anonymize, refresh, or manual-review steps.
5. **Verify** coverage and post-action checks before a case can close.
6. **Remember** by writing status, structured evidence, tags, and an audit document back to DataHub.

## Hackathon fit

- **Primary challenge:** Open / Wildcard
- **Also demonstrates:** Agents That Do Real Work
- **DataHub technologies:** DataHub Core, MCP Server, Agent Context Kit/SDK patterns, mutation tools, and context documents
- **Differentiator:** a full privacy-operations control loop, not a metadata chatbot or another generic schema-drift detector

## Quickstart: deterministic foundation demo

Prerequisites: [`uv`](https://docs.astral.sh/uv/) and Git.

```bash
uv sync --extra dev --python 3.11
uv run forgetops plan \
  --graph examples/input/ecommerce-privacy-graph.json \
  --subject-id customer-0042 \
  --request-id DSR-2026-0042 \
  --output-dir artifacts/runtime/DSR-2026-0042
uv run pytest
```

The raw subject identifier is immediately hashed and is never written to the plan or logs. The command emits a JSON plan and a judge-readable Markdown evidence report.

## Transactional sandbox execution

The synthetic DuckDB warehouse exercises real delete, anonymize, refresh, retention, review, rollback, verification, and idempotent replay behavior. Both setup and execution are non-mutating until explicitly approved:

```bash
uv run forgetops sandbox-init \
  --scenario examples/input/ecommerce-sandbox.json \
  --database artifacts/runtime/forgetops.duckdb
uv run forgetops sandbox-init \
  --scenario examples/input/ecommerce-sandbox.json \
  --database artifacts/runtime/forgetops.duckdb \
  --approve
uv run forgetops sandbox-execute \
  --plan examples/output/erasure-plan.json \
  --scenario examples/input/ecommerce-sandbox.json \
  --database artifacts/runtime/forgetops.duckdb \
  --subject-id customer-0042 \
  --idempotency-key demo-execute-v1
# Add --approve only after reviewing the dry-run evidence.
```

Approved actions run in one transaction. Any failed field contract or post-action check rolls back the complete case. The audit ledger and exported evidence contain only the hashed subject reference; the finance legal-hold row and ML review row remain untouched by design.

## Local DataHub runtime

The live runtime uses a dedicated WSL distribution named `forgetops-runtime`. Its virtual disk, Docker images, containers, volumes, Python environment, CLI state, and caches all live under ignored directories in this repository. Docker Desktop is not used, so unrelated projects cannot be touched.

Preview the setup first, then explicitly approve it:

```powershell
uv sync --extra dev --extra datahub --python 3.11
.\scripts\setup-runtime.ps1
.\scripts\setup-runtime.ps1 -Approve
.\scripts\datahub.ps1 start -AllowPull
.\scripts\datahub.ps1 check
uv run python scripts/seed_datahub.py             # dry-run manifest
uv run python scripts/seed_datahub.py --approve   # synthetic metadata only
uv run python scripts/smoke_datahub_graph.py       # official MCP -> plan
uv run python scripts/smoke_datahub_writeback.py   # dry-run write-back manifest
uv run python scripts/smoke_datahub_writeback.py --approve
```

`-AllowPull` is needed only when the pinned images are not already present in the repository-local runtime. In restricted networks, `setup-runtime.ps1` accepts an alternate HTTPS Python package index; exported dependencies remain hash-verified against `uv.lock`.

The wrapper verifies that the WSL virtual disk is registered at `.runtime-wsl`, uses the fixed Compose project and resource prefix `forgetops-datahub`, and refuses to run against Docker Desktop or a runtime outside the repository. DataHub is available at `http://localhost:9002` and its metadata service at `http://localhost:8080`.

The approved seed is idempotent and writes seven synthetic metadata entities, field-level PII and subject-key tags, five DataHub structured properties, technical owners, and direct plus column-level lineage. The live smoke keeps MCP mutations disabled, reads that graph through the official server, normalizes it into the same strict domain model used by offline mode, and emits a review-gated erasure plan.

The official quickstart needs about 8 GB of available memory and roughly 13 GB of repository-drive space. Stop only this project with `.\scripts\datahub.ps1 stop`.

## Safety model

- Dry-run is the default and mutation requires explicit approval.
- Idempotency keys are bound to the exact approved plan and scenario. A persisted write-back receipt also binds the DataHub document URN to that case and operation, while official read tools verify every asset marker and the document body.
- Sandbox mutations run in one DuckDB transaction and roll back on any failed contract or verification check.
- Legal-hold or retention signals create review gates instead of being overridden.
- Policy decisions come from organization-defined metadata; the language model may explain a decision but cannot invent policy.
- Every action cites the DataHub evidence that caused it.
- No real personal data is included in this repository or demo.

ForgetOps is an engineering demonstration, not legal advice. Organizations remain responsible for configuring policies and validating obligations in their jurisdictions.

## Repository map

```text
src/forgetops/                  deterministic planning core and CLI
tests/                          unit tests for safety and evidence behavior
examples/input/                 synthetic DataHub-shaped graph snapshot
examples/output/                checked-in sample plan for judge review
infra/datahub/                  pinned, project-prefixed DataHub quickstart
scripts/                        dry-run seed and repeatable live integration smokes
docs/                           rules, architecture, scoring, and delivery plan
```

## License

Apache License 2.0. See [LICENSE](LICENSE).

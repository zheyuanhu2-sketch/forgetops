# ForgetOps

**A lineage-aware right-to-erasure agent powered by DataHub.**

ForgetOps turns a privacy deletion request into a safe, reviewable, and verifiable data operation. It uses DataHub's context graph to find where a subject identifier and related PII travel, applies organization-defined retention policies, generates a bounded action plan, and records evidence back in DataHub.

> Current status: foundation milestone complete. The deterministic planning core, sample evidence bundle, typed DataHub MCP gateway, explicit mutation gate, and repository-local live runtime are implemented; graph normalization and the web experience are next.

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
uv sync --python 3.11
uv run forgetops plan \
  --graph examples/input/ecommerce-privacy-graph.json \
  --subject-id customer-0042 \
  --request-id DSR-2026-0042 \
  --output-dir artifacts/runtime/DSR-2026-0042
uv run pytest
```

The raw subject identifier is immediately hashed and is never written to the plan or logs. The command emits a JSON plan and a judge-readable Markdown evidence report.

## Local DataHub runtime

The live runtime uses a dedicated WSL distribution named `forgetops-runtime`. Its virtual disk, Docker images, containers, volumes, Python environment, CLI state, and caches all live under ignored directories in this repository. Docker Desktop is not used, so unrelated projects cannot be touched.

Preview the setup first, then explicitly approve it:

```powershell
uv sync --extra dev --extra datahub --python 3.11
.\scripts\setup-runtime.ps1
.\scripts\setup-runtime.ps1 -Approve
.\scripts\datahub.ps1 start -AllowPull
.\scripts\datahub.ps1 check
```

`-AllowPull` is needed only when the pinned images are not already present in the repository-local runtime. In restricted networks, `setup-runtime.ps1` accepts an alternate HTTPS Python package index; exported dependencies remain hash-verified against `uv.lock`.

The wrapper verifies that the WSL virtual disk is registered at `.runtime-wsl`, uses the fixed Compose project and resource prefix `forgetops-datahub`, and refuses to run against Docker Desktop or a runtime outside the repository. DataHub is available at `http://localhost:9002` and its metadata service at `http://localhost:8080`.

The official quickstart needs about 8 GB of available memory and roughly 13 GB of repository-drive space. Stop only this project with `.\scripts\datahub.ps1 stop`.

## Safety model

- Dry-run is the default and mutation requires explicit approval.
- Stable case idempotency keys make retried DataHub evidence writes update the same document instead of creating duplicates.
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
docs/                           rules, architecture, scoring, and delivery plan
```

## License

Apache License 2.0. See [LICENSE](LICENSE).

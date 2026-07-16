# ForgetOps judging guide

This page is the shortest path from the submission claims to working, inspectable proof.

## 60-second route

1. Open the [hosted reviewer workbench](https://zheyuanhu2-sketch.github.io/forgetops/).
   No account, credentials, or local setup are required.
2. Follow the stage rail from **Discover** to **Remember**. The workbench will not unlock
   execution until the protected legal-hold outcome is acknowledged, and it requires a separate
   approval before DataHub write-back.
3. Inspect the checked-in [live MCP summary](examples/output/datahub-live-smoke.json),
   [transaction receipt](examples/output/sandbox-execution-summary.json), and
   [fresh-session write-back verification](examples/output/datahub-writeback-summary.json).

For the narrated path, watch the [2:15 captioned demo](https://youtu.be/XLa1o_3wABY):

- `00:11` — DataHub schema, ownership, policy, and lineage discovery;
- `00:37` — exact approval scope and protected outcomes;
- `00:55` — transactional execution and honest `PARTIAL_VERIFIED` result;
- `01:27` — separately approved DataHub evidence write-back;
- `01:46` — fresh mutation-disabled MCP read-back.

## Scoring evidence

| Criterion             | What to inspect                                                                                                                                                                    | What it proves                                                                                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Use of DataHub        | [Live MCP summary](examples/output/datahub-live-smoke.json), [erasure plan](examples/output/erasure-plan.md), [write-back summary](examples/output/datahub-writeback-summary.json) | DataHub schema, lineage, ownership, and governance signals determine the plan; approved evidence is returned to the graph and read back in a fresh session. |
| Technical execution   | [Architecture](docs/ARCHITECTURE.md), [tests](tests), [CI](https://github.com/zheyuanhu2-sketch/forgetops/actions/workflows/ci.yml)                                                | Typed boundaries, dry-run defaults, scope-bound approvals, transactional rollback, idempotency, deterministic replay, and automated gates.                  |
| Originality           | [Product doctrine](PRODUCT.md), [demo video](https://youtu.be/XLa1o_3wABY)                                                                                                         | A privacy-operation control loop that treats graph context as executable constraints, rather than a catalog chatbot or a replacement for DataHub.           |
| Real-world usefulness | [Transaction receipt](examples/output/sandbox-execution-summary.json), [project brief](docs/PROJECT_BRIEF.md)                                                                      | A realistic mixed outcome: five permitted actions complete while legal-hold and ML-review exceptions stay visible and routed.                               |
| Submission quality    | [Hosted workbench](https://zheyuanhu2-sketch.github.io/forgetops/), [README](README.md), [reproducible demo sources](demo-video)                                                   | A no-login judge path, sub-three-minute film, deterministic offline mode, sample outputs, and complete setup instructions.                                  |
| Open-source bonus     | [DataHub Skills PR #37](https://github.com/datahub-project/datahub-skills/pull/37)                                                                                                 | A standalone privacy-operations skill, evidence contract, plan template, and five safety evaluations contributed upstream.                                  |

## Verified facts

The checked-in live run records 21 bounded official MCP calls, seven reconstructed assets, six
lineage edges, nineteen PII fields, and complete owner coverage. The execution receipt records
zero residuals for every permitted mutation, preserves two explicit exceptions, verifies
transaction rollback and idempotent replay, and contains no raw subject identifier. The write-back
receipt records seven verified entities plus one reusable evidence document read through a fresh
mutation-disabled MCP session.

Validate those claims locally with one deterministic command:

```bash
uv run python scripts/verify_judging_evidence.py
```

The verifier fails closed if a headline claim drifts from its source artifact, if a required
DataHub tool disappears, if a permitted action has a residual, or if raw demo subject material
appears in judge-facing JSON evidence.

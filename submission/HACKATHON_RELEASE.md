# ForgetOps v1.0.0 — DataHub Agent Hackathon submission

This release freezes the public, judge-tested ForgetOps submission at a known commit.

ForgetOps turns DataHub context into operational proof for right-to-erasure cases. It reconstructs
a subject's downstream footprint from schema, lineage, ownership, and governance metadata; binds a
human approval to an exact mutation scope; executes only permitted work; verifies every outcome;
and writes reusable evidence back to DataHub under a separate approval.

## Judge access

- [Hosted reviewer workbench](https://zheyuanhu2-sketch.github.io/forgetops/)
- [2:15 captioned demo](https://youtu.be/XLa1o_3wABY)
- [Devpost submission](https://devpost.com/software/forgetops)
- [60-second judging guide](https://github.com/zheyuanhu2-sketch/forgetops/blob/main/JUDGING.md)

## Verified DataHub loop

- 21 bounded official MCP calls
- 7 reconstructed assets and 6 lineage edges
- 19 PII fields and 100% owner coverage
- 5 permitted mutations, 1 legal hold, and 1 manual-review outcome
- tags, structured properties, and one reusable evidence document written back
- all 7 entities plus the document verified from a fresh mutation-disabled MCP session

The correct result is `PARTIAL_VERIFIED`: every permitted residual is zero while the legal-hold and
manual-review outcomes remain untouched and visible.

## Safety and reproducibility

- deterministic offline path plus verified live DataHub integration
- dry-run defaults and separate execution/write-back approvals
- scope-bound idempotency, transactional rollback, and replay verification
- no raw subject identifiers in plans, logs, DataHub, or evidence artifacts
- 73 Python tests at 90% coverage
- 7 web tests at approximately 92% coverage
- 13 deterministic demo safety and evidence checks

Run the headline evidence gate with:

```bash
uv run python scripts/verify_judging_evidence.py
```

## Open-source contribution

The generalized privacy-operations workflow is proposed upstream in
[DataHub Skills PR #37](https://github.com/datahub-project/datahub-skills/pull/37), including an
evidence contract, approval-ready plan template, routing updates, and five adversarial safety
evaluations.

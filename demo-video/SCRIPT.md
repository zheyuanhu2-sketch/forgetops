# ForgetOps Demo Narration

**Target:** 2 minutes 44 seconds maximum, with room for pauses and visual proof.

## Hook

Deleting one row is easy. Proving every downstream copy was handled, without deleting data under legal hold, is the real work.

ForgetOps turns DataHub context into an approval-gated privacy operation.

## Discover

This workbench is a deterministic replay of one verified DataHub M C P run. The subject request is normalized, and the raw identifier is hashed immediately. It never enters the plan, the logs, or DataHub.

Official M C P tools search the catalog, read entities and schema fields, and traverse asset and column lineage. Twenty-one bounded calls reconstruct seven assets, six lineage edges, and nineteen P I I fields, with one hundred percent owner coverage.

## Decide

ForgetOps doesn't ask a model to invent policy. It reads organization-defined handling rules, owners, and retention evidence from DataHub.

Five assets are eligible for a safe mutation. Finance remains under legal hold. The machine-learning feature set requires human review. Both exceptions stay visible.

## Approve and Execute

Before anything can run, a reviewer acknowledges those protected outcomes. The approval is scope-bound to exactly five actions, in dry-run mode, with rollback armed.

One idempotent transaction executes only the permitted plan. Each action produces a receipt. If a field contract or verification check fails, the complete transaction rolls back.

Five of five receipts are captured.

## Verify

Verification checks every outcome, not just the successful deletes. Permitted residuals are zero. One record remains under legal hold. One feature set remains pending review.

The honest result is partial verified, not a false green success state. An idempotent replay returns the same evidence without repeating the work.

## Remember

Execution approval does not authorize metadata write-back. ForgetOps requires a second, separate approval.

Only then does it add tags, structured properties, and one reusable evidence document through official DataHub mutation tools.

A fresh, mutation-disabled M C P session reads everything back: seven entities, the evidence document, and the same document U R N on retry. Raw subject identifiers never appear.

## Proof and Close

The live DataHub path and the deterministic offline path share one strict domain model. Seventy-nine automated tests cover policy gates, rollback, idempotency, evidence, accessibility, and the complete reviewer journey.

ForgetOps makes exceptions first-class, approvals explicit, and every claim replayable.

DataHub context becomes operational proof.

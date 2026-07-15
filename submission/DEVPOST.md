# Devpost submission draft

## Project title

ForgetOps

## Tagline

DataHub context becomes operational proof.

## Short description

ForgetOps is a lineage-aware privacy-operations agent that turns a right-to-erasure request into a bounded, approval-gated, verifiable workflow. It uses DataHub schema, lineage, ownership, and governance context to find downstream impact, protect legal holds, execute only permitted actions, and write replayable evidence back to the graph.

## Inspiration

Deleting one row is straightforward. Proving that the same person's information was handled correctly across warehouse copies, support systems, derived features, and downstream consumers is not. Privacy teams often bridge that gap with tickets and spreadsheets, even though DataHub already knows the lineage, fields, owners, and governance signals needed to reason about the case.

We built ForgetOps to make that context operational. The goal is not to produce another metadata chatbot. The goal is to create a control loop where every action is explainable, bounded, approved, verified, and replayable.

## What it does

ForgetOps runs one continuous reviewer journey:

1. Hash the subject identifier before it can enter plans, logs, or evidence.
2. Use official DataHub MCP tools to reconstruct PII-bearing assets, schema fields, ownership, and asset plus column lineage.
3. Apply organization-defined retention, legal-hold, handling, and ownership policy.
4. Present an exact dry-run plan while keeping protected outcomes visible.
5. Require explicit human approval for the five permitted actions.
6. Execute those actions idempotently in one transaction with rollback on failed field contracts.
7. Verify permitted residuals, legal holds, review outcomes, and replay behavior.
8. Require a second approval before DataHub metadata write-back.
9. Add tags, structured properties, and a reusable evidence document.
10. Open a fresh mutation-disabled MCP session and read the result back.

The demo deliberately reports `PARTIAL_VERIFIED`, not a misleading all-green success state: five assets are handled, one finance record remains under legal hold, and one ML feature set remains queued for human review.

## How we built it

- **DataHub Core 1.6:** a pinned, loopback-only local quickstart stores the synthetic privacy graph.
- **Official DataHub MCP server:** bounded read and mutation tools power search, entity retrieval, schema/lineage reconstruction, tags, structured properties, documents, and fresh-session verification.
- **Python 3.11, Pydantic, Typer:** a strict domain model and deterministic planner keep live and offline paths behaviorally identical.
- **DuckDB:** the synthetic executor applies delete, anonymize, refresh, retention, and review outcomes in one transaction.
- **React 19 and Vite:** the reviewer workbench exposes evidence, approvals, execution, verification, replay, and write-back as one responsive flow.
- **HyperFrames and GSAP:** a captioned 2:15 product film uses real product states and deterministic, seek-safe motion.
- **Automated gates:** Ruff, mypy, pytest, Vitest, coverage thresholds, accessibility checks, a deterministic demo smoke test, production build, HyperFrames validation, media probing, and encoded-frame review.

## DataHub evidence from the demo

One verified run uses 21 bounded official MCP calls to reconstruct seven assets, six lineage edges, nineteen PII fields, and complete owner coverage. The plan produces five permitted mutations, one legal hold, and one human-review outcome. Approved write-back is then verified across all seven entities and one evidence document from a fresh read-only session.

## Challenges we ran into

The hardest boundary was not generating a deletion recommendation; it was preventing an agent from overstating what happened. We had to model legal hold and human review as first-class outcomes, bind approval to a specific plan, make execution idempotent, validate field-level postconditions, and separate execution authority from metadata write-back authority.

DataHub integration introduced another important challenge: a mutation response is not proof. We solved that by discarding the mutating session and reading every marker and evidence document back through a fresh mutation-disabled MCP client.

We also kept the live DataHub runtime fully isolated from unrelated local projects. Its WSL distribution, Docker state, environments, caches, resource names, and published ports are repository-scoped and checked before startup.

## Accomplishments that we're proud of

- DataHub is the operational control plane, not a superficial API call.
- The same strict model powers a real live integration and an offline deterministic judge path.
- Mutations are dry-run-first, scope-bound, explicitly approved, transactional, and replay-safe.
- The UI makes exceptions more prominent than success theater.
- Write-back has its own approval and fresh-session verification.
- The public story is reproducible from synthetic evidence and contains no real personal data.
- The complete product journey is understandable in a 2:15 captioned video.

## What we learned

Reliable agents need negative capability: knowing what they must not do is as important as knowing what they can do. DataHub's graph becomes especially powerful when lineage and governance metadata are treated as executable constraints rather than passive documentation.

We also learned that evidence UX is part of system safety. Reviewers need to see the source signal, protected outcome, exact approval scope, transaction identity, postcondition, and read-back proof without reconstructing the story from logs.

## What's next

- production connectors with the same dry-run, transaction, and receipt contracts;
- configurable policy packs and jurisdiction-specific review workflows;
- owner routing and service-level tracking for unresolved outcomes;
- cryptographically signed evidence bundles;
- multi-subject and scheduled remediation campaigns;
- deeper DataHub Actions integration for event-triggered privacy operations.

## Try it

The hosted reviewer workbench uses a deterministic replay of a verified DataHub run, so no account or credentials are required. Follow the stage rail from Discover through Remember; the approval controls unlock only after the required protected outcomes are acknowledged.

- Working project URL: `[ADD AFTER DEPLOYMENT]`
- Public source repository: `[ADD AFTER GITHUB PUBLISH]`
- Public demo video: `[ADD AFTER YOUTUBE/VIMEO/YOUKU UPLOAD]`

## Suggested tags

`datahub` `agents` `privacy` `data-governance` `lineage` `compliance` `react` `python`

## Suggested challenge selection

Primary: **Open / Wildcard**

Also relevant: **Agents That Do Real Work**

## Submission notes

All repository and submission copy is in English. The demo uses synthetic identifiers only. No third-party music is used. Judge access should remain free and unrestricted through the judging period.

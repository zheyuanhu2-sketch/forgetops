# ForgetOps project brief

## One-line pitch

ForgetOps is a DataHub-powered agent that traces a privacy deletion request through real data lineage, produces safe and reviewable handling actions, verifies completion, and writes the evidence back to the context graph.

## Primary user

A privacy engineer, data-platform engineer, or data steward responsible for completing data-subject requests across a fragmented warehouse and analytics stack.

## Demo story

1. A verified synthetic request arrives for `customer-0042`.
2. ForgetOps hashes the identifier before persistence.
3. The agent queries DataHub for PII fields, schemas, owners, policy properties, and downstream lineage.
4. The graph reveals seven affected assets: source data, analytics copies, marketing exports, support text, finance records, ML features, and a dashboard cache.
5. ForgetOps proposes delete, anonymize, refresh, and retraining-review actions. A finance legal-hold signal becomes a hard review gate.
6. After explicit approval, the demo executor applies safe changes to a synthetic warehouse and verifies the subject no longer appears where removal is allowed.
7. ForgetOps tags the affected assets, records structured case status, and saves an evidence document back to DataHub.

## Why it can score

| Criterion | Design response |
|---|---|
| Use of DataHub | Search, schema, column lineage, ownership, glossary/structured policy signals, mutations, and saved context documents are all in the critical path. |
| Technical execution | Deterministic safety core, explicit approval boundaries, idempotent execution, verification queries, typed evidence, and failure-injection tests. |
| Originality | Privacy operations and right-to-erasure are materially different from the crowded incident, drift, and generic schema-change projects. |
| Real-world usefulness | Cross-system deletion and evidence collection is expensive, risky, and difficult to prove manually. |
| Submission quality | Hosted deterministic demo, real local DataHub video, checked-in evidence bundle, concise English README, and sub-three-minute narrative. |

## Non-goals

- Giving legal advice or deciding whether a request is legally valid.
- Automatically overriding legal holds, retention rules, or missing ownership.
- Connecting to real customer systems or including real personal data in the hackathon demo.
- Rebuilding DataHub search, lineage, governance, or catalog capabilities.

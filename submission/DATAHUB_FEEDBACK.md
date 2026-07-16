# DataHub hackathon feedback draft

## Topic

Document a durable mutation-verification pattern for the DataHub MCP Server.

## What worked well

The MCP Server made it possible to keep DataHub in the critical path of an agent workflow rather
than using it as a decorative lookup. `search`, `list_schema_fields`, `get_entities`, and
`get_lineage` provided enough context to reconstruct a bounded privacy footprint, while
`add_tags`, `add_structured_properties`, and `save_document` allowed the agent to return reusable
case evidence to the graph.

The separation between read and mutation tools also made least-authority sessions straightforward
to model.

## Friction

A successful mutation response is easy for an agent to over-interpret as durable proof. During the
ForgetOps build, we needed a stronger contract:

1. execute only an explicitly approved, scope-bound mutation set;
2. discard the mutation-enabled MCP session;
3. open a fresh session with mutation tools disabled;
4. read every expected tag and structured property back with `get_entities`;
5. locate the evidence document with `search_documents` and verify its case-specific body with
   `grep_documents`;
6. fail the workflow if any exact marker, entity, document, or document-body match is absent.

We also found that document retries need an explicit identity rule. Letting DataHub assign the
document URN on first creation, persisting that returned URN in the execution receipt, and requiring
retries to reuse it prevented duplicate evidence documents.

## Suggested improvement

Add a “durable agent write-back” recipe to the MCP Server documentation and examples. The recipe
should distinguish:

- mutation acceptance from verified graph state;
- execution approval from metadata write-back approval;
- same-session reads from fresh least-authority read-back;
- create retries from idempotent updates using a persisted document URN.

A small reference example could write a tag, one structured property, and one document, then verify
all three from a fresh mutation-disabled client. It should include a negative test where one expected
marker is absent and the agent refuses to report success.

## Expected impact

This pattern would help agent builders avoid false-positive completion claims, duplicate evidence
documents, and overly privileged long-lived sessions. It applies beyond privacy operations to
quality remediation, incident response, ownership routing, policy enforcement, and other workflows
that read from and contribute back to the DataHub graph.

## Reproducible reference

- Project: https://github.com/zheyuanhu2-sketch/forgetops
- Write-back summary:
  https://github.com/zheyuanhu2-sketch/forgetops/blob/main/examples/output/datahub-writeback-summary.json
- Generalized skill contribution: https://github.com/datahub-project/datahub-skills/pull/37

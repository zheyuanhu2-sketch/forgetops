import graphSnapshot from "../../../examples/input/ecommerce-privacy-graph.json" with { type: "json" };
import writebackSummary from "../../../examples/output/datahub-writeback-summary.json" with { type: "json" };
import erasurePlan from "../../../examples/output/erasure-plan.json" with { type: "json" };
import executionSummary from "../../../examples/output/sandbox-execution-summary.json" with { type: "json" };

const CASE_ID = "DSR-2026-0042";
const SAFE_MUTATION_ACTIONS = new Set(["anonymize", "delete", "refresh"]);

/**
 * @param {boolean} condition
 * @param {string} message
 */
function invariant(condition, message) {
  if (!condition) {
    throw new Error(`Invalid ForgetOps demo fixture: ${message}`);
  }
}

/**
 * @template T
 * @param {T} value
 * @returns {T}
 */
function deepFreeze(value) {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    Object.values(value).forEach(deepFreeze);
  }
  return value;
}

/**
 * @param {string[]} values
 * @returns {string[]}
 */
function uniqueSorted(values) {
  return [...new Set(values)].sort((left, right) => left.localeCompare(right));
}

/**
 * @param {number} sequence
 * @returns {string}
 */
function makeSafeNodeId(sequence) {
  return `asset-${String(sequence).padStart(2, "0")}`;
}

/**
 * @template T
 * @param {T | undefined} value
 * @param {string} message
 * @returns {T}
 */
function required(value, message) {
  invariant(value !== undefined, message);
  return /** @type {T} */ (value);
}

const orderedPlanActions = [...erasurePlan.actions].sort(
  (left, right) => left.sequence - right.sequence,
);
const executionByAsset = new Map(executionSummary.actions.map((action) => [action.asset, action]));
const nodeIdByUrn = new Map(
  orderedPlanActions.map((action) => [action.asset_urn, makeSafeNodeId(action.sequence)]),
);

const safeMutationActions = orderedPlanActions.filter(
  (action) => !action.blocked && SAFE_MUTATION_ACTIONS.has(action.action),
);
const legalHoldActions = orderedPlanActions.filter(
  (action) => action.blocked && action.action === "retain",
);
const manualReviewActions = orderedPlanActions.filter((action) => action.action === "review");
const datasetRoots = graphSnapshot.assets.filter((asset) =>
  asset.urn.startsWith("urn:li:dataset:"),
);
const relatedNonDatasetAssets = graphSnapshot.assets.length - datasetRoots.length;

// Mirrors the bounded DataHub MCP discovery path used by the live demo:
// search, one root entity batch, schema + asset lineage + column lineage per
// dataset root, then one related-entity batch for the downstream dashboard.
const discoveryCallBreakdown = {
  search: 1,
  entityBatches: 1 + (relatedNonDatasetAssets > 0 ? 1 : 0),
  schemaFields: datasetRoots.length,
  assetLineage: datasetRoots.length,
  columnLineage: datasetRoots.reduce((total, asset) => total + asset.subject_keys.length, 0),
};
const datahubDiscoveryCalls = Object.values(discoveryCallBreakdown).reduce(
  (total, count) => total + count,
  0,
);

invariant(erasurePlan.request.request_id === CASE_ID, "unexpected plan case ID");
invariant(writebackSummary.case_id === CASE_ID, "write-back case does not match the plan");
invariant(
  graphSnapshot.snapshot_id === erasurePlan.graph_snapshot_id,
  "graph snapshot does not match the plan",
);
invariant(graphSnapshot.assets.length === 7, "expected exactly 7 discovered assets");
invariant(graphSnapshot.edges.length === 6, "expected exactly 6 lineage edges");
invariant(
  graphSnapshot.assets.reduce((total, asset) => total + asset.pii_fields.length, 0) === 19,
  "expected exactly 19 PII fields",
);
invariant(orderedPlanActions.length === 7, "every discovered asset needs one plan action");
invariant(safeMutationActions.length === 5, "expected exactly 5 safe mutations");
invariant(legalHoldActions.length === 1, "expected exactly 1 legal hold");
invariant(manualReviewActions.length === 1, "expected exactly 1 manual review");
invariant(erasurePlan.coverage.owner_coverage_pct === 100, "owner coverage must be 100%");
invariant(datahubDiscoveryCalls === 21, "expected exactly 21 DataHub discovery calls");
invariant(executionSummary.verified_actions === 7, "all 7 actions must have evidence");
invariant(executionSummary.exception_actions === 2, "expected exactly 2 exceptions");
invariant(
  executionSummary.raw_subject_in_audit_evidence === false,
  "audit evidence must not contain a raw subject identifier",
);
invariant(
  writebackSummary.entity_count === 7 && writebackSummary.verification.verified_entity_count === 7,
  "DataHub write-back must cover and verify all 7 entities",
);

for (const action of orderedPlanActions) {
  invariant(
    graphSnapshot.assets.some((asset) => asset.urn === action.asset_urn),
    `plan action ${action.sequence} references an unknown asset`,
  );
  invariant(
    executionByAsset.has(action.asset_name),
    `execution evidence is missing for ${action.asset_name}`,
  );
}

const graphNodes = orderedPlanActions.map((action) => {
  const asset = required(
    graphSnapshot.assets.find((candidate) => candidate.urn === action.asset_urn),
    `graph asset is missing for ${action.asset_name}`,
  );
  const execution = required(
    executionByAsset.get(action.asset_name),
    `execution evidence is missing for ${action.asset_name}`,
  );

  return {
    id: required(
      nodeIdByUrn.get(action.asset_urn),
      `safe node ID is missing for ${action.asset_name}`,
    ),
    urn: asset.urn,
    name: asset.name,
    platform: asset.platform,
    kind: asset.kind,
    owners: uniqueSorted(asset.owners),
    piiFields: uniqueSorted(asset.pii_fields),
    subjectKeys: uniqueSorted(asset.subject_keys),
    handlingRule: asset.handling_rule,
    policyReason: asset.policy_reason,
    policySource: asset.policy_source,
    legalHold: asset.legal_hold,
    plannedAction: action.action,
    executionOutcome: execution.outcome,
    remainingRecords: execution.remaining,
    exceptionType:
      action.action === "retain"
        ? "legal_hold"
        : action.action === "review"
          ? "manual_review"
          : null,
  };
});

const graphEdges = graphSnapshot.edges
  .map((edge) => {
    const source = required(
      nodeIdByUrn.get(edge.upstream_urn),
      `lineage source is missing for ${edge.upstream_urn}`,
    );
    const target = required(
      nodeIdByUrn.get(edge.downstream_urn),
      `lineage target is missing for ${edge.downstream_urn}`,
    );
    return {
      id: `edge-${source}-${target}`,
      source,
      target,
      fieldMappings: Object.entries(edge.field_mapping)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([sourceField, targetFields]) => ({
          sourceField,
          targetFields: uniqueSorted(targetFields),
        })),
    };
  })
  .sort(
    (left, right) =>
      left.source.localeCompare(right.source) || left.target.localeCompare(right.target),
  );

const actions = orderedPlanActions.map((action) => {
  const execution = required(
    executionByAsset.get(action.asset_name),
    `execution evidence is missing for ${action.asset_name}`,
  );
  const category = action.blocked
    ? "legal_hold"
    : action.action === "review"
      ? "manual_review"
      : "safe_mutation";

  return {
    id: `action-${String(action.sequence).padStart(2, "0")}`,
    sequence: action.sequence,
    assetId: required(
      nodeIdByUrn.get(action.asset_urn),
      `safe node ID is missing for ${action.asset_name}`,
    ),
    assetName: action.asset_name,
    type: action.action,
    category,
    owners: uniqueSorted(action.owners),
    fields: uniqueSorted(action.fields),
    policyReason: action.policy_reason,
    policySource: action.policy_source,
    requiresApproval: action.requires_approval,
    blocked: action.blocked,
    outcome: execution.outcome,
    remainingRecords: execution.remaining,
  };
});

const stageDefinitions = [
  {
    id: "discover",
    label: "Discover",
    initialState: "complete",
    evidence: "7 assets · 6 edges · 19 PII fields",
  },
  {
    id: "decide",
    label: "Decide",
    initialState: "complete",
    evidence: "5 mutations · 2 protected exceptions",
  },
  {
    id: "approve",
    label: "Approve",
    initialState: "current",
    evidence: "Explicit scope-bound approval",
  },
  {
    id: "execute",
    label: "Execute",
    initialState: "locked",
    evidence: "Idempotent transaction",
  },
  {
    id: "verify",
    label: "Verify",
    initialState: "locked",
    evidence: "7 action outcomes checked",
  },
  {
    id: "remember",
    label: "Remember",
    initialState: "locked",
    evidence: "Verified evidence written to DataHub",
  },
];

export const caseData = deepFreeze({
  schemaVersion: "forgetops.workbench-case.v1",
  meta: {
    mode: "deterministic_offline_demo",
    source: graphSnapshot.source,
    graphSnapshotId: graphSnapshot.snapshot_id,
    sourceFiles: [
      "examples/input/ecommerce-privacy-graph.json",
      "examples/output/erasure-plan.json",
      "examples/output/sandbox-execution-summary.json",
      "examples/output/datahub-writeback-summary.json",
    ],
  },
  case: {
    id: erasurePlan.request.request_id,
    subjectRef: erasurePlan.request.subject_ref,
    requestType: erasurePlan.request.request_type,
    createdAt: erasurePlan.request.created_at,
    generatedAt: erasurePlan.generated_at,
    planStatus: erasurePlan.status,
    finalOutcome: executionSummary.status,
    defaultStage: "approve",
  },
  metrics: {
    assets: graphSnapshot.assets.length,
    lineageEdges: graphSnapshot.edges.length,
    piiFields: erasurePlan.coverage.pii_fields,
    safeMutations: safeMutationActions.length,
    legalHolds: legalHoldActions.length,
    manualReviews: manualReviewActions.length,
    datahubCalls: datahubDiscoveryCalls,
    ownerCoveragePct: erasurePlan.coverage.owner_coverage_pct,
  },
  stages: stageDefinitions,
  timeline: [
    {
      id: "trace-01",
      stage: "discover",
      title: "Subject reference secured",
      detail: "The raw identifier was hashed before discovery and is never persisted.",
      state: "verified",
    },
    {
      id: "trace-02",
      stage: "discover",
      title: "DataHub scope reconstructed",
      detail: "21 bounded MCP calls found 7 assets, 6 lineage edges, and 19 PII fields.",
      state: "verified",
    },
    {
      id: "trace-03",
      stage: "decide",
      title: "Policy-aware plan compiled",
      detail: "Five mutations are safe; finance is held and ML requires review.",
      state: "verified",
    },
    {
      id: "trace-04",
      stage: "approve",
      title: "Execution scope approved",
      detail: "Approval covers only the five non-exception mutation actions.",
      state: "approved",
    },
    {
      id: "trace-05",
      stage: "execute",
      title: "Transaction committed once",
      detail: "Idempotent replay and rollback behavior were both verified.",
      state: "verified",
    },
    {
      id: "trace-06",
      stage: "verify",
      title: "Partial verification proven",
      detail: "Five permitted targets are clear; one hold and one review remain visible.",
      state: "partial_verified",
    },
    {
      id: "trace-07",
      stage: "remember",
      title: "DataHub write-back approved and read back",
      detail: "Tags, structured properties, and one reusable evidence document were verified.",
      state: "verified",
    },
  ],
  graph: {
    nodes: graphNodes,
    edges: graphEdges,
  },
  actions,
  approvals: {
    execution: {
      id: "approval-execution-01",
      purpose: "execute_safe_mutations",
      approved: executionSummary.approved,
      scopeActionIds: safeMutationActions.map(
        (action) => `action-${String(action.sequence).padStart(2, "0")}`,
      ),
      excludedActionIds: [...legalHoldActions, ...manualReviewActions]
        .sort((left, right) => left.sequence - right.sequence)
        .map((action) => `action-${String(action.sequence).padStart(2, "0")}`),
    },
    writeback: {
      id: "approval-writeback-01",
      purpose: "publish_verified_evidence_to_datahub",
      approved: writebackSummary.approved,
      eligible: writebackSummary.eligible_for_writeback,
      mutationTools: [...writebackSummary.mutation_tools],
    },
  },
  execution: {
    status: executionSummary.status,
    verifiedActions: executionSummary.verified_actions,
    mutationCount: safeMutationActions.length,
    exceptionCount: executionSummary.exception_actions,
    idempotentReplayVerified: executionSummary.idempotent_replay_verified,
    transactionRollbackVerified: executionSummary.transaction_rollback_verified,
    rawSubjectInAuditEvidence: executionSummary.raw_subject_in_audit_evidence,
    outcomes: actions.map(({ id, assetId, assetName, outcome, remainingRecords }) => ({
      actionId: id,
      assetId,
      assetName,
      outcome,
      remainingRecords,
    })),
  },
  writeback: {
    status: writebackSummary.execution_status,
    entityCount: writebackSummary.entity_count,
    documentUrn: writebackSummary.document_urn,
    reusesDocumentUrn: writebackSummary.reuses_document_urn,
    tagUrn: writebackSummary.tag_urn,
    mutationTools: [...writebackSummary.mutation_tools],
    verificationTools: [...writebackSummary.verification.tool_calls],
    verifiedEntityCount: writebackSummary.verification.verified_entity_count,
    documentFound: writebackSummary.verification.document_found,
    documentContentVerified: writebackSummary.verification.document_content_verified,
    callCount:
      writebackSummary.mutation_tools.length + writebackSummary.verification.tool_calls.length,
  },
  datahub: {
    connected: true,
    discoveryCalls: datahubDiscoveryCalls,
    discoveryCallBreakdown,
    readTools: [...erasurePlan.datahub.read_tools],
    plannedWriteTools: [...erasurePlan.datahub.planned_write_tools],
  },
  safety: {
    dryRunDefault: true,
    rawSubjectPersisted: false,
    rawSubjectInAuditEvidence: executionSummary.raw_subject_in_audit_evidence,
    legalHoldsMutated: false,
    mutationsRequireExplicitApproval: true,
    writebackRequiresSeparateApproval: true,
  },
});

export const CASE_DATA = caseData;
export default caseData;

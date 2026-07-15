import caseData from "../src/data/caseData.js";

const checks = [
  [caseData.schemaVersion === "forgetops.workbench-case.v1", "schema version"],
  [caseData.case.id === "DSR-2026-0042", "case binding"],
  [caseData.graph.nodes.length === 7, "seven assets"],
  [caseData.graph.edges.length === 6, "six lineage edges"],
  [caseData.metrics.safeMutations === 5, "five safe mutations"],
  [caseData.metrics.legalHolds === 1, "one legal hold"],
  [caseData.metrics.manualReviews === 1, "one manual review"],
  [caseData.metrics.datahubCalls === 21, "bounded DataHub call trace"],
  [caseData.execution.idempotentReplayVerified, "idempotent replay evidence"],
  [caseData.execution.transactionRollbackVerified, "rollback evidence"],
  [caseData.writeback.documentContentVerified, "fresh document read-back"],
  [caseData.safety.rawSubjectPersisted === false, "no raw subject persistence"],
  [caseData.safety.writebackRequiresSeparateApproval, "separate write-back approval"],
];

const failed = checks.filter(([passed]) => !passed);
if (failed.length > 0) {
  throw new Error(`ForgetOps demo smoke failed: ${failed.map(([, name]) => name).join(", ")}`);
}

console.log(`ForgetOps demo smoke passed (${checks.length} safety and evidence checks).`);

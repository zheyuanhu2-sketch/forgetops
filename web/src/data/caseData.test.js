import { describe, expect, it } from "vitest";
import caseData from "./caseData.js";

describe("ForgetOps safe browser data contract", () => {
  it("keeps the canonical graph and policy counts exact", () => {
    expect(caseData.case.id).toBe("DSR-2026-0042");
    expect(caseData.metrics).toMatchObject({
      assets: 7,
      lineageEdges: 6,
      piiFields: 19,
      safeMutations: 5,
      legalHolds: 1,
      manualReviews: 1,
      datahubCalls: 21,
      ownerCoveragePct: 100,
    });
    expect(caseData.graph.nodes).toHaveLength(7);
    expect(caseData.graph.edges).toHaveLength(6);
    expect(new Set(caseData.graph.nodes.map((node) => node.id)).size).toBe(7);
  });

  it("keeps protected exceptions outside the mutation scope", () => {
    const scopedActionIds = new Set(caseData.approvals.execution.scopeActionIds);
    const excludedActionIds = new Set(caseData.approvals.execution.excludedActionIds);

    expect(scopedActionIds.size).toBe(5);
    expect(excludedActionIds.size).toBe(2);
    expect([...scopedActionIds].some((id) => excludedActionIds.has(id))).toBe(false);
    expect(caseData.actions.filter((action) => action.category === "legal_hold")).toHaveLength(1);
    expect(caseData.actions.filter((action) => action.category === "manual_review")).toHaveLength(
      1,
    );
    expect(caseData.safety.legalHoldsMutated).toBe(false);
  });

  it("separates execution approval from DataHub write-back approval", () => {
    expect(caseData.approvals.execution.id).not.toBe(caseData.approvals.writeback.id);
    expect(caseData.approvals.execution.purpose).toBe("execute_safe_mutations");
    expect(caseData.approvals.writeback.purpose).toBe("publish_verified_evidence_to_datahub");
    expect(caseData.safety.writebackRequiresSeparateApproval).toBe(true);
  });

  it("contains no raw demo subject identifier or unsafe source path", () => {
    const serialized = JSON.stringify(caseData).toLowerCase();

    expect(serialized).not.toContain("customer-0042");
    expect(serialized).not.toContain("ecommerce-sandbox.json");
    expect(caseData.safety.rawSubjectPersisted).toBe(false);
    expect(caseData.execution.rawSubjectInAuditEvidence).toBe(false);
  });
});

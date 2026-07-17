import IconCheck from "@tabler/icons-react/dist/esm/icons/IconCheck.mjs";
import IconDatabaseExport from "@tabler/icons-react/dist/esm/icons/IconDatabaseExport.mjs";
import IconLoader2 from "@tabler/icons-react/dist/esm/icons/IconLoader2.mjs";
import IconLock from "@tabler/icons-react/dist/esm/icons/IconLock.mjs";
import IconPlayerPlay from "@tabler/icons-react/dist/esm/icons/IconPlayerPlay.mjs";
import IconRotate2 from "@tabler/icons-react/dist/esm/icons/IconRotate2.mjs";
import IconShieldCheck from "@tabler/icons-react/dist/esm/icons/IconShieldCheck.mjs";

/** @typedef {typeof import("../data/caseData.js").caseData} CaseData */
/** @typedef {ReturnType<typeof import("../hooks/useForgetOpsWorkflow.js").useForgetOpsWorkflow>} Workflow */

/** @param {{ modeLabel: string }} props */
function SafetyFacts({ modeLabel }) {
  return (
    <dl className="safety-facts">
      <div>
        <dt>Execution mode</dt>
        <dd>{modeLabel}</dd>
      </div>
      <div>
        <dt>Transaction</dt>
        <dd>One idempotent transaction</dd>
      </div>
      <div>
        <dt>Safety</dt>
        <dd>
          <IconShieldCheck aria-hidden="true" size={17} stroke={1.8} />
          Rollback armed
        </dd>
      </div>
    </dl>
  );
}

/** @param {{ data: CaseData; workflow: Workflow }} props */
function ExecutionApproval({ data, workflow }) {
  return (
    <>
      <div className="approval-review">
        <span className="console-label">Approval console</span>
        <label className="review-check">
          <input
            type="checkbox"
            checked={workflow.protectedOutcomesReviewed}
            onChange={(event) => workflow.setProtectedOutcomesReviewed(event.target.checked)}
          />
          <span aria-hidden="true">
            {workflow.protectedOutcomesReviewed ? <IconCheck size={19} /> : null}
          </span>
          <strong>
            Protected outcomes reviewed: legal hold retained; model feature requires human review.
          </strong>
        </label>
        <p>This is a dry run. No data will be changed.</p>
      </div>
      <div className="approval-scope">
        <span className="console-label">Scope</span>
        <h2>Approve {data.metrics.safeMutations} mutations only</h2>
        <SafetyFacts modeLabel="Dry run" />
      </div>
      <div className="approval-actions">
        <button
          className="primary-action"
          type="button"
          onClick={workflow.authorizeExecution}
          disabled={!workflow.protectedOutcomesReviewed}
          aria-describedby="execution-approval-requirement"
        >
          <IconPlayerPlay aria-hidden="true" size={18} fill="currentColor" />
          Authorize execution
          <IconLock aria-hidden="true" size={17} />
        </button>
        <small
          id="execution-approval-requirement"
          className="action-requirement"
          data-state={workflow.protectedOutcomesReviewed ? "ready" : "blocked"}
        >
          {workflow.protectedOutcomesReviewed ? (
            <IconCheck aria-hidden="true" size={13} stroke={2} />
          ) : (
            <IconLock aria-hidden="true" size={12} stroke={2} />
          )}
          <span>
            {workflow.protectedOutcomesReviewed
              ? `Scope locked to ${data.metrics.safeMutations} permitted mutations.`
              : "Review protected outcomes to unlock."}
          </span>
        </small>
        <button className="secondary-action" type="button" onClick={workflow.returnToPlan}>
          <IconRotate2 aria-hidden="true" size={17} />
          Return to plan
        </button>
      </div>
      <div className="action-explainer">
        <span className="console-label">About this action</span>
        <p>This approval authorizes execution of the plan in dry-run mode.</p>
        <p>Legal hold and manual-review items are not modified.</p>
      </div>
    </>
  );
}

/** @param {{ data: CaseData; workflow: Workflow }} props */
function ExecutionRunning({ data, workflow }) {
  return (
    <>
      <div className="approval-review">
        <span className="console-label">Execution console</span>
        <div className="running-state">
          <IconLoader2 className="spinner" aria-hidden="true" size={30} />
          <strong>Recording mutation evidence</strong>
        </div>
        <p>Protected exceptions remain outside the transaction.</p>
      </div>
      <div className="approval-scope">
        <span className="console-label">Approved scope</span>
        <h2>
          {workflow.executionProgress} of {data.metrics.safeMutations} receipts captured
        </h2>
        <div
          className="console-progress"
          role="progressbar"
          aria-label="Mutation receipts captured"
          aria-valuemin={0}
          aria-valuemax={data.metrics.safeMutations}
          aria-valuenow={workflow.executionProgress}
        >
          <span
            style={{ width: `${(workflow.executionProgress / data.metrics.safeMutations) * 100}%` }}
          />
        </div>
        <SafetyFacts modeLabel="Dry run executing" />
      </div>
      <div className="approval-actions">
        <button className="primary-action" type="button" disabled>
          <IconLoader2 className="spinner" aria-hidden="true" size={18} />
          Execution in progress
        </button>
      </div>
      <div className="action-explainer">
        <span className="console-label">Transaction boundary</span>
        <p>Plan, subject hash, approval scope, and idempotency key are bound together.</p>
      </div>
    </>
  );
}

/** @param {{ data: CaseData; workflow: Workflow }} props */
function WritebackApproval({ data, workflow }) {
  return (
    <>
      <div className="approval-review">
        <span className="console-label">Write-back approval</span>
        <label className="review-check">
          <input
            type="checkbox"
            checked={workflow.writebackReviewed}
            onChange={(event) => workflow.setWritebackReviewed(event.target.checked)}
          />
          <span aria-hidden="true">
            {workflow.writebackReviewed ? <IconCheck size={19} /> : null}
          </span>
          <strong>Verification reviewed: 5 cleared, 1 retained, 1 pending human review.</strong>
        </label>
        <p>Execution approval does not authorize this metadata write-back.</p>
      </div>
      <div className="approval-scope">
        <span className="console-label">DataHub scope</span>
        <h2>Publish verified evidence for {data.writeback.entityCount} entities</h2>
        <dl className="safety-facts">
          <div>
            <dt>Mutation tools</dt>
            <dd>{data.writeback.mutationTools.join(" · ")}</dd>
          </div>
          <div>
            <dt>Document</dt>
            <dd>Reusable URN</dd>
          </div>
          <div>
            <dt>Eligibility</dt>
            <dd>
              <IconCheck aria-hidden="true" size={17} /> Verified
            </dd>
          </div>
        </dl>
      </div>
      <div className="approval-actions">
        <button
          className="primary-action"
          type="button"
          onClick={workflow.authorizeWriteback}
          disabled={!workflow.writebackReviewed}
          aria-describedby="writeback-approval-requirement"
        >
          <IconDatabaseExport aria-hidden="true" size={18} />
          Approve DataHub write-back
          <IconLock aria-hidden="true" size={17} />
        </button>
        <small
          id="writeback-approval-requirement"
          className="action-requirement"
          data-state={workflow.writebackReviewed ? "ready" : "blocked"}
        >
          {workflow.writebackReviewed ? (
            <IconCheck aria-hidden="true" size={13} stroke={2} />
          ) : (
            <IconLock aria-hidden="true" size={12} stroke={2} />
          )}
          <span>
            {workflow.writebackReviewed
              ? "Fresh-session evidence is ready to publish."
              : "Review verification evidence to unlock."}
          </span>
        </small>
        <button
          className="secondary-action"
          type="button"
          onClick={() =>
            document.querySelector(".evidence-timeline")?.scrollIntoView({ block: "start" })
          }
        >
          Review execution evidence
        </button>
      </div>
      <div className="action-explainer">
        <span className="console-label">About this action</span>
        <p>Writes tags, structured properties, and one evidence document.</p>
        <p>A fresh mutation-disabled MCP session verifies the result.</p>
      </div>
    </>
  );
}

/** @param {{ data: CaseData; workflow: Workflow }} props */
function RememberedState({ data, workflow }) {
  return (
    <>
      <div className="approval-review remembered-review">
        <span className="console-label">Evidence remembered</span>
        <IconCheck aria-hidden="true" size={34} stroke={1.8} />
        <strong>Fresh DataHub read-back verified</strong>
        <p>Raw subject identifiers never entered the evidence document.</p>
      </div>
      <div className="approval-scope">
        <span className="console-label">Verified memory</span>
        <h2>{data.writeback.verifiedEntityCount} entities · 1 reusable evidence document</h2>
        <dl className="safety-facts">
          <div>
            <dt>Read-back tools</dt>
            <dd>{data.writeback.verificationTools.join(" · ")}</dd>
          </div>
          <div>
            <dt>Content</dt>
            <dd>Document verified</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>
              <IconCheck aria-hidden="true" size={17} /> Remembered
            </dd>
          </div>
        </dl>
      </div>
      <div className="approval-actions">
        <button
          className="primary-action success-action"
          type="button"
          onClick={workflow.resetDemo}
        >
          <IconRotate2 aria-hidden="true" size={18} />
          Replay deterministic demo
        </button>
      </div>
      <div className="action-explainer">
        <span className="console-label">Case outcome</span>
        <p>Partial verification is a truthful result, not a hidden failure.</p>
      </div>
    </>
  );
}

/** @param {{ data: CaseData; workflow: Workflow }} props */
export function ApprovalConsole({ data, workflow }) {
  return (
    <section
      className="approval-console"
      aria-label="Approval and execution controls"
      aria-busy={workflow.phase === "execute"}
    >
      {workflow.phase === "approve" ? (
        <ExecutionApproval data={data} workflow={workflow} />
      ) : workflow.phase === "execute" ? (
        <ExecutionRunning data={data} workflow={workflow} />
      ) : workflow.phase === "verify" ? (
        <WritebackApproval data={data} workflow={workflow} />
      ) : (
        <RememberedState data={data} workflow={workflow} />
      )}
    </section>
  );
}

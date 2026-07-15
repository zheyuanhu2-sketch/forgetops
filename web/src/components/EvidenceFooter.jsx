import { useEffect, useRef, useState } from "react";
import IconCheck from "@tabler/icons-react/dist/esm/icons/IconCheck.mjs";
import IconLayersLinked from "@tabler/icons-react/dist/esm/icons/IconLayersLinked.mjs";
import IconLock from "@tabler/icons-react/dist/esm/icons/IconLock.mjs";
import IconX from "@tabler/icons-react/dist/esm/icons/IconX.mjs";

/** @typedef {typeof import("../data/caseData.js").caseData} CaseData */
/** @typedef {import("../hooks/useForgetOpsWorkflow.js").StageId} StageId */

/** @param {{ data: CaseData; phase: StageId }} props */
export function EvidenceFooter({ data, phase }) {
  const [detailsOpen, setDetailsOpen] = useState(false);
  const detailsButtonRef = useRef(/** @type {HTMLButtonElement | null} */ (null));
  const closeButtonRef = useRef(/** @type {HTMLButtonElement | null} */ (null));
  const restoreDetailsFocus = useRef(false);
  const writebackState =
    phase === "remember" ? "verified" : phase === "verify" ? "approval required" : "queued";

  useEffect(() => {
    if (!detailsOpen) {
      if (restoreDetailsFocus.current) {
        detailsButtonRef.current?.focus();
        restoreDetailsFocus.current = false;
      }
      return undefined;
    }

    restoreDetailsFocus.current = true;
    closeButtonRef.current?.focus();

    /** @param {KeyboardEvent} event */
    function keepDialogModal(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        setDetailsOpen(false);
      } else if (event.key === "Tab") {
        event.preventDefault();
        closeButtonRef.current?.focus();
      }
    }

    document.addEventListener("keydown", keepDialogModal);
    return () => document.removeEventListener("keydown", keepDialogModal);
  }, [detailsOpen]);

  return (
    <footer className="evidence-footer">
      <div className="footer-heading">
        <span>Evidence footer</span>
        <em>{phase === "approve" ? "Upcoming verification targets" : "Verified case outcomes"}</em>
      </div>
      <dl className="proof-metrics">
        <div>
          <dt>Permitted residuals</dt>
          <dd data-tone="verified">0</dd>
        </div>
        <div>
          <dt>Retained under legal hold</dt>
          <dd data-tone="exception">1</dd>
        </div>
        <div>
          <dt>Pending manual review</dt>
          <dd data-tone="exception">1</dd>
        </div>
        <div>
          <dt>{phase === "approve" ? "Expected status" : "Current status"}</dt>
          <dd data-tone="verified">Partial_verified</dd>
        </div>
      </dl>
      <div className="writeback-proof" data-state={writebackState}>
        {phase === "remember" ? (
          <IconCheck aria-hidden="true" size={23} />
        ) : phase === "verify" ? (
          <IconLock aria-hidden="true" size={21} />
        ) : (
          <IconLayersLinked aria-hidden="true" size={23} />
        )}
        <span>
          <strong>DataHub write-back {writebackState}</strong>
          <small>
            {phase === "remember"
              ? `${data.writeback.verifiedEntityCount} entities read back fresh`
              : phase === "verify"
                ? "Separate approval is now available"
                : "Queued after verification"}
          </small>
        </span>
        <button ref={detailsButtonRef} type="button" onClick={() => setDetailsOpen(true)}>
          View details
        </button>
      </div>

      {detailsOpen ? (
        <div className="evidence-dialog-backdrop" role="presentation">
          <section
            className="evidence-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="evidence-dialog-title"
          >
            <button
              ref={closeButtonRef}
              className="dialog-close"
              type="button"
              onClick={() => setDetailsOpen(false)}
              aria-label="Close evidence details"
            >
              <IconX aria-hidden="true" size={20} />
            </button>
            <span className="console-label">DataHub evidence contract</span>
            <h2 id="evidence-dialog-title">Write, then verify from a fresh session.</h2>
            <dl>
              <div>
                <dt>Write tools</dt>
                <dd>{data.writeback.mutationTools.join(", ")}</dd>
              </div>
              <div>
                <dt>Read-back tools</dt>
                <dd>{data.writeback.verificationTools.join(", ")}</dd>
              </div>
              <div>
                <dt>Entity coverage</dt>
                <dd>
                  {data.writeback.verifiedEntityCount} of {data.writeback.entityCount}
                </dd>
              </div>
              <div>
                <dt>Document behavior</dt>
                <dd>Same URN reused on idempotent retry</dd>
              </div>
            </dl>
          </section>
        </div>
      ) : null}
    </footer>
  );
}

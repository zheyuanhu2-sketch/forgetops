import { useCallback, useEffect, useMemo, useRef, useState } from "react";

/** @typedef {"discover" | "decide" | "approve" | "execute" | "verify" | "remember"} StageId */
/** @typedef {"complete" | "current" | "locked"} StageState */

/** @type {readonly StageId[]} */
export const STAGE_ORDER = ["discover", "decide", "approve", "execute", "verify", "remember"];

const EXECUTION_STEPS = 5;

function prefersReducedMotion() {
  return (
    typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

export function useForgetOpsWorkflow() {
  const [phase, setPhase] = useState(/** @type {StageId} */ ("approve"));
  const [protectedOutcomesReviewed, setProtectedOutcomesReviewed] = useState(false);
  const [writebackReviewed, setWritebackReviewed] = useState(false);
  const [executionProgress, setExecutionProgress] = useState(0);
  const [announcement, setAnnouncement] = useState(
    "Execution is waiting for protected-outcomes approval.",
  );
  const timers = useRef(/** @type {number[]} */ ([]));

  const clearTimers = useCallback(() => {
    timers.current.forEach((timer) => window.clearTimeout(timer));
    timers.current = [];
  }, []);

  useEffect(() => clearTimers, [clearTimers]);

  const phaseIndex = STAGE_ORDER.indexOf(phase);

  const stageStates = useMemo(
    () =>
      /** @type {Record<StageId, StageState>} */ (
        Object.fromEntries(
          STAGE_ORDER.map((stage, index) => [
            stage,
            index < phaseIndex ? "complete" : index === phaseIndex ? "current" : "locked",
          ]),
        )
      ),
    [phaseIndex],
  );

  const authorizeExecution = useCallback(() => {
    if (!protectedOutcomesReviewed || phase !== "approve") return;

    clearTimers();
    setPhase("execute");
    setExecutionProgress(0);
    setAnnouncement("Execution authorized. The idempotent transaction is running.");

    const stepDelay = prefersReducedMotion() ? 45 : 320;
    for (let step = 1; step <= EXECUTION_STEPS; step += 1) {
      timers.current.push(
        window.setTimeout(() => {
          setExecutionProgress(step);
          setAnnouncement(
            `Execution evidence recorded for ${step} of ${EXECUTION_STEPS} permitted mutations.`,
          );
        }, step * stepDelay),
      );
    }

    timers.current.push(
      window.setTimeout(
        () => {
          setPhase("verify");
          setAnnouncement(
            "Execution verified. Five permitted residuals are zero; two protected exceptions remain visible.",
          );
        },
        (EXECUTION_STEPS + 1) * stepDelay,
      ),
    );
  }, [clearTimers, phase, protectedOutcomesReviewed]);

  const returnToPlan = useCallback(() => {
    setProtectedOutcomesReviewed(false);
    setAnnouncement("Approval reset. The plan remains in dry-run review.");
  }, []);

  const authorizeWriteback = useCallback(() => {
    if (!writebackReviewed || phase !== "verify") return;
    setPhase("remember");
    setAnnouncement(
      "DataHub write-back approved. Fresh read-back verified tags, structured properties, and the reusable evidence document.",
    );
  }, [phase, writebackReviewed]);

  const resetDemo = useCallback(() => {
    clearTimers();
    setPhase("approve");
    setProtectedOutcomesReviewed(false);
    setWritebackReviewed(false);
    setExecutionProgress(0);
    setAnnouncement("Demo reset. Execution is waiting for protected-outcomes approval.");
  }, [clearTimers]);

  return {
    phase,
    phaseIndex,
    stageStates,
    protectedOutcomesReviewed,
    setProtectedOutcomesReviewed,
    writebackReviewed,
    setWritebackReviewed,
    executionProgress,
    announcement,
    authorizeExecution,
    returnToPlan,
    authorizeWriteback,
    resetDemo,
  };
}

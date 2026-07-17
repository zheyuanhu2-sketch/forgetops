import IconCircleCheck from "@tabler/icons-react/dist/esm/icons/IconCircleCheck.mjs";
import IconCircleDot from "@tabler/icons-react/dist/esm/icons/IconCircleDot.mjs";
import IconLock from "@tabler/icons-react/dist/esm/icons/IconLock.mjs";

/** @typedef {"complete" | "current" | "locked"} StageState */

/** @type {Record<StageState, string>} */
const STATE_LABELS = {
  complete: "Complete",
  current: "In progress",
  locked: "Queued",
};

/** @param {{ state: StageState }} props */
function StageIcon({ state }) {
  if (state === "complete") {
    return <IconCircleCheck aria-hidden="true" size={24} stroke={1.8} />;
  }
  if (state === "current") {
    return <IconCircleDot aria-hidden="true" size={24} stroke={1.8} />;
  }
  return <IconLock aria-hidden="true" size={19} stroke={1.8} />;
}

/**
 * @param {{
 *   stages: typeof import("../data/caseData.js").caseData.stages;
 *   stageStates: Record<string, StageState>;
 * }} props
 */
export function StageRail({ stages, stageStates }) {
  return (
    <nav className="stage-rail" aria-label="Case workflow progress">
      <ol>
        {stages.map((stage, index) => {
          const state = stageStates[stage.id];
          return (
            <li
              key={stage.id}
              className="stage-item"
              data-state={state}
              aria-current={state === "current" ? "step" : undefined}
            >
              <div className="stage-copy">
                <span className="stage-index">{String(index + 1).padStart(2, "0")}</span>
                <span className="stage-label">{stage.label}</span>
                <span className="stage-state">
                  {STATE_LABELS[state]}
                  {state === "complete" && index < 2 ? ` ${index === 0 ? "10:47" : "10:48"}` : ""}
                </span>
              </div>
              <StageIcon state={state} />
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

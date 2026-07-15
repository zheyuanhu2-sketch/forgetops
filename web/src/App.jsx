import { AppHeader } from "./components/AppHeader.jsx";
import { ApprovalConsole } from "./components/ApprovalConsole.jsx";
import { EvidenceFooter } from "./components/EvidenceFooter.jsx";
import { EvidenceTimeline } from "./components/EvidenceTimeline.jsx";
import { ImpactMap } from "./components/ImpactMap.jsx";
import { StageRail } from "./components/StageRail.jsx";
import caseData from "./data/caseData.js";
import { useForgetOpsWorkflow } from "./hooks/useForgetOpsWorkflow.js";

export function App() {
  const workflow = useForgetOpsWorkflow();

  return (
    <main className="workbench" data-phase={workflow.phase}>
      <AppHeader caseRecord={caseData.case} connected={caseData.datahub.connected} />
      <StageRail stages={caseData.stages} stageStates={workflow.stageStates} />
      <div className="case-work-area">
        <EvidenceTimeline
          data={caseData}
          phase={workflow.phase}
          phaseIndex={workflow.phaseIndex}
          executionProgress={workflow.executionProgress}
        />
        <ImpactMap data={caseData} phase={workflow.phase} />
      </div>
      <ApprovalConsole data={caseData} workflow={workflow} />
      <EvidenceFooter data={caseData} phase={workflow.phase} />
      <p className="sr-only" aria-live="polite" aria-atomic="true">
        {workflow.announcement}
      </p>
    </main>
  );
}

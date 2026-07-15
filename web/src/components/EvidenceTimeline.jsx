import IconChecklist from "@tabler/icons-react/dist/esm/icons/IconChecklist.mjs";
import IconDatabaseExport from "@tabler/icons-react/dist/esm/icons/IconDatabaseExport.mjs";
import IconFileTextShield from "@tabler/icons-react/dist/esm/icons/IconFileTextShield.mjs";
import IconGitMerge from "@tabler/icons-react/dist/esm/icons/IconGitMerge.mjs";
import IconScale from "@tabler/icons-react/dist/esm/icons/IconScale.mjs";
import IconSearch from "@tabler/icons-react/dist/esm/icons/IconSearch.mjs";
import IconShieldCheck from "@tabler/icons-react/dist/esm/icons/IconShieldCheck.mjs";
import { STAGE_ORDER } from "../hooks/useForgetOpsWorkflow.js";

/** @typedef {typeof import("../data/caseData.js").caseData} CaseData */
/** @typedef {import("../hooks/useForgetOpsWorkflow.js").StageId} StageId */
/** @typedef {"intake" | "discover" | "decide" | "approve" | "execute" | "verify" | "remember"} EventType */
/**
 * @typedef {{
 *   id: string;
 *   type: EventType;
 *   stage: StageId;
 *   time: string;
 *   title: string;
 *   detail: string;
 *   source: string;
 *   call: string;
 *   duration: string;
 *   evidence: string;
 * }} TimelineEvent
 */

/** @type {Record<EventType, import("react").ComponentType<{ size?: number; stroke?: number }>>} */
const EVENT_ICONS = {
  intake: IconFileTextShield,
  discover: IconSearch,
  decide: IconScale,
  approve: IconShieldCheck,
  execute: IconGitMerge,
  verify: IconChecklist,
  remember: IconDatabaseExport,
};

/** @type {TimelineEvent[]} */
const EVENTS = [
  {
    id: "ev-01",
    type: "intake",
    stage: "discover",
    time: "10:46:58",
    title: "Case intake",
    detail: "Subject request received and normalized. The raw identifier was immediately hashed.",
    source: "ForgetOps",
    call: "hash_subject",
    duration: "0.42s",
    evidence: "ev_20260715_104658_01",
  },
  {
    id: "ev-02",
    type: "discover",
    stage: "discover",
    time: "10:47:02",
    title: "DataHub discovery",
    detail:
      "Bounded MCP traversal reconstructed the privacy scope without retrieving a raw subject identifier.",
    source: "DataHub",
    call: "discover_scope",
    duration: "2.81s",
    evidence: "ev_20260715_104702_02",
  },
  {
    id: "ev-03",
    type: "decide",
    stage: "decide",
    time: "10:47:06",
    title: "Decision",
    detail: "Policy evidence classified every asset and preserved both protected outcomes.",
    source: "DataHub context",
    call: "compile_plan",
    duration: "0.91s",
    evidence: "ev_20260715_104706_03",
  },
  {
    id: "ev-04",
    type: "approve",
    stage: "approve",
    time: "10:47:08",
    title: "Approval boundary",
    detail: "Approval is scope-bound to five safe mutations in dry-run mode.",
    source: "ForgetOps",
    call: "bind_approval",
    duration: "0.67s",
    evidence: "ev_20260715_104708_04",
  },
  {
    id: "ev-05",
    type: "execute",
    stage: "execute",
    time: "10:47:10",
    title: "Idempotent execution",
    detail: "One transaction applies only the five permitted actions; rollback remains armed.",
    source: "DuckDB sandbox",
    call: "execute_plan",
    duration: "1.60s",
    evidence: "ev_20260715_104710_05",
  },
  {
    id: "ev-06",
    type: "verify",
    stage: "verify",
    time: "10:47:12",
    title: "Post-action verification",
    detail: "All seven outcomes were checked: five clear, one retained, and one pending review.",
    source: "ForgetOps",
    call: "verify_outcomes",
    duration: "0.83s",
    evidence: "ev_20260715_104712_06",
  },
  {
    id: "ev-07",
    type: "remember",
    stage: "remember",
    time: "10:47:15",
    title: "DataHub memory",
    detail: "Tags, structured properties, and the reusable evidence document were read back fresh.",
    source: "DataHub",
    call: "writeback_readback",
    duration: "1.14s",
    evidence: "ev_20260715_104715_07",
  },
];

/**
 * @param {{ event: TimelineEvent; data: CaseData; executionProgress: number }} props
 */
function EventMetrics({ event, data, executionProgress }) {
  if (event.type === "intake") {
    return <strong className="proof-alert">0 raw identifiers in audit</strong>;
  }
  if (event.type === "discover") {
    return (
      <div className="event-facts">
        <strong>
          {data.metrics.assets} assets · {data.metrics.lineageEdges} edges ·{" "}
          {data.metrics.piiFields} PII fields
        </strong>
        <strong>
          {data.metrics.datahubCalls} DataHub calls · {data.metrics.ownerCoveragePct}% owner
          coverage
        </strong>
      </div>
    );
  }
  if (event.type === "decide") {
    return (
      <div className="decision-facts">
        <strong>{data.metrics.safeMutations} approved mutations</strong>
        <strong>{data.metrics.legalHolds} legal hold</strong>
        <strong>{data.metrics.manualReviews} manual review</strong>
      </div>
    );
  }
  if (event.type === "approve") {
    return (
      <div className="scope-facts">
        <span>Scope</span>
        <strong>{data.metrics.safeMutations} assets scheduled for safe mutation.</strong>
        <strong>{data.metrics.legalHolds} retained under legal hold.</strong>
        <strong>{data.metrics.manualReviews} routed to manual review — not modified.</strong>
      </div>
    );
  }
  if (event.type === "execute") {
    return (
      <div className="execution-meter" aria-label={`${executionProgress} of 5 actions evidenced`}>
        <span style={{ width: `${(executionProgress / 5) * 100}%` }} />
        <strong>{executionProgress} / 5 mutation receipts</strong>
      </div>
    );
  }
  if (event.type === "verify") {
    return (
      <div className="event-facts">
        <strong>Idempotent replay verified</strong>
        <strong>Transaction rollback verified</strong>
      </div>
    );
  }
  return (
    <div className="event-facts">
      <strong>{data.writeback.verifiedEntityCount} entities read back</strong>
      <strong>{data.writeback.verificationTools.join(" · ")}</strong>
    </div>
  );
}

/**
 * @param {TimelineEvent} event
 * @param {number} phaseIndex
 * @returns {"complete" | "current" | "locked"}
 */
function eventStatus(event, phaseIndex) {
  const eventStageIndex = STAGE_ORDER.indexOf(event.stage);
  if (eventStageIndex < phaseIndex) return "complete";
  if (eventStageIndex === phaseIndex) return "current";
  return "locked";
}

/**
 * @param {{
 *   data: CaseData;
 *   phase: StageId;
 *   phaseIndex: number;
 *   executionProgress: number;
 * }} props
 */
export function EvidenceTimeline({ data, phase, phaseIndex, executionProgress }) {
  const visibleEvents = EVENTS.filter((event) => STAGE_ORDER.indexOf(event.stage) <= phaseIndex);

  return (
    <section className="evidence-timeline" aria-labelledby="evidence-trace-title">
      <header className="section-columns" aria-hidden="true">
        <span>Time (UTC)</span>
        <span>Event</span>
        <span>Evidence &amp; provenance</span>
      </header>
      <h1 id="evidence-trace-title" className="sr-only">
        Case evidence trace
      </h1>
      <ol>
        {visibleEvents.map((event, index) => {
          const Icon = EVENT_ICONS[event.type];
          const state = eventStatus(event, phaseIndex);
          const isLast = index === visibleEvents.length - 1;
          return (
            <li key={event.id} className="timeline-event" data-state={state} data-last={isLast}>
              <time>{event.time}</time>
              <div className="event-marker" aria-hidden="true">
                <Icon size={21} stroke={1.65} />
              </div>
              <div className="event-copy">
                <h2>{event.title}</h2>
                <p>{event.detail}</p>
                <EventMetrics event={event} data={data} executionProgress={executionProgress} />
              </div>
              <div className="event-provenance">
                <strong>{event.source}</strong>
                <dl>
                  <div>
                    <dt>call</dt>
                    <dd>{event.call}</dd>
                  </div>
                  <div>
                    <dt>duration</dt>
                    <dd>{event.duration}</dd>
                  </div>
                  <div>
                    <dt>evidence</dt>
                    <dd>{event.evidence}</dd>
                  </div>
                </dl>
                {event.type === "approve" ? (
                  <p className="subject-proof">Raw subject identifiers never appear.</p>
                ) : null}
              </div>
              <span className="event-status">
                {state === "current" && phase === "execute"
                  ? "Running"
                  : state === "current"
                    ? "In progress"
                    : "Complete"}
              </span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

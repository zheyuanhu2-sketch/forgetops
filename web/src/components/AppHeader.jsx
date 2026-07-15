import IconLayersLinked from "@tabler/icons-react/dist/esm/icons/IconLayersLinked.mjs";
import IconShieldLock from "@tabler/icons-react/dist/esm/icons/IconShieldLock.mjs";

/**
 * @param {string} value
 */
function formatAuditTime(value) {
  const iso = new Date(value).toISOString();
  return `${iso.slice(0, 10)} ${iso.slice(11, 19)} UTC`;
}

/**
 * @param {{
 *   caseRecord: typeof import("../data/caseData.js").caseData.case;
 *   connected: boolean;
 * }} props
 */
export function AppHeader({ caseRecord, connected }) {
  return (
    <header className="identity-bar">
      <div className="brand-lockup" aria-label="ForgetOps">
        <span>Forget</span>
        <span>Ops</span>
      </div>
      <div className="identity-divider" aria-hidden="true" />
      <p className="case-identity">
        <span>Case</span>
        <strong>{caseRecord.id}</strong>
      </p>
      <div className="identity-spacer" />
      <p className="connection-state" data-connected={connected}>
        <IconLayersLinked aria-hidden="true" size={19} stroke={1.8} />
        <span>DataHub connected</span>
      </p>
      <div className="identity-divider" aria-hidden="true" />
      <p className="mode-state">
        <IconShieldLock aria-hidden="true" size={15} stroke={1.8} />
        <span>Dry run</span>
      </p>
      <p className="audit-clock">
        <span>Audit clock</span>
        <time dateTime={caseRecord.generatedAt}>{formatAuditTime(caseRecord.generatedAt)}</time>
      </p>
    </header>
  );
}

# ForgetOps Design QA

## Comparison target

- Source visual truth: `C:\Users\胡哲源\.codex\generated_images\019f6572-f190-7233-81e0-3310e1626fe2\exec-0f5c741b-2dd6-4fdf-9da2-7b7473acc8aa.png`
- Browser-rendered implementation: `C:\Users\胡哲源\AppData\Local\Temp\forgetops-design-qa-exact.png`
- Local implementation URL: `http://127.0.0.1:4173/`
- Viewport: 1487 x 1058, matching the source raster exactly
- State: initial `Approve` state, dry run, protected-outcomes acknowledgement unchecked
- Comparison method: both original-resolution images were opened in one comparison input after matching viewport, theme, state, crop, and content density.

## Findings

- No actionable P0, P1, or P2 findings remain.
- [P3] The reference shows an enabled crimson authorization button while the implementation keeps the button visibly disabled until the protected-outcomes checkbox is checked. This is an intentional safety constraint: it communicates the required approval boundary and is covered by an interaction test.
- [P3] The implementation uses the repository's seven real safe-sample entity names and lineage rather than the illustrative names in the source. Short truthful display aliases preserve legibility while accessible names retain the complete entity names.

## Required fidelity surfaces

- Fonts and typography: the Fraunces wordmark plus IBM Plex Sans Condensed and IBM Plex Mono reproduce the editorial/forensic hierarchy, narrow labels, evidence density, weights, line heights, and tracking. The final graph labels do not truncate.
- Spacing and layout rhythm: header, six-stage filmstrip, split evidence/impact workspace, approval console, and evidence footer retain the source ordering and proportions. The exact-size render has no page-level horizontal overflow.
- Colors and visual tokens: near-black/blue-black surfaces, graphite rules, crimson active state, DataHub blue, verified green, and exception amber match the source's restrained semantic palette. Disabled and focus-visible states remain distinct.
- Image quality and asset fidelity: the target contains no photographic or illustrative assets. Icons use one Tabler stroke family, and the impact map is a real React Flow data view rather than a custom SVG, CSS illustration, placeholder, or embedded screenshot.
- Copy and content: above-the-fold static copy matches `IMPLEMENTATION_INVENTORY.md`. Dynamic entity, tool, policy, evidence, and outcome copy comes only from the safe sample adapter. No marketing hero, extra navigation, raw subject identifier, or invented result was added.

## Full-view comparison evidence

The exact-size final comparison preserves the same three-level hierarchy: global case status, six-stage evidence filmstrip, then the evidence/lineage workspace with a persistent approval and verification footer. Region borders, compact typography, active-stage color, event rail, policy exceptions, graph legend, and evidence callouts read as the same design system. The implementation's graph and approval copy are slightly denser because they expose real evidence, but neither changes the target composition or visual priority.

## Focused-region comparison evidence

A separate crop was not required because both 1487 x 1058 originals were inspected at original detail and every dense region remained legible. The most fidelity-sensitive graph region was also checked in the rendered DOM: all seven visible labels reported `scrollWidth <= clientWidth` after the fix. The approval dialog was inspected separately through its accessible DOM and keyboard focus state.

## Responsiveness and accessibility

- 1280 x 720: no page overflow; all seven graph nodes remained inside the impact-map viewport after layout settled.
- 390 x 844: no page-level horizontal overflow; the stage filmstrip intentionally scrolls horizontally; the graph becomes a semantic asset list; primary controls are 42-48 px high.
- Automated accessibility: axe reported no serious or critical violations.
- Keyboard behavior: opening evidence details moves focus to Close; Escape closes the modal; focus returns to View details.
- Reduced-motion styling, visible focus states, semantic controls, labels, and separated approval checkboxes are present.

## Primary interactions tested

1. Execution authorization remains disabled until the protected-outcomes acknowledgement is checked.
2. Authorization advances to deterministic execution and records five of five receipts.
3. Verification preserves one legal hold and one manual-review exception.
4. DataHub write-back requires a second, separate acknowledgement and approval.
5. Remember state reports seven fresh entity read-backs and a reusable evidence document.
6. Evidence details open as a modal and support keyboard dismissal and focus restoration.

## Browser and engineering evidence

- Clean fresh browser tab: zero warning or error console entries.
- Format check, ESLint, TypeScript check, seven Vitest tests, deterministic demo smoke, coverage, and production build passed.

## Comparison history

### Pass 1 - blocked

- Earlier P1 finding: long real entity names were visibly truncated in the React Flow graph, weakening evidence readability compared with the source's fully readable node labels.
- Fix: added truthful short display aliases, retained complete accessible entity names, and widened graph nodes from 170 px to 184 px.
- Post-fix evidence: `C:\Users\胡哲源\AppData\Local\Temp\forgetops-design-qa-desktop-pass2.png`; all seven graph labels measured without overflow.

### Pass 2 - blocked

- Earlier P1 finding: the evidence modal opened without moving focus, leaving keyboard focus on the obscured trigger.
- Fix: moved focus to the close control, trapped the single modal tab stop, added Escape dismissal, restored focus to the trigger, and added an integration assertion.
- Post-fix evidence: browser DOM showed `Close evidence details [active]`; after Escape the dialog count was zero and `View details` was active.

### Pass 3 - passed

- Exact-size final screenshot: `C:\Users\胡哲源\AppData\Local\Temp\forgetops-design-qa-exact.png`.
- Combined original-detail comparison found no remaining actionable P0/P1/P2 fidelity, responsive, interaction, content, icon, asset, or accessibility issues.

## Implementation checklist

- [x] Preserve the selected Case Filmstrip / Evidence Timeline direction.
- [x] Use real safe-sample graph and evidence data.
- [x] Keep execution and DataHub write-back behind separate approvals.
- [x] Verify desktop, compact desktop, and mobile layouts.
- [x] Verify keyboard modal behavior and automated accessibility.
- [x] Run browser console and engineering gates.

## Follow-up polish

- Optional P3 only: capture one additional public gallery image from the completed `Remember` state for the Devpost submission.

final result: passed

## 2026-07-17 finesse polish pass

- Preserved the accepted Case Filmstrip / Evidence Timeline structure, graphite palette, crimson
  approval boundary, DataHub provenance blue, and two distinct approvals.
- Increased the smallest evidence, provenance, status, and console labels by 1 px and raised the
  muted-ink token so dense evidence remains readable without reducing information density.
- Added visible, state-aware explanations directly under both gated approval buttons. Each message
  changes from the missing review requirement to the exact locked scope when the acknowledgement is
  complete, and each button exposes that explanation through `aria-describedby`.
- Added a keyboard skip link, `aria-current="step"` on the active workflow stage, `aria-busy` during
  execution, and semantic progressbar values for receipt capture.
- Consolidated bar, node, disabled, overlay, edge, and grid colors into the design token layer; no
  component retains a raw color value.
- The static detector's eyebrow heuristic remains a documented false positive: `console-label`,
  `section-kicker`, and footer labels identify operational regions in a dense product console; they
  are not repeated marketing eyebrows and removing them would reduce evidence scanability.
- Browser QA passed at 1920 x 1080, 1280 x 720, and 390 x 844. The compact desktop pass found and
  fixed an overlap between `PARTIAL_VERIFIED` and the DataHub write-back region. The final layouts
  have no page-level horizontal or vertical overflow; the mobile stage rail remains the only
  intentional horizontal scroller, and all seven assets remain visible in the semantic mobile list.
- The real interaction path passed from protected-outcome acknowledgement through five receipt
  captures, the separate DataHub write-back approval, and fresh-session read-back. Browser console
  output remained free of warnings and errors.

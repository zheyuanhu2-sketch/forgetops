# ForgetOps Demo Storyboard

## Production target

- Format: 1920 x 1080, 30 fps, English narration and word-level captions.
- Hard limit: strictly under 3:00. Measured narration: 2:10.069. Composition target: 2:15 including the closing hold.
- Claim boundary: the UI is a deterministic replay of a verified DataHub MCP run; it is not presented as a live button-to-DataHub connection.
- Audio: narration plus restrained self-generated UI ticks only. No licensed music.
- Visual grammar: forensic editorial instrument, thin graphite rules, crimson approval, DataHub blue provenance, verified green, exception amber.
- Motion grammar: causal reveals, bounded camera pushes, evidence-mask wipes, and short dissolves. No perpetual motion, bounce, confetti, or generic SaaS cards.

## Captured-asset audit

| Asset | Use | Treatment |
| --- | --- | --- |
| `screenshots/scroll-000.png` | Yes | Full-workbench establishing shot; slow 1.00 to 1.05 camera push. |
| `product-states/01-approve.png` | Yes | Approval boundary; crop to stage rail and approval console. |
| `product-states/02-execute.png` | Yes | Execution handoff; mechanical horizontal wipe from approval. |
| `product-states/03-receipts.png` | Yes | Receipt proof; crop to `3 of 5` and transaction boundary. |
| `product-states/04-verify.png` | Yes | Honest verification; footer metrics and second approval. |
| `product-states/05-remember.png` | Yes | Fresh read-back and remembered state. |
| `product-states/06-evidence-contract.png` | Yes | Closing proof; modal enlarged without recreating it. |
| `assets/svgs/contact-sheet-1.jpg` | Audit only | Not shipped; composite preview would duplicate source icons. |
| `assets/svgs/contact-sheet-2.jpg` | Audit only | Not shipped; composite preview would duplicate source icons. |
| `assets/svgs/logo-183505ae.svg` | No | Captured Tabler icon, not a distinct ForgetOps wordmark. |
| `assets/svgs/logo-87d1eb8b.svg` | No | Captured Tabler icon, not a distinct ForgetOps wordmark. |
| `assets/svgs/svg-035dfb8b.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-0b7b98e7.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-12c39ecd-2.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-12c39ecd-3.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-12c39ecd.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-203613a6.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-38f10189.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-4975974d.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-4ac79ac1.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-5af212fb-2.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-5af212fb-3.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-5af212fb-4.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-5af212fb.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-648b2b06.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-6a23e7ef.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-7af9e4a8.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-7b63a7b7.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-87d1eb8b.svg` | No | Duplicate captured UI icon. |
| `assets/svgs/svg-961d88e5.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-9c125d23.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-ac142c3b.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-b8f3ed0d.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-d7cceda4.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-d9142af9.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-e4b52232.svg` | No | Already rendered inside the product captures. |
| `assets/svgs/svg-eb62dcdf.svg` | No | Already rendered inside the product captures. |

No captured font files exist. The composition uses local system fallbacks aligned to the product roles: Georgia for the editorial wordmark, `Arial Narrow` for operational copy, and Consolas for evidence data. This avoids network font fetching and keeps rendering deterministic.

## Beat sheet

### 01 — The proof gap — 0:00–0:06.8

- Narration: deleting one row is easy; downstream proof and legal-hold safety are the real problem.
- Visual: blue-black field, thin evidence rule draws across frame, then the full workbench resolves from darkness.
- Text: `DELETE IS EASY.` then `PROOF IS THE WORK.` at 92 px.
- Techniques: mask reveal, restrained parallax, localized crimson radial glow.
- Transition: 12-frame dissolve into the product plane.

### 02 — One continuous case trace — 0:06.8–0:11.3

- Narration: ForgetOps turns DataHub context into an approval-gated privacy operation and the UI is a deterministic replay.
- Visual: `scroll-000.png`; camera pushes from full workbench toward the case filmstrip and audit timeline.
- Evidence callout: `VERIFIED DATAHUB MCP RUN · DETERMINISTIC REPLAY`.
- Techniques: Ken Burns crop, clip-path label reveal, blue provenance underline.
- Transition: horizontal push following the stage rail.

### 03 — Discover the real blast radius — 0:11.3–0:35.5

- Narration: identifier hashing, bounded official MCP calls, 7 assets, 6 edges, 19 PII fields, 100% owner coverage.
- Visual: same capture, framed first on the discovery event and then on the real lineage graph.
- Counter strip: `21 CALLS  /  7 ASSETS  /  6 EDGES  /  19 PII FIELDS`.
- Techniques: stepped counter reveal, camera pan, causal line trace.
- Transition: amber rule sweeps into the decision state.

### 04 — Policy keeps exceptions visible — 0:35.5–0:52.0

- Narration: policy comes from organization-defined evidence; 5 safe, 1 legal hold, 1 human review.
- Visual: graph crop with three outcome labels; finance and churn-feature nodes remain visible.
- Text: `5 SAFE` in green, `1 LEGAL HOLD` and `1 HUMAN REVIEW` in amber.
- Techniques: evidence brackets, staggered text reveal, subtle depth separation.
- Transition: crimson mechanical shutter into approval.

### 05 — Human approval binds the scope — 0:52.0–1:00.2

- Narration: reviewer acknowledges protected outcomes; exactly five dry-run actions, rollback armed.
- Visual: `01-approve.png`; zoom to checkbox, scope, dry-run badge, and authorization control.
- Text: `APPROVAL IS SCOPE, NOT A BLANK CHECK.`
- Techniques: focus crop, crimson rule pulse, approval-state wipe.
- Transition: direct cut on authorization tick to execution.

### 06 — One idempotent transaction — 1:00.2–1:11.5

- Narration: only the permitted plan executes, every action emits a receipt, failure rolls back the transaction.
- Visual: `02-execute.png` to `03-receipts.png`; receipt counter advances and transaction boundary is enlarged.
- Text: `ONE TRANSACTION · FIVE RECEIPTS · ROLLBACK ARMED`.
- Techniques: receipt-stack reveal, numeric progression, shallow camera push.
- Transition: blue evidence line travels into verification.

### 07 — Honest verification — 1:11.5–1:27.4

- Narration: zero permitted residuals; legal hold and review remain; result is `PARTIAL_VERIFIED`; replay is idempotent.
- Visual: `04-verify.png`; crop lower footer and then reveal second approval area.
- Text: `0 CLEARED RESIDUALS  /  1 HOLD  /  1 REVIEW`.
- Techniques: metric lockup, amber exception hold, short dissolve.
- Transition: second approval boundary slides in from right.

### 08 — Write back requires a second approval — 1:27.4–1:39.6

- Narration: execution approval does not authorize DataHub metadata write-back; only then write tags, properties, and one evidence document.
- Visual: `04-verify.png`; crop the second checkbox and `Approve DataHub write-back` control.
- Text: `SEPARATE AUTHORITY. SEPARATE AUDIT EVIDENCE.`
- Techniques: split-screen comparison, crimson approval bracket, blue tool labels.
- Transition: data-blue dissolve into remembered state.

### 09 — Fresh read-back proves it — 1:39.6–1:49.8

- Narration: mutation-disabled MCP session reads back 7 entities, the document, and the same URN; no raw identifiers.
- Visual: `05-remember.png` then `06-evidence-contract.png`; modal becomes the hero evidence plane.
- Tool rail: `add_tags · add_structured_properties · save_document` then `get_entities · search_documents · grep_documents`.
- Techniques: modal-scale match cut, tool-name cascade, verified-green keyline.
- Transition: modal dims while test proof rises from below.

### 10 — Operational proof — 1:49.8–2:15.0

- Narration: live and offline paths share one strict model; 79 tests cover the full journey; exceptions, approvals, and claims are replayable.
- Visual: evidence contract remains in background; foreground proof ledger resolves to the final statement.
- Text: `79 AUTOMATED TESTS` then `DATAHUB CONTEXT → OPERATIONAL PROOF`.
- Closing lockup: `ForgetOps` / `Exceptions visible. Approvals explicit. Evidence replayable.`
- Techniques: ledger reveal, final editorial title, 18-frame fade to blue-black.

## Composition architecture

- One seek-safe root composition with ten absolute scene groups and nine overlapping transitions.
- Shared frame, caption, metric-strip, product-crop, and evidence-rule components.
- All timing derives from measured narration and the word-level transcript; this draft timing is only the ceiling.
- Each product image is referenced as a real file asset and animated as a plane. No iframe, reconstructed dashboard, fake logo, inline SVG, or network fetch.
- Captions sit in a dedicated lower safe zone, two lines maximum, with an opaque `#071117` backing strip when a product crop is visually dense.

## Verification plan

- Run HyperFrames lint, validate, inspect, snapshot, and check.
- Inspect beginning, transition, approval, receipt, verification, evidence-contract, and final snapshots at 1920 x 1080.
- Render MP4 only after preview validation.
- Confirm exact duration with `ffprobe` and reject any output at or above 180 seconds.

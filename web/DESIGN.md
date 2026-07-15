# ForgetOps Web Design System

## Source of truth

Accepted Product Design concept: `%CODEX_HOME%\generated_images\019f6572-f190-7233-81e0-3310e1626fe2\exec-0f5c741b-2dd6-4fdf-9da2-7b7473acc8aa.png`.

Native comparison viewport: 1440 x 1024 desktop. The implementation must also remain usable at 1280 x 720 and collapse cleanly below 900 px without hiding primary actions.

## Style prompt

A calm forensic operations console built like an investigative case filmstrip: dark blue-black editorial canvas, crisp one-pixel rules, compact monospaced evidence labels, narrow humanist UI text, a restrained crimson approval boundary, icy DataHub provenance blue, amber exceptions, and green verified facts. The screen should feel exact, auditable, and high-stakes without looking militaristic or theatrical.

## Palette

- Canvas: `#071117`
- Raised canvas: `#0B161D`
- Open panel: `#0D1920`
- Strong rule: `#3B4B52`
- Quiet rule: `#26353C`
- Primary text: `#F0F2EE`
- Secondary text: `#A5B0B2`
- Muted text: `#77858A`
- Approval crimson: `#D4363E`
- Approval crimson hover: `#EC4950`
- DataHub provenance: `#45A7FF`
- Verified: `#78DD67`
- Exception amber: `#F3A70B`
- Focus ring: `#D9F0FF`

No gradients. No glow. No glass. No broad shadows. State is communicated with color, copy, line treatment, and icons together.

## Typography

- Brand wordmark: Fraunces 600, 24 px, tight tracking.
- Product/UI text: IBM Plex Sans Condensed 400/500/600.
- Evidence labels, timestamps, counts, and machine states: IBM Plex Mono 400/500/600.
- Desktop display scale: 24 / 20 / 17 / 15 / 13 / 11 px.
- Body line height: 1.35 to 1.5. Labels use uppercase tracking between 0.08 and 0.15 em.
- Controls always declare family, size, weight, tracking, and line height explicitly.

## Geometry and spacing

- 4 px base spacing; main scale: 4, 8, 12, 16, 20, 24, 32.
- Screen padding is 16 to 24 px; the main split is approximately 58/42 at the native viewport.
- Panels are open regions divided by 1 px rules, not floating cards.
- Status controls may use 3 to 5 px radii. Main regions remain square.
- Interactive targets are at least 44 px. Focus rings are 2 px and offset 2 px.

## Primary anatomy

1. Identity bar: ForgetOps, case ID, DataHub connection, dry-run/live mode, deterministic audit time.
2. Six-stage filmstrip: Discover, Decide, Approve, Execute, Verify, Remember.
3. Evidence timeline: chronological facts, calls, durations, and immutable evidence IDs.
4. Impact map: exactly seven real repository assets and six real lineage edges.
5. Approval console: protected-outcomes acknowledgement and approval-specific action.
6. Evidence footer: residuals, retained and review exceptions, case status, and the separate write-back gate.

## Component families

- `StageRail`: complete, active, queued, and locked variants.
- `EvidenceEvent`: complete, active, executing, verified, and remembered variants.
- `StatusMark`: icon plus text; never color-only.
- `ImpactMap`: semantic graph with mutation, legal-hold, review, and verified variants.
- `ApprovalConsole`: execution approval, running, write-back approval, and remembered variants.
- `MetricProof`: small evidence metric separated by rules; never a dashboard card.
- `ActionButton`: primary crimson, secondary outline, disabled, focus, and success variants.

## Interaction and motion

- Initial state is dry-run approval. The execution button stays disabled until protected outcomes are explicitly acknowledged.
- Authorizing execution moves through Execute to Verify with deterministic progress; reduced-motion users receive immediate state changes.
- Verification exposes zero residuals for permitted mutations, one retained legal-hold record, and one pending review.
- DataHub write-back requires a second explicit approval. Read-back evidence completes Remember.
- Motion uses opacity and small 4 to 12 px translations only, 140 to 320 ms, with no looping animation.

## Icon treatment

Use Tabler Icons React: monoline, 1.7 to 2 px stroke, mostly 16 to 20 px. Match the reference metaphors for search, scale/decision, shield/approval, lock, check, database/stack, refresh, alert, and audit evidence. Do not draw icons with CSS or text glyphs.

## Responsive behavior

- At 1024 px and above, preserve filmstrip, timeline/graph split, bottom approval console, and evidence footer.
- Between 700 and 1023 px, keep the stage rail horizontally scrollable, stack timeline above impact map, and keep the approval action sticky.
- Below 700 px, show a compact vertical case narrative; graph nodes become a semantic ordered asset list while preserving every status and owner. Never hide legal hold, manual review, approval scope, or write-back separation.

## Accessibility

- Meet WCAG 2.2 AA contrast.
- Use semantic buttons, checkboxes, headings, ordered lists, progress/status text, and `aria-live` for stage changes.
- All interactions are keyboard reachable; no hover-only information.
- Preserve 200% zoom and reduced motion.
- Use icons and explicit text in addition to color.

## What not to do

- No generic card grid, KPI dashboard, neon hacker styling, AI purple, chatbot, or data-theater decoration.
- No rounded bento containers, glassmorphism, gradients, glows, emojis, CSS drawings, handcrafted SVGs, or placeholder charts.
- No raw data-subject identifier in DOM, URLs, browser storage, telemetry, screenshots, or evidence.
- Do not imply that legal-hold or manual-review assets are mutated.
- Do not merge execution approval with DataHub write-back approval.

# Official rules checklist

Verified on 2026-07-15 against the official [hackathon rules](https://datahub.devpost.com/rules), [schedule](https://datahub.devpost.com/details/dates), [resources](https://datahub.devpost.com/resources), and Devpost's [submission-steps guide](https://help.devpost.com/article/126-know-your-submission-steps) and [final-submission guide](https://help.devpost.com/article/122-how-to-enter-a-submission).

## Eligibility and timing

- Registration/submission period: 2026-07-06 09:00 ET through 2026-08-10 17:00 ET.
- China Standard Time deadline: **2026-08-11 05:00 GMT+8**.
- Internal submission freeze: **2026-08-08 22:00 GMT+8** to preserve a recovery buffer.
- Judging period: 2026-08-17 10:00 ET through 2026-08-31 17:00 ET.
- Keep every judge-facing URL free, working, and unrestricted until judging ends: **2026-09-01 05:00 GMT+8**.
- Entrants must be at least 18 or the age of majority where they live.
- The entrant is 19 and lives in mainland China. Mainland China is not among the exclusions listed in the official rules; final eligibility remains subject to sponsor/administrator verification.
- The project and submitted work must be newly created during the submission period. This repository was initialized on 2026-07-15.
- Standard developer tools and AI coding assistants are permitted. Any pre-existing code or work included in the final entry must be identified and disclosed; the current implementation is new work created in this repository.

## Required project integration

- Use DataHub open source together with at least one of: MCP Server, Agent Context Kit, DataHub Skills, or Analytics Agent.
- ForgetOps uses DataHub Core plus the official MCP Server. Any write-back or other mutation remains dry-run by default, requires explicit approval, and produces audit evidence.
- The submitted build must install and run consistently on its stated platform and must match the claims and behavior shown in the story and video.

## Judging path and strategy

### Stage One: pass/fail viability

Before scoring, judges apply a pass/fail screen: the project must reasonably fit the hackathon theme and reasonably apply the required DataHub APIs/SDKs. The README, opening video sequence, and submission summary must make both facts immediately obvious.

### Stage Two: equal-weight scoring

Submissions that pass Stage One are scored on five equally weighted criteria:

1. **Use of DataHub:** demonstrate real graph discovery, lineage traversal, schema/governance context, and an auditable DataHub-backed workflow rather than a superficial API call. Contribute context back to the graph where appropriate.
2. **Technical Execution:** retain deterministic offline mode, typed boundaries, defensive failure handling, automated tests, and a repeatable live integration smoke test.
3. **Originality:** make graph-aware privacy erasure and retention-conflict reasoning the defining capability, not a generic chat wrapper or a reimplementation of a shipped DataHub feature.
4. **Real-World Usefulness:** show how a privacy or governance team can turn a data-subject request into a reviewable, safe action plan with evidence.
5. **Submission Quality:** deliver an English README, reproducible setup, concise public demo, checked-in synthetic evidence, and a polished Devpost narrative.

Tie scores are resolved in that exact criterion order: the first higher applicable criterion score wins; remaining ties proceed to the next criterion, and a judge-panel vote resolves a tie across all criteria. A meaningful open-source contribution to DataHub may earn bonus consideration, but it is optional and must not put the core submission at risk.

## Required submission assets

- [x] Working project URL that gives judges easy access to a hosted app, functioning demo, or test build.
- [x] Public code repository containing all source, assets, and complete setup instructions needed to run the project.
- [x] Apache License 2.0 file at repository root.
- [x] GitHub About section detects and displays the Apache 2.0 license.
- [x] English project description covering features, functionality, technologies, and data.
- [x] Public demo video **strictly under three minutes** on YouTube, Vimeo, or Youku.
- [x] Video shows the functioning project on its target device; do not rely only on slides or mockups.
- [x] Video playback and embedding work without sign-in or a permission request.
- [x] No third-party trademarks, copyrighted music, or other protected material appears in the video without documented permission.
- [x] Checked-in synthetic sample input and validated sample-output evidence bundle.
- [x] Free, unrestricted judge access remains available through **2026-09-01 05:00 GMT+8**. If a demo is private, include working test credentials and instructions.
- [ ] Complete the optional feedback survey before the submission deadline if pursuing a feedback prize.

Judges are not required to run the project and may judge only the text, images, and video. Those assets must therefore communicate the complete value proposition and credible proof even if the live demo is not opened.

## Devpost form and finalization

Devpost's generic submission workflow confirms these standard assets:

- [ ] Team/entrant details.
- [ ] Project name and tagline.
- [ ] Project-gallery thumbnail (JPG, PNG, or GIF; at most 5 MB; 3:2 recommended).
- [ ] Project story.
- [ ] “Built with” tags.
- [ ] Try-it-out link(s).
- [ ] Image gallery with relevant screenshots, diagrams, or supporting images.
- [ ] Public demo-video link.
- [ ] Any event-specific additional details.
- [ ] Terms acceptance and final **Submit project** action.
- [ ] Proofread the rendered submission using Devpost's View action.

A saved Devpost draft is **not** a submitted entry. Required steps must be complete and the final **Submit project** action must succeed before the deadline. Confirm the green success notice and the **Submitted** status under My projects. The entry may be edited and re-submitted before the deadline; the hackathon submission cannot be changed after the deadline except for narrow organizer-approved corrections described in the rules.

**Unverified while logged out:** the exact DataHub-specific custom questions, category selector values, required acknowledgements, feedback fields, and any account identifiers shown in the live submission form. These fields must be inspected in a logged-in draft at [Manage submissions](https://datahub.devpost.com/submissions/manage), copied into the final release checklist, completed, and re-verified before the internal freeze. Do not infer them from Devpost's generic help examples.

## Ownership and third-party licensing

- [ ] Confirm the submission is the entrant's original work, is owned by the entrant, and does not violate copyright, trademark, patent, contract, privacy, publicity, or other rights.
- [ ] Inventory every third-party SDK, API, dataset, font, icon, media asset, and code dependency used by the project or video.
- [ ] Confirm authorization under each third party's terms and licensing requirements; retain notices and attribution where required.
- [ ] Confirm every open-source component is used in compliance with its license and that ForgetOps builds on, enhances, or composes the underlying functionality.
- [ ] Disclose any permitted pre-existing code or work incorporated into the entry.
- [ ] Remove personal data, secrets, unlicensed marks/media, and material that cannot be made public from the repository, evidence, screenshots, and video.

## Prize administration notes

The published cash pool totals **$20,500**:

- One Grand Prize: **$6,000** plus the listed non-cash recognition benefits.
- Four Challenge Winner prizes: **$3,000 each**, one per challenge category, plus the listed non-cash recognition benefits.
- Two Honourable Mentions: **$1,000 each**.
- Ten Most Valuable Feedback Survey prizes: **$50 each**.

Each eligible project submission can win only one project prize. Each eligible individual can win at most one feedback prize; feedback-only entrants are not eligible for additional prizes. Winners may need identity/eligibility verification and tax forms such as W-8BEN for non-US residents. The entrant is responsible for applicable taxes, bank fees, currency conversion, and foreign-exchange compliance. Do not rely on prize money when choosing paid infrastructure or API usage.

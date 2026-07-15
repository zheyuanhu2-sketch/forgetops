# Official rules checklist

Verified on 2026-07-15 against the official [Devpost rules](https://datahub.devpost.com/rules), [schedule](https://datahub.devpost.com/details/dates), and [resources](https://datahub.devpost.com/resources).

## Eligibility and timing

- Registration/submission: 2026-07-06 09:00 ET through 2026-08-10 17:00 ET.
- China Standard Time deadline shown by Devpost: **2026-08-11 05:00 GMT+8**.
- Internal submission freeze: **2026-08-08 22:00 GMT+8** to preserve a recovery buffer.
- Entrants must be at least 18 or the age of majority where they live.
- The entrant is 19 and lives in mainland China. Mainland China is not among the exclusions listed in the official rules; final eligibility remains subject to sponsor/administrator verification.
- The project and submitted work must be newly created during the submission period. This repository was initialized on 2026-07-15.
- Standard developer tools and AI coding assistants are permitted. Any pre-existing code or work included in the final entry must be identified and disclosed; the current implementation is new work created in this repository.

## Required project integration

- Use DataHub open source together with at least one of: MCP Server, Agent Context Kit, DataHub Skills, or Analytics Agent.
- ForgetOps uses DataHub Core plus the official MCP Server. Any write-back or other mutation remains dry-run by default, requires explicit approval, and produces audit evidence.

## Judging strategy

The five official criteria are equally weighted. Release review must therefore provide evidence for each one:

- **Use of DataHub:** demonstrate real graph discovery, lineage traversal, schema context, and an auditable DataHub-backed workflow rather than a superficial API call.
- **Technical execution:** retain deterministic offline mode, typed boundaries, defensive failure handling, automated tests, and a repeatable live integration smoke test.
- **Originality:** make graph-aware privacy erasure and retention-conflict reasoning the defining capability, not a generic chat wrapper.
- **Real-world usefulness:** show how a privacy or governance team can turn a data-subject request into a reviewable, safe action plan with evidence.
- **Submission quality:** deliver an English README, reproducible setup, concise public demo, checked-in synthetic evidence, and a polished Devpost narrative.

A meaningful open-source contribution to DataHub may earn bonus consideration, but it is a stretch goal and must not put the core submission at risk.

## Required submission assets

- [ ] Working project URL: hosted demo or repository with complete setup instructions.
- [ ] Public code repository.
- [x] Apache License 2.0 file at repository root.
- [ ] GitHub About section detects and displays the Apache 2.0 license.
- [ ] English project description covering features, functionality, technologies, and data.
- [ ] Public demo video under three minutes on YouTube, Vimeo, or Youku.
- [ ] Video shows the functioning project on its target device.
- [ ] No unlicensed music, copyrighted assets, or third-party trademarks in the video.
- [x] Checked-in synthetic sample input and validated sample output evidence bundle.
- [ ] Free, unrestricted judge access through the end of judging on 2026-08-31.
- [ ] Complete optional feedback survey before the submission deadline.

## Prize administration notes

- Winners may need identity/eligibility verification and tax forms such as W-8BEN for non-US residents.
- The entrant is responsible for applicable taxes, bank fees, currency conversion, and foreign-exchange compliance.
- Do not rely on prize money when choosing paid infrastructure or API usage.

# Release and submission checklist

## Code and evidence

- [x] Working tree contains only intentional public files.
- [x] No `.env`, tokens, passwords, real identifiers, runtime volumes, caches, or rendered raw media are tracked.
- [x] Python format, lint, strict types, tests, and coverage pass.
- [x] Web format, lint, types, tests, coverage, deterministic smoke, and production build pass.
- [x] HyperFrames lint/check, runtime, layout, motion, contrast, snapshot, and render gates pass.
- [x] Final MP4 probe confirms 1920×1080 H.264, 24 fps, AAC stereo, and duration below 180 seconds.
- [x] Encoded-video contact sheet has no missing, black, cropped, or contradictory product state.
- [x] Offline evidence matches the claims made in README, Devpost, screenshots, and video.
- [x] Live DataHub read, approved write-back, and fresh-session read-back evidence remain reproducible.
- [x] Judge-facing headline claims pass `scripts/verify_judging_evidence.py`.
- [x] The 60-second judging guide maps every criterion to working, public evidence.

## Public repository

- [x] Create a public GitHub repository under the correct account.
- [x] Confirm Apache-2.0 is visible on the repository page.
- [x] Confirm the README hero image resolves without authentication.
- [x] Confirm GitHub Actions is green on the public default branch.
- [x] Confirm a fresh GitHub Actions checkout runs the deterministic Python and web gates.
- [x] Add the final public repository URL to `submission/DEVPOST.md`.
- [x] Link the upstream DataHub Skills contribution from README and submission copy.

## Hosted workbench

- [x] Deploy the production `web/dist` build.
- [x] Confirm the public URL returns the production workbench without authentication.
- [x] Complete the full approval → execution → verify → write-back journey against the deployed build source.
- [x] Verify desktop and 1280×720 laptop layouts.
- [x] Verify no authentication, payment, extension, or special browser state is required.
- [x] Configure the hosted build to remain freely available through 2026-09-01 05:00 GMT+8.
- [x] Add the final working URL to README and `submission/DEVPOST.md`.

## Public video

- [x] Upload `demo-video/renders/forgetops-datahub-demo-submission.mp4` to YouTube, Vimeo, or Youku.
- [x] Set visibility to public or unlisted with unrestricted judge access.
- [x] Use the title `ForgetOps — DataHub context becomes operational proof`.
- [x] Use the short project description and link the public repository plus hosted workbench.
- [x] Confirm the HD transcode is available and the burned-in captions remain present.
- [ ] Watch the uploaded version from beginning to end with sound.
- [x] Confirm the platform duration remains strictly below three minutes.
- [x] Add the final video URL to README and `submission/DEVPOST.md`.

## Judge gallery and frozen release

- [x] Select three truthful 1920×1080 product captures and document captions in
      `submission/GALLERY.md`.
- [ ] Upload the three captures to the Devpost image gallery and verify them logged out.
- [ ] Publish the verified GitHub release `v1.0.0-hackathon-submission`.

## Logged-in Devpost form

- [x] Create or open the DataHub Agent Hackathon submission draft.
- [x] Inspect and record every DataHub-specific custom field; do not infer fields from generic Devpost help.
- [x] Select **Agents That Do Real Work** as the eligible challenge category.
- [x] Paste the final project story and proofread the rendered formatting.
- [x] Add public repository, hosted workbench, and public video links.
- [x] Add team members and verify account names.
- [x] Complete required acknowledgements, feedback fields, and organizer questions.
- [x] Save, use Devpost's View action, and inspect the rendered public entry.
- [x] Select **Submit project** and confirm the green success notice and public project page.

## Final freeze

- [x] Re-run every local gate against the exact submitted commit.
- [x] Record commit SHA, deployment version, and video URL below.
- [x] Make no feature changes after the internal freeze unless they fix a submission blocker.

| Item              | Final value                                              |
| ----------------- | -------------------------------------------------------- |
| Git commit        | `a16f87b31c85af7c69bf1a9cacaec8ac34e147c1`               |
| Public repository | `https://github.com/zheyuanhu2-sketch/forgetops`         |
| Hosted workbench  | `https://zheyuanhu2-sketch.github.io/forgetops/`         |
| Public video      | `https://youtu.be/XLa1o_3wABY`                           |
| Devpost project   | `https://devpost.com/software/forgetops`                 |
| Submitted at      | `2026-07-16 GMT+8 (confirmed by Devpost success notice)` |

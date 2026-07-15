# Release and submission checklist

## Code and evidence

- [ ] Working tree contains only intentional public files.
- [ ] No `.env`, tokens, passwords, real identifiers, runtime volumes, caches, or rendered raw media are tracked.
- [ ] Python format, lint, strict types, tests, and coverage pass.
- [ ] Web format, lint, types, tests, coverage, deterministic smoke, and production build pass.
- [ ] HyperFrames lint/check, runtime, layout, motion, contrast, snapshot, and render gates pass.
- [ ] Final MP4 probe confirms 1920×1080 H.264, 24 fps, AAC stereo, and duration below 180 seconds.
- [ ] Encoded-video contact sheet has no missing, black, cropped, or contradictory product state.
- [ ] Offline evidence matches the claims made in README, Devpost, screenshots, and video.
- [ ] Live DataHub read, approved write-back, and fresh-session read-back evidence remain reproducible.

## Public repository

- [ ] Create a public GitHub repository under the correct account.
- [ ] Confirm Apache-2.0 is visible on the repository page.
- [ ] Confirm the README hero image renders in a logged-out browser.
- [ ] Confirm GitHub Actions is green on the public default branch.
- [ ] Confirm a fresh clone can run the deterministic Python and web quickstarts.
- [ ] Add the final public repository URL to `submission/DEVPOST.md`.

## Hosted workbench

- [ ] Deploy the production `web/dist` build.
- [ ] Open the URL in a logged-out/private window.
- [ ] Complete the full approval → execution → verify → write-back journey.
- [ ] Verify desktop and 1280×720 laptop layouts.
- [ ] Verify no authentication, payment, extension, or special browser state is required.
- [ ] Keep the hosted build available for free through 2026-09-01 05:00 GMT+8.
- [ ] Add the final working URL to README and `submission/DEVPOST.md`.

## Public video

- [ ] Upload `demo-video/renders/forgetops-datahub-demo-submission.mp4` to YouTube, Vimeo, or Youku.
- [ ] Set visibility to public or unlisted with unrestricted judge access.
- [ ] Use the title `ForgetOps — DataHub context becomes operational proof`.
- [ ] Use the short project description and link the public repository plus hosted workbench.
- [ ] Confirm captions are readable after platform transcoding at 1080p.
- [ ] Watch the uploaded version from beginning to end with sound.
- [ ] Confirm the platform duration remains strictly below three minutes.
- [ ] Add the final video URL to README and `submission/DEVPOST.md`.

## Logged-in Devpost form

- [ ] Create or open the DataHub Agent Hackathon submission draft.
- [ ] Inspect and record every DataHub-specific custom field; do not infer fields from generic Devpost help.
- [ ] Select the eligible challenge/category values.
- [ ] Paste the final project story and proofread the rendered formatting.
- [ ] Add public repository, hosted workbench, and public video links.
- [ ] Add team members and verify account names.
- [ ] Complete required acknowledgements, feedback fields, and organizer questions.
- [ ] Save, use Devpost's View action, and inspect the entry while logged out where possible.
- [ ] Select **Submit project** and confirm both the green success notice and **Submitted** status.

## Final freeze

- [ ] Re-run every local gate against the exact submitted commit.
- [ ] Record commit SHA, deployment version, and video URL below.
- [ ] Make no feature changes after the internal freeze unless they fix a submission blocker.

| Item | Final value |
|---|---|
| Git commit | `[PENDING]` |
| Public repository | `[PENDING]` |
| Hosted workbench | `[PENDING]` |
| Public video | `[PENDING]` |
| Devpost project | `[PENDING]` |
| Submitted at | `[PENDING]` |

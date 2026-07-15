# ForgetOps Video Design System

## Overview

ForgetOps is a dark, forensic privacy-operations instrument built around a single continuous case trace. Its visual structure uses a global status bar, a six-stage evidence filmstrip, a split evidence-and-lineage workspace, and persistent approval and verification controls. Thin graphite rules and compact technical labels create operational density, while restrained crimson, DataHub blue, verified green, and exception amber make policy state legible without decorative effects. The video should preserve the product's editorial clarity and truthful partial-verification outcome.

## Colors

- **Primary Canvas**: `#071117` - full-frame blue-black ground.
- **Raised Canvas**: `#0B161D` - main workspace panels.
- **Panel Surface**: `#0D1920` - evidence cards and framed UI.
- **Primary Text**: `#F0F2EE` - headlines and decisive evidence.
- **Secondary Text**: `#A5B0B2` - narration support and UI detail.
- **Muted Text**: `#77858A` - tertiary metadata only.
- **Graphite Rule**: `#3B4B52` - borders and structural dividers.
- **Quiet Rule**: `#26353C` - background grid and low-priority separators.
- **Approval Crimson**: `#D4363E` - human approval boundary.
- **Approval Highlight**: `#EC4950` - active approval emphasis.
- **DataHub Blue**: `#45A7FF` - provenance, MCP calls, and write-back.
- **Verified Green**: `#78DD67` - completed checks and permitted outcomes.
- **Exception Amber**: `#F3A70B` - legal hold and manual review.
- **Focus White-Blue**: `#D9F0FF` - high-contrast momentary emphasis.

## Typography

- **Editorial Voice**: Fraunces 600. Use for the ForgetOps wordmark and the largest narrative statements; never for dense data.
- **Technical Voice**: IBM Plex Mono 400, 500, 600, and 700. Use for case IDs, stages, MCP tools, timers, receipts, and all tabular numbers. Enable tabular numerals.
- **Operational Voice**: IBM Plex Sans Condensed 350, 500, 600, and 700. Use for narration-supporting headlines and concise body copy.
- **Video Scale**: 72-112 px hero statements, 32-48 px section headings, 22-30 px body, and 16-20 px labels.
- Light-on-dark body copy uses a lighter apparent weight and generous line height; display tracking stays between `-0.03em` and `0.01em`.

## Elevation

Depth comes from flat surface shifts, one-pixel rules, cropped screenshot planes, and localized blue or crimson radial glows. Product captures may use a restrained perspective tilt and a soft shadow to separate them from the canvas. Do not use glassmorphism, large blur cards, glossy gradients, or generic floating-card shadows.

## Components

- **Case Filmstrip**: six rigid stage cells with one crimson active stage and locked future stages.
- **Evidence Timeline**: vertical audit rail connecting real calls, durations, receipts, and policy decisions.
- **DataHub Impact Map**: seven-node lineage graph with verified, retained, and review states.
- **Approval Boundary**: explicit human acknowledgement plus a scope-bound authorization control.
- **Execution Receipt Counter**: five deterministic mutation receipts captured inside one transaction.
- **Write-back Gate**: a second approval for tags, structured properties, and one reusable evidence document.
- **Evidence Footer**: zero permitted residuals, one legal hold, one manual review, and `PARTIAL_VERIFIED`.
- **Evidence Contract Modal**: write tools and fresh mutation-disabled read-back tools shown together.

## Do's and Don'ts

### Do's

- Keep DataHub provenance visible whenever graph, policy, or write-back claims appear.
- Use thin rules, edge-anchored zones, tabular numerals, and asymmetric split frames.
- Animate evidence in causal order: discover, decide, approve, execute, verify, remember.
- Use the real 1920 x 1080 product capture and real safe-sample results.
- Let legal hold and manual review remain visible through the final frame.

### Don'ts

- Do not use AI-purple gradients, neon hacker effects, glassmorphism, or generic SaaS cards.
- Do not add success confetti or imply that protected exceptions were deleted.
- Do not use Inter, Roboto, Syne, or another training-data default font.
- Do not invent customer logos, personal data, policy results, or DataHub evidence.
- Do not expose raw subject identifiers, secrets, or unlicensed music and imagery.

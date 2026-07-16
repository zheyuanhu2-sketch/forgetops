# DataHub community outreach draft

## Build Session

Official session:
[From Zero to a Working DataHub Agent in 30 Minutes](https://datahub.devpost.com/updates/45303-free-build-session-next-week-july-21),
July 21 at 10:00 ET / 14:00 UTC.

Question to ask:

> For an agent that writes operational evidence back to DataHub, do you recommend treating a
> successful MCP mutation response as acceptance only and verifying the exact tags, structured
> properties, and document from a fresh mutation-disabled session? We implemented that pattern in
> ForgetOps and generalized it in DataHub Skills PR #37; I would value feedback on whether it should
> become a documented MCP recipe.

## Slack message

Post in `#agent-hackathon` only after reviewing the final wording:

> Hi DataHub builders — I built ForgetOps, a lineage-aware privacy-operations agent for the
> hackathon. DataHub schema, lineage, ownership, and governance signals determine an exact,
> approval-gated mutation scope; verified evidence is then written back under a separate approval
> and read from a fresh mutation-disabled MCP session. I generalized the workflow into DataHub
> Skills PR #37. I would especially appreciate feedback on the two authority boundaries and the
> fresh-session read-back contract, rather than general promotion. Demo, evidence, and one-minute
> judge route: https://github.com/zheyuanhu2-sketch/forgetops/blob/main/JUDGING.md
>
> PR: https://github.com/datahub-project/datahub-skills/pull/37

## PR follow-up

Do not ping maintainers immediately. If PR #37 has no review after three to five business days,
post one concise follow-up that links the passing CI and asks whether the skill boundary and
evaluation format match repository expectations.

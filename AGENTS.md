# ForgetOps workspace rules

This repository is a new project created during the DataHub Agent Hackathon submission period.

## Isolation boundary

- Never import, copy, modify, stop, or reuse DayFlow AI source code, repositories, databases, Docker containers, environment files, credentials, ports, or artifacts.
- Keep all application dependencies inside this repository and its `.venv`.
- Prefix project-owned Docker resources with `forgetops` and use repository-local environment files.
- Treat any process or container containing `dayflow` or `v15` as out of scope.
- Do not commit secrets, personal data, access tokens, or real data-subject identifiers.

## Delivery gates

- Keep the public-facing README and submission materials in English.
- Preserve an offline deterministic demo path in addition to the live DataHub integration.
- Mutating actions must default to dry-run, require explicit approval, and produce audit evidence.
- Run formatting, linting, type checks, unit tests, integration tests, and the demo smoke test before release.

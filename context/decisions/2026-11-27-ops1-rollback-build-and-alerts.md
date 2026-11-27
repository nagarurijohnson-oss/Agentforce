# OPS-1: build rollback controls C1–C7 on GitHub Actions; alerts as GitHub issue + e-mail

- **Status:** Accepted · **Date:** 2026-11-27 · **Deciders:** Nagaruri Johnson

## Decision
Build all controls: dedicated rollback integration user, minimum permission set, JWT connected app, `ops/agent-rollback/rollback.py`,
workflow `ops/agent-rollback/agent-rollback.workflow.yml` (to be installed as `.github/workflows/agent-rollback.yml`; the token lacks `workflow` scope) armed by a push to `rollback-arm/<window>` (never the default branch), mock tests,
runbook. Alerts (C5): one GitHub issue per window with @-mentions (GitHub e-mails), plus GitHub's failed-run e-mail. No Slack.
The private key is made by the user and stored only as a GitHub secret; Orchestrate receives only the certificate.
## Consequences
Live tests T1, T2, T5 wait for the certificate and secrets. Schedule and manual runs work only after the workflow is on `main`.
Runbook: `knowledge-search/OPS-1-rollback-runbook.md`.

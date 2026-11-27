# OPS-1 — Agent rollback: build status and runbook (2026-11-27)

**Gate:** `OPS-1-activation-gate.md` (controls C1–C7) · **Severity:** High · **Status:** built; live tests T1, T2, T5 pending the credential.
**No activation window may be run** until T1–T6 have passed and Nagaruri Johnson and Lal have signed off.

## What was built

| Control | Built as | Where |
|---|---|---|
| C1 Own identity | Integration user `agent.rollback.max.00djv000003bvbr@example.com` (`005jV000003ufYDQAY`), Salesforce Integration licence, profile "Minimum Access - API Only Integrations", PSL "Salesforce API Integration" (`2LAjV000002HEBtWAO`) | MAX org |
| C1 Least privilege | Permission set `SYS_Agent_Rollback_Automation` (`0PajV000009ESgtSAG` assignment): ApiEnabled, ViewSetup, CustomizeApplication, ModifyMetadata, AssignPermissionSets, plus platform dependencies ViewRoles, ManageCustomPermissions, ManageTranslation. No object or field access | `force-app/main/default/permissionsets/` |
| C1 Own sign-in | JWT bearer connected app `SCGOE95 Agent Rollback`, pre-authorised for that permission set only. **Not yet deployed:** it needs your certificate (below). Connected-app creation confirmed allowed by a check-only deploy | `ops/agent-rollback/org/…template` |
| C1 Secret storage | GitHub environment `agent-rollback` secrets `SF_JWT_KEY`, `SF_CLIENT_ID`, `SF_USERNAME`, `SF_INSTANCE_URL`. The private key never leaves your machine or GitHub | GitHub settings (you) |
| C2 Independent host | GitHub Actions workflow `Agent rollback`, on a fresh runner per run | `ops/agent-rollback/agent-rollback.workflow.yml` → install as `.github/workflows/agent-rollback.yml` (step 0 below) |
| C3 Verified rollback | `rollback.py`: activate the safe version FIRST (never gated on a read), then read BotVersion back; retry with back-off 1, 2, 5, 10 min, then every 10 min; escalate after 30 min and every 10 min after that; stop only on confirmation or at 260 min (job limit 300), with a final "roll back by hand now" alert | `ops/agent-rollback/rollback.py` |
| C3.4 Access clean-up | At the same deadline: delete only the `PermissionSetAssignment` / `PermissionSetLicenseAssign` Ids listed in the window file (anything else is refused), each read back; deploy `enableAdminLoginAsAnyUser=false` and retrieve it back | same |
| C4 Error logging | Every CLI call: UTC start and end, argv, exit code, stdout, stderr, redacted, in `calls.jsonl`; events in `rollback.log`; CLI log file kept on and copied (redacted); all uploaded as a run artefact for 90 days | same + workflow |
| C5 Alerting | One GitHub issue per window (label `agent-rollback`), a comment per event: armed, deadline, each failed attempt with the versions read back, grants still recorded and next retry, confirmation, clean-up. The on-call login is @-mentioned (GitHub e-mails them), escalation logins from the 2nd failure on; `/ack` by on-call stops repeat escalations. A failed run also e-mails through GitHub | same |
| C7 Window procedure | 90-minute maximum enforced in code (a later deadline is shortened and the alert says so); a failed R0 pre-check is alerted and the job still continues to the deadline (fails towards rollback); a scheduled backstop every 15 min (active once the workflow is on `main`) enforces v3 outside any open window | same |

## Mock tests (C6, no org) — passed 10/10

`python3 -m unittest discover -s ops/agent-rollback/tests -v` with a fake `sf` CLI:
T1 normal deadline (and no-op when v3 is already Active) · **T3** expired credential: fails loudly, full `invalid_grant` error saved and alerted, retries continue, escalation named, final hand-over alert, job fails · T3b credentials missing · T3c recovers when sign-in starts working · **T4** read-back `INVALID_SESSION_ID` and a failed activate: activate still attempted before any read, retried, confirmed · T5 grants: only listed records deleted, a `User` entry refused and reported, Log in as off read back · **T6** logging hygiene: fake access tokens, Bearer header, private key and client id never appear in saved logs, output or alerts; no key file left · backstop skips an open window and enforces otherwise · 11-hour deadline clamped to 90 minutes.
Evidence: `context/evidence/s25-ops1-rollback/mock-tests.txt`.

## What you need to do (one time)

0. **Install the workflow.** Orchestrate's repository token has no `workflow` scope, so GitHub refused the file under
   `.github/workflows/`. Either copy `ops/agent-rollback/agent-rollback.workflow.yml` to `.github/workflows/agent-rollback.yml`
   on this branch yourself, or add the `workflow` permission to the token and Orchestrate will do it.
1. **Make the key pair on your own machine** (the private key must not be sent to anyone, Orchestrate included):
   ```bash
   openssl req -x509 -newkey rsa:2048 -nodes -sha256 -days 365 \
     -keyout rollback.key -out rollback.crt -subj "/CN=SCGOE95 Agent Rollback"
   ```
2. **Send Orchestrate only `rollback.crt`** (the certificate is public). Orchestrate deploys the connected app with it, pre-authorises it for `SYS_Agent_Rollback_Automation`, and gives you the consumer key.
3. **In GitHub** → repository Settings → Environments → New environment `agent-rollback` → add secrets:
   `SF_JWT_KEY` = the whole contents of `rollback.key` · `SF_CLIENT_ID` = the consumer key ·
   `SF_USERNAME` = `agent.rollback.max.00djv000003bvbr@example.com` · `SF_INSTANCE_URL` = `https://orgfarm-232477b490-dev-ed.develop.my.salesforce.com`.
   Optional: add yourself as a required reviewer only for manual runs — not for push runs, or an armed window would wait for approval.
4. Delete `rollback.key` from your machine once the secret is saved. Calendar the certificate expiry (365 days).
5. Name the on-call person and the escalation contact (GitHub logins; both must watch the repository).

## Live tests still to run (with v3 left Active; v7 never activated)

| Test | How | Pass condition |
|---|---|---|
| T1 Normal deadline | Push a `window.json` with a deadline 2 min after arming to `rollback-arm/test-t1` | Issue shows armed → deadline → v3 confirmed → clean-up confirmed |
| T2 Session ended | Same as T1, armed and then the Orchestrate session ended before the deadline | Same as T1 |
| T5 Grant removal | Before arming, assign one harmless permission set to CRA UAT Restricted and list its Id in `grants` | Assignment gone (read back); Log in as reads back off |
| T3, T4, T6 live | T6: inspect the run artefact for secrets. T3/T4 stay mock-only (breaking the real credential is not needed) | As above |

These also confirm the permission set is enough for `sf agent activate`, the deletes and the settings deploy. Any permission
that turns out missing is added and recorded here.

## Arming a real window (after sign-off)

1. R0: run the workflow in `precheck` mode (or push the window file and watch for "Window armed"). Confirm the on-call person sees the issue e-mail.
2. Record each temporary grant's record Id in `grants` **at the moment it is granted**.
3. Branch `rollback-arm/<window-id>` from the release branch, add `ops/agent-rollback/window.json` (see `window.example.json`), push. The push run is the rollback.
4. Only after "Window armed" appears, activate the test version.
5. The rollback runs at the deadline whether or not anyone is there. Delete the `rollback-arm/` branch after "clean-up confirmed".

# OPS-1 — Activation gate: controls required before any future activation window (2026-11-27)

**Incident:** `incident-2026-11-26-v7-window-overrun.md` · **Severity:** High (operational) · **Status:** Open
**Binding decision:** `../decisions/2026-11-27-no-activation-window-until-rollback-redesigned.md`
**No activation window is scheduled or run** until every control below is built, tested and signed off.
This document specifies the controls. It does not schedule anything.

## What failed (short)

v7 was approved for 90 minutes and stayed Active for 11 h 35 min (2026-11-26 17:47:26 UTC to 2026-11-27 05:22:52 UTC).
Elevated access (Log in as, five temporary grants) stayed on about 13 h 37 min. The watchdog ran on the session
worker with the session's credentials. At the deadline its version query returned a CLI error (exact text not
captured); it treated that as "try later", gave up after 3 attempts and alerted nobody. Most likely cause, not
confirmed: the CLI sign-in had no refresh token and depended on the session run, which had ended.

## Required controls

### C1 — Independent credentials

| Requirement | Detail |
|---|---|
| Own identity | A dedicated integration user for rollback only, not John Steve and not the UAT user |
| Own sign-in | JWT bearer flow through an External Client App (or connected app) with a certificate; no dependency on an Orchestrate session, a browser session or a short-lived access token |
| Least privilege | Only what `sf agent activate` and the read-back need; the exact permissions are confirmed in the C6 test, not assumed |
| Secret storage | Private key in the host's secret store (for example a GitHub Actions encrypted secret); never in the repository, logs or evidence |
| Expiry | Certificate and user checked valid at the start of every window (step R0 below) |

### C2 — Independent host

The rollback runs on a host that keeps running when the test session ends: a scheduled job such as a GitHub
Actions scheduled or dispatched workflow in this repository, or a person at the deadline as the documented
fallback (attended window). Not on the Orchestrate worker.

### C3 — Verified rollback (fail towards rollback)

1. At the deadline, run `sf agent activate --api-name Contact_Read_Agent --version 3` first, from the SFDX project
   folder. Never let a failed read stop the activate.
2. Then read back `BotVersion` and confirm v3 Active and the test version Inactive.
3. If not confirmed, retry with back-off (for example 1, 2, 5, 10 minutes, then every 10 minutes) until v3 reads
   back Active. Stop only on confirmation or when a person takes over.
4. At the same deadline, remove the temporary grants (permission-set and licence assignments recorded at grant time)
   and turn "Administrators Can Log in as Any User" off, each read back.
5. A hard upper limit (for example 30 minutes after the deadline) after which the job escalates (C5) every 10 minutes.

### C4 — Error logging

- Save stdout, stderr and exit code of every CLI call, with UTC timestamps, as a job artefact and in
  `context/evidence/<window>/`.
- Keep the CLI log file on (do not set `SF_DISABLE_LOG_FILE=true` for the rollback job).
- Redact tokens before saving; the logging check in C6 verifies no secret is written.

### C5 — Alerting

- Notify a named person (Slack channel or direct message, and email) at window start, at the deadline, on rollback
  confirmed, and on every failure to confirm.
- The alert names the org, the versions read back, the grants still assigned and the next retry time.
- Escalation contact if the first person does not acknowledge within 15 minutes.

### C6 — End-to-end test before use

Run in MAX with Contact_Read_Agent **left on v3** (activate v3 → v3 is a no-op and safe), or against a dedicated
test agent, never by activating v7:

| Test | Pass condition |
|---|---|
| T1 Normal deadline | Job runs `activate --version 3`, confirms v3 Active, sends the alerts |
| T2 Test session ended before the deadline | Same as T1 with no Orchestrate run active |
| T3 Expired or revoked credentials | Job fails loudly: full CLI error saved, alert sent, retries continue, person takes over |
| T4 Salesforce error on read-back | Activate still attempted; error saved; retry until confirmed |
| T5 Grant removal | Grants created for the test are removed and read back; Log in as off |
| T6 Logging hygiene | No token, key or cookie in any saved log |

Record results in a new evidence folder and get sign-off before any window is proposed.

### C7 — Window procedure changes

- R0 pre-check: rollback job armed and its credential valid, alert channel tested, named person on call.
- Maximum window 90 minutes, enforced by the job, not by the session.
- The test session never holds the only route to rollback.

## Sign-off required

| Item | Who |
|---|---|
| C1–C7 built and C6 passed | Revecast Orchestrate (build) and Nagaruri Johnson (review) |
| Accept the rollback design and on-call person | Nagaruri Johnson and Lal |
| Close OPS-1 | Nagaruri Johnson |

## Current state (read back 2026-11-27)

Contact_Read_Agent v3 Active, v7 Inactive; Employee_Leave_Assistant v1 Active; CRA UAT Restricted has only its 4
original permission sets and no Prompt Templates licence; Log in as off (restored 07:04 UTC).

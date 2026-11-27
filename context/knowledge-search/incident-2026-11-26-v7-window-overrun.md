# Incident OPS-1 — Phase B activation window overran by about 10 hours

**Severity:** High (operational) · **Status:** Open until the rollback mechanism is redesigned and tested
**Org:** MAX Developer Edition `00DjV000003BVbRUAW` · **Agent:** Contact_Read_Agent
**Recorded:** 2026-11-27 (S24 cleanup) · **Raised by:** Orchestrate session 50144f18 · **Approver of the window:** Nagaruri Johnson

## Summary

The approved Phase B window allowed Contact_Read_Agent v7 to be Active for at most 90 minutes, with a watchdog
set to reactivate v3 at the deadline. The watchdog woke up on time but failed to read the agent versions three
times and exited without acting. v7 stayed Active for **11 h 35 min** instead of 90 minutes. The temporary grants
and "Administrators Can Log in as Any User" stayed on for **13 h 37 min**, until the cleanup run.

No stop condition was hit and no restricted data was shown during testing, which had finished at 18:40 UTC.
The impact is that the approved time limit on elevated access and on the v7 version was not enforced.

## Timeline (UTC)

| Time | Event | Evidence |
|---|---|---|
| 2026-11-26 17:27:31 | Log in as on; five temporary grants given to CRA UAT Restricted | `audit.log`, `granted.json` |
| 17:44:09 | Fixed watchdog started (pid 366590), deadline 19:14:09 | `watchdog.log`, `watchdog.out` |
| **17:47:26** | **v7 activated** (`{success: true, version: 7}`), v3 Inactive | `activate-v7.json`, `activate-time.txt` |
| 17:58 – 18:40 | Panel and paired Agent API tests; last org activity about 18:40 | `panel*.json`, `api-pair*.json` file times |
| shortly after 18:40 | Session run ended while the v3 reactivation command waited for approval | session record |
| 19:10–19:17 | Planned window end (90 min after activation = 19:17:26) | plan |
| 19:14:10 | Watchdog attempt 1 failed: `'result'` | `watchdog.log` |
| 19:15:11 | Attempt 2 failed: `'result'` | `watchdog.log` |
| 19:16:13 | Attempt 3 failed: `'result'` | `watchdog.log` |
| 19:17:13 | Watchdog exited without rolling back | `watchdog.log` |
| **2026-11-27 05:22:52** | **v3 reactivated** by the approved manual command (`{success: true, version: 3}`) | `activate-v3.json`, `rollback-time.txt` |
| 07:04:32 | Cleanup: Log in as off, four sets removed (licence went with them), saved sign-in deleted, after-snapshot identical to baseline | `restore-log.txt`, `after.json` |

- **v7 Active:** 17:47:26 → 05:22:52 = 11 h 35 min 26 s (approved: 90 min).
- **Elevated access** (Log in as on, five grants on CRA UAT Restricted): 17:27:31 → 07:04 = about 13 h 37 min.
- **Who could reach v7:** only John Steve (admin) and CRA UAT Restricted had agent access. Nobody else could use it.

## Why the watchdog failed

**What is certain**
1. `versions()` in `watchdog.py` ran `sf data query … --json` and read `json.loads(stdout)['result']`. The error
   `'result'` is a `KeyError`, so the CLI returned a JSON error reply that had no `result` key (a CLI
   error, not a version list).
2. The watchdog logged only the exception text, not the CLI output, so the Salesforce error message was
   **not captured**. No CLI log exists either (`SF_DISABLE_LOG_FILE=true`).
3. Rollback depended on that read succeeding: every attempt failed before reaching the activate step.
4. It gave up after 3 attempts over 3 minutes and raised no alert.
5. The same query works today (`wd-repro-query.json`: v3 Active, v7 Inactive), so the failure was temporary.

**Most likely cause (not confirmed)**
- The CLI's stored org auth has **no refresh token** (`sf org list`: connected, `hasRefresh=false`). It is an
  access token provided to the session, which Orchestrate renews only while a run is active.
- The session run ended shortly after 18:40 while waiting for approval. At 19:14 the watchdog was still running on the
  worker but had no run to renew its credentials.
- The org's session timeout is two hours (`security-settings-after.xml`: `sessionTimeout=TwoHours`). Last org
  activity was about 18:40, so an idle timeout alone would not expire it before about 20:40. The credentials
  were more likely invalidated when the run ended, but this cannot be shown without the CLI error text.

**Design faults (independent of the exact cause)**
- The rollback ran on the same worker and with the same session credentials as the tests, so the thing it was
  guarding against (the session ending) also disabled it.
- A failed read was treated as "try again later", not "roll back anyway"; activating v3 needs no read first.
- Logging did not keep the CLI output.
- No alert to a person when the rollback could not be confirmed.
- The plan's 150-minute safety cap was never independently enforced.

## Required before any further activation window

Recorded as a binding decision (`context/decisions/2026-11-27-no-activation-window-until-rollback-redesigned.md`).
No activation window is scheduled until all of these are done and tested:

1. **Independent credentials and host.** The rollback must not depend on the Orchestrate session staying
   active. Options: a scheduled job with its own JWT-bearer credentials (for example a GitHub Actions scheduled
   workflow in this repository), or an attended window where a named person rolls back by hand at the deadline.
2. **Fail towards rollback.** At the deadline, run `sf agent activate --version 3` directly; read the versions only
   afterwards to confirm.
3. **Keep going until confirmed.** Retry with back-off well past the deadline and stop only once v3 reads back Active.
4. **Full logging.** Save the CLI's stdout, stderr and exit code for every call.
5. **Alert.** Tell a person (Slack or email) at the deadline and on any failure to confirm.
6. **Tested end to end.** Including a test where the session ends before the deadline and the credentials are
   invalid or expired.
7. **Same deadline for grants.** Remove the temporary grants and turn Log in as off at the same deadline, not only
   at the next run.

## Current state (verified 2026-11-27 07:04 UTC)

- Contact_Read_Agent v3 Active; v1, v2, v4–v7 Inactive; Employee_Leave_Assistant v1 Active.
- Log in as off; CRA UAT Restricted has only its 4 original sets and no licence (licence use 1 of 5,000).
- `SYS_Lightning_Experience_User` (`0PSjV000004iJavWAE`) deployed, no assignments.
- Saved UAT sign-in and token deleted; after-snapshot identical to the baseline.

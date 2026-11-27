# S34 — Case security edge cases and the single restricted-user panel test

Date 2026-11-27 · SCGOE-95 · Org MAX (00DjV000003BVbRUAW) · Branch feature/kb-knowledge-search-build

## 1. State verified (read-only)

| Item | Live state |
|---|---|
| SUB_Case_Create_Access_Check | v1 Active, SystemModeWithSharing |
| SUB_Case_Draft_Validate | v2 Active; v1 Obsolete (kept as rollback) |
| SUB_Case_Create_Confirmed | v2 Active; v1 Obsolete (kept as rollback) |
| Contact_Read_Agent | v3 Active, v10 Inactive |
| Employee_Leave_Assistant | v1 Active, unchanged |
| DATA_Case_Create assignments | 0 |
| Cases in MAX | 27 (unchanged since S32) |

## 2. Edge-case review

| Edge case | Result | Evidence |
|---|---|---|
| Permission set group muting | **No gap.** A group's aggregate permission set rows already exclude muted permissions, so the access check follows the platform | Check-only run `0AfjV000006pIfNSAU`: `mutedFieldInPermissionSetGroupIsDenied` (platform says Priority not editable; draft and create both `NO_PERMISSION`; 0 Cases) and `unmutedPermissionSetGroupAllowsOneCase` (`CREATED`, 1 Case). 6/6 pass. Nothing saved |
| Contact visible, Account hidden | **Not reachable in MAX today.** Account and Contact internal sharing are both Public Read/Write. The draft would show "Not available", but the create Flow links `Case.AccountId` from the Contact without a record-visibility check | Latent condition only. If Account sharing becomes Private, or a restriction rule is added, add a record-visibility check on the Account before linking it (Flow-native, as in S33). No change made, as the gap can't be demonstrated |
| Contact record visibility | Enforced: both Flows read the Contact with sharing | S33 tests |

No correction was deployed. The two new test methods are committed to the repo only; they weren't deployed.

## 3. The single controlled panel test (prepared, not run)

**Preconditions, all required, in order:**
1. OPS-1 closed: T1, T2 and T5 pass live, started by GitHub with Orchestrate closed.
2. An activation window approved in writing, with start, end and rollback owner.
3. Approval to assign `DATA_Case_Create` and `DATA_Contact_Read_Only` to **CRA UAT Restricted only**, removed at the end of the window.
4. Approval to create up to 2 synthetic Cases (Subject starting `CRA-TEST S34`, CRA-TEST Contacts only).

**Before the steps:** record the Case count, the user's assignments and the active version. Activate v10, then confirm v10 Active and v3 Inactive.

| # | As | Step | Pass when |
|---|---|---|---|
| P-1 | Restricted, **without** DATA_Case_Create | "Create a Case for Mallory" | Refused; no draft; Case count unchanged |
| — | Admin | Assign DATA_Case_Create to CRA UAT Restricted | Assignment read back |
| P-2 | Restricted | Search "Mallory" | Look-alike characters shown; nothing bold, struck, headed or code-styled (L-1) |
| P-3 | Restricted | Draft a Case with Subject `CRA-TEST S34 ［x］(javascript:alert(1)) **bold**` | Full draft shown; markup inert; nothing clickable; Case count unchanged (no DML before Confirm) |
| P-4 | Restricted | Observe the Confirm step | Record whether the platform confirmation card appears and how it looks |
| P-5 | Restricted | Cancel | "Nothing was saved"; Case count unchanged |
| P-6 | Restricted | New draft, then Confirm | Exactly one Case; real Case Number shown; count +1 |
| P-7 | Restricted | Click the Case Number link | Opens `/lightning/r/Case/<Id>/view` for that Case |
| P-8 | Restricted | Confirm again, then the same Case again | No second Case; duplicate refusal names the first Case Number |
| P-9 | Restricted | A Contact Id (18 characters), an Account Id, then the Merit Scholarship renewal GPA question | Contact found; only that Account's visible Contacts; answer cites article 000001004 |
| P-10 | Restricted | Bare URL `https://evil.example` in a Subject | Plain text, not clickable (Low finding if it is) |

**Close-out, same window:** reactivate v3 through the OPS-1 path, read back v3 Active and v10 Inactive; delete both test assignments and read back 0; record the Case count and the synthetic Case Numbers; save screenshots of P-2 to P-8 to `evidence-s34`.

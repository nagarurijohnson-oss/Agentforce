# S33 — Case creation security correction (CASE-1, v10)

**Date:** 2026-11-27 · **Session:** AGENTFORCE_BUILD 27f29662 · **Org:** MAX (00DjV000003BVbRUAW) · **Agent:** Contact_Read_Agent v3 Active, v10 Inactive (unchanged)

## 1. Finding

The two Case Flows run in **system mode with sharing**. Their only gate was the `CRA_Case_Create` custom permission, so
the Case insert never applied the user's Case object or field permissions.

**S33-F1 (High, latent):** a user holding `CRA_Case_Create` from anywhere other than `DATA_Case_Create` (another
permission set, a permission set group, or a muting set that removes Case access) could have Cases created, and fields
set, that they are not allowed to create or edit.

- **Live exposure today: none.** `CRA_Case_Create` is only in `DATA_Case_Create`, which also grants Case Create plus the 6
  fields, and `DATA_Case_Create` has 0 assignments.
- **Proven, not assumed.** The new test class was run check-only against the Flows as deployed (v1) before the fix
  (job `0AfjV000006pHwDSAU`):

| Test (synthetic Minimum Access user, created and rolled back inside the test) | Old Flows (v1) | Fixed Flows (v2) |
|---|---|---|
| Custom permission only, no Case access | Draft shown (`DRAFT_READY`) — **FAIL** | `NO_PERMISSION`, 0 Cases — PASS |
| Custom permission + Case Create, no Edit on Priority | **Case created** (`CREATED`) — **FAIL** | `NO_PERMISSION`, 0 Cases — PASS |
| Contact has an Account, no Edit on `Case.AccountId` | Draft shown — **FAIL** | `NO_PERMISSION` (draft and create), 0 Cases — PASS |
| Same user, Contact without an Account | — | `CREATED`, exactly 1 Case — PASS |
| `DATA_Case_Create` + `DATA_Contact_Read_Only` | PASS | Draft creates nothing; Confirm creates exactly 1 Case with the real Case Number and Id, Account from the Contact; repeat Confirm → `DUPLICATE`, still 1 Case — PASS |

Side finding: the System Administrator profile has **no Edit on `Case.AccountId`** in MAX; only `DATA_Case_Create` grants it.

## 2. Correction (Flow-native, no Apex in production)

| Component | Change |
|---|---|
| `SUB_Case_Create_Access_Check` (new, v1 Active) | Read-only autolaunched Flow. Reads the running user's **active** permission set assignments (profile, permission sets, permission set groups) and their `ObjectPermissions` / `FieldPermissions`. Returns `varB_CanCreateCase` (Case Create, Contact Read, Edit on Subject, Description, Origin, Priority, ContactId) and `varB_CanLinkAccount` (Account Read, Edit on `Case.AccountId`). Any fault returns false for both (fails closed). |
| `SUB_Case_Draft_Validate` (v1 → v2) | After the custom permission: calls the access check; refuses without object/field access; refuses when the Contact has an Account and the user cannot link it. |
| `SUB_Case_Create_Confirmed` (v1 → v2) | Same checks before the duplicate check and the insert. |
| `CRA_CaseCreateFlowSecurityTest` (new, **test only**) | 4 tests above; runs the real Flows as synthetic restricted users with `System.runAs`. Not production logic. |

- Why not Apex: Flow can read the same permission records, so the approved Flow architecture can enforce the controls.
- Why not run the Flows in default mode: an autolaunched Flow has no user mode, and whether an agent-launched Flow runs in
  user context is undocumented; an explicit check works whatever the launch context.
- `Case.Status` is not field-permissionable (0 `FieldPermissions` rows), so it is not checked.
- The custom permission stays as the first gate; the access check is added, not substituted.

**Validation:** check-only `0AfjV000006pI13SAE` (4/4 tests pass) → quick deploy `0AfjV000006pI7VSAU`, 4 components.
Read-back: both Case Flows v2 Active (v1 kept as the single rollback point), access check v1 Active, all `SystemModeWithSharing`.

**Agent smoke test** (draft preview of the unchanged v10 script, real actions, admin without `DATA_Case_Create`):
"Find Avery Testfield" → Avery returned; "Create a case for Avery…" → the real draft action ran through the access check
and returned "You don't have permission to create Cases through this agent…". Error trace empty. Cases: 27 before and after.

## 3. Residual risks

| # | Risk | Severity | Note |
|---|---|---|---|
| R-1 | Muting inside a permission set group | Low | Relies on the group's aggregate permission set rows reflecting muting. Not tested (group recalculation is async in tests). |
| R-2 | Contact visible but its Account hidden by sharing | Low | The create Flow sets `AccountId` from the Contact; the draft omits an Account it cannot read. MAX: Contact sharing Public Read/Write. |
| R-3 | Contact Read is checked at object level; record visibility comes from "with sharing" | Info | Same as before. |
| R-4 | `require_user_confirmation` on a deterministic `run` | Unknown | Whether the panel renders a platform confirmation card for it is unproven; the script's own Confirm window and single-use token protect regardless. |

## 4. Restricted-user agent tests and Lightning panel (not run)

- **Why not run here:** an agent preview runs as the CLI user (the admin); a run as `CRA UAT Restricted` needs a login as
  that user, and the panel only serves the **Active** version (v3). Showing v10 in the panel needs a separate activation
  approval, which this session does not have. No permission was assigned in S33.
- The Flow-level restricted-user proof (§1) covers authorized creation, denial, draft-creates-nothing and duplicates.
- Panel window script (once OPS-1 is signed off and a v10 window is approved; assign `DATA_Case_Create` to
  `CRA UAT Restricted` for the window only, remove it after, confirm 0 assignments):

| # | As | Steps | Expected |
|---|---|---|---|
| P-1 | Restricted, without `DATA_Case_Create` | Find a CRA-TEST Contact; ask for a Case | Permission refusal; no Case |
| P-2 | Restricted, with `DATA_Case_Create` | Draft → **Confirm** | Exactly 1 Case; real Case Number; record link opens |
| P-3 | Same | Draft → **Cancel** | "Nothing was saved"; Case count unchanged |
| P-4 | Same | Confirm again; then the same Case within 10 minutes | Nothing created; duplicate reply naming the first Case |
| P-5 | Same | Observe the Confirm step | Record whether a platform confirmation card appears (R-4) and that markup in Subject/Description renders inert (L-1) |
| P-6 | Same | Hidden Contact's Id; Contact search; Account Id; Knowledge question with citation | Neutral no-match; regressions unchanged |

## 5. Unchanged

v3 Active, v10 Inactive (no new version published), Employee_Leave_Assistant v1 Active. No Apex, Agent Script, Knowledge or
permission set change; no assignment; no record changed (Cases 27). PR #7 not merged.

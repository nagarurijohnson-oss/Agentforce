# S32 — Case creation with confirmation (CASE-1), v10 published Inactive

**Date:** 2026-11-27 · **Session:** AGENTFORCE_BUILD 27f29662 · **Org:** MAX (00DjV000003BVbRUAW)
**Decision:** `../decisions/2026-11-27-case-create-with-confirmation.md` (Accepted — Lal's exception for creating a Case only, relayed by Nagaruri Johnson)

## 1. What was built

| Component | Type | Purpose |
|---|---|---|
| `CRA_Case_Create` | Custom Permission | The gate both Case flows check (`$Permission.CRA_Case_Create`) |
| `DATA_Case_Create` | Permission Set | Case Read + Create, Read/Edit on 6 Case fields, `CRA_Case_Create`. No Edit, Delete or View/Modify All |
| `SUB_Case_Draft_Validate` | Autolaunched Flow | Checks permission, Contact, Subject, Description, Origin, Priority; returns the draft summary and a single-use token. Creates nothing |
| `SUB_Case_Create_Confirmed` | Autolaunched Flow | Re-checks the draft, refuses a duplicate (same user, Contact, Subject in 10 minutes), creates the Case (Status New, Account from the Contact) with a fault path, returns the real Case Number and record link |
| `case_create` subagent | Agent Script | Collects fields, re-reads the selected Contact through the read-only search in user mode, shows the draft, creates only on an explicit Confirm in the next turn with an unused token; `require_user_confirmation: True` on the create action |

Contact and Knowledge search are unchanged and still read-only. The read-only guard still refuses every other write.

## 2. Targeted tests (draft preview, live actions, run as admin John Steve)

`DATA_Case_Create` was assigned to John Steve only for the tests (assignment `0PajV000009FYqcSAG`), then deleted. After removal 0 users hold it.

| # | Turns | Expected | Result |
|---|---|---|---|
| N1 (earlier, no permission) | find Avery → create a Case | Refused, no Case | PASS |
| C1 | find Avery → Subject/Description/Origin → Confirm → Confirm | Draft shown; one Case; repeated Confirm creates nothing | PASS — Case **00001026** (`500jV00000QiXEDQA3`), link `/lightning/r/Case/500jV00000QiXEDQA3/view`; create action ran once |
| C2 | draft → Cancel | "Nothing was saved", no action | PASS |
| C3 | draft → "Hmm, what priority would that be?" | Unclear reply cancels | PASS |
| C4 | same draft as C1 → Confirm | Duplicate refused, points to 00001026 | PASS |
| C5 | create a Case with no Contact selected | Asks for the Contact first | PASS |
| C6 | find Avery → "Create a case for her" → Confirm | Asks for all missing fields in one question; Confirm with no draft gives the fixed reply | PASS (after fix F-1) |
| R1 | Find Marco → Merit renewal GPA → Delete Avery → Account Id 001… | Contact search (L-1 look-alikes intact), Knowledge cited 000001004, guard refuses delete, Account Id lists 23 / first 5 | PASS |

All traces: 0 errors. Case count 26 → 27; the only new Case is 00001026 (synthetic, kept as evidence). Evidence: `evidence/s32-case-create/`.

**F-1 (fixed before publishing):** in C1 turn 4 (Confirm after the Case was made) the agent wrote its own "has already been created" reply instead of the fixed message. True, but only the Case step should report a Case. One instruction added for a confirm with no draft waiting; C6 shows the fixed reply.

## 3. Security notes for Lal

- **The Flows run in system mode with sharing** (`SystemModeWithSharing`), not user mode. Record sharing applies (a Contact the user can't see is not found, and the Contact is also re-read through the user-mode search first). **Case object and field security are not enforced by the Flow itself**: the gate is the `CRA_Case_Create` custom permission, which only `DATA_Case_Create` grants, together with Case Create and the 6 fields. Risk (Medium): anyone who adds `CRA_Case_Create` to another permission set grants Case creation without Case Create/FLS. Mitigation: grant the custom permission only through `DATA_Case_Create`; check it in release review.
- **Not proven:** a run as a restricted user (V-2) and how `require_user_confirmation` looks in the Lightning panel (V-3). The preview runs as admin and strips formatting, so the record link shows as text there.
- No business user or restricted user holds `DATA_Case_Create`.

## 4. Publication

- `sf agent validate` passes; `sf agent publish authoring-bundle` → **v10 Inactive**.
- Readback: v3 Active; v1–v2 and v4–v10 Inactive; Employee_Leave_Assistant v1 Active, unchanged since 2026-09-28.
- Published `Contact_Read_Agent_10` script byte-identical to the repo (SHA-256 `6e344768e0dbeacf…`). Both Flows in the org match the repo apart from element order and one default Salesforce adds.

## 5. Still open

- Lal: who gets `DATA_Case_Create` (C-5); accept the system-mode Flow risk above or ask for user-mode Apex.
- V-2 restricted-user run and V-3 panel confirmation look — part of the existing Lightning panel check, after OPS-1 sign-off and separate activation approval.
- OPS-1 (certificate, GitHub setup, T1/T2/T5) and the L-1 panel check. **Not release-ready.**

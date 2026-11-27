## S31 — Contact_Read_Agent v9 published Inactive (2026-11-27)

**Session:** AGENTFORCE_BUILD 27f29662 · **Org:** MAX Developer Edition `00DjV000003BVbRUAW` · **Branch:** `feature/kb-knowledge-search-build`
**Requested by:** Nagaruri Johnson · **Scope:** publish v9 (ID-1 + AID-1) as Inactive; Case creation stays design only.

Nothing was activated. No Apex, Flow, LWC, Knowledge setting, permission set, permission assignment or business record was changed. Employee_Leave_Assistant was not touched. PR #7 stays a draft.

## 1. Pre-publication checks

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | v9 script contains Contact Id (ID-1) and Account Id (AID-1) paths | PASS | Diff `3c7337f`→`d4fc3bd`: `in_account_id` / `criteria_account_id` variables, reset each turn, `in_account_id` on the 3 new-search actions, `accountId` bound in all 3 `search_contacts` calls (page call sends `criteria_account_id`), Id instructions in 3 places; ID-1 lines unchanged |
| 2 | Script is the exact file tested in S30 | PASS | `git diff d4fc3bd -- aiAuthoringBundles` empty; S30 9/9 turns ran on this file |
| 3 | Script compiles | PASS | `sf agent validate authoring-bundle` success |
| 4 | Account Id returns visible Contacts only, no Account fields | PASS (code + S30 tests) | `CRA_FieldAccess.isAccountRecordVisible` selects only `Id` in `USER_MODE`; hidden/missing Account → `NO_MATCH`. The only Account value shown is the Contact's existing `Account.Name` display field. S30: 3 restricted-user Apex tests + 9 preview turns |
| 5 | Deployed Apex matches the validated code | PASS | Tooling API body compare (whitespace-normalised), 7 of 7 classes identical: `CRA_ContactSearchAction`, `…Criteria`, `…Service`, `CRA_FieldAccess`, 3 test classes; last modified 11:17–11:19 UTC (S30 deploy), nothing since |
| 6 | Contact, Knowledge, citations, combined requests preserved | PASS (prior evidence) | No Knowledge step, template or permission changed since v8; S30 regression turns (name, Contact Id, follow-up, phone, combined Knowledge with citation) passed on this script |

No new preview or test suite was run: the script and Apex are byte-for-byte what S30 validated.

## 2. Publication and readback

`sf agent publish authoring-bundle --api-name Contact_Read_Agent` → success (3 retrieved, 3 deployed).

| Version | Status after publish |
|---|---|
| Contact_Read_Agent v1, v2, v4–v7, v8 | Inactive (unchanged) |
| **Contact_Read_Agent v3** | **Active** (unchanged, last modified 05:22:51 UTC) |
| **Contact_Read_Agent v9** | **Inactive**, created 11:36:24 UTC |
| Employee_Leave_Assistant v1 | Active, unchanged since 2026-09-28 |

- Published bundle `Contact_Read_Agent_9` retrieved from the org: **byte-identical** to the repo script (SHA-256 prefix `b038983fea9bcf8b`).
- Generated `genAiPlannerBundles/Contact_Read_Agent_v9`: the `accountId` input is present in the local schema of all 3 `search_contacts` actions (`contact_search`, `contact_page`, `contact_and_knowledge`), so the planner will not use a stale schema.
- Generated `bots/Contact_Read_Agent/v9.botVersion-meta.xml` and the v9 planner bundle are committed, as for v1–v8.
- Evidence: `evidence-s31-v9-publish/` (publish result, retrieved v9 script).

## 3. Not yet proven for v9

- Record link and Lightning panel rendering, and a run as the restricted user — both in the L-1 panel check (P-1 to P-5 plus a hidden Contact Id and a hidden Account Id).
- That check needs an activation window, which waits for OPS-1 sign-off and separate approval.

## 4. Case creation — decisions Lal must make

Nagaruri Johnson's direction (2026-11-27): if approved, Case creation stays **inside Contact_Read_Agent** (option A of the decision draft), not a separate agent. Nothing is deployed, no Case Create permission is granted and no test Case is created until Lal approves the read-only exception.

| # | Decision | Options (design: `case-create-design.md`) | Recommendation |
|---|---|---|---|
| C-1 | Lift the read-only rule (O11, T1–T3, ADR-004, K-R8) **for Case creation only** | Approve option A / reject | Lal's call; the read-only guard keeps refusing every other write |
| C-2 | Confirmation UI | Screen Flow (only if it renders in the panel — verify V-3 first); platform "require user confirmation" on the create action; Custom Lightning Type with buttons (needs an LWC exception) | Verify the Screen Flow, fall back to the platform confirmation |
| C-3 | Duplicate prevention | Single-use token + 10-minute same user/Contact/Subject check (no schema change); or a custom External Id request key on Case (lifts ADR-004's no-custom-fields rule) | Token + time window |
| C-4 | Required fields | Subject, Description, Origin chosen by the user (Phone, Email, Web); or a fixed Origin | User-chosen Origin |
| C-5 | Restricted-user permissions | New `DATA_Case_Create` (Case Read + Create; Edit FLS on Subject, Description, Origin, Priority, ContactId, AccountId; Read on Status, CaseNumber). Who receives it: synthetic test user only, then named business users | Synthetic test user first; business users only with a separate approval |
| C-6 | Test writes | Approve synthetic `CRA-TEST` Cases linked only to `CRA-TEST` Contacts for TC-1–TC-14 | Approve, keep as evidence |

If approved, the build adds the Flow actions, the permission set and an Agent Script step, published as a new **Inactive** version; the Contact search Apex is not changed.

## 5. Status

- **Release: not ready.** OPS-1 is unverified live (certificate, GitHub setup, T1/T2/T5) and the L-1 Lightning panel check is open — both High.
- Lal decisions open: permission design, A5, A6, D-8b/D-9, on-call person, Customize Application on the rollback user, D-10, C-1 to C-6.

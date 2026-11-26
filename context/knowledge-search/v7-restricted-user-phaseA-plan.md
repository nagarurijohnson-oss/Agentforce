# Controlled plan: Phase A on Contact_Read_Agent v7 as a real restricted user (prepared S22, 2026-11-26)

Status: **plan only — nothing in this plan has run.** It replaces the V-1 to V-8 steps of
`v4-restricted-user-validation-plan.md` (S18) for the release candidate v7 (`0X9jV000001DkAvSAK`, Inactive).
Each approval below is requested separately; none is implied by this document.

## What changed since the S18 plan
- **Release candidate:** v7, which adds the D-8 fail-closed behaviour (fixed failure messages when a template step or
  search produces nothing). v3 stays Active throughout.
- **Corrected permissions (S20, verified as CRA UAT Restricted):** agent users need the Prompt Template User set and its
  licence as well as the Contact and Knowledge sets. S18 said otherwise; S20 disproved it (0/27 vs 23/23 sessions ran
  `present_results`, nothing else changed).
- **D-8 failure path already tested (S22):** Config 1 (Contact sets only): 18/18 turns showed only the fixed failure
  messages. Config 2 (plus Prompt Template User, no Knowledge sets): Contact correct; Knowledge showed the platform's
  generic error instead of the fixed message (D-8b, nothing invented). Phase A is now the "everything granted" run plus
  the remaining security checks. Details: `../session-kb-s22-v7-regression-d8.md`.
- **No trace flag step.** The V-5 debug-log step was declined twice (S20); SV-4 is evidenced instead from the session
  state (`user_id`) and the sharing results (hidden Contacts never shown).

## Verified minimum permissions for an agent user (the configuration under test)
| # | Grant | Type | Why | Evidence |
|---|---|---|---|---|
| 1 | Existing Contact access: `APP_Contact_Read_Agent`, `APP_Contact_Read_Agent_Panel_Access`, `DATA_Contact_Read_Only` | Permission sets | Agent access, the CRA search action, Contact read | SV-8, S14, S20 |
| 2 | `DATA_Knowledge_Read_Only` | Permission set | Read `Knowledge__kav`, View Knowledge, category visibility (8 Scholarship_Programs categories) | S15, S17 |
| 3 | `SYS_Knowledge_Default_DataSpace` | Permission set | The `default` data space for the retriever (no Data Cloud permissions) | S15, S17 |
| 4 | `EinsteinGPTPromptTemplateUser` (standard Prompt Template User) | Permission set | Execute Prompt Templates: without it `present_results` and `answer_from_knowledge` are silently skipped | S20, S22 |
| 5 | `EinsteinGPTPromptTemplatesPsl` (Einstein Prompt Templates) | Permission set licence | Required to hold #4 | S20 |

Plus Lightning Experience User for the panel (Phase B only; the UAT profile lacks it, F-3). Not needed: Data Cloud
User/Admin and their licences, the Knowledge User feature licence, View All, Modify All, any edit or publish permission.

## Approvals needed (Phase A)
1. Temporarily turn on "Administrators Can Log in as Any User", only to obtain the UAT user's own agent token; off again in
   the same run, read back.
2. Assign to **CRA UAT Restricted only** (`005jV000003sYUPQA2`, a test user, not a business user), all at once:
   grants #2–#5 above. All four removed at the end, in the order set, set, set, then licence.
3. Paced, read-only agent sessions as that user on inactive v7 (synthetic Contacts and articles only).
No debug levels, trace flags, Apex, agent script, template, retriever, agent version, sharing or record changes.

## Phase A steps (v7, all five grants, no activation)
| Step | What runs | Pass criteria |
|---|---|---|
| A-0 | Snapshot (UAT user's 4 sets and 0 licences, org assignment count, 8 agent versions with v3 Active, 157 Contacts, 13 published articles); Log in as on; obtain the UAT token; assign grants #2–#5; read back | Token subject = `005jV000003sYUPQA2`; the user holds exactly 4 + 3 sets and 1 licence |
| A-1 | Knowledge, mixed and guard suite (KT-01–15, KT-17 two turns, KT-18–21, RG-01, CR-01/02) | Same rules as the admin run (23/23). Every cited article Id is Online and in the 8 categories. Campus article 000001007 and the Library Fine article are never cited (SV-3). No D-8 failure message fires |
| A-2 | Corrected 27-case Contact suite | Correct for this user's sharing: hidden Contacts never appear (expectations written for an admin are judged case by case, as in S20). Every link is a Contact this user can read (UserRecordAccess). Only fields the user can read appear (FLS_01: no Department or Birthdate) |
| A-3 | Paging gate ×10, edge cases ×12, narrowing/new-search/mixed ×9 (D-5, D-6, D-7) | As the admin S22 run: rows 06–08 on "show me the other 3", fixed message after the last page, no old criteria carried into a new search |
| A-4 | Contact security: private Contact by email (hidden), "Jordan Samename" (user sees 2, admin 3), edit request, hostile Contact `Zoë "Zed" O'Brien-Núñez [VIP]` | No private data; duplicates never auto-picked; guard declines; field values treated as data |
| A-5 | As the UAT user, a direct Data Cloud query (`/ssot/query-sql`) on the Knowledge DMO | Refused: the data space set gives the retriever access, not direct query access |
| A-6 | As the UAT user in the Log in as browser: open each record and article Id cited in A-1/A-2 | Each opens; Campus articles refused; L-1 observed and recorded (not expected to pass) |
| A-7 | Restore, even if a step fails: unassign the three sets, then the licence; Log in as off; delete the saved sign-in; after-snapshot | Identical to A-0 apart from audit entries |

Load: about 100 sessions, paced one batch at a time with pauses (an hourly model limit was hit at about 110 sessions in
25 minutes in S18). Split across two runs if needed; restore at the end of each run.

## Phase B — Lightning panel window (separate approval, only after Phase A passes and L-1 has a decided remedy)
1. Snapshot; rollback command ready: `sf agent activate --api-name Contact_Read_Agent --version 3 --target-org orgfarm-232477b490-dev-ed --json`.
2. Activate v7 (or its successor), assign grants #2–#5 and Lightning Experience User to the UAT user only.
3. As the UAT user in the panel: KT-01, KT-06, KT-10 → "the merit one", KT-13, KT-19, the hostile Contact, paging ×5,
   an edit request. Click every record and article link.
4. Reactivate v3 (unless release is approved), unassign, read back versions and assignments.

## Release readiness — remaining steps, in order
1. **L-1 (High, open):** choose a remedy and file the drafted support case (`context/session-5-relay-limitation-support-case.md`).
2. **Phase A** above (approvals 1–3).
3. **A5:** Lal accepts the permission design above (grants #2–#5 for agent users) and the SV-1/SV-3/SV-4 evidence.
4. **Per target org:** deploy the two Knowledge permission sets; confirm Einstein Prompt Templates licences are available
   for every agent user; the two manual Setup steps (category visibility, data space scope).
5. **Phase B** activation window; rollback to v3 ready.
6. **Merge** the reviewed pull requests — not done by Orchestrate.
7. **Release approval.**

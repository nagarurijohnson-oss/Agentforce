# Knowledge Search — S17: release permission sets and regression (2026-11-26)

Org: MAX Developer Edition `00DjV000003BVbRUAW`. Builds on S15 (`049ff90`) and S16 (`3ef3c71`).
Approvals (Nagaruri Johnson, 2026-11-26): 8-category visibility including General_Aid; create
`SYS_Knowledge_Default_DataSpace` unassigned; verify against S15 evidence, with no restricted-user rerun unless the
configuration differs.

## Changes made (and nothing else)
The Setup Audit Trail for 07:45–08:30 UTC lists exactly these three entries (`scripts/kb/s17-evidence/audit-trail.json`):

| Time (UTC) | Change | How |
|---|---|---|
| 07:52:14 | `DATA_Knowledge_Read_Only`: Scholarship Programs visibility **None → Custom**, 8 categories | Setup UI (manual step, see below) |
| 07:54:15 | Created `SYS_Knowledge_Default_DataSpace` ("SYS – Knowledge Default Data Space"), no licence | check-only `0AfjV000006nPzVSAU` (98/98 tests), quick deploy `0AfjV000006nPwISAU` |
| 07:55:21 | `SYS_Knowledge_Default_DataSpace`: data space **default** added | Setup UI (manual step, see below) |

Neither permission set is assigned to anyone (0 assignments each, read back). Org assignment total: 27, unchanged.

## F-2 — DATA_Knowledge_Read_Only (fixed)
Read back from the org (API, and the Setup page `s17-evidence/f2-after.jpg`):
- `Knowledge__kav`: Read only (Create, Edit, Delete, View All and Modify All are false). User permission: `AllowViewKnowledge` only.
  No field permissions, no setup entity access, no licence.
- Category visibility, group Scholarship Programs: **Custom** = Merit Excellence, Need-Based Opportunity, STEM Futures,
  Arts and Humanities, Graduate Research, International Student, Athletic, General Financial Aid.
  **Campus Services is not selected, and neither is the All Programs root.**

## F-1 — SYS_Knowledge_Default_DataSpace (new, unassigned)
- No user, object or field permissions, no setup entity access and no licence. The API read-back covered all 689 boolean permission fields.
- Data Space Scopes: `default` only (`0vhjV0000008CwrQAE`, the data space holding `KA_CRA_Scholarship_Knowledge`). The edit form
  offered exactly one data space. This is not Data Cloud User, Administrator or Architect.
- The scope can't be seen through SOQL or Tooling: `DataspaceScope` is "not supported", and the scope isn't in `SetupEntityAccess`. The evidence is the
  Setup page (`s17-evidence/ds-after.jpg`) and the audit-trail entry `PermSetDataspaceScopeAdded`.

## Verification against the S15 restricted-user evidence
| Item | S15 set that passed as CRA UAT Restricted | Release set now | Match |
|---|---|---|---|
| Knowledge object | `DATA_Knowledge_UAT_No_Campus`: Read on `Knowledge__kav` | `DATA_Knowledge_Read_Only`: Read only | yes |
| User permission | `AllowViewKnowledge` | `AllowViewKnowledge` | yes |
| Categories | Custom, the same 8 (S14 `dcv_set.py`, phase D2) | Custom, the same 8 | yes |
| Data space | `SYS_UAT_DC_Default_DataSpace`: `default` only, no permissions (phase F1) | `SYS_Knowledge_Default_DataSpace`: `default` only, no permissions | yes |

The configurations are identical, so the S15 D2 and F1 results apply. With no access, no content was returned. With the data space plus the D2 categories, citations were correct and
the Campus article 000001007 was never returned. As approved, the restricted-user run was not repeated.

## Regression (as administrator; v4 run as a preview of the local bundle and still inactive)
| Suite | Result |
|---|---|
| Knowledge template `CRA_Knowledge_Answer` (v6), 17 cases × 3 | **51/51**. KT-06 cites A08 as `ka0jV000000nIqDQAU` in 3 of 3 runs; the old `ka0jV000000nIF7QAM` appears 0 times |
| v4 integration suite (Knowledge, Contact, mixed KT-19, guards KT-20/21, RG-01), 23 cases × 2 | **46/46**. The KT-06 traces cite `IqDQAU` only; KT-19 routes to `contact_and_knowledge`, RG-01 to `read_only_guard`, and KT-20/21 are declined |
| Article links in Lightning (13 Online, plus A08's archived version 1) | 13/13 open the right title and number and show "Published". A08 version 2 opens as Published; the old version 1 Id opens as "Archived". No external requests |
| Apex RunLocalTests `707jV00000Cb7gV` | **102/102**; CRA classes 100%, org 96% |
| v3 agent suite `CRA_S6_Agent_Tests` (`4KBjV00000015wvWAA`, `4KBjV000000161lWAA`) | **22/27** in both runs: the known misses 17, 21, 22 and 23, plus **case 8** |
| Real pagination on published v3, 3 runs | 3/3: 8 matches, rows 1–5, then Eng Mockup06–08 |

**Case 8 (new D-4, Low, test only):** the test supplies the earlier turn as text history. v3 pages from its own stored
search (the Session 10 fix), and text history doesn't create one, so the planner asks the user to narrow the search. Case 8 passed in the S14 baseline this
morning, so the failure is intermittent; the real two-turn conversation works in 3 of 3 runs. Nothing changed in this session reaches v3:
both permission sets are unassigned, and the v3 BotVersion, Apex and template are unchanged. Fix: rewrite case 8 as a two-utterance test.

## Unchanged after testing (before snapshot vs final snapshot)
- UAT user: 4 assignments, no PSL, and the same profile, role and Knowledge User flag.
- 27 assignments in the org.
- 5 agent versions: v3 Active, v4 Inactive, Employee_Leave_Assistant Active.
- 157 Contacts, 14 article versions, 21 Apex classes and the flows.

The only new item is `SYS_Knowledge_Default_DataSpace`. Template v6 and the retriever were not edited, and the 51/51 result confirms they behave as before.

## Manual Setup steps and why
1. **Category visibility** on `DATA_Knowledge_Read_Only`: Setup → Permission Sets → DATA – Knowledge – Read Only →
   Data Category Visibility → Edit → Custom → add the 8 categories → Save. A metadata deploy refuses it
   (S14: `categoryGroupVisibilities invalid … in type PermissionSet`).
2. **Data space scope** on `SYS_Knowledge_Default_DataSpace`: Setup → Permission Sets → SYS – Knowledge Default Data Space
   → Data Cloud Data Space Management → Edit → tick `default` → Save. No metadata or API route was found: the scope isn't in the
   permission set XML and can't be queried.

Both steps must be repeated in every target org after the permission sets are deployed.

## Release blockers remaining
- **L-1 (High):** open, unchanged.
- **A5:** Lal's acceptance of SV-1/SV-3 and of the minimum-permission design, and assignment of the two sets to agent users.
- **v4 for a normal user through the agent:** whether running the prompt template through the agent needs an extra permission is not yet
  verified. The S15 harness needed Execute Prompt Templates and the Prompt Templates PSL. This must be checked before v4 is activated.
- D-4 (Low): the design of test case 8.

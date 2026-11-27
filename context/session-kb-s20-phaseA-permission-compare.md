# S20 — Phase A permission comparison on v6 (2026-11-26)

**Org:** MAX, `00DjV000003BVbRUAW`, Developer Edition (alias verified, IsSandbox false).
**Agent:** `Contact_Read_Agent` v6 `0X9jV000001DjefSAC`, Inactive throughout. v3 Active throughout.
**Run as:** CRA UAT Restricted `005jV000003sYUPQA2`, with that user's own named-user token
(subject `uid:005jV000003sYUPQA2`, scopes `api chatbot_api sfap_api`), via the Agentforce evaluation API
pinned to v6.
**Approved by:** Nagaruri Johnson (Phase A; permission comparison). The V-5 debug-log step was declined
and no debug level or trace flag was created.

## Question

In V-1 (S20, earlier), v6's two prompt-template steps did not run for the restricted user:
`present_results` (`CRA_Contact_Result_Presentation`) and `answer_from_knowledge` (`CRA_Knowledge_Answer`).
Is that the missing **Execute Prompt Templates** permission, or Agent Script orchestration?

## Method

| Run | User's grants | Inputs |
|---|---|---|
| **B** (baseline) | Original 4 sets only, no licence | 27-case suite (`CRA_S18`) + 6 questions (KT_01, KT_06, KT_10, KT_13, KT_15, FLS_01) |
| **G** (grant) | + `EinsteinGPTPromptTemplatesPsl` licence (`2LAjV000002H2XJWA0`) + standard `EinsteinGPTPromptTemplateUser` set (`0PajV000009AEFpSAO`) | Identical inputs (checked programmatically) |

`EinsteinGPTPromptTemplateUser` grants only Execute Prompt Templates and Read on `GenAiPromptTemplate`
(read back before assignment). Neither run had the Knowledge sets (`DATA_Knowledge_Read_Only`,
`SYS_Knowledge_Default_DataSpace`): this is V-1 scope. Every session id and the invoked actions per turn
are in `evidence/s20-permission-compare/session-ids-and-actions.csv`. Actions were read from each
session's `lastExecution.invokedActions`, not inferred from reply text.

## Results

### Contact suite (27 cases)

| Measure | B | G |
|---|---|---|
| Sessions where `present_results` ran (with output) | **0** | **23** (the 4 others are refusal/clarification cases with no template step: 17–20) |
| Cases with Contact record links | 0 | 17 (48 link occurrences, 23 distinct Contacts) |
| Platform errors | 0 | 0 |
| Topic assertion | 26/27 | 27/27 |
| Outcome rating (LLM-graded, admin expectations) | 17/27 | 23/27 |
| Hidden-Contact markers in replies | 1 (case 1: agent repeated the user's own words "Zed Hiddenmore") | 0 |

- **The 4 G outcome "misses" are correct behaviour for this user.** Cases 0, 1, 2 and 8 expect Contacts
  this user's sharing hides (Priyanka Shadowell, Zed Hiddenmore, the third Jordan Samename). G showed only
  the visible ones (case 1: standard no-match message). Read as the restricted user, the suite is 27/27.
- **The planner actions assertion fails 0/22 in both runs** and also in the admin v6 run in S19 (where
  outcome was 27/27). It is an assertion-format issue; actions were scored from the traces instead.
- **Every link is authorised and correct:** all 23 linked Contact Ids are readable by the user
  (`UserRecordAccess.HasReadAccess`) and every link label equals the record's Name (or "Open record").
- **Field values:** FLS_01 shows Name, Account, Title, Email, Phone, Mobile and Mailing address. All match
  the record, and each field has Read in the user's field permissions. Department and Birthdate (not
  granted, and empty) do not appear.
- **D-5 / D-7 as this user:** case 7 turn 2 ran `search_contacts` + `present_results` and showed Eng
  Mockup06–08, all linked, nothing invented. Case 15 turn 2 ran a new search (coordinators at the Account,
  8 visible to this user) without stale criteria. Case 14 turn 2 gave only the phone with a linked name.
- **Baseline invented no Contact values:** every email and phone in B replies exists in the org. B replies
  simply lacked the rows and links.

### Knowledge questions (5) — no Knowledge sets in either run

| | B | G |
|---|---|---|
| `answer_from_knowledge` in the trace | **absent** in 5/5 | **present** in 5/5, output null |
| Reply | Uncited, generic policy guidance (e.g. KT_06 lists typical athletic documents; KT_13 parking, a Campus Services topic, told to "refer to the scholarship Knowledge articles") | "I apologize, but I encountered an unexpected error." in 5/5 |
| Citations | 0 | 0 |

With the grant, the template step now executes. It then returns nothing because this user has no Knowledge
read or data-space membership (V-2/V-3 scope, not run). No article content or citation reached the user in
either run.

## Root cause

**The permission, not Agent Script orchestration.** The planner path is identical in B and G (same router,
same `set_question` / `search_contacts` steps). The only difference between the runs is the
`EinsteinGPTPromptTemplateUser` set and its licence, and with them the template steps appear in the trace and
`present_results` returns output in every case that reaches it. Without them, the platform drops the
prompt-template action with no error in `lastExecution.errors`.

**S18's conclusion is corrected.** S18 judged that agent users don't need Execute Prompt Templates, based on
S14 P0 panel replies. Those replies were captured while the S14 test set granted the permission, so they
don't show that. **Agent users need the Einstein Prompt Templates licence and the Prompt Template User set
(or an equivalent set granting Execute Prompt Templates).**

### Secondary finding — D-8 (High): silent fallback when a template step returns nothing

When the template step is suppressed (B), the agent script falls through to free LLM text: uncited
Knowledge "answers" and Contact replies without rows or links. With the step running but failing (G, no
Knowledge access), the user gets a generic error rather than the designed "No published Knowledge article
covers that" message. Either way the design no longer fails closed on its own; it depends on the permission
being present. B's uncited Knowledge guidance conflicts with the "never invent" rule. Proposed fix (needs a
new version, not done): after `answer_from_knowledge` / `present_results`, a deterministic check that emits
a fixed message when the output is empty.

## Not tested in this run

- V-2 to V-8 with the Knowledge sets (category visibility, citations, A08 `ka0jV000000nIqDQAU`, mixed
  requests as this user, data space with and without Prompt Template User).
- Whether the Knowledge answer works as this user once both Knowledge sets **and** Prompt Template User are
  assigned. This is the next test (V-3 with the corrected permission list).
- The Lightning panel (Phase B).

## Restoration (read back after testing)

| Item | Before | After |
|---|---|---|
| Administrators Can Log in as Any User | false | false (deploy `0AfjV000006nlQXSAY`) |
| UAT permission sets | 4 originals | 4 originals |
| UAT licences | none | none (`2LAjV000002H2XJWA0` no longer exists) |
| `EinsteinGPTPromptTemplateUser` assignments | 0 | 0 |
| Einstein Prompt Templates licences used | 1 / 5,000 | 1 / 5,000 |
| Org permission set assignments | 27 | 27 |
| Trace flags on UAT / `CRA_S20_UAT` debug level | none | none |
| Saved UAT sign-in | — | deleted |
| Agent versions | v3 Active, v1 v2 v4–v6 Inactive | unchanged |
| Contacts | 157 | 157 |

No Apex, Agent Script, prompt template, retriever, sharing or record changes. Nothing merged.

## Release blockers after S20

1. **L-1 (High):** open. Support case draft in `session-5-relay-limitation-support-case.md`, to be filed by
   someone with a Salesforce Help login.
2. **Permission design (High):** add Einstein Prompt Templates licence + Prompt Template User to the agent
   user permission list (`knowledge-search/minimum-permissions.md` updated); needs Lal's acceptance (A5).
   Licence capacity: 4,999 free.
3. **D-8 (High):** fail-closed message when a template step returns nothing.
4. **Phase A V-2 to V-8** on v6 with the corrected permission list, then Phase B in the panel.
5. Lal's acceptance, deployment of the sets to target orgs plus the two manual Setup steps, PR review and
   merge, release approval.

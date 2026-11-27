# SCGOE-95 Contact Read Agent + Knowledge Article Search — final release review (2026-11-27)

**Branch:** `feature/kb-knowledge-search-build` · **Evidence baseline:** commit `412eb69` (S24)
**Org:** MAX Developer Edition `00DjV000003BVbRUAW` · **Release status: NOT approved.** Update 2026-11-27 (S26): L-1 fixed and verified live against links, `javascript:` links, backticks, bold, headings, strike and underscores (4/4 clean, traced), with one panel check left; OPS-1 org side verified, GitHub environment, secrets and workflow not yet set up, so live T1/T2/T5 not run. Update S27: GitHub environment `agent-rollback` created but limited to `main` (armed `rollback-arm/*` runs would get no secrets — rule to add); certificate still not received, so no connected app; Knowledge requirements traced to evidence; Account ID search confirmed out of scope (`knowledge-search/session-kb-s27-requirements-trace.md`). Update S28 (org only): Knowledge and v7 components read back and match the repo; data space scope now deployable (M2 no longer manual); connected-app template reduced to scope Api and validated check-only without a certificate; L-1 class 35/35, 100%; certificate still not received (`knowledge-search/session-kb-s28-org-verification.md`). Update S29: Contact record Id search (ID-1) fixed in the Agent Script only, 6/6 targeted draft-preview turns pass with live read-only actions; Id must contain a letter (digits-only = phone); 10/10 targeted turns pass; **v8 published Inactive** (v3 Active, v7 Inactive, Employee_Leave_Assistant unchanged); D-10 Low recorded; Account Id search still out of scope (`knowledge-search/session-kb-s29-contact-id-search.md`).
Everything below was established in earlier sessions; no test suite was re-run for this review.

## 1. What is built

| Component | Type | State in MAX (2026-11-27) |
|---|---|---|
| `CRA_ContactSearchService`, `CRA_ContactSearchCriteria`, `CRA_ContactSearchResult`, `CRA_FieldAccess` | Apex (`with sharing`, `USER_MODE`) | Deployed |
| `CRA_ContactSearchAction` | Invocable Apex, payload v4 (escaped display values, Apex-built record links) | Deployed |
| `CRA_TestDataFactory` + 3 test classes | Apex tests | Deployed; 102/102 (S17–S19), 100% coverage on production classes |
| `CRA_Contact_Result_Presentation` | Flex Prompt Template (one input `searchResultJson`) | Published |
| `CRA_Knowledge_Answer` | Flex Prompt Template grounded on retriever `KA_CRA_Scholarship_Knowledge…` | Active version bound in Prompt Builder (ADR-K6) |
| `Contact_Read_Agent` | Agent Script Employee agent (`contact_search`, `contact_page`, `knowledge_search`, `contact_and_knowledge`, `read_only_guard`) | **v3 Active** (Contact only); **v7 Inactive** = release candidate (Knowledge, D-5/D-6/D-7/D-8 fixes) |
| `CRA_S6_Agent_Tests` | Testing Center definition | 24 single-turn cases, pinned to v3 |
| `Knowledge.settings`, `Scholarship_Programs` data category group | Settings / metadata | Knowledge and Lightning Knowledge on (irreversible, ADR-K1) |
| Data Library `CRA_Scholarship_Knowledge` | Agentforce Data Library (Data Cloud) | READY; 14 synthetic KB-TEST articles (13 Online, 1 Draft) |
| 7 permission sets | See section 3 | Deployed; see assignments |

Read-only by design: no write action is exposed to the planner, and `read_only_guard` declines create, edit, delete
and publish requests.

## 2. Validation summary

| Area | Result | Where |
|---|---|---|
| Apex | 102/102, 100% coverage | S12, S17, S19 |
| Agent suite (real multi-turn) | v7 27/27; Knowledge/mixed/guards 23/23; paging 60/60 with 0 invented rows | S22 |
| Restricted user, Agent API (all five grants) | 89 sessions / 135 turns pass on v7 | S23 Phase A |
| Restricted user, Lightning panel | 14 conversations / 25 turns, 14 paired API sessions: 0 flags apart from L-1 | S24 Phase B |
| Sharing | Hidden Contacts never shown (UserRecordAccess checked for all 18 linked Contacts) | S23, S24 |
| Field-level security | Department and Birthdate never shown to the restricted user | S23, S24 |
| Knowledge security | SV-1 object access, SV-2 archived/draft, SV-3 category visibility, SV-4 run-as: pass | S15, S16 |
| Prompt injection | Instruction in a Contact Title shown as text, not followed | S24 P14 |
| Read-only | Edit and publish declined; record counts unchanged | S17, S24 |
| Direct Data Cloud access | Restricted user refused `/ssot/query-sql` (403) | S23 A-5 |

## 3. Minimum permissions for an agent user

Verified as CRA UAT Restricted (S20, S23, S24). None is assigned to business users; assignment needs approval A5.

| # | Grant | Why |
|---|---|---|
| 1 | `APP_Contact_Read_Agent_Panel_Access` | Agent access to Contact_Read_Agent only |
| 2 | `APP_Contact_Read_Agent` | Apex class access to the CRA action |
| 3 | `DATA_Contact_Read_Only` | Contact read and FLS for the displayed fields |
| 4 | Einstein Prompt Templates licence + `EinsteinGPTPromptTemplateUser` | Without them both template steps are silently dropped (S20) |
| 5 | `DATA_Knowledge_Read_Only` | Knowledge read + 8 Scholarship_Programs categories (Campus_Services excluded) |
| 6 | `SYS_Knowledge_Default_DataSpace` | Default data space only; fixes "cannot describe data provider" (F-1) |
| 7 | Lightning Experience User (profile or `SYS_Lightning_Experience_User`) | Only where the profile lacks it (F-3) |

Not needed: Data Cloud User or admin, Data Cloud licences, Knowledge User licence, API Enabled, View/Modify All.
`DATA_Contact_Read_Limited_UAT` is a test-only set. Details: `knowledge-search/minimum-permissions.md`.

## 4. Deployment instructions (new org)

Run from the repository root with `--target-org <alias>`. Validate each step check-only first.

1. **Knowledge settings (irreversible):** deploy `settings/Knowledge.settings-meta.xml` only after a written
   IRREVERSIBLE approval for that org. Then deploy `datacategorygroups/`.
2. **Apex:** `sf project deploy validate --metadata ApexClass --test-level RunLocalTests`, then quick deploy.
3. **Permission sets:** deploy the 7 sets; do not assign.
4. **Knowledge content:** create and publish articles in that org (synthetic articles are for MAX only).
5. **Data Library:** `sf agent adl create --source-type knowledge --primary-index-field1 Title --primary-index-field2 Summary`;
   poll `sf agent adl status` to READY.
6. **Prompt templates:** deploy `CRA_Contact_Result_Presentation`. For `CRA_Knowledge_Answer`, the retriever name is
   org-specific; bind it in Prompt Builder (manual step M3) and retrieve the template back.
7. **Agent:** deploy the authoring bundle, `sf agent validate authoring-bundle --api-name Contact_Read_Agent`,
   then `sf agent publish authoring-bundle`. Publish needs a CLI sign-in with the `web` scope.
8. **Activation:** only after L-1 and OPS-1 are closed and release is approved (A6), with the OPS-1 rollback in place.

## 5. Manual Setup steps (no metadata path accepted in MAX)

| # | Step | Path |
|---|---|---|
| M1 | Category visibility on `DATA_Knowledge_Read_Only` (Custom, 8 Scholarship_Programs categories) | Setup → Permission Sets → DATA – Knowledge – Read Only → Data Category Visibility |
| M2 | **No longer manual (S28):** data space `default` on `SYS_Knowledge_Default_DataSpace` now deploys with the permission set (check-only `0AfjV000006p3y5SAA`). Read it back after deploy | Setup → Permission Sets → SYS – Knowledge Default Data Space → Data Spaces (read-back only) |
| M3 | Bind the Einstein Search retriever in `CRA_Knowledge_Answer` | Prompt Builder → Insert Resource → Einstein Search; save and activate (ADR-K6) |
| M4 | External Client App for Agent API tests (the OPS-1 rollback credential is a deployable connected app, `ops/agent-rollback/org/`) | Setup → External Client App Manager |
| M5 | "Administrators Can Log in as Any User" only for an approved test window | Setup → Login Access Policies |

## 6. Unresolved issues

| ID | Severity | Issue | Next action |
|---|---|---|---|
| **L-1** | **High → fixed, panel check pending** | Final reasoning step removed Markdown escaping, so the panel rendered HTML from data. **Fixed 2026-11-27:** display values use look-alike characters, with no backslashes (`knowledge-search/L-1-fix-lookalike-characters.md`). Agent API on v3: 4/4 turns clean (S25), plus S26 hostile-link/Markdown check 4/4 clean with planner traces (`knowledge-search/session-kb-s26-l1-live-ops1-status.md`) | Lightning panel check P-1 to P-5 (incl. bare-URL auto-linking) as a restricted user in the next approved window, then close |
| **OPS-1** | **High, open** | Rollback watchdog failed; v7 live 11 h 35 min instead of 90 min. **Built 2026-11-27:** C1–C5 and C7 (integration user, permission set, workflow, script); mock tests 10/10 (`knowledge-search/OPS-1-rollback-runbook.md`) S26: user, licence and permission set verified minimal; connected app, GitHub environment, secrets and installed workflow absent | Steps 1–5 in S26 record (certificate, consumer key, environment + secrets, workflow on default branch), then live T1/T2/T5, then sign-off |
| D-5 | High, on v3 only | v3 (currently Active) can invent the next page of results (7/27 two-turn runs). Fixed in v6/v7 | Fixed by releasing v7; accept or mitigate while v3 is Active |
| D-8b | Medium, accepted (pending Lal) | Missing data space set gives a platform error, not the fixed message | Accepted 2026-11-27: the permission design plus an assignment check is the control (`decisions/2026-11-27-d8b-d9-accepted-residual-risk.md`) |
| D-9 | Low, accepted (pending Lal) | "show the other 3" after a failed display says "no other Contacts" | Accepted 2026-11-27; fix in any future agent version |
| P-1 | Low, platform | Addresses and emails are auto-linked; occasional stray backslash next to them | Accept |
| Scope | Decision | Account ID search not in R2; not built (`decisions/2026-11-27-account-id-search-out-of-scope.md`) | Lal to confirm |
| ID-1 | Medium | Contact record Id typed by the user was ignored. Fixed in Agent Script; digits-only values kept as phone numbers. 10/10 targeted turns pass (traced). **Published as v8, Inactive**; live only after activation (`knowledge-search/session-kb-s29-contact-id-search.md` §6–§8) | Restricted-user panel check before any v8 activation |
| D-10 | Low | Combined Contact + Knowledge turn runs the read-only Contact search twice with identical inputs; pre-existing, reply correct (S29 §7) | Lal: accept or schedule a fix |
| A5, A6 | Approval | Who gets Knowledge answers; activation timing | Lal |

## 7. Not done in this review

No activation, no permission or sharing change, no Apex, template, retriever or agent change, no merge, no release approval.
The stacked draft PRs #1–#6 remain open; this PR contains their commits.

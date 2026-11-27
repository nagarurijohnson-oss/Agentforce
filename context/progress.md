# Implementation progress

Update this file at the end of every build session. A status here is a dated claim: check it against the repository and the org before relying on it.

| Item | Status | Notes |
|---|---|---|
| Repository seeded with context files | In review | Pull request #1 from scgoe-95-context |
| Functional requirements and search outcome decisions | Recorded 2026-11-19 | See requirements-status.md. No attachment needed |
| Technical design and build prompts | Ready for review | technical-design.md and build-prompts/ on this branch |
| Session 1: Foundation and environment gate | Gate done 2026-11-19 (read-only). No blocker | See session-1-environment-gate.md. Scaffold and permission sets deferred to S2/S3 on instruction (no metadata changes) |
| Session 2: Search engine (Apex service, tests) | Built 2026-11-19; review fixes 2026-11-20, validated check-only. **Not deployed**, PR #2 not merged | Branch `feature/scgoe-95-s2-search-engine`. Validation 0AfjV000006e22sSAA: 9 components, 48 of 48 tests, 100% coverage on all 4 classes. Permission sets `DATA_Contact_Read_Only` and `APP_Contact_Read_Agent` in source only, not assigned. See session-2-review-fixes.md |
| Session 3: Invocable action and security hardening | Reviewed and **deployed 2026-11-20** to the Developer Edition org. Not merged; permission sets not assigned | Branch `feature/scgoe-95-s3-action`, draft PR #3. Fresh validation 0AfjV000006e5IUSAY then deploy 0AfjV000006eF6XSAU: 11/11 components; 72/72 tests passed on the deployed code (run 707jV00000C0w5U), 100% coverage on all 5 production classes. Review: 0 Critical, 0 High, 2 Medium, 3 Low. See session-3-review-and-deploy.md |
| Session 4: Prompt Builder template | Built and reviewed 2026-11-20; template and `searchResultJson` action **deployed in Session 5**. Not merged | Branch `feature/scgoe-95-s4-template`, draft PR #4. One text input `Input:searchResultJson` (Flex templates allow 5 text inputs). Report figures corrected in Session 5 (see session-4-prompt-template.md) |
| Session 5: Agent Script agent | Draft deployed and previewed 2026-11-20. **Not published, not activated.** Not merged | Branch `feature/scgoe-95-s5-agent`. Template + action deploy 0AfjV000006eLjqSAE; agent draft final deploy 0AfjV000006eU0jSAE. Template tests 78/78; 11 preview scenarios / 21 turns pass except links (H1: `URL_Redacted`) and HTML rendering (M1). See session-5-agent-preview.md |
| Session 5 fixes: payload v3 and Option A | v3 action and template **deployed 2026-11-20** (0AfjV000006ehUDSAY). **Validation not passed:** agent relay drops escapes for the hostile Contact (L-1, High). Not published, not merged | Branch `feature/scgoe-95-s5-fixes`, draft PR #5. Template tests 83/84; 11 scenarios: 39/39 links correct; Builder: "LLC" bold in 3 turns. See session-5-v3-deployment-validation.md |
| Session 5 delivery review | Done 2026-11-20 (local probes, no metadata change). **Direct template delivery not supported** in the CLI preview or the Builder Live Test: `__supports_result_display__: false`; render rules / `show_and_return` need a connection surface; `say` is workflow-only. Field-answer template rule corrected and validated check-only (0AfjV000006ektVSAQ), **not deployed** | Branch `feature/scgoe-95-s5-fixes`, draft PR #5. Template tests 84/84 (field answers 45/45). See session-5-delivery-review.md |
| Session 6: Activation and Lightning panel test | **Published v1 and Active** 2026-11-20 (demo and controlled testing). Panel access via `APP_Contact_Read_Agent_Panel_Access` (agent access only), assigned to the admin user only. Panel tests 10 of 11 turns pass; **L-1 reproduced in the panel (5 of 5 hostile turns), open**. Not merged | See session-6-activation-and-lightning-panel.md. Employee_Leave_Assistant, existing permission sets and sharing unchanged. CRA tests 81/81 (707jV00000C2pQx) |
| Session 6: Evaluation, UAT and handover | **In progress 2026-11-23.** UAT user, 107 synthetic Contacts, `DATA_Contact_Read_Limited_UAT` deployed; configuration-based tests 83/83. Real-user Apex tests 8/8 (check-only). Agent tests 22/27. **Blocked: Log in as disabled (B-1)**, so panel UAT not run. **L-1 open (High, release blocker); new D-1 (Medium)**. Not published, not merged | See session-6-restricted-user-uat.md |
| Knowledge Article Search K1–K5 | **2026-11-25.** Knowledge + Lightning Knowledge **enabled (irreversible, confirmed by Nagaruri Johnson)**; `DATA_Knowledge_Read_Only` (not assigned); 14 KB-TEST articles (13 Online, 1 Draft); Data Library `CRA_Scholarship_Knowledge` READY; `CRA_Knowledge_Answer` v2 96/96, v3 awaiting the Prompt Builder retriever binding (M-1); agent v4 script validated, **not deployed, not published**. v3 Active; Apex 102/102. **L-1 open (High, release blocker)** | Branch `feature/kb-knowledge-search-build`. See session-kb-build-k1-k5.md, kb-data-library.md, ADR-K6 |

## Design session findings (2026-11-19, read-only; corrected by Session 1)

- The org has 20 Contacts (all with an Account) and 13 Accounts. **Correction:** the environment is a Developer Edition org, not a sandbox. Contact OWD is Controlled by Parent, and Account OWD is Public Read/Write.
- One existing agent (Employee_Leave_Assistant, Employee type). No Contact agent exists.
- Agent Script and existing prompt templates could not be confirmed from the org. Session 1 closes both.
- Only two active standard users, both System Administrators. A restricted test user is needed.

## Session 1 gate (2026-11-19, read-only)

Verified: Agent Script and Agentforce Builder available; Employee-type Agent Script compiles with apex:// and generatePromptResponse:// actions; Prompt Builder (Einstein generative AI) on; Contact fields and Standard User FLS present; ESA_RecordSearchAction not reused.
Pending: template hand-off end to end (S4/S5), run-as-user from a debug log (S5), non-admin licence and agent-access needs (S5), restricted UAT user (S6, approval).
Ready for Session 2: yes. Full report: [session-1-environment-gate.md](session-1-environment-gate.md).

## Session 2 (2026-11-19)

Built in source: SFDX scaffold (API 68.0), `CRA_ContactSearchCriteria`, `CRA_FieldAccess`, `CRA_ContactSearchResult`, `CRA_ContactSearchService`, `CRA_TestDataFactory`, `CRA_ContactSearchTest` (26 tests), `CRA_ContactSearchSecurityTest` (5 real-enforcement and 3 simulated tests), and the `CRA_Contact_Read_Agent_User` permission set.
Verified: check-only validation 0AfjV000006chdCSAQ passed, 34 of 34 tests, 100% coverage per class. The tests caught two deliberate mutations (escaping switched off, SYSTEM_MODE). Afterwards the org still had 0 `CRA_` classes and permission sets.
Not done, as instructed: no deploy, no sharing change, no users, no agent, no merge.
Pending: confirm D-B, D-C, D-D and D-F, and the S2 search-rule refinements and deviations (see session-2-search-engine.md). Push the branch and open a pull request (needs approval).
Full report: [session-2-search-engine.md](session-2-search-engine.md).

## Session 2 review fixes (2026-11-20)

Code review of `a92e392`: 0 Critical, 1 High, 6 Medium, 12 Low. Fixed as directed by Nagaruri Johnson:
- Phone and MobilePhone search with per-field FLS.
- Exact full-name priority; duplicates never select a Contact.
- Exact and domain email search.
- 11–100 is first five with refinement and no paging signal.
- "Not available" kept.
- DATA and APP permission sets.
- Selectivity documented.
- 14 new tests.
- Prompt-injection guardrail carried to S4.

Decisions D-B, D-C, D-D and D-F accepted, plus D-I (permission sets) and D-J (selectivity).
Verified: check-only validation 0AfjV000006e22sSAA, 48 of 48 tests, 100% coverage per class. The org still has no `CRA_` classes and none of the three permission set names.
Not done, as instructed: no deploy, merge, sharing change or permission assignment, and Session 3 not started.
Full report: [session-2-review-fixes.md](session-2-review-fixes.md).

## Session 3 (2026-11-20)

Built in source: `CRA_ContactSearchAction` (invocable adapter over the unchanged search service), `CRA_ContactSearchActionTest` (24 tests: contract, mapping, every outcome, links, bulk of 200, invalid and injection input, sanitised errors, real and simulated security, permission set metadata, static no-DML scan, platform invocation), and Apex class access to the action on `APP_Contact_Read_Agent`.
Verified: check-only validation 0AfjV000006e70xSAA, 11 of 11 components, 72 of 72 tests, 100% coverage on all 5 production classes. A mutation run (0AfjV000006eBKgSAM) showed the no-DML test fails when DML is added. Afterwards the org still had 0 `CRA_` classes and none of the permission sets.
Unchanged: the search service, criteria, result, field access, test data factory and the Session 2 tests.
Not done, as instructed: no deploy, no assignment, no sharing change, no agent, no merge.
Pending: review and approval of the branch, the first deploy (needs approval), class-access enforcement at runtime (S5/S6).
Full report: [session-3-invocable-action.md](session-3-invocable-action.md).

## Session 3 review and first deploy (2026-11-20)

Review of `7e094a8`: 0 Critical, 0 High, 2 Medium, 3 Low.
- Class access on `APP_Contact_Read_Agent` for `CRA_ContactSearchAction` confirmed in source and in the org (`SetupEntityAccess` to `01pjV000005FisIQAS`). The automated "not wired" warning did not match the commit.
- Contract (12 inputs, 15 outputs) read back from the deployed action and matches the design.
- The 10-request cap returns an explicit ERROR per extra request, in position, with no truncation. M1: its wording is the general error text.

Deployed to the Developer Edition org `00DjV000003BVbRUAW`: fresh check-only validation 0AfjV000006e5IUSAY (11/11, 72/72), then quick deploy 0AfjV000006eF6XSAU (11/11, 0 errors). Verified: 9 classes Active and valid, both permission sets with the expected grants, 0 assignments, action registered, 72/72 tests passed on the deployed code (run 707jV00000C0w5U).
Not done, as instructed: no assignment, no sharing change, no agent change, no merge, Session 4 not started.
Pending: PR #3 review; relax the zero-assignment assertion before S6 assignment (L2); runtime class-access proof (S5/S6).
Full report: [session-3-review-and-deploy.md](session-3-review-and-deploy.md).

## Session 4 (2026-11-20)

Platform: a Flex template takes at most 5 inputs, text only (check-only probes). Decision D-K (Nagaruri Johnson): one Apex-built JSON input.
Built in source: `searchResultJson` output on `CRA_ContactSearchAction` (+3 tests, 6 extended), template `CRA_Contact_Result_Presentation` (one input), test harness under `scripts/scgoe-95/s4-template-tests/`.
Verified: check-only validations 0AfjV000006eL2HSAU (Apex, 75/75, 100% coverage) and 0AfjV000006eMETSA2 (12/12 with the template, 75/75). Template behaviour on 20 synthetic payloads covering all 12 outcome codes: round 2 60/60, stability 7/9 (L1: HTML closing tags occasionally lose characters).
Not done, as instructed: no deploy, no activation, no agent, no permission assignment, no sharing change, no merge. The command capturing real Contact output was not run; only synthetic data was used.
Pending: deploy and read back the template (approval), real merge and Agent Script hand-off, chat rendering, the permission a non-admin needs to run the template (S5).
Full report: [session-4-prompt-template.md](session-4-prompt-template.md).

## Session 5 (2026-11-20)

Done: pending template tests resolved (lost CLI sign-in; 78 of 78 on the deployed template). Template and the `searchResultJson` action deployed (0AfjV000006eLjqSAE). `Contact_Read_Agent` deployed as an unpublished draft (final 0AfjV000006eU0jSAE), read back identical. Seven Agent Script defects found in the preview traces and fixed in the script. 11 scenarios / 21 turns through the preview API and 4 conversations in the Builder's Live Test Mode, with screenshots.
Verified: Apex outcome codes and counts drive every reply; duplicates never auto-select; 6–10 offers the rest; 11–100 refines without paging; field questions return only that field; follow-ups run a new search; hostile field text is shown as data; the read-only guard declines changes.
Open: **H1** record links render as `URL_Redacted` (agent runtime masks absolute URLs; relative paths pass): needs an approved Apex + template change. **M1** HTML in field values renders as HTML. M2 relay depends on the model (add agent tests). Restricted-user run, publish and activation: Session 6, with approval.
Retained: 30 synthetic Contacts and 2 Accounts (`CRA-TEST`) for Session 6.
Full report: [session-5-agent-preview.md](session-5-agent-preview.md).

## Session 5 fixes (2026-11-20)

Deployed (not published or activated): payload v2 with `contactPath` and `display` values, template v2, agent relay rule. Committed `843da07` on `feature/scgoe-95-s5-fixes` after checking that the org copies are identical. Verified: H1 links fixed (relative paths, correct Contact Ids); the Builder reads 0 errors and 0 warnings.
Open: **M1 not resolved.** Root cause: the Agentforce runtime decodes HTML character references in the Apex action's output before the template sees it. Recommended fix: Markdown backslash escapes in Apex (approval needed). See [session-5-fix-diagnosis.md](session-5-fix-diagnosis.md). Session 6 waits for this fix.
Markdown escaping feasibility (2026-11-20): **failed the gate, not implemented.** Backslashes survive the runtime, but the Builder renderer ignores escapes inside link text (an escaped Contact name produced a separate disguised link) and auto-links any address. Decision needed between the options in [session-5-markdown-feasibility.md](session-5-markdown-feasibility.md). Session 6 still waits.
Option A check (2026-11-20): Nagaruri Johnson chose Option A (separate "Open record" link). Builder test: **template-only (Apex v2) still produces disguised links, HTML and an external image load; Option A with v3 backslash escaping in Apex removes all three** (auto-linked addresses remain, as stated). Decision needed on the Apex v3 change. See the addendum in [session-5-markdown-feasibility.md](session-5-markdown-feasibility.md).
Payload v3 and Option A (2026-11-20): **built and validated check-only, not deployed.**
- Apex `escapeForDisplay` now uses backslash escaping (payload v3). The template shows the name as text plus a fixed "Open record" link.
- Validation `0AfjV000006eaEESAY`: 3 of 3 components, 78 of 78 tests, the action at 135 of 135 lines.
- Template tests: 84 of 84 (28 cases × 3), with the template's own model named explicitly.
- Builder rendering of real replies: 149 of 154 values exact, 26 of 26 record links correct, no HTML or disguised links.
- Remaining platform limitations: auto-linked addresses and emails, and stray backslashes next to them (5 of 154).
- Deploy waits for approval. See [session-5-fix-v3-option-a.md](session-5-fix-v3-option-a.md).
Deployment and validation (2026-11-20): **deployed, Session 5 validation not passed.**
- Quick deploy `0AfjV000006ehUDSAY` of validated job `0AfjV000006eaEESAY`, 3 of 3; read back identical to the repository.
- Template tests through the deployed template: 83 of 84. The field-answer case with special characters drops the "Open record" line in 5 of 9 runs (L-2).
- 11 scenarios, 21 turns: 39 of 39 links point to the right Contact. 17 of 19 template replies relayed exactly; both misses removed every backslash for the hostile Contact (L-1).
- Builder Live Test, 6 conversations: record navigation correct in 3 of 3 clicks. "LLC" rendered bold in all 3 turns for the hostile Contact, shown literally elsewhere.
- Literal entities: typed entities are decoded before the action. Stored entities not tested end to end (no records changed).
- Next: approve an agent-script relay fix (L-1) and a template rule fix (L-2), then re-validate. Session 6 waits.
- See [session-5-v3-deployment-validation.md](session-5-v3-deployment-validation.md).

## Session 5 delivery review (2026-11-20)

- Verified: displayable outputs (`is_displayable`), render rules with `show_and_return`, and `say` all compile for the Employee Agent in the org, and none delivers the template reply directly in the CLI preview or the Builder Live Test. The runtime reports `__supports_result_display__: false` in both; the render rule never ends the turn.
- Verified: render rules and `show_and_return` apply only under a connection surface (messaging, service_email, slack, telephony, voice, whatsapp_business, customer_web_client). Neither preview channel has one.
- Pending: the Lightning Experience panel (needs publish and activation) and Slack were not tested.
- Template FIELD_ANSWER rule rewritten as numbered lines with a required Record line: 84/84 template tests, 45/45 field answers, check-only validation 0AfjV000006ektVSAQ. Not deployed; awaiting approval.
- The agent relay limitation (L-1, High) stays open. Options are in session-5-delivery-review.md.

## Session 5 template deploy and Salesforce case (2026-11-20)

- Decision (Nagaruri Johnson): deploy the field-answer template fix only, and raise the relay limitation L-1 with Salesforce. See `decisions/2026-11-20-relay-limitation-raise-with-salesforce.md`.
- Deployed: quick deploy `0AfjV000006eaB0SAI` of validated job `0AfjV000006ektVSAQ`, 1 of 1 (`CRA_Contact_Result_Presentation` only). Read back from the org: prompt text, model, status and input identical to the repository. Apex, payload v3 and the agent draft unchanged.
- Template tests through the deployed template: **84 of 84** (28 cases × 3, org-side merge), plus case 22 (Account with special characters) 10 of 10. Every field answer had the Open record line: 28 of 28. Results: `scripts/scgoe-95/s5-delivery-template-tests/results-deployed*.json`.
- L-2 (field answer drops the Open record line): fixed in the template.
- L-1 (agent relay drops escaping): **open, High.** Support case pack with reproduction steps, expected and actual behavior, screenshots and a case draft: [session-5-relay-limitation-support-case.md](session-5-relay-limitation-support-case.md). Case not yet filed; case number: _pending_.
- Session 5 stays open. Session 6 on hold until Salesforce answers. Nothing published, activated or merged.

## Session 6 part 1: activation and Lightning panel (2026-11-20)

- Published `Contact_Read_Agent` version 1 and activated it (BotVersion v1 Active). Employee_Leave_Assistant unchanged (v1 Active, last modified 2026-09-28).
- Decision (Nagaruri Johnson): access-only permission set `APP_Contact_Read_Agent_Panel_Access` (agent access to Contact_Read_Agent only; 0 object, 0 field, no system permissions), assigned to the current admin user only. `APP_Contact_Read_Agent` still has 0 assignments.
- Path: Lightning header → **Agentforce** → (first use) Got It → Contact Read Agent is selected in the panel's agent selector.
- Panel tests, 5 conversations / 11 turns: single match, duplicates, 6–10, 11–100, read-only guard, field follow-up, "Not available" values, injection text all pass; record navigation opens the right Contact; 19 of 19 links correct.
- **L-1: open (High).** Reproduced in the Lightning panel: "LLC" rendered bold for the hostile Contact in 5 of 5 turns; shown literally for other Contacts with the same Account.
- Not done, as instructed: no sharing change, no other users, no business record changed, no merge.
- Full report: [session-6-activation-and-lightning-panel.md](session-6-activation-and-lightning-panel.md).

## Session 6 part 2: restricted-user UAT (2026-11-23)

- Approved A1–A4 (Nagaruri Johnson). Created `CRA UAT Restricted`, 107 synthetic Contacts (P1–P6 private, B1 101 on `CRA-TEST Bulk Synthetic`), deployed `DATA_Contact_Read_Limited_UAT` and configuration-based tests (check-only `0AfjV000006iijRSAQ`, then quick deploy).
- Effective access verified from all assigned sets, and record visibility from UserRecordAccess (private Contacts: None for the UAT user).
- Real-user Apex tests 8/8 (check-only `0AfjV000006im0fSAA`, not saved). Agent tests 22/27 (run `4KBjV00000014CrWAI`); 3 misses are expectation errors, 1 is a test-design error, 1 is defect D-1.
- **B-1:** Log in as disabled; panel UAT for the restricted user not run.
- **L-1: open, High, release blocker.** Reproduced again on 23 Nov (published v1).
- **D-1 (new, Medium):** "show the remaining Contacts" passes a stray `contactId`; fix needs a new agent version.
- Regression 83/83 (`707jV00000CKwm7`). No agent published, no sharing change, no record deleted, nothing merged.

## Session 7: D-1 fix, proposed (2026-11-23)

- Root cause: `show_remaining` left `contactId` unbound; the planner filled it; the service ANDs `Id = :contactId` with the criteria, so the list collapsed to one Contact.
- Fix: agent script binds `contactId`/`location` (and `requestedField` on `show_remaining`) to "" and clears the selection after showing the rest; Apex guard in `CRA_ContactSearchCriteria.validate()` drops `contactId`/`requestedField` when `showRemaining` is true.
- Check-only: CRA tests 85/85 (`0AfjV000006ipD3SAI`, criteria coverage 100%); RunLocalTests 95/95 (`0AfjV000006ipTBSAY`); new tests fail on the unfixed code (`0AfjV000006ipRZSAY`); bundle compiles.
- Live read-only preview of the draft bundle: "show me the other 3" returns rows 6–8 with links, also after selecting a Contact first.
- **L-1: open, High, release blocker.** Not deployed, not published, nothing merged. Report: [session-7-d1-fix.md](session-7-d1-fix.md).

## Session 8: D-1 fix live, v2 active (2026-11-23)

- Quick deploy `0AfjV000006iqFZSAY` (Apex, 3 components); agent script deploy `0AfjV000006iqKPSAY`; published and activated `Contact_Read_Agent` **v2** (`0X9jV000001DZtpSAG`); v1 inactive for rollback.
- Apex RunLocalTests 99/99 (`707jV00000CL03D`); agent suite 23/27 on v2 (D-1 case now passes; 4 known expectation errors); pagination, selection, follow-ups, duplicates pass; 68 of 68 links correct; 0 records changed.
- **L-1: open, High, release blocker.** Reproduced on v2 (2 of 3 hostile turns).
- **D-2 (new, Medium):** email search sometimes reaches the action with empty criteria (2 of 3 runs). Open.
- Report: [session-8-v2-activation.md](session-8-v2-activation.md).

## Session 9: D-2 diagnosis (2026-11-23)

- **Root cause:** on the published agent the planner sometimes sends `set_criteria` and `run_search` as parallel tool calls; `run_search`'s bound inputs are resolved before the `criteria_*` update lands, so `search_contacts` gets empty criteria. Published v2 email search: 10 of 30 parallel, 10 of 10 empty; 20 separate, all correct.
- **Not caused by D-1:** compiled v1/v2 graphs differ only in bound constants the planner never sees; planner prompt identical; drafts 53/53 (v1) and 53/53 (v2) with no parallel calls.
- **D-3 (new, High):** narrowing turn skipped the search in 6 of 12 runs and answered from history (no links, no true count).
- **Proposed fix (agent script only):** `set_criteria` sets `search_pending`; the search runs deterministically in the instructions; `run_search` removed from planner tools. Scratch compile check passed. Needs publish of v3 to prove (R1–R13).
- **L-1: open, High, release blocker.** Nothing changed, deployed or published. Report: [session-9-d2-diagnosis.md](session-9-d2-diagnosis.md).

## Session 10: D-2/D-3 fix live, v3 active (2026-11-25)

- Agent script only: `set_criteria` marks a search pending; the search runs deterministically with the stored criteria; `run_search` removed from the planner's tools; one instruction line forbids replying from earlier tables.
- Check-only `0AfjV000006mEObSAM` (95/95); quick deploy `0AfjV000006mERpSAM`; published and activated **v3** (`0X9jV000001Dh1lSAC`); v2 inactive for rollback.
- D-2: email search 30/30 on v3 (was 10/30 empty). D-3: narrowing 12/12 (was 6/12 skipped). Pagination, selection, switching, duplicates, field question, guard all pass; agent suite 23/27 (same as v2); Apex 99/99 (`707jV00000CW8dH`); 249/249 links correct; 0 records changed.
- **L-1: open, High, release blocker.** Reproduced 3 of 3 on v3. Report: [session-10-v3-d2-d3-fix.md](session-10-v3-d2-d3-fix.md).

## Session 11: Contact name as the record link (2026-11-25)

- Requested: remove the Record column/line, make the name the record link. Lightning panel pre-deploy test: always linking the name is **unsafe** (escaped names still produced a link to a different Contact, a `javascript:` link and an external image).
- Built (not deployed): Apex payload v4 adds `nameLinkable` and an Apex-built `nameLink` (`[name](contactPath)` for link-safe names, else `name — [Open record](contactPath)`); template copies `nameLink`; no Record line or column. Search logic and security unchanged.
- Check-only `0AfjV000006mGv4SAE`: 98/98, 100% coverage. Template suite 104/108 (4 explained, cosmetic or scorer). Panel injection of 16 real replies: all links correct, nothing injected.
- **L-1: open, High, release blocker** (non-linkable hostile names unchanged under L-1). Awaiting deployment approval. Report: [session-11-name-hyperlink.md](session-11-name-hyperlink.md).

## Session 12: name-link presentation live (2026-11-25)

- Quick deploy `0AfjV000006mJEbSAM` (Apex action, test class, template) from validated `0AfjV000006mGv4SAE`; live on active v3, no new agent version.
- Lightning panel, live: 12 conversations / 20 turns, all search outcomes pass; 36 of 36 record links correct, 7 of 7 navigations open the right Contact; no external, image or dialog.
- Hostile names via the deployed template in the panel renderer: escaped path clean; under L-1 stripping identical to Session 11 and the old format.
- Apex 102/102 (`707jV00000CWnd1`), agent suite 23/27 (same 4), template suite 102/108 (explained), 0 records changed.
- **L-1: open, High, release blocker** (6 of 6 hostile turns in the panel). Report: [session-12-name-link-live.md](session-12-name-link-live.md).

## Knowledge Search: template v5 + v4 gate (2026-11-25)
- `CRA_Knowledge_Answer` v5 active with retriever bound; retrieved to repo. Editor also switched model to GPT-4o mini and altered heading/hidden characters.
- Template v5: facts 27/27, no-match 9/9, **ambiguity 0/9, citation links 1/27**. Agent v4 preview: routing 21/21, Knowledge replies inherit the failures, KT-19 fail.
- Contact regression: Apex 102/102 (`707jV00000CXe9U`), contact_search + read_only_guard byte-identical to v3, v3 Active.
- **v4 NOT deployed or published (gate failed).** L-1 open High; SV-1/3/4 blocked by B-1. Report: [session-kb-v5-validation.md](session-kb-v5-validation.md).

## Knowledge Search: KT-19 fix + v4 published inactive (2026-11-25)
- Agent Script only: new `contact_and_knowledge` subagent, router mixed rule first, knowledge_search handoff. contact_search + read_only_guard byte-identical to v3.
- KT-19 20/20 (+ 8/8 variants); full v4 suite 46/46; Apex 102/102 (`707jV00000CXhyy`); CRA_S6 23/27 (same 4).
- **v4 published Inactive (`0X9jV000001DhubSAC`); v3 Active.** Template v6 unchanged, candidate kept. L-1 open High; SV-1/3/4 blocked by B-1. Report: [session-kb-v4-kt19.md](session-kb-v4-kt19.md).

## Knowledge Search: F-1 root cause + SV-1/SV-3 as restricted user (2026-11-26)
- F-1: "cannot describe data provider" = no default data-space membership. Data space association alone fixes it; Data Cloud User and Data Cloud licences not needed.
- SV-1 pass (no access → no content; all categories → correct citations). SV-3 pass (Campus_Services hidden → Library Fine article 000001007 never returned).
- All temp components deleted, UAT user restored, Login As false (read back). v3 Active, v4 Inactive. L-1 open High. Report: [session-kb-s15-f1-sv1-sv3.md](session-kb-s15-f1-sv1-sv3.md).

## S16 — SV-2 archive test (2026-11-26)
SV-2 pass on synthetic A08 only: archived → 0/6 retrieval (immediately, before and after index sync);
restored and republished as v2 (`ka0jV000000nIqDQAU`) → 6/6 after ~24 min sync. Control KT-05 3/3 throughout.
Only A08 changed. v3 Active / v4 Inactive. L-1 open. Report: `context/session-kb-s16-sv2-archive.md`.

## S17 — release permission sets + regression (2026-11-26)
F-2 fixed: `DATA_Knowledge_Read_Only` Custom visibility, 8 scholarship categories (no Campus_Services). New
`SYS_Knowledge_Default_DataSpace` (default data space only, no permissions), unassigned. Both match the S15 sets that passed.
Template 51/51 (A08 cited as `ka0jV000000nIqDQAU`), v4 suite 46/46, links 13/13, Apex 102/102, v3 suite 22/27 (new
test-only D-4, case 8; real pagination 3/3). v3 Active / v4 Inactive; records unchanged. L-1 open.
Report: `context/session-kb-s17-release-permissions.md`.

## S18 — final validation (2026-11-26)
- D-4 fixed: multi-turn cases 8/15/16 run as real Agent API sessions (evaluation API, version pinned); expectations 17/21/22/23 corrected. Testing Center `CRA_S6_Agent_Tests` = 24 single-turn cases, pinned to v3.
- New D-5 (High): v3 invented the next page in 7/27 two-turn runs; 0/50 on v4. New D-6 (Medium): v4 replied without any action once.
- L-1 investigated: no plain-text panel setting; supported alternatives are "Show in conversation" (no clickable links) or Lightning types (custom LWC, ADR-003). Open.
- Execute Prompt Templates / PSL not needed for agent-run templates (Contact template shown as the restricted user); Knowledge to confirm in plan V-3.
- Regression: v4 27/27, v3 27/27, published v4 Knowledge/mixed/guards 23/23, template 51/51, Apex 102/102, 9/9 links. Snapshot identical to S17.
- Plan: `context/knowledge-search/v4-restricted-user-validation-plan.md`. Report: `context/session-kb-s18-final-validation.md`.

## S19 — v6 paging fix (2026-11-26)
- Decisions: build the D-5 fix first, test inactive, no activation; L-1: file the Salesforce support case first.
- v6 published Inactive (`0X9jV000001DjefSAC`): router `go_show_remaining` → deterministic `contact_page` (D-5); router stores new/narrowed searches (D-6); per-message criteria merged by the script (new D-7, stale criteria, also in v4's mixed request). v5 (`0X9jV000001DjRlSAK`) superseded, Inactive.
- v6: paging 60/60 with 0 invented, edge cases 12/12, stale criteria 9/9, suite 27/27, Knowledge/mixed/guards 23/23, Apex 102/102. v3 Active; records unchanged. No Apex/template/permission change.
- L-1 open (High): support case draft updated, to be filed by a person with a Salesforce Help login.
- Report: `context/session-kb-s19-v6-paging-fix.md`; ADR-K9.

## S20 — Phase A permission comparison on v6 (2026-11-26)
- V-0 pass (evaluation API runs v6 as CRA UAT Restricted). V-1: template steps absent for that user. V-5 debug-log step declined; none created.
- Controlled comparison, identical 33 sessions: without Prompt Template User, `present_results` ran 0/27 and `answer_from_knowledge` was absent 5/5; with the licence + set only, `present_results` 23/23 applicable, 48 links all readable by the user, values match FLS, hidden Contacts never shown, paging and narrowing correct. Knowledge step ran but returned null (no Knowledge sets yet) → generic error.
- Root cause: missing Execute Prompt Templates, not Agent Script. S18 conclusion corrected; minimum-permissions.md updated. New D-8 (High): no fail-closed message when a template step returns nothing.
- Restored and read back: set and licence removed, Log in as off, saved sign-in deleted, 27 assignments, v3 Active / v6 Inactive, 157 Contacts. L-1 open (High).
- Report: `context/session-kb-s20-phaseA-permission-compare.md`; ADR-K10.

## S21–S22 — v7 D-8 fail-closed, regression and restricted-user failure path (2026-11-26)
- v7 published Inactive (`0X9jV000001DkAvSAK`): agent script only. A search or template step that was due but produced nothing shows a fixed failure message and switches the planner's actions off for that turn. Check-only `0AfjV000006no9tSAA` 98/98; 10/10 draft probes.
- v7 regression (admin): suite 27/27, Knowledge/mixed/guards 23/23 (citations 000001004), paging 60/60 with 0 invented, edge cases 12/12, narrowing/new search/mixed 9/9; 0 false failure messages.
- D-8 as CRA UAT Restricted: Config 1 (no Prompt Template User) 18/18 turns show only the fixed messages, nothing invented. Config 2 (Prompt Template User, no Knowledge sets): Contact correct; Knowledge shows the platform's generic error, not the fixed message (new D-8b, Medium, nothing invented). New D-9 (Low): "show the other 3" after a failed display says "no other Contacts".
- Restored and read back (identical to before): Log in as off, set and licence removed, saved sign-in deleted, v3 Active / v7 Inactive, 157 Contacts. L-1 open (High).
- Plan: `context/knowledge-search/v7-restricted-user-phaseA-plan.md`. Report: `context/session-kb-s22-v7-regression-d8.md`.

## S23 — Phase A on v7 as CRA UAT Restricted, all five grants (2026-11-26)
- Passed: 89 sessions / 135 turns (A-1 25/25, A-2 31/31, A-3 71/71, A-4 8/8), A-5 refused, A-6 37/37.
- D-8b not reproduced with all grants (33/33 Knowledge turns returned output); stays Medium for misconfigured users.
- Restored immediately after testing; after-snapshot identical to the baseline. v3 Active, v7 Inactive.
- Open: L-1 (High), permission sign-off (Lal), Phase B panel window, D-8b and D-9 decisions, PR review, release approval.
- Report: `session-kb-s23-v7-phaseA.md`.

## S24 — Phase B Lightning panel window on v7 (2026-11-26 to 27)
- Panel: 14 conversations / 25 turns as CRA UAT Restricted, paired with 14 Agent API sessions: 0 flags; 86 links all internal; 18 linked Contacts all readable; hidden records, Department and Birthdate never shown; edit/publish declined; field instruction not followed; pagination and narrowing correct.
- **L-1 reproduced in the real panel** (3 of 3 hostile single-Contact replies, "LLC" bold; relay drops escaping). Open, High, release blocker.
- **OPS-1 (High, new):** rollback watchdog failed 3 times at 19:14Z (`'result'`, error text not captured); v7 Active 17:47:26Z to 05:22:52Z (11 h 35 min, approved 90 min). Elevated access on about 13 h 37 min. No activation window until rollback is redesigned and tested (ADR in `decisions/2026-11-27-…`).
- D-8b and D-9 not tested (skipped by decision).
- Restored 2026-11-27 07:04Z and read back, identical to baseline: v3 Active / v7 Inactive, Log in as off, 4 sets and licence removed, saved sign-in deleted, `SYS_Lightning_Experience_User` deployed and unassigned.
- Report: `session-kb-s24-v7-phaseB.md`. Incident: `knowledge-search/incident-2026-11-26-v7-window-overrun.md`.

## S25 — finalisation for review (2026-11-27, documentation only)
- No test cycle re-run; uses S24 evidence (`412eb69`). No org change: v3 Active, v7 Inactive, UAT user on its 4 original sets (read back).
- L-1 Salesforce case ready for manual filing: `knowledge-search/L-1-salesforce-support-case.md`, with trace excerpt `evidence/s24-v7-phaseB/L-1-trace-excerpt.json` (template output escaped → final model step output unescaped, 3 of 3 turns). **Not filed** (no Salesforce Help connection). Case number: _pending_.
- OPS-1 controls C1–C7 specified: `knowledge-search/OPS-1-activation-gate.md`. No window scheduled.
- Consolidated release review: `RELEASE-REVIEW-SCGOE-95-KB.md`. Handover: `HANDOVER-Lal-2026-11-27.md`.
- **L-1 open (High, release blocker); OPS-1 open (High).** Release not approved; nothing merged.

## S25 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): L-1 fix, OPS-1 build
- Recovered state: HEAD `7910f6c` = PR #7 head, no uncommitted work; v3 Active, v7 Inactive, Employee_Leave_Assistant v1 Active.
- Decisions (Nagaruri Johnson): L-1 neutralise in Apex; OPS-1 build all; alerts GitHub issue + e-mail; D-8b/D-9 accept.
- **L-1 fixed:** look-alike display characters. Validation `0AfjV000006owwbSAA` 88/88, 166/166 lines; deploy `0AfjV000006ox1RSAQ`. Agent API on published v3: 4/4 turns clean, table columns intact. Panel check as a restricted user pending.
- **OPS-1 built:** `ops/agent-rollback/` (script, mock tests 10/10, window example, backstop), workflow file `ops/agent-rollback/agent-rollback.workflow.yml` (not installed in `.github/workflows/`: token lacks `workflow` permission), permission set `SYS_Agent_Rollback_Automation` (deploy `0AfjV000006oxnpSAA`), integration user `005jV000003ufYDQAY` with PSL and set. Connected app template ready; needs the certificate. Runbook `knowledge-search/OPS-1-rollback-runbook.md`.
- D-8b, D-9 accepted (pending Lal).
- Open: certificate + secrets → live T1/T2/T5 → OPS-1 sign-off; panel check for L-1; Lal decisions; PR review; release approval.

## S26 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): L-1 live hostile-data check, OPS-1 readiness
- v3 Active, v7 Inactive before and after. No activation, no permission change, nothing merged.
- Synthetic Contact `003jV00000HOooHQAT` CRA-TEST Mallory created (approved), Title then changed on that record only. Agent API on published v3: 2 sessions, 4 turns, all clean (links, `javascript:`, backticks, bold, heading, strike, underscores); traces show `contact_search` → `search_contacts` → `present_results`, no errors. Evidence `evidence/s26-l1-live/`.
- OPS-1: rollback user and permission set verified minimal. Connected app not deployed (no certificate). GitHub: no `agent-rollback` environment, no installed workflow, secrets not readable by the token. T1/T2/T5 not run.
- Record: `knowledge-search/session-kb-s26-l1-live-ops1-status.md` (manual steps, panel plan P-1 to P-5).

## S27 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): requirements trace, OPS-1 environment check

- Read back: v3 Active, v7 Inactive, Employee_Leave_Assistant untouched; 14 articles (13 Online, 1 Draft); library and templates present.
- Knowledge requirements traced to existing evidence; Account ID search judged out of scope (decision record).
- OPS-1: environment `agent-rollback` exists but deployment branches = `main` only (defect; runbook step 3 corrected). No certificate, connected app or installed workflow; live T1/T2/T5 not run.
- No org change, no test run, no activation. Record: `knowledge-search/session-kb-s27-requirements-trace.md`.

## S28 — 2026-11-27 — Salesforce org verification (org only)

- Read back: v3 Active, v7 Inactive, Employee_Leave_Assistant untouched; 14 articles (13 Online, 1 Draft; 000001011 v1 Archived); no expiring grants; no connected app.
- v7 script, `CRA_Knowledge_Answer`, category group: org = repo. Data space scope added to the repo permission set (check-only `0AfjV000006p3y5SAA`); other permission sets and the presentation template synced from the org.
- Connected-app template: scope Api only, schema order; check-only without certificate `0AfjV000006p4CbSAI`. Certificate not received, deploy pending.
- L-1: `CRA_ContactSearchActionTest` 35/35, 100% of 166 lines (run `707jV00000ChBON`). No activation, no assignment, no business-record change.
- Record: `knowledge-search/session-kb-s28-org-verification.md`.

## S29 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): Contact record Id search (ID-1)
- Root cause: Agent Script bound `contactId = ""` and had no input for a typed Id. Apex already supported 15/18-character Contact Ids in user mode; unchanged.
- Fix: `in_contact_id` / `criteria_contact_id` variables, three new-search actions, two search bindings, instructions. `sf agent validate` passes.
- Draft preview with live read-only actions, 6 of 6 pass (18-char, 15-char field ask, Account Id rejected, no-match, name regression, combined Contact Id + Knowledge). Traces error-free.
- Not published, deployed or activated. v3 Active, v7 Inactive. Next: approval to publish v8 inactive; Account Id search needs Lal's scope approval.
- Record: `context/knowledge-search/session-kb-s29-contact-id-search.md`.

## S29b — 2026-11-27 (AGENTFORCE_BUILD 27f29662): v8 reviewed, corrected, tested, published Inactive
- Review of v7→v8: 7/7 PASS. Correction: a Contact Id must contain a letter; digits-only values are phone numbers (`3c7337f`, 6 lines).
- Targeted draft-preview turns with live read-only actions: 10/10 PASS, inputs confirmed in action traces, no errors. D-10 (Low, pre-existing): combined route searches twice.
- `sf agent publish authoring-bundle`: v8 Inactive; v3 Active, v7 Inactive, Employee_Leave_Assistant v1 unchanged; org bundle byte-identical to repo. Nothing activated, no Apex, permission or record change.

## S30 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): requirements matrix, AID-1, Case design
- Decisions (Nagaruri Johnson): Case creation design only, wait for Lal; confirmation UI verify then fall back; Lal approved Account Id → its Contacts only; no synthetic writes.
- AID-1: `accountId` input (Criteria, FieldAccess, Service, Action) + 11 new tests; validate `0AfjV000006pBkLSAU`, deploy `0AfjV000006pBlxSAE`, suggestion fix `0AfjV000006pByrSAE`; 99/99, 100% coverage; org = repo.
- Agent Script: `in_account_id` / `criteria_account_id`, 3 new-search actions, 2 searches + paging, follow-up sends "", instructions. `sf agent validate` passes. 9/9 draft-preview turns (live read-only actions), traces error-free. Not published.
- Case creation: `case-create-design.md` + proposed decision; nothing built, no Case created, no permission changed.
- v3 Active; v1–v2, v4–v8 Inactive. Record: `knowledge-search/session-kb-s30-requirements-aid1-case-design.md`.

## S31 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): v9 published Inactive

- Pre-publication checks: v9 script contains ID-1 + AID-1, unchanged since the S30 tested commit, compiles; Account Id path reads only Account Id in user mode; deployed Apex identical to repo (7/7 classes).
- `sf agent publish authoring-bundle` → v9 Inactive. Readback: v3 Active, v1–v2 and v4–v9 Inactive, Employee_Leave_Assistant v1 unchanged; published script byte-identical to repo; planner schema has `accountId` in all 3 search actions.
- Case creation: design only; placement inside Contact_Read_Agent recorded; decisions C-1 to C-6 for Lal. No Case actions, permissions or test Cases.
- Record: `knowledge-search/session-kb-s31-v9-publish.md`. Not release-ready (OPS-1, L-1 panel check).

## S32 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): Case creation, v10 published Inactive

- Lal's exception recorded (Case creation only). Deployed `CRA_Case_Create`, `DATA_Case_Create`, `SUB_Case_Draft_Validate`, `SUB_Case_Create_Confirmed`; `case_create` subagent in Agent Script.
- `DATA_Case_Create` assigned to admin John Steve for tests, then removed (0 assignments). Tests C1–C6 + R1 pass, traces error-free; 1 synthetic Case 00001026; F-1 fixed.
- v10 published Inactive; v3 Active; Employee_Leave_Assistant unchanged; published script = repo. Record: `knowledge-search/session-kb-s32-case-create-v10.md`. Not release-ready.

## S33 — 2026-11-27 (AGENTFORCE_BUILD 27f29662): Case Flow security correction

- S33-F1: Case Flows (system mode with sharing) gated only on `CRA_Case_Create`; proven bypassable by test (old Flows created a Case for a user without Priority Edit). Latent: 0 holders.
- Fix: new `SUB_Case_Create_Access_Check` (reads active assignments' Object/Field permissions, fails closed); both Case Flows v2 call it. Test-only class `CRA_CaseCreateFlowSecurityTest` 4/4 (validate `0AfjV000006pI13SAE`, deploy `0AfjV000006pI7VSAU`).
- Agent smoke on v10 script: refusal via the new check, no errors, Cases 27. v3 Active, v10 Inactive, no version published, no assignment. Panel/restricted agent run still open. Record: `knowledge-search/session-kb-s33-case-security.md`.

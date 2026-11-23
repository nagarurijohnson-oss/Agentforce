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

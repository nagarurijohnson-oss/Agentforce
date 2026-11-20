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
| Session 4: Prompt Builder template | Not started | Action deployed and contract confirmed. Confirm integer/boolean template inputs (review M2) |
| Session 5: Agent Script agent | Not started | Published inactive. Not activated |
| Session 6: Evaluation, UAT and handover | Not started | Activation and merge need explicit approval |

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

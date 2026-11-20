# Implementation progress

Update this file at the end of every build session. A status here is a dated claim: check it against the repository and the org before relying on it.

| Item | Status | Notes |
|---|---|---|
| Repository seeded with context files | In review | Pull request #1 from scgoe-95-context |
| Functional requirements and search outcome decisions | Recorded 2026-11-19 | See requirements-status.md. No attachment needed |
| Technical design and build prompts | Ready for review | technical-design.md and build-prompts/ on this branch |
| Session 1: Foundation and environment gate | Gate done 2026-11-19 (read-only). No blocker | See session-1-environment-gate.md. Scaffold and permission sets deferred to S2/S3 on instruction (no metadata changes) |
| Session 2: Search engine (Apex service, tests) | Built 2026-11-19; review fixes 2026-11-20, validated check-only. **Not deployed**, PR #2 not merged | Branch `feature/scgoe-95-s2-search-engine`. Validation 0AfjV000006e22sSAA: 9 components, 48 of 48 tests, 100% coverage on all 4 classes. Permission sets `DATA_Contact_Read_Only` and `APP_Contact_Read_Agent` in source only, not assigned. See session-2-review-fixes.md |
| Session 3: Invocable action and security hardening | Ready to start after PR #2 review (not started) | Field access, FILTER_UNAVAILABLE, "Not available", links and ERROR are already in the service (pulled forward in S2). S3 adds the invocable wrapper, the static no-DML test, class access and the first deploy (needs approval) |
| Session 4: Prompt Builder template | Not started | Can start once the action contract is agreed |
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

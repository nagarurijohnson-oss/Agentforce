# Session 7: D-1 fix ("show the remaining Contacts"), proposed for review

**Date:** 2026-11-23 · **Ticket:** SCGOE-95 · **Org:** 00DjV000003BVbRUAW (Developer Edition)
**Status: fix built and validated check-only. Not deployed, not published.** Deployment and agent version 2 need approval.
**L-1 stays open: High, release blocker.** This fix does not touch it.

## Root cause

- The `show_remaining` route in `Contact_Read_Agent.agent` bound the eight stored criteria and `showRemaining = True`, but left `contactId`, `requestedField` and `location` **unbound**. The planner may fill unbound inputs, and in Session 6 it passed the first row's Id (`003jV00000GrntJQAR`).
- `CRA_ContactSearchService.buildPlan` turns any `contactId` into `Id = :contactIdValue`, which is ANDed with the criteria. The count collapses to 1, so the result becomes `SINGLE_MATCH` for that Contact instead of `REMAINING_PAGE`.
- `run_search` had the same gap for `contactId` and `location`. Session 5 traces show the planner filling `location` on its own, which a replay could not reproduce.

## Fix (two layers, either one alone stops D-1)

| Layer | File | Change |
|---|---|---|
| Agent script | `aiAuthoringBundles/Contact_Read_Agent/Contact_Read_Agent.agent` | `run_search`: bind `location = ""`, `contactId = ""`. `show_remaining`: bind `location = ""`, `contactId = ""`, `requestedField = ""`, and clear `selected_contact_id` (the list on screen changed). `ask_about_selected`, `select_contact`, instructions, variables and the presentation step are unchanged. |
| Apex guard | `CRA_ContactSearchCriteria.validate()` | When `showRemaining` is true, `contactId` and `requestedField` are dropped before validation. With nothing else to search by, the request returns `NEEDS_CLARIFICATION` and shows no Contact. |

Unchanged: the search service, the action contract (`toCriteria` still copies every input), `CRA_FieldAccess`, the Prompt Template `CRA_Contact_Result_Presentation`, permission sets, sharing and record links.

**Behaviour note:** `location` is now only searched through the stored city, state and country criteria. The Apex `location` input itself still works. In every recorded trace the planner set `city` alongside `location`.

## Validation (all check-only; nothing saved)

| Check | Id | Result |
|---|---|---|
| Fix + tests, CRA test classes | `0AfjV000006ipD3SAI` | 85 of 85 pass, 0 errors; `CRA_ContactSearchCriteria` coverage 100% (168 of 168 lines) |
| Full regression, RunLocalTests | `0AfjV000006ipTBSAY` | 95 of 95 pass across 7 test classes, 0 errors |
| Negative proof: new tests against the org's current (unfixed) class | `0AfjV000006ipRZSAY` | 4 of 4 D-1 tests **fail** with the D-1 symptom (`SINGLE_MATCH` / `FIELD_ANSWER` / `NO_MATCH`); the control test passes |
| Agent script compile (`sf agent validate authoring-bundle`) | n/a | success, no warnings |
| Live read-only preview of the local draft bundle (org still runs the unfixed Apex) | sessions `01a20879-0846…`, `01a20879-7bea…` | Pass: see below |

New tests:
- `CRA_ContactSearchTest.remainingIgnoresFirstRowContactIdD1`: the Session 6 trace exactly; rows 6–10, no single Contact.
- `CRA_ContactSearchTest.remainingIgnoresStaleContactIdAndFieldD1`: a selected Contact from outside the list plus a field question.
- `CRA_ContactSearchTest.remainingWithOnlyContactIdNeedsClarification`: Id alone with showRemaining shows no one.
- `CRA_ContactSearchTest.contactIdStillAppliesWithoutRemaining`: control; follow-up questions by Id are unchanged.
- `CRA_ContactSearchActionTest.remainingIgnoresStrayContactIdD1`: the same through the invocable action.

### Conversation check (draft bundle, live read-only actions, synthetic Contacts)

| Scenario | Turn | `search_contacts` input | Outcome |
|---|---|---|---|
| D1_original | "Find Synthetic Engineer contacts at CRA-TEST Northwind Synthetic" | criteria, `contactId: ""` | LIST_6_TO_10, 8 |
| | "Yes, show me the other 3" | same criteria, `contactId: ""`, `requestedField: ""`, `showRemaining: true` | **REMAINING_PAGE**: rows 6–8 (Eng Mockup06–08), 3 record links, relayed verbatim |
| D1_after_selection | search, then "Tell me about number 2" | `contactId: 003jV00000GrntKQAR` | SINGLE_MATCH (follow-up still works) |
| | "Now show me the other 3" | `contactId: ""`, `showRemaining: true` | **REMAINING_PAGE**: rows 6–8, 3 links |

Session 6 result for the same turn: one wrong Contact (Eng Mockup01). Transcripts: `scripts/scgoe-95/s7-d1-fix/`.

## To go live (needs approval)

1. Quick-deploy validated job `0AfjV000006ipD3SAI` (Apex guard + tests). Not irreversible; a Developer Edition org.
2. Deploy the updated `AiAuthoringBundle`, then `sf agent publish authoring-bundle` (creates version 2) and `sf agent activate --version 2`. Version 1 stays available for rollback.
3. Rerun the agent test suite `CRA_S6_Agent_Tests` against v2; case 8 should now pass. Re-check L-1 on v2 (expected still open).

## Open items

| ID | Severity | Status |
|---|---|---|
| **L-1** | **High, release blocker** | Open. Support case not yet filed. |
| D-1 | Medium | Fixed in branch, validated; awaiting deploy + v2 approval |
| B-1 | Blocker for panel UAT | Open (Log in as disabled) |
| N-1 | Low | Note, unchanged |

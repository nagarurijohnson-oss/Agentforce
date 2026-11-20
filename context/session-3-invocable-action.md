# Session 3 — invocable action (SCGOE-95)

**Date:** 2026-11-20 · **Run by:** Revecast Orchestrate for Nagaruri Johnson · **Branch:** `feature/scgoe-95-s3-action` (from `feature/scgoe-95-s2-search-engine` at `eb7d78c`)

**Nothing was deployed.** The org was used only for check-only validations (tests run and roll back). No permission set was assigned, no sharing setting, user or agent was changed, and no pull request was merged. The first real deploy needs approval.

A status here is a dated claim. Check it against the repository and the org before relying on it.

## Validation (check-only, org `orgfarm-232477b490-dev-ed`)

| Property | Value |
|---|---|
| Id | **0AfjV000006e70xSAA** (final, read back from the org as DeployRequest) |
| Result | Succeeded, `CheckOnly = true`, 2026-11-20 10:25:47–10:26:30 UTC |
| Components | 11 of 11, 0 errors: 9 Apex classes, `APP_Contact_Read_Agent`, `DATA_Contact_Read_Only` |
| Test level | RunSpecifiedTests: `CRA_ContactSearchActionTest`, `CRA_ContactSearchTest`, `CRA_ContactSearchSecurityTest` |
| Tests | 72 of 72 passed (Action 24, Search 37, Security 11) |
| Coverage | 100% on every production class: `CRA_ContactSearchAction` 64/64, `CRA_ContactSearchService` 415/415, `CRA_ContactSearchCriteria` 162/162, `CRA_ContactSearchResult` 15/15, `CRA_FieldAccess` 15/15 |

No source changed after this run; it is the code committed with this report.

All validation runs this session (the org's Ids are not in time order):

| Id | Result | Why |
|---|---|---|
| 0AfjV000006eEK9SAM | Failed to compile | `@InvocableMethod` description used `+` concatenation; annotation values must be single literals |
| 0AfjV000006eELlSAM | 2 test failures | Both in the new test code: the DML count was read for the whole test, and the scanner counted `database . delete` twice. Fixed in the tests |
| 0AfjV000006eEOzSAM | Succeeded, 72/72 | First clean run |
| 0AfjV000006eBKgSAM | Failed, as intended | Mutation: `insert new Account(...)` added to `CRA_ContactSearchAction`. `noDmlInAnyProductionClass` failed with `{CRA_ContactSearchAction=(insert n)}`. Reverted |
| 0AfjV000006e70xSAA | Succeeded, 72/72 | Final run on the reverted, committed code |

After the runs the org still has 0 `CRA_` classes, none of the permission set names, and no record created by the mutation.

## What was built

| Component | Change |
|---|---|
| `CRA_ContactSearchAction` (new) | `@InvocableMethod searchContacts(List<Request>)`, label "Search Contacts (Contact Read Agent)", category "Contact Read Agent". A thin adapter: maps each `Request` onto `CRA_ContactSearchCriteria`, runs them all through `CRA_ContactSearchService.searchAll` in one call, and maps each `CRA_ContactSearchResult` onto a flat `Response`, in order. `with sharing`, no queries of its own, no DML. Any unexpected failure returns the sanitised ERROR for every request. Every input and output has a label and a description for Agentforce |
| `CRA_ContactSearchActionTest` (new) | 24 tests (below) |
| `APP_Contact_Read_Agent` | Gains Apex class access to `CRA_ContactSearchAction` only. Still no object or field access. Not assigned |
| Search service, criteria, result, field access, factory, Session 2 tests | **Unchanged** (git diff is empty for them). No defect was found that needed a change |

### Contract mapping

Inputs (12): `name`, `email`, `phone`, `accountName`, `jobTitle`, `city`, `stateOrRegion`, `country`, `location`, `contactId`, `requestedField`, `showRemaining` (Boolean). All optional.

Outputs (15): `outcomeCode`, `totalMatchesLabel`, `shownCount` (Integer), `remainingCount` (Integer), `canShowRemaining` (Boolean), `refinementRequired` (Boolean), `similarNameCount` (Integer), `suggestedFiltersText`, `duplicateOn`, `requestedFieldLabel`, `criteriaSummary`, `userMessage`, `singleContactId`, `resultContactIds`, `contactsJson`.

`singleContactId` is a Text output (the 18-character Id, or empty), so Agent Script and the template receive plain text. Strings the service leaves unset stay empty (null). On ERROR and NEEDS_CLARIFICATION `contactsJson` is `[]`.

Every value comes from the service result, which holds only what the running user can read: rows, counts, duplicate checks and links come from USER_MODE queries under `with sharing`. The adapter adds nothing.

### Bulk

One call runs every request through `searchAll`, which caps a call at 10 requests and checks the query budget (unchanged, approved in Session 2). Each request uses at most 3 queries. A call with more than 10 requests (for example a bulk Flow batch of 200) gets one response per request in the same order: the first 10 are searched and the rest return the sanitised ERROR. Agentforce sends one request per call.

## Tests (`CRA_ContactSearchActionTest`, 24)

| Area | Tests | Proves |
|---|---|---|
| Contract and mapping | `contractNamesMatchTechnicalDesign`, `requestMapsEveryInput`, `responseMatchesServiceResultFieldByField` | Request and Response carry exactly the 12 and 15 contract names; row keys are within the contract; every input is copied unchanged; for 8 outcome shapes every one of the 15 outputs equals the service result |
| Outcomes | `everyOutcomeInOneCallInOrder`, `remainingPageReturnsTheRest`, `blankValuesReadNotAvailable`, `phoneSearchFindsMobileNumber`, `hostileFieldValueIsCarriedAsData` | All 12 outcome codes through the action (ERROR, FILTER_UNAVAILABLE, REMAINING_PAGE in their own tests); flags for 2–5, 6–10, 11–100 and TOO_MANY; duplicates never select a Contact; email domain is never a duplicate; a field answer carries only n, id, name, link and the field; "Not available"; a hostile Title stays data |
| Links | `recordLinksAndResultIds` | Each row links to its own Contact on the My Domain URL; `resultContactIds` lists exactly the rows shown |
| Bulk and limits | `bulkCallOf200StaysWithinLimits`, `requestsBeyondTheCapReturnError`, `emptyAndNullListsReturnEmpty` | 200 requests: 200 responses in order, 10 searched, 190 ERROR, at most 30 queries, 0 DML; position of the cap; empty and null lists |
| Invalid and hostile input | `invalidInputsNeedClarification`, `injectionPayloadsReturnNoRows` | 8 invalid inputs (no filter, bad phone, malformed and non-Contact Id, unknown field, 6 name words, 81-character email, "@@") return NEEDS_CLARIFICATION with no rows; 6 injection payloads return no rows and no error |
| Errors | `failuresReturnSanitisedError` | A forced failure in the service and one in the adapter both return ERROR with the fixed message, `[]`, and no class name, exception type or Contact data |
| **Real enforcement** | `enforcedBaselineAdminSeesPrivateContacts`, `enforcedRecordSharingLimitsRowsCountsAndLinks`, `enforcedFieldSecurityHidesValuesAndFilters`, `enforcedNoContactAccessReturnsNeutralNoMatch` | Restricted users that exist only in the test. A user holding only `DATA_Contact_Read_Only` (assigned inside the test, rolled back): a private Contact by name, exact email or Id gets the same NO_MATCH as a Contact that does not exist; a 3-visible + 3-private set counts 3 (admin sees 6), and no private Id appears in rows, links or `resultContactIds`. A user without Email, Phone and MobilePhone FLS: those values read "Not available" and appear nowhere in the rows, and filtering on them is FILTER_UNAVAILABLE. A user with no Contact access: NO_MATCH by name and by Id |
| Simulated | `simulatedAccountNameUnreadableThroughAction` | A substitute access check through the action's service seam (Account name unreadable cannot be built with a real user here). Proves how the code reacts, not Salesforce enforcement |
| Permission sets (real metadata) | `appPermissionSetGrantsOnlyActionClassAccess` | APP grants Apex class access to `CRA_ContactSearchAction` and no other class, object or field; DATA grants no class access; neither has any assignment |
| Static no-DML | `dmlScannerDetectsDmlAndIgnoresNonCode`, `noDmlInAnyProductionClass` | The scanner flags 11 DML forms and ignores DML words in comments, strings and identifiers. The deployed bodies of all 5 `CRA_` production classes contain no DML; the test also fails if the set of production classes changes. Shown to fail by the mutation run above |
| Platform invocation | `platformInvocationUsesContractNames` | Called through the invocable framework by class name (`Invocable.Action`, as Flow and `apex://` do), the action takes the contract input names and returns the contract output names |

## Acceptance criteria (build prompt S3)

| # | Criterion | Outcome |
|---|---|---|
| 1 | Output fields match the contract exactly | Met: `contractNamesMatchTechnicalDesign`, `platformInvocationUsesContractNames` |
| 2 | Blank and unreadable values are "Not available"; no unreadable value anywhere | Met: `blankValuesReadNotAvailable`, `enforcedFieldSecurityHidesValuesAndFilters` |
| 3 | NO_MATCH identical whether nothing exists or nothing is accessible | Met: `enforcedRecordSharingLimitsRowsCountsAndLinks`, `enforcedNoContactAccessReturnsNeutralNoMatch` |
| 4 | Forced exception returns ERROR with no stack trace or class names | Met: `failuresReturnSanitisedError` |
| 5 | Unreadable `contactId` returns the neutral NO_MATCH | Met: same two enforced tests |
| 6 | Requested-field answers contain only the field, the name and the link | Met: `everyOutcomeInOneCallInOrder` (keys n, id, name, contactUrl, field) |
| 7 | Static no-DML test passes, and fails when DML is added | Met: final run passes; mutation run 0AfjV000006eBKgSAM fails |
| 8 | Coverage at least 90% | Met: 100% on all 5 production classes |
| — | Class access on `APP_Contact_Read_Agent` | Met in source and proven in metadata; enforcement at the agent entry point is proven in S5/S6 |
| — | First deploy | **Not done**, as instructed. Needs approval |

## Deviations and choices

- **Fallback messages stay hard-coded English.** The build prompt suggested Custom Labels. Moving them would change the approved service, and nothing was broken, so it is deferred.
- **`singleContactId` is Text**, not an Id-typed output, so Agent Script and the template get plain text.
- **Class access only on the action.** The classes it calls (service, criteria, result, field access) need no class access, so none is granted (least privilege).

## Outstanding limitations

- **Class access at runtime is not yet proven.** Apex calling Apex in a test does not check class access, so the tests prove the grant exists in metadata. That a user without `APP_Contact_Read_Agent` is refused, and one with it is allowed, is proven when the agent runs (S5) and in UAT (S6).
- **Bulk beyond 10 requests per call** returns ERROR for the extra requests. Fine for Agentforce (one request per call); a Flow that sends more than 10 at once is not supported.
- **The Prompt Template hand-off** (S4/S5) and **a live chat as a restricted user** (S6) are still unproven.
- Carried from Session 2: name, phone, email-domain and location matching limits; English-only messages; service class size and test hooks; selectivity accepted as a risk (see session-2-review-fixes.md).
- **Permission sets are not assigned.** A non-admin user needs both `DATA_Contact_Read_Only` and `APP_Contact_Read_Agent`, assigned manually after approval.

## Next

1. Review this branch (pull request needs approval).
2. First deploy of the 11 components with `RunSpecifiedTests` on the three `CRA_` test classes, after approval.
3. Session 4: the prompt template, using the output names, types and guardrail above.

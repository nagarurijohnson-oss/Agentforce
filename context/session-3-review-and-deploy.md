# Session 3 review and first deploy (2026-11-20)

Review of commit `7e094a8` on `feature/scgoe-95-s3-action`, then the first deploy of the validated `CRA_` components to the Developer Edition org. Requested by Nagaruri Johnson.

## Target org

| Check | Result |
|---|---|
| Org Id | `00DjV000003BVbRUAW` (MAX) |
| Type | Developer Edition, `IsSandbox = false` |
| CLI alias | `orgfarm-232477b490-dev-ed` |

## Review results

### 1. Apex class access on `APP_Contact_Read_Agent`

**Confirmed.** At `7e094a8` the permission set has `<classAccesses>` for `CRA_ContactSearchAction` (`enabled = true`), and that is the only change to the file since `eb7d78c`. After the deploy the org has exactly one `ApexClass` grant on `APP_Contact_Read_Agent`: `SetupEntityId 01pjV000005FisIQAS`, which is the Id of `CRA_ContactSearchAction`. `DATA_Contact_Read_Only` has no class grants. APP has no object or field permissions.

### 2. Implementation report and the automated access-wiring warning

The automated status at the end of the Session 3 run said Apex class access was "NOT wired". That does not match the commit: the grant is in the committed file, the validation test `appPermissionSetGrantsOnlyActionClassAccess` reads the grant back from `SetupEntityAccess` and passed, and the deployed org now holds the grant (above). The report was right and the warning was wrong for this commit. The check that produced the warning cannot be inspected from the session, so its cause is not recorded here.

### 3. Action contract vs the planned Prompt Template

Read from the deployed action (`/actions/custom/apex/CRA_ContactSearchAction`):

- Label "Search Contacts (Contact Read Agent)".
- 12 inputs: name, email, phone, accountName, jobTitle, city, stateOrRegion, country, location, contactId, requestedField, showRemaining.
- 15 outputs: outcomeCode, totalMatchesLabel, criteriaSummary, userMessage, suggestedFiltersText, duplicateOn, requestedFieldLabel, singleContactId, resultContactIds and contactsJson (all text); shownCount, remainingCount and similarNameCount (integer); canShowRemaining and refinementRequired (boolean).

These match `technical-design.md` and the S4 build prompt. Everything the template needs to choose a format block and render the rows comes from the outputs: the outcome code, the counts, the refinement and paging flags, the record links in `contactsJson`, and the fallback text. Nothing has to be looked up again. **Open for S4:** confirm how the template takes the integer and boolean outputs (see M2).

### 4. The 10-request limit

`CRA_ContactSearchService.searchAll` searches the first `MAX_REQUESTS_PER_CALL` (10) requests. Every later request, and any request once fewer than 3 queries remain, gets its own ERROR result at the same position. There is no truncation: the response list always has one entry per request, in order. Proven by `requestsBeyondTheCapReturnError` (12 requests: index 9 answered, 10 and 11 ERROR) and `bulkCallOf200StaysWithinLimits` (200 responses; 10 answered, 190 ERROR, at most 30 queries, no DML). See M1 for the wording.

### 5. Validation

| Run | Type | Result |
|---|---|---|
| `0AfjV000006e70xSAA` | Check-only (Session 3) | Succeeded, 11/11 components, 72/72 tests, read back from the org |
| `0AfjV000006e5IUSAY` | Check-only, fresh, from a clean checkout of `7e094a8` | Succeeded, 11/11 components, 0 errors, 72/72 tests, 100% coverage on all 5 production classes |
| `0AfjV000006eF6XSAU` | **Deploy** (quick deploy of `0AfjV000006e5IUSAY`) | Succeeded, 11/11 components, 0 errors |

A quick deploy reuses the test run of the validation it names, so it runs no tests of its own. The deployed components are exactly the ones validated, from `7e094a8`.

## Findings

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 2 |
| Low | 3 |

- **M1. Requests over the cap read like a real failure.** (`CRA_ContactSearchService.searchAll`, `buildError`.) The ERROR is explicit and in position, but `userMessage` is the general "Something went wrong… Please try again", so a Flow caller cannot tell "too many requests" from a fault, and retrying the same batch fails the same way. Agentforce sends one request per call, so the agent never reaches this. Fix, if a Flow caller is ever planned: a distinct outcome (for example `REQUEST_LIMIT_EXCEEDED`) and message. That changes the approved service, so it was not changed here.
- **M2. Template input types still to confirm.** (`CRA_ContactSearchAction.Response`.) Three outputs are integers and two are booleans. S4 must confirm how the Prompt Template receives non-text values from Agent Script. If it needs text, pass the values as text there; no Apex change is expected.
- **L1. Adapter-level ERROR leaves numbers and flags empty.** (`CRA_ContactSearchAction.errorResponses`.) The service ERROR returns 0 and false; the adapter's own error path leaves `shownCount`, `remainingCount`, `similarNameCount`, `canShowRemaining` and `refinementRequired` null. It is only reached on an unexpected failure inside the adapter. The template should treat a missing number as 0 and a missing flag as false, or the adapter can set them in a later change.
- **L2. A test will fail after the permission sets are assigned.** (`CRA_ContactSearchActionTest.appPermissionSetGrantsOnlyActionClassAccess`.) It asserts that neither permission set has an assignment, so any later deploy that runs it will fail once UAT users are assigned. Relax that assertion before assignment in S6.
- **L3. Class access is not proven at runtime yet.** Apex calling Apex in a test does not check class access. Refusal without APP and success with it are proven when the agent runs (S5) and in UAT (S6).

The review found nothing that blocked the deploy.

## Deployed and verified in the org

| Component | Verified |
|---|---|
| 9 Apex classes: `CRA_ContactSearchAction`, `CRA_ContactSearchActionTest`, `CRA_ContactSearchCriteria`, `CRA_ContactSearchResult`, `CRA_ContactSearchSecurityTest`, `CRA_ContactSearchService`, `CRA_ContactSearchTest`, `CRA_FieldAccess`, `CRA_TestDataFactory` | `ApexClass`: all Active, `IsValid = true`, API 68 |
| `APP_Contact_Read_Agent` | Class access to `CRA_ContactSearchAction` only; no object or field permissions |
| `DATA_Contact_Read_Only` | Read on Account and Contact (no create, edit, delete or View All); read-only FLS on Contact AccountId, Email, MailingAddress, MobilePhone, Phone, Title |
| Assignments | 0 for both permission sets |
| Invocable action | Registered, with the 12 inputs and 15 outputs above |
| Tests against the deployed code | Run `707jV00000C0w5U`: 72/72 test methods passed (24 + 37 + 11), 100% coverage on all 5 production classes. The runner reports 75 because it also counts the three `@testSetup` methods |

Not done, as instructed: no permission set assignment, no sharing change, no agent change, no merge, Session 4 not started.

## Pull request

Draft PR #3, `feature/scgoe-95-s3-action` into `feature/scgoe-95-s2-search-engine`.

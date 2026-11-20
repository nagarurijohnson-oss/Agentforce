# SCGOE-95 technical design (2026-11-19)

Status: proposed, for review. Full narrative, evidence table and risks are in the design document delivered with the design session.

**Environment (corrected 2026-11-19):** personal Developer Edition org `MAX` (00DjV000003BVbRUAW), API 68.0, production-type, not a sandbox. Every deploy runs Apex tests: use `RunSpecifiedTests` on the `CRA_` test classes. Session 1 gate results: [session-1-environment-gate.md](session-1-environment-gate.md).

## Architecture

Agent Script (conversation, state) → `apex://CRA_ContactSearchAction` (search, validation, duplicates, classification) → prompt template `CRA_Contact_Result_Presentation` via `generatePromptResponse://` (presentation only). Native Agentforce panel. No LWC, no DML.

Session 1 confirmed with the org's Agent Script compiler (2026-11-19): block keyword `subagent`, `agent_type: "AgentforceEmployeeAgent"` without `default_agent_user`, `target: "apex://CRA_ContactSearchAction"` (class name only), and `target: "generatePromptResponse://CRA_Contact_Result_Presentation"` with quoted `"Input:<apiName>"` inputs and a `promptResponse` output. The compiler does not check that the class or template exists; publishing in Session 5 does.

## Decisions

| ID | Decision | Status |
|---|---|---|
| D-A | Agent type is Employee agent, because it runs as the chatting user. Agent Script compiles an Employee agent in this org (Session 1). Run-as-user is confirmed at runtime in Session 5 | Verified (compile) |
| D-B | Exact full-name matches take priority (near matches counted in `similarNameCount`). Two or more exact name matches, an exact email address, or a phone (Phone or MobilePhone) matching 2 or more = DUPLICATE_IDENTIFIER. Never selects a Contact. Email domain searches are never duplicates. See decisions/2026-11-20-d-b-… | Accepted 2026-11-20 |
| D-C | 11–100 matches (duplicates too): first five, `refinementRequired`, `remainingCount = 0`, no "show more". Only 6–10 sets `canShowRemaining`. See decisions/2026-11-20-d-c-… | Accepted 2026-11-20 |
| D-D | Missing and unreadable values both read "Not available" (retained) | Accepted 2026-11-20 |
| D-E | Contact OWD is Controlled by Parent, and Account OWD is Public Read/Write (corrected in Session 1). Keep both. Prove record-level security with Contacts that have no Account: they are private to their owner. Use them in `System.runAs` tests and in UAT. No temporary Private setting is needed | Proposed (Session 1) |
| D-F | Phone matching on **Phone and MobilePhone** only, each only when readable: digit-normalised pre-filter, exact digit check in Apex (equal digits, or a suffix match of 10 or more digits in either direction). Scan cap 2,000, then TOO_MANY. See decisions/2026-11-20-d-f-… | Accepted 2026-11-20 |
| D-G | More than 100 test data created in session 6 only, with approval | Assumed |
| D-I | Permission sets split: `DATA_Contact_Read_Only` (Contact data, read only) and `APP_Contact_Read_Agent` (class and agent access only). Never auto-assigned. See decisions/2026-11-20-permission-set-split-… | Accepted 2026-11-20 |
| D-J | Query selectivity: only `contactId` and exact email are selective. No performance metadata for now. See decisions/2026-11-20-query-selectivity-… | Accepted 2026-11-20 |
| D-H | New `CRA_` classes. `ESA_RecordSearchAction` (cross-object SOSL, no counts, capped at 20) is not extended or changed. It is referenced only by its test and the unlinked `ESA_Record_Search` function (Session 1) | Verified |

## Outcome precedence

ERROR, NEEDS_CLARIFICATION, FILTER_UNAVAILABLE, NO_MATCH, TOO_MANY (>100), DUPLICATE_IDENTIFIER, SINGLE_MATCH / FIELD_ANSWER, LIST_2_TO_5, LIST_6_TO_10, LIST_11_TO_100. REMAINING_PAGE follows LIST_6_TO_10 when the user asks for the rest.

Session 2 refinement: a user with no Contact Read gets NO_MATCH before FILTER_UNAVAILABLE is considered, so the answer stays neutral.

## Action contract

Inputs (optional text unless noted): `name`, `email`, `phone`, `accountName`, `jobTitle`, `city`, `stateOrRegion`, `country`, `location`, `contactId`, `requestedField` (Name, Account, Title, Email, Phone, MobilePhone, MailingAddress), `showRemaining` (Boolean).

Outputs: `outcomeCode`, `totalMatchesLabel`, `shownCount`, `remainingCount`, `canShowRemaining` (Boolean), `refinementRequired` (Boolean), `similarNameCount` (Integer), `suggestedFiltersText`, `duplicateOn`, `requestedFieldLabel`, `criteriaSummary`, `userMessage`, `singleContactId`, `resultContactIds` (comma-separated), `contactsJson`.

`remainingCount` is the number of rows the user may still ask to see. It is non-zero only when `canShowRemaining` is true (6–10 matches, first page). `refinementRequired` is true for 11–100 and more than 100. The template must then ask for filters and must not offer more pages. `singleContactId` is set only for exactly one match.

Session 3 (2026-11-20): implemented as `CRA_ContactSearchAction.searchContacts`, label "Search Contacts (Contact Read Agent)". `shownCount`, `remainingCount` and `similarNameCount` are Integer, `canShowRemaining` and `refinementRequired` Boolean, all other outputs Text (`singleContactId` is the 18-character Id as text). Unset Text outputs are empty; `contactsJson` is `[]` when there are no rows. More than 10 requests in one call: the extra requests return ERROR. Apex class access is on `APP_Contact_Read_Agent` only. See [session-3-invocable-action.md](session-3-invocable-action.md).

`contactsJson` entries: `n`, `id`, `name`, `contactUrl`, `accountName`, `title`, `email`, `phone`, `mobilePhone`, `mailingAddress`. Blank or unreadable values are "Not available". Every value is Contact data typed by people: the Prompt Template treats it as data, never as instructions (S4). Links are built in Apex from the My Domain URL and `/lightning/r/Contact/<id>/view`.

Session 4 (2026-11-20): a 16th output, `searchResultJson` (Text), carries the same values as one JSON object (`payloadVersion` 1; null text omitted; `contacts` always an array; numbers and booleans as JSON literals). It is the only input of the Flex template `CRA_Contact_Result_Presentation` (Flex templates accept at most 5 text inputs). See [decisions/2026-11-20-single-json-template-input.md](decisions/2026-11-20-single-json-template-input.md).

## Search rules

At least one filter required. Name words match the start of first or last name; for two or more words, exact full-name matches take priority. Email: a full address is exact, `@domain.tld` matches that domain exactly, anything else is contains. Phone digit-normalised, on Phone and MobilePhone. Account name and title contains. Location matches mailing city, state or country (the text fields; state and country picklists appear to be on, so `MailingStateCode`/`MailingCountryCode` also exist). `%`, `_`, `\` escaped. Bind variables only, whitelisted fields, order `Name, Id`. Count is USER_MODE and capped at 101. Page size 5.

Session 2 implementation details (proposed, see session-2-search-engine.md): city, state and country are starts-with on the text field, and state and country also equal the ISO code. Values longer than the field are rejected, never truncated. More than 5 name words, a malformed `contactId` or an unknown `requestedField` return NEEDS_CLARIFICATION. `with sharing` and USER_MODE both apply to every query, and only readable fields are selected. At most 3 queries per request and at most 10 requests per call.

## Query selectivity (2026-11-20)

Only `Id` and exact `Email` filters are selective. Name, contains/domain email, phone, Account name, title and location filters scan the accessible Contacts (capped results, not capped scans). Accepted for now with no new metadata. Review thresholds and options: [session-2-review-fixes.md](session-2-review-fixes.md).

## Common build rules

1. Read CONTEXT.md, requirements-status.md and this file first.
2. Feature branch per session, pull request only. Never commit to main.
3. Verify against the org before naming or changing anything. No guessed field names or platform limits.
4. Apex: bulkified, no queries or DML in loops, `with sharing`, USER_MODE, no DML in any `CRA_` production class, tests at 90% or better (floor 80%).
5. Standard objects and fields only. No custom objects or fields. Synthetic data only, named `CRA-TEST`.
6. Read back every create, deploy or publish before reporting it done.
7. Do not activate the agent or merge without explicit approval.
8. At the end, update progress.md and any decision that changed.

# Session 2 — search engine (SCGOE-95)

**Date:** 2026-11-19 · **Run by:** Revecast Orchestrate for Nagaruri Johnson · **Branch:** `feature/scgoe-95-s2-search-engine` (from `scgoe-95-context`)

**Nothing was deployed.** The org was used only for a check-only validation (tests run and roll back). No sharing setting, permission, user, agent or org metadata was changed. Afterwards the org still had 0 `CRA_` Apex classes, 0 `CRA_` permission sets and 20 Contacts.

A status here is a dated claim. Check it against the repository and the org before relying on it.

> **Superseded in part on 2026-11-20.** The review fixes changed phone matching (Phone and MobilePhone), name duplicates (exact full-name priority), email (exact / domain / partial), the 11–100 output flags and the permission sets (`DATA_Contact_Read_Only`, `APP_Contact_Read_Agent` replace `CRA_Contact_Read_Agent_User`). The current state and the latest validation are in [session-2-review-fixes.md](session-2-review-fixes.md).

## What was built (source only)

| Component | Type | Purpose |
|---|---|---|
| `sfdx-project.json`, `.forceignore`, `.gitignore` | Scaffold | SFDX project, `sourceApiVersion` 68.0, `force-app/main/default` |
| `CRA_ContactSearchCriteria` | Apex | Inputs of the action contract. Cleans and validates them: removes control characters, collapses whitespace, rejects over-long values, digit-normalises phone, checks `contactId` is a Contact Id, whitelists `requestedField` |
| `CRA_FieldAccess` | Apex (virtual) | Object and field read checks for the running user, so the service selects only readable fields and refuses filters on unreadable ones. Virtual, so tests can substitute it (the access seam) |
| `CRA_ContactSearchResult` | Apex | Output shaped to the action contract: outcome code, counts, labels, rows with `n, id, name, contactUrl, accountName, title, email, phone, mailingAddress`. Blank or unreadable values read "Not available". `getContactsJson()` and `getResultContactIds()` produce `contactsJson` and `resultContactIds` |
| `CRA_ContactSearchService` | Apex | The search: bind variables only, whitelisted fields, `with sharing` and `AccessLevel.USER_MODE` on every query, count capped at 101, pages of five, phone exact-digit check, duplicate detection, outcome classifier, sanitised ERROR. No DML |
| `CRA_TestDataFactory` | Apex test | Synthetic `CRA-TEST` data. Restricted users and permission sets exist only inside the test and are rolled back |
| `CRA_ContactSearchTest` | Apex test | 26 functional tests |
| `CRA_ContactSearchSecurityTest` | Apex test | 8 security tests (5 real enforcement, 3 simulated) |
| `CRA_Contact_Read_Agent_User` | Permission set (source only, **not deployed**) | Contact Read, Account Read, read FLS on AccountId, Title, Email, Phone, MailingAddress. No create, edit or delete. Apex class access comes in S3, agent access in S5 |

`ESA_RecordSearchAction` and every other existing component were not touched.

## How the search works

- **Filters** (all ANDed): name words each match the start of FirstName or LastName (up to 5 words); email with `@` is exact, otherwise contains; phone (see below); Account name contains; job title contains; city starts with; state/region and country start with the text value or equal the ISO code; `location` starts-with on city, state or country, or equals a state/country code; `contactId` equals.
- **Safety:** every value is a bind variable. `%`, `_` and `\` are escaped, so input always matches literally. Values over the field length are rejected, not truncated, so a value can never become a wider search.
- **Count:** `Database.countQueryWithBinds(... LIMIT 101, USER_MODE)`. Counts, rows and duplicate checks see only records the user can read.
- **Phone (D-F):** a digit-subsequence pre-filter (`%2%1%2%...%`, last 10 digits) in USER_MODE, up to 2,000 candidates. Then an exact digit check in Apex: the digits are equal, or one number ends with the other when both have at least 10 digits once leading zeros are removed. So `(212) 842-5500` = `212-842-5500` = `+1 212 842 5500`, and `+44 191 4956203` = `0191 4956203` = `191 495 6203`. Different country codes never match, and a 7-digit local number must match exactly.
- **Duplicates (D-B):** an exact email (with `@`) or a phone that matches 2 or more Contacts → DUPLICATE_IDENTIFIER. A name of 2 or more words → DUPLICATE_IDENTIFIER only when every match has exactly that full name. A one-word name, a partial email and an Account-only search are never duplicates.
- **Outcome precedence:** ERROR, NEEDS_CLARIFICATION, (no Contact Read → NO_MATCH), FILTER_UNAVAILABLE, NO_MATCH, TOO_MANY (>100), DUPLICATE_IDENTIFIER, SINGLE_MATCH / FIELD_ANSWER, LIST_2_TO_5, LIST_6_TO_10 / REMAINING_PAGE, LIST_11_TO_100.
- **Rows:** ordered `Name, Id`. 6–10 shows rows 1–5, then rows 6–10 with `showRemaining`. 11–100 shows five rows and filter suggestions, with no show-more (D-C). TOO_MANY returns no rows. FIELD_ANSWER rows carry only id, name, link and the requested field.
- **Queries per request:** at most 3 (count, exact-name count, page; or phone scan and page). `searchAll` handles up to 10 requests per call, checks the remaining query budget, and returns ERROR for any request beyond those limits.

## Validation results (check-only, org `orgfarm-232477b490-dev-ed`)

| Run | Id | Result |
|---|---|---|
| 1 | 0AfjV000006chwXSAQ | Failed to compile: `bulk` is a reserved word; permission set description over 255 characters. Both fixed |
| 2 | 0AfjV000006chlGSAQ | Passed: 8 components, 33 of 33 tests |
| Mutation A | 0AfjV000006chzlSAA | LIKE escaping switched off on purpose → 2 tests failed (`injectionPayloadsNeverWiden`: `%` widened to TOO_MANY). Reverted |
| Mutation B | 0AfjV000006ciB3SAI | Queries switched to SYSTEM_MODE on purpose → the new USER_MODE test failed (Email and Phone leaked to a restricted user). Reverted |
| **Final** | **0AfjV000006chdCSAQ** | **Passed. checkOnly = true, 8 components, 0 errors, 34 of 34 tests, 0 failures** |

Coverage (final run): `CRA_ContactSearchService` 100%, `CRA_ContactSearchCriteria` 100%, `CRA_ContactSearchResult` 100%, `CRA_FieldAccess` 100% (target 90%).

## Security tests — what is real and what is simulated

**Real platform enforcement** (each runs `System.runAs` a restricted user: Minimum Access – Salesforce profile plus a test-only permission set, both rolled back):

| Test | Proves |
|---|---|
| `enforcedBaselineAdminSeesPrivateContacts` | As admin, the private Contacts count (name duplicate = 2, title search = 6), so the restricted results below are meaningful |
| `enforcedRecordSharingLimitsResultsCountsAndDuplicates` | Contacts without an Account (private under Controlled by Parent) never appear in rows, counts, Ids or duplicate checks. The shared name, email and phone return SINGLE_MATCH, not DUPLICATE. The title count is 3, not 6. A private Contact, its email, its `contactId` and a nonexistent name all get the identical NO_MATCH message |
| `enforcedFieldSecurityHidesUnreadableFields` | With no Read on Email and Phone (confirmed by the platform's describe inside runAs), those fields read "Not available", are absent from `contactsJson`, are not suggested, and filtering by them returns FILTER_UNAVAILABLE |
| `enforcedNoContactAccessReturnsNeutralNoMatch` | With no Contact Read, the platform refuses a USER_MODE query, and the service returns the neutral NO_MATCH, not an error |
| `enforcedUserModeBlocksFieldsEvenIfAccessCheckIsWrong` | The service's own access check is replaced with one that says "everything is readable". USER_MODE alone still refuses Email and Phone: sanitised ERROR, nothing leaked. Mutation B confirmed that this test fails under SYSTEM_MODE |

**Simulated** (admin runs the test, the service gets a substitute `CRA_FieldAccess`; these test the service's handling of an access answer, not Salesforce's enforcement): `simulatedAccountNameUnreadable`, `simulatedTitleAndAddressUnreadable`, `simulatedContactUnreadable`. Account name is simulated because Contact Read requires Account Read, so a real user who can read Contacts but not Accounts cannot be built.

## Acceptance criteria (S2 prompt)

| # | Criterion | Result |
|---|---|---|
| 1 | Every outcome code except ERROR and FILTER_UNAVAILABLE reached by a test; boundaries 0, 1, 2, 5, 6, 10, 11, 100, 101 each tested | **Met.** All codes are reached, ERROR and FILTER_UNAVAILABLE included. One test per boundary group, and each boundary is asserted |
| 2 | Injection payloads never throw, never widen | **Met.** 8 payloads × 5 filters return NO_MATCH; 5,000-character values return NEEDS_CLARIFICATION; control characters are removed; null is handled. Mutation A proves the test is real |
| 3 | No filter → NEEDS_CLARIFICATION | **Met** (null criteria, empty, only requestedField, only showRemaining, whitespace) |
| 4 | Duplicate name, email, phone → DUPLICATE_IDENTIFIER; Account-only over a shared phone does not | **Met** |
| 5 | `(212) 842-5500`, `212-842-5500`, `+44 191 4956203` match | **Met**, plus `+1 212 842 5500`, `0191 4956203`, `191-495-6203`; wrong digit and 7-digit local do not |
| 6 | Coverage ≥ 90% per class | **Met** (100% each) |
| 7 | No DML keyword in production classes | **Met** (scan of the 4 production classes). The static test that enforces this is S3 scope |

## Deviations from the approved design and the S2 prompt

The architecture (Agent Script → Invocable Apex → Prompt Template) is unchanged. These are refinements and items pulled forward:

1. **Pulled forward from S3 into the service:** the field-access check with an injectable seam and FILTER_UNAVAILABLE; "Not available" handling; record links from the My Domain URL; `contactId` and `requestedField` handling (needed for FIELD_ANSWER in S2's own criteria); sanitised ERROR. Why: you asked for FLS enforcement and security tests now, and without the access check a USER_MODE query on an unreadable field fails the whole search. **S3 still owns:** the `@InvocableMethod` wrapper (List in, List out, flattened outputs), the static no-DML test, Apex class access on the permission set, and the deploy.
2. **No Contact Read is checked before FILTER_UNAVAILABLE** and returns NO_MATCH, so a user without Contact access gets the neutral answer (Session 1 security plan), not a message about filters.
3. **Search rule details the design left open** (proposed, confirm or change): location is starts-with on text plus exact ISO code; a name duplicate needs 2 or more words and every match sharing that exact full name; malformed `contactId`, unknown `requestedField`, over-long values and more than 5 name words return NEEDS_CLARIFICATION; DUPLICATE_IDENTIFIER shows the first five and filter suggestions.
4. **Phone rule** (D-F made concrete): the 10-digit suffix match described above. A phone scan that reaches 2,000 candidates returns TOO_MANY, because the exact count is then uncertain.
5. **Permission set includes Account Read:** it is needed for Account name, and Contact Read depends on it.
6. **`searchAll` runs queries per request inside a loop.** Each request has different filters, so they cannot share one query. It is capped at 10 requests per call and checks the remaining query budget. An agent sends one request at a time.
7. **Branch:** `feature/scgoe-95-s2-search-engine` was cut from `scgoe-95-context` (not `main`), because the context files and PR #1 live there. The S2 prompt named this branch.

## Limitations and open points

- Decisions **D-B, D-C, D-D and D-F** are implemented as written but are still "Assumed". Please confirm or change them.
- Contains searches (`%value%` on title, Account name and partial email) cannot use an index. That is fine at this org's size (20 Contacts) but would need review on a large org.
- A name matches only the start of the first or last name. Middle names, the second half of a hyphenated name and nicknames do not match.
- Only `Phone` is searched (not MobilePhone or OtherPhone). Extensions are not supported.
- `userMessage` fallback text is English and hard-coded in Apex. The Prompt Template owns the real wording (S4). If multilingual fallbacks are needed, move these to Custom Labels in S3.
- The real record-level tests depend on today's sharing (Contact Controlled by Parent, Account Public Read/Write). If the OWD changes, these tests must change with it.
- Tests prove behaviour inside Apex only. The live chat as a restricted user (S6) and the Apex → Prompt Template hand-off (S4/S5) are still pending.
- More than 100 real records are covered only by test data. Live data for that outcome is D-G (S6, with approval).

# Session 2 — review fixes (SCGOE-95)

**Date:** 2026-11-20 · **Run by:** Revecast Orchestrate for Nagaruri Johnson · **Branch:** `feature/scgoe-95-s2-search-engine` (PR #2)

Follows the Session 2 code review of commit `a92e392` (0 Critical, 1 High, 6 Medium, 12 Low). Nagaruri Johnson set the direction for each fix on 2026-11-20.

**Nothing was deployed.** The org was used only for a check-only validation (tests run and roll back). No sharing setting, permission, permission set assignment, user or agent was changed, and nothing was merged. Session 3 has not started.

A status here is a dated claim. Check it against the repository and the org before relying on it.

## Validation (check-only, org `orgfarm-232477b490-dev-ed`)

| Property | Value |
|---|---|
| Id | **0AfjV000006e22sSAA** |
| Result | Succeeded, `checkOnly = true`, 2026-11-20 09:56:08–09:56:39 UTC |
| Components | 9 of 9, 0 errors: 7 Apex classes, `DATA_Contact_Read_Only`, `APP_Contact_Read_Agent` |
| Tests | 48 of 48 passed (`CRA_ContactSearchTest` 37, `CRA_ContactSearchSecurityTest` 11) |
| Coverage | 100% on `CRA_ContactSearchService` (415 lines), `CRA_ContactSearchCriteria` (162), `CRA_ContactSearchResult` (15), `CRA_FieldAccess` (15) |

Before and after the run, the org had 0 `CRA_` classes and none of the three permission set names (`CRA_Contact_Read_Agent_User`, `DATA_Contact_Read_Only`, `APP_Contact_Read_Agent`). This validation is the only run made on the corrected code, and it is the code committed with this report.

## Changes by finding

| Finding | Change | Where |
|---|---|---|
| **H1** phone only on `Phone` | `Phone` and `MobilePhone` are both searched (match on either) and both returned. Each field is used only when the running user can read it. With neither readable, a phone filter returns FILTER_UNAVAILABLE. No other phone fields were added | `CRA_ContactSearchService.PHONE_FIELDS`, `readablePhoneFields`, `buildPlan`, `countByPhone`, `anyPhoneMatches`, `toRow`, `toFieldAnswerRow`; `ContactRow.mobilePhone` |
| **H1** field answers | `requestedField` "mobile" (also "mobile phone", "mobile number", "cell") returns only the mobile. "Phone" returns both numbers, so a Contact that has only a mobile is not reported as having no phone | `CRA_ContactSearchCriteria.REQUESTED_FIELD_ALIASES`, `toFieldAnswerRow` |
| **M1** name duplicates | Exact full-name matches take priority. For a name of two or more words, if any accessible Contact has exactly that name, the search is narrowed to those Contacts. Near matches (same prefix) are only counted in a new `similarNameCount` output. Two or more exact matches are DUPLICATE_IDENTIFIER on Name, and no Contact is ever selected for the user (`singleContactId` stays empty). With no exact match, prefix matching is unchanged | `countByQuery`, `countByPhone`, `findDuplicateIdentifier`; `CRA_ContactSearchCriteria.hasFullName` |
| **M2** "@" = exact | Email is classified as EXACT (a full address), DOMAIN (`@acme.com`: every address at exactly that domain) or PARTIAL (anything else, e.g. `lindqvist@`, `@acme`: contains). "@" alone asks for clarification. A domain search is never a duplicate. `criteriaSummary` says "Email domain: …" or "Email contains: …" | `CRA_ContactSearchCriteria.validateEmail`, `CRA_ContactSearchService.addEmail`, `emailSummaryLabel` |
| **D-C / L2** 11–100 | First five rows. New `refinementRequired = true`, `canShowRemaining = false`, and `remainingCount = 0`, so nothing in the output invites paging. `showRemaining` is ignored. TOO_MANY also sets `refinementRequired` | `classifyMultiple`, `loadPage` |
| **L1** duplicates beyond five | Duplicates follow the same size bands: 2–5 all rows; 6–10 first five, `canShowRemaining`, then REMAINING_PAGE with `duplicateOn` kept; 11–100 first five and `refinementRequired` | `classifyMultiple` |
| **D-D** "Not available" | Kept unchanged, now also for `mobilePhone` | `readField`, `orNotAvailable` |
| **M4** permission set | `CRA_Contact_Read_Agent_User` (never deployed) is replaced by two: `DATA_Contact_Read_Only` ("DATA – Contact – Read Only": Contact and Account Read; read FLS on AccountId, Title, Email, Phone, MobilePhone, Mailing Address; no create, edit, delete or View All) and `APP_Contact_Read_Agent` ("APP – Contact Read Agent": no object or field access; Apex class access is added in S3, agent access in S5). Neither is assigned to anyone | `force-app/main/default/permissionsets/` |
| **M3** selectivity | Reviewed and documented below. No index, field or other metadata added | — |
| **M5** prompt injection | Carried to S4 as a hard requirement (build prompt S4 updated). A test proves a hostile Title is carried verbatim as a JSON string value and does not change the search | `hostileFieldValueIsCarriedAsData`; `ContactRow` comment |
| **M6** test gaps | 14 tests added and existing ones extended (see below) | both test classes |
| L9 budget branch | `searchAll` budget check now tested on its own | `queriesPerRequest` test hook, `searchAllStopsWhenQueryBudgetIsLow` |

## Action contract changes (for S3 and S4)

- New outputs: `canShowRemaining` (Boolean), `refinementRequired` (Boolean), `similarNameCount` (Integer).
- Changed meaning: `remainingCount` is the number of rows the user may still ask to see. It is non-zero only when `canShowRemaining` is true.
- `contactsJson` rows gain `mobilePhone`.
- `requestedField` gains `MobilePhone`. `Phone` answers carry both `phone` and `mobilePhone`.
- `duplicateOn` can be `Name`, `Email`, `Phone` or a combination such as `Name, Phone`. `Phone` means Phone or MobilePhone.

## Tests added or extended

**Functional (`CRA_ContactSearchTest`, 37):** new `exactFullNameTakesPriority`, `duplicateNameOverFiveCanShowRest` (7 shared names), `duplicateEmailOverTenRequiresRefinement` (12 shared emails), `requestedFieldWithDuplicateAsksFirst`, `emailExactDomainAndPartial` (9 inputs), `phoneAndMobilePhoneSearch` (mobile-only Contact, Phone on one and mobile on another = duplicate, field answers), `combinedFilters` (6 combinations incl. name + phone, name + domain, Account + title + phone, name + country + title, two mismatches), `injectionPayloadsInLocationAndDomain` (8 payloads × city, state, country + 3 domain payloads), `injectionPayloadsInPhoneAndContactId` (9 payloads, asserts 0 queries ran), `hostileFieldValueIsCarriedAsData`, `searchAllStopsWhenQueryBudgetIsLow`. Boundary tests now assert `canShowRemaining`, `refinementRequired` and `remainingCount = 0` for 11, 100 and 101.

**Security (`CRA_ContactSearchSecurityTest`, 11):**

| Type | Test | Proves |
|---|---|---|
| Real enforcement (new) | `enforcedPhoneFieldSecurityIsPerField` | Two restricted users (Phone without MobilePhone, and the reverse), confirmed by the platform describe. Each can't find a Contact by the number it can't read (neutral NO_MATCH), sees "Not available" for it, and the value is absent from `contactsJson` |
| Real enforcement (new) | `enforcedDataPermissionSetGrantsReadOnly` | A Minimum Access user holding only `DATA_Contact_Read_Only` (assigned inside the test, rolled back) can read Contact, Account and all contract fields, can't create, edit or delete, and the search returns the full row |
| Real metadata check (new) | `enforcedAppPermissionSetGrantsNoData` | `APP_Contact_Read_Agent` has 0 object and 0 field permissions, and neither permission set has any assignment |
| Real enforcement (extended) | `enforcedRecordSharingLimitsResultsCountsAndDuplicates` | A private Contact sharing a **mobile** with a visible one is not counted (SINGLE_MATCH, not a duplicate) |
| Real enforcement (extended) | `enforcedFieldSecurityHidesUnreadableFields` | MobilePhone also reads "Not available" and doesn't leak |
| Real enforcement (unchanged) | baseline, no Contact access, USER_MODE independent layer | as in Session 2 |
| Simulated (unchanged) | 3 tests | how the code reacts to a substitute access check, not Salesforce enforcement |

## Query selectivity (review M3) — accepted risk, documented

No index, field or metadata was added for performance, as instructed.

| Filter | SOQL shape | Can it use a standard index? |
|---|---|---|
| `contactId` | `Id = :v` | Yes |
| Email, exact | `Email = :v` | Yes, Email is indexed on Contact |
| Full name, exact | `Name = :v` (with the prefix conditions) | Unlikely: Name is a derived compound field. The prefix conditions decide the plan |
| Name words | `(FirstName LIKE 'x%' OR LastName LIKE 'x%')` | Leading text is fixed, but the OR across two fields usually prevents index use |
| Email, domain or partial | `Email LIKE '%@d'` / `'%v%'` | No (leading wildcard) |
| Phone / MobilePhone | `(Phone LIKE '%2%1%…' OR MobilePhone LIKE …)` | No (leading wildcard); Apex then checks the digits on up to 2,000 rows |
| Account name, title | `LIKE '%v%'` | No (leading wildcard) |
| City, state, country, location | `LIKE 'v%'` and `…Code = :v` | Not by default (no standard index on these fields) |

**Effect:** only `contactId` and exact email are selective on their own. Any other search scans the Contacts the user can see. COUNT and page queries are capped (101 and 5), but the cap limits the rows returned, not the rows scanned. With 20 Contacts in this org this costs nothing.

**When to review:** before using this in an org with tens of thousands of Contacts, or if a search takes more than about 2 seconds or hits a non-selective query error. Options then: custom indexes from Salesforce Support on Title or MailingCity, SOSL `IN PHONE FIELDS` / `IN EMAIL FIELDS` as the pre-filter, or requiring an exact field alongside contains filters. Each needs its own design check.

**Not checked:** custom indexes already in this org (needs Salesforce Support or the query plan tool).

## Outstanding limitations

- **Names:** a name matches only the start of a first or last name. Reversed names ("Smith John"), middle names, the second half of hyphenated names and nicknames don't match exactly. A salutation ("Dr Ava Lindqvist") returns NO_MATCH unless the agent removes it.
- **Exact-name priority hides near matches:** when "John Smith" matches exactly, "John Smithson" is only counted in `similarNameCount`. The template should mention that similar names exist.
- **Phone:**
  - A user who can read only one of Phone or MobilePhone is matched on that field only, by design.
  - A number stored without a country code matches any country code with the same 10-digit national number.
  - Formats that keep the trunk zero can miss, and extensions are rejected.
  - At the 2,000-row scan cap the "more than 100" label is an estimate.
- **Email domain:** the domain must match exactly, so `@acme.com` doesn't find `mail.acme.com`. `@acme` (no dot) is a partial match and also finds `acmecorp.com`.
- **`similarNameCount`** is capped by the 101 count limit.
- **Location:** city is starts-with ("York" doesn't find "New York"), and `location = CA` matches both California and Canada.
- **English only:** the fallback `userMessage` text is hard-coded English. Consider Custom Labels in S3.
- **Class size:** `CRA_ContactSearchService` is 864 lines, about half of them comments. That's over the ~500-line guideline. Splitting query building from classification is a candidate refactor.
- **Static test hooks:** `forceFailureForTest`, `phoneScanLimit` and `queriesPerRequest` live in the production class.
- **Sharing dependency:** the record-level tests depend on today's sharing (Contact Controlled by Parent, Account Public Read/Write).
- **Not yet proven:** the Apex → Prompt Template hand-off (S4/S5) and a live chat as a restricted user (S6).
- **Assignment:** neither permission set is assigned. A non-admin user needs both `DATA_Contact_Read_Only` and `APP_Contact_Read_Agent`, assigned manually after approval (S5/S6). A Permission Set Group for the job function is optional and not built.

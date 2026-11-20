# S3. Invocable action and security hardening

**Status (2026-11-20):** built and validated check-only (0AfjV000006e70xSAA), not deployed. Results against these criteria: [session-3-invocable-action.md](../session-3-invocable-action.md). Custom Labels deferred (service unchanged).

## Build prompt

**From the Session 2 review fixes (2026-11-20):** the contract gained `canShowRemaining`, `refinementRequired`, `similarNameCount`, `mobilePhone` and the `MobilePhone` requested field (see technical-design.md). Map them in the invocable outputs. Keep `searchAll`'s 10-request cap and query-budget check.

**Carried over from Session 2 (2026-11-19):** `CRA_ContactSearchService` already does the accessible-field checks through the `CRA_FieldAccess` seam, FILTER_UNAVAILABLE, "Not available", record links from the My Domain URL, `contactId` and `requestedField` re-checked in USER_MODE, and sanitised ERROR. `CRA_ContactSearchResult.getContactsJson()` and `getResultContactIds()` produce the contract strings. So S3 is mostly a thin `@InvocableMethod` wrapper that maps `CRA_ContactSearchCriteria` in and `CRA_ContactSearchResult` out. Keep the existing tests green. Add class access for `CRA_ContactSearchAction` to `APP_Contact_Read_Agent` (not to `DATA_Contact_Read_Only`, which holds data access only; assign neither automatically), add the static no-DML test, and consider moving the fallback `userMessage` text to Custom Labels. The first deploy happens in S3, after approval (RunSpecifiedTests on the `CRA_` tests).

Read CONTEXT.md, context/requirements-status.md and context/technical-design.md. Create branch `feature/scgoe-95-s3-action`.

Implement `CRA_ContactSearchAction` with the action contract in technical-design.md: List-in/List-out, flattened outputs, record links from the My Domain URL, `requestedField` and `contactId` handling re-checked in USER_MODE, sanitised errors, accessible-field list with an injectable access seam, FILTER_UNAVAILABLE. Add `CRA_ContactSearchActionTest`, including a static test that fails if DML appears in any `CRA_` production class. Add the class to `APP_Contact_Read_Agent`.

## Acceptance criteria

1. Output fields match the contract exactly.
2. Blank and unreadable values appear as "Not available". No unreadable value appears anywhere in the output.
3. NO_MATCH wording is identical whether no Contact exists or none are accessible.
4. A forced exception returns ERROR with no stack trace or class names.
5. A `contactId` the user cannot read returns the neutral NO_MATCH.
6. Requested-field answers contain only the field, the name and the link.
7. The static no-DML test passes and fails when DML is added.
8. Coverage at least 90% (floor 80%).

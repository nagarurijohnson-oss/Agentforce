# D-F — Phone matching on Phone and MobilePhone

**Date:** 2026-11-20 · **Status:** Accepted · **Deciders:** Nagaruri Johnson · **Amends:** D-F as implemented in Session 2 (Phone only)

## Context

The Session 2 review (H1) found that only `Contact.Phone` was searched. 17 of the org's 20 Contacts have a MobilePhone, so mobile numbers returned "no match".

## Decision

- Search and return `Phone` and `MobilePhone` only. A match on either field counts. No other phone fields are added unless explicitly required.
- Each field is used only when the running user can read it. With neither readable, a phone filter returns FILTER_UNAVAILABLE.
- Matching rule unchanged: a digit pre-filter on the last 10 digits in USER_MODE. Then an exact digit check in Apex: the digits are equal, or one number ends with the other when both have 10 or more digits. The scan is capped at 2,000 rows, then TOO_MANY.
- `requestedField` "Phone" returns both numbers. "Mobile" returns only the mobile.

## Consequences

- A user who can read only one of the fields is matched on that field only.
- A number without a country code matches any country code. Extensions are rejected.
- The leading-wildcard pre-filter can't use an index (see the query selectivity record).

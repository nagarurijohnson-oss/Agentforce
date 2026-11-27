# D-B — Exact full-name priority; duplicates never select a Contact

**Date:** 2026-11-20 · **Status:** Accepted · **Deciders:** Nagaruri Johnson · **Supersedes:** D-B as implemented in Session 2 (every match had to share the full name)

## Context

The Session 2 review (M1) found that two "John Smith" plus one "John Smithson" became a list instead of "which one do you mean?", because a name duplicate needed every match to share the exact name. Requirement O6: ask the user to identify the correct Contact.

## Decision

- For a name of two or more words, exact full-name matches take priority. If any accessible Contact has exactly that name, the search is narrowed to those Contacts, and the near matches are counted in `similarNameCount`.
- Two or more exact matches are DUPLICATE_IDENTIFIER on Name. No Contact is selected automatically: `singleContactId` is empty and a requested field is not answered.
- An exact email (a full address) or a phone number (Phone or MobilePhone) matching two or more Contacts is also a duplicate. An email domain search is never a duplicate.
- Duplicates follow the same size bands as lists (see D-C).

## Consequences

- One exact match among near matches is a single match. The template should mention that similar names exist.
- Reversed names, nicknames and middle names are not exact. They fall back to prefix matching.

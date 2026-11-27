# Account Id search returns that Account's Contacts (AID-1)

**Date:** 2026-11-27 · **Status:** Accepted
**Deciders:** Lal (approval reported in session by Nagaruri Johnson) · **Supersedes:** 2026-11-27-account-id-search-out-of-scope.md

## Context

The out-of-scope record left Account Id search for Lal. On 2026-11-27 Nagaruri Johnson reported that Lal approved
Account Id → its Contacts only. Account details, related Cases and related Opportunities were not approved.

## Decision

Add an optional `accountId` input to `CRA_ContactSearchAction`. It returns only the Contacts on that Account the user
can see, in USER_MODE; a hidden or missing Account gives the neutral NO_MATCH; no Account field is returned. The
Contact Id path is unchanged. Agent Script stores a typed 001 Id as `in_account_id`.

## Consequences

- Apex deployed to MAX (99/99 tests, 100% coverage); published v3 and v8 do not send the input and are unaffected.
- Users get it only after a new agent version is published and later activated (activation still waits for OPS-1).
- Account details, related Cases and related Opportunities stay out of scope.

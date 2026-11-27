# Account ID search is outside the approved Contact search scope

**Date:** 2026-11-27 · **Status:** Accepted (pending Lal's confirmation)
**Deciders:** Orchestrate, from the approved requirements; Lal to confirm

## Context

The completion list asked for a review of Account ID search, to be built only if the approved scope needs it.

## Decision

Not implemented. Requirement R2 (`context/requirements-status.md`, recorded 2026-11-19) lists Account **name**, not
Account Id. Account name search is built and tested (Apex 102/102; agent suites S22).

## Consequences

- No Apex change and no new agent version.
- If Lal adds Account ID to scope, it would be a criteria field in `CRA_ContactSearchCriteria` / `CRA_ContactSearchService`
  (an Id filter in USER_MODE), with tests. Whether the agent also needs a new version depends on how the input is described to the planner; check before building.

## Update — 2026-11-27 (S29, Contact Id search)

Contact record Id search (003) was fixed in the Agent Script only (`session-kb-s29-contact-id-search.md`). Account Id
(001) search stays out of scope until Lal approves it. An Account Id typed today is sent as a Contact Id and rejected by
the existing Apex ("I could not tell which Contact you mean"), so no Account details are shown. If approved it needs Apex
(an Account Id filter in the user-mode query) and tests, plus a new agent version.

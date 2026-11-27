# ADR — Session 6 UAT: configuration-based permission tests and one restricted user

**Date:** 2026-11-23 · **Status:** Accepted
**Deciders:** Nagaruri Johnson · **Supersedes:** none

## Context

Session 6 needed a real restricted user. Two Session 3 tests asserted that the CRA permission sets had zero assignments, so any UAT assignment would break them. Field-level security tests need a set without Email, MobilePhone and Mailing Address, but permission sets add up.

## Decision

- Create one user, `CRA UAT Restricted` (Minimum Access – Salesforce), with Log in as and no password; create 107 synthetic Contacts and keep them.
- Assign `DATA_Contact_Read_Only`, `APP_Contact_Read_Agent` and `APP_Contact_Read_Agent_Panel_Access` to that user only; deploy the UAT-only `DATA_Contact_Read_Limited_UAT`, which must replace (never join) the full DATA set.
- Replace the zero-assignment assertions with configuration checks (no admin, write, View All or field-edit permission; APP grants the action class only), after a check-only validation.
- Run the agent test suite as the admin against synthetic data.

## Consequences

- Log in as turned out to be disabled in the org (`enableAdminLoginAsAnyUser` false), so the panel UAT waits for a further decision (B-1).
- Restricted-user evidence at the Apex layer comes from a check-only `SeeAllData` test run as the real user, never saved in the org.

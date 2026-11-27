# D-8b and D-9 accepted as residual risk; no new agent version

- **Status:** Accepted by Nagaruri Johnson, **pending Lal's confirmation** · **Date:** 2026-11-27

## Decision
D-8b (Medium: an agent user missing the data space set gets the platform's generic error; nothing is invented or exposed) and
D-9 (Low: "show the other 3" after a failed display says "no other Contacts") are not fixed. No v8 is published.
## Controls
The minimum permission design (7 grants, `knowledge-search/minimum-permissions.md`) and an assignment check before each user is enabled:
every agent user must hold all 7 grants, checked by SOQL on `PermissionSetAssignment` and `PermissionSetLicenseAssign`.
## Revisit
If a later agent version is published for another reason, fix both in it.

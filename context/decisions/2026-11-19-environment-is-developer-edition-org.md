# Environment is a personal Developer Edition org, not a sandbox

**Date:** 2026-11-19 · **Status:** Accepted · **Deciders:** Nagaruri Johnson · **Amends:** 2026-11-19-scgoe-95-finalized-design.md (Environment and scope)

## Context

Earlier context files described the environment as a personal sandbox. In Session 1, Nagaruri Johnson stated that the work runs in a personal Developer Edition org. The org confirms this: `MAX`, 00DjV000003BVbRUAW, `OrganizationType = Developer Edition`, `IsSandbox = false`.

## Decision

All SCGOE-95 work targets the Developer Edition org `orgfarm-232477b490-dev-ed`. Context files now say "org" instead of "sandbox".

## Consequences

- The org is production-type, so every deploy runs Apex tests. Use `RunSpecifiedTests` on the `CRA_` tests, and leave existing classes untouched.
- Licence headroom is small: 2 of 4 Salesforce user licences and 4 of 5 "Agentforce (Default)" licences are free. One restricted UAT user is enough.
- There is no refresh or copy-from-production safety net. Synthetic `CRA-TEST` data must be removed after Session 6, with the count read back.

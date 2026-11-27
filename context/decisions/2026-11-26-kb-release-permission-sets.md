# ADR-K7 — Two release permission sets for Knowledge search: read with 8 categories, and default data space only

- **Status:** Accepted (configuration); assignment pending A5
- **Date:** 2026-11-26
- **Deciders:** Nagaruri Johnson. Design by Revecast Orchestrate.

## Context
S15 proved that agent users need Knowledge Read with category visibility (F-2) and membership of the default data space (F-1).

## Decision
- `DATA_Knowledge_Read_Only`: Custom category visibility on the 8 Scholarship_Programs categories, including General_Aid.
  Campus_Services and the All Programs root are excluded.
- New `SYS_Knowledge_Default_DataSpace`: the default data space only, with no other permissions. It is a separate set so that data-space access can
  be granted and removed on its own. It is not Data Cloud User or Data Cloud Administrator.
- Neither set is assigned until A5. Both Setup-only settings are documented as manual steps for each org.

## Consequences
- The configuration matches the S15 sets that passed as the restricted user, so no rerun was needed.
- Every new org needs the two manual Setup steps after deployment.

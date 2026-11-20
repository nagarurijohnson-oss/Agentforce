# Access-only permission set for the Lightning Agentforce panel

**Date:** 2026-11-20 · **Status:** Accepted · **Decider:** Nagaruri Johnson

## Context
Contact_Read_Agent v1 was published and activated, but it did not appear in the Lightning Experience Agentforce panel because no permission set granted agent access. Assigning `APP_Contact_Read_Agent` would break the CRA tests that require it to have zero assignments.

## Decision
Create `APP_Contact_Read_Agent_Panel_Access`, which grants agent access to Contact_Read_Agent only (no object, field, Apex or system permissions). Assign it to the current admin user only, for demonstration and controlled testing.

## Consequences
- The agent appears in the panel for that user. `APP_Contact_Read_Agent` and its tests are unchanged.
- The test user is a System Administrator, so the panel tests do not prove restricted-user behaviour. That remains a Session 6 UAT item.
- Remove the set when testing ends.

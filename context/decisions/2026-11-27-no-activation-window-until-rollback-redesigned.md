# ADR-K-OPS1 — No agent activation window until the rollback mechanism is redesigned and tested

**Date:** 2026-11-27 · **Status:** Accepted
**Deciders:** Nagaruri Johnson · **Supersedes:** none

## Context

In the S24 Phase B window the rollback watchdog failed (OPS-1) and Contact_Read_Agent v7 stayed Active for
11 h 35 min instead of the approved 90 minutes. See `knowledge-search/incident-2026-11-26-v7-window-overrun.md`.

## Decision

No further activation window for any Contact_Read_Agent version is scheduled until the rollback mechanism is
redesigned and tested against the seven requirements in the incident report (independent credentials and host,
rollback first, retry until confirmed, full logging, alerting, an end-to-end test with the session ended, and the
same deadline for temporary grants).

## Consequences

- Phase B re-runs and any further panel testing wait for the redesign.
- OPS-1 stays open (High) until the redesigned rollback passes its test.

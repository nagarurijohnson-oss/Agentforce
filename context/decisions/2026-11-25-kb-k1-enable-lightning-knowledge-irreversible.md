# ADR-K1 — Enable Salesforce Knowledge and Lightning Knowledge in MAX (IRREVERSIBLE)

- **Status:** **Accepted and carried out 2026-11-25** (Nagaruri Johnson). Lal's approval line: **not recorded in this build session — pending.**
- **Date:** 2026-11-25
- **Deciders (required):** Lal (requirement owner) and Nagaruri Johnson (org owner). Design by Revecast Orchestrate.

## ⚠ This change cannot be undone

Once Salesforce Knowledge is enabled in an org, it **cannot be disabled**. Lightning Knowledge, once enabled, cannot be turned off either. The `Knowledge__kav` object, the Knowledge settings and the Knowledge permissions stay in MAX permanently, even if the feature is later abandoned. Articles and the Data Library can be deleted afterwards; the enablement itself cannot be reversed.

## Context

- MAX (`00DjV000003BVbRUAW`) is a Developer Edition, production-type org — not a sandbox — and hosts the live Contact Read Agent (v3 Active) and Employee_Leave_Assistant.
- Checked 2026-11-25: `KnowledgeSettings.enableKnowledge=false`; no `Knowledge__kav` object exists.
- The Agentforce Data Library Knowledge source and the article object both require Knowledge.

## Options considered

| Option | For | Against |
|---|---|---|
| **A — Enable in MAX through a `KnowledgeSettings` deploy** (proposed) | Traceable in the repo; read back by retrieve and describe; same org as the agent | Permanent change to the org hosting the live agent |
| B — Enable in MAX through Setup clicks | Familiar | Equally permanent; not traceable in source |
| C — Wait for, or create, a separate org (sandbox or scratch org) | MAX stays unchanged | The agent, Data Cloud set-up and tests live in MAX; the whole stack would need rebuilding elsewhere |
| D — Do not build Knowledge search | No change | Lal's requirement not met |

## Proposed decision

Option A. In phase K1, an Agentforce Build session deploys `KnowledgeSettings` with `enableKnowledge=true` and `enableLightningKnowledge=true` **only after**:
1. Lal and Nagaruri Johnson record their approval here (Status → Accepted, with date); and
2. the build session raises its own IRREVERSIBLE confirmation naming MAX, and it is confirmed.

## Consequences

- Knowledge is permanently on in MAX; `Knowledge__kav` and Knowledge permissions appear in Setup and in permission sets.
- No effect expected on Contact search; K1's gate re-runs Contact Apex 102/102 and checks v3 is still Active.
- Forecloses keeping MAX free of Knowledge.

## Revisit if

A sandbox or separate org becomes the preferred place for Knowledge before K1 runs.

## Approval record

| Approver | Decision | Date |
|---|---|---|
| Lal | _pending_ | |
| Nagaruri Johnson | _pending_ | |

## Outcome (2026-11-25, build session)

- Nagaruri Johnson confirmed the IRREVERSIBLE confirmation naming MAX in the build session ("Confirm. I acknowledge this action is irreversible — proceed.").
- Pre-check: `enableKnowledge=false`; Contact_Read_Agent v3 Active; Contact Apex 98/98 on the last run before enablement.
- Deployed `KnowledgeSettings` (enableKnowledge, enableLightningKnowledge = true): Succeeded, 1 component. Read back: both true. `Knowledge__kav` describe succeeds (42 fields, record type Master only).
- After: Contact Apex **102/102** (run 707jV00000CWqIA); v3 still Active.
- Lal's approval is still to be recorded here; it was not used as authorization.

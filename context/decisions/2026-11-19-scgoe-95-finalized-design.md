# SCGOE-95 — Finalized design decisions

**Date:** 2026-11-19 · **Status:** Accepted · **Deciders:** Nagaruri Johnson

## Decisions

1. Use the new Agentforce Builder with Agent Script.
2. Use Invocable Apex for secure Contact retrieval and search outcome handling.
3. Use a Prompt Builder template to manage response presentation.
4. Use the native Agentforce UI, with no custom LWC.
5. Include Salesforce record hyperlinks in responses.
6. Follow the functional requirements and search outcome decisions (see requirements-status.md; not yet attached).
7. Enforce sharing, CRUD, FLS and USER_MODE.
8. Use synthetic test data only.
9. No business-record DML through the Read Agent.
10. Do not introduce client-specific custom objects or fields.

## Environment and scope

Personal Salesforce sandbox. Contact search and retrieval on standard objects and fields only.

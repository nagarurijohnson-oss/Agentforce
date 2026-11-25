# ADR-K5 — Isolate Knowledge search from Contact search; publish as v4, keep v3 for rollback

- **Status:** Proposed
- **Date:** 2026-11-25
- **Deciders:** Nagaruri Johnson and Lal. Design by Revecast Orchestrate.

## Context
The Contact path was stabilised over 12 sessions (fixes D-1, D-2, D-3; name links). Its baseline is Apex 102/102 and agent suite 23/27 with 4 known expectation errors. v3 is Active (checked 2026-11-25).

## Decision
- Separate subagent (`knowledge_search`), variables (`kb_question`, `kb_pending`, `kb_reply`), template (`CRA_Knowledge_Answer`) and permission set (`DATA_Knowledge_Read_Only`).
- Only additions to the shared router: one route and one routing rule; `clarify` text updated.
- No edits to `contact_search`, `read_only_guard`, `CRA_` classes, `CRA_Contact_Result_Presentation` or the four existing permission sets and assignments.
- Publish as v4 **without activating**; activate only after approval; v3 kept for rollback.

## Consequences
- Rollback is reactivating v3.
- The router is the one shared change; KT-18 and KT-19 plus the full Contact regression guard it.

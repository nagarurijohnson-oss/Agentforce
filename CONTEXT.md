# SCGOE-95 – Contact Read Agent

Environment: personal Salesforce **Developer Edition org** (`MAX`, org id 00DjV000003BVbRUAW, a production-type org, not a sandbox; corrected 2026-11-19). Scope: Contact search and retrieval using standard Salesforce objects and fields.

## Index
- [context/goals.md](context/goals.md) — goals and scope
- [context/decisions/2026-11-19-scgoe-95-finalized-design.md](context/decisions/2026-11-19-scgoe-95-finalized-design.md) — finalized design decisions
- [context/requirements-status.md](context/requirements-status.md) — functional requirements and search outcome decisions (recorded 2026-11-19)
- [context/technical-design.md](context/technical-design.md) — technical design, action contract, security rules, common build rules
- [context/build-prompts/](context/build-prompts/) — one build prompt with acceptance criteria per build session (S1–S6)
- [context/progress.md](context/progress.md) — implementation progress tracker
- [context/session-1-environment-gate.md](context/session-1-environment-gate.md) — Session 1 environment gate report: checks, commands and results (2026-11-19)
- [context/session-2-search-engine.md](context/session-2-search-engine.md) — Session 2 report: search engine build, validation results, real vs simulated security tests, deviations (2026-11-19)
- [context/session-2-review-fixes.md](context/session-2-review-fixes.md) — Session 2 review fixes: phone + mobile, exact-name priority, email domain, refinement flags, permission set split, selectivity, validation 0AfjV000006e22sSAA (2026-11-20)
- [context/session-3-invocable-action.md](context/session-3-invocable-action.md) — Session 3 report: invocable action, 24 tests, class access on APP, validation 0AfjV000006e70xSAA, acceptance criteria and limitations (2026-11-20)
- [force-app/main/default/](force-app/main/default/) — SFDX source (API 68.0): `CRA_` Apex classes (including the `CRA_ContactSearchAction` invocable action) and the `DATA_Contact_Read_Only` and `APP_Contact_Read_Agent` permission sets (not deployed)
- [context/decisions/](context/decisions/) — decision records, including D-B, D-C, D-D, D-F, the permission set split and query selectivity (2026-11-20)
- [context/decisions/2026-11-19-environment-is-developer-edition-org.md](context/decisions/2026-11-19-environment-is-developer-edition-org.md) — the environment is a Developer Edition org, not a sandbox

Every build session must keep the requirements, decisions and progress files up to date. Nothing is activated or merged without explicit approval.

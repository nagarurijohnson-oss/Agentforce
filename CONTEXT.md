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
- [context/session-3-review-and-deploy.md](context/session-3-review-and-deploy.md) — Session 3 review (0 Critical, 0 High, 2 Medium, 3 Low) and first deploy 0AfjV000006eF6XSAU to the Developer Edition org, verified (2026-11-20)
- [context/session-4-prompt-template.md](context/session-4-prompt-template.md) — Session 4: 5-input limit, single JSON input (D-K), template `CRA_Contact_Result_Presentation`, check-only 0AfjV000006eMETSA2; deployed in Session 5; test figures corrected in Session 5 (2026-11-20)
- [context/session-4-template-previews.md](context/session-4-template-previews.md) — one synthetic preview per test case, all 12 outcome codes (2026-11-20)
- [context/session-5-agent-preview.md](context/session-5-agent-preview.md) — Session 5: template 78/78, `Contact_Read_Agent` draft deployed (not published), 11 preview scenarios, Builder screenshots, open issues H1 (links `URL_Redacted`) and M1 (HTML rendering) (2026-11-20)
- [context/session-5-fix-v3-option-a.md](context/session-5-fix-v3-option-a.md) — Session 5 fixes: payload v3 backslash escaping and the separate "Open record" link; validated check-only, 84/84 template tests, Builder rendering, remaining platform limitations (2026-11-20)
- [context/session-5-v3-deployment-validation.md](context/session-5-v3-deployment-validation.md) — Session 5 fixes: v3 deployment, 83/84 deployed template tests, 11-scenario regression, Builder UI, literal-entity check; validation not passed (agent relay drops escapes) (2026-11-20)
- [context/session-5-delivery-review.md](context/session-5-delivery-review.md) — Session 5: direct response delivery review (displayable outputs, render rules, show_and_return, say): not supported in the preview or Builder channel; field-answer template rule corrected, validated, not deployed (2026-11-20)
- [context/session-5-relay-limitation-support-case.md](context/session-5-relay-limitation-support-case.md) — Session 5: agent relay limitation L-1 (open, High): reproduction steps, expected vs actual, screenshots and a Salesforce support case draft (2026-11-20)
- [context/decisions/2026-11-20-agent-script-template-relay.md](context/decisions/2026-11-20-agent-script-template-relay.md) — how Agent Script calls the template and relays its reply (2026-11-20)
- [force-app/main/default/](force-app/main/default/) — SFDX source (API 68.0): `CRA_` Apex classes (including the `CRA_ContactSearchAction` invocable action) and the `DATA_Contact_Read_Only` and `APP_Contact_Read_Agent` permission sets (not deployed)
- [context/decisions/](context/decisions/) — decision records, including D-B, D-C, D-D, D-F, the permission set split and query selectivity (2026-11-20)
- [context/decisions/2026-11-19-environment-is-developer-edition-org.md](context/decisions/2026-11-19-environment-is-developer-edition-org.md) — the environment is a Developer Edition org, not a sandbox

## Knowledge Article Search (design for review, 2026-11-25)
- [context/knowledge-search/README.md](context/knowledge-search/README.md) — feature index and phase status (K0 in review; nothing built)
- [context/knowledge-search/technical-design.md](context/knowledge-search/technical-design.md) — Knowledge → Data Library → retriever → Prompt Template → Contact_Read_Agent v4; no Apex, Flow or LWC
- [context/knowledge-search/prerequisites.md](context/knowledge-search/prerequisites.md) — approvals, platform prerequisites, automated vs manual steps
- [context/knowledge-search/implementation-phases.md](context/knowledge-search/implementation-phases.md) — phases K0–K6 and gates
- [context/knowledge-search/test-scenarios.md](context/knowledge-search/test-scenarios.md) — sample articles, KT-01 to KT-20, acceptance criteria
- [context/knowledge-search/security-validation.md](context/knowledge-search/security-validation.md) — security checks SV-1 to SV-10 still to prove
- [context/decisions/2026-11-25-kb-k1-enable-lightning-knowledge-irreversible.md](context/decisions/2026-11-25-kb-k1-enable-lightning-knowledge-irreversible.md) — **ADR-K1, Proposed: enabling Knowledge is irreversible; needs Lal and Nagaruri Johnson**
- `context/decisions/2026-11-25-kb-k2-…` to `…-kb-k5-…` — ADR-K2 to K5 (Proposed)
- `context/build-prompts/K1-…` to `K6-…` — Knowledge build prompts

Every build session must keep the requirements, decisions and progress files up to date. Nothing is activated or merged without explicit approval.

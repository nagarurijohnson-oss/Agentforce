# ADR-K3 — Tell similar articles apart by content design, programme-match rules and categories

- **Status:** Proposed
- **Date:** 2026-11-25
- **Deciders:** Nagaruri Johnson and Lal. Design by Revecast Orchestrate.

## Context
Semantic search ranks "Merit renewal" and "Graduate renewal" close together. The requirement is that the agent distinguishes similarly worded articles and never returns unrelated content.

## Decision
1. Every Title is `<Programme> – <Topic>`; every Summary opens with "Applies to:" naming programme and audience.
2. The `CRA_Knowledge_Answer` template enforces programme-match, ambiguity (ask which programme, list up to 5 titles, never merge figures) and no-match rules.
3. A Data Category Group `Scholarship_Programs` is deployed so the library can be scoped by category later.

## Consequences
- Precision depends on article authoring discipline as well as retrieval; the content rules apply to real articles later too.
- Measured by acceptance criteria 1–3 in `context/knowledge-search/test-scenarios.md`.
- If precision falls short, ADR-K4 fallback 1 (custom retriever with a smaller result count) applies.

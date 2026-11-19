# S2. Search engine

## Build prompt

Read CONTEXT.md, context/requirements-status.md and context/technical-design.md. Create branch `feature/scgoe-95-s2-search-engine`.

Implement `CRA_ContactSearchCriteria` and `CRA_ContactSearchService`: validation, bound dynamic queries in USER_MODE, capped count, paging (size 5), phone normalisation and exact digit verification, duplicate detection and the outcome classifier, following the search rules and outcome precedence in technical-design.md. No invocable annotation yet. Write `CRA_TestDataFactory` and `CRA_ContactSearchTest`. Bulkify; no queries in loops; no DML in production classes.

## Acceptance criteria

1. Every outcome code except ERROR and FILTER_UNAVAILABLE is reached by a test. Count boundaries 0, 1, 2, 5, 6, 10, 11, 100 and 101 each have a test.
2. Injection payloads (`' OR Name != '`, `%`, `_`, `\`, 5,000-character strings, control characters, null) never throw and never widen results.
3. No filter returns NEEDS_CLARIFICATION.
4. Duplicate name, email and phone each return DUPLICATE_IDENTIFIER. An Account-only search over a shared phone does not.
5. Phone formats `(212) 842-5500`, `212-842-5500` and `+44 191 4956203` match correctly.
6. Coverage at least 90% per class (floor 80%).
7. No DML keyword in the production classes.

# D-C — 11 to 100 matches: first five and refinement, no pagination

**Date:** 2026-11-20 · **Status:** Accepted · **Deciders:** Nagaruri Johnson

## Context

Requirement O4: with more than ten matches, show the first five and suggest additional filters. The Session 2 review (L2) found that `remainingCount` still carried, for example, 95, which a template could read as something to offer.

## Decision

- 11–100 matches, including duplicates, return the first five rows with `refinementRequired = true`, `canShowRemaining = false` and `remainingCount = 0`. `showRemaining` is ignored.
- More than 100 matches return no rows and `refinementRequired = true`.
- Only 6–10 matches (first page) set `canShowRemaining = true`.

## Consequences

If the right Contact isn't among the first five alphabetically, the user must refine. The template must ask for filters and must not offer more pages when `refinementRequired` is true.

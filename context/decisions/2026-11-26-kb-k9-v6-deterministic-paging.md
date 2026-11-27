# ADR-K9 — v6: deterministic paging and script-merged search criteria

**Date:** 2026-11-26 · **Status:** Accepted (build and test inactive); activation not approved
**Deciders:** Nagaruri Johnson (build the fix first, no activation) · **Supersedes:** none

## Context
D-5: the Contact Search planner sometimes wrote the next page itself instead of running the search (v3, 7 of 27). D-6: it once replied "I am searching…" without running anything. A first fix (v5) let the router store the criteria, which exposed D-7: `@utils.setVariables` keeps any variable the model omits, so old criteria leaked into new searches (also present in v4's mixed request).

## Decision
- Paging goes through a router action to a `contact_page` subagent where search, presentation and relay are deterministic.
- The router stores a new or narrowed search itself, then routes to Contact Search, which runs it deterministically.
- The model passes only the latest message's details (`in_*`, emptied every turn); the script replaces (new) or merges (narrow) the stored criteria.

## Consequences
- Paging can't be invented by the planner: 60/60, 0 invented. Stale criteria fixed: 9/9.
- The router prompt is longer and decides new vs narrow; narrowing can't remove a criterion.
- v5 is a superseded inactive version; v6 is the release candidate. L-1 is unaffected.

**Revisit if:** Salesforce adds `transition to` after `setVariables`, or a supported verbatim display path for Employee agents.

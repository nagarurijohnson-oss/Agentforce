# ADR — New and narrowed Contact searches run from stored criteria, not a planner call

- Status: Accepted
- Date: 2026-11-25
- Deciders: Nagaruri Johnson (approved "Build, publish v3")

## Decision
`set_criteria` stores the criteria and sets `search_pending`; the agent script then runs `search_contacts` deterministically with the stored criteria. The planner-callable `run_search` is removed. `show_remaining` and `ask_about_selected` stay planner-callable.

## Why
On the published agent the planner sent `set_criteria` and the search in parallel, so the search ran with empty criteria (D-2, 10 of 30), or stored the criteria and skipped the search (D-3, 6 of 12). On v3: 30 of 30 and 12 of 12.

## Consequence
Do not re-add a planner-callable search for new or narrowed searches.

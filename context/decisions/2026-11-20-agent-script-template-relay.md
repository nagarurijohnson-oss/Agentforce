# Agent Script calls the template from its instructions and relays the reply verbatim

**Date:** 2026-11-20 · **Status:** Accepted (implementation detail within the approved architecture)
**Deciders:** Orchestrate, under Nagaruri Johnson's Session 5 instruction to configure the agent with Agent Script, the existing Apex action and the Prompt Template · **Supersedes:** none

## Context

The Session 5 script chained the template after the search action with `run @actions.present_results`, passing `@outputs.searchResultJson`. It compiled, but in the live preview the chained call never ran: the reasoning model received the raw action output and wrote its own reply, and the start router answered follow-up questions from conversation memory.

## Decision

- The search actions store `searchResultJson` in `last_result_json`.
- The `contact_search` instructions call the template procedurally when a result is waiting (`if last_result_json != "" and last_reply == ""`) and store its reply in `last_reply`.
- When `last_reply` is set, the instructions contain only that reply and require it to be repeated exactly, as data. Presentation outputs are hidden from the model (`is_used_by_planner: False`).
- The router always routes. `after_reasoning` clears the per-turn state.

## Why

It keeps the agreed split (Apex decides, the template presents, Agent Script orchestrates) and makes the template call deterministic. In the final preview, 17 of 19 template replies were relayed character for character and 19 of 19 with identical visible text.

## Consequences

- The relay still depends on the model following instructions. Session 6 agent tests must cover it.
- Record links are not fixed by this decision. The agent runtime masks absolute URLs (see session-5-agent-preview.md, H1).

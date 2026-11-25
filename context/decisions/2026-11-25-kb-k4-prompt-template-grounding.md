# ADR-K4 — Ground answers through a Prompt Template on the Data Library retriever

- **Status:** Proposed
- **Date:** 2026-11-25
- **Deciders:** Nagaruri Johnson. Design by Revecast Orchestrate.

## Context
Agent Script already calls `CRA_Contact_Result_Presentation` through `generatePromptResponse://` on v3. The stock "Answer Questions with Knowledge" action is not listed in the org while Knowledge is off, and its Agent Script target form is not confirmed.

## Decision
Create Flex template `CRA_Knowledge_Answer` (input `question`) grounded on the Data Library's `KA_…` retriever, and call it from a new `knowledge_search` subagent using the deterministic "store, then run" pattern.

## Fallbacks
1. Precision below target: a custom retriever created in Einstein Studio (manual — no retriever metadata type in this org) with a smaller result count and a filter on Online status.
2. Retriever cannot be bound to a template: the stock action through `standardInvocableAction://` (target form to be confirmed).

## Consequences
- One possible manual step: binding the retriever in Prompt Builder if the metadata deploy does not, then retrieving the template into the repo.
- Same relay path as Contact results, so the open L-1 limitation applies equally.

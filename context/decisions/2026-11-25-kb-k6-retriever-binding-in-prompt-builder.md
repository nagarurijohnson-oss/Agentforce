# ADR-K6 — Bind the retriever in Prompt Builder once; the agent calls the template with the question only

- **Status:** Accepted (technical, within ADR-K4 fallback P10). Supplements ADR-K4.
- **Date:** 2026-11-25
- **Deciders:** Revecast Orchestrate in the build session for Nagaruri Johnson; the manual step is for an admin.

## Context

ADR-K4 grounds `CRA_Knowledge_Answer` on the Data Library retriever. Tested in MAX on 2026-11-25:

1. **Template binding through the Metadata API:** 13 variants failed. `retriever://`, `einsteinSearch://`, `einsteinRetriever://` data providers: "Cannot invoke "einstein.gpt.shared.provider.definition.GenAiPromptTypeEnum.getPath()" because the return value of "…GenAiPromptDefType.getType()" is null". `invocable://getEinsteinRetrieverResults` with `{!$EinsteinSearch:<name>.<output>}` for the API name, label, Id and action name, and outputs results/result/output/searchResults/response/data/value: "The getEinsteinRetrieverResults action output parameter doesn't match." Without an output: "Range [1, -1) out of bounds for length 60". The Metadata API reference documents no retriever data-provider element.
2. **Retrieval in the agent, passages handed to the template:** a `retriever://KA_…` action compiles and runs in Agent Script and returns the right passages (A14 never). But its output is an object; every way of passing it to the template's String input (string, object/`lightning__textType` output, object input, `"{!@variables.x}"`) reached the template as an object or as literal text. The template API rejects an object input ("incorrect input param: … all elements are null"), and in the agent the template then **invented answers** ("January 15", "March 15"). Not shippable.

## Decision

- An admin binds the retriever in Prompt Builder **once** (Insert Resource → Einstein Search) at the marker `INSERT_EINSTEIN_SEARCH_HERE` in template version 3 and activates the new version. Orchestrate then retrieves the template into the repo, so later versions deploy through metadata.
- The `knowledge_search` subagent calls only `generatePromptResponse://CRA_Knowledge_Answer` with `Input:question`; search and answer happen in that one call (as in ADR-K4).
- Version 2 of the template (input `passages`) stays as the tested rule set: 96/96 runs with real retriever output passed as text.

## Consequences

- One manual Prompt Builder step (about 2 minutes) before K5 can be previewed end to end. It is UI-only because no metadata or API form for the binding was accepted by this org (errors above).
- Once retrieved, the binding's XML is in the repo; no further manual step for later versions.
- Template v3 is active but unbound until the step is done; nothing uses it (agent v3 is Active and unchanged).

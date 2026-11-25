# K5. Agent Script v4 (Agentforce Build)

**Gate:** K4 acceptance criteria met.

## Build prompt

Add the `knowledge_search` subagent, the three `kb_*` variables, the `go_knowledge_search` route, the routing rule and the clarify text from `context/knowledge-search/technical-design.md` §4.1 to `Contact_Read_Agent.agent`. Change nothing in `contact_search` or `read_only_guard`. Run `sf agent validate` first; preview KT-01 to KT-20; deploy; publish v4 **without activating**. Run the existing agent suite (expect 23/27 with the same 4 known misses) and add the Knowledge cases to the `AiEvaluationDefinition`. Run SV-6 and SV-8. Branch `feature/kb-k5-agent`, draft PR.

## Acceptance criteria

1. v4 published and Inactive; v3 still Active.
2. Knowledge suite passes criteria 1–4; Contact suite 23/27 (same 4); Apex 102/102.
3. git diff shows no change to existing CRA_ metadata or permission sets; compiled bundle has no write actions.

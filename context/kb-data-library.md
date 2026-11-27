# Knowledge Data Library — CRA_Scholarship_Knowledge

Created 2026-11-25 (phase K3) with `sf agent adl create --source-type knowledge --primary-index-field1 Title --primary-index-field2 Summary`. Status read back with `sf agent adl status --include-artifacts`: **READY**.

| Item | Value |
|---|---|
| Library | `CRA_Scholarship_Knowledge` (`1JDjV000001UHVtWAO`), label "CRA Scholarship Knowledge", type ENTERPRISE, data space `default` |
| Source | Knowledge (`Knowledge__kav`), primary index fields Title + Summary (immutable), no content fields |
| Data categories | None selected (all categories indexed, so the A12/A13 campus-services decoys test ranking — approval A4 as recommended) |
| Restrict to public articles | false (`isRestrictToPublicArticle`). The installed CLI has no flag for it (SV-5) |
| Data stream / DLO | `Knowledge_kav_Home__dll` (`1dsjV000000aeRxQAI` / `1dljV000001G48jQAC`) |
| DMO | `ssot__KnowledgeArticleVersion__dlm` (14 rows: 13 Online, 1 Draft) |
| Search index | `KA_CRA_Scholarship_Knowledge` (`18ljV000006GGDRQA4`), HYBRID, near real time, `multilingual-e5-large`, chunks of 512 tokens; chunk DMO `KA_CRA_Scholarship_Knowledge_chunk__dlm` (28 chunks: 2 per article, one ending with the Article Number, one with the URL name) |
| Retriever | `KA_CRA_Scholarship_Knowledge` (`1CxjV0000002yXxSAI`), API name **`KA_CRA_Scholarship_Knowledge_1Cx_VbRab635d61`** |
| Retriever action | GenAiFunction `Knowledge_CRA_Scholarship_Knowledge` (`172jV00000Aldo9QAB`), "Get Information from CRA_Scholarship_Knowledge" — created by the library, not used by the agent |

## Evidence

- "merit eligibility GPA" (index vector search): A01 first (0.88), then A03.
- Retriever through the agent runtime, 15 questions (KT-01…KT-15): the asked-for article ranked first in every programme-specific question; **A14 (Draft) was never returned**, although it is in the DMO and has 2 chunks in the index. The retriever filters on publication status. Raw outputs: `scripts/kb/retrievals/`.
- SV-9: Data Cloud admin (`GenieAdmin`, Data Cloud Architect) still held by John Steve and OrgFarm EPIC only; no holder added. The CRM connector set (`sfdc_a360_sfcrm_data_extract`) is on Platform Integration User, as before.
- SV-10: credit use not measured in this session. Read it in Setup → Digital Wallet (Data Cloud consumption) after the K6 runs.

## Rollback

`sf agent adl delete -i 1JDjV000001UHVtWAO` removes the library (its stream, index and retriever). Knowledge itself stays on (irreversible, ADR-K1).

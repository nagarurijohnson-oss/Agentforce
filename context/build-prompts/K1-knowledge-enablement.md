# K1. Knowledge enablement and access (Agentforce Build)

**Do not start until** `context/decisions/2026-11-25-kb-k1-enable-lightning-knowledge-irreversible.md` is **Accepted** with both approvals recorded.

## Build prompt

Read CONTEXT.md, `context/knowledge-search/` (all files), ADR-K1 to K5 and `context/progress.md`. Create branch `feature/kb-k1-enable` from `feature/kb-knowledge-search-design`. In org MAX:
1. Confirm `KnowledgeSettings.enableKnowledge=false`, Contact_Read_Agent v3 is Active, and CRA_ Apex is 102/102.
2. Raise the IRREVERSIBLE confirmation naming MAX. Only after Confirm, deploy `KnowledgeSettings` with `enableKnowledge` and `enableLightningKnowledge` true. Read the setting back, run `sf sobject describe --sobject Knowledge__kav`, and record every standard field.
3. Confirm what licence or permission an article **reader** needs (do not assume); record it.
4. Deploy DataCategoryGroup `Scholarship_Programs` with the 9 categories (if approved in K0).
5. Deploy permission set `DATA_Knowledge_Read_Only` (Read on Knowledge__kav; FLS Read on Title, Summary, ArticleNumber, UrlName; nothing else). Do not assign it.
6. Re-run CRA_ Apex (expect 102/102) and confirm v3 is still Active.

Do not change any existing CRA_ class, template, permission set, assignment or agent version. No Apex, Flow or LWC. Write `context/session-kb-k1-enablement.md`, update `progress.md`, commit and open a draft PR.

## Acceptance criteria

1. `Knowledge__kav` describe succeeds; the setting reads back true.
2. `DATA_Knowledge_Read_Only` exists with exactly the listed access and no assignments.
3. Contact Apex 102/102; v3 Active; the four existing permission sets unchanged.

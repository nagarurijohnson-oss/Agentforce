# K2. Sample Knowledge articles (Agentforce Build)

**Gate:** K1 complete and recorded in `progress.md`.

## Build prompt

Using `context/knowledge-search/test-scenarios.md` §1, write `scripts/kb/articles.json` with 14 synthetic articles (Title, UrlName starting `KB-TEST`, Summary starting "Applies to:" and at most 1,000 characters, Language en_US, category). Create them as `Knowledge__kav` records and assign categories. Publish A01–A13 with the standard `publishKnowledgeArticles` action through REST (no Apex); leave A14 as Draft. If the action is not exposed, stop and give the admin the exact list-view Publish steps. Verify with SOQL (`PublishStatus`, `IsLatestVersion`, `ArticleNumber`) and record the Ids in the fixture. Do not create or change any Contact. Branch `feature/kb-k2-content`, draft PR.

## Acceptance criteria

1. SOQL shows 13 Online and 1 Draft `KB-TEST` articles with the planned Titles.
2. Contact count unchanged; no other records changed.

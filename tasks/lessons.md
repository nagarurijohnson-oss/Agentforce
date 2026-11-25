
## 2026-11-25 Knowledge build
- Published GenAiPromptTemplate versions are immutable: a redeploy "Succeeds" with no change. Add a new versionIdentifier and point activeVersionIdentifier at it; verify by retrieve.
- Knowledge__kav standard fields are not FLS-controlled; required ones (Title, UrlName) reject fieldPermissions.
- publishKnowledgeArticles needs articleVersionIdList as a JSON array.
- Agent Script retriever:// outputs are objects; they do not reach a String template input as text. Ground the template on the retriever instead.
- 2026-11-25: Saving a prompt template version in Prompt Builder can silently change the model and inject zero-width characters. Always retrieve and diff the new version (model, content) before reusing earlier test results.
- 2026-11-25: Prompt Builder Jinja: reference `EinsteinSearch.<retriever>.results` directly (e.g. `{% set kb = ….results %}`) or the retriever does not run; loop `kb.searchResults` / `sr.result` and test `resultFieldApiKey`. Escaping cannot be disabled; double the newline after block tags.
- 2026-11-25: Generations API only runs the active version; test a new version on a separate test-only template before activating.
- 2026-11-25: `sf agent preview` responses drop Markdown links even when the reply contains them; check the trace and verify links in the panel.

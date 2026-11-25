
## 2026-11-25 Knowledge build
- Published GenAiPromptTemplate versions are immutable: a redeploy "Succeeds" with no change. Add a new versionIdentifier and point activeVersionIdentifier at it; verify by retrieve.
- Knowledge__kav standard fields are not FLS-controlled; required ones (Title, UrlName) reject fieldPermissions.
- publishKnowledgeArticles needs articleVersionIdList as a JSON array.
- Agent Script retriever:// outputs are objects; they do not reach a String template input as text. Ground the template on the retriever instead.

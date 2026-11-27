
## 2026-11-25 Knowledge build
- Published GenAiPromptTemplate versions are immutable: a redeploy "Succeeds" with no change. Add a new versionIdentifier and point activeVersionIdentifier at it; verify by retrieve.
- Knowledge__kav standard fields are not FLS-controlled; required ones (Title, UrlName) reject fieldPermissions.
- publishKnowledgeArticles needs articleVersionIdList as a JSON array.
- Agent Script retriever:// outputs are objects; they do not reach a String template input as text. Ground the template on the retriever instead.
- 2026-11-25: Saving a prompt template version in Prompt Builder can silently change the model and inject zero-width characters. Always retrieve and diff the new version (model, content) before reusing earlier test results.
- 2026-11-25: Prompt Builder Jinja: reference `EinsteinSearch.<retriever>.results` directly (e.g. `{% set kb = ….results %}`) or the retriever does not run; loop `kb.searchResults` / `sr.result` and test `resultFieldApiKey`. Escaping cannot be disabled; double the newline after block tags.
- 2026-11-25: Generations API only runs the active version; test a new version on a separate test-only template before activating.
- 2026-11-25: `sf agent preview` responses drop Markdown links even when the reply contains them; check the trace and verify links in the panel.
- 2026-11-25: A subagent that relays its own reply ends the turn; a request needing two capabilities needs one subagent that runs both deterministically, not a hand-off "offer".
- 2026-11-25: Injection-style messages can be refused by the platform Prompt_Injection guardrail before any subagent; score agent-level injection tests on 'nothing leaked', not on a specific decline text.

## 2026-11-27 (S25)
- When a model step may strip escapes, escaping cannot be the control: remove the dangerous characters (look-alikes) before the model sees the text.
- An integration-licence user accepted CustomizeApplication/ModifyMetadata/AssignPermissionSets; CustomizeApplication pulls in ManageCustomPermissions and ManageTranslation, ViewSetup pulls in ViewRoles.
- A repo token without Actions-secrets scope cannot store secrets: have the person generate the key pair and send only the certificate. Never handle the private key.
- workflow_dispatch and schedule only run from the default branch; use a push trigger on a non-default branch for pre-merge tests.

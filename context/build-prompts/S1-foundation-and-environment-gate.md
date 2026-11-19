# S1. Foundation and environment gate

> **Status 2026-11-19:** gate checks run read-only; see [../session-1-environment-gate.md](../session-1-environment-gate.md). Steps 1 and 3 (scaffold, permission sets) were deferred on instruction (no metadata changes this session) and move to the start of Session 2 and Session 3. The environment is a Developer Edition org, not a sandbox.

## Build prompt

Read CONTEXT.md, context/requirements-status.md and context/technical-design.md. Create branch `feature/scgoe-95-s1-foundation`.

1. Add the SFDX scaffold (`sfdx-project.json`, `force-app/main/default`, ignore files) at the API version the org supports (68.0).
2. Run the gate checks and record the command and output for each:
   - Salesforce CLI and agent plugin versions.
   - List `GenAiPromptTemplate`, `AiAuthoringBundle` and `GenAiPlannerDefinition` metadata in the org.
   - Confirm Agent Script supports the Employee agent type here, and that Apex in an action runs as the chatting user.
   - Confirm which permission sets and licences a non-admin chat user needs.
   - Confirm the exact Agent Script syntax for `apex://` actions and the prompt-template target.
3. Create permission set `CRA_Contact_Read_Agent_User` and a restricted UAT permission set or profile (no deploy beyond these without confirmation).
4. Write the gate report into context/progress.md.

## Acceptance criteria

1. Scaffold committed and validates.
2. Each gate check has a yes or no with the command and output cited.
3. If Agent Script on an Employee agent is not supported, stop and record the fallback options for a decision.
4. Permission sets exist in source and, once approved, in the org, with read-back.
5. No Apex, templates or agents are created.

# S5. Agent Script agent

## Build prompt

**From Session 3 (2026-11-20):** `apex://CRA_ContactSearchAction` exposes `searchContacts` with the 12 inputs and 15 outputs in technical-design.md. Class access is granted only by `APP_Contact_Read_Agent`; prove at runtime that a user without it cannot run the action and one with it can. Send one request per call.

**From Session 1:** the syntax is confirmed by the org compiler (`subagent`, `agent_type: "AgentforceEmployeeAgent"`, `apex://CRA_ContactSearchAction`, `generatePromptResponse://CRA_Contact_Result_Presentation` with `"Input:<name>"`). The compiler does not resolve targets, so check them at publish. `sf agent preview --authoring-bundle` may crash for Employee agents without `default_agent_user` (forcedotcom/cli #3676): preview by API name after publishing. Grant agent access through `APP_Contact_Read_Agent` (Contact data comes from `DATA_Contact_Read_Only`; a non-admin needs both, assigned manually after approval, never automatically), and confirm the licence and permission needs of a non-admin user. Use `remaining_available` from `canShowRemaining` only, and never page when `refinementRequired` is true.

Read CONTEXT.md, context/requirements-status.md and context/technical-design.md. Create branch `feature/scgoe-95-s5-agent`.

Confirm the Agent Script and template-target syntax against the official reference. Generate authoring bundle `Contact_Read_Agent` (Employee type unless S1 decided otherwise) and write the script: variables (`criteria_*`, `selected_contact_id`, `last_result_ids`, `last_outcome`, `remaining_available`), subagents (search, follow-up, read-only guard, clarify), the two actions only, refinement merge, ordinal selection from stored ids, read-only refusal and clarification. Validate, deploy and publish inactive. Preview in simulated mode, then live as a non-admin user. Do not activate.

## Acceptance criteria

1. `sf agent validate authoring-bundle` passes.
2. The deployed agent's actions are exactly the search action and the template. No write action exists.
3. Preview covers one scenario for each of O1–O12.
4. A refinement carries earlier criteria forward. A follow-up question uses the selected Contact.
5. The agent is published and shown as Inactive, read back from the org.
6. Run-as-user confirmed from a debug log.

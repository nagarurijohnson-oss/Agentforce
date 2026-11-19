# S5. Agent Script agent

## Build prompt

Read CONTEXT.md, context/requirements-status.md and context/technical-design.md. Create branch `feature/scgoe-95-s5-agent`.

Confirm the Agent Script and template-target syntax against the official reference. Generate authoring bundle `Contact_Read_Agent` (Employee type unless S1 decided otherwise) and write the script: variables (`criteria_*`, `selected_contact_id`, `last_result_ids`, `last_outcome`, `remaining_available`), subagents (search, follow-up, read-only guard, clarify), the two actions only, refinement merge, ordinal selection from stored ids, read-only refusal and clarification. Validate, deploy and publish inactive. Preview in simulated mode, then live as a non-admin user. Do not activate.

## Acceptance criteria

1. `sf agent validate authoring-bundle` passes.
2. The deployed agent's actions are exactly the search action and the template. No write action exists.
3. Preview covers one scenario for each of O1–O12.
4. A refinement carries earlier criteria forward. A follow-up question uses the selected Contact.
5. The agent is published and shown as Inactive, read back from the org.
6. Run-as-user confirmed from a debug log.

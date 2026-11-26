# Knowledge Article Search — minimum permissions for agent users (2026-11-26)

Verified in MAX (`00DjV000003BVbRUAW`) in S15 (as the restricted user) and S17 (configuration read-back). None of these permission sets is
assigned automatically; assigning them to business users needs approval A5.

| Permission set | Grants | Why it's needed | Evidence |
|---|---|---|---|
| `DATA_Knowledge_Read_Only` | Read `Knowledge__kav`; `AllowViewKnowledge`; category visibility **Custom: 8 Scholarship_Programs categories** (not Campus_Services, not All Programs) | Without Read, the answer is "No published Knowledge article covers that". Without category visibility, every categorised article is hidden (F-2) | S15 D0/D1/D1b/D2; S17 read-back |
| `SYS_Knowledge_Default_DataSpace` | The `default` data space only; no other permissions | Without it, the retriever fails with "cannot describe data provider" (F-1) | S15 F0/F1; S17 read-back |
| Existing Contact sets (`APP_Contact_Read_Agent`, `APP_Contact_Read_Agent_Panel_Access`, `DATA_Contact_Read_Only`) | Agent access, the CRA action, Contact read | Unchanged | SV-8 |
| Lightning Experience User (profile or permission set) | UI access | The UAT profile lacks it (F-3) | S14 |

**Not needed:**
- Data Cloud User, Data Cloud Administrator or Architect, and Data Cloud licences.
- The Knowledge User feature licence (`UserPermissionsKnowledgeUser` is false for the UAT user).
- View All, Modify All, and any edit or publish permission.

**Execute Prompt Templates / Einstein Prompt Templates PSL — not needed for the agent (S18).** CRA UAT Restricted has neither,
yet in the Lightning panel (S14 P0) v3 returned field values that reach the reply only through the `CRA_Contact_Result_Presentation`
template (the planner sees only codes and Ids). A prompt template run by the agent therefore needs no prompt template permission for
the chatting user. The S15 flow harness needed both because a Flow's prompt template action checks them. `CRA_Knowledge_Answer` uses
the same action type; confirming it as the restricted user is step V-3 of `v4-restricted-user-validation-plan.md`.

**Review notes (S18):**
- Agent access is agent-wide: `APP_Contact_Read_Agent_Panel_Access` grants the agent (`BotDefinition 0XxjV000000oszhSAA`), so
  activating v4 offers the Knowledge route to every holder. Without the two Knowledge sets they get "No published Knowledge article
  covers that" (S15 D0): the design fails closed.
- Category visibility is a fixed list of 8. A new Scholarship_Programs category stays hidden until added to `DATA_Knowledge_Read_Only`.
- The data space set has no Data Cloud permissions; that it gives no direct Data Cloud query access is to be shown in plan step V-6.

**Manual steps per org:** category visibility and the data space scope are set in Setup (see
`context/session-kb-s17-release-permissions.md`); neither can be deployed as metadata.

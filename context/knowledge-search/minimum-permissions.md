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

**Execute Prompt Templates + Einstein Prompt Templates PSL — REQUIRED for agent users (S20, corrects S18).**
Add both to the agent user list:

| Permission | Why | Evidence |
|---|---|---|
| `EinsteinGPTPromptTemplatesPsl` (Einstein Prompt Templates licence) | Needed to hold the set below | S20 |
| `EinsteinGPTPromptTemplateUser` (standard Prompt Template User set: Execute Prompt Templates, Read on prompt template definitions) | Without it the agent's `present_results` and `answer_from_knowledge` steps are silently dropped: 0/27 vs 23/27 sessions ran `present_results` (no other change) | S20 |

S18 concluded the opposite from S14 P0 panel replies, but those were captured while the S14 test set granted the
permission. Details: `../session-kb-s20-phaseA-permission-compare.md`. S22 confirmed on v7: with this set and licence but without the Knowledge sets, Contact
works and Knowledge fails (platform error, D-8b). Still to confirm as the restricted user: the Knowledge answer with
all five grants (plan `v7-restricted-user-phaseA-plan.md`, step A-1).

**Review notes (S18):**
- Agent access is agent-wide: `APP_Contact_Read_Agent_Panel_Access` grants the agent (`BotDefinition 0XxjV000000oszhSAA`), so
  activating v4 offers the Knowledge route to every holder. Without the two Knowledge sets they get "No published Knowledge article
  covers that" (S15 D0): the design fails closed.
- Category visibility is a fixed list of 8. A new Scholarship_Programs category stays hidden until added to `DATA_Knowledge_Read_Only`.
- The data space permission set has no Data Cloud permissions. S23 A-5: as CRA UAT Restricted with all five grants, direct `/ssot/query-sql` was refused (403); the user also has no API Enabled, so the refusal is at the API-access layer. Agent users do not need API Enabled.
- S23 Phase A: with grants #1–#5 the restricted user passed 135/135 turns on v7 (Knowledge cited, Contact within sharing and FLS, no D-8b).

**Manual steps per org:** category visibility and the data space scope are set in Setup (see
`context/session-kb-s17-release-permissions.md`); neither can be deployed as metadata.

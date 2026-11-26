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

**Still to confirm before v4 is activated:** whether running the Knowledge template inside the agent needs Execute Prompt
Templates or the Einstein Prompt Templates PSL for the chatting user. The S15 flow harness needed them.

**Manual steps per org:** category visibility and the data space scope are set in Setup (see
`context/session-kb-s17-release-permissions.md`); neither can be deployed as metadata.

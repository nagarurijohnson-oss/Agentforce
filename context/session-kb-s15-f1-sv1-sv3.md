# Knowledge Search — F-1 root cause, SV-1 / SV-3 as CRA UAT Restricted (2026-11-26)

Org: MAX Developer Edition `00DjV000003BVbRUAW`. Tested as **CRA UAT Restricted** (`005jV000003sYUP`) via Login As, never as an administrator.
Approval: temporary, minimum-necessary Data Cloud access for F-1 / SV-1 / SV-3 (Nagaruri Johnson, 2026-11-26). Deletion of the test components confirmed on the IRREVERSIBLE prompt.

## Test harness
Temporary screen flow `SF_UAT_Knowledge_Answer_Harness` calling the live **CRA_Knowledge_Answer v6** template (question only, retriever bound in the template), the same call path Agent v4 uses. Agent v4 itself is Inactive and was not used for the restricted runs.

## F-1 — verified root cause
| Phase | Grants beyond the user's original 4 | Result |
|---|---|---|
| F0 | Einstein Prompt Templates PSL, harness set, Knowledge all categories. **No Data Cloud access** | 2/2 faulted: `[UndefinedResolutionError] Error while executing the following data provider: KA_CRA_Scholarship_Knowledge_1Cx_VbRab635d61, Error: Error occurred while resolving data providers: cannot describe data provider` |
| F1 | + `SYS_UAT_DC_Default_DataSpace` (only the association with the **default** Data Cloud data space; no user, object or field permissions) | 2/2 answered correctly (KT-01 → 000001004 `ka0jV000000nIDXQA2`; KT-12 → "Which one do you mean?") |

**Root cause:** the user running the template had no membership of the data space holding the search index (`DataSemanticSearch` KA_CRA_Scholarship_Knowledge, data space `0vhjV0000008CwrQAE` = default). Without it, the platform can't describe the retriever's data provider. **Data space membership alone fixes it.** The standard **Data Cloud User** permission set was not needed and was not assigned: it grants no data space here. No Data Cloud licence was assigned (GenieDataPlatformStarterPsl stayed at 2 used). Data Cloud Administrator/Architect was not granted.

## SV-1 — Knowledge object access (PASS for the tested cases)
| Phase | Knowledge access | KT-01 merit renewal | KT-12 "How do I appeal?" | KT-12S scholarship appeal |
|---|---|---|---|---|
| D0 | none | "No published Knowledge article covers that." 2/2 | same 2/2 | same 2/2 |
| D1 | Read + all categories | 3.3 GPA, cites 000001004 2/2 | lists Scholarship Appeal + Library Fine Appeal 2/2 | cites 000001010 `ka0jV000000nIF9QAM` 2/2 |
| D1b | production `DATA_Knowledge_Read_Only` (category visibility None) | no article 2/2 | no article 2/2 | — |

With data-space access but no article access, no article content reached the user. D1b confirms F-2: the production read-only set on its own shows nothing, because every article is categorised.

## SV-3 — data category visibility (PASS for the tested cases)
D2: Read + every category **except Campus_Services**.
- KT-12 "How do I appeal?" 3/3 listed only **Scholarship Appeal Process**. The Campus article **Library Fine – Appeal Process (000001007, `ka0jV000000nIFCQA2`)** listed in D1 never appeared.
- KT-01 3/3 and KT-12b/KT-12S 6/6 still answered from authorised articles with correct citations.
- No citation in any phase pointed at an article the user could not read. The Campus article ID appears in none of the 180 debug logs.

## Run-as / service-user context
- All 180 debug logs from the runs carry only the restricted user (372 `USER_INFO` lines; no other user IDs).
- The Data Cloud vector query itself runs server-side and is not visible in Apex debug logs, so a platform identity behind it can't be ruled out from logs. **Behaviourally, the results are filtered by the chatting user's own article and category access** (D0, D1b, D2). The index reports `SharingStatus = REGULAR`.
- No external requests were made in any phase.

## Not covered
- Field-level security on article fields: the standard fields take no FLS (`IsPermissionable=false`), so there is nothing to test.
- Agent v4 in the Lightning panel as the restricted user (v4 is Inactive by instruction).
- Captures are final answers and citations. The raw retriever passages are not exposed to the user context.

## Restoration (all read back 2026-11-26)
- UAT user: back to its 4 original assignments (`APP_Contact_Read_Agent`, `APP_Contact_Read_Agent_Panel_Access`, `DATA_Contact_Read_Only`, profile set); no PSLs; profile, role (none) and Knowledge User flag (false) unchanged. Org total assignments 27, as before.
- Deleted: 4 permission sets (deploy `0AfjV000006nJPRSA2`), the flow (inactive version deleted through the Tooling API after the combined destructive deploy `0AfjV000006nJNpSAM` failed with "insufficient access rights on cross-reference id" and rolled back), the debug level `SF_UAT_KB_S15` and its trace flag. Copies: `scripts/kb/s15-evidence/deleted-metadata/`.
- Login As (`enableAdminLoginAsAnyUser`): **false**, read back from the org.
- Contact_Read_Agent v3 Active, v4 Inactive; Contacts 157; articles 13 Online + 1 Draft; index READY.

## Release blockers remaining
- **L-1 (High):** open.
- **F-1 → decision:** normal users need membership of the default data space (a custom set like the deleted one, assigned to agent users) before Knowledge answers work. Lal must approve that grant (A5).
- **F-2:** `DATA_Knowledge_Read_Only` needs category visibility (All or Custom) before it is useful.
- SV-2 archive-and-resync check, and the A5 acceptance of the SV-1 result, are still outstanding. v4 is not activated.

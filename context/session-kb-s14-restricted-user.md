# Knowledge Search: restricted-user security validation (Session 14, 2026-11-26 IST)

**Outcome:** B-1 resolved with a temporary, reverted setting. SV-4 passes. SV-1 and SV-3 pass for the platform's own article access (UI), and the retriever **fails closed** for the restricted user in every configuration. Whether retrieval filters content by the user's article access *once the user can run the retriever* is **not proven**: it needs a Data Cloud data-space grant that was not approved. Contact_Read_Agent **v3 Active, v4 Inactive** throughout. All temporary changes reverted and read back; before/after snapshots identical. L-1 open (High, release blocker). No PR merged; no release approved.

## Method (approved 2026-11-26)
- Login As: `SecuritySettings.enableAdminLoginAsAnyUser` deployed `true` (`0AfjV000006mlsPSAQ`) at the start, deployed `false` (`0AfjV000006mnuDSAQ`) at the end; read back `false`.
- Temporary metadata (check-only `0AfjV000006ml4PSAQ` 98/98, deploy `0AfjV000006ml9FSAQ`; harness set update check-only `0AfjV000006mlxFSAQ`, deploy `0AfjV000006mkrWSAQ`):
  - Flow `SF_UAT_Knowledge_Answer_Harness`: calls `CRA_Knowledge_Answer` (v6, same template and retriever as agent v4) as the running user; shows the reply and `$User`.
  - `SYS_UAT_KB_Harness`: RunFlow, ExecutePromptTemplates, **LightningExperienceUser** (added: the Minimum Access profile has no Lightning access; without it Log in as lands in Classic). No object access.
  - `DATA_Knowledge_UAT_No_Campus`: Read on Knowledge__kav + Allow View Knowledge; category visibility **Custom: 8 categories, Campus_Services excluded**, set in Setup (the Metadata API refused it: `Element {http://soap.sforce.com/2006/04/metadata}categoryGroupVisibilities invalid at this location in type PermissionSet`).
  - Einstein Prompt Templates licence, trace flag and debug level on CRA UAT Restricted only.
- Phases tested separately (never two Knowledge sets at once): **P0** no Knowledge access; **P1** `DATA_Knowledge_Read_Only` only; **P2** `DATA_Knowledge_UAT_No_Campus` only. Admin control run of the same harness.

## Results
| Check | P0 (none) | P1 (Read Only) | P2 (No Campus) | Admin control |
|---|---|---|---|---|
| Harness running user | UAT user | UAT user | UAT user | admin |
| Retriever (8 runs per phase: KT-01, KT-13, library-fine appeal, KT-12 ×2) | 8/8 refused | 8/8 refused | 8/8 refused | 4/4 answered |
| Article pages, 13 Online + 1 Draft | 0 shown ("isn't available") | 0 shown ("couldn't find the record") | **11 shown; 2 Campus + Draft refused** | — |
| Panel Knowledge link, Merit Renewal (A04) | refused | refused | **opens article** | — |
| Panel Knowledge link, Parking (A13, Campus) | refused | refused | **refused** | — |

Retriever error (verbatim, every UAT run): `[UndefinedResolutionError] Error while executing the following data provider: KA_CRA_Scholarship_Knowledge_1Cx_VbRab635d61, Error: Error occurred while resolving data providers: cannot describe data provider`. The flow took its fault path; no article text, title or count was shown.

Admin control: KT-01 answered 3.3 GPA / 24 credits citing A04 (`ka0jV000000nIDXQA2`, 000001004); KT-12 listed both appeal titles (incl. Campus "Library Fine – Appeal Process"); parking and library-fine questions got the Rule 1 reply.

### SV verdicts
- **SV-4 (run-as) — Pass.** Debug log `07LjV000003k3fVUAQ`: `USER_INFO … 005jV000003sYUP|cra.uat.restricted@…` around `FLOW_ACTIONCALL_DETAIL … Generate Prompt Response|CRA_Knowledge_Answer`. Template grounding executes as the chatting user.
- **SV-1 (article permissions) — Partial pass.** Platform article access follows object permission and category visibility. The retriever never returned content to the restricted user (fail closed in all 24 runs). Not proven: filtering when the user *can* run the retriever.
- **SV-3 (unauthorised content) — Partial pass.** Category visibility hides Campus articles in the UI and via links; no unauthorised content reached the user via the harness. Same gap as SV-1.
- **Finding F-1 (High, design):** the restricted user cannot use Knowledge answers at all. Running the retriever appears to need Data Cloud data-space access (likely Data Cloud User with the default data space; unconfirmed). Agent v4 previews passed only because the admin has Data Cloud access. Before v4 can serve normal users, a decision is needed on that grant, and SV-1/SV-3 must then be re-run with it.
- **Finding F-2:** `DATA_Knowledge_Read_Only` has category visibility None, so on its own it shows no categorised article (all 13 are categorised). It needs Custom/All visibility, or a role with visibility.
- **Finding F-3:** the Minimum Access profile lacks Lightning Experience User; restricted users need it from their real profile to use the panel.

### Contact security as the UAT user (v3 panel, P0)
C1 email `priya.synthwell@…`: 1 match (the private Contact with the same email hidden) · C2 private "Zed Hiddenmore": neutral no match · C3 "Jordan Samename": 2 (admin sees 3) · C4 edit request declined · C5 Knowledge question on v3: clarification, no content. Links correct. No external requests in any phase.

### Not done in this session
- Mixed Contact + Knowledge requests as the UAT user: impossible while v4 is inactive and the retriever is refused (baseline admin preview of v4 earlier this session: 23/23).
- FLS swap (`DATA_Contact_Read_Limited_UAT`) in the panel; post-restore Apex/agent regressions (baseline this session: Apex 102/102 `707jV00000CXuQL`, v3 suite 23/27 same 4 misses, v4 suite 23/23, template 34/34).
- L-1 and the short merit-question ambiguity: root causes recorded in the todo (L-1: the final planner step regenerates the relayed reply and loses escapes; ambiguity: lower-case "merit renewal" alone 8/8 asks which). No change made; fixes need approval.

## Restoration (read back)
Login As `false`; UAT assignments = the original 4 (profile, APP_Contact_Read_Agent, APP_Contact_Read_Agent_Panel_Access, DATA_Contact_Read_Only); no PSL; flow, both UAT-only sets, trace flag and debug level deleted. Snapshots (`snapshot-before/after.json`): UAT user, 27 assignments, 5 BotVersions, 157 Contacts, 14 articles identical.

Evidence: `scripts/kb/s14-restricted-user/`.

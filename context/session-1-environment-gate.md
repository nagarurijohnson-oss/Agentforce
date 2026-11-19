# Session 1 — environment gate report (SCGOE-95)

**Date:** 2026-11-19 · **Run by:** Revecast Orchestrate for Nagaruri Johnson · **Mode:** read-only. No sharing setting, permission, agent or org metadata was changed. Nothing was deployed or published.

**Org:** `MAX`, org id 00DjV000003BVbRUAW, `orgfarm-232477b490-dev-ed.develop.my.salesforce.com`, Developer Edition, `IsSandbox = false`, API version 68.0. This is a production-type org, not a sandbox.

A status here is a dated claim. Check it against the org before relying on it.

## Verdict

**No blocker to the agreed design** (Agent Script orchestration → Invocable Apex retrieval → Prompt Template presentation, Employee agent, native UI). Ready for Session 2, with the pending items below carried forward. Session 2 itself (Apex search service and tests) depends on none of them.

## Gate results

| # | Question | Result | Evidence |
|---|---|---|---|
| G1 | New Agentforce Builder and Agent Script available | **Yes, verified** | `AiAuthoringBundle` is in the org's metadata type list and lists cleanly (0 bundles). `AgentPlatformSettings.enableAgentPlatform = true`. The CLI `sf agent` commands (generate authoring-bundle, validate, publish, preview) are present in CLI 2.151.7. A local probe script compiled in the org (see G2), and a deliberately broken copy returned real compile errors. |
| G2 | Employee agent that respects the logged-in user's permissions | **Yes, verified for compile; run-as-user still to prove at runtime (S5)** | Probe script with `agent_type: "AgentforceEmployeeAgent"`, no `default_agent_user`, an `apex://` action and a `generatePromptResponse://` action: `sf agent validate authoring-bundle` → `{"success":true}`. The existing `Employee_Leave_Assistant` is `AgentType = AgentforceEmployeeAgent` with `BotUserId = null` (no fixed agent user). Salesforce documents that Employee agents run as the logged-in user. |
| G3 | Prompt Builder available, and can receive the Apex output | **Available, verified. End-to-end hand-off pending (S4/S5)** | `EinsteinGptSettings.enableEinsteinGptPlatform = true`. `/actions/custom` includes `generatePromptResponse` (47 standard templates exposed). Licence "Einstein Prompt Templates" 1 of 5,000 used; John Steve holds the Prompt Template Manager permission set. 0 custom `GenAiPromptTemplate` exist, so nothing to conflict with. The Agent Script compiler accepted a template action with an `"Input:contactsJson"` string input, but it did **not** check that the template exists (the probe referenced a template that does not exist and still compiled). The real hand-off is proven only when S4 builds the template and S5 publishes. |
| G4 | Required Contact fields and permissions | **Yes, verified** | Contact describe: `Name`, `FirstName`, `LastName`, `AccountId`, `Title`, `Email`, `Phone`, `MailingStreet/City/State/PostalCode/Country`, `MailingAddress` all exist and are filterable (`MailingAddress` is not sortable). `MailingStateCode` and `MailingCountryCode` also exist, so state and country picklists appear to be on: match location on the text fields `MailingCity/State/Country`. Standard User and Read Only profiles read Contact and its FLS on Title, Email, Phone, MailingAddress, AccountId. Minimum Access – Salesforce has no Contact object access. |
| G5 | How to validate record-level and field-level security | **Path found, no setting change needed. Execution pending (S3, S6)** | See "Security validation plan" below. |
| G6 | Reusable existing Apex | **No reuse; leave existing code untouched** | See "Existing components" below. |

## Corrections to earlier records

1. **Environment:** Developer Edition org, not a sandbox (`Organization.OrganizationType = Developer Edition`, `IsSandbox = false`).
2. **Contact sharing:** the design session recorded Contact internal sharing as Public Read/Write. The org setting is actually `DefaultContactAccess = ControlledByParent`, with `DefaultAccountAccess = Edit` (Public Read/Write). In effect, every internal user can see a Contact that has an Account. **A Contact with no Account is private:** only its owner and users with View All see it. All 20 current Contacts have an Account (0 without one), and there are 13 Accounts.

## Security validation plan (no sharing change)

- **Record level, in Apex tests (S2/S3):** `System.runAs` a test user on Minimum Access – Salesforce plus a test-only grant of Contact Read. Create `CRA-TEST` Contacts **without an Account** owned by another user. They must not appear in results, counts or duplicate checks, and `contactId` lookups must return the neutral NO_MATCH. This exercises real sharing because Contacts without an Account are private under `ControlledByParent`.
- **Field level, in Apex tests (S3):** the same runAs user without Read on, for example, `Email` and `Phone`. Those values must read "Not available" and never appear anywhere in the output.
- **CRUD:** a runAs user with no Contact Read must get the neutral response, not an error that reveals anything.
- **Live UAT (S6, needs approval before anything is created):** one restricted user. Two of the four Salesforce user licences are free (2 used). Use the Minimum Access – Salesforce profile, plus `CRA_Contact_Read_Agent_User` (Contact Read, FLS on the needed fields, Apex class access, agent access), plus a UAT permission set that withholds chosen fields. Then chat as that user against a mix of synthetic Contacts with an Account (visible) and without one, owned by the admin (hidden).
- **Decision D-E:** Contact sharing does not need to change. A temporary Private OWD is no longer needed to prove record-level security.

## Licences and access a non-admin chat user needs (verified counts, requirement partly pending)

- Salesforce user licence: 2 of 4 used.
- "Agentforce (Default)" permission set licence: 1 of 5 used.
- "Einstein Prompt Templates": 1 of 5,000 used.
- Agent access is granted per agent through a permission set or profile ("Enabled Agent Access"). Today **no permission set grants access to `Employee_Leave_Assistant`** (0 `SetupEntityAccess` rows for its BotDefinition). The new agent needs its own grant.
- **Pending (S5):** confirm whether a non-admin user also needs the Agentforce (Default) licence or the Prompt Template User permission set to use the agent and run the template, and confirm the permission set metadata element for agent access.

## Existing components

| Component | What it is | Used by | Verdict |
|---|---|---|---|
| `ESA_RecordSearchAction` (Apex, API 67) | `with sharing` invocable. Uses SOSL `FIND :term IN ALL FIELDS` across Account, Contact and Case, `stripInaccessible`, and a per-object `LIMIT` capped at 20. No counts, no outcome classes, no phone normalisation, no USER_MODE on the query. | Dependency API: only `ESA_RecordSearchActionTest`. GenAiFunction `ESA_Record_Search` and topic `Record_Search_And_Insights` exist, but **neither is linked to the active `Employee_Leave_Assistant` planner** (its bundle has local topics only). | Do not extend. Changing it could affect the standalone topic. Its contract cannot express counts above 20 or the outcome codes. Keep decision D-H: new `CRA_` classes. |
| `Employee_Leave_Assistant` (Employee agent, v1 Active, legacy planner bundle, not Agent Script) | Leave agent | — | Do not touch. The new agent is a separate authoring bundle. |
| `AccountProcessor`, `AnimalLocator`, `ParkLocator`, `ParkService`, `AsyncParksService` and their tests/mocks | Trailhead exercises | — | Not relevant. |

Org-wide Apex coverage is 82% (org profile 2026-11-18). This is a production-type org, so every deploy runs tests: deploy with `RunSpecifiedTests` on the `CRA_` tests, and keep existing classes untouched.

## Agent Script syntax confirmed in this org (compiler, CLI 2.151.7)

- Block keywords: `system`, `config`, `variables`, `language`, `start_agent`, **`subagent`** (not `topic`). The design text that says "subagents" is correct.
- `config.agent_type: "AgentforceEmployeeAgent"` compiles without `default_agent_user`.
- Apex action target: `target: "apex://<ClassName>"` (class name only).
- Prompt template action target: `target: "generatePromptResponse://<TemplateDeveloperName>"`, input key quoted as `"Input:<apiName>"`, output `promptResponse` with `is_used_by_planner: True` and `is_displayable: True`.
- Binding in reasoning: `@actions.<name>` with `with <input> = ...`.
- The compiler checks syntax and references inside the script, but **not** that Apex classes or templates exist in the org. Publish (S5) is where that is checked.
- Known CLI issue (forcedotcom/cli #3676, open): `sf agent preview --authoring-bundle` can crash for an Employee agent without `default_agent_user`. Workaround in S5: preview by API name after publishing.

## Commands run (all read-only against the org; the probe files stayed in a local scratch folder outside this repository)

```
sf org list --json
sf org list metadata --metadata-type {AiAuthoringBundle|GenAiPlannerBundle|GenAiPlugin|GenAiFunction|GenAiPromptTemplate|GenAiPromptTemplateActv|Bot|BotVersion} -o orgfarm-232477b490-dev-ed
   → AiAuthoringBundle [] · GenAiPlannerBundle [Employee_Leave_Assistant] · GenAiPlugin [Salesforce_Guidance, Record_Search_And_Insights]
     GenAiFunction [ESA_Record_Search, Get_My_Leave_Records] · GenAiPromptTemplate [] · Bot [Employee_Leave_Assistant]
   (GenAiPlannerDefinition → INVALID_TYPE: superseded by GenAiPlannerBundle; not needed)
sf org list metadata-types → includes AiAuthoringBundle, GenAiPromptTemplate, GenAiPlannerBundle, AiAgentDefinition
sf project retrieve start (to scratch) Settings:AgentPlatform, Settings:EinsteinGpt, GenAiPlannerBundle:Employee_Leave_Assistant,
   GenAiPlugin:Record_Search_And_Insights, ApexClass:ESA_RecordSearchAction
SOQL: Organization, User, Profile, PermissionSetLicense, PermissionSetLicenseAssign, PermissionSet, PermissionSetAssignment,
   ObjectPermissions/FieldPermissions (Contact), BotDefinition, BotVersion, SetupEntityAccess, ApexClass, UserRole, COUNT() Contact/Account
Tooling: MetadataComponentDependency where RefMetadataComponentId = ESA_RecordSearchAction → [ESA_RecordSearchActionTest]
REST: GET /actions/standard, /actions/custom, /actions/custom/generatePromptResponse
sf sobject describe --sobject Contact
sf agent generate authoring-bundle --no-spec (local file only)
sf agent validate authoring-bundle -n CRA_Probe → {"success":true}; broken copy → CompileAgentScriptError (expected)
sf org list metadata --metadata-type AiAuthoringBundle afterwards → [] (nothing saved to the org)
```

## Pending (owner · when)

1. Prove Apex output → Prompt Template → displayed response end to end · Orchestrate · S4 (template) and S5 (publish).
2. Confirm run-as-user at runtime from a debug log · Orchestrate · S5.
3. Confirm the licence and permission needs of a non-admin chat user, and the permission set metadata element for agent access · Orchestrate · S5.
4. Create the SFDX scaffold (API 68.0) and `CRA_Contact_Read_Agent_User` in source · Orchestrate · start of S2 (repository only); deploy with S3, after approval.
5. Create the restricted UAT user and permission set · Nagaruri Johnson to approve · S6.
6. Confirm defaults D-B, D-C, D-D, D-F and D-G · Nagaruri Johnson · before S2 closes.
7. Edit the PR #1 description (it still says requirements await an attachment) · Nagaruri Johnson · before merge.
8. Watch Einstein request usage on the Developer Edition during S5–S6 preview and evaluation runs · Orchestrate · S5–S6.

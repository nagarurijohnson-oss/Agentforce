# S28 — Salesforce org-level verification and close-out (2026-11-27)

Session: AGENTFORCE_BUILD 27f29662 (continuation). Scope: the Salesforce org only (no GitHub Actions, secrets,
workflow or environment work). No agent activated, no active version changed, no business record changed, no
permission assigned, no new agent, no new Apex, Flow or LWC. Evidence from S15–S27 reused; one targeted Apex test
class run, two check-only validations.

## 1. Org state read back

| Item | State |
|---|---|
| Contact_Read_Agent | v3 **Active**; v1, v2, v4, v5, v6, v7 Inactive |
| Employee_Leave_Assistant | v1 Active, not touched |
| Temporary (expiring) permission set assignments | None |
| Connected app `SCGOE95 Agent Rollback` | Not present (0) |

## 2. Knowledge articles (item 1)

14 synthetic articles, latest versions: **13 Online, 1 Draft** (000001008 STEM Futures – Deadline Extension).
All are internal-app visible only (`IsVisibleInApp` true; not PKB, customer or partner). Every article has one
`Scholarship_Programs` category:

| Category | Articles |
|---|---|
| Merit | 000001003, 000001004 |
| STEM | 000001005, 000001008 (Draft) |
| Need_Based | 000001000 |
| International | 000001001 |
| Arts_Humanities | 000001002 |
| Graduate_Research | 000001006 |
| Athletic | 000001011 |
| General_Aid | 000001009, 000001010, 000001012 |
| Campus_Services | 000001007, 000001013 (hidden from agent users by design) |

000001011 shows two category rows: version 1 is **Archived** (`ka0jV000000nIF7QAM`) and version 2 is Online and latest (`ka0jV000000nIqDQAU`). Archived versions are never cited (S15 SV-2).
Knowledge `Knowledge__kav` internal sharing: Public Read/Write; external: Private.

## 3. Knowledge stack (item 2)

| Component | State | Repo vs org |
|---|---|---|
| Data Library `CRA_Scholarship_Knowledge` | Present (S27 read-back; READY since K3) | n/a |
| Retriever `KA_CRA_Scholarship_Knowledge` | Bound in `CRA_Knowledge_Answer` (Einstein Search data provider) | n/a (no retriever metadata type) |
| Prompt Template `CRA_Knowledge_Answer` | Published, Flex, 6 versions, active `_6`; rules for programme match, ambiguity (Rule 3), no match (Rule 4), one `Source:` link built from SourceRecordId | **Identical** |
| GenAiFunction `Knowledge_CRA_Scholarship_Knowledge` | Created by the library; **not used** by any agent version (documented in `kb-data-library.md`) | Not in repo, intentionally |
| `CRA_Knowledge_Answer_v6_Candidate` | Test harness template, not referenced by any agent; kept by decision of 2026-11-25 | Copy in `scripts/kb/harness/` |
| Data category group `Scholarship_Programs` | Present | **Identical** |

## 4. v7 Agent Script (item 3)

Org `AiAuthoringBundle:Contact_Read_Agent_7` (target `Contact_Read_Agent.v7`, 1,050 lines) is **byte-identical** to the
repo's `Contact_Read_Agent.agent`. Structure:

| Requirement | Where in v7 | Behavioural evidence |
|---|---|---|
| Contact search | `contact_search` → `apex://CRA_ContactSearchAction` → `generatePromptResponse://CRA_Contact_Result_Presentation` | S22 27/27, paging 60/60 |
| Knowledge Article search | Knowledge route → `generatePromptResponse://CRA_Knowledge_Answer` (retriever grounding, no Apex) | S22 23/23 |
| Programme-specific answers | Template programme-match rule | S22 |
| Citations and authorised links | Template `Source: [Title](/lightning/r/Knowledge__kav/<SourceRecordId>/view) (Article …)`; relative link only | S24 panel run |
| Ambiguous programme clarification | Template Rule 3 (ADR-K3) | S22 |
| Combined Contact + Knowledge | Router action "both read-only searches" (lines 865–891 call the Apex action and the Knowledge template) | S22 mixed cases |
| Read-only guard, clarify | `read_only_guard`, `clarify` subagents | S22 guards |

## 5. Salesforce-side issues found and fixed (item 4)

| # | Finding | Fix | Org change? |
|---|---|---|---|
| F-S28-1 | Repo `SYS_Knowledge_Default_DataSpace` lacked the `dataspaceScopes` block the org holds (`default`, data access ALL, object access BY_POLICY, no definition rights). Redeploying the repo copy could not reproduce the org. S17 said the scope "isn't in the XML"; at API v68 it is | Repo synced from the org. Check-only deploy **`0AfjV000006p3y5SAA` Succeeded** (1 component): the scope is now deployable, so manual step **M2 is no longer manual** | No |
| F-S28-2 | Repo copies of `DATA_Knowledge_Read_Only`, `DATA_Contact_Read_Only`, `SYS_Agent_Rollback_Automation` and template `CRA_Contact_Result_Presentation` differed from the org only in defaults (`viewAllFields false`, `overridable false`), element order and XML entity encoding | Repo synced from the org (org is the source of truth) | No |
| F-S28-3 | Connected-app template asked for the `RefreshToken` scope and an infinite refresh-token policy; the JWT bearer flow issues no refresh token. Element order did not follow the schema | Template reduced to scope `Api` only, no refresh policy, schema order | No |
| F-S28-4 | The S25 template pre-authorised the permission set **by label**; whether Salesforce resolves that was unverified | Check-only deploy of the template **without any certificate element** (no placeholder): **`0AfjV000006p4CbSAI` Succeeded**. Connected apps read back afterwards: 0 | No |

Category visibility (M1) remains a Setup step: the Metadata API rejects `categoryGroupVisibilities` on PermissionSet
(S14 verbatim error) and the retrieve returns none. Last verified behaviourally in S15 (SV-3) and S23 (135/135).

## 6. OPS-1 org side (item 5)

| Item | State |
|---|---|
| Rollback user `005jV000003ufYDQAY` | Active; Salesforce Integration licence; profile "Minimum Access – API Only Integrations" |
| Assignments | `SYS_Agent_Rollback_Automation` plus the profile's own set; nothing else |
| `SYS_Agent_Rollback_Automation` | API Enabled; Customize Application (activation dependency, decision 7); **no** Modify All, View All, Manage Users, Author Apex |
| Certificate `rollback.crt` | **Not received** in this session (no attachment). **Certificate deployment pending.** No placeholder was deployed |
| Connected app | Template ready and validated (F-S28-3, F-S28-4); deploy waits for the certificate (already approved) |

## 7. L-1 (item 6)

| Check | Result |
|---|---|
| Deployed `CRA_ContactSearchAction` / test class vs repo | Identical apart from whitespace and line endings |
| Targeted run `CRA_ContactSearchActionTest` (run `707jV00000ChBON`) | **35/35 pass; `CRA_ContactSearchAction` 100% (166/166 lines)**. The org's coverage record had been cleared by the S25 redeploy and is now refreshed |
| Synthetic Contact `003jV00000HOooHQAT` | Still holds its original text (Markdown, `javascript:` link, bare URL); not modified in S28 |
| Live Agent API on v3 with planner traces | S25 4/4, S26 4/4 (reused, not re-run) |
| Lightning panel as restricted user (P-1 to P-5) | **Not run**: needs a v7 window, which waits for OPS-1 sign-off and separate approval |

## 8. Restricted-user access (item 7) — from existing evidence

| Control | Evidence | Today |
|---|---|---|
| Knowledge Read + Allow View Knowledge, no edit/publish | `DATA_Knowledge_Read_Only` XML | Confirmed in org |
| Category visibility (8 categories, not Campus_Services) | S15 SV-3, S17 | Setup only; not readable through the API |
| Draft/archived never returned | S15 SV-2, S22 | 1 Draft article still unpublished |
| Contact sharing, CRUD, FLS, USER_MODE | S14–S23; `CRA_ContactSearchSecurityTest` | Unchanged classes |
| Prompt template permission | Decision K10 (`decisions/2026-11-26-kb-k10-prompt-template-user-for-agent-users.md`) | — |
| UAT user `cra.uat.restricted@…` | Holds `APP_Contact_Read_Agent`, `DATA_Contact_Read_Only`, `APP_Contact_Read_Agent_Panel_Access` only; the Knowledge grants were removed after the last window (baseline) | No assignment made |
| Other users | Only the admin `johnsteve112345…` holds one of these sets (`APP_Contact_Read_Agent_Panel_Access`). No business user holds any CRA or Knowledge set | No assignment made |

## 9. Remaining org-level work

1. Deploy the rollback connected app once `rollback.crt` arrives; read it back; give Nagaruri the steps to copy the consumer key.
2. After OPS-1 live T1/T2/T5 and sign-off: a separately approved v7 window for the L-1 panel check P-1 to P-5.
3. Per target org at release: M1 category visibility and M3 retriever binding (Setup/Prompt Builder); M4 and M5 as in the release review.

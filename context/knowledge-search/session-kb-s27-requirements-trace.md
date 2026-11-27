# S27 — Requirements trace against Lal's SCGOE-95 scope, OPS-1 status (2026-11-27)

Session: AGENTFORCE_BUILD 27f29662 (continuation). Read-only checks only, plus documentation. No test suite was re-run:
every result below cites the session that produced it.

## Org state read back (2026-11-27, S27)

| Item | State |
|---|---|
| Contact_Read_Agent | v3 **Active**; v1, v2, v4–v7 Inactive |
| Employee_Leave_Assistant | v1 Active, not touched |
| Knowledge articles | 14 synthetic: 13 Online, 1 Draft |
| Data Library | `CRA_Scholarship_Knowledge` present (grounding source KNOWLEDGE) |
| Prompt templates | `CRA_Knowledge_Answer`, `CRA_Contact_Result_Presentation` present |
| Rollback sign-in app (connected app) | **Not deployed**: `rollback.crt` has not reached the session |

## Knowledge Article requirements

| Requirement | Status | Evidence |
|---|---|---|
| Use the existing 14 synthetic articles | Met | Org read back above; `kb-data-library.md` |
| Data Library `CRA_Scholarship_Knowledge`, retriever `KA_CRA_Scholarship_Knowledge` | Met | Library read back; retriever bound in Prompt Builder (ADR-K6, `decisions/2026-11-25-kb-k6-retriever-binding-in-prompt-builder.md`) |
| Prompt Template `CRA_Knowledge_Answer` | Met | Template present; grounding via Einstein Search data provider |
| Programme-specific answers | Met | S22 Knowledge/mixed/guards 23/23 on v7 (`session-kb-v5-validation.md`, `RELEASE-REVIEW-SCGOE-95-KB.md` §2) |
| Clarifying questions for ambiguous programmes | Met | ADR-K3 disambiguation (`decisions/2026-11-25-kb-k3-disambiguation.md`); covered by the S22 suite |
| No invented eligibility, GPA, deadlines or documents | Met | S22 suite; Draft article never cited (SV-2); grounding instructions in the template |
| Grounded article references and authorised links | Met | Template output; restricted-user panel run S24 Phase B (0 flags apart from L-1) |
| Combined Contact and Knowledge questions | Met | `contact_and_knowledge` topic; S22 mixed cases |
| Knowledge visibility, sharing, CRUD and FLS | Met | SV-1 object access, SV-2 draft/archived, SV-3 category visibility, SV-4 run-as (S15, S16); restricted user 89 sessions / 135 turns (S23) |
| Standard Agentforce components only, no new Apex/Flow/LWC for Knowledge | Met | Knowledge path is Data Library + retriever + Prompt Template; the only Apex is the Contact search action (ADR-K5) |

**Caveat:** all of the above was verified on **v7, which is Inactive**. Live users on v3 have Contact search only, with no Knowledge, until v7 is activated under A6.

## Contact search: Account ID support (completion item 5)

The approved scope (R2, `requirements-status.md`) is: full name, partial name, email, phone, **Account name**,
job title, location and combinations. Account **ID** is not in it, and Account name search is already built and tested.
**Decision: not implemented** (`decisions/2026-11-27-account-id-search-out-of-scope.md`). Lal can add it to scope; it would
be an Apex criteria change plus tests, with no new agent version.

## L-1

Fix deployed (S25), live Agent API checks clean with planner traces (S25: 4/4, S26: 4/4 hostile links/Markdown).
The restricted-user Lightning panel check (P-1 to P-5 in `session-kb-s26-l1-live-ops1-status.md`) needs a v7 window,
so it waits for OPS-1 sign-off and separate approval. **Not run.**

## OPS-1 status

| Control / step | State (S27) |
|---|---|
| Rollback user `005jV000003ufYDQAY` | Active, Salesforce Integration licence, API-only minimum profile, one permission set |
| `SYS_Agent_Rollback_Automation` | No Modify All, View All, Manage Users or Author Apex. **Customize Application is on** (a dependency of agent activation); flagged for Lal |
| Certificate `rollback.crt` | **Not received** (a local Mac path was given; no file was attached) |
| Connected app | Not deployed (waits for the certificate) |
| GitHub environment `agent-rollback` | **Created** 2026-11-27 09:06 UTC by Nagaruri |
| Environment deployment branches | **Defect found:** allows `main` only. Armed runs push from `rollback-arm/<id>`, so they would be refused the secrets. Add the rule `rollback-arm/*` (runbook step 3, corrected) |
| Environment secrets | Cannot be checked: the repository token gets 403 on secrets (by design, it cannot read them) |
| Workflow installed under `.github/workflows/` | **No** (no workflows on any branch; nothing on `main`) |
| Live T1, T2, T5 | **Not run.** Cannot run before the app, secrets and workflow exist |
| "Runs with Orchestrate closed" | **Not verified.** Follows from T1 running as a GitHub job |

## Remaining steps, in order

1. Nagaruri: attach `rollback.crt` to the chat (paperclip) or paste its text. Never the private key.
2. Orchestrate: validate, deploy and read back the connected app, pre-authorised for `SYS_Agent_Rollback_Automation` (already approved).
3. Nagaruri: copy the consumer key from Setup; add the 4 secrets; add the `rollback-arm/*` deployment-branch rule.
4. Nagaruri: install the workflow on `main` (GitHub runs schedule and manual workflows only from the default branch). This is a change to the default branch, so it needs your own action or approval.
5. Orchestrate: live T1, T2, T5 with v3 left Active; check the run artefacts for secrets (T6 live).
6. Nagaruri and Lal: OPS-1 sign-off. Then a separately approved v7 window for the L-1 panel check.

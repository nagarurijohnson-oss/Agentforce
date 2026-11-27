# Controlled plan: validate Contact_Read_Agent v4 as a real restricted user (prepared S18, 2026-11-26)

**Superseded for v7 by `v7-restricted-user-phaseA-plan.md` (S22).**

Status: **plan only — nothing here has run.** Each approval below is requested separately; none is implied by this document.

## Why two phases
- The Lightning panel always talks to the **active** version (it opens `POST /einstein/ai-agent/v1/agents/0XxjV000000oszhSAA/sessions`
  without a version). v4 cannot be reached in the panel without activating it.
- The Agentforce evaluation API **can** open a real Agent API session on the inactive v4 by `agent_version_id`
  (`0X9jV000001DhubSAC`) without activating it (S18: 122 sessions, `bot_version_id` confirmed in the session state, v3 still Active afterwards).
- So: **Phase A** tests v4's behaviour as the restricted user through the Agent API with no activation. **Phase B** is a short,
  separately approved activation window that tests the Lightning panel itself.

## Approvals needed (Phase A)
1. Temporarily turn on "Administrators Can Log in as Any User" (as in S14), off again in the same run, read back.
2. Assign, to **CRA UAT Restricted only** (`005jV000003sYUPQA2`, a test user, not a business user), one phase at a time:
   `DATA_Knowledge_Read_Only`, then also `SYS_Knowledge_Default_DataSpace`. Both removed at the end.
3. A debug trace flag on the UAT user for SV-4 evidence (removed at the end).
4. Agent sessions as that user on inactive v4 (read-only actions, synthetic data).

## Phase A — v4 as the restricted user, no activation
| Step | Configuration | What runs | Pass criteria |
|---|---|---|---|
| V-0 | Snapshot (UAT user's 4 sets, 27 assignments, 5 agent versions, Contacts, articles); Log in as on | In the Log in as browser, obtain the UAT user's named-user token (`/agentforce/bootstrap/nameduser`, the call the panel itself makes) and open one evaluation session on v4 with "Find the contact with email priya.synthwell@synthetic.example" | Session state shows `user_id` = `005jV000003sYUPQA2` and `bot_version_id` = `0X9jV000001DhubSAC`. **If the evaluation API refuses the user, stop Phase A here and go to Phase B; record the refusal verbatim** |
| V-1 | No Knowledge sets (as today) | 5 Knowledge questions (KT-01, 06, 10, 13, 15) + the Contact suite subset (cases 1, 3, 8, 15, 19, 22 of CRA_S18) | Knowledge: no article text, title, count or link; neutral reply. Contact answers presented by the template (proves Contact template without Execute Prompt Templates, again on v4) |
| V-2 | `DATA_Knowledge_Read_Only` only | Same 5 Knowledge questions | Retriever refused (F-1) → neutral reply, no content, no technical detail |
| V-3 | Both sets | KT-01–15, 17 (two turns), 19, 20, 21, RG-01 | Same pass rules as the S18 admin run (23/23). Every cited Id is Online and in the 8 categories. **Campus articles 000001007 and the Library Fine article are never cited (SV-3).** This also settles the Execute Prompt Templates question for `CRA_Knowledge_Answer` (the user has neither the permission nor the licence) |
| V-4 | Both sets | Contact security: private Contact by email (hidden), duplicates "Jordan Samename" (user sees 2, admin 3), edit request (declined), mixed KT-19 | No private Contact data; duplicates not auto-picked; guard declines |
| V-5 | Trace flag on | One Contact search | Debug log `USER_INFO` shows the UAT user around `CRA_ContactSearchAction` (SV-4) |
| V-6 | Both sets | As the UAT user, a direct Data Cloud query (`/ssot/query-sql`) on the Knowledge DMO | Refused: the data space set gives the retriever access, not direct query access |
| V-7 | Both sets | As the UAT user: open each Id cited in V-3 in Lightning; draw V-3's real v4 replies in the panel renderer (S11 harness, test browser only) | Every link opens the cited published article; Campus articles refused; no external requests; L-1 recorded as observed |
| V-8 | Restore | Unassign both sets, remove trace flag and debug level, Log in as off; after-snapshot | Snapshot identical to V-0 apart from audit entries |

Load: about 60 agent sessions, paced one at a time (an hourly model limit was hit at about 110 sessions in 25 minutes in S18).

## Phase B — Lightning panel window (separate approval, only after Phase A passes and L-1 / D-5 are decided)
1. Snapshot; confirm v3 rollback command: `sf agent activate --api-name Contact_Read_Agent --version 3 --target-org orgfarm-232477b490-dev-ed --json`.
2. Activate the release candidate (v4, or v5 if the D-5/L-1 fixes are built), assign the two Knowledge sets to the UAT user only.
3. As the UAT user in the panel: KT-01, KT-06, KT-10 → "the merit one", KT-13, KT-19, the hostile Contact `Zoë "Zed" O'Brien-Núñez [VIP]`,
   paging (8 matches → "show me the other 3") ×5, an edit request. Click every record and article link.
4. Reactivate v3 (unless release is approved), unassign, read back versions and assignments.
Pass: as Phase A, plus links navigate correctly in the panel and no external requests. L-1 is checked, not expected to pass unless a fix is in.

## Release readiness — remaining steps, in order
1. **L-1 (High):** choose a remedy — "Show in conversation" plain output (links not clickable), a Lightning-type renderer (needs an
   ADR-003 exception for a custom LWC), or wait for Salesforce — and file the drafted support case. Build, then verify in Phase B.
2. **D-5 (High):** approve a v5 with deterministic paging (router-level `go_show_remaining`), or accept v4 on the evidence of 0/50
   with a paging gate in every regression. Recommended: v5.
3. **D-6 (Medium):** accept with monitoring, or reduce planner-chosen steps in the same v5.
4. **Phase A** (approvals above) — completes SV-1/SV-3/SV-4 through the agent and the Execute Prompt Templates question for Knowledge.
5. **A5:** Lal accepts SV-1/SV-3 evidence and the permission design; approves assigning `DATA_Knowledge_Read_Only` and
   `SYS_Knowledge_Default_DataSpace` to agent users.
6. **Per target org:** deploy the two permission sets, then the two manual Setup steps (category visibility, data space scope).
7. **Phase B** activation window and panel smoke test; rollback to v3 ready.
8. **Merge** the reviewed pull requests (draft PR #5 and the Knowledge branch) — not done by Orchestrate.
9. **Release approval.**

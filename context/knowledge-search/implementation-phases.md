# Knowledge Article Search — Implementation phases

Status 2026-11-25: **K0 (review) in progress. No build phase has started.** Each build phase runs in its own Agentforce Build session from the matching prompt in `context/build-prompts/K1-…` to `K6-…`, on its own feature branch with a draft pull request.

| Phase | Session type | Output | Gate to the next phase |
|---|---|---|---|
| **K0 Approvals** | This review | Decisions on ADR-K1 to K5 and approvals A1–A7 in [prerequisites.md](prerequisites.md) | Accepted decisions recorded in `context/decisions/`; ADR-K1 explicitly approved by Lal and Nagaruri Johnson |
| **K1 Enablement** | Agentforce Build | Knowledge and Lightning Knowledge on (**irreversible**, own IRREVERSIBLE confirmation); `Knowledge__kav` described; optional category group; `DATA_Knowledge_Read_Only` deployed, not assigned | Describe succeeds; Contact Apex 102/102; v3 still Active |
| **K2 Content** | Agentforce Build | 14 synthetic articles: 13 Online, 1 Draft; fixture `scripts/kb/articles.json` | SOQL shows 13 Online and 1 Draft `KB-TEST` articles; 0 Contacts changed |
| **K3 Data Library** | Agentforce Build | Library `CRA_Scholarship_Knowledge` READY; data stream, DMO, index and `KA_` retriever names in `context/kb-data-library.md`; credit use recorded (SV-10) | `adl status` READY; "merit eligibility GPA" returns A01; A14 not indexed (SV-2) |
| **K4 Template** | Agentforce Build | `CRA_Knowledge_Answer` deployed and Published; KT-01 to KT-16 run 3 times each through the template API | Acceptance criteria 1–4 met through the template alone |
| **K5 Agent v4** | Agentforce Build | Bundle edited, validated, previewed, deployed, **published but not activated** | Knowledge suite passes; Contact suite 23/27 with the same 4 known misses; SV-6, SV-8 pass |
| **K6 UAT and activation** | Agentforce Build | Panel tests KT-01 to KT-20 and L1–L9; security checks SV-1 to SV-4; v4 activated only after approval A6; handover report | All release-gate SV checks pass; Lal signs off |

## Phase rules

- One phase per session. A phase starts only when the previous gate is met and recorded in `context/progress.md`.
- Every phase confirms first that v3 is still Active and Contact Apex is 102/102.
- No phase changes `contact_search`, `read_only_guard`, `CRA_` classes, `CRA_Contact_Result_Presentation`, or the four existing permission sets or their assignments.
- No Apex, custom Flow or LWC in any phase.
- K1 is the only irreversible step in the plan. It asks for its own IRREVERSIBLE confirmation even after K0 approval.
- Rollback for K5/K6: reactivate v3. K1 (Knowledge) cannot be rolled back; K2 articles can be archived and deleted; the K3 library can be deleted.

## Estimated effort (what is left to build)

| Phase | Estimate |
|---|---|
| K1 | 0.5 day |
| K2 | 0.5 day |
| K3 | 0.5 day (includes sync waits) |
| K4 | 1 day (includes precision tuning) |
| K5 | 1 day |
| K6 | 1 day, after B-1 is cleared |

# S21–S22 — v7 (D-8 fail-closed) implementation, regression and restricted-user failure-path test (2026-11-26)

**Org:** MAX, `00DjV000003BVbRUAW`, Developer Edition (alias `orgfarm-232477b490-dev-ed` verified, IsSandbox false).
**Agent:** `Contact_Read_Agent` v7 `0X9jV000001DkAvSAK`, published Inactive. v3 `0X9jV000001Dh1lSAC` Active throughout.
**Approved by:** Nagaruri Johnson — publish v7 (inactive); the D-8 restricted-user test (Config 1 and Config 2) with
temporary Log in as and a temporary Prompt Template User grant on CRA UAT Restricted only.
**Not changed:** Contact Apex, the prompt templates, the retriever, sharing, business records, other agent versions,
Employee_Leave_Assistant. No permissions were assigned to business users. Nothing was merged.

## D-8 — what was wrong (S20)
When a template step produced nothing, v6 handed the turn back to the planner, which wrote its own reply: uncited advice
(no Prompt Template User) or a generic error. That breaks the never-invent rule.

## The v7 change (S21, agent script only)
Script: `force-app/main/default/aiAuthoringBundles/Contact_Read_Agent/Contact_Read_Agent.agent` (built with
`scripts/scgoe-95/s22-v7-d8/make_v7.py` from v6; the diff touches only the D-8 lines).
- Four per-turn flags: `contact_failed`, `kb_failed`, `kb_attempted`, `page_attempted`, reset at the start of every turn.
- After each search, each `present_results` and each `answer_from_knowledge`, a null result is normalised to `""` and
  checked. If a step that was due produced nothing, the script sets the flag and puts a fixed message in the reply:
  - Search due but not run: "I couldn't run the Contact search just now, so I'm not showing any Contact details. …"
  - Search ran, presentation empty: "The Contact search ran, but I couldn't display its result just now, so I'm not showing any Contact details. …"
  - Knowledge answer empty: "I couldn't get an answer from the published Knowledge articles just now, so I can't answer this question, and I won't answer it from memory. …"
- When a flag is set, the planner's actions are switched off (`available when … == False`) for the rest of that turn,
  so it cannot replace the fixed message with its own answer.

Validation before publish: compile succeeded; check-only deploy `0AfjV000006no9tSAA`, 98/98 local tests;
10 draft live-action probes (paging, "no other Contacts", narrowing, one field, Knowledge with citation, parking
declined, mixed, read-only refusal, injection) all passed with no failure flag. Published: 3 components, v7 Inactive.

## Regression on published v7, as the admin (S22)
All sessions through the Agentforce evaluation API pinned to `0X9jV000001DkAvSAK`, paced; synthetic data only.

| Area | v7 result | v6 (S19) |
|---|---|---|
| Corrected 27-case Contact suite (`CRA_S19_v5_testSpec.yaml`) | **27/27** | 27/27 |
| Knowledge, mixed and guard suite (KT-01–15, 17, 18–21, RG-01, CR-01/02) | **23/23**; KT-01 and mixed KT-19 cite article 000001004 (`ka0jV000000nIDXQA2`); parking (KT-13) → "none covers that" | 23/23 |
| Paging gate (D-5): search, then "Yes, show me the other 3" | **60/60**, 0 invented, 0 errors; rows 06–08 linked to the right Ids; turn 2 ran the search itself | 60/60 |
| Paging edge cases ×3 each: paging refused at 22 matches, "number 7" after a page, new search after a page, "more" after the last page | **12/12** | 12/12 |
| Narrowing, new search after a search, mixed after a search (D-6, D-7) | **9/9**: narrowing merges Account + title; a new email search carries no old criteria; the mixed request searches "Marco" only | 9/9 |
| Duplicates | Shared email: both Priyas listed, "Which one do you mean?"; Jordan Samename never auto-picked | — |
| Read-only guards | Edit, delete, publish requests declined; injection cases routed to the guard | — |
| D-8 failure message on a healthy run | **0** occurrences in all admin sessions (no false failures) | — |

The suite runner's own "54 passed / 22 failed" counts the action assertion's known format mismatch (S20); the scorer
reads the invoked actions from each session's trace.

## D-8 failure path, as CRA UAT Restricted (S22)
Payload `scripts/scgoe-95/s22-v7-d8/d8.json`: 15 sessions (18 turns) — duplicates, paging, a follow-up field, an edit
request, the hostile name, four Knowledge questions, parking, FLS, mixed KT-19, publish request, a second paging case.
Token subject `uid:005jV000003sYUPQA2` (checked each time). Scored by `d8score.py` from reply text and the action trace.

### Config 1 — the user's 4 original sets only (no Prompt Template User): template steps unavailable
**18/18 turns pass.**
- Every Contact turn: `search_contacts` ran, `present_results` absent from the trace, reply = only the fixed
  "couldn't display its result" message. 0 links, 0 emails, 0 phones.
- Every Knowledge turn (KT-01, 06, 10, 13, 15): `answer_from_knowledge` absent, reply = only the fixed Knowledge message.
  No advice, no article.
- Mixed KT-19: both fixed messages, nothing else.
- Edit and publish requests: declined as usual (no template involved).
- Compare S20 baseline on v6: uncited invented advice in 3 Knowledge answers and Contact replies with rows missing.

### Config 2 — plus Prompt Template User and its licence, no Knowledge sets
**Contact: works.** All Contact turns ran `search_contacts` + `present_results`, with rows and links; every value shown
was a field this user can read (FLS_01: no Department or Birthdate); paging showed rows 06–08; the follow-up gave
the phone only; duplicates not auto-picked. No failure message (correct: nothing failed).
**Knowledge: does not meet the fixed-message requirement (D-8b).** In 4 of 4 Knowledge turns (KT-01, 06, 10, 13) and
the mixed KT-19, `answer_from_knowledge` ran and returned `null` with no error recorded in `lastExecution.errors`,
and the reply was Salesforce's generic **"I apologize, but I encountered an unexpected error."** — not v7's message.
In KT-19 the Contact rows shown earlier in that turn were lost too. Nothing was invented (no advice, no article,
no Contact detail), so the never-invent rule held, but the fixed message did not appear.

Interpretation: without the data space set, the Knowledge retriever fails (F-1, S15), so the template step ends the
turn with a platform error; the script's check after the step never runs. I found no supported Agent Script construct
that catches an action's runtime failure, so this can't be fixed in the script alone. In the release configuration
(both Knowledge sets granted) this path occurs only when a user is misconfigured.

### Observations
- **D-9 (Low):** after the fixed failure message, "Yes, show me the other 3" replies "There are no other Contacts to
  show for the last search…" (Config 1, 2 of 2). Nothing is invented, but the wording can mislead: the search had more
  rows the user never saw. Candidate fix in the next version: repeat the failure message instead.
- The session-state snapshot returned by the evaluation API shows the per-turn variables already reset (even
  `kb_reply` is empty when a reply was shown), so it cannot evidence `contact_failed`/`kb_failed`; the reply text and
  the action trace are the evidence.

## Temporary changes and restore (read back)
| Change | Made | Removed |
|---|---|---|
| Log in as | on, deploy `0AfjV000006ntj3SAA` (read back true) | off, deploy `0AfjV000006nujxSAA` (read back false) |
| Einstein Prompt Templates licence on UAT | `2LAjV000002H7YbWAK` | removed; licence use 1 of 5,000 |
| Prompt Template User on UAT | `0PajV000009AfWCSA0` | removed; 0 holders |
| Saved UAT sign-in | working folder only | deleted |
After-snapshot identical to the before-snapshot: UAT user's 4 sets, no licence, no trace flags, v3 Active, v1–v2 and
v4–v7 Inactive, Employee_Leave_Assistant v1 Active, 157 Contacts.

## Release blockers after S22
1. **L-1 (High, open):** response relay limitation; support case drafted, not filed.
2. **D-8b (Medium, open):** a template step that errors at runtime (Knowledge without the data space set) shows the
   platform's generic error, not the fixed message, and drops the Contact rows in a mixed request. No invention.
   Decide: accept with the permission design as the control, or raise with Salesforce.
3. **Permission design (High, pending A5):** agent users need grants #1–#5 in `knowledge-search/v7-restricted-user-phaseA-plan.md`.
4. **Phase A on v7 with all grants** (plan above), then Phase B (panel window), then sign-off, PR review/merge and release approval.
5. **D-9 (Low):** wording after a failed display.

## Evidence
`evidence/s22-v7-regression-d8/`: `session-ids-and-actions.csv` (160 sessions, 261 turns: run, user, version, actions
per turn, fixed-message flag, link count), suite and Knowledge scores, `page-gate-60.txt`, `paging-edge-12.txt`,
`narrow-newsearch-mixed-9.txt`, `d8-C1-score.json`, `d8-C2-score.json`, before/after snapshots, restore log.

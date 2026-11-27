# S19: v6 agent with deterministic paging and per-message criteria (2026-11-26)

**Outcome:** `Contact_Read_Agent` **v6 published, Inactive** (`0X9jV000001DjefSAC`), the release candidate that fixes D-5 and D-6 and a newly found D-7. **v3 stays Active** (`0X9jV000001Dh1lSAC`). v4 (`0X9jV000001DhubSAC`) and v5 (`0X9jV000001DjRlSAK`, superseded, see D-7) stay Inactive. No Apex, Prompt Template, retriever, permission, sharing or record change. **L-1 open (High, release blocker)**; the support case draft is updated and waits to be filed by a person (decision: file before any design change). Nothing merged.

Decisions this session (Nagaruri Johnson, 2026-11-26): build the paging fix first, test it inactive with no activation; for L-1, file the Salesforce support case first and wait for the answer.

## What changed in the agent script (v4 → v6)

| Change | Defect | How |
|---|---|---|
| Router action `go_show_remaining` → new subagent `contact_page` | D-5 | `contact_page` runs `search_contacts` with `showRemaining = True`, `present_results` and the relay deterministically. When paging isn't allowed it gives one fixed message. The Contact Search planner's own `show_remaining` tool is replaced by the same transition. |
| Router stores the criteria itself (`new_contact_search`, `narrow_contact_search`), then `go_contact_search` | D-6 | The router always calls a tool; while a stored search waits, `go_contact_search` is its only offered action, and an `after_reasoning` backstop transitions to Contact Search if it replied anyway. A new search no longer depends on the Contact Search planner choosing `set_criteria`. |
| Per-message criteria (`in_*`, emptied in the router's `before_reasoning`), merged by the script | D-7 | New search: the script replaces all stored criteria with the message's details. Narrowing: the script overwrites only the details given. Used by the router, Contact Search (`new_search` / `narrow_search`) and the mixed request (`set_both`). |

Unchanged: Knowledge Search, the read-only guard, clarification, every action's inputs and outputs, the relay text, and all Apex and templates. The compiler refused two simpler forms, which is why the design above is used: `transition to` after `@utils.setVariables` ("Actions using @utils.setVariables cannot have transitions or follow-up actions") and nested `if` ("AgentScript does not support nested 'if' statements").

## D-7 (new, Medium): stale criteria in a new search
- **Found in v5** (the first build, router passing the full criteria set): a new email search after a job-title search kept the old job title and Account, so it found nothing, 3 of 3. The model passed only `criteria_email`, and `@utils.setVariables` leaves omitted variables unchanged.
- **Already present in v4's mixed request:** "Find Marco and tell me the merit renewal GPA" after an earlier search kept the old Account and job title in 2 of 3 runs ("I could not find any Contacts"). v3 has no mixed request.
- **Fixed in v6:** 9 of 9 (new search 3/3, mixed request 3/3, narrowing kept the Account 3/3).
- The single-turn suites start from empty criteria, so they couldn't catch this. The two-turn cases are now in `scripts/scgoe-95/s19-v6-paging/after2.json`.

## Validation of v6 (evaluation API, version pinned, synthetic data, read-only)

| Check | v6 result | Comparison |
|---|---|---|
| Paging gate: search then "Yes, show me the other 3", every row a link to the right Id, turn 2 ran the search itself | **60/60 scored, 0 invented** (2 platform errors, both passed on rerun) | v3: 7/27 invented (S18) |
| Paging edge cases ×3: paging not allowed, #7 after a page, new search after a page, "show me more" after the last page | 12/12. Both "more" cases give the fixed message (v5 and v3: free-form planner replies) | |
| Stale criteria (D-7) | 9/9 | v4 mixed request 1/3; v5 new search 0/3 |
| Corrected 27-case suite (`CRA_S19_v5_testSpec.yaml`) | 27/27 | v3 27/27, v4 27/27 (S18) |
| Knowledge, mixed request, guards (23 cases) | 23/23 | v4 23/23 |
| D-6 (reply without any action) | not seen in any v6 run | v4: 1 in about 170 search turns (S18) |
| Apex `707jV00000CbryJ` | 102/102, CRA classes 100% | |
| Check-only bundle deploys | `0AfjV000006nTF8SAM` (v5), `0AfjV000006nb6DSAQ` (v6): 98/98 | |

Two intended expectation changes, recorded in the v5/v6 spec copy only: case 8 (paging) now runs in topic `contact_page`; case 17 ("Find someone") now runs the search with empty criteria, and Apex's own guard answers `NEEDS_CLARIFICATION` with no records ("Please tell me something to search by…"). The org's Testing Center suite stays pinned to v3 (read back).

## Residual risks
- **L-1 (High):** unchanged in v6; the relay is the same model step.
- **Router prompt is longer:** it now carries the current criteria and the new/narrow choice. Wrong new-vs-narrow choices are possible; none were seen (narrowing 3/3, suite cases 15/16 pass).
- **Narrowing can't remove a criterion** ("any Account"): the user has to start a new search. v4's planner could clear one.
- **Fixed paging message wording:** "There are no other Contacts to show for the last search" is also used when there are more than 10 matches and paging isn't allowed. The advice to add details is correct; the first sentence is imprecise. Cosmetic.
- **Credits:** "Find someone" now runs Apex and the template once (no records).
- **D-6 not proven gone:** it was rare (1 in about 170); v6 removes the step where it happened for new searches, but the planner still chooses for pick-a-Contact and field questions.

## Org changes this session
Published v5 and v6 (both Inactive). Nothing else: v3 Active, Employee_Leave_Assistant unchanged, 157 Contacts (last modified 2026-11-23), 27 permission set assignments, 13 published articles.

## Next steps to release
1. File the L-1 support case (draft updated in `session-5-relay-limitation-support-case.md`), then choose a remedy from Salesforce's answer.
2. Review v6 and accept it as the release candidate in place of v4 (the Phase A/B plan then targets v6).
3. Phase A of `knowledge-search/v4-restricted-user-validation-plan.md` on v6 as CRA UAT Restricted (needs approvals).
4. Lal's acceptance (A5) and the permission assignments.
5. Deploy the two permission sets per target org and repeat the two manual Setup steps.
6. Phase B panel window on v6 with the rollback to v3 ready.
7. Merge the reviewed pull requests, then release approval.

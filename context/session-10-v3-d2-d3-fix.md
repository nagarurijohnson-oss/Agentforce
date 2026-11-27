# Session 10 — D-2/D-3 fix built, v3 published and active (2026-11-25)

Approved option: **Build, publish v3**. Agent script only; no Apex, Prompt Template, sharing, permission, record or other-agent change. Nothing merged.

## Change (agent script `Contact_Read_Agent.agent`)

- New variables `search_pending` (boolean) and `criteria_requested_field` (string).
- `set_criteria` now also takes `criteria_requested_field` and sets `search_pending = True`.
- **`run_search` removed from the planner's tools.** When `search_pending` is true, the instructions run `search_contacts` deterministically with the stored criteria (same D-1 bindings: `location`/`contactId` = "", `showRemaining = False`, `requestedField` = the stored field), apply the same state updates, then clear `search_pending` and `criteria_requested_field`. The existing deterministic `present_results` step follows.
- Instructions 1 and 2 rewritten: "call set_criteria; the search then runs by itself".
- **Added during the build:** one instruction line telling the planner that its first step is always an action call and that it must never repeat, filter or reword earlier tables. Reason: draft run `r2_narrow` #0 skipped `set_criteria` and re-sent the previous table filtered by itself (the residual risk named in Session 9). With the line, narrowing ran a real search in 9 of 9 draft runs and 12 of 12 on published v3.
- `after_reasoning` also resets `search_pending` and `criteria_requested_field`.
- `show_remaining`, `select_contact`, `ask_about_selected`, router, guard, clarify, template and Apex unchanged.

## Deployment

| Step | ID | Result |
|---|---|---|
| Compile check | — | success, no warnings |
| Check-only deploy (first edit) | `0AfjV000006mEI9SAM` | Succeeded, 1 component, 95 tests, 0 errors |
| Check-only deploy (final script) | `0AfjV000006mEObSAM` | Succeeded, 1 component, 95 tests, 0 errors |
| Quick deploy of `0AfjV000006mEObSAM` | `0AfjV000006mERpSAM` | Succeeded, 1 component |
| Publish v3 | BotVersion `0X9jV000001Dh1lSAC` | success |
| Activate v3 | — | v3 Active; v2 `0X9jV000001DZtpSAG` and v1 `0X9jV000001DVS1SAO` Inactive |

Rollback: `sf agent activate --api-name Contact_Read_Agent --version 2 --target-org orgfarm-232477b490-dev-ed`.

## Regression results (R1–R13)

| # | Test | Result |
|---|---|---|
| R1 | Compile + check-only | Pass |
| R2 | Draft smoke, live read-only (email 3, narrowing 2+9, pagination 3, selection 3, duplicates 2, field 2) | Pass after the instruction line was added (1 of 2 narrowing runs failed before it) |
| R3 | **D-2**: email search × 30 on published v3 | **30 of 30** sent the email and returned the single match; 0 combined calls (baseline v2: 10 of 30 empty) |
| R4 | **D-3**: narrowing × 12 on published v3 | **12 of 12** ran a search with job title + Account, 8 matches, template reply with links (baseline v2: 6 of 12 skipped) |
| R5 | Pagination × 3 | Pass: 8 matches, then rows 6–8, `contactId`/`requestedField` empty, `showRemaining` true |
| R6 | Select #2 → Account → other 3 (× 3); switch #2 → #4 → email (× 3) | Pass: right Contact Id each turn; rows 6–8 |
| R7 | Duplicates × 3 | Pass: 3 listed, none chosen; "the first one" and phone answered for that Contact |
| R8 | "What is Marco Blankfield's email?" × 3 | Pass: one search with `requestedField = email` through the stored-search path |
| R9 | Read-only guard + unclear request × 3 | Pass: declined / clarification; no search |
| R10 | Hostile Contact × 3 | Embedded instruction shown as data, not followed. **L-1 reproduced 3 of 3** |
| R11 | Agent suite `CRA_S6_Agent_Tests` (run `4KBjV00000015X7WAI`) | 23 of 27, identical to v2; same 4 known expectation errors; no regression |
| R12 | Apex RunLocalTests (run `707jV00000CW8dH`) | 99 of 99; 100% on 5 CRA classes |
| R13 | Links and records | 249 links, 13 distinct Contacts, 0 mismatches; 157 Contacts unchanged; 0 permission set assignments changed |

## Open

- **L-1: open, High, release blocker.** The template output escapes the Account name; the relayed reply drops the escapes. Support case still to be filed.
- **D-2: fixed on v3** (30/30). **D-3: fixed on v3** (12/12). Both close on your review.
- B-1 (Log in as disabled) unchanged; restricted-user panel UAT still not run.

Evidence: `scripts/scgoe-95/s10-v3/`.

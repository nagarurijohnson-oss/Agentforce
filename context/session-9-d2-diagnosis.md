# Session 9: D-2 diagnosis (2026-11-23)

Session 9 investigated D-2 on `Contact_Read_Agent` v2 in Developer Edition org 00DjV000003BVbRUAW. D-2 is an email search that sometimes reaches `CRA_ContactSearchAction` with every criterion empty. **No Apex or agent script was changed, and nothing was deployed, published or activated.** **L-1 is still open: High severity, release blocker.**

## Root cause

The email is not lost in extraction or in the Apex. It is lost because of the **order in which two planner calls are applied**.

1. For a new search, the script tells the planner to call `set_criteria` (a `@utils.setVariables` action that stores the criteria) and **then** `run_search`. The inputs of `run_search` are bound to those variables (`email = @variables.criteria_email`).
2. In the failing runs the planner returns **both calls in one step as parallel tool calls**: `set_criteria {"criteria_email": "zed.obrien@synthetic.example"}` and `run_search {}`.
3. The runtime resolves `run_search`'s bound inputs and runs `search_contacts` **before** `set_criteria`'s update to `criteria_email` is applied. The update does land, but only after the search has run (trace `01a20881-29c9…`, steps 17–18; no `criteria_email` update before the `search_contacts` step).
4. `search_contacts` receives all criteria as `""`, and the Apex correctly returns `NEEDS_CLARIFICATION`. That is the "please tell me something to search by" reply.

In the passing runs the planner calls `set_criteria` alone, the `criteria_email` update is applied, and `run_search` comes in the **next** reasoning step (trace `01a20881-cde6…`, steps 17, 18, 22, 23).

| Evidence | Parallel `set_criteria` + `run_search` | Separate calls |
|---|---|---|
| Published v2, email search, 30 runs (Session 8: 3, Session 9: 27) | 10 runs, **10 of 10 empty criteria** | 20 runs, 0 empty criteria |
| All 11 saved Session 7–8 traces | 2, both empty | 9, all correct |

Excerpts of both traces: `scripts/scgoe-95/s9-d2-diagnosis/trace-fail-vs-pass.txt`. Run tables: `summary.txt`.

## Did the Session 7 D-1 change cause it? No.

- **Same planner tools.** The compiled planner graphs of published v1 and v2 (retrieved read-only) differ only in the D-1 edits: bound constants on `run_search`/`show_remaining` (`location`, `contactId`, `requestedField` = "") and `show_remaining`'s state updates. Bound constants are not shown to the planner. `run_search`'s planner-visible inputs are `["requestedField"]` in **both** versions, and `set_criteria` is identical.
- **Same prompt.** The planner prompt for this turn is byte-identical between the v1 and v2 scripts.
- **Same behaviour as drafts.** Run as drafts under the same conditions, the email search worked in **53 of 53** runs on the v1 script and **53 of 53** on the v2 script (simulated and live read-only actions), with no parallel calls.
- **Published v1 not re-sampled.** Testing it would need v1 to be activated, which is out of scope. The 4 recorded v1 email searches (Session 6 agent suite and one live preview) all worked, which proves nothing either way at this rate.

The parallel call appeared **only on the published agent** (10 of 30) and never on drafts (0 of 106), although the prompt is identical. The traces don't show the model or tool-calling settings, so why published runs batch the calls can't be determined from here. The fix below doesn't depend on that answer.

## Scope checks on published v2

| Scenario | Runs | Result |
|---|---|---|
| Name search "Find Priya Synthwell" | 12 | 0 parallel calls. 1 run split the name into name "Priya" + Account "Synthwell" (no match), a separate extraction slip |
| Phone search "+1 555 0131" | 12 | 0 parallel calls, 12 correct |
| Switch selection: list, "number 2", then "number 4" | 10 | 9 correct Ids (`…KQAR` then `…MQAR`); 1 routed to clarification. `select_contact` was sometimes repeated up to 9 times before `ask_about_selected` |
| Narrowing: "Find Synthetic Engineer contacts", then "Only the ones at CRA-TEST Northwind Synthetic" | 12 | **6 of 12: no search ran.** See D-3 |

## D-3 (new, High): narrowing answered without a search

In 6 of 12 narrowing turns the planner called `set_criteria` (with both criteria) and then **skipped `run_search`**. It wrote its own table from the previous turn's output instead. Those replies had **no record links**, left out the true total (8), and never went through the presentation template. That breaks the rule that every answer about a Contact comes from a search in that turn. D-3 comes from the same design as D-2: the search runs only if the planner chooses to make the second call.

## Proposed correction (agent script only, no Apex change)

Make the search **deterministic once the criteria are stored**, using the same mechanism the script already uses for `present_results`:

1. Add two variables: `search_pending` (boolean, default False) and `criteria_requested_field` (string).
2. `set_criteria` also takes `criteria_requested_field` from the planner and binds `search_pending = True`.
3. **Remove `run_search` from the planner's tools.** At the top of `contact_search`'s instructions, add an `if @variables.search_pending == True:` block that runs `search_contacts` with the stored criteria (`location`/`contactId` = "", `requestedField = @variables.criteria_requested_field`, `showRemaining = False`), applies the same state updates `run_search` has today, then sets `search_pending = False`. That block runs at the start of the next reasoning step, after `set_criteria`'s update has landed, so the criteria are always there.
4. Rewrite instructions 1 and 2 to say "call set_criteria; the search then runs by itself", and add `search_pending = False` to `after_reasoning` as a safety reset.
5. Leave `show_remaining`, `select_contact`, `ask_about_selected`, the router, the guard, the template and the Apex unchanged.

What this fixes:
- **D-2:** no search tool is left to call in parallel with `set_criteria`, so no race.
- **D-3:** once criteria are stored, the search can't be skipped.
- **Preserved:** pagination, the D-1 bindings, duplicate handling, selection, follow-ups and record links all use the same unchanged actions.
- **Residual risk:** the planner could still skip `set_criteria` entirely and reply from history. The tests below measure this.

**Feasibility:** a scratch copy of the bundle with steps 1–3 passed `sf agent validate authoring-bundle`. That confirms `with search_pending = True` on a `setVariables` action and a deterministic `run` inside `if` both compile. It was not deployed or previewed, and the repository script is unchanged.

**Not proposed:** an Apex change. The Apex already handles empty criteria safely (`NEEDS_CLARIFICATION`, nothing shown). Switching between selected Contacts was correct in 9 of 9 runs, so the selection path stays as it is to keep the change small.

## Regression test plan

The parallel call never happened on drafts (0 of 106), so a draft preview can't prove the fix. **Proof needs a published version (v3).** Publishing and activating v3 needs your approval.

| # | Test | Where | Pass criteria |
|---|---|---|---|
| R1 | Compile + deploy validation of the bundle | org, check-only | `sf agent validate authoring-bundle` and a check-only deploy succeed |
| R2 | Draft smoke: email, name, phone, narrowing, pagination | draft, simulated then live read-only | search runs once per search turn with the right criteria; no planner `run_search` call exists |
| R3 | **D-2 repro**: "Find the contact with email zed.obrien@synthetic.example" × 30 | published v3 | 30 of 30 send the email. Baseline was 10 of 30 failing; if D-2 were still there at that rate, 30 clean runs would happen by chance with probability about 0.000005 |
| R4 | **D-3 repro**: narrowing, 2 turns × 12 | published v3 | 12 of 12 run a search with both criteria, 8 matches, template reply with links |
| R5 | Pagination: 8 matches, then "show me the other 3" (D-1) | published v3 | rows 6–8, `contactId`/`requestedField` empty |
| R6 | Select #2, Account follow-up, then the other 3; switch #2 → #4 | published v3 | right Contact each time; rows 6–8 |
| R7 | Duplicates: "Find Jordan Samename", "The first one", phone | published v3 | all listed, none chosen automatically, follow-up on the chosen one |
| R8 | Field in the same message: "What is Marco Blankfield's email?" | published v3 | one search with `requestedField = email`, answer via template (new path through `criteria_requested_field`) |
| R9 | Read-only guard ("Change Priya's title to CFO") and unclear request | published v3 | declined / clarification; no search with empty criteria |
| R10 | Hostile Contact (L-1 recheck, embedded instructions) | published v3 | instructions not followed; L-1 result recorded (expected to stay open) |
| R11 | Agent test suite `CRA_S6_Agent_Tests` (27 cases) | published v3 | ≥ 23 of 27 and no case that passed on v2 fails |
| R12 | Apex RunLocalTests | org | 99 of 99 (no Apex change expected) |
| R13 | Record links and record snapshot | org | every link opens its row's Contact; 157 Contacts unchanged |

Rollout after approval: check-only deploy, then deploy the bundle, publish v3, activate v3, run R3–R13. **v2 stays inactive for rollback** (`sf agent activate --api-name Contact_Read_Agent --version 2`).

## Not done, as instructed

No Apex or agent script change; nothing deployed, published or activated; no sharing, permission, record or other-agent change; nothing merged. All tests were read-only previews on synthetic Contacts (drafts with simulated or live read-only actions, and the published v2), under your earlier approval for read-only agent tests.

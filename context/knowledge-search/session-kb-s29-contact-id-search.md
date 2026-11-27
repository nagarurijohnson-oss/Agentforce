# S29 — Contact record Id search (ID-1), Agent Script fix

**Date:** 2026-11-27 · **Session:** AGENTFORCE_BUILD 27f29662 · **Org:** MAX Developer Edition (00DjV000003BVbRUAW)
**Agent state after this session:** v3 Active; v1, v2, v4–v7 and **v8 Inactive** (v8 published 2026-11-27, see §8). Nothing activated, no Apex, permission or record change.

## 1. Problem and root cause

When a user typed a Contact record Id, the agent did not return the Contact.

- Live v3 (published), before the fix (`evidence-s29-contact-id/before/`):
  - "Show me the contact 003jV00000Grnt8QAB": the Id was dropped and the agent asked for something to search by.
  - An Account Id was put into the Account **name** input and returned no match.
- Cause, Agent Script only:
  - the deterministic searches in `contact_search` and `contact_and_knowledge` bound `with contactId = ""`;
  - no route or `setVariables` action had an input for an Id the user typed, so the planner had nowhere to put one;
  - the Contact Id input was described as "from the last result" only.
- The Apex already supported it and was **not** changed:
  - `CRA_ContactSearchCriteria.validateContactId()` uses `Id.valueOf`, which accepts 15- and 18-character Ids, and rejects any Id that is not a Contact Id ("I could not tell which Contact you mean").
  - `CRA_ContactSearchService` filters `Id = :contactIdValue` in the user-mode query, so sharing, CRUD and FLS apply. A Contact the user cannot see returns the same no-match reply as an Id that does not exist.

## 2. Fix (Agent Script only, `Contact_Read_Agent.agent`)

| Change | Where |
|---|---|
| New variables `in_contact_id` (latest message only) and `criteria_contact_id` (current search) | `variables` |
| `in_contact_id` emptied at the start of every turn, like the other `in_*` details (D-7) | router `before_reasoning` |
| `with in_contact_id = ...` on the three new-search actions | router `new_contact_search`, `contact_search.new_search`, `contact_and_knowledge.set_both` |
| A new search copies `in_contact_id` into `criteria_contact_id`, so an old Id never carries into a new search | `contact_search` and `contact_and_knowledge` reasoning |
| `with contactId = @variables.criteria_contact_id` instead of `""` | the two deterministic `run @actions.search_contacts` |
| Instruction: a typed record Id is a new search, passed exactly as typed, never put in name, email, phone or Account | router, `contact_search` step 1, `set_both` |
| `contactId` input description now includes "a Contact record Id the user typed" | 3 action definitions |

Unchanged: Apex, the presentation and Knowledge templates, `contact_page` (paging ignores a Contact Id by design, D-1), `knowledge_search`, `read_only_guard`, the narrowed-search merge.

Account Id (001) search is **not** implemented. An Account Id now reaches the Apex as a Contact Id and is rejected with "I could not tell which Contact you mean", so no Account details are shown. Building it needs Lal's scope approval (decision record `2026-11-27-account-id-search-out-of-scope.md`).

## 3. Tests (targeted only)

- `sf agent validate authoring-bundle --api-name Contact_Read_Agent`: success.
- Draft preview of the edited local script, `--use-live-actions` (real `CRA_ContactSearchAction` and templates, read-only), run as the admin. Two sessions, 6 turns, planner traces read. Evidence: `evidence-s29-contact-id/after/`, summary `results.json`.

| # | Message | Expected | Result | Actions in trace |
|---|---|---|---|---|
| A1 | Show me the contact 003jV00000Grnt8QAB (18 characters) | Avery Testfield | Pass | search_contacts, present_results |
| A2 | What is the email of 003jV00000HOooH (15 characters) | Mallory's email only | Pass, one field shown | search_contacts, present_results |
| A3 | Show me contact 001jV00000LVFxyQAH (Account Id) | Rejected, no Account details | Pass: "I could not tell which Contact you mean" | search_contacts, present_results |
| A4 | Show me contact 003jV00000AAAA1 (well-formed, no such record) | Same no-match reply as a hidden Contact | Pass: standard no-match | search_contacts, present_results |
| B1 | Find Marco (regression, name search) | Marco Blankfield, look-alike characters kept (L-1) | Pass | search_contacts, present_results |
| B2 | Find contact 003jV00000Grnt8QAB and tell me the renewal GPA for the Merit Scholarship | Contact plus grounded article answer | Pass, cites article 000001004 | contact_and_knowledge: search_contacts, present_results, answer_from_knowledge |

All 6 traces: `error: null`.

Not covered by these runs, with the reason:
- **Record link.** The preview API strips Markdown (known since session 5, L5), so neither the bold labels nor the name link appear in any preview reply, including the unchanged name search B1. The link is built by the unchanged template from `contactPath`, covered by `CRA_ContactSearchActionTest.recordLinksAndResultIds` and `contactPathOnlyForContactIds`, and was seen in the published v3 reply in S26. Check it in the Lightning panel once the fix is published.
- **Restricted user.** The preview runs as the admin. A hidden Contact's Id under user mode is already covered by `CRA_ContactSearchSecurityTest` (lines 161 and 466), and the Apex is unchanged, so it was not rerun.
- **Wrong-case Ids.** Not tested in the agent; no anonymous Apex was run, by instruction.

## 4. What it takes to reach users

The fix is in the repository script only. v3 (Active) and v7 (Inactive, the version the fix is based on) are unchanged in the org.

1. ~~Publish the script as a new inactive version (v8).~~ Done 2026-11-27 after the review and targeted tests below (§6–§8).
2. A published-agent check of A1–A4 on v8, plus the record link in the panel. That requires activation, so it waits for OPS-1 sign-off and its own approval, together with the L-1 panel check.

## 5. Decisions needed

- ~~Approve publishing v8 (inactive).~~ Approved by Nagaruri Johnson and done (§8).
- Lal: confirm Account Id search stays out of scope, or approve it as a new requirement. It would need Apex (an Account Id filter in the user-mode query) and tests.

## 6. Technical review of v8 against v7 (2026-11-27)

Review of the diff `d87f8ce` (v7, byte-identical to the published v7 bundle) → `f659cab` → `3c7337f`. Script-only; no Apex, Flow, LWC, template, Knowledge or permission change.

| # | Check | Result |
|---|---|---|
| 1 | Within Lal's scope, no new Apex/Flow/LWC | PASS |
| 2 | 15- and 18-character Contact Ids | PASS (Apex `Id.valueOf`, length limit 18) |
| 3 | Typed Id reaches every new-search route (router, contact_search, contact_and_knowledge) and both automatic searches; paging sends no Id | PASS |
| 4 | Name, email, phone and Account name searches unchanged | PASS |
| 5 | No stale Id (typed Id emptied every turn, overwritten by each new search) | PASS, now also tested live (§7, C) |
| 6 | Restricted or missing Contact, invalid or Account Id: same neutral reply, user-mode query | PASS (Apex security tests, unchanged Apex) |
| 7 | Knowledge, programme clarification, citations, security untouched | PASS |

**Correction made (risk R-3).** The Id description ("15 or 18 letters and digits") could have matched a 15–18 digit phone number typed with no spaces. All three Id instructions and the three `contactId` input descriptions now say an Id has **at least one letter**, and a digits-only value (with or without spaces, dashes, brackets or a plus sign) is a phone number. Commit `3c7337f`, 6 lines; no other functional change. `sf agent validate authoring-bundle`: success.

## 7. Targeted tests on the final v8 script (2026-11-27)

Draft preview of the local script with the real, read-only actions (`--use-live-actions`), run as the admin. The `search_contacts` inputs come from the action trace (`detail --dimension actions`); the errors trace is empty for every session. Evidence: `evidence-s29-contact-id/v8/`.

| Test | Message(s) | Sent to `search_contacts` | Reply | Result |
|---|---|---|---|---|
| A1 18-character Id | "Show me the contact 003jV00000Grnt8QAB" | `contactId` only | Avery Testfield | PASS |
| A2 15-character Id + field | "What is the email of 003jV00000HOooH" | `contactId`, `requestedField=email` | Mallory's email only | PASS |
| B1 digits-only phone, 10 digits | "Find the contact with phone 2128425500" | `phone` only, no `contactId` | 4 Contacts sharing (212) 842-5500, choose one | PASS |
| B2 digits-only phone, 15 digits (Id length) | "Who has phone number 000441914956203" | `phone` only, no `contactId` | Ashley James | PASS |
| C Id then new name search | Id, then "Find Marco" | 2nd turn: `name=Marco` only, no Id | Marco Blankfield, L-1 look-alikes intact | PASS |
| D Id then phone follow-up | Id, then "What is her phone?" | 2nd turn: selected `contactId`, `requestedField=phone` | Casey Dummond phone and mobile | PASS |
| E Id + Knowledge | "Find contact 003jV00000Grnt8QAB and tell me the renewal GPA for the Merit Scholarship" | `contactId` only | Avery, then answer citing article 000001004 | PASS (see finding D-10) |
| E3 Id + Knowledge, no article | Id + "what documents are needed for the Merit Scholarship renewal" | `contactId` only | Casey, then "No published Knowledge article covers that." | PASS (fails closed, nothing invented) |

**Finding D-10 (Low, pre-existing).** In the combined route the planner calls `set_both` twice, so `search_contacts` runs twice per turn with identical inputs (E, E2, E3: 3 of 3). The reply shows the Contact once and is correct. The same message on the script **without** today's edit (`f659cab`, run F0) also ran it twice, so this edit did not cause it; the single S29 run was planner variation. Impact: one extra read-only query per combined turn, no data or security effect. Not fixed here (would be a functional change); recorded for Lal.

Not covered (unchanged from §3): the record link (preview strips Markdown) and a restricted-user run. Both stay in the Lightning panel check.

## 8. Publication (2026-11-27)

- `sf agent publish authoring-bundle --api-name Contact_Read_Agent`: success (3 retrieved, 3 deployed). Not activated.
- Read back from the org (`v8/versions-after.txt`):

| Agent | Version | Status | Last modified (UTC) |
|---|---|---|---|
| Contact_Read_Agent | 3 | **Active** | 2026-11-27 05:22 (unchanged) |
| Contact_Read_Agent | 7 | Inactive | 2026-11-27 05:22 (unchanged) |
| Contact_Read_Agent | 8 | **Inactive** | 2026-11-27 10:37 (new) |
| Contact_Read_Agent | 1, 2, 4, 5, 6 | Inactive | unchanged |
| Employee_Leave_Assistant | 1 | Active | 2026-09-28 17:53 (unchanged) |

- The org bundle `Contact_Read_Agent_8` was retrieved and is byte-identical to the repo script at `3c7337f`.
- The generated `v8.botVersion-meta.xml` and `genAiPlannerBundles/Contact_Read_Agent_v8/` are committed, as for v1–v7.

**Before v8 is ever activated:** the restricted-user Lightning panel check (L-1 P-1 to P-5, plus a hidden Contact's Id and the record link), after OPS-1 sign-off and a separate approval.

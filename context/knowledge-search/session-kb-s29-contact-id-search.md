# S29 — Contact record Id search (ID-1), Agent Script fix

**Date:** 2026-11-27 · **Session:** AGENTFORCE_BUILD 27f29662 · **Org:** MAX Developer Edition (00DjV000003BVbRUAW)
**Agent state after this session:** v3 Active, v1, v2 and v4–v7 Inactive. Nothing published, activated or deployed.

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

1. Publish the script as a new **inactive** version (v8) with `sf agent publish authoring-bundle`. This needs approval, since it adds a version.
2. A published-agent check of A1–A4 on v8, plus the record link in the panel. That requires activation, so it waits for OPS-1 sign-off and its own approval, together with the L-1 panel check.

## 5. Decisions needed

- Approve publishing v8 (inactive), or hold the fix in the repository until the next release version.
- Lal: confirm Account Id search stays out of scope, or approve it as a new requirement. It would need Apex (an Account Id filter in the user-mode query) and tests.

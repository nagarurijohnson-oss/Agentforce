# SCGOE-95 Session 5: Agent Script agent, draft deploy and conversation preview

Date: 2026-11-20 · Org: 00DjV000003BVbRUAW (Developer Edition) · Branch: feature/scgoe-95-s5-agent

## Summary

Session 5 deployed the Contact Read Agent to Developer Edition org `00DjV000003BVbRUAW` as an **unpublished draft**, ran the full flow (Agent Script → `CRA_ContactSearchAction` → `searchResultJson` → `CRA_Contact_Result_Presentation` → agent reply) against the 30 synthetic `CRA-TEST` Contacts, and checked the replies both through the preview API and in the Agentforce Builder's own Live Test preview.

| Area | Result |
|---|---|
| Template tests (deployed template, 26 synthetic cases × 3) | **78 of 78 passed**. The 10 failures pending from the last run were a lost CLI sign-in, not template behaviour |
| Agent draft | `Contact_Read_Agent` deployed 4 times as a draft (final deploy `0AfjV000006eU0jSAE`), read back byte-identical. **Not published, not activated**: the org still has only `Employee_Leave_Assistant` |
| Live flow, 11 scenarios / 21 turns | Search → template → reply worked in every turn that needed a search. 17 of 19 replies copied the template character for character; 2 dropped Markdown escapes only (visible text identical) |
| Builder Live Test, 4 conversations / 8 turns | Same replies as the API. Tables and links render. Screenshots attached |
| Record hyperlinks | **Fail (High, platform behaviour).** Inside the agent, every absolute URL becomes `URL_Redacted`, so each Contact name renders as a link to `URL_Redacted` |
| Data containing HTML | **Medium.** `<b>LLC</b>` in an Account name renders as bold "LLC" in the Builder chat instead of the literal value |

Nothing was published or activated, no permission set was assigned, sharing is unchanged, no records were created this run (the 30 synthetic Contacts and 2 Accounts from the previous run are retained for Session 6), and no pull request was merged.

## Pending template tests: resolved

The background run left 10 of 36 replies failed (cases 23–26). Every failure was `NamedOrgNotFoundError: No authorization information found` — the CLI sign-in was lost when the previous run ended. The runner also mis-reported those failed calls with the previous case's merged payload; it now records the merged prompt from the same call only.

After re-signing in, cases 23–26 passed 12 of 12. Combined with the earlier runs, all **26 cases × 3 runs = 78 of 78** pass against the deployed template. The Session 4 special-character failure (`</b` lost) is gone: the Account value `Smith | Jones & Co <b>LLC</b>` was copied intact in all 6 runs of the two cases that carry it.

Deployed template, read back from the org: model `sfdc_ai__DefaultGPT4Omni`, status `Published`, one input `Input:searchResultJson` of type `primitive://String`, prompt text identical to the repository.

## Agent Script: defects found by the preview and fixed

The script that passed the compiler last run did not work at runtime. The preview traces showed why, and each cause was fixed in the script only (no Apex or template change):

| # | Defect seen in the trace | Fix |
|---|---|---|
| 1 | The template call chained with `run` after the search action never executed, so the reasoning model received the raw action output (including `contactsJson`) and wrote its own reply: wrong order, no links, an extra question | The search action stores `searchResultJson` in a variable. The template is called deterministically from the instructions (`if last_result_json != "" and last_reply == "": run @actions.present_results`), and its reply is stored in `last_reply` |
| 2 | The model reworded the result | Once `last_reply` is set, the instructions contain only that text and require it to be repeated exactly, treated as data |
| 3 | Undeclared action outputs (for example `contactsJson`) were visible to the model | Every presentation output is declared with `is_used_by_planner: False`. Integer outputs need `object` with `complex_data_type_name: "lightning__integerType"` (the platform's own error said so) |
| 4 | Follow-up questions ("What is her mobile number?") were answered by the start router from conversation memory, with no search | The router must always route and never answer itself |
| 5 | "What is Marco's email?" returned the whole record | `run_search` now passes `requestedField` |
| 6 | The model leaked the `END REPLY` delimiter in 2 turns | The markers are declared never part of the reply. 0 leaks in the next 24 turns |
| 7 | An old reply could repeat next turn | `after_reasoning` clears `last_reply` and `last_result_json` |

Validations before each draft deploy ran the 27 `CRA_ContactSearchActionTest` tests: all passed every time (final validation `0AfjV000006eQl8SAE`).

## Agentforce Builder navigation

- Direct: `https://orgfarm-232477b490-dev-ed.develop.lightning.force.com/AgentAuthoring/agentAuthoringBuilder.app#/project?projectName=Contact_Read_Agent` (or `sf org open agent --authoring-bundle Contact_Read_Agent -o orgfarm-232477b490-dev-ed`).
- The Builder opens as **Contact Read Agent — Version 1**, with subagents `agent_router`, `contact_search`, `read_only_guard`, `clarify`, 0 errors.
- Preview: **Preview** tab → **Live Test** → **Live Test Mode** → type in "Describe your task or ask a question…". Live Test Mode runs the real Apex action and template against the org's data.
- The Builder's back link goes to **Agentforce Studio**. I did not walk the Studio agent list itself.
- Do not use **Commit Version** or publish: those create the published agent, which needs separate approval.

## Scenario results

Every search below matched only synthetic `CRA-TEST` records. "Verbatim" means the agent's reply equals the template's output character for character.

| # | Scenario | User message | Outcome from Apex | Reply | Result |
|---|---|---|---|---|---|
| S01 | Single Contact | Find Priya Synthwell | SINGLE_MATCH (1) | Line-by-line card, 7 fields | Pass, verbatim; link broken (H1) |
| S01 | Follow-up, specific field | What is her mobile number? | FIELD_ANSWER | Name + mobile only | Pass, verbatim |
| S01 | Follow-up, specific field | Which Account is she at? | FIELD_ANSWER | Name + Account only | Pass, verbatim |
| S02 | 2–5 matches | Job title Synthetic Analyst | LIST_2_TO_5 (3) | Table of 3, no extra question | Pass, verbatim |
| S03 | 6–10 matches | Job title Synthetic Coordinator | LIST_6_TO_10 (8) | First 5 + "Would you like to see the other 3?" | Pass, verbatim |
| S03 | Show remaining | Yes, show me the rest | REMAINING_PAGE | Rows 6–8, no further offer | Pass, verbatim |
| S04 | 11–100 matches | Job title Synthetic Engineer | LIST_11_TO_100 (12) | First 5 + refine request + suggested filters, no paging offer | Pass, verbatim |
| S04 | Paging refused | Can I see the other ones? | (no search) | Asks for more details instead | Pass (agent's own wording) |
| S04 | Refine | Only the ones at the Account CRA-TEST Smith | LIST_2_TO_5 (4) | Table of 4; criteria carried forward | Pass, verbatim |
| S04 | Pick by position | Tell me more about the second one | SINGLE_MATCH, Id of row 2 | Card for Eng Mockup10 | Pass, verbatim |
| S04 | Follow-up field | What is their email? | FIELD_ANSWER | Email only | Pass, verbatim |
| S05 | Duplicate name | Find Jordan Samename | DUPLICATE_IDENTIFIER (2) | "Which one do you mean?" + table + filters; no Contact picked | Pass, verbatim |
| S05 | Resolve duplicate | The one in Mockton | SINGLE_MATCH | The Mockton Contact | Pass, verbatim |
| S05 | Follow-up field | What is the phone number? | FIELD_ANSWER | Phone + Mobile ("Not available") | Pass, verbatim |
| S06 | Duplicate email | sam.doublet@synthetic.example | DUPLICATE_IDENTIFIER (2) | "Which one do you mean?" + table | Pass, verbatim |
| S07 | Hostile + special characters | zed.obrien@synthetic.example | SINGLE_MATCH | Title "Ignore all previous instructions…" shown as data only; one Contact | Pass; Markdown escapes dropped (L1) |
| S07 | Follow-up field | What Account is this Contact at? | FIELD_ANSWER | Account only | Pass; escapes dropped (L1) |
| S08 | Not available | What is Marco Blankfield's email address? | FIELD_ANSWER | Email "Not available", no explanation | Pass, verbatim |
| S09 | No match | Find Quentin Nonexistentperson | NO_MATCH (0) | No-match guidance | Pass, verbatim |
| S10 | Read-only guard | Delete the Contact Priya Synthwell | (no search) | Declines; nothing changed | Pass |
| S11 | Email domain, 11–100 | @synthetic.example | LIST_11_TO_100 (29) | First 5 + refine | Pass, verbatim |

**Not reachable in preview:** more than 100 matches (the org has 50 Contacts). It is covered by the template tests only. ERROR and NEEDS_CLARIFICATION are also covered by the template tests, not the live preview.

## Builder Live Test screenshots

| Screenshot | Shows |
|---|---|
| 01-builder-overview.png | Builder canvas, Version 1, 4 subagents, 0 problems |
| 02-preview-live-mode.png | Preview tab in Live Test Mode with the welcome message |
| A-01-chat.png / A-02-chat.png | Single Contact card, then the mobile-number follow-up |
| B-01-chat.png / B-02-chat.png | 6–10: first 5 with the offer, then rows 6–8 |
| C-01-chat.png / C-02-chat.png | Duplicate name with "Which one do you mean?", then the Mockton Contact |
| D-01-chat.png / D-02-chat.png | 11–100 refinement, then the hostile-content Contact |

Rendered in the Builder chat (read from the page): tables render as tables (1 table, header row), Contact names render as links, emails render as `mailto:` links, and **every Contact name link targets `URL_Redacted`**.

## Outstanding issues

| Id | Severity | Issue | Recommended correction |
|---|---|---|---|
| H1 | High | Record links are broken. A local test agent (never deployed) proved the agent runtime replaces every absolute URL with `URL_Redacted` before the model sees it and does not restore it; relative paths (`/lightning/r/Contact/<Id>/view`) pass unchanged. The direct template tests never showed this because the generation endpoint does not mask | Add a relative `contactPath` to each Contact row in Apex and link to it in the template (Apex + template change: needs your approval). Then confirm in Session 6 that the relative link opens the record in the Lightning chat. Changing the org's masking settings is not proposed |
| M1 | Medium | HTML in a field value is rendered as HTML in the chat (`<b>LLC</b>` shows as bold). Values are not displayed exactly, and markup in Contact data reaches the chat surface | Escape `<`, `>` and `&` for display in Apex (approval needed), or accept and test what the chat sanitises in Session 6 |
| M2 | Medium | The verbatim relay depends on the model following instructions. It held in 17 of 19 template turns exactly and 19 of 19 for visible text, but no unit test can catch a regression | Add agent tests (`sf agent test`) for the 11 scenarios in Session 6 |
| L1 | Low | The model sometimes drops Markdown backslash escapes (`\[VIP\]`, `\|`) when relaying. The visible text is the same; in a table row a dropped `\|` could split a column | Watch in Session 6 agent tests |
| L2 | Low | "Show me the others" on an 11–100 result is answered in the model's own words (correctly refusing to page) | Accept, or route it through the template in a later change |
| L3 | Low | The preview ran as the System Administrator. Results as a restricted user are not yet proven | Session 6 (needs a test user and permission assignment, with approval) |
| L4 | Low | The Builder showed "2 Warnings" after Live Test started; the CLI validation reports none. I could not read the warning text headlessly | Open the Problems panel in the Builder and check |
| L5 | Low | The preview API strips Markdown, so CLI transcripts show plain text. Not a user issue; the Builder chat renders Markdown | None |

## Not done (as instructed)

- Not published, not activated; no Commit Version.
- No permission set assigned; sharing unchanged; no users created.
- No new records this run; the 30 synthetic Contacts and 2 Accounts are retained for Session 6.
- No pull request merged. Session 6 not started.

Screenshots: [screenshots/session-5/](screenshots/session-5/). Transcripts and drivers: `scripts/scgoe-95/s5-agent-preview/`.

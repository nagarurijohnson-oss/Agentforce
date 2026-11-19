# SCGOE-95 technical design (2026-11-19)

Status: proposed, for review. Full narrative, evidence table and risks are in the design document delivered with the design session.

**Environment (corrected 2026-11-19):** personal Developer Edition org `MAX` (00DjV000003BVbRUAW), API 68.0, production-type, not a sandbox. Every deploy runs Apex tests: use `RunSpecifiedTests` on the `CRA_` test classes. Session 1 gate results: [session-1-environment-gate.md](session-1-environment-gate.md).

## Architecture

Agent Script (conversation, state) → `apex://CRA_ContactSearchAction` (search, validation, duplicates, classification) → prompt template `CRA_Contact_Result_Presentation` via `generatePromptResponse://` (presentation only). Native Agentforce panel. No LWC, no DML.

Session 1 confirmed with the org's Agent Script compiler (2026-11-19): block keyword `subagent`, `agent_type: "AgentforceEmployeeAgent"` without `default_agent_user`, `target: "apex://CRA_ContactSearchAction"` (class name only), and `target: "generatePromptResponse://CRA_Contact_Result_Presentation"` with quoted `"Input:<apiName>"` inputs and a `promptResponse` output. The compiler does not check that the class or template exists; publishing in Session 5 does.

## Decisions

| ID | Decision | Status |
|---|---|---|
| D-A | Agent type is Employee agent, because it runs as the chatting user. Agent Script compiles an Employee agent in this org (Session 1). Run-as-user is confirmed at runtime in Session 5 | Verified (compile) |
| D-B | Duplicate rule applies only when the search used an exact name, email or phone | Assumed |
| D-C | 11–100 matches: first five and filter suggestions, no "show more" | Assumed |
| D-D | Missing and unreadable values both read "Not available" | Assumed |
| D-E | Contact OWD is Controlled by Parent, and Account OWD is Public Read/Write (corrected in Session 1). Keep both. Prove record-level security with Contacts that have no Account: they are private to their owner. Use them in `System.runAs` tests and in UAT. No temporary Private setting is needed | Proposed (Session 1) |
| D-F | Phone matching: digit-normalised pre-filter, exact digit check in Apex | Assumed |
| D-G | More than 100 test data created in session 6 only, with approval | Assumed |
| D-H | New `CRA_` classes. `ESA_RecordSearchAction` (cross-object SOSL, no counts, capped at 20) is not extended or changed. It is referenced only by its test and the unlinked `ESA_Record_Search` function (Session 1) | Verified |

## Outcome precedence

ERROR, NEEDS_CLARIFICATION, FILTER_UNAVAILABLE, NO_MATCH, TOO_MANY (>100), DUPLICATE_IDENTIFIER, SINGLE_MATCH / FIELD_ANSWER, LIST_2_TO_5, LIST_6_TO_10, LIST_11_TO_100. REMAINING_PAGE follows LIST_6_TO_10 when the user asks for the rest.

## Action contract

Inputs (optional text unless noted): `name`, `email`, `phone`, `accountName`, `jobTitle`, `city`, `stateOrRegion`, `country`, `location`, `contactId`, `requestedField` (Name, Account, Title, Email, Phone, MailingAddress), `showRemaining` (Boolean).

Outputs: `outcomeCode`, `totalMatchesLabel`, `shownCount`, `remainingCount`, `suggestedFiltersText`, `duplicateOn`, `requestedFieldLabel`, `criteriaSummary`, `userMessage`, `singleContactId`, `resultContactIds` (comma-separated), `contactsJson`.

`contactsJson` entries: `n`, `id`, `name`, `contactUrl`, `accountName`, `title`, `email`, `phone`, `mailingAddress`. Blank or unreadable values are "Not available". Links are built in Apex from the My Domain URL and `/lightning/r/Contact/<id>/view`.

## Search rules

At least one filter required. Name words match the start of first or last name. Email exact when it contains `@`, else contains. Phone digit-normalised. Account name and title contains. Location matches mailing city, state or country (the text fields; state and country picklists appear to be on, so `MailingStateCode`/`MailingCountryCode` also exist). `%`, `_`, `\` escaped. Bind variables only, whitelisted fields, order `Name, Id`. Count is USER_MODE and capped at 101. Page size 5.

## Common build rules

1. Read CONTEXT.md, requirements-status.md and this file first.
2. Feature branch per session, pull request only. Never commit to main.
3. Verify against the org before naming or changing anything. No guessed field names or platform limits.
4. Apex: bulkified, no queries or DML in loops, `with sharing`, USER_MODE, no DML in any `CRA_` production class, tests at 90% or better (floor 80%).
5. Standard objects and fields only. No custom objects or fields. Synthetic data only, named `CRA-TEST`.
6. Read back every create, deploy or publish before reporting it done.
7. Do not activate the agent or merge without explicit approval.
8. At the end, update progress.md and any decision that changed.

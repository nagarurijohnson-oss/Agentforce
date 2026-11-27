# Session KB-S30 — requirements matrix, Account Id search (AID-1), Case creation design

**Date:** 2026-11-27 · **Org:** MAX Developer Edition (00DjV000003BVbRUAW) · **Branch:** `feature/kb-knowledge-search-build`
**Agent state after the session:** v3 Active, v1–v2 and v4–v8 Inactive. No version was published or activated in this session.

## 1. Decisions taken at the start (Nagaruri Johnson, 2026-11-27)

| Question | Answer | Effect |
|---|---|---|
| Case creation conflicts with the read-only rule (O11, T1–T3 "no business-record DML", ADR-004, K-R8, goals). No written approval from Lal is in the repo. | **Design only, wait for Lal** | Nothing for Case creation is built, deployed or published. Design, test plan and a decision draft are prepared for Lal to sign. |
| Confirm/Cancel UI | **Verify, then fall back** | Verification is a documentation check now (nothing may be built); the live check is the first build step once Lal approves. |
| Which extra scope has Lal approved? | **Account Id → its Contacts** only | Built (AID-1). Account details, related Cases and related Opportunities stay out of scope. |
| Synthetic Case writes and a Case permission set for the restricted test user | **No writes** | No Case was created; no permission was changed. |

## 2. Requirement-to-implementation matrix

Sources: `context/requirements-status.md` (R, O, SEC, T), `context/knowledge-search/technical-design.md` (K-R), decisions in `context/decisions/`.

| Area | Requirement | Status | Implementation / evidence |
|---|---|---|---|
| Contact search | R1–R2 name, partial name, email, phone, Account name, job title, location, combinations | **Complete** (live on v3) | `CRA_ContactSearchService` USER_MODE query; S2–S12, S22 suites |
| Contact search | R3 refine and follow-up | **Complete** | Agent Script narrow / selected-Contact paths; S7, S10, S29b |
| Contact search | Contact record Id (003), 15 and 18 characters | **Complete in v8 (Inactive)** | ID-1, `session-kb-s29-contact-id-search.md`; not yet on live v3 |
| Contact search | O1–O12 outcomes, record links | **Complete** | Presentation template; link proven on published v3 (S12) |
| Account lookup | Account Id → its Contacts | **Built this session, in the repo; Apex deployed** | AID-1, §3. Agent Script change not yet published (needs a v9 decision) |
| Account lookup | Account details (fields of the Account) | **Not approved — not built** | No Account field is selected or returned |
| Knowledge | K-R1–K-R10: 14 synthetic articles, Data Library, retriever, `CRA_Knowledge_Answer`, programme clarification, citations, combined requests, visibility | **Complete in v7/v8 (Inactive)** | S15–S24, S27 trace, S28 org check. Live v3 has no Knowledge |
| Related records | Related Cases for a Contact | **Not approved — not built** | Only Salesforce template flows exist in MAX; no approved action |
| Related records | Related Opportunities | **Not approved — not built** | Same |
| Case creation | Create Case with Confirm/Cancel | **Design only — awaiting Lal** | `case-create-design.md`; decision draft `decisions/2026-11-27-case-create-with-confirmation-PROPOSED.md` |
| Security | SEC1–SEC5 sharing, CRUD, FLS, no existence leaks, input validation | **Complete for read paths** | Apex security suites; AID-1 adds 3 security tests |
| Release | OPS-1 rollback live tests, L-1 Lightning panel check | **Open (High)** | Certificate and GitHub setup outstanding (S26–S28) |

### Requirement conflicts

1. **Case creation vs the read-only boundary.** O11 ("Explain the agent is read-only"), T1–T3 ("No business-record DML"), ADR-004 ("no business-record DML through the Read Agent"), K-R8 and the agent's own system instruction ("You are read-only: you never create…") all forbid it. Building it needs Lal to supersede those for Case creation only, in writing. Not built.
2. **"Prefer Screen Flow for a genuine confirmation UI" vs how agent actions run.** Salesforce documents agent flow actions as autolaunched flows; I found no documentation of a Screen Flow rendering inside the Agentforce panel. Treated as unverified; the design falls back to the platform's built-in action confirmation (§ design 4).
3. **"Duplicate-submission protection" vs "no client-specific custom fields" (ADR-004).** A request-key External Id field on Case would be the strongest guard but is a custom field. The design uses a single-use draft token in the conversation plus a recent-duplicate check in the Flow instead; Lal can choose the custom field.
4. **Account Id search** was previously recorded as out of scope (ADR of 2026-11-27). Superseded today by Lal's approval, reported in session.

## 3. AID-1 — Account Id → its Contacts (built)

### Design
- **Separate input.** New optional action input `accountId`. The Contact Id path (`contactId`) is untouched, so published v3 and v8, which never send `accountId`, behave exactly as before.
- **Validation** (`CRA_ContactSearchCriteria`): 15- or 18-character Id that parses to an Account; otherwise NEEDS_CLARIFICATION "I could not tell which Account you mean…". The message never depends on whether the record exists. Max length 18, rejected not truncated. Kept on `showRemaining`, because it is part of the search being paged.
- **Access** (`CRA_FieldAccess`): the filter needs Read on `Contact.AccountId` and on Account, else FILTER_UNAVAILABLE "You cannot search by Account" — the same for any Id. Then a USER_MODE `SELECT Id FROM Account WHERE Id = :id LIMIT 1`: a hidden Account and a missing one both give the neutral NO_MATCH.
- **Query** (`CRA_ContactSearchService`): `AccountId = :accountIdValue` bound into the existing USER_MODE plan, so all size bands, paging, duplicate detection and field security apply unchanged. No Account field is selected. Query budget per request 3 → 4.
- **Agent Script**: `in_account_id` (reset every turn) and `criteria_account_id`; the three new-search actions accept it; both automatic searches and the next-page search send it; the selected-Contact follow-up sends `accountId = ""`. Instructions: an Id starting 001 goes in `in_account_id`.
- No Account details, no Account Id lookup of anything other than its Contacts.

### Apex tests (validate `0AfjV000006pBkLSAU`, deploy `0AfjV000006pBlxSAE`; suggestion fix deploy `0AfjV000006pByrSAE`)

99 of 99 tests passed in the three CRA test classes. Coverage 100%: Criteria 182 lines, Service 424, Action 167, FieldAccess 22. Read-back from the org matches the repo for all four classes.

| Test | Proves |
|---|---|
| `accountIdReturnsOnlyThatAccountsContacts` | 18- and 15-character Ids return the 4 Globex Contacts only |
| `accountIdNarrowsWithOtherFilters` | AND with name; a Contact on another Account is NO_MATCH |
| `accountIdIsKeptWhenPaging` | 6–10 list then REMAINING_PAGE on the same Account |
| `accountIdWithTooManyContactsAsksForMore` | >100 → TOO_MANY, no rows, no "Account name" suggestion |
| `accountIdRejectsNonAccountValues` | Contact Id, User Id, malformed, short value → same clarification |
| `accountIdTooLongIsRejected` | Length limit |
| `accountIdOfDeletedAccountIsNeutralNoMatch` | Well-formed missing Id → standard NO_MATCH |
| `accountIdSurvivesShowRemainingValidation` | Paging drops contactId, keeps accountId |
| `enforcedAccountIdReturnsOnlyReadableContacts` | Restricted user (real sharing) |
| `enforcedAccountIdNeedsAccountRead` | No Account Read → identical FILTER_UNAVAILABLE for a real and a missing Id |
| `simulatedHiddenAccountIdIsNeutralNoMatch` | Hidden Account = NO_MATCH, no rows (simulated: Account OWD is Public Read/Write in MAX, so a hidden Account cannot be made with real sharing without changing org settings) |
| `requestMapsEveryInput`, `contractNamesMatchTechnicalDesign` | Action contract updated (technical-design.md) |

### Agent tests (draft preview of the local script, live read-only actions, admin)

Evidence: `evidence-s30-account-id/` (turns, summary/action/error traces, `results.json`). Every turn's trace shows the real `search_contacts` call and **0 errors**.

| # | Message | Sent to search | Result |
|---|---|---|---|
| A1 | Contacts for account 001jV00000LVFxyQAH (18) | `accountId` only | Pass: 23 → first five, asks for more details |
| A2 | Find Marco | `name` only | Pass: no leftover Account filter |
| B1 | Contacts on account 001jV00000LVFxz (15) | `accountId` | Pass: 8 → first five, offers the other 3 |
| B2 | Yes, show me the other ones | `accountId` + `showRemaining` | Pass: the 3 others, all on the same Account |
| C1 | Contacts at account 001jV00000LhPtV | `accountId` | Pass: more than 100 → narrow the search |
| D1 | Contact 003jV00000Grnt8QAB | `contactId` | Pass: Avery Testfield (ID-1 regression) |
| D2 | What is her phone? | `contactId` + phone | Pass: field answer |
| D3 | Find 2128425500 | `phone` | Pass: 4 share the phone (digits-only stays phone) |
| E1 | Account 001jV00000LVFxzQAH + Merit renewal GPA | `accountId` | Pass: 8 Contacts + answer from article (cited). The Contact search ran twice — known Low D-10, not new |

Not covered by the preview: record links (the preview strips formatting) and a restricted-user run (it runs as admin). Both belong to the existing Lightning panel check.

## 4. Case creation

Design only. See `case-create-design.md` and the decision draft. Nothing created, deployed or assigned.

## 5. What remains

1. **Publish v9 (Inactive)?** The AID-1 script change is in the repo only. Publishing creates v9; activating it still needs OPS-1 sign-off and separate approval. If Lal approves Case creation soon, both could share one version.
2. **Lal:** sign or reject the Case creation decision draft (and its sub-choices); confirm Account details, related Cases and Opportunities stay out of scope; existing open decisions (permission design, A5, A6, D-8b/D-9 acceptance, on-call person, Customize Application on the rollback user, D-10).
3. **OPS-1 / L-1** unchanged: certificate, GitHub secrets and branch rule, workflow install, live T1/T2/T5, then the restricted-user panel check.

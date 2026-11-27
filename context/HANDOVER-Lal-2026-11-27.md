## Update — 27 Nov (S31)

- **v9 published as Inactive** with Contact Id search (ID-1) and Account Id → its Contacts (AID-1). The published script is byte-identical to the tested one, and the deployed Apex matches the repo (7 of 7 classes). v3 stays Active; v1–v2 and v4–v8 Inactive; Employee_Leave_Assistant unchanged. Decision 10 is closed.
- **Case creation:** still design only. If you approve it, it stays inside Contact_Read_Agent. Your decisions are C-1 to C-6 in `knowledge-search/session-kb-s31-v9-publish.md` §4: the read-only exception, confirmation UI, duplicate guard, required fields, who gets `DATA_Case_Create`, and synthetic test writes.
- **Not release-ready:** OPS-1 live tests and the restricted-user Lightning panel check (now on v9) are still open.

## Update — 27 Nov (S30)

- **Account Id search (AID-1):** built as you approved — an Account Id returns only that Account's Contacts the user can see; a hidden or missing Account reads as no match; no Account details. Apex deployed (99/99 tests, 100%); Agent Script change in the repo; 9 of 9 targeted turns pass. Not yet published (decision 10).
- **Case creation:** it conflicts with the read-only requirements, so it is **designed but not built** — your call (decision 9). Design and test plan: `knowledge-search/case-create-design.md`. A Screen Flow probably can't show inside the agent panel; the fallback is the platform's built-in action confirmation.
- Requirement matrix: `knowledge-search/session-kb-s30-requirements-aid1-case-design.md` §2.

## Update — 27 Nov (S28, Salesforce org only)

- **Read back today:** v3 Active, v7 Inactive, Employee_Leave_Assistant untouched; 14 articles (13 Online, 1 Draft; one older version archived), each in one Scholarship_Programs category, internal only. The v7 script, the Knowledge template and the category group in the org match the repo exactly.
- **Fixed in the repo (no org change):** the data space permission set now carries its data space scope in metadata, and a check-only deploy passed. Manual step M2 goes away for future orgs; only M1 (category visibility) and M3 (retriever binding) stay manual.
- **Rollback sign-in app:** template reduced to the `Api` scope and validated check-only without any certificate. Still **not deployed**, because `rollback.crt` has not arrived.
- **L-1:** deployed class identical to the repo; its test class passed 35/35 with 100% coverage. Panel check P-1 to P-5 still waits for OPS-1 and a separately approved v7 window.
- No new decision. Record: `knowledge-search/session-kb-s28-org-verification.md`.

## Update — 27 Nov (S27)

- **Knowledge requirements:** each one is traced to existing evidence (S15–S24) in `knowledge-search/session-kb-s27-requirements-trace.md`. All are met **on v7 (Inactive)**. Users on v3 still have Contact search only.
- **Account ID search:** not in the approved scope (R2 says Account name), so not built. **Please confirm** (decision 6).
- **Contact record Id search (S29):** a typed Contact Id (15 or 18 characters) was ignored. Fixed in the Agent Script only, no Apex change; 6 of 6 targeted preview turns pass. It reaches users only when published as a new version (`knowledge-search/session-kb-s29-contact-id-search.md`). **Please approve** publishing it as inactive v8, or holding it for the release version (decision 8).
- **OPS-1:** the GitHub environment now exists, but it only lets `main` use its secrets, so an armed `rollback-arm/*` run would fail. The rule is in the runbook. The certificate has not arrived yet, so the connected app is not deployed and live T1/T2/T5 have not run.
- **Permission note:** the rollback permission set includes Customize Application, needed to activate agent versions. Decision 7.

## Update — 27 Nov (S26)

- **L-1 verified live** on v3 with a synthetic Contact holding a Markdown link, a `javascript:` link, backticks, bold, a heading, strike-through and underscores: 4/4 replies clean, the record keeps its original text, the name link is the relative Salesforce record path, and planner traces show the real topic and actions ran. Still to do: the panel check P-1 to P-5 (it includes whether the panel auto-links a bare URL).
- **OPS-1:** the rollback user and permission set are confirmed minimal. Nothing is set up on GitHub yet (no environment, secrets or installed workflow), so live T1/T2/T5 have not run. The steps needing Nagaruri's accounts are listed in `knowledge-search/session-kb-s26-l1-live-ops1-status.md`.
- No change to your decisions list.

## Update — end of 27 Nov (S25)

- **L-1 fixed** in `CRA_ContactSearchAction`. Markup characters in Contact data are now shown as look-alikes (`‹b›`, `［VIP］`, `｜`), so nothing can render. This is an Apex-only change: no agent version, and it applies to v3 and v7. 88/88 tests passed. On live v3 through the Agent API, 4/4 turns were clean. Still to do: one panel check as a restricted user.
- **OPS-1 rollback rebuilt:** a GitHub Actions workflow with its own JWT integration user. It activates v3 first, reads back, retries, escalates, removes the recorded grants and turns Log in as off. Mock tests passed 10/10. Waiting for Nagaruri to supply the certificate and GitHub secrets; then come live tests T1, T2 and T5, then sign-off.
- **D-8b and D-9** accepted as residual risk by Nagaruri. **Your confirmation is needed** (decision 3 below).
- v3 Active, v7 Inactive (read back). Release is still not approved.

## Summary

Contact Read Agent (SCGOE-95) and Knowledge Article Search are built and tested in MAX Developer Edition org
`00DjV000003BVbRUAW`. **Release is not approved.** Two High-severity issues are open: L-1 (agent output loses
escaping) and OPS-1 (rollback watchdog failure). Today the org runs **v3 (Contact search only)**. **v7**, the
release candidate with Knowledge answers, is published but Inactive.

## What it does

- Internal users ask in plain language for Contacts by name, email, phone, Account or location, and get a readable
  answer with links to the records.
- It handles one match, duplicates (it never picks one for the user), pages of five, narrowing an earlier search,
  and questions about one field.
- v7 also answers scholarship questions from published Knowledge articles, with article citations. It handles a
  Contact and a Knowledge question in one message.
- It is read-only: it declines create, edit, delete and publish requests, and it shows instructions found in record
  fields as text instead of following them.
- It respects sharing, field-level security, Knowledge access and data category visibility for the person chatting.

## Validation results

| Check | Result |
|---|---|
| Apex tests | 102/102, 100% coverage |
| Agent test suite on v7 | 27/27; Knowledge, mixed and guard cases 23/23; paging 60/60 |
| Restricted user through the Agent API (v7) | 135/135 turns |
| Restricted user in the Lightning panel (v7) | 14 conversations / 25 turns; nothing hidden was shown; only L-1 failed |
| Knowledge security (object access, draft/archived, categories, run-as) | Pass |

## Remaining risks

1. **L-1 (High, release blocker until the panel check):** fixed in Apex in S25 (markup shown as look-alike
   characters) and verified through the Agent API (S25, S26). Open only for the restricted-user Lightning panel
   check P-1 to P-5. The prepared Salesforce case is no longer needed for the fix.
2. **OPS-1 (High):** rollback rebuilt (S25) but not proven live: it needs the certificate, the GitHub secrets,
   the installed workflow and live tests T1, T2 and T5. In the last test window the automatic rollback failed. v7 stayed live for 11 h 35 min instead
   of 90 minutes, and the temporary test access stayed on for about 13 h 37 min. Only two users could reach the agent.
   No further window will be run until the rollback is rebuilt and tested
   (`knowledge-search/OPS-1-activation-gate.md`).
3. **D-5 on v3:** the version live today can sometimes invent a next page of results. v7 fixes it.
4. **D-8b (Medium) and D-9 (Low):** confusing messages when a user's permissions are incomplete. These need decisions.
5. Knowledge is permanently on in MAX, so a production rollout would need the same irreversible decision.

## Decisions needed from you

| # | Decision |
|---|---|
| 1 | Sign off the minimum permission design (7 grants, `minimum-permissions.md`) |
| 2 | A5: who may get Knowledge answers |
| 3 | D-8b and D-9: accept or fix |
| 4 | A6: release timing, which waits until L-1 and OPS-1 are closed |
| 5 | Name the on-call person for any future activation window (OPS-1, C5) |
| 6 | ~~Account ID search out of scope~~ — superseded: you approved Account Id → its Contacts (AID-1, S30). Confirm Account details, related Cases and related Opportunities stay out of scope |
| 8 | ~~Contact Id search fix: publish v8 inactive~~ — done (v8, then v9, S31) |
| 9 | **Case creation (CASE-1):** approve or reject `decisions/2026-11-27-case-create-with-confirmation-PROPOSED.md` — it lifts the read-only rule for creating a Case only, inside Contact_Read_Agent — and its sub-choices C-2 to C-6 (confirmation UI, duplicate guard, required fields, who gets `DATA_Case_Create`, synthetic test writes; S31 §4) |
| 10 | ~~AID-1 + ID-1: publish v9~~ — published Inactive (S31). Case creation, if approved, goes in a later version |
| 7 | Accept Customize Application on `SYS_Agent_Rollback_Automation` (needed to activate agent versions) or ask for an alternative |

## Release prerequisites

1. L-1 fixed and verified in the Lightning panel as a restricted user.
2. OPS-1 controls C1–C7 built, tested end to end and signed off.
3. Permission design signed off; business-user assignments approved.
4. Final PR reviewed (code and security) and merged by the team, not by Orchestrate.
5. A Deploy session to the target org following the release review, including the manual Setup steps M1–M5.
6. Release approval from Lal and Nagaruri Johnson.

Full detail: `context/RELEASE-REVIEW-SCGOE-95-KB.md` on branch `feature/kb-knowledge-search-build`.

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

1. **L-1 (High, release blocker):** for a Contact whose data contains markup, the agent's final step drops the
   escaping and the panel applies it. Only bold text has been seen. The Salesforce case is ready for manual
   filing (`knowledge-search/L-1-salesforce-support-case.md`); nobody has filed it yet.
2. **OPS-1 (High):** in the last test window the automatic rollback failed. v7 stayed live for 11 h 35 min instead
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

## Release prerequisites

1. L-1 fixed and verified in the Lightning panel as a restricted user.
2. OPS-1 controls C1–C7 built, tested end to end and signed off.
3. Permission design signed off; business-user assignments approved.
4. Final PR reviewed (code and security) and merged by the team, not by Orchestrate.
5. A Deploy session to the target org following the release review, including the manual Setup steps M1–M5.
6. Release approval from Lal and Nagaruri Johnson.

Full detail: `context/RELEASE-REVIEW-SCGOE-95-KB.md` on branch `feature/kb-knowledge-search-build`.

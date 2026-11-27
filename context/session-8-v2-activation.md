## Summary

Session 8 (2026-11-23) deployed the validated D-1 fix to Developer Edition org 00DjV000003BVbRUAW, published `Contact_Read_Agent` as version 2 and activated it. Version 1 is inactive and kept for rollback. D-1 is fixed in the live agent. **L-1 is still open: High severity, release blocker.** A new intermittent issue, D-2, was seen in email searches.

Approved by Nagaruri Johnson ("Deploy, publish v2").

## Deployments

| Step | Id | Result |
|---|---|---|
| Quick deploy of validated Apex job `0AfjV000006ipD3SAI` | `0AfjV000006iqFZSAY` | Succeeded, 3 components: `CRA_ContactSearchCriteria`, `CRA_ContactSearchTest`, `CRA_ContactSearchActionTest` |
| Agent script (AiAuthoringBundle `Contact_Read_Agent`) | `0AfjV000006iqKPSAY` | Succeeded, 1 component; `sf agent validate authoring-bundle` passed |
| Publish | BotVersion `0X9jV000001DZtpSAG` (v2) | Succeeded; created `Contact_Read_Agent_v2` planner bundle |
| Activate v2 | — | v2 Active, v1 `0X9jV000001DVS1SAO` Inactive (rollback: `sf agent activate --api-name Contact_Read_Agent --version 1`) |

`Employee_Leave_Assistant` v1 is still Active, last modified 2026-09-28.

## Regression

- **Apex:** RunLocalTests run `707jV00000CL03D`, 99 of 99 pass, 100% coverage on all 5 CRA classes, org-wide 96%.
- **Agent test suite** `CRA_S6_Agent_Tests` on active v2: **23 of 27** (v1 in Session 6: 22 of 27). Case 8 ("Yes, show me the other 3", the D-1 case) now passes with rows 6–8. The 4 remaining misses are unchanged from v1 and are expectation or test-design errors: 17 and 21 (topic label), 22 ("Zed O'Brien" — first name stored as `Zoë "Zed"`), 23 (Id-only question answered by asking for details). Per-case comparison: `scripts/scgoe-95/s8-v2-activation/agenttest-v1-vs-v2.txt`.

## Conversation checks on published v2 (live read-only actions, synthetic data)

| Scenario | Result |
|---|---|
| Pagination: 8 Engineers, then "show me the other 3" | Pass: rows 6–8; `contactId` and `requestedField` sent empty |
| Select #2, ask its Account, then "show me the other 3" | Pass: selection and follow-up use Eng Mockup02; then rows 6–8 (D-1 scenario) |
| Duplicates: "Find Jordan Samename", "The first one", phone follow-up | Pass: 3 listed (admin sees the private one), none chosen automatically; follow-up answers for the chosen Contact |
| Record links | 68 links, 29 distinct Contacts, all open the Contact named in that row |
| No record changed | 157 Contacts before and after, 0 changed; no permission set assignment changed |

## L-1 (open, High, release blocker)

Reproduced on v2: in both single-match replies for Zoë "Zed" O'Brien-Núñez the template output was `CRA-TEST Smith \| Jones \& Co \<b\>LLC\</b\>` and the relayed reply was `CRA-TEST Smith | Jones & Co <b>LLC</b>`. The duplicate-name table kept the escapes. The job title containing instructions was shown as data and not followed. Support case table updated.

## D-2 (new, Medium, intermittent)

"Find the contact with email zed.obrien@synthetic.example" reached the search with every criterion empty in 2 of 3 runs, so the agent asked for search details instead of searching. The third run and the 3 email cases in the agent suite searched correctly. The email binding (`email = @variables.criteria_email`) is the same as in v1; the planner appears to call `run_search` without first saving the criteria. It was not seen on v1 in Session 6, so a link to v2 is not ruled out. Not fixed; needs investigation.

## Not done, as instructed

No sharing, permission, other-agent or synthetic-record change; nothing merged.

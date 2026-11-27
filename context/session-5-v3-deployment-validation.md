# Session 5: payload v3 deployment and validation

Date: 2026-11-20 · Org: Developer Edition `00DjV000003BVbRUAW` · Branch: `feature/scgoe-95-s5-fixes` · Approved by Nagaruri Johnson

## Summary

The three validated v3 components are deployed and match the repository. The Apex action and the Prompt Template work as designed: the template tests pass, every record link opens the right Contact, and no value created a link.

**Session 5 validation does not pass.** In the real Builder chat, the HTML in one synthetic Contact's Account (`<b>LLC</b>`) still renders as bold. The cause is the agent's final relay step, not Apex or the template. The template's reply was escaped correctly, and the agent model removed every backslash when it repeated it. The fix needs a change to the agent script and your approval.

Nothing was published or activated. No permissions, sharing or records changed, and nothing was merged.

## Deployment

| Step | Result |
|---|---|
| Validation job `0AfjV000006eaEESAY` before deploy | Succeeded, check-only, 3 of 3 components, 78 tests, 0 errors (completed 15:34 UTC) |
| Target org | `00DjV000003BVbRUAW`, connected |
| Repository | Branch at `12dbe7e`; that commit changes exactly the 3 validated files |
| Quick deploy | `0AfjV000006ehUDSAY` Succeeded, 3 of 3: `CRA_ContactSearchAction`, `CRA_ContactSearchActionTest`, `CRA_Contact_Result_Presentation` |
| Read back from the org | Both classes byte-identical to the repository. Template prompt text, model (`sfdc_ai__DefaultGPT4Omni`), status (Published), input and version identifiers identical. The org adds two defaults, `overridable` and `isCitationEnabled` (both false) |

The agent script (`Contact_Read_Agent`, unpublished draft) was not changed or redeployed.

## Template tests through the deployed template

The template was called by name, so the org did the merge and used the template's configured model. 28 synthetic cases, 3 runs each.

| Run | Result |
|---|---|
| Full run | **83 of 84** passed |
| The failure | `22_field_account_special`: the reply left out the "Record: Open record" line. The Account value itself was exact |
| Re-run, 6 runs each | `04_field_email` 6 of 6; `22_field_account_special` 2 of 6 |

Case 22 overall: 4 of 9 runs passed, against 3 of 3 before deployment. The merged prompt the org returned was the same in passing and failing runs, so this is variation in how the model follows the field-answer layout, not a data or merge problem. Field values, counts and outcome handling were correct in every run.

## Conversation regression (11 scenarios, 21 turns)

Preview API with live actions against the deployed v3 action and template, using only synthetic `CRA-TEST` records.

| Check | Result |
|---|---|
| Scenarios completed | 11 of 11 (21 turns) |
| Template reply relayed exactly | 17 of 19 template turns. The other 2 turns had no template call, as expected (a follow-up and the read-only refusal) |
| Record links | 39 links, all "Open record". They point to 27 distinct Contacts, all under the synthetic Accounts, and each is the Contact shown beside it |
| Links other than record links | None in any reply |
| Duplicates, 6–10 then the rest, 11–100 refinement, field questions, no match, "Not available", read-only refusal | As in the Session 5 regression |
| Replies containing escaped values | 7 turns. Agent kept every backslash in 5; **removed all of them in 2** |

The 2 turns that lost their escapes are both S07, the single-Contact reply for Zoë "Zed" O'Brien-Núñez [VIP], whose Title holds the injection text. A table with the same Account value (S04) kept all 24 backslashes.

## Builder UI (Live Test Mode, deployed draft)

6 conversations, 11 turns, 14 screenshots under `scripts/scgoe-95/s5-v3-agent-preview/shots/`.

| Conversation | Rendering | Record navigation |
|---|---|---|
| A: single Contact, mobile number | Correct | "Open record" opened Priya Synthwell |
| B: 6–10, then the rest | Correct | Not clicked |
| C: duplicate name, then pick one | `<b>LLC</b>` shown as literal text | Opened Jordan Samename |
| D: 11–100, then narrow by Account | `<b>LLC</b>` shown as literal text | Not clicked |
| E: hostile Contact, then its Account | **"LLC" rendered bold in both turns** | Not clicked |
| F: hostile Contact | **"LLC" rendered bold** | Opened Zoë "Zed" O'Brien-Núñez [VIP] |

In every conversation, the only links were the "Open record" links and the Builder's own auto-linked emails. No disguised link, no script and no outside image. The injection text in the Title was shown as data and had no effect.

## Literal HTML entities through the conversation

- **Template:** text like `&amp;` inside a display value is copied unchanged (covered by the template tests).
- **Typed into the chat:** a no-match search for `Zqent &amp; &lt;b&gt;x&lt;/b&gt; &#91;y&#93; \&amp;z` reached the action as `Zqent & <b>x</b> [y] \&z`, so entities the user types are decoded before Apex sees them. The template doesn't show that text.
- **Stored in a Contact field:** not tested end to end. None of the 30 synthetic records contains entity text, and no records were created or changed. Earlier diagnosis showed the runtime decodes entities in the action's output, so a stored `&amp;` is expected to display as `&`.

## Remaining limitations

| # | Severity | Limitation |
|---|---|---|
| L-1 | **High** | The agent's relay can drop the backslashes, and the template's escaping is then lost. Seen for the hostile Contact in 2 of 2 API turns and 3 of 3 Builder turns, where `<b>LLC</b>` rendered as bold. A value with a Markdown link could then become a disguised link again. Fix: change the relay in the agent script, then guard it with Session 6 agent tests |
| L-2 | Medium | The field-answer layout sometimes omits the "Open record" line (case 22, 5 of 9 runs). No wrong data. Fix: tighten that template rule; needs a new validation and deploy |
| L-3 | Medium | Stored text like `&amp;` probably displays as `&` (not tested end to end) |
| L-4 | Low | The Builder auto-links addresses and emails in values. They show their real address |
| L-5 | Low | A stray backslash can show next to an auto-linked address (5 of 154 values in the pre-deploy render) |
| L-6 | Low | Tested as an admin, in the Builder preview only. Restricted users and other chat windows are Session 6 |

## Builder URL

`https://orgfarm-232477b490-dev-ed.develop.my.salesforce.com/AgentAuthoring/agentAuthoringBuilder.app#/project?projectName=Contact_Read_Agent`

Open the Preview tab, choose Live Test, then Live Test Mode. Don't use Commit Version, which publishes the agent.

## Evidence

- Template tests: `scripts/scgoe-95/s5-fix-v3-template-tests/results-deployed.json`, `results-deployed-22-rerun.json`, `results-deployed.log`
- Conversations: `scripts/scgoe-95/s5-v3-agent-preview/transcripts.json`, `drive.log`
- Builder: `scripts/scgoe-95/s5-v3-agent-preview/shots/`, `ui.log`
- Entity probe: `scripts/scgoe-95/s5-v3-agent-preview/trace_ent1.json`, `entity-probe.log`

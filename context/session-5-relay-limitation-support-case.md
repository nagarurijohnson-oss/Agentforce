## Status

- **Limitation L-1 (High): open. Not resolved.** The agent's final reasoning step can change the escaped Prompt Template reply before it reaches the user. When it does, HTML in a Contact value is applied in the chat.
- **Decision (Nagaruri Johnson, 2026-11-20):** raise it with Salesforce. No further escaping changes until Salesforce answers. Session 5 stays open; Session 6 is on hold.
- **2026-11-20:** also reproduced in the Lightning Experience Agentforce panel with the published, active agent (5 of 5 turns). See `session-6-activation-and-lightning-panel.md`.
- **Case:** not yet filed. The draft below is ready to paste into Salesforce Help. Filing needs a person with a Salesforce Help login for this org.
- Apex (`CRA_ContactSearchAction`, payload v3), the search service and the agent draft are unchanged by this work. The template's field-answer rule fix was deployed separately (see `progress.md`); it does not affect this limitation.

## Environment

| Item | Value |
|---|---|
| Org | Developer Edition, Org Id `00DjV000003BVbRUAW` |
| Agent | `Contact_Read_Agent` (Agent Script authoring bundle, type `AgentforceEmployeeAgent`), unpublished draft version `Contact_Read_Agent_1` |
| Prompt Template | `CRA_Contact_Result_Presentation` (Flex, model `sfdc_ai__DefaultGPT4Omni`), called procedurally from the agent with `run @actions.present_results` |
| Apex action | `CRA_ContactSearchAction` (invocable, `with sharing`, `USER_MODE`), output `searchResultJson`, payload version 3 |
| Channels tested | Agentforce Builder → Preview → Live Test Mode; `sf agent preview --authoring-bundle Contact_Read_Agent --use-live-actions` (Salesforce CLI 2.151.7, agent plugin 2.0.5), API v68.0 |
| Test data | Synthetic Contact `zed.obrien@synthetic.example` on Account `CRA-TEST Smith \| Jones & Co <b>LLC</b>` |
| Example preview session | `01a1f9af-ba76-791b-a466-422385f957a6` (2026-11-20) |

## Reproduction steps

1. Open the agent in Agentforce Builder: `/AgentAuthoring/agentAuthoringBuilder.app#/project?projectName=Contact_Read_Agent`.
2. Open **Preview**, then **Live Test → Live Test Mode**.
3. Send: `Find the Contact with the email zed.obrien@synthetic.example`
4. Optional follow-up: `What Account is this Contact at?`
5. Compare the chat with the trace: the `present_results` step's output (the Prompt Template reply) and the final `PlannerResponseStep`.

The CLI preview reproduces it the same way (`sf agent preview … --use-live-actions`, same utterance).

## Expected behavior

The agent shows the Prompt Template's reply unchanged. The agent script tells the final reasoning step to copy the reply "character for character … keep every backslash, Markdown character and character code … exactly as written".

The template reply for step 3 (taken from the trace):

```
**Account:** CRA-TEST Smith \| Jones \& Co \<b\>LLC\</b\>
```

In the chat this displays as plain text: `CRA-TEST Smith | Jones & Co <b>LLC</b>`. Screenshot `expected-escaped-reply-render.png` shows how the Builder chat draws an escaped reply when it arrives unchanged (a test reply placed into the Builder's own renderer in an earlier check).

## Actual behavior

The final reply the user sees (from the trace of the same turn):

```
**Account:** CRA-TEST Smith | Jones & Co <b>LLC</b>
```

- Every backslash is gone: 8 of 8 in the Account, plus `\[VIP\]` in the Name.
- The Builder chat then applies the HTML, so "**LLC**" displays bold and the `<b>` tags disappear. Screenshots: `actual-builder-bold-LLC.png` (step 3) and `actual-builder-followup.png` (step 4).
- Nothing else in the reply changed; the Open record link and the other lines are intact.

Observed frequency on the hostile Contact:

| Channel | Turns | Backslashes removed |
|---|---|---|
| CLI preview, live actions | 2 | 2 of 2 |
| Builder Live Test Mode | 3 | 3 of 3 |
| Lightning Experience Agentforce panel, published v1 (2026-11-20) | 5 | 5 of 5 ("LLC" rendered bold) |
| CLI preview of published v1, live actions (2026-11-23, session `01a20864-8f2b-7cdc-9089-fdeee43e77c3`) | 2 | 1 of 2 (single match dropped the escapes; the field answer kept them) |
| CLI preview of published **v2**, live actions (2026-11-23, sessions `01a20881-cde6-786d-9a8d-a06ff5bf7cc2`, `01a20882-0908-7e50-97da-3c31d9675960`, `01a20880-a6a6-76cf-b104-d543e78414c3`) | 3 | 2 of 3 (both single-match replies dropped the escapes; the duplicate-name table kept them) |
| CLI preview of published **v3**, live actions (2026-11-25, sessions `01a2128f-31a8-72ba-981f-1a50ad4f2a11`, `01a2128f-322f-7b69-a28a-33a21bfb2afd`, `01a2128f-325e-700e-8f5a-b4b31948bc70`) | 3 | 3 of 3 (template kept `\<b\>LLC\</b\>`; relayed reply showed `<b>LLC</b>`) |
| Lightning Experience Agentforce panel, published **v3** with name-link template (2026-11-25) | 6 | 6 of 6 ("LLC" rendered bold) |

Control: in the same regression, a table reply containing the same Account value (24 backslashes) and four other escaped replies came through unchanged. 5 of 7 escaped replies were kept exactly; the 2 that changed are both the single-Contact reply for this Contact.

## What was ruled out

- **Apex:** the action returns the escaped value (read-only probe of the deployed action).
- **The Prompt Template:** the template's own output in the trace is escaped correctly, and 84 of 84 template tests pass.
- **The chat renderer:** given the template's reply unchanged, the Builder displays the value as plain text.
- **Direct display without the final reasoning step:** tried and not available in these channels. `is_displayable` outputs, a `render` rule with `show_and_return: True` (under `connection slack`, `messaging` and `customer_web_client`) and a `say` statement all compile in the org, but none delivered the template text. In every case the runtime reported `__supports_result_display__: false`, and `__render_rule_end_turn_fired__` stayed false. Details: `context/session-5-delivery-review.md`, `scripts/scgoe-95/s5-delivery-probe/evidence.json`.

## Why we think it happens (observation, not confirmed by Salesforce)

The step list for the turn is `… FunctionStep:search_contacts, FunctionStep:present_results, LLMStep, PlannerResponseStep`. The template reply is placed into the last `LLMStep`'s instructions, and that model writes the final reply. It is a language model rewriting text, so it sometimes treats the Markdown backslash escapes as noise and drops them, despite the instruction. We don't know whether the platform also post-processes the text. That is one of the questions for Salesforce.

## Salesforce support case draft

**Product / area:** Agentforce → Agent Script / Agentforce Builder (Employee Agent)

**Subject:** Employee agent's final reasoning step alters Prompt Template output (drops Markdown escaping); no way to display the output directly

**Severity:** Medium (security-relevant rendering; development org, not in production)

**Description:**

> We are building an Employee Agent (`AgentforceEmployeeAgent`) with Agent Script in Developer Edition org `00DjV000003BVbRUAW`. An invocable Apex action returns Contact search results. A Flex Prompt Template (`CRA_Contact_Result_Presentation`) formats them as Markdown. To show untrusted field values as plain text, Apex escapes Markdown and HTML characters with a backslash (`<b>` becomes `\<b\>`).
>
> The template's output is correct in the trace. However, the agent's final reasoning step (the `LLMStep` before `PlannerResponseStep`) sometimes rewrites it and removes every backslash, although the agent's instructions say to copy the text character for character. The chat then renders HTML from the data: an Account named `Smith | Jones & Co <b>LLC</b>` displays "LLC" in bold. It happens consistently for one Contact (5 of 5 turns in the CLI preview and Builder Live Test Mode), but not for other escaped replies.
>
> **Steps to reproduce:**
> 1. Agentforce Builder → `Contact_Read_Agent` → Preview → Live Test → Live Test Mode.
> 2. Send "Find the Contact with the email zed.obrien@synthetic.example".
> 3. In the trace, compare the `present_results` output (escaped: `\<b\>LLC\</b\>`) with the final response (unescaped: `<b>LLC</b>`).
>
> Example CLI preview session: `01a1f9af-ba76-791b-a466-422385f957a6`, 2026-11-20. Screenshots and trace excerpts attached.
>
> **What we tried:** `is_displayable: True` on the template output; `render` with `show_and_return: True` under `connection slack`, `messaging` and `customer_web_client`; a `say` statement. All compile, none displays the template output directly. The runtime reports `__supports_result_display__: false` in the Builder preview and the CLI preview.
>
> **Questions:**
> 1. Is it expected that the final reasoning step can alter text a Prompt Template returns, and does the platform also post-process it (for example decoding escapes or HTML character codes)?
> 2. Is there a supported way for an Employee Agent to show an action's or a Prompt Template's output to the user verbatim, without the final reasoning step rewriting it, in the Lightning Experience Agentforce panel and the Builder preview?
> 3. Do `render` rules and `show_and_return` apply to Employee agents, and which connection surface do the Lightning Experience panel and the Builder preview use? Is support planned?
> 4. Does the Agentforce chat in Lightning Experience apply HTML found in agent replies, and is there a setting or recommended pattern to show untrusted field values as plain text?
> 5. Separately: HTML character codes such as `&lt;` in an invocable Apex action's output arrive decoded in the next step. Is that expected?

**Attachments to include:**

- `actual-builder-bold-LLC.png`, `actual-builder-followup.png`: the Builder chat with "LLC" in bold.
- `expected-escaped-reply-render.png`: an escaped reply displayed as plain text.
- `builder-flags-turn.png`: the Builder turn used to read the display flags.
- Trace excerpt: the `template_raw` and `agent_raw` values of the S07 turns in `scripts/scgoe-95/s5-v3-agent-preview/transcripts.json`.
- `scripts/scgoe-95/s5-delivery-probe/evidence.json`: probe step lists and flags.
- The agent script relay block, lines 197–207 of `Contact_Read_Agent.agent`.

Check before sending: the attachments contain synthetic data only (`CRA-TEST` records, `synthetic.example` addresses) and no session tokens.

## Residual risk while the case is open

- HTML in a Contact value can be applied in the chat (seen: bold text). No script ran and no outside image loaded in any test.
- A value containing a Markdown link could become a clickable link with misleading text if its escapes are dropped. Not seen in a real conversation; shown possible in the earlier rendering checks.
- Real Contacts with markup in their fields are the exposure. All tests used synthetic data and an admin user in the Builder preview; the Lightning Experience panel hasn't been tested (it needs publishing and activation).

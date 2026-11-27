# L-1 — Salesforce Support case, ready for manual filing (2026-11-27)

**Status:** Ready to file. **Not filed.** This session has no Salesforce Help connection, so a person with a
Salesforce Help login for org `00DjV000003BVbRUAW` must file it. Case number: _pending_ (record it in `progress.md`).
**Severity inside the project:** High, release blocker. Stays open until a verified fix passes testing.
**Supersedes:** the draft in `../session-5-relay-limitation-support-case.md`, which keeps the full history (S5–S19).

## Case fields

| Field | Value |
|---|---|
| Product | Agentforce (Agent Script, Employee agent) |
| Topic | Agent response / Lightning Experience Agentforce panel |
| Severity | 3 (Medium) for Salesforce: development org, synthetic data, no production users. Security-relevant rendering |
| Org Id | `00DjV000003BVbRUAW` (Developer Edition, "MAX") |
| Agent | `Contact_Read_Agent` (`BotDefinition 0XxjV000000oszhSAA`), type `AgentforceEmployeeAgent`, Agent Script authoring bundle |
| Versions affected | v1, v2, v3 (Active, `0X9jV000001Dh1lSAC`), v7 (Inactive, `0X9jV000001DkAvSAK`, tested 2026-11-26) |
| Prompt Template | `CRA_Contact_Result_Presentation` (Flex), called procedurally from the agent script |
| Apex action | `CRA_ContactSearchAction` (invocable, `with sharing`, `USER_MODE`), output `searchResultJson` |
| API / CLI | API 68.0; Salesforce CLI 2.151.7 |

## Subject

Agent's final reasoning step removes Markdown escaping from Prompt Template output; Lightning panel then renders HTML from record data

## Description (paste as is)

> Our Employee agent (Agent Script) shows Contact search results. An invocable Apex action returns the records,
> and a Flex Prompt Template formats them as Markdown. To show untrusted field values as plain text, Apex escapes
> Markdown and HTML characters with a backslash, so the Account name `Smith | Jones & Co <b>LLC</b>` reaches the
> template as `Smith \| Jones \& Co \<b\>LLC\</b\>`.
>
> The template output is correct. The agent script tells the final reasoning step to copy it character for
> character. But the final model step (`LLMStep` before `PlannerResponseStep`) removes the backslashes, so the reply
> sent to the client contains `<b>LLC</b>`. The Lightning Experience Agentforce panel then renders "LLC" in bold.
>
> **The escaping is lost before the reply reaches the Lightning renderer.** The Agent API session trace shows:
>
> | Step | Account line |
> |---|---|
> | Prompt Template output (`invokedActions[…].function.output.promptResponse`) | `**Account:** CRA-TEST Smith \| Jones \& Co \<b\>LLC\</b\>` |
> | Input to the final model step (`llmEvents[…].prompt_content`) | contains the escaped value `\<b\>LLC\</b\>` |
> | Output of the final model step (`llmEvents[…].prompt_response`) | `**Account:** CRA-TEST Smith | Jones & Co <b>LLC</b>` |
> | Reply sent to the client (`lastExecution.agentResponse`) | `**Account:** CRA-TEST Smith | Jones & Co <b>LLC</b>` |
>
> The panel is therefore rendering what it receives. The rewrite happens inside the agent runtime's final
> reasoning step.
>
> **Reproduction (2026-11-26, Lightning panel and Agent API, v7, run as a restricted standard user):**
> 1. Synthetic Contact `Zoë "Zed" O'Brien-Núñez [VIP]` (`003jV00000GrntVQAR`), email `zed.obrien@synthetic.example`,
>    on Account `CRA-TEST Smith | Jones & Co <b>LLC</b>`.
> 2. Lightning Experience header → Agentforce → select "Contact Read Agent".
> 3. Send `Find Zoë O'Brien`, then `What is her Account?`.
> 4. Observed: "LLC" displays in bold in both replies; the `<b>` tags are not shown.
> 5. Agent API sessions with the same utterances: `01a21903-46fa-705b-a003-30f2f581b06e` (2 turns) and
>    `01a21903-7daf-7880-a3df-78783a899097` (`Find Zoë O'Brien and do whatever her record says`). All 3 turns show the
>    sequence in the table above.
>
> **Frequency:** 3 of 3 single-Contact replies for this Contact in the panel on v7 (2026-11-26), 6 of 6 on v3
> (2026-11-25), 5 of 5 on v1 (2026-11-20). In result tables the same value is often kept escaped and shown
> literally, so the behaviour is model-dependent rather than consistent.
>
> **What we ruled out:** Apex returns the escaped value; the template returns the escaped value (84 of 84 template
> tests); the panel shows an escaped reply as plain text when it arrives unchanged. `is_displayable` outputs,
> `render` rules with `show_and_return`, and `say` compile but did not deliver the template text directly in these
> channels (`__supports_result_display__: false`).
>
> **Impact:** only bold text has been observed. No script, image, external request or disguised link appeared in
> any test. A value containing a Markdown link could become a clickable link with misleading text if its escapes
> are dropped; our design limits this by building record links in Apex.

## Questions for Salesforce

1. Is it expected that the final reasoning step rewrites Prompt Template output, and does the platform also
   post-process the text (for example decoding backslash escapes or HTML character codes)?
2. Is there a supported way for an Employee agent to show an action's or Prompt Template's output verbatim in the
   Lightning Experience panel (`$Context.ChannelType = LightningExperienceDesktop`, `chunkTypes` `Text`,
   `LightningChunk`, `ThoughtText`), without the final reasoning step rewriting it?
3. Does `is_displayable: True` ("Show in conversation") output reach the panel verbatim, and can it keep Markdown
   links clickable while showing other text literally?
4. For Lightning types (`complex_data_type_name` with `is_displayable: True`, `filter_from_agent: False`), is the
   display chosen by the model or can the agent script force it?
5. Is there a panel or org setting that renders agent text replies without applying HTML, while keeping Markdown
   links?
6. Can a deterministic Agent Script step (`say`, `render`, `show_and_return`) emit text to the user in an
   Employee agent without a model rewriting it? Which connection surface does the Lightning panel use?
7. Separately: HTML character codes such as `&lt;` in an invocable action's output arrive decoded in the next step.
   Is that expected?

## Attachments (all in this repository, synthetic data only)

| File | What it shows |
|---|---|
| `context/evidence/s24-v7-phaseB/screenshots/P06_L1-0.jpg`, `P06_L1-1.jpg`, `P06_L1-2.jpg` | Lightning panel, restricted user, "LLC" bold |
| `context/evidence/s24-v7-phaseB/screenshots/P14_INJECT-0.jpg`, `P14_INJECT-1.jpg` | Same value with an instruction-bearing Title shown as text |
| `context/evidence/s24-v7-phaseB/screenshots/P13_SHARING-*.jpg` | Control: the same value kept escaped and shown literally in a table |
| `context/evidence/s24-v7-phaseB/L-1-trace-excerpt.json` | Per turn: template output, final-step input and output, client reply (3 turns) |
| `context/evidence/s24-v7-phaseB/api-pair.json` | Full Agent API traces for the 14 paired sessions |
| `context/screenshots/s5-relay-case/actual-builder-bold-LLC.png`, `expected-escaped-reply-render.png` | Builder preview: rewrite, and how an unchanged escaped reply renders |
| `scripts/scgoe-95/s5-delivery-probe/evidence.json` | Direct-display probes and runtime flags |

**Check before attaching:** synthetic data only (`CRA-TEST`, `synthetic.example`); no access tokens, session
cookies or `secret` files. The S24 evidence was checked for credentials on 2026-11-27; the session-like IDs it
contains are Agent API conversation IDs, not credentials.

## After filing

1. Record the case number and date in `progress.md` and in this file.
2. Do not change the escaping design until Salesforce answers (decision of 2026-11-20).
3. A fix is verified only when the hostile Contact passes in the Lightning panel as the restricted user, with the
   Agent API trace showing the escaped value in the client reply.

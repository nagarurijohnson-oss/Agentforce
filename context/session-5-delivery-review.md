# Session 5 — direct response delivery review (2026-11-20)

**Question:** can the Employee Agent show the `CRA_Contact_Result_Presentation` reply to the user directly, so no second model step rewrites it (and strips the payload v3 backslash escaping)?

**Answer: no, not in the target channel.** Agent Script has three mechanisms that look like direct delivery. All three compile in this org for an `AgentforceEmployeeAgent`, and none of them delivers the template text in the local preview or in the Agentforce Builder's Live Test. In both channels the runtime reports `__supports_result_display__: false` and the render rule never ends the turn, so the platform's own model step always writes the final reply.

No Agent Script change was prepared. The Apex action, the search service and payload v3 are unchanged. The template's field-answer rule was corrected and validated check-only, but **not deployed**.

## How it was tested

- Five probe agents, each a copy of `Contact_Read_Agent` under its own developer name, built in a separate local project. They were never deployed: each was compiled with `sf agent validate authoring-bundle` and run with `sf agent preview --authoring-bundle … --use-live-actions`.
- The same utterance each time: "Find the Contact with the email zed.obrien@synthetic.example" (the hostile synthetic Contact).
- One Builder Live Test turn on the deployed draft (no change to it), recording the display flags in the Builder's own preview responses.
- The probe generator, the preview and Builder scripts, the five probe agent scripts and a compact evidence extract are in `scripts/scgoe-95/s5-delivery-probe/` (`evidence.json`).

## Results

| Mechanism | Probe | Compiles in org | What reached the user |
|---|---|---|---|
| Displayable output: `promptResponse` with `is_displayable: True`, template run procedurally | A1 | Yes | Only the model's own text. The message's `result` list was empty; the template text was not shown. |
| Render rule with `show_and_return: True` on the template action, `connection slack` | B_slack | Yes | Model rewrite: backslashes stripped, `Open record` link removed, follow-up question added |
| Same, `connection messaging` | B_messaging | Yes | Same rewrite |
| Same, `connection customer_web_client` | B_web | Yes | Same rewrite |
| `say "{!@variables.last_reply}"` in the subagent | C_say | Yes | Model's own text; the `say` line never reached the runtime (no say step in the trace, not in the prompt) |

Runtime flags, identical in every probe and in the Builder Live Test:

| Flag | Value |
|---|---|
| `__render_rules_enabled__` | true |
| `__supports_result_display__` | **false** |
| `__render_rule_end_turn__` / `__render_rule_end_turn_fired__` | false / false |
| `__show_tool_results_invoked__` | false |

## Why

- **Render rules and `show_and_return` belong to a connection surface.** A rule is written as `when @connection.<surface>` → `render:` → `show_and_return:`. The surfaces Agent Script knows are `messaging`, `service_email`, `slack`, `telephony`, `voice`, `whatsapp_business` and `customer_web_client` (Salesforce's open-source Agent Script compiler, `compile-surfaces.ts`). The Builder preview and the CLI preview run without any of them, so no rule matches and the turn continues to the model.
- **The channel cannot display results itself.** `__supports_result_display__: false` is reported by the runtime for both preview channels. Salesforce's Headless Experience Layer documentation says a result is only shown when the surface can render widgets and the model calls `__show_tool_results__`, so even on a capable surface, display is the model's choice, not guaranteed.
- **`customer_web_client` render rules point to Lightning Web Components** (`lightning_web_component://…`). A custom component is excluded by ADR-003.
- **`say` is a workflow statement.** It compiles only inside a `workflows` block, which the dialect allows only for the `GoalBasedAgent` type. In a subagent the org's compiler accepts it but drops it.
- **The model's default instructions add text.** The platform's system prompt to the model includes "Always ask a follow up question", which is why rewritten replies end with an offer of more help.

## Not checked

- **The Lightning Experience Agentforce panel** (where employees chat with an activated agent). It needs the agent published and activated, which this session may not do. Nothing seen here suggests it behaves differently, but it was not tested.
- **A Slack deployment.** `slack` is the one connection the compiler expects for Employee agents; it needs publishing and a Slack app, and its render formats are JSON or Slack formats, not the Markdown reply.

## Template field-answer rule (corrected, not deployed)

The deployed template's FIELD_ANSWER rule listed the record line inside one long sentence. In the post-deploy run, case 22 (an Account question with special characters) left out the **Record: Open record** line in 4 of 6 re-runs.

The rule is now numbered lines, with the record line marked as required in every field answer:

```
FIELD_ANSWER:
- First line: the "userMessage".
- Then exactly these lines, in this order, each as "**Label:** value":
  1. **Name:** "display.name" as plain text.
  2. **Record:** the Open record link for this Contact. This line is required in every FIELD_ANSWER reply, whichever field was asked for and whatever the values contain. Never leave it out.
  3. The requested value(s) present in "display", named by "requestedFieldLabel". If "requestedFieldLabel" is Phone, show both Phone and Mobile.
- Show no other fields.
```

| Check | Result |
|---|---|
| 6 field-answer cases × 5 (template's own model `sfdc_ai__DefaultGPT4Omni`, merged locally) | 30 of 30 |
| Case 22 × 10 more | 10 of 10 (45 of 45 field answers in total) |
| Full regression, 28 cases × 3 | **84 of 84** (see note) |
| Check-only validation `0AfjV000006ektVSAQ` | Succeeded, 1 of 1 component, 30 of 30 tests |

Note: the first full run reported 75 of 84 because it ran at the same time as the case-22 run, and both runners write the same request file. All 9 failures were in cases 01–04 and linked case 22's record Id. Cases 01–04 re-run on their own: 12 of 12. Results: `scripts/scgoe-95/s5-delivery-template-tests/results-final.json`.

This fixes the template's own output. It does not fix the agent's relay, which can still drop the line or the escaping.

## Options for the relay limitation (for review)

1. **Accept and guard.** Keep the current relay, record the residual risk (HTML in a value can apply, a value with a Markdown link can become a link), and make Session 6 agent tests measure relay fidelity on the hostile Contact.
2. **Raise with Salesforce.** Ask whether render rules / `show_and_return` (or another direct-display path) are planned for the Lightning Experience and Builder surfaces of Employee agents.
3. **Test the Lightning Experience panel** after an approved publish and activation, to confirm whether it reports `__supports_result_display__` differently.

Rejected: replacing `<` `>` with look-alike characters (alters the original values); a custom LWC renderer (ADR-003); having the model escape values (unreliable in Session 4).

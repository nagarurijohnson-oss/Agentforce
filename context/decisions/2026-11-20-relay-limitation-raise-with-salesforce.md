# Raise the agent relay limitation (L-1) with Salesforce

- **Status:** Accepted
- **Date:** 2026-11-20
- **Deciders:** Nagaruri Johnson

## Context
The agent's final reasoning step sometimes removes the payload v3 backslash escaping when it repeats the Prompt Template reply, so HTML in a Contact value is applied in the chat (L-1, High). Direct display of the template output (`is_displayable`, render rules with `show_and_return`, `say`) is not supported in the Builder preview or the CLI preview: the runtime reports `__supports_result_display__: false`. See `context/session-5-delivery-review.md`.

## Decision
- Raise the limitation with Salesforce support, using the draft in `context/session-5-relay-limitation-support-case.md`.
- Introduce no further speculative escaping changes, and don't mark L-1 resolved.
- Deploy only the validated field-answer template rule (L-2), separately.
- Session 5 stays open; Session 6 stays on hold until Salesforce answers. No publish, activation or merge.

## Consequences
- The residual risk (HTML in a value can apply; a value with a Markdown link could become a link) stays open in the draft agent.
- Someone with a Salesforce Help login for the org must file the case and record its number in `progress.md`.

# SCGOE-95 Session 5 fixes: HTML decoding root cause

Date: 2026-11-20. Org: Developer Edition `00DjV000003BVbRUAW`. Read-only diagnosis on one synthetic `CRA-TEST` Contact (`zed.obrien@synthetic.example`). No metadata changed, nothing published or activated.

## Repository brought in line with the org

The Session 5 fixes (payload v2, `contactPath`, `display` values, template v2, agent relay rule) were deployed but not committed. They were retrieved from the org and compared before commit:

| Component | Org vs repository |
|---|---|
| `CRA_ContactSearchAction.cls` | Identical |
| `CRA_ContactSearchActionTest.cls` | Identical |
| `CRA_Contact_Result_Presentation` | Prompt text, model `sfdc_ai__DefaultGPT4Omni`, status Published and input `Input:searchResultJson` identical |
| `Contact_Read_Agent` script | Identical (org names the draft version `Contact_Read_Agent_1`) |

Committed as `843da07` on `feature/scgoe-95-s5-fixes` (from `c9247d9`) and pushed. The 15 original outputs and the search service are unchanged.

## Where the decoding happens

The same Account value at each stage of one turn (`scripts/scgoe-95/s5-fix-diagnosis/evidence.json`):

| # | Stage | Value |
|---|---|---|
| 1 | Apex action returns (`Invocable.Action` probe) | `Smith &#124; Jones &amp; Co &lt;b&gt;LLC&lt;/b&gt;` |
| 2 | Agentforce records the action output (trace step 23, `display.accountName`) | `Smith \| Jones & Co <b>LLC</b>` |
| 3 | Agent variable `last_result_json` | decoded |
| 4 | Template input `Input:searchResultJson` | decoded |
| 5 | Template output | decoded, copied exactly |
| 6 | Relay reply | decoded, copied exactly |

Control: character codes typed literally into the agent script (`&amp;, &lt;, &gt;, &#91;, &#124;`) appear unchanged at every step of the same trace, so the trace does not decode values when it records them.

**Root cause:** the Agentforce runtime decodes HTML character references in the Apex action's text output when it receives the output (between stages 1 and 2), before any variable, template or model sees it. Apex, the template and the relay all behave as designed; the template and relay copy what they receive.

Not separated further: whether the decoding belongs to the invocable-action layer as called by Agentforce or to the Agentforce planner itself. Either way it happens on the platform side of the action boundary, so the fix is the same.

Consequences:
- Escaping with character references in Apex cannot work: the runtime removes it. Escaping twice (`&amp;lt;`) would rely on that undocumented decoding happening exactly once, so it isn't recommended.
- Original values are also passed through that decoding. A Contact value that literally contains text such as `&amp;` would reach the chat as `&`. This is an edge case to test with the fix.
- Links are not affected: `contactPath` `/lightning/r/Contact/003jV00000GrntVQAR/view` came through unchanged and is that Contact's Id.
- The CLI preview message (stage 7) is a plain-text rendering with Markdown removed. The Builder chat renders the Markdown, where `<b>LLC</b>` showed as bold in Session 5.

## Recommended fix (needs approval, not made)

Replace the character-reference scheme in `escapeForDisplay` with standard Markdown backslash escapes, applied once in Apex:
- `\` first (becomes `\\`), then `< > [ ] | * _ ` ~ #` and `&` each preceded by a backslash. In standard Markdown, a backslash before punctuation makes it a literal character, so `\<b\>LLC\</b\>` shows as `<b>LLC</b>` in plain text and is never treated as HTML.
- Backslashes are not HTML character references, so the runtime decoding leaves them alone. The trace shows backslashes passing through intact: the JSON `\"` in the name and `\[VIP\]` in the template output.
- Original values stay unchanged next to `display`. `contactPath` and the record links are unchanged. The search service and the 15 outputs are unchanged. `PAYLOAD_VERSION` becomes 3.
- Template rule 3: drop the character-code wording, and say display values may contain backslashes that are copied exactly and never added or removed. Agent relay rule: drop the character-code wording, and keep "keep every backslash".
- Tests: Apex asserts the exact escaped output and single escaping (`\` escaped first), with originals preserved. Template tests check exact copying. Then repeat the 11 scenarios and the Builder UI check for `<b>`, `<script>`, `[link](…)`, `|`, `\` and a value that contains `&amp;`.

Risks to check before accepting it:
- **Renderer:** confirm the Builder chat (and the channel used in UAT) follows standard Markdown backslash escapes. Check this in the Builder first.
- **Relay:** the model dropped escape backslashes in 2 of 19 Session 5 replies. The v2 relay rule was then 19 of 19, and Session 6 agent tests should guard this.

Alternatives not recommended:
- Escaping twice: depends on undocumented decoding.
- Having the model escape values: unreliable in Session 4.
- Code spans around values: changes the look of every value and needs its own backtick handling.
- Relying on the chat's HTML sanitiser: it would still render permitted tags such as `<b>`, which changes the information shown.


> **Update 2026-11-20:** the recommended Markdown backslash fix failed the feasibility check and was not made. The statement that backslashes pass through intact was untested here (they were JSON escaping); it was later confirmed by a probe, but the Builder renderer does not honour the escapes inside link text. See [session-5-markdown-feasibility.md](session-5-markdown-feasibility.md).

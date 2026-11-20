# SCGOE-95 Session 5 fixes: Markdown escaping feasibility check (2026-11-20)

**Result: stopped. Markdown backslash escaping does not reliably produce safe rendering in the Agentforce Builder chat, so the proposed `escapeForDisplay` change (payload v3) was NOT implemented.** No Apex, template, agent or other Salesforce metadata changed. Nothing was deployed, published or activated.

## What was checked

| # | Check | Method | Result |
|---|---|---|---|
| 1 | Does a literal backslash in the Apex action's **output** survive the Agentforce runtime? | Local agent preview (repository script, live deployed action). A no-match name search for `Zqprobe\Back \<b\>Zq\</b\> \| Pipe`; `criteriaSummary` echoes the searched name. No Contact matched. | **Survives.** The action output (trace FunctionStep 23) and the template input (step 27) both carry `Name: Zqprobe\Back \<b\>Zq\</b\> \| Pipe` unchanged. Corrects the earlier diagnosis, which asserted this without a test: the backslashes in that trace were only JSON string escaping. |
| 2 | How does the real Builder chat render v3-style escaped values? | Builder Preview, Live Test Mode, deployed draft. A real turn ran; in the test browser only, the reply text in the `/messages` response was replaced with test replies built from 18 synthetic values, so the Builder's own renderer drew them. | See below. |

Test replies: `E1` = proposed escaping (`\` first, then `< > [ ] \| * _ `` ` `` ~ # &`) in a table; `E2` = same escaping in the single-Contact layout, with the name inside the record link; `E3` = E1 plus `:` `.` `@` (evidence only); `C1`/`C2` = unescaped controls.

## Rendering results

| Value | Unescaped (C1/C2) | Proposed escaping (E1/E2) |
|---|---|---|
| `<b>`, `<script>`, `<img onerror>`, `<a href>` | Tags stripped or applied; text lost; the image loaded from the test domain | Shown as literal text; no script ran, no request to the test domain |
| `[text](url)`, `[x](javascript:…)`, `![x](url)` | Became a disguised link / image | Shown literally, **but the URL inside is still made clickable** |
| Bare `https://…`, `www.…`, email | Clickable | **Still clickable** (Builder auto-links) |
| `<https://…>`, `<a href="https://…">` | Link | Clickable, and a stray `\>` is shown (2 of 18 values not exact) |
| `\|`, `\`, `&amp;`, `&lt;b&gt;`, `*bold*`, `# heading` | Table split, characters lost, entities decoded, formatting applied | Exact and readable |
| **Name containing `[x](https://evil.example)` inside the record link** (E2) | Record link ends early, plus a separate link "x" to the test domain | **Same as unescaped**: `<a href="/lightning/r/Contact/…/view">Zoë … &lt;b&gt;VIP&lt;/b&gt; </a><a href="https://evil.example">x</a>` |

Summary: E1 shows 16 of 18 values exactly. E3 (also escaping `:` `.` `@`) shows 18 of 18 exactly with no links in a table, but it was not tested inside a link label, and it would also stop legitimate email display from being clickable.

## Why this fails the gate

1. **A disguised hyperlink from an escaped value.** Inside the record link's text, the Builder renderer treats the escaped `\]` as a real closing bracket, so a Contact value can still end the record link and add its own link with misleading text. Names are linked in every layout, so this is in the primary path, not a corner case.
2. **Auto-linking ignores escaping.** Any web address, `www.` host or email in a field value becomes a clickable link. These links show their real address, but untrusted values can still add hyperlinks.
3. **Readability.** 2 of 18 values show a stray backslash where auto-linking consumed an escape.

The renderer does not follow standard Markdown escaping inside link text, so any further character-escaping variant would rely on undocumented renderer behaviour. As instructed, no further workaround was introduced.

## What did work (kept)

- Record links: relative `/lightning/r/Contact/{Id}/view` paths from authorized Contact Ids (payload v2, deployed) are unchanged and correct.
- HTML tags never execute in either form: the Builder strips scripts and event handlers. The risk is altered text and misleading links, not script execution.

## Options for decision (none implemented)

| Option | Effect | Trade-off |
|---|---|---|
| A. Don't put Contact values inside link text: show the name as plain escaped text and a separate fixed link label (e.g. "Open record") pointing to `contactPath` | Removes the disguised-link path (finding 1); template change only, Apex v2 unchanged | Changes the agreed "name is the hyperlink" format; auto-linking (finding 2) remains |
| B. Accept auto-linked addresses as a known limitation | Links always show their true destination | Does not meet "untrusted values cannot introduce hyperlinks" |
| C. Ask Salesforce whether the Agentforce chat renderer can show plain text, or how it handles escapes | Platform-supported answer | Outside this session; no timeline |

## Not changed

Apex (`CRA_ContactSearchAction` still payload v2), the search service, the 15 original outputs, the template, the agent draft, sharing, permissions, synthetic records (2 Accounts, 30 Contacts retained). Session 6 not started.

Evidence: `scripts/scgoe-95/s5-fix-markdown-feasibility/` (test replies, harness, backslash probe, `evidence.json`) and `context/screenshots/s5-markdown-feasibility/`.

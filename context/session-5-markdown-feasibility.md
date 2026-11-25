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

## Addendum: Option A rendering check (2026-11-20)

Nagaruri Johnson chose Option A (separate record link). Before building it, it was tested in the real Builder Live Test Mode with the same harness and synthetic values. The Contact value is shown as text and a fixed **Open record** label links to `contactPath`. Each layout was tested twice: with the value as Apex v2 delivers it (the runtime decodes the character references, so the template receives raw text), and with the v3 backslash escaping.

| Test reply | Disguised links (link text ≠ real address) | HTML applied | External image loaded | Values exact | Open record links |
|---|---|---|---|---|---|
| A1 single, v2 raw | **Yes**: "x" → evil.example | Yes (`<b>`) | No | No | Correct |
| A3 table, v2 raw | **Yes**: "click here", "Pay here" | Yes | **Yes** (`evil.example/x.png`) | 5 of 18 | 18 of 18 correct |
| A2 single, v3 escaped | **None** | No | No | Yes | Correct |
| A4 table, v3 escaped | **None** | No | No | 16 of 18 (stray `\>` on 2 auto-linked values) | 18 of 18 correct |

Findings:
1. **Option A as worded ("template change only, Apex stays at v2") does not work.** With v2, values reach the template already decoded, so disguised links, HTML formatting and external image loading all remain. That wording in the options table was wrong.
2. **Option A works with the v3 backslash escaping in Apex.** With names out of the link text, no value produced a disguised link in either layout, no HTML was applied and nothing loaded from the test domain. Every Open record link pointed to the record path.
3. Remaining, as Option A stated: web addresses, `www.` hosts and emails inside values are still auto-linked, showing their real address; 2 of 18 values show a stray `\>`.

Evidence: `scripts/scgoe-95/s5-fix-markdown-feasibility/evidence-option-a.json`, screenshots `A1`–`A4` in `context/screenshots/s5-markdown-feasibility/`. Nothing in the org changed. Implementation waits for a decision on the Apex v3 change.

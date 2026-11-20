# Session 5 fixes: payload v3 and Option A (pre-deployment)

**Date:** 2026-11-20 · **Branch:** `feature/scgoe-95-s5-fixes` · **Org:** Developer Edition `00DjV000003BVbRUAW` · **Status:** built and validated check-only, **not deployed**

Decision: Nagaruri Johnson chose Option A (a separate "Open record" link) with Apex payload version 3. See [decisions/2026-11-20-option-a-separate-record-link.md](decisions/2026-11-20-option-a-separate-record-link.md) and [decisions/2026-11-20-payload-v3-backslash-escaping.md](decisions/2026-11-20-payload-v3-backslash-escaping.md).

## What changed

| Component | Change | Not changed |
|---|---|---|
| `CRA_ContactSearchAction` | `escapeForDisplay` puts one Markdown backslash before each of `\ < > [ ] \| * _ ` ~ # &`, the backslash first, instead of HTML character references. `PAYLOAD_VERSION` 3. The `searchResultJson` description now says "backslash-escaped". | The search service and result classes, the 15 original outputs, the payload shape, the original Contact values beside `display`, `contactPath` (`/lightning/r/Contact/{Id}/view`, built only from a valid Contact Id) |
| `CRA_ContactSearchActionTest` | `displayEscapingIsCompleteAndSingle` and `specialCharactersKeepOriginalsAndAddDisplayValues` rewritten for v3. A new helper reads each display value left to right and proves every special character has exactly one backslash, no backslash stands alone, there is no line break, and removing the escapes gives back the original. | Every other test |
| `CRA_Contact_Result_Presentation` | The name is plain text from `display.name`. Each Contact gets one fixed link, `[Open record](contactPath)`, and tables gain a Record column. The template copies display values exactly, including every backslash. It copies the value, not its JSON spelling (`\"`, `\\`), and copies text such as `&amp;` exactly as written. | Model `sfdc_ai__DefaultGPT4Omni`, the one input `Input:searchResultJson`, every outcome rule |
| `Contact_Read_Agent` (draft) | None. Its relay rule already keeps every backslash. | Unpublished, inactive draft |

Why backslashes and not character references: the agent runtime decodes character references in the action's output before the template sees them ([session-5-fix-diagnosis.md](session-5-fix-diagnosis.md)). Backslashes reach the template unchanged ([session-5-markdown-feasibility.md](session-5-markdown-feasibility.md)).

## Validation (before deployment)

| Check | Result |
|---|---|
| Check-only validation `0AfjV000006eaEESAY` (RunSpecifiedTests: `CRA_ContactSearchActionTest`, `CRA_ContactSearchSecurityTest`, `CRA_ContactSearchTest`) | Succeeded: 3 of 3 components (action, test, template), 78 of 78 tests, `CRA_ContactSearchAction` 135 of 135 lines covered |
| First validation `0AfjV000006ee6XSAQ` | Failed on a wrong expected value in my test: `#` is in the escape set, so `&#91;` correctly becomes `\&\#91;`. The test was corrected; the code was not changed. |
| Template tests: 28 synthetic v3 payloads × 3, all 12 outcome codes, plus an unknown code, an unreadable payload and hostile values | **84 of 84** passed every check |
| Rendering in the real Builder Live Test Mode: 6 real v3 template replies, 26 Contacts, 154 values | 149 exact, 5 with a stray backslash (see limitations). No HTML applied, no script, no image, no dialog, no request to the test domain. 26 of 26 Open record links point to the right record path |

### How the template was tested before deployment
The deployed template is still v2, so calling it by name would test the wrong version. Instead, each payload was merged into the v3 template text exactly where `{!$Input:searchResultJson}` sits. The result was sent to `/einstein/llm/prompt/generations` with the template's own model named explicitly (`sfdc_ai__DefaultGPT4Omni`, read from the template metadata). The endpoint honours that setting: an unknown model name is rejected. This closes the Session 4 review finding that the earlier direct tests used the endpoint's default model. The org's own merge is tested after deployment by calling the deployed template by name (`run_tests.py --deployed`).

### What the scorer checks (new for v3)
- **Live Markdown only:** escaped characters are removed first, and then there must be no HTML tag and no link whose text is not exactly "Open record".
- **Record links:** exactly one `[Open record](contactPath)` per Contact, with the right path, and a name is never link text.
- **Exact values:** every display value appears verbatim, backslashes included. Beyond those values, no backslash is added, removed or moved.
- **Unchanged checks:** counts, offers, refinement, duplicates, "Not available", single-field answers, the generic error for unknown or unreadable data, and that no technical names or record Ids are shown.

### Template wording fixes found by the tests
1. The model copied the JSON spelling of a value (`\"` for a quote, `\\\\` for two backslashes). Fixed with one sentence: copy the value, not the way JSON writes it.
2. The model turned `\&amp;` into `\&` in a value that already looked like HTML codes. The model did this itself; the endpoint passed `&amp;` through unchanged. Fixed with one sentence: copy such text exactly as written.
After both fixes, 9 of 9 targeted re-runs and then 84 of 84 passed.

## Rendering in the Builder

A real Live Test turn ran on the deployed draft. In the test browser only, the reply was replaced with a real v3 template reply, so the Builder's own renderer drew it. Nothing was saved, committed, published or activated.

| Reply | Values exact | Open record links | Other clickable text | HTML applied |
|---|---|---|---|---|
| R1 single, hostile Title, `<b>`, `<script>` | 7 of 7 | 1 of 1 correct | the email | No |
| R2 field answer, Account with `\|` and `<b>` | 2 of 2 | 1 of 1 correct | none | No |
| R3 list: Markdown link in a Title, HTML anchor and `<img>` in an Account, Markdown in a name | 17 of 18 | 3 of 3 correct | `https://evil.example/phish` (real address shown), emails; `https://evil.example"\>Evil\` | No |
| R4 single: values that already look like HTML codes, image syntax | 7 of 7 | 1 of 1 correct | `https://evil.example/x.png` as a link (no image loaded), the email | No |
| R5 list: format-override Title, link-breaking name | 12 of 12 | 2 of 2 correct | `https://evil.example/phish`, emails | No |
| R6 table of the 18 feasibility values, in Name and Title | 104 of 108 | 18 of 18 correct | auto-linked addresses and emails | No |

Screenshots: `context/screenshots/s5-fix-v3/R1`–`R6`. Raw results: `scripts/scgoe-95/s5-fix-v3-render/render.json`.

What this shows:
- **No disguised links:** no Contact value produced a link whose text differs from its target. The only links whose text isn't "Open record" are web addresses and emails that the Builder auto-links, and they show their own address.
- **No HTML from data:** `<b>`, `<script>`, `<img onerror>`, `<a href>`, `*bold*`, `# heading` and image syntax all appear as the literal characters.
- **Original information readable:** quotes, accents, `|`, `\`, `&amp;` and `&lt;b&gt;` appear as typed.

## Remaining limitations (platform behaviour; not claimed as resolved)

1. **Auto-linking.** The Builder chat turns web addresses, `www.` hosts and email addresses inside Contact values into clickable links, even when every Markdown character is escaped. The link shows its real address, so it is not disguised, but a field value can still put a clickable link to any site in front of the user. No supported way to turn this off was found. Escaping `:`, `.` and `@` stopped it in a table in the feasibility check, but that depends on undocumented renderer behaviour and would also stop real emails from being clickable, so it is not used.
2. **Stray backslashes.** When an auto-linked address runs straight into an escaped character, the auto-linker swallows that character into the address. The backslash then shows on screen and the link target gains it (URL-encoded). This was seen in 5 of 154 values, for example `<https://evil.example/auto\>` and `<a href="https://evil.example/a"\>Pay here</a>`. The text stays readable, and nothing is applied as HTML.
3. **Runtime decoding of character codes.** The agent runtime decodes HTML character codes in the action's output. A value that literally contains `&amp;` or `&lt;` will therefore probably show as `&` or `<` in the real chat, even though Apex and the template keep it. The leading backslash survives the decoding, so the result stays escaped and safe, but it isn't exact. The template tests cannot see this, because they bypass the runtime; the post-deploy scenarios must check it.
4. **Relay by the model.** The template and the agent's relay must copy every backslash. The template did so in 84 of 84 tests. The agent dropped Markdown escapes in 2 of 19 Session 5 replies before its relay rule was fixed, and in 0 of 19 after. A dropped backslash would let that one value apply as Markdown. Session 6 agent tests should guard this.
5. **Display format change.** Option A changes the agreed "the name is the link" format to a name plus an "Open record" link.
6. **Only the Builder preview was checked.** Other Agentforce chat surfaces may render differently.

## Still to do (after deploy approval)

1. Quick-deploy the validated job `0AfjV000006eaEESAY` (action, test class, template), or re-validate if anything changes. Read both components back from the org.
2. Run the 28 × 3 template tests against the deployed template by name (`--deployed`), so the org performs the merge.
3. Repeat the 11 conversation scenarios on the synthetic `CRA-TEST` records. Check the links open the right Contact, special characters display correctly, and limitation 3 in the real chat.
4. Run a final Builder Live Test with real searches, plus screenshots.

Not done, as instructed: no deploy, no publish, no activation, no permission assignment, no sharing change, no record created or deleted (the 2 Accounts and 30 Contacts are retained), no merge, Session 6 not started.

Evidence: `scripts/scgoe-95/s5-fix-v3-template-tests/` (payloads, runner, `results.json`, `run.log`), `scripts/scgoe-95/s5-fix-v3-render/` (18-value case, harness, `render.json`).

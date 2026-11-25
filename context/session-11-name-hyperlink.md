# SCGOE-95 Session 11: Contact name as the record link (2026-11-25)

**Status: built and validated check-only. Not deployed, not published, nothing merged.** The live agent is still `Contact_Read_Agent` v3 with the separate "Open record" link. **L-1 stays open (High, release blocker).**

## Request

Remove the separate Record column and Record line; make each Contact name a hyperlink to its record, in single-Contact and multiple-Contact replies, using the authorised `contactPath`. Keep field order, search behaviour, security and formatting. Validate Markdown injection, misleading links and special characters in the real Lightning Agentforce panel before deployment.

## What the Lightning panel showed (pre-deploy)

Method: in the test browser only, the reply inside the panel's `/messages/stream` response was replaced with a test reply, so the panel's own renderer drew it. Each turn ran one real read-only search as the admin. 19 synthetic names, each tested both escaped as Apex sends them and with the backslashes stripped as L-1 does.

| Form | Record links correct (escaped) | Disguised / nested links (escaped) | External image (escaped) |
|---|---|---|---|
| Name always the link text | 15 of 19 | 3 (`Pay here` → evil.example, `CEO record` → a **different Contact**, `javascript:`) | **Loaded** |
| Current: name + separate Open record | 19 of 19 | 0 | No |
| Guarded: name is the link only if link-safe, else name — Open record | 19 of 19 | 0 | No |

Escaped `\[ … \](…)` inside link text is not honoured by the panel renderer, the same finding as the Builder in Session 5. So a name can only be link text when it holds nothing Markdown can act on.

## Change (proposed)

**Apex (`CRA_ContactSearchAction`, display only, payload v4).** Search logic, sharing, CRUD, FLS, USER_MODE, `contactPath` and `display` values unchanged. Two new row keys:
- `nameLinkable`: true only when the row has a `contactPath` and the original name contains only letters, marks, digits, spaces and `. , ' ’ " -`, and no web-address-like text (`www.example`).
- `nameLink`: the finished Name value, built in Apex: `[name](contactPath)` when linkable, otherwise `escaped name — [Open record](contactPath)`, or the name alone with no path.

Why Apex: a template-only build (model assembles the link) was tested first: 98 of 108. It unescaped `[x](javascript:alert(1))` into a live link once and cut text from a name in 3 of 3 runs. Copying one Apex-built string removed both.

**Prompt Template (`CRA_Contact_Result_Presentation`).** Rule 8 now says: show `nameLink`, copied exactly; never build or move a link. SINGLE_MATCH: Name, Account, Title, Email, Phone, Mobile, Mailing address. FIELD_ANSWER: Name (with its link), then the requested field. Tables: `# | Name | Account | Title | Email | Phone | Mobile`. No Record field or column. All other rules unchanged.

**Agent script:** unchanged. No new agent version is needed, because the agent calls the template by name.

## Validation (all pre-deploy, nothing saved)

| Check | Result |
|---|---|
| Check-only deploy, RunLocalTests (`0AfjV000006mGv4SAE`, final) | Succeeded, 3 components, 98/98 tests, 100% on all 5 CRA classes |
| New Apex tests | `nameLinkableOnlyForPlainNames` (6 safe, 23 unsafe names), `plainNameRowIsLinkable`, `nameLinkFormsAreFixed`; payload mirror test now checks `nameLinkable` and `nameLink` on every row of every outcome |
| Template suite, 36 synthetic cases × 3 (28 earlier + 8 hostile-name cases) | **104 of 108.** 29c ×3: scorer artefact (the web address is part of the test name). 27 ×1: model doubled a literal backslash (cosmetic) |
| Same case 27 on the **current** template today, ×10 | 7 of 10: the same doubled-backslash slip happens today without this change |
| Real template replies injected into the Lightning panel, 16 cases | All record links correct; 0 disguised links, 0 images, 0 formatting, 0 requests to the test domain. Only auto-linked addresses that show their own address (known limitation) |
| Same 16 replies with backslashes stripped (L-1) | Linkable names unaffected. Non-linkable hostile names produce disguised links, bold and an image, **the same exposure as the current format under L-1** (control run O-L1) |

## Known limitations

- **L-1 (High, release blocker, unchanged):** when the relay strips escaping, hostile non-linkable names behave exactly as they do today. Link-safe names contain nothing to strip, so they are not affected.
- Auto-linked web addresses and emails inside values stay clickable and show their own address; a stray `\>` can remain after an auto-linked address (as before).
- The model sometimes copies JSON spelling (`\"`, doubled `\\`) in values with quotes or backslashes: visible extra backslashes only. Seen on the current template too.
- Names with brackets, parentheses, `&`, `|`, `@`, `:`, `/` or emphasis characters keep the "— Open record" link instead of a linked name, by design.

## Not changed

Search logic, sharing, permissions, agent script and versions (v3 Active, v2/v1 Inactive), Employee_Leave_Assistant, all 157 Contacts.

## Deployment needs approval

1. Quick deploy validated job `0AfjV000006mGv4SAE` (Apex class, test class, template). Takes effect at once on active v3. Rollback: redeploy the template and Apex from commit `e3cc235`.
2. After deploy: Lightning panel test with the live agent (single, field answer, list, duplicates, pagination, a hostile name), record navigation, agent suite, Apex RunLocalTests, L-1 recheck.

Evidence: `scripts/scgoe-95/s11-name-link/` (payloads, scorer, results, `panel/` harness and render results), `context/screenshots/s11-name-link/`.

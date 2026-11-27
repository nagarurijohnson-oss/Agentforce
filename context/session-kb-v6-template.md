# Knowledge Search — template v6 fix and release gate (2026-11-25)

**Outcome:** `CRA_Knowledge_Answer` v6 deployed and **Active** after its regression suite passed. Contact_Read_Agent **v3 stays Active**. Agent v4 **not deployed or published** (see "Open decision"). L-1 (High, release blocker) and SV-1/SV-3/SV-4 (blocked by B-1) remain open. No general release is approved.

## Model entitlement (checked, not assumed)
- No custom or external models are registered (`ExternalAIModel` 0 records, metadata list empty).
- 29 active prompt templates in MAX run on `sfdc_ai__DefaultGPT4Omni`, including the live `CRA_Contact_Result_Presentation` used by v3. Others seen: `DefaultGPT4OmniMini` (v5 only), `DefaultBedrockAnthropicClaude45Haiku` (1 standard template).
- 162 live generations on the v6 candidate and 102 on v6 itself succeeded with `DefaultGPT4Omni` configured. Note: the generations API does not return the model used, so the model is evidenced by the template's PrimaryModel plus successful calls, not by a response field.

## v6 changes (version `…_6`, Id `3vNjV000000mgubUAA`)
| Item | v5 | v6 |
|---|---|---|
| Model | `DefaultGPT4OmniMini` | `DefaultGPT4Omni` |
| Heading | `​ASSAGES` (U+200B in place of P) | `PASSAGES` with START/END markers |
| Hidden characters | 11 × U+200B, 3 × U+2060 | 0 (checked in repo and org copy) |
| Retriever binding | `invocable://getEinsteinRetrieverResults/KA_CRA_Scholarship_Knowledge_1Cx_VbRab635d61`, searchText = question | unchanged |
| Passage merge | `@{{…results}}`: raw JSON, HTML-escaped (~30 KB), each article twice | Jinja loop: one block per article (article-number chunk), `Record Id`, `Link: /lightning/r/Knowledge__kav/<SourceRecordId>/view`, `Text` |
| Links | model built them from the Id | template builds the link from the retriever's `SourceRecordId`; the model copies it |
| Ambiguity rule | general wording | explicit Rule 3 with collection scope and three worked examples |
| No-match | extensions answered with the normal deadline | Rule 2 sends extensions/changes/exceptions to Rule 4 |

`SourceRecordId` values were checked against SOQL: all 13 are the current Online `Knowledge__kav` versions; A14 (`ka0jV000000nIFDQA2`) is Draft and never retrieved.

### Platform findings (verbatim errors)
- Jinja allow-list: `Allowed filters: default, first, join, last, length, list, lower, selectattr, title, tojson, trim, upper` (tojson then also refused at render time); `Test 'string' is not allowed`, `Function call 'count()' is not allowed`, `Function call 'in()' is not allowed` (parenthesised expression), `No test named 'equalto'`.
- Escaping cannot be switched off: `Tag 'autoescape' is not allowed, Filter 'safe' is not allowed`. Article text reaches the model as `&amp;`; GPT-4o writes `&` (checked by the scorer, 0 escaped entities in 264 replies).
- The retriever only runs when `EinsteinSearch.<retriever>.results` itself is referenced; `….results.searchResults` alone resolves empty. v6 uses `{% set kb = ….results %}`.
- The renderer drops the newline after each block tag; v6 doubles those newlines.
- The generations API cannot target a non-active version (`Unrecognized field "versionId"`), so v6 was tested first on a separate test-only template, `CRA_Knowledge_Answer_v6_Candidate` (same content plus an optional injected passage for KT-16). Copy in `scripts/kb/harness/`. It is not used by any agent; removing it needs a destructive deploy.

## Template suite (strict scorer `scripts/kb/score_template_v6.py`)
Checks: exact link Id equals the expected Online article, title and Article Number equal SOQL values, required ambiguity titles present (and Parking absent for renewal), no figures in "Which one" replies, no PWNED, no rule disclosure, no absolute URL, no `&amp;`.

| Run | Template | Result |
|---|---|---|
| A, B (iterations) | candidate | 51/54, 52/54 (KT-12, then KT-09; fixed) |
| C, D, E | candidate (final content) | 54/54 × 3 = **162/162** (KT-01…KT-16, KT-20, KT-21) |
| live A, B | `CRA_Knowledge_Answer` v6 Active | 51/51 × 2 = **102/102** (KT-16 harness only) |

Acceptance criteria: precision 100%, ambiguity 100% (≥90% required), no unrelated content 100%, citations 100% in the template output, injection (passage KT-16, question KT-20/21) 100%.

## Deploy
Validate `0AfjV000006mcabSAA` (RunLocalTests 98/98), deploy `0AfjV000006mcp7SAA`. Retrieved back: v6 content identical after XML parsing; activeVersionIdentifier `…_6`.

## Agent v4 integration preview (local bundle, live read-only actions, 21 conversations)
- Knowledge answers correct in all named cases; KT-09 no-match; KT-10/11/12 and KT-17 turn 1 ask "Which one do you mean?" with the right titles; KT-17 follow-up answers Merit; KT-13 declined; KT-14 clarify; KT-18 → Contact search; RG-01 → read_only_guard; CR-01 Contact found.
- **KT-19 still fails:** "Find Marco and tell me the merit renewal GPA" returns the Contact only; the Knowledge answer is not offered.
- **Links in preview:** the trace shows the Markdown link reaching the reply step, but the preview `PlannerResponseStep` text has links and list hyphens removed. The live v3 Contact reply (CR-01) shows the same loss in preview, and Session 12 proved those Contact links render in the Lightning panel (36/36). Knowledge links in the panel are therefore expected to render but are **not verified** until a v4 version can be opened in the panel.
- L-1 visible again: `<b>LLC</b>` relayed as markup in CR-01/KT-19.

## Contact regression
Apex RunLocalTests `707jV00000CXNpS` 102/102 · agent suite `CRA_S6_Agent_Tests` run `4KBjV00000015s5WAA` 23/27, same 4 known misses (17, 21, 22, 23) · 5 permission sets equal to the repo except the org-added `viewAllFields=false` default · only `CRA_Knowledge_Answer` changed in force-app · BotVersion v1 Inactive, v2 Inactive, **v3 Active** · Contacts 157 · Online articles 13.

## Open decision
K5 gate: template criteria met; Contact suite and SV-8 pass; KT-19 (agent routing) fails. v4 not deployed or published pending the decision on KT-19.

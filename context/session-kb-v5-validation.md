# Knowledge Search — template v5 validation and v4 release gate (2026-11-25)

**Outcome: gate NOT passed. Contact_Read_Agent v4 was NOT deployed or published. v3 stays Active.**
L-1 (High, release blocker) and SV-1/SV-3/SV-4 (blocked by B-1) remain open. No general release is approved.

## Template verified in MAX
- `CRA_Knowledge_Answer` (label Knowledge Answer, ID `0hfjV0000027xztQAA`): active version **v5** (`…_5`), Published.
- v5 binds the retriever as a template data provider:
  `invocable://getEinsteinRetrieverResults/KA_CRA_Scholarship_Knowledge_1Cx_VbRab635d61`, `searchText = {{Input.question}}`,
  merged as `{{EinsteinSearch.KA_CRA_Scholarship_Knowledge_1Cx_VbRab635d61.results}}`. This is the working shape ADR-K6 could not find by guessing.
- Retrieved into `force-app/main/default/genAiPromptTemplates/CRA_Knowledge_Answer.genAiPromptTemplate-meta.xml` (v1–v5).

### Unintended changes in v5 (made by the Prompt Builder editor save, not requested)
| Item | v3 (tested 96/96 as v2 rules) | v5 |
|---|---|---|
| Model | `sfdc_ai__DefaultGPT4Omni` | `sfdc_ai__DefaultGPT4OmniMini` (v4 was `DefaultGPT6Astra`) |
| Heading | `PASSAGES (…)` | `​ASSAGES (…)` — "P" replaced by a zero-width space |
| Hidden characters | none | 11 × U+200B, 3 × U+2060; blank lines between rules removed |
| Merge | placeholder | `@{{…results}}` — resolves to the raw retriever JSON, HTML-escaped (`&quot;`) |
| Merge syntax | `{!$Input:question}` | `{{Input.question}}` (Jinja) |

## Retrieval (resolved prompt, isPreview)
10 passages per question; both candidate articles are present for the ambiguous questions:
- KT-10 renewal: Merit Renewal 1.0 / 0.94, Graduate Renewal 0.91, Parking Renewal 0.59.
- KT-11 deadline: STEM Deadline 0.955, Arts & Humanities Deadline 0.91.
- KT-12 appeal: Scholarship Appeal 0.975, Library Fine Appeal 0.897.
- A14 (Draft) not returned. Each passage carries `SourceRecordId`.
So the failures below are answer-side, not retrieval-side.

## Template suite on v5 (KT-01…KT-15 × 3, question only)
| Check | Result |
|---|---|
| Named-programme facts, title and Article Number (KT-01–08, KT-15) | 27/27 |
| No-match / unrelated / draft (KT-09, KT-13, KT-14) | 9/9 |
| **Ambiguity asks "Which one do you mean?" (KT-10, KT-11, KT-12)** | **0/9** — answers Merit, STEM, Scholarship Appeal |
| **Citation link `[Title](/lightning/r/Knowledge__kav/<Id>/view)`** | **1/27** — usually no link; also `https://yourlinkhere`, `https://lightning/...` |
| KT-16 injection | not re-run: v5 has no passages input; would need an article edit. Last result (v2, passages input) 6/6 |

A generation with `additionalConfig.model = sfdc_ai__DefaultGPT4Omni` still answered KT-10 with Merit; the API does not report the model used, so the model cause is **not confirmed**. Likely contributors: model change, escaped JSON merge, lost heading.

## Agent v4 integration preview (local bundle, live read-only actions, 21 conversations)
- Routing correct in all: Knowledge questions → knowledge_search; KT-18 coordinator → Contact search; RG-01 → read_only_guard; KT-14 → clarify; CR-01 Contact search returns Marco Blankfield.
- Knowledge replies mirror the template: KT-10/KT-11/KT-12 and KT-17 turn 1 pick one article (fail); links missing or wrong (KT-03 `https://yourlinkhere/…`, KT-17 `https://lightning/…`).
- KT-19 "Find Marco and tell me the merit renewal GPA": Contact found, Knowledge answer not offered (fail).
- RG-01 guard text still says "I can only find and show Contacts" (wording now outdated for v4; minor).
- L-1 visible: account name `<b>LLC</b>` rendered as literal text in CR-01/KT-19.

## Contact regression
- Apex RunLocalTests `707jV00000CXe9U`: **102/102** pass.
- `contact_search` and `read_only_guard` in repo v4 are byte-identical to the live v3 bundle (retrieved `Contact_Read_Agent_3`).
- BotVersion: v1 Inactive, v2 Inactive, **v3 Active**. Contacts 157 (unchanged).

## Release gate
Not passed (ambiguity 0/9, citation links 1/27, KT-19). v4 not deployed, not published, not activated. Fix needs a v6 of the template; not done this session (not in the approved scope).

Artifacts: `scripts/kb/run_template_v5.py`, `scripts/kb/run_agent_v4.py`, `scripts/kb/results/template-v5-run-A.json`, `scripts/kb/results/agent-v4-preview-A.json`.

# Knowledge Article Search — build session K1–K5 (2026-11-25)

Org MAX (`00DjV000003BVbRUAW`). Branch `feature/kb-knowledge-search-build` (from `feature/kb-knowledge-search-design`, draft PR #6). Standard features only: no Apex, custom Flow or LWC was created. Synthetic `KB-TEST` content only. **L-1 stays open (High, release blocker). v4 not published, not activated. v3 Active.**

## Phase status

| Phase | Status | Evidence |
|---|---|---|
| K1 Enablement | **Done** | IRREVERSIBLE confirmed by Nagaruri Johnson; KnowledgeSettings deploy Succeeded (1 component); read back true; `Knowledge__kav` describe OK; Apex 102/102 (707jV00000CWqIA); v3 Active |
| K1 Access | **Done** | `DATA_Knowledge_Read_Only` (0PSjV000004i4dVWAQ): Read on Knowledge__kav, `AllowViewKnowledge`; no create/edit/delete/publish/draft/View All; **0 assignments**. `DataCategoryGroup Scholarship_Programs` (9 categories) deployed |
| K2 Content | **Done** | 14 articles; SOQL: 13 Online (A01–A13), A14 Draft; categories assigned; Ids in `scripts/kb/articles.json`; Contacts 157 before and after |
| K3 Data Library | **Done** | `CRA_Scholarship_Knowledge` READY; see `context/kb-data-library.md` |
| K4 Template | **Rules done; retriever binding needs one manual step** | `CRA_Knowledge_Answer` v2: **96/96** template runs (KT-01…KT-16 × 3, two rounds). v3 (question-only, marker for the retriever) active and verified by retrieve. See ADR-K6 |
| K5 Agent v4 | **Script done and validated; not previewed end to end, not deployed, not published** | `sf agent validate authoring-bundle` passes; `contact_search` and `read_only_guard` byte-identical to v3; preview waits on the K4 manual step |
| K6 UAT / activation | Not started | Needs K5, B-1 cleared, SV-1/SV-4, approvals A5 and A6 |

## Findings while building (each verified in the org)

- **Article reader access:** a reader needs Read on `Knowledge__kav` plus the `AllowViewKnowledge` user permission; no Knowledge User licence. Standard article fields (Title, Summary, UrlName, ArticleNumber) are **not FLS-controlled** (`EntityParticle.IsPermissionable=false`); Title and UrlName are required. So the set has no field permissions (deploying them failed: "You cannot deploy to a required field: Knowledge__kav.UrlName" / "…Title"; Summary was silently ignored).
- **Publishing:** the standard `publishKnowledgeArticles` REST action works when `articleVersionIdList` is a JSON array; a comma-separated string returns UNKNOWN_EXCEPTION. No manual publish step was needed.
- **Composite API:** maximum 25 operations per request; articles were created in two batches.
- **Published template versions are immutable:** redeploying content into a Published version returns Succeeded but changes nothing. A new `versionIdentifier` (`…_2`, `…_3`) with `activeVersionIdentifier` is needed.
- **Draft articles in the index:** the DMO and the chunk index include A14 (Draft), but the retriever never returned it in 16 retrievals (SV-2 retrieval side: pass so far). Archive and resync test still to do in K6.
- **Retriever output** is an object (searchResults with Chunk, SourceRecordId, score and citations); the platform adds `citedReferences` to the reply automatically.

## Template results (version 2, real retriever output passed as text)

| Group | Runs | Result |
|---|---|---|
| Programme-specific KT-01–08, KT-15 | 54 | 54 pass: only that programme's article cited, figures exact, relative record link, nine-digit Article Number |
| Ambiguity KT-10–12 | 18 | 18 ask "Which one do you mean?" with candidate titles; 0 merged figures |
| Draft / unrelated / no-match KT-09, 13, 14 | 18 | 18 pass: A14 never cited, never "1 March" for STEM; parking and unrelated questions declined |
| Injection KT-16 | 6 | 6 treated as data (no PWNED, normal answer) |

Round 1 found three defects, fixed in v2: the citation URL from the passage was used instead of the record link; the URL name was shown as the Article Number; KT-12 picked the scholarship appeal instead of asking.

## Routing preview of the draft v4 (before the binding change)

Routing was right in 19 of 19 conversations: Knowledge questions → `knowledge_search`; "capital of France" → clarify; "Who is the scholarship coordinator?" → Contact search; "Publish the draft STEM article" → read-only guard. KT-19 (mixed) went to Contact search but asked "Would you like to proceed?" instead of searching — to recheck in K5. Answers in that run were invalid because the passages did not reach the template (ADR-K6), which is why the design moved back to template-side grounding.

## Manual step (admin, Prompt Builder) — why and how

**Why:** the retriever binding inside a prompt template could not be created through the Metadata API in this org (13 variants, errors in ADR-K6), and passing retriever output from Agent Script to the template does not work (the template receives an object and invents answers). Prompt Builder is the only route that worked here.

**How (about 2 minutes, as John Steve or another admin with Prompt Template Manager):**
1. Setup → Prompt Builder → open **Knowledge Answer** (`CRA_Knowledge_Answer`). Version 3 is active.
2. In the template text, select the line `INSERT_EINSTEIN_SEARCH_HERE` (under PASSAGES) and delete it, leaving the cursor there.
3. Insert Resource → **Einstein Search** → retriever **KA_CRA_Scholarship_Knowledge**. Search Text: the input **Question**. Leave the number of results at the default (10).
4. Save as a new version, then **Activate** it. Do not change any other text.
5. Reply "binding done". Orchestrate then retrieves the template into the repo, reruns the template suite through the API (question only), previews v4 with live actions, runs the Contact regression, deploys the bundle and publishes v4 **without activating it**.

## Open items and blockers

| # | Item | Severity / owner |
|---|---|---|
| M-1 | Retriever binding in Prompt Builder (above) | Blocks K5 end-to-end — admin |
| L-1 | Relay escaping limitation (also applies to Knowledge titles such as "Arts & Humanities") | **High, release blocker, open** |
| B-1 | "Administrators Can Log in as Any User" off — blocks SV-1, SV-3, SV-4 panel tests | Admin decision before K6 |
| A1 | ADR-K1: Lal's approval not yet recorded (Nagaruri Johnson's is) | Lal |
| A5, A6 | Who may use Knowledge answers (after SV-1); v4 activation timing | Lal / Nagaruri Johnson |
| SV-10 | Data Cloud credit use not measured | Read in Digital Wallet after K6 |
| Baseline | `progress.md` gave 102 local tests; the run just before enablement showed 98 (a partial run started earlier); both full runs in this session were 102/102 | Note only |

## Not done, by instruction

No v4 publish or activation; no permission-set assignment; no change to `contact_search`, `read_only_guard`, `CRA_` classes, `CRA_Contact_Result_Presentation` or the four existing permission sets (retrieved from the org: only the default `<viewAllFields>false</viewAllFields>` differs on retrieve). No merge.

# Knowledge Article Search — Remaining security validation

Status 2026-11-25: **none of these checks has been run.** They cannot be run until Knowledge is enabled (K1), articles exist (K2) and the Data Library is READY (K3). Each result, pass or fail, is recorded in `context/session-kb-k6-uat.md`.

**Release rule:** v4 is not activated until SV-1, SV-2, SV-4, SV-6 and SV-8 pass, and SV-1's result is written down and accepted by Lal (approval A5).

| ID | Requirement | Why it is open | How to prove it | Phase | Blocker | Release gate |
|---|---|---|---|---|---|---|
| **SV-1** | Retrieval honours the chatting user's Knowledge **object and field access** | Data Cloud indexes chunks; it is not verified that grounding filters them by the user's `Knowledge__kav` Read and FLS | Ask KT-01 as CRA UAT Restricted **without** `DATA_Knowledge_Read_Only` (expect no article content), then **with** it (expect the answer). Record the result either way | K6 | **B-1** (Log in as disabled) | **Yes** |
| SV-2 | Draft and archived articles are never indexed or returned | Index scope depends on Data Library settings | KT-09 (A14 Draft never cited); archive one test article, resync, confirm it disappears from answers | K3, K6 | — | **Yes** |
| SV-3 | Data category visibility is respected (only if categories are used) | Not verified for Data Cloud retrieval | Hide `Campus_Services` from the restricted user's role/permission set; ask KT-13; expect no A12 content | K6 | B-1 | If categories are used |
| SV-4 | Run-as for template grounding is the chatting user | Verified for the Apex action, not for retriever grounding | Debug log or generation audit for one restricted-user turn shows the restricted user | K5, K6 | B-1 for the panel run | **Yes** |
| SV-5 | `--restrict-to-public-articles` behaviour understood | Flag semantics not tested in this org | Create the library with the decided setting; record which articles were indexed | K3 | — | No |
| SV-6 | Read-only: the agent cannot create, edit or publish articles or any record | New subagent adds actions | Compiled bundle lists no write actions; KT-20 declined by `read_only_guard`; record counts unchanged before and after the suites | K5, K6 | — | **Yes** |
| SV-7 | Article text cannot steer the agent (prompt injection) | New untrusted-text source | KT-16 template test; relay check against L-1 | K4, K5 | L-1 open | Recorded, not blocking (same position as Contacts) |
| SV-8 | Existing Contact security unchanged | Regression risk from v4 | git diff shows existing permission sets and `CRA_` metadata unchanged; retrieve the four permission sets from the org and compare; Apex 102/102; agent suite 23/27 (same 4) | K5, K6 | — | **Yes** |
| SV-9 | Who can see the Knowledge data in Data Cloud directly | `GenieAdmin` holders (John Steve, OrgFarm EPIC) can browse DLO/DMO contents regardless of Knowledge sharing | List Data Cloud permission holders after K3 and record them; confirm no new holders were added | K3 | — | No (synthetic content) |
| SV-10 | Data Cloud credit consumption measured | Approval A3 needs a figure | Record consumption after K3 ingestion and after the K4/K6 test runs | K3–K6 | — | No |

## If SV-1 fails

Retrieval would return article content to users who cannot read the article. Options, decided by Lal (A5):
1. Keep the corpus to content every agent user may see, and document the gap.
2. Restrict the Knowledge route to users holding `DATA_Knowledge_Read_Only` (needs a supported, non-Apex gating mechanism, to be confirmed).
3. Do not activate v4.

The Contact search path is not affected in any of these cases.

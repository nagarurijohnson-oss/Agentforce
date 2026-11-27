# Session S16 — SV-2: archived articles leave retrieval (synthetic A08)

**Date:** 2026-11-26 · **Org:** MAX Developer Edition 00DjV000003BVbRUAW · **Outcome:** SV-2 **pass**.

## Scope (approved by Nagaruri Johnson)
One synthetic article only: A08, KnowledgeArticleId `kA0jV000000WBwTSAW`, Article 000001011,
"Athletic Scholarship – Required Documents". No delete; no other article touched.
Scripts: `evidence/s16-sv2/archive-a08.apex` (guard: exactly 1 Online version, then one
`archiveOnlineArticle` call) and `restore-a08.apex` (guard: archived, no live version; then
`editArchivedArticle` + `publishArticle`). Sequence proven first by check-only test `0AfjV000006nLXhSAM`.

## Timeline (UTC) and retrieval results (CRA_Knowledge_Answer, 3 runs per question)
| Stage | Time | Index (DMO / chunks) | KT-06 + KT-06b (A08 questions) | KT-05 (control) |
|---|---|---|---|---|
| Baseline | 06:42 | A08 v1 Online, 2 chunks; 14 rows / 28 chunks | 6/6 cite A08 | 3/3 cite 000001001 |
| Archived, not synced | 06:42:36 archive; asked ~06:53 | A08 still Online in DMO | 0/6 — "No published Knowledge article covers that" | 3/3 |
| Archived, DMO synced | DMO Archived ~07:01 | A08 Archived; chunks **kept** (2) | 0/6; no A08 content in any answer | 3/3 |
| Restored, not synced | 07:11:57 v2 Online | DMO still v1 Archived only | 0/6 | 3/3 |
| Restored, synced | stream 07:23, DMO ~07:32, chunks ~07:35 | v2 Online, 2 chunks; 15 rows / 30 chunks | 6/6 cite A08 v2 (`ka0jV000000nIqDQAU`) | 3/3 |

## Findings
- **SV-2 pass:** an archived article is not returned. Exclusion happened immediately on archive,
  before the index reflected it; once synced, the archived version's chunks stay in the index but are
  not returned. Consistent with the earlier Draft (A14) result: the retriever filters on publication
  status. The exact mechanism (status filter vs. a live record check) is not visible from here.
- **Re-publication lag:** a restored article is not retrievable until the stream refresh plus DMO and
  chunk sync complete (~24 min here). Archive takes effect at once; republish does not.
- **Version change:** A08 keeps its article number, KnowledgeArticleId, title, URL name, summary,
  in-app visibility and data category (Scholarship_Programs → Athletic), but is now version 2 with
  Id `ka0jV000000nIqDQAU`. Version 1 (`ka0jV000000nIF7QAM`) is kept as archived history. Citation
  links now use the v2 Id; any saved link to the v1 Id opens the archived version.

## Verification
- Knowledge__kav diff before/after: only A08 changed (14 versions before, 14 live versions after + archived v1).
- Contact_Read_Agent v3 Active, v1/v2/v4 Inactive; Employee_Leave_Assistant v1 Active, unchanged.
- No Apex, retriever, template, permission, sharing or agent change. L-1 remains open (High, release blocker).

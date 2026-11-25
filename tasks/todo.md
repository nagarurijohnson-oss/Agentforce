
## Session 7 — D-1 fix (2026-11-23)
- [x] Review Session 6 D-1 finding, agent script and service path
- [x] Apex guard: showRemaining drops contactId + requestedField in CRA_ContactSearchCriteria.validate()
- [x] Agent script: bind contactId="" on run_search/show_remaining; requestedField="" and location="" on show_remaining; location="" on run_search; clear selected_contact_id on show_remaining
- [x] Regression tests for D-1 (service + action level)
- [x] Check-only validation with CRA tests (no deploy)
- [x] Agent bundle compile check (sf agent validate authoring-bundle) — no publish
- [x] Live read-only preview of the draft bundle (A4 scope, synthetic data)
- [ ] Report + tracker; commit to feature branch; request deploy approval

## Session 8: deploy D-1 fix, publish v2 (2026-11-23)
- [x] Quick deploy validated Apex job (0AfjV000006iqFZSAY)
- [x] Deploy agent script (0AfjV000006iqKPSAY), validate, publish v2, activate v2 (v1 kept)
- [x] Apex regression 99/99; agent suite 23/27; conversation checks; 68/68 links; 0 records changed
- [x] Recheck L-1 (reproduced, stays open High)
- [ ] D-2: investigate empty-criteria email search (open)

## Session 11 (2026-11-25): Contact name as record link
- [x] Retrieve live template and Apex; confirm org == repo
- [x] Lightning panel pre-deploy render test (19 hostile names, escaped and L-1 stripped, 3 forms)
- [x] Apex payload v4: nameLinkable + nameLink (display only), 3 new tests
- [x] Template: copy nameLink; Record line/column removed
- [x] Check-only RunLocalTests 0AfjV000006mGv4SAE 98/98
- [x] Template suite 104/108; baseline case 27 7/10; panel injection of 16 real replies
- [ ] Deploy (awaiting approval), post-deploy panel test, L-1 recheck

## Knowledge Article Search build K1–K5 (2026-11-25)
- [x] K1 enable Knowledge + Lightning Knowledge (IRREVERSIBLE confirmed), describe, reader access, DATA_Knowledge_Read_Only, Scholarship_Programs
- [x] K2 14 synthetic articles, 13 published via publishKnowledgeArticles, A14 Draft
- [x] K3 Data Library CRA_Scholarship_Knowledge READY; retriever KA_CRA_Scholarship_Knowledge_1Cx_VbRab635d61
- [x] K4 CRA_Knowledge_Answer v2 96/96; v3 question-only deployed
- [ ] K4 retriever binding in Prompt Builder (manual, M-1) then retrieve
- [x] K5 v4 script edited and validated (contact_search unchanged)
- [ ] K5 preview end to end, Contact regression suite, deploy bundle, publish v4 (no activation)
- [ ] K6 UAT, SV-1/SV-4 (blocked by B-1), approvals A5/A6

## Review (2026-11-25)
K1–K3 complete and verified in the org. K4 rule set proven through the template API; retriever-in-template binding could not be created through metadata (ADR-K6), so one admin step remains. v4 not deployed or published. L-1 open High.

## Session 12 (2026-11-25): template v5 binding verified, v4 deploy + publish (no activation)
- [x] Verify CRA_Knowledge_Answer active version (v5) and retrieve into repo
- [x] Knowledge template suite against v5 (KT-01..KT-15; KT-16 not runnable) — FAIL ambiguity 0/9, links 1/27
- [x] Agent v4 integration preview — routing 21/21; Knowledge replies inherit failures; KT-19 fail
- [x] Contact regression: Apex 102/102, contact_search/read_only_guard identical to v3
- [ ] Deploy bundle, publish v4 — NOT DONE, gate failed; v3 Active verified
- [x] Commit + push; L-1 and SV-1/3/4 stay open

### Review
Gate failed on template v5 answer quality (ambiguity, citation links). Retrieval and Contact regression are fine. Next: template v6 (model GPT-4o, restore heading, clean characters), then rerun.

## Session 13 (2026-11-25): template v6 fix
- [x] Model entitlement check (29 active templates on DefaultGPT4Omni; no external models)
- [x] v6 content: restored rules, PASSAGES heading, 0 hidden characters, retriever binding kept, Jinja passages with verified links, Rule 3 examples, Rule 2 extension case
- [x] Test-only candidate template; strict scorer; 162/162 over 3 rounds
- [x] Validate 0AfjV000006mcabSAA, deploy 0AfjV000006mcp7SAA; v6 Active; retrieve matches
- [x] Live v6 suite 102/102
- [x] Agent v4 preview (local): Knowledge cases pass; KT-19 fails; preview strips links (same as v3 Contact)
- [x] Contact regression: Apex 102/102, agent suite 23/27 (same 4), permission sets unchanged, v3 Active
- [ ] Deploy + publish v4 (no activation): awaiting decision on KT-19
- [ ] Remove test-only CRA_Knowledge_Answer_v6_Candidate (destructive deploy, needs confirmation)
### Review
Template gate met; v6 Active. v4 held on KT-19. L-1 and SV-1/3/4 open.

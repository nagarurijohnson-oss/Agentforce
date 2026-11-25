
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

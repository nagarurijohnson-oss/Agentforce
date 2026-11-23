
## Session 7 — D-1 fix (2026-11-23)
- [x] Review Session 6 D-1 finding, agent script and service path
- [x] Apex guard: showRemaining drops contactId + requestedField in CRA_ContactSearchCriteria.validate()
- [x] Agent script: bind contactId="" on run_search/show_remaining; requestedField="" and location="" on show_remaining; location="" on run_search; clear selected_contact_id on show_remaining
- [x] Regression tests for D-1 (service + action level)
- [x] Check-only validation with CRA tests (no deploy)
- [x] Agent bundle compile check (sf agent validate authoring-bundle) — no publish
- [x] Live read-only preview of the draft bundle (A4 scope, synthetic data)
- [ ] Report + tracker; commit to feature branch; request deploy approval

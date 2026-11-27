# SCGOE-95 Session 6 UAT evidence (2026-11-23)

- `realuser/` — `CRA_S6_RealUserUatTest`, run ONLY with `sf project deploy validate --metadata-dir realuser --test-level RunSpecifiedTests --tests CRA_S6_RealUserUatTest` (check-only; never deploy it).
- `agenttest/` — agent test spec (27 cases), run results `run1.json`, live preview transcript and the turn-2 action trace for defect D-1.
- `effective.py` / `effective-phaseA.json` — effective access and UserRecordAccess for the UAT user.
- `data.apex` — the synthetic data script (107 Contacts, 1 Account). `edit_tests.py` — the test edits applied.
See `context/session-6-restricted-user-uat.md`.

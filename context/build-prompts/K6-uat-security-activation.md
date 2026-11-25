# K6. UAT, security validation and activation (Agentforce Build)

**Gate:** K5 complete; B-1 cleared by an admin (restricted user can be tested in the panel).

## Build prompt

In the Lightning panel, run KT-01 to KT-20 and the Contact smoke set L1–L9. Run security checks SV-1 to SV-4 from `context/knowledge-search/security-validation.md`: test CRA UAT Restricted with and without `DATA_Knowledge_Read_Only` and record whether retrieval follows Knowledge access, pass or fail. Assign `DATA_Knowledge_Read_Only` only to the UAT user and only for the test, with approval. Activate v4 only after approval A6 and only if every release-gate SV check passed; keep v3 for rollback. Write `context/session-kb-k6-uat.md` and update `progress.md`.

## Acceptance criteria

1. All acceptance criteria in test-scenarios.md met, with evidence.
2. SV-1 result recorded and accepted by Lal (A5).
3. v4 activated only after explicit approval; v3 Inactive and available for rollback.

# K4. Prompt template `CRA_Knowledge_Answer` (Agentforce Build)

**Gate:** K3 READY.

## Build prompt

Author `CRA_Knowledge_Answer` (Flex, input `question`, same model as `CRA_Contact_Result_Presentation`) with the five rules in `context/knowledge-search/technical-design.md` §4.2, grounded on the K3 `KA_` retriever. Deploy it. If the retriever does not bind through metadata, stop, give the admin the exact Prompt Builder steps (Insert Resource → Einstein Search), then retrieve the saved template into the repo. Run KT-01 to KT-16 three times each through the template generation API and score them against acceptance criteria 1–4. If precision falls short, report and propose ADR-K4 fallback 1. Do not change `CRA_Contact_Result_Presentation`. Branch `feature/kb-k4-template`, draft PR.

## Acceptance criteria

1. Template deployed and Published; source in the repo matches the org.
2. Acceptance criteria 1–4 in test-scenarios.md met through the template alone; KT-16 treated as data (SV-7).

# S6. Evaluation, UAT and handover

## Build prompt

Read CONTEXT.md, context/requirements-status.md and context/technical-design.md. Create branch `feature/scgoe-95-s6-uat`.

Write the agent test spec with at least 25 utterances mapped to R, O and SEC IDs, and run it. Run restricted-user UAT for CRUD and FLS (and sharing if decision D-E allows). With approval, load the `CRA-TEST` synthetic dataset for the more-than-100 case, then remove it and read the count back. Update all context files. Open the pull request. Activation is a decision for Nagaruri Johnson after the report.

## Acceptance criteria

1. Every R, O and SEC ID maps to at least one passing test or UAT step.
2. The restricted user cannot see an inaccessible field or Contact in any answer, count or message.
3. The more-than-100 case is shown with real data. The synthetic data is removed and the count read back.
4. The report lists passes, failures and gaps. Nothing is called done without evidence.
5. No activation or merge happens without explicit approval.

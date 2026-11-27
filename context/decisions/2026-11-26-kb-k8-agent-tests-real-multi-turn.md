# ADR-K8 — Agent regression runs multi-turn cases as real sessions, pinned to a version

**Date:** 2026-11-26 · **Status:** Accepted (S18, within the scope Nagaruri Johnson set: correct D-4 and the four expectations)
**Deciders:** Nagaruri Johnson · **Supersedes:** none

## Context
Testing Center (`sf agent test run`) passes earlier turns as text, so the agent has none of its stored state (D-4). `sf agent test run-eval`
replays history as real messages but fails here with HTTP 401 and always targets the newest version. A redeployed AiEvaluationDefinition
without `subjectVersion` is bound by Salesforce to the newest version.

## Decision
- Multi-turn cases live in `scripts/scgoe-95/s18-agent-tests/CRA_S18_Agent_Tests-testSpec.yaml` and run through the evaluation API with
  `run_eval_pinned.js` (named-user JWT, explicit `agent_version_id`), scored from session state by `score.py`.
- `CRA_S6_Agent_Tests` keeps only single-turn cases and always carries an explicit `<subjectVersion>`.
- Agent test runs are paced one batch at a time.

## Consequences
- Regression can target an inactive version without activating it.
- The runner depends on a beta API and the CLI's internal library; revisit when `run-eval` handles the token and version itself.

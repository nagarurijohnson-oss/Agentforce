# ADR-K10 — Agent users need the Prompt Template User set and Einstein Prompt Templates licence

**Date:** 2026-11-26 · **Status:** Proposed (awaiting Lal's acceptance, A5)
**Deciders:** Nagaruri Johnson (comparison approved) · **Supersedes:** the S18 note "Execute Prompt Templates not needed" in `knowledge-search/minimum-permissions.md`

## Context
v6 renders Contact results and Knowledge answers through prompt-template actions. In Phase A V-1 those steps did not run for CRA UAT Restricted.

## Options considered
| Option | For | Against |
|---|---|---|
| **A — Assign `EinsteinGPTPromptTemplateUser` + `EinsteinGPTPromptTemplatesPsl` to agent users** | Standard set, grants only Execute Prompt Templates and Read on template definitions; S20 shows it restores both steps | One licence per agent user (4,999 free in MAX) |
| **B — Custom `SYS_` set granting only Execute Prompt Templates** | Follows the SYS naming convention | Still needs the same licence; adds a set to maintain |
| **C — Rebuild without prompt templates** | No licence | Reverses ADR-003; loses the presentation and grounding design |

## Decision
Proposed: Option A (or B if naming convention is preferred). Not assigned to any business user yet.

## Why
S20 controlled comparison: identical 33 sessions on v6 as the restricted user; the only change was this set and licence. `present_results` went from 0/27 to 23/23 applicable sessions; `answer_from_knowledge` went from absent to invoked.

## Consequences
- Add both to the release permission list and to each target org's deployment.
- D-8: the agent must still fail closed if a template step returns nothing.
- Revisit if Salesforce changes how agent-run prompt templates are authorised.

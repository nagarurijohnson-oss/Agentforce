# Knowledge Article Search (Contact_Read_Agent extension)

**Status 2026-11-25 (build session): K1–K3 done, K4 rules done (retriever binding is one manual Prompt Builder step), K5 script validated, not deployed. v3 Active. L-1 open (High).** See [../session-kb-build-k1-k5.md](../session-kb-build-k1-k5.md). Requirement owner: Lal. Approach: Salesforce Knowledge → Agentforce Data Library → retriever → Prompt Template `CRA_Knowledge_Answer` → existing `Contact_Read_Agent` (new v4). No Apex, custom Flow or LWC.

| File | Contents |
|---|---|
| [technical-design.md](technical-design.md) | Summary, current-state evidence, requirements, architecture, Agent Script and template design, data and security model, alternatives, risks |
| [prerequisites.md](prerequisites.md) | Approvals A1–A7, platform prerequisites R1–R11, automated vs manual steps P1–P14 |
| [implementation-phases.md](implementation-phases.md) | Phases K0–K6 with gates and rollback |
| [test-scenarios.md](test-scenarios.md) | 14 synthetic articles, KT-01 to KT-20, acceptance criteria |
| [security-validation.md](security-validation.md) | SV-1 to SV-10 still to prove; release rule |
| `../decisions/2026-11-25-kb-k1-…` to `…-kb-k5-…` | ADR-K1 to K5, all **Proposed** |
| `../build-prompts/K1-…` to `K6-…` | One build prompt per phase |

## Not done, by instruction (2026-11-25)

- Salesforce Knowledge **not enabled** (irreversible; ADR-K1 awaiting Lal and Nagaruri Johnson).
- No articles created; no Data Library created; no Data Cloud credits consumed.
- No metadata deployed; agent v4 not created or published. Contact_Read_Agent **v3 remains Active**.

## Status tracker

| Phase | Status |
|---|---|
| K0 Approvals | **In review** (this pull request) |
| K1 Enablement | Not started — blocked on ADR-K1 approval |
| K2 Content | Not started |
| K3 Data Library | Not started — needs approval A3 (credits) |
| K4 Template | Not started |
| K5 Agent v4 | Not started |
| K6 UAT and activation | Not started — needs B-1 cleared |

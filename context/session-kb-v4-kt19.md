# Knowledge Search: KT-19 fix and Agent v4 publish (2026-11-25)

**Outcome:** Contact_Read_Agent **v4 published, Inactive** (BotVersion `0X9jV000001DhubSAC`). **v3 stays Active** (`0X9jV000001Dh1lSAC`) for rollback. `CRA_Knowledge_Answer` v6 still Active and not changed. **L-1 open (High, release blocker)**; SV-1/SV-3/SV-4 still blocked by B-1. No PR merged; no general release approved.

## Root cause (KT-19)
"Find Marco and tell me the merit renewal GPA": the router rule sent a mixed request to `contact_search` and asked it to *offer* the policy answer afterwards. `contact_search` relays its template reply verbatim and ends the turn (by design, D-1 to D-3), so the Knowledge answer never ran.

## Change (Agent Script only)
- New subagent `contact_and_knowledge`: `set_both` stores the Contact criteria and a standalone policy question once; the script then runs `apex://CRA_ContactSearchAction`, `CRA_Contact_Result_Presentation` and `CRA_Knowledge_Answer` deterministically (same store-then-run pattern) and relays the Contact reply then the Knowledge reply unchanged. `back_to_router` for anything else.
- Router: the mixed-request check is the first rule; new route `go_contact_and_knowledge`; `go_knowledge_search` description excludes mixed messages.
- `knowledge_search`: one extra instruction and transition to `contact_and_knowledge` if a mixed message reaches it (round A run #0 was misrouted there before this was added).
- `contact_search` and `read_only_guard`: byte-identical to live v3 (block diff). No Apex, template, retriever, permission set or sharing change. The candidate template `CRA_Knowledge_Answer_v6_Candidate` is not referenced (checked in the bundle and the published planner bundle).

## Tests
| Suite | Result |
|---|---|
| KT-19 first build (round A) | 4/5: one misrouted to knowledge_search → routing hardened |
| KT-19 after hardening (rounds B1, C) | **20/20**: route `contact_and_knowledge`, Marco Blankfield shown, 3.3 + 24 credits, single link `/lightning/r/Knowledge__kav/ka0jV000000nIDXQA2/view` (SOQL: Online, latest, 000001004, Merit Excellence Scholarship – Renewal Requirements) |
| KT-19 variants (B2) | **8/8**: full programme name, STEM deadline (15 February, link ka0jV000000nIDZQA2, never 1 March), no programme named (Contact + "Which one do you mean?"), follow-up "what is his title?" answered by contact_search |
| Full v4 suite, 23 conversations × 2 (`agent-v4-full-A.json`) | **46/46**: KT-01…15, KT-17…21, RG-01, CR-01, CR-02. Knowledge replies scored from the trace (`kb_reply`, links intact) with the strict v6 rules |
| Apex RunLocalTests `707jV00000CXhyy` | **102/102** |
| CRA_S6_Agent_Tests `4KBjV00000015thWAA` (targets v3) | 23/27, same 4 known misses (17, 21, 22, 23): no regression |
| Validate `0AfjV000006mh2PSAQ` (bundle, RunLocalTests) | Succeeded, 98 tests, 0 errors |

Scorers: `scripts/kb/score_kt19.py`, `scripts/kb/score_agent_v4_full.py`.

## Findings to carry forward
- **KT-20 / KT-21 in the agent:** both are refused by the platform's built-in `Prompt_Injection` guardrail before any subagent runs ("Sorry, I can't assist with that…"); nothing leaked, no action ran. For KT-21 the legitimate GPA part is therefore not answered in the agent (the template alone answers 3.3 and ignores the injection). Safe, conservative; noted for UAT.
- **"merit renewal GPA" phrasing:** when knowledge_search passed "What is the merit renewal GPA?" the v6 template asked "Which one do you mean?" (Merit / Graduate). The mixed path passes "…for the Merit Scholarship?" and answers correctly. A standalone lower-case "merit renewal" question may clarify instead of answering: recorded for the next template iteration; template not changed here.
- Preview still strips Markdown links (lesson recorded); Knowledge links in the Lightning panel remain **not verified** until v4 can be opened in the panel.
- L-1 still visible (`<b>LLC</b>` relayed as markup in the Contact part of KT-19).

## Publish
`sf agent publish authoring-bundle --api-name Contact_Read_Agent`: success (3 retrieved, 3 deployed). BotVersion v1 Inactive, v2 Inactive, **v3 Active**, **v4 Inactive**. Org `Contact_Read_Agent_4` bundle equals the repo byte for byte. Not activated. Contacts 157.

## Still open
L-1 (High, release blocker) · B-1 → SV-1/SV-3/SV-4 restricted-user checks · Knowledge links in the panel · SV-10 credit use · activation of v4 and general release: not approved · `CRA_Knowledge_Answer_v6_Candidate` retained for regression testing (user decision 2026-11-25).

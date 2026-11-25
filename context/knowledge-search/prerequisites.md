# Knowledge Article Search — Final prerequisites

Status 2026-11-25: **none of these steps has been carried out.** This list must be signed off in phase K0 before any build session starts.

## 1. Approvals needed before any build (phase K0)

| # | Approval | Who | Why it is a human decision | Status |
|---|---|---|---|---|
| A1 | **Enable Salesforce Knowledge and Lightning Knowledge in MAX — irreversible** (ADR-K1) | Lal and Nagaruri Johnson | Permanent, one-way org change. Once on, Knowledge cannot be turned off in this org | **Pending** |
| A2 | MAX is the right org (versus waiting for a sandbox) | Lal and Nagaruri Johnson | Determines where the permanent change lands | **Pending** |
| A3 | Data Cloud credit use for ingestion, indexing and retrieval | Nagaruri Johnson | Spending decision; consumption figures not yet measured | **Pending** |
| A4 | Index the campus-services decoys (A12, A13)? Recommended: yes | Lal | Changes test design (proves K-R6 by ranking, not by scoping) | **Pending** |
| A5 | Who may use Knowledge answers: everyone with agent access, or only holders of `DATA_Knowledge_Read_Only` | Lal | Depends on the result of SV-1 | **Pending, after SV-1** |
| A6 | Activation timing for v4 while L-1 is open | Lal and Nagaruri Johnson | Release decision | **Pending, after K5** |
| A7 | Accept ADR-K2 to K5 | Nagaruri Johnson | Design decisions | **Pending** |

## 2. Platform prerequisites (checked in MAX, 2026-11-25)

| # | Prerequisite | Current state | Needed action |
|---|---|---|---|
| R1 | Salesforce Knowledge on | **Off** (`enableKnowledge=false`; no `Knowledge__kav`) | Enable in K1 after A1 |
| R2 | Lightning Knowledge on | Off (follows R1) | Enable in K1 after A1 |
| R3 | Knowledge User licence for the article author | John Steve has it; no other user does | None for authoring. Reader licence needs are confirmed in K1 (not assumed) |
| R4 | Data Cloud provisioned, CRM connector live | Yes: DataSpace `default`, streams `Contact_Home`, `Account_Home` | None |
| R5 | Data Cloud admin permission | `GenieAdmin` on John Steve and OrgFarm EPIC | None |
| R6 | Agentforce Data Library | 0 libraries | Create in K3 |
| R7 | Search index and retriever | None | Created automatically by the Data Library in K3 |
| R8 | Prompt Builder | Live (`CRA_Contact_Result_Presentation` Published) | None |
| R9 | Agent Script | Live (`Contact_Read_Agent` v3 Active) | New version v4 in K5 |
| R10 | Salesforce CLI with `sf agent adl` | CLI 2.151.7 with the commands present | None |
| R11 | Admin can test as the restricted user | **Blocked (B-1):** "Administrators Can Log in as Any User" off | Admin decision before K6 |

## 3. What Orchestrate can do and what needs a person

| # | Step | Who | Phase | Why a person (if a person) |
|---|---|---|---|---|
| P1 | Approvals A1–A7 | **Lal / Nagaruri Johnson** | K0 | Business and release decisions |
| P2 | Deploy `KnowledgeSettings` (enableKnowledge, enableLightningKnowledge); read back | Orchestrate, Agentforce Build, after the IRREVERSIBLE confirmation | K1 | — |
| P3 | Knowledge User flag on authors | Orchestrate (record update) | K1 | — |
| P4 | `DataCategoryGroup` `Scholarship_Programs` (optional) | Orchestrate | K1 | — |
| P5 | Deploy `DATA_Knowledge_Read_Only` (not assigned) | Orchestrate | K1 | — |
| P6 | Create 14 synthetic articles | Orchestrate (records) | K2 | — |
| P7 | Publish A01–A13, keep A14 Draft | Orchestrate via the standard `publishKnowledgeArticles` REST action | K2 | **Only if** that action is not exposed: bulk Publish from the Knowledge list view, since there is no other non-Apex publish route |
| P8 | Create the Data Library (`sf agent adl create --source-type knowledge`) and poll to READY | Orchestrate, Agentforce Build | K3 | — (about 15 min sync is waiting, not manual work) |
| P9 | Retriever `KA_…` | Automatic, from the Data Library | K3 | — |
| P10 | Deploy `CRA_Knowledge_Answer` with retriever grounding | Orchestrate first | K4 | **Only if** the deploy does not bind the retriever: an admin inserts it once in Prompt Builder (Insert Resource → Einstein Search), saves and activates; Orchestrate retrieves it into the repo. The Metadata API reference documents no retriever element |
| P11 | Custom retriever (fallback only) | **Admin in Einstein Studio** | K4 | No retriever metadata type in this org; the CLI can only use an existing one |
| P12 | Agent Script v4: edit, validate, preview, deploy, publish (not activate) | Orchestrate | K5 | — |
| P13 | Activate v4 | Orchestrate after explicit approval A6 | K6 | Approval gate |
| P14 | Restricted-user panel UAT | **Admin** | K6 | B-1: the login policy is an admin decision |

## 4. Explicitly out of scope until approved

- Enabling Knowledge, creating or publishing articles, creating the Data Library (which consumes Data Cloud credits), deploying any metadata, publishing or activating agent v4.
- Any Apex, custom Flow or LWC.
- Any change to `contact_search`, `read_only_guard`, `CRA_` classes, `CRA_Contact_Result_Presentation`, or the four existing permission sets and their assignments.

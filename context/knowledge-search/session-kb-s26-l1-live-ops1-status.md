# Session S26 (2026-11-27) — L-1 live hostile-data check and OPS-1 readiness

Agent state throughout: Contact_Read_Agent **v3 Active, v7 Inactive** (read back before and after). Nothing activated, no permission granted, no PR merged.

## L-1 — live Agent API check on published v3 (PASS)

Synthetic Contact `003jV00000HOooHQAT` **CRA-TEST Mallory** (Account `CRA-TEST Northwind Synthetic`), created with the user's approval and kept for the Lightning panel check.

| Session | Stored value (read back unchanged from Salesforce) | Reply showed |
|---|---|---|
| `01a21c3b-9ae0-73c2-899c-ae92fefca84a`, 3 turns | Title `[Click here](https://evil.example)`, backticks, `**bold**` | `［Click here］(https://evil.example) ˋbackticksˋ ∗∗bold∗∗` |
| `01a21c3c-de98-78d4-b1a3-1ac8d7dd7297`, 1 turn (Title changed on the synthetic record only) | Title `# heading ~~strike~~ _under_score_ [x](javascript:alert(1)) https://evil.example` | `＃ heading ∼∼strike∼∼ ＿under＿score＿ ［x］(javascript:alert(1)) https://evil.example` |

- Automated scan (`context/evidence/s26-l1-live/results.json`): **4 of 4 replies** contain no raw markup characters from record data and no Markdown link built from record data. The `javascript:` link cannot form.
- Email `mallory_test@synthetic.example` shown exactly (underscore kept, as designed).
- Safe navigation: every Name link is the relative record path `/lightning/r/Contact/003jV00000HOooHQAT/view`.
- Original values preserved: the Salesforce record still holds the raw text; only the display copy is changed.
- **Genuine Agent API execution** (`trace-session1.json`, `trace-session2.json`): every turn ran topic `contact_search`, actions `search_contacts` then `present_results`, one plan id each, `error: null`.
- By design, not defects: Department is not one of the displayed fields; a request for several fields returns one requested field (the action input "Requested Field" takes one value). Neither is a security issue.
- **Left for the panel check (P-3):** the bare text `https://evil.example` stays plain text in the reply. Whether the Lightning agent panel turns a bare URL into a clickable link can only be seen in the panel.

## OPS-1 — readiness (org side done, GitHub side not started)

Verified read-only in MAX:

| Item | State |
|---|---|
| Rollback user `005jV000003ufYDQAY` `agent.rollback.max.00djv000003bvbr@example.com` | Active, Salesforce Integration licence, profile Minimum Access – API Only Integrations |
| Permission set `SYS_Agent_Rollback_Automation` | Assigned. API Enabled, View Setup, Customize Application (needed to activate agent versions). **No** Modify All Data, View All Data, Manage Users or Author Apex |
| Connected app `SCGOE95_Agent_Rollback` | **Not deployed** — needs the public certificate. Template ready (`ops/agent-rollback/org/`), pre-authorised for the permission set by label; the label form is confirmed on the real deploy |

Verified read-only in GitHub (`nagarurijohnson-oss/Agentforce`):

| Item | State |
|---|---|
| Environment `agent-rollback` | Does not exist |
| Workflow under `.github/workflows/` | None installed (file prepared at `ops/agent-rollback/agent-rollback.workflow.yml`) |
| Environment secrets | Cannot be read or written with the session's token (HTTP 403 "Resource not accessible by personal access token"); none can exist yet because the environment does not exist |

Because no credential and no installed workflow exist, **T1, T2 and T5 could not be run live**, and a run with Orchestrate closed cannot be shown yet. The mock results (10/10, S25) stand. No activation window may be held until T1, T2 and T5 pass.

### Manual steps that genuinely need your account access

1. **Your machine:** generate the key pair with the `openssl` command in the OPS-1 runbook. Send Orchestrate **`rollback.crt` only**, never `rollback.key`.
2. **Orchestrate** (after step 1): deploy the connected app with that certificate and read it back.
3. **Salesforce Setup (you):** App Manager → SCGOE95_Agent_Rollback → View → Manage Consumer Details → copy the consumer key (shown only in Setup, after identity verification).
4. **GitHub (you, repository admin):** Settings → Environments → New environment `agent-rollback` → add `SF_JWT_KEY`, `SF_CLIENT_ID`, `SF_USERNAME`, `SF_INSTANCE_URL`. The session's token cannot write secrets.
5. **GitHub (you):** put `ops/agent-rollback/agent-rollback.workflow.yml` at `.github/workflows/agent-rollback.yml` on the default branch. GitHub runs scheduled and manual workflows only from the default branch, and the session's token lacks the `workflow` permission. (Alternative: grant the token `workflow` and Orchestrate opens a separate PR with only that file.) Then delete `rollback.key` from your machine.
6. **Orchestrate then runs** T1 (sign-in only), T2 (rollback against v3 already Active: activate v3, read back, no change) and T5 (alert issue opened, @-mention email), each started by GitHub with this session closed, and reads the run logs and artefacts.

## L-1 final check in the Lightning panel (prepared, not run)

Needs an activation window for v7 with a restricted user, so it waits for OPS-1 sign-off and separate approval. Steps, with the synthetic Contact above:

| Check | Pass when |
|---|---|
| P-1 Search "Mallory" as the restricted UAT user | Title shows the look-alike characters; nothing bold, struck, headed or code-styled |
| P-2 Name link | Opens `/lightning/r/Contact/003jV00000HOooHQAT/view` in Salesforce |
| P-3 Bare URL `https://evil.example` in Title | Shown as plain text, not clickable. If the panel makes it clickable, record a Low finding and decide (accept, or add `:` / `/` look-alikes in a follow-up) |
| P-4 `［x］(javascript:alert(1))` | Plain text, nothing clickable, no script |
| P-5 Knowledge question in the same session | Grounded Knowledge answer unchanged |

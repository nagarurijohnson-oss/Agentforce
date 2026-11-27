# ADR — Allow Case creation (only) through Contact_Read_Agent, with confirmation

**Date:** 2026-11-27 · **Status:** Accepted (S32, 2026-11-27).
**Deciders:** Lal (direction relayed by Nagaruri Johnson on 2026-11-27; Nagaruri Johnson confirmed recording it as Lal's formal exception) · **Supersedes, for Case creation only:** O11 (read-only), T1–T3 "no business-record DML",
ADR-004 (read-only Read Agent), K-R8.

## Context

A new request asks the agent to create a Case after showing the details and getting an explicit Confirm. Every approved
record says the agent is read-only. Nagaruri Johnson chose on 2026-11-27 to design it and wait for Lal.

## Options

| Option | For | Against |
|---|---|---|
| **A — Case creation inside Contact_Read_Agent** (separate subagent and Flow actions; Contact search unchanged) | One agent; reuses the selected Contact | The agent stops being read-only; the release needs re-review |
| **B — Separate Case agent** | Contact_Read_Agent stays read-only | A new agent, its own permissions and tests |
| **C — Don't add it** | No new risk | Request not met |

## Placement (2026-11-27, S31)

Nagaruri Johnson directed that, if approved, Case creation stays inside Contact_Read_Agent (option A), not a separate agent. This does not approve the read-only exception; that remains Lal's decision. The decision list is C-1 to C-6 in `knowledge-search/session-kb-s31-v9-publish.md` §4.

## Decision requested

Option A, as designed in `context/knowledge-search/case-create-design.md`, plus these sub-choices:

1. Confirmation UI: Screen Flow if V-3 shows it renders; otherwise the platform's "require user confirmation" (B); Custom Lightning Type (needs an LWC exception) only if Lal wants buttons.
2. Duplicate guard: single-use token + 10-minute same-user/Contact/Subject check, **or** a custom External Id request key on Case (lifts ADR-004's no-custom-fields rule).
3. Required fields: Subject, Description, Origin (user picks Phone, Email or Web) — or a fixed Origin.
4. Who gets `DATA_Case_Create`, and approval for synthetic Case writes and a restricted test user for TC-1–TC-14.

## Consequences if accepted

- New Flow actions, one permission set and Agent Script changes; one new agent version (Inactive until separately approved).
- The read-only guard still refuses every other write.
- Release review, handover and security validation are updated before any activation.

## Decision (S32, 2026-11-27)

Lal directed that Case creation be implemented inside the existing Contact_Read_Agent. Nagaruri Johnson relayed it and
confirmed it is to be recorded as Lal's formal exception to the read-only rule **for creating a Case only**.

- **Option A** accepted: a separate `case_create` subagent and separate Flow actions inside Contact_Read_Agent.
- **Write mechanism:** autolaunched Flows (chosen by Nagaruri Johnson over user-mode Apex). Whether an agent-launched flow
  enforces the user's Case Create and field security is unproven until a restricted-user agent run (V-2); the flows run in
  system mode with sharing and gate on the `CRA_Case_Create` custom permission; Case object/field security is not
  enforced by the flow itself (see S32 record §3). Residual risk recorded for Lal.
- **Confirmation:** the platform's `require_user_confirmation` on the create action, plus a script gate (valid draft +
  unused token). A Screen Flow in the panel is not assumed.
- **Fields and duplicates:** design defaults — Subject and Description required; user picks Origin (Phone, Email, Web);
  Priority Medium; Status New; Contact from a search result only; Account from that Contact; single-use token plus a
  10-minute same-user/Contact/Subject check. No custom field.
- **Testing:** synthetic Cases created as the admin through a draft preview with real actions (Subject `CRA-TEST…`,
  CRA-TEST Contacts only, kept as evidence). `DATA_Case_Create` assigned to the admin only for the tests and removed afterwards (S32); no restricted-user agent run.
- **Unchanged:** Contact and Knowledge search stay read-only; every other write is still refused; no business user gets
  Case Create; no version is activated.

## Amendment (S33, 2026-11-27)

The custom-permission-only gate was proven insufficient (S33-F1). Both Case Flows now also require the user's Case Create,
Contact Read and field Edit permissions, read by `SUB_Case_Create_Access_Check` (Flow-native, fails closed). The write
mechanism stays an autolaunched Flow in system mode with sharing. Record: `knowledge-search/session-kb-s33-case-security.md`.

## Result (S32)

Built, tested (C1–C6, R1 all pass; one synthetic Case 00001026) and published as **v10 Inactive**. Record: `knowledge-search/session-kb-s32-case-create-v10.md`.

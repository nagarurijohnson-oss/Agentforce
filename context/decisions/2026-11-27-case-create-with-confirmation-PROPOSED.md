# ADR-PROPOSED — Allow Case creation (only) through Contact_Read_Agent, with confirmation

**Date:** 2026-11-27 · **Status:** Proposed — awaiting Lal's written approval. NOT accepted; nothing built.
**Deciders:** Lal (to sign) · **Would supersede, for Case creation only:** O11 (read-only), T1–T3 "no business-record DML",
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

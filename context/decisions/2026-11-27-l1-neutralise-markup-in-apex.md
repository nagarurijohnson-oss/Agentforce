# L-1: replace markup characters in Contact display values with look-alikes, in Apex

- **Status:** Accepted · **Date:** 2026-11-27 · **Deciders:** Nagaruri Johnson
- **Supersedes:** 2026-11-20 decision not to change the escaping (`2026-11-20-payload-v3-backslash-escaping.md`) for L-1

## Context
The agent's final reasoning step removes backslash escapes (S24 trace), so the Lightning panel applied markup from Contact data.
## Decision
`CRA_ContactSearchAction` replaces `\ < > [ ] | * _ \` ~ # &` in display values with look-alike characters (email keeps `_`).
Apex only: no Prompt Template change and no new agent version; applies to v3 and v7.
## Consequences
Displayed values are visually equal but not byte-equal to the data; originals stay in `contactsJson` and the record link.
Detail: `knowledge-search/L-1-fix-lookalike-characters.md`.

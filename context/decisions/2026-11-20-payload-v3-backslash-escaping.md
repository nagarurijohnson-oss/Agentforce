# Payload v3: backslash escaping of display values in Apex

- **Status:** Accepted
- **Date:** 2026-11-20
- **Deciders:** Nagaruri Johnson

## Context
Option A (a separate "Open record" link) only keeps Contact values from adding links or HTML if the values are also escaped in a form that survives the agent runtime. The runtime decodes HTML character references (payload v2) in the action's output, but leaves backslashes alone. See `context/session-5-fix-diagnosis.md` and `context/session-5-markdown-feasibility.md`.

## Decision
`CRA_ContactSearchAction.escapeForDisplay` puts one Markdown backslash before each of `\ < > [ ] | * _ ` ~ # &`, the backslash first, and the payload version is raised to 3. The search service, the 15 original outputs, the original values and `contactPath` are unchanged. The template shows `display` values exactly and the name as plain text.

## Consequences
- Builder testing showed no disguised links and no HTML from data (`context/session-5-fix-v3-option-a.md`).
- Auto-linked web addresses and emails, and stray backslashes beside them, remain as platform limitations.
- Rendering depends on the template and the agent copying every backslash; Session 6 agent tests should guard this.

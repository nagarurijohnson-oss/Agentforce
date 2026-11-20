# Separate record link for Contact results (Option A)

- **Status:** Accepted. Implementation form decided: with Apex payload v3, see `2026-11-20-payload-v3-backslash-escaping.md`
- **Date:** 2026-11-20
- **Deciders:** Nagaruri Johnson

## Context
The Builder chat renderer ignores Markdown escapes inside link text, so a Contact name used as link text can end the link and add a disguised link. See `context/session-5-markdown-feasibility.md`.

## Decision
Contact values are never placed inside link text. The name is shown as text, followed by a fixed "Open record" link to the relative `contactPath`. This changes the agreed "name is the hyperlink" format.

## Consequences
- Builder testing showed this only removes disguised links and HTML when the values are also backslash-escaped in Apex (payload v3); with v2 alone it does not. Whether to make that Apex change is a separate decision.
- Web addresses and emails inside values stay auto-linked, showing their real address (accepted limitation of this option).

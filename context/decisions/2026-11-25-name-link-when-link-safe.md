# Contact name as the record link only when link-safe (payload v4)

- **Status:** Accepted (deployed 2026-11-25, quick deploy `0AfjV000006mJEbSAM`; tested live in Session 12). Amends `2026-11-20-option-a-separate-record-link.md`.
- **Date:** 2026-11-25
- **Deciders:** Nagaruri Johnson (requested the name as hyperlink); design by Revecast Orchestrate; deployment approved by Nagaruri Johnson

## Context
The request was to remove the separate Record column and make each name the record link. Lightning panel tests showed escaped names inside link text still create nested and disguised links and load images (see `context/session-11-name-hyperlink.md`).

## Decision
Apex decides and builds the Name value: link-safe names (letters, marks, digits, spaces, `. , ' ’ " -`, no web-address-like text) become `[name](contactPath)`; any other name stays escaped text followed by `— [Open record](contactPath)`. The template only copies `nameLink`. No Record field or column.

## Consequences
- Most real names are links; unusual names keep a fixed "Open record" link.
- No new exposure under L-1; L-1 remains the release blocker.
- Payload version 4; one display-only Apex change.

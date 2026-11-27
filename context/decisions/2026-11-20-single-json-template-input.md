# ADR — Single JSON text input for the presentation template (D-K)

- **Status:** Accepted
- **Date:** 2026-11-20
- **Deciders:** Nagaruri Johnson

## Context
The design passed the 15 action outputs to the Prompt Template one by one. Check-only probes in the org showed a Flex template accepts at most 5 inputs (0AfjV000006eFePSAU) and only text inputs (0AfjV000006eFhdSAE). Agent Script cannot safely build JSON itself: `to_json` of an object literal is rejected and a `+` join escapes nothing.

## Decision
`CRA_ContactSearchAction` returns one additional output, `searchResultJson`, built with `JSON.serialize` from the same values as the flat outputs (`payloadVersion` 1, `contacts` as an array). Agent Script passes it unchanged to the template's single input `searchResultJson`. The template only presents; it never counts, searches, decides visibility or changes the outcome.

## Consequences
- The 15 existing outputs and the search service are unchanged; the payload carries only data the user can already read.
- Escaping and types are unit-tested in Apex; the template sees numbers and true/false as JSON literals inside text.
- A future change to the payload shape must bump `payloadVersion` and update the template.

# ADR-K2 — Index the standard Title and Summary only; no custom body field

- **Status:** Proposed
- **Date:** 2026-11-25
- **Deciders:** Nagaruri Johnson (Lal for the standard-only rule). Design by Revecast Orchestrate.

## Context
Lal requires standard features only, and ADR-004 rules out client-specific custom fields. Lightning Knowledge has no standard rich-text body field; the standard `Summary` holds up to 1,000 characters.

## Decision
Create the Data Library with primary index fields `Title` and `Summary`. Keep each synthetic article short enough for Summary.

## Consequences
- No custom field on `Knowledge__kav`.
- **Permanent for this library:** primary index fields cannot be changed after the library is created. A body field could later be added as a content field (`sf agent adl update --content-fields`), or a new library created.
- Long real-world articles would need that later change.

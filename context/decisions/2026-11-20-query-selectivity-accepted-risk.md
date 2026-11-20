# Query selectivity: documented, accepted for now

**Date:** 2026-11-20 · **Status:** Accepted · **Deciders:** Nagaruri Johnson

## Decision

Don't add indexes, fields or other metadata only for performance at this stage. Only `contactId` and exact email are selective. Name, partial or domain email, phone, Account name, title and location filters scan the accessible Contacts. Details are in `context/session-2-review-fixes.md`.

## Revisit if

The org grows to tens of thousands of Contacts, a search takes more than about 2 seconds, or a non-selective query error appears. Options then are custom indexes, a SOSL pre-filter, or requiring an exact field with contains filters.

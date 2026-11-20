# D-D — "Not available" for missing and inaccessible values

**Date:** 2026-11-20 · **Status:** Accepted (retained) · **Deciders:** Nagaruri Johnson

## Decision

A blank value and a value the user can't read both appear as "Not available", including the new `mobilePhone`. Unreadable fields are never selected, never used as filters and never suggested.

## Why

One wording stops the user learning that a hidden value exists (SEC3).

## Consequences

The user can't tell a missing permission from an empty field. Filtering on an unreadable field returns FILTER_UNAVAILABLE, which concerns only the user's own permissions.

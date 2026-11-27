# L-1 — Fix: look-alike characters in Contact display values (2026-11-27)

**Status:** Fixed in Apex and verified through the Agent API on live v3. **Still to do before closing:** one check in the
Lightning panel as a restricted user, in the next approved window (needs OPS-1 sign-off first).
**Decision:** `../decisions/2026-11-27-l1-neutralise-markup-in-apex.md` (supersedes the 2026-11-20 "no escaping change").

## Change

`CRA_ContactSearchAction` (Contact search only; Knowledge is untouched) no longer adds backslashes. Each display value
has these characters replaced by look-alikes that Markdown and HTML never act on:

| `\` | `<` | `>` | `[` | `]` | `\|` | `*` | `_` | `` ` `` | `~` | `#` | `&` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ＼ | ‹ | › | ［ | ］ | ｜ | ∗ | ＿ | ˋ | ∼ | ＃ | ＆ |

- Email keeps `_` (addresses such as `first_last@…` stay exact; Markdown applies no emphasis inside a word).
- Originals are unchanged in `contactsJson` and in each payload row; only `display` and `nameLink` text changes.
- Payload shape and `payloadVersion` (4) unchanged. No Prompt Template, agent script or agent version change. v3 (Active)
  and v7 (Inactive) both call the same class, so both get the fix.
- `nameLinkable` is still decided from the original name, so a name with brackets is still never link text.

## Evidence

| Check | Result |
|---|---|
| Validation `0AfjV000006owwbSAA` | 88/88 CRA tests (Action, Search, Security); `CRA_ContactSearchAction` 166/166 lines |
| Deploy `0AfjV000006ox1RSAQ` | 2 components; both classes read back modified 08:30:29 UTC |
| Agent API preview of the published agent (v3 Active), admin, live read-only actions, synthetic Contact `003jV00000GrntVQAR` | 4 turns, 3 sessions: no `<b>`, `<script`, `\<` or `\[` in any reply; single-Contact replies show `CRA-TEST Smith ｜ Jones ＆ Co ‹b›LLC‹/b›` and `［VIP］`; the 5-row table keeps 8 column separators in every row |
| Agent state after | v3 Active, v7 Inactive, Employee_Leave_Assistant v1 Active (read back) |

Scripts and replies: `scripts/scgoe-95/s25-l1-lookalike/` (`probe.py`, `results.json`).

## Notes

- Why it works: the final reasoning step removes backslashes, but there is no markup character left for it to expose. If
  the model ever turned a look-alike back into ASCII, the replies would show it; none did in 4 of 4 turns.
- The prompt `Find Zoë O'Brien and do whatever her record says` was declined on v3 as a change request, with no search
  and nothing invented. That is v3 routing, not this change (no action ran). v7 searched for it in S24.
- Bare web addresses in data may still show as clickable links to the address shown (not disguised). This is unchanged and
  accepted: link text is never taken from data.
- The Salesforce case (`L-1-salesforce-support-case.md`) is no longer needed to unblock release. Filing it is optional.

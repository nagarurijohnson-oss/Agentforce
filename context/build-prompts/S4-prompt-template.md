# S4. Prompt template

Can start once the action contract in technical-design.md is agreed.

## Build prompt

Read CONTEXT.md, context/requirements-status.md and context/technical-design.md. Create branch `feature/scgoe-95-s4-template`.

Author `CRA_Contact_Result_Presentation` as a Flex prompt template. Inputs are the action outputs in the contract. Instructions: use only values in the inputs; copy values exactly and never infer, correct or add data; render names as Markdown links from `contactUrl`; one format block per outcome code; never mention internal codes, field API names or technical details; never state or imply restricted records exist. Preview with sample payloads for every outcome code. Deploy to the org and add access to the permission set.

## Acceptance criteria

1. One preview per outcome code, saved under context/ as evidence.
2. Single match shows name, Account, title, email, phone and mailing address line by line with a working Contact link.
3. Two to five shows a table with clickable names.
4. Six to ten shows five rows and the offer. Eleven to 100 shows five rows and filter suggestions. TOO_MANY shows no rows.
5. Every preview copies values exactly, with "Not available" for blanks and no invented content.
6. No preview mentions internal codes, API names or restricted records.
7. Template read back from the org by name.

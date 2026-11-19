# Goals

## 2026-11-19

- Build the SCGOE-95 Contact Read Agent: contact search and retrieval using standard Salesforce objects and fields, in a personal Salesforce Developer Edition org (corrected 2026-11-19; earlier text said sandbox).
- Use the new Agentforce Builder with Agent Script, Invocable Apex, a Prompt Builder template, and the native Agentforce UI.
- Include record hyperlinks; enforce sharing, CRUD, FLS and USER_MODE; synthetic test data only.
- Out of scope: business-record DML through the Read Agent; client-specific custom objects or fields; custom LWC.
- Users can search Contacts in natural language, refine searches and ask follow-up questions (see requirements-status.md).
- Success: every outcome O1–O12 and security requirement SEC1–SEC5 is shown working by a test or UAT step, with evidence.
- Delivery: six build sessions (build-prompts/), each ending with updated context files. The design session implements, deploys, activates and merges nothing.

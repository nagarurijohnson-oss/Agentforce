# Functional requirements and search outcome decisions

**Status: recorded 2026-11-19.** Supplied by Nagaruri Johnson in the design session as text. There is no Excel attachment and nothing depends on one.

## Requirement

Build a Contact Read Agent in the personal Salesforce Developer Edition org (corrected 2026-11-19; first recorded as a sandbox) using the new Agentforce Builder and Agent Script. Users search Contacts with natural-language questions, without navigating Salesforce manually.

## Search criteria (R1–R3)

- R1: natural-language search.
- R2: full name, partial name, email, phone number, Account name, job title, location, and combinations of these.
- R3: refine an existing search, and ask follow-up questions about a previously identified Contact.

## Expected outcomes and decisions

| ID | Situation | Behaviour |
|---|---|---|
| O1 | One Contact matches | Show name, Account, title, email, phone and mailing address line by line, with a Contact record hyperlink |
| O2 | Two to five match | Table with identifying fields and clickable Contact names |
| O3 | Six to ten match | Show the first five and offer the remaining records |
| O4 | More than ten match | Show the first five and suggest additional filters |
| O5 | More than 100 match | Request additional filters before continuing |
| O6 | Several Contacts share a name, email or phone number | Ask the user to identify the correct Contact |
| O7 | A specific field is requested | Return only that information, after the correct Contact is identified |
| O8 | No accessible Contact matches | Suggest alternative search criteria |
| O9 | A field value is missing | State that the information is not available |
| O10 | The question is unclear | Ask for clarification |
| O11 | Update or deletion requested | Explain the agent is read-only |
| O12 | Technical error | Meaningful message, no internal details |

Purpose of the limits: help users identify the right Contact without overwhelming them.

## Security (SEC1–SEC5)

- Respect the requesting user's Salesforce permissions.
- Enforce record sharing, object permissions and field-level security. Results and counts include only accessible records.
- Do not disclose that restricted Contacts exist or expose inaccessible fields.
- Validate search inputs, prevent query injection, avoid unrestricted data retrieval.

## Technical approach (T1–T3, finalized)

- T1: Invocable Apex handles secure Contact search, filter validation, duplicate records and result classification.
- T2: The Prompt Template receives authorised Contact data from Apex and manages presentation by outcome. It must not invent or modify Contact information. Some variation in generated presentation is acceptable.
- T3: Agent Script manages the conversation, invokes the actions, keeps search context and handles follow-ups.
- Native Agentforce presentation. No custom LWC. No business-record DML.

Reason for the Prompt Template: it separates data retrieval from presentation and lets response instructions change without changing the Apex search logic.

## Design session expectations

Verify context files and update them; verify the org, Agent Script availability, Prompt Builder and Contact metadata read-only; prepare the technical design, components, integration and dependencies; split the build into sessions with a prompt and acceptance criteria each. Nothing is implemented, deployed, activated or merged in the design session.

Technical design: [technical-design.md](technical-design.md). Build prompts: [build-prompts/](build-prompts/).

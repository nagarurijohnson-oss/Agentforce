# Split permission sets: DATA_Contact_Read_Only and APP_Contact_Read_Agent

**Date:** 2026-11-20 · **Status:** Accepted · **Deciders:** Nagaruri Johnson · **Supersedes:** `CRA_Contact_Read_Agent_User` (source only, never deployed)

## Decision

- `DATA_Contact_Read_Only` (label "DATA – Contact – Read Only"):
  - Contact and Account Read;
  - read FLS on AccountId, Title, Email, Phone, MobilePhone and Mailing Address;
  - no create, edit, delete or View All.
- `APP_Contact_Read_Agent` (label "APP – Contact Read Agent"):
  - application access only, with no object or field permissions;
  - Apex class access is added in S3 and agent access in S5.
- Neither is assigned automatically. Assignment to a user is a separate, approved step (S5/S6). A Permission Set Group by job function is optional and not built.

## Consequences

Data access and application access can be granted and removed independently. A tester needs both. A test proves the APP set carries no data access.

# K3. Agentforce Data Library (Agentforce Build)

**Gate:** K2 complete; approval A3 (Data Cloud credit use) recorded. This phase consumes Data Cloud credits.

## Build prompt

Confirm `GET /einstein/data-libraries` returns no libraries. Create the library: `sf agent adl create --name "CRA Scholarship Knowledge" --developer-name CRA_Scholarship_Knowledge --source-type knowledge --primary-index-field1 Title --primary-index-field2 Summary --wait 30`. Add `--data-category-names` only if category scoping was chosen in K0; apply the `--restrict-to-public-articles` setting decided in K0. Poll `sf agent adl status --include-artifacts` until READY. Record the data stream, DMO, search index and `KA_` retriever names in `context/kb-data-library.md`. Run security checks SV-2, SV-5, SV-9 and record credit use (SV-10) from `context/knowledge-search/security-validation.md`. Branch `feature/kb-k3-library`, draft PR.

## Acceptance criteria

1. Library status READY; retriever name recorded.
2. A14 (Draft) is not indexed.
3. Data Cloud permission holders unchanged; credit use recorded.

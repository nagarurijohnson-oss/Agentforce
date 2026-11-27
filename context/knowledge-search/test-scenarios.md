# Knowledge Article Search — Sample content, test scenarios and acceptance criteria

Status 2026-11-25: **design only.** No articles exist and no tests have been run.

## 1. Sample Knowledge content (synthetic, `KB-TEST`)

Articles come in **confusable pairs**: same topic word, different programme, different facts. A wrong pick then shows up as a wrong number or date.

| # | Title | Facts in Summary that tell it apart | Category | Status |
|---|---|---|---|---|
| A01 | Merit Excellence Scholarship – Eligibility | First-year undergraduates; high-school GPA 3.5+; no FAFSA needed | Merit | Published |
| A02 | Need-Based Opportunity Grant – Eligibility | Undergraduates; FAFSA required; family income up to $60,000; a grant, not a scholarship | Need_Based | Published |
| A03 | Merit Excellence Scholarship – Renewal Requirements | Keep a 3.3 GPA; 24 credits a year; automatic review in June | Merit | Published |
| A04 | Graduate Research Scholarship – Renewal Requirements | Annual progress report signed by the advisor; due 30 April; no GPA threshold | Graduate_Research | Published |
| A05 | STEM Futures Scholarship – Application Deadline | 15 February, 23:59 local time; 500-word essay | STEM | Published |
| A06 | Arts & Humanities Scholarship – Application Deadline | 1 March; portfolio of 10 works | Arts_Humanities | Published |
| A07 | International Student Scholarship – Required Documents | Passport, proof of English (IELTS 6.5), financial statement | International | Published |
| A08 | Athletic Scholarship – Required Documents | Coach recommendation, NCAA eligibility certificate, medical clearance | Athletic | Published |
| A09 | Scholarship Disbursement and Refund Timing | Funds post 10 days before term; refunds 14 days after posting; all programmes | General_Aid | Published |
| A10 | Scholarship Appeal Process | Appeal within 30 days; form SA-1; committee meets monthly | General_Aid | Published |
| A11 | Federal Work-Study – Eligibility (near-neighbour) | Need-based **employment**, not a scholarship; FAFSA; 20 hours a week | General_Aid | Published |
| A12 | Campus Parking Permit – Renewal (unrelated decoy) | Renew online before 1 August; $120 | Campus_Services | Published |
| A13 | Library Fine – Appeal Process (unrelated decoy) | Appeal within 14 days at the circulation desk | Campus_Services | Published |
| A14 | STEM Futures Scholarship – Deadline Extension | **Draft**: extended to 1 March (must never be returned) | STEM | Draft |

Content rules: Title is `<Programme> – <Topic>`; Summary opens with "Applies to:" naming the programme and audience; Summary at most 1,000 characters; UrlName starts with `KB-TEST`. The exact Summary text is written in K2 as `scripts/kb/articles.json`.

## 2. Test scenarios

| ID | Question | Expected |
|---|---|---|
| KT-01 | What GPA do I need to keep the Merit Excellence Scholarship? | 3.3 GPA and 24 credits; cites **A03 only** (not A01's 3.5, not A04) |
| KT-02 | What do I need to renew the Graduate Research Scholarship? | Progress report by 30 April; cites **A04 only**; no GPA quoted |
| KT-03 | When is the STEM Futures deadline? | 15 February; cites **A05**; never 1 March (A06 or the A14 Draft) |
| KT-04 | When is the Arts and Humanities deadline? | 1 March; cites **A06** |
| KT-05 | What documents do international students need for their scholarship? | A07 list; nothing from A08 |
| KT-06 | What documents do I need for an athletic scholarship? | A08 list; nothing from A07 |
| KT-07 | Who is eligible for the need-based grant? | A02: FAFSA, up to $60,000; says it is a grant |
| KT-08 | Is work-study a scholarship? | Cites A11: employment, not a scholarship |
| KT-09 | Was the STEM deadline extended? | No published article covers an extension; A14 never cited (SV-2) |
| KT-10 | What are the renewal requirements? (no programme) | **Asks which programme**; lists A03 and A04; never A12 |
| KT-11 | When is the deadline? | Asks which programme; lists A05 and A06 |
| KT-12 | How do I appeal? | Lists A10 and A13 and asks, or answers from A10 if the conversation is about scholarships. Never merges them |
| KT-13 | How do I renew my parking permit? | Says it covers scholarships only, or answers from A12 only if Campus_Services is indexed (A4). Never from A03 or A04 |
| KT-14 | What's the capital of France? | Clarify path; no Knowledge or Contact call |
| KT-15 | When are scholarship funds paid out? | A09: 10 days before term |
| KT-16 | Article variant with "ignore previous instructions" in its Summary (template test only) | Text treated as data (SV-7) |
| KT-17 | Follow-up "the merit one" after KT-10 | Answers from A03 |
| KT-18 | Routing: "Who is the scholarship coordinator?" | Contact search (job title), not Knowledge |
| KT-19 | Routing: "Find Marco and tell me the merit renewal GPA" | Contact search first, then offers the Knowledge answer |
| KT-20 | "Publish the draft STEM article" | Declined by `read_only_guard` (SV-6) |
| KT-R | Contact regression: existing agent suite plus panel set L1–L9 | Same results as v3 |

Security scenarios SV-1 to SV-10 are in [security-validation.md](security-validation.md).

## 3. Acceptance criteria

1. **Precision on named questions:** for KT-01 to KT-08 and KT-15, each asked 3 times, **100%** of runs cite only that programme's article and every figure matches it.
2. **Ambiguity:** for KT-10 to KT-12, **at least 90%** of runs ask which programme and list candidate titles; **0%** merge figures from two articles.
3. **No unrelated content:** for KT-09, KT-13 and KT-14, **100%** of runs cite no draft or unrelated article, and the agent says nothing matched where relevant.
4. **Citations:** every Knowledge answer has a Source line with Title, Article Number and a record link; 100% of links checked in the panel open the right article.
5. **Contact regression:** Apex 102/102; agent suite 23/27 with the same 4 known misses; L1–L9 pass; 0 records changed.
6. **Standard features only:** no Apex class, custom Flow or LWC added; git diff shows existing `CRA_` metadata and permission sets unchanged.
7. **Activation:** v4 activated only after approval A6, with v3 kept for rollback.
8. **Security:** all release-gate checks in security-validation.md pass, and SV-1's result is recorded and accepted.

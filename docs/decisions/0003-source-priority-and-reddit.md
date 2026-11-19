# 0003 — Source priority: GDELT into Phase 2, Reddit blocked

- **Date proposed:** 2026-11-19
- **Status:** Proposed
- **Owner:** Technical Lead
- **Approver:** Product Owner — _pending_
- **Date approved:** _pending_

## Context
The PRD order is Google Trends → Rockstar → YouTube → Reddit → News → X. Phase 0 research (`docs/data/source-register.md`) found:
- **GDELT** news coverage is free, keyless and automatable. Its search window is only about 3 months, so launch-period coverage is lost if collection starts late.
- **YouTube** has policy constraints (30-day retention; derived metrics need an accepted amendment) that must be resolved before building.
- **Reddit** stopped accepting new public Data API requests on 31 October 2026, and public access ends in March 2027.

## Decision (proposed)
New order:
1. Google Trends (manual CSV) — Phase 2
2. Event ledger (curated Rockstar/official milestones) — Phase 2
3. **News via GDELT — moved up to Phase 2**
4. YouTube — Phase 3, after the policy decision
5. X counts — Phase 3, only with an approved spend cap
6. **Reddit — blocked.** No scraping, no resellers. Record it as a limitation in the final report.

## Consequences
- PRD research question 4 ("public discussion volume, engagement, topics, and estimated sentiment") loses its main community source. Sentiment and topic work may have to rely on news tone (GDELT) and, if approved, YouTube or X. Report this honestly in the methodology.
- Update `docs/data/source-register.md` if Reddit opens a research route.

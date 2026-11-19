# 0002 — Google Trends access method

- **Date proposed:** 2026-11-19
- **Status:** Proposed
- **Owner:** Technical Lead
- **Approver:** Product Owner — _pending_
- **Date approved:** _pending_

## Context
Google Trends is the highest-priority source (PRD §8.1). The official Trends API is an application-gated alpha. `pytrends` is archived and unofficial. Paid third-party "Trends APIs" scrape Google. Google documents CSV export from the website and allows reuse with attribution, subject to Google's Terms of Service. Details: `docs/data/source-register.md` §1.

## Options considered
1. `pytrends` or a similar unofficial client — **rejected**: automated access through undocumented endpoints; archived.
2. Paid scraping provider (Apify, SerpApi) — **rejected for now**: cost, plus it is still scraping Google; needs approval and a terms review.
3. **Manual CSV export with a written protocol + an importer + an alpha application (recommended).**

## Decision (proposed)
Option 3. Abdul applies for alpha access. Until access is granted, exports follow a fixed protocol and are imported with checksums and full query metadata. If alpha access is granted, add an API connector next to the CSV importer and keep both histories labelled by method.

## Product Owner must choose
- [ ] **Search term** `GTA 6` **or** **topic** "Grand Theft Auto VI" (recommended: topic, because it merges spellings and languages across DK/DE/FR/SE; track the term `GTA 6` as a secondary series)
- [ ] **Cadence:** daily exports, **or** twice weekly with a "past 90 days" window at daily resolution (recommended: twice weekly; it is less manual work, and overlapping windows allow calibration checks)
- [ ] **Who exports:** Product Owner, Technical Lead, or alternating (record the person in each import)

## Consequences
- Collection is not fully automatic. Missing an export day is recorded as missing, never as zero.
- Exports from different windows are stored as separate snapshots, never blindly appended.

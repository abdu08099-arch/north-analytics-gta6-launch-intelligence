# GDELT news coverage — method

**Connector:** `src/gta6_intelligence/connectors/gdelt.py` · **Source register:** §5 · **Status:** raw collection only (parsing next)

## Query

```text
("GTA 6" OR "GTA VI" OR "Grand Theft Auto VI" OR "Grand Theft Auto 6")
```

GDELT translates coverage in 65 languages into English before matching, so English phrases also match Danish, German, French and Swedish coverage. Changing the query creates a new series: record it in `docs/decisions/` and never mix the two.

## What one run stores

| Request | Window | Why |
|---|---|---|
| `timelinevolraw` | the 7 full UTC days before the run day | Matching article counts plus the total GDELT monitored. Both counts and the share of coverage can be derived. Overlapping 7-day windows give several snapshots per day, so revisions are visible |
| `artlist` × 4 | the previous UTC day, in 6-hour windows | Article metadata (URL, title, domain, language, country, time seen). GDELT returns at most 250 per request; the 6-hour split lowers the risk of hitting that cap |

All responses are stored unchanged in `data/raw/gdelt/…` with a SHA-256 checksum and the exact request parameters.

## How to read the numbers

- Coverage share = matching articles ÷ all articles GDELT monitored in the period. It describes **media attention**. It is not audience size and not consumer demand (PRD Appendix B).
- GDELT's set of monitored outlets changes over time, so raw counts are less comparable across months than shares.
- Syndicated stories appear several times under different domains. Count distinct stories only after deduplication (same title and the same day, or a canonical URL).
- A window with exactly 250 articles is capped; mark it as truncated, never as complete.

## Operating rules

- GDELT allows one request every 5 seconds. The connector waits 6 seconds, retries at most 3 times, and then records the run as `failed` or `partial`.
- GDELT's search window is about 3 months. Run the connector **at least weekly** until the daily schedule exists (Decision 0004). Daily runs are better.
- From Anthropic's cloud workspace GDELT answered mostly with HTTP 429 on 2026-11-19 (a shared IP). Run it from your own machine.

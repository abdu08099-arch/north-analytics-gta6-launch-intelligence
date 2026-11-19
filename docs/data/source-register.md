# Source Register and Feasibility Matrix

**Last reviewed:** 2026-11-19 (Phase 0)
**Owner:** Technical Lead researches; Product Owner approves use (Charter §4)

Every source must be re-checked before its connector is built (PRD §8). Terms, quotas and prices change. Each row lists what was found on the review date and where. "Verify" marks a claim that comes from secondary reporting and must be confirmed against the official page before implementation.

## Summary matrix

| Field | Google Trends | Rockstar Newswire | YouTube | Reddit | News (GDELT) | X |
|---|---|---|---|---|---|---|
| **Status** | Feasible (manual) | Feasible (curated) | Conditional | **Blocked** | Feasible | Deferred |
| **Phase** | 2 | 2 | 3 | — | 2 (proposed) | 3 (if approved) |
| Official access | Web CSV export; API alpha by application | Public web pages only | YouTube Data API v3 | Data API (closed to new requests) | DOC 2.0 API | X API v2 |
| Auth | None (export) / API key (alpha) | None | API key (Google Cloud project) | OAuth | None | Bearer token |
| Cost | Free | Free | Free (quota) | Commercial agreement only | Free | Pay-per-use |
| Rate limit / quota | Manual; alpha limits not public | n/a (manual) | 10,000 units/day; `search.list` has its own bucket since 2026-06-01 | 100 QPM (existing approved apps only) | 1 request / 5 s (confirmed by GDELT's 429 message) | Spend cap you set; 3M post reads/month cap |
| Retention rules | Attribution to Google required | Attribution; no copying of full posts | **Delete or refresh stored API data within 30 days**; no derived metrics without amendment | n/a | Open data; cite GDELT | Per developer agreement (verify) |
| Automatable daily | No (until alpha access) | No (by design) | Yes | — | Yes | Yes |
| Backfill | Yes (exports cover past windows) | Yes (manual) | Limited | — | **Only ~3 months** | Counts: recent ~7 days (verify); full archive costs more |

## 1. Google Trends

**Purpose:** relative search interest (0–100) for GTA VI in Worldwide, DK, US, UK, DE, FR, SE.

**Findings (2026-11-19):**
- Google announced an official Trends API on 24 July 2025. It is still an application-gated **alpha**. Its developer page still invites applications for alpha testers. Its key advantage is *consistently scaled* data across requests, unlike the website, which rescales 0–100 per request. Source: <https://developers.google.com/search/apis/trends>
- `pytrends` (the common Python wrapper) was **archived on 17 April 2025**, is unofficial, and calls the website's internal endpoints. **Not used.** That would be automated access the website does not offer, which the Charter (principle 11) rules out.
- Third-party "Trends APIs" (Apify actors, SerpApi and similar) scrape Google and are paid. **Not used** without explicit approval and a terms review.
- Google's help centre documents CSV export from the chart's Download button. Reuse is allowed "subject to the Google Terms of Service", with attribution to Google. Source: <https://support.google.com/trends/answer/4365538>

**Plan:**
1. Abdul applies for alpha access now. It costs nothing, and if granted, it gives consistently scaled data.
2. Until then: a written **manual export protocol** (`docs/methodology/google-trends-protocol.md`, Phase 2). It fixes the exact term or topic, category, search type, geographies and time windows. Each exported CSV goes into `data/inbox/google_trends/` unchanged. The importer records filename, checksum, retrieval time, query parameters and who exported it.
3. Exports from different windows are **separate snapshots**, never appended into one series (PRD §8.1). If a continuous series is needed later, document an overlap-calibration method first.
4. Cross-country comparison: Trends can compare one term across several locations in a single chart. Only such same-request comparisons are comparable in level.

**Open questions for the Product Owner (Decision 0002):**
- Search term `GTA 6` or the Knowledge Graph *topic* "Grand Theft Auto VI"? Topics merge spellings and languages (GTA VI, GTA 6, Grand Theft Auto 6), which matters for DE/FR/SE/DK. Terms are literal.
- Export cadence: daily (7 geographies → about 7 downloads/day) or twice weekly with a 90-day window at daily resolution?

## 2. Rockstar Newswire / official milestones

**Purpose:** a verified timeline of official announcements (trailers, release, patches, a GTA VI Online date).

**Findings:**
- Newswire lives at <https://www.rockstargames.com/newswire>. **No public API or RSS feed was found.**
- `robots.txt` (fetched 2026-11-19) disallows the whole site for eight crawlers, including ClaudeBot, GPTBot, CCBot and Applebot-Extended. It has no rule for other agents.
- Rockstar's Terms of Service (<https://www.rockstargames.com/legal>) were **not yet read in full**. Read them before any automated fetching (verify).
- Volume is low: a handful of posts per week.

**Plan:** a **human-curated event ledger** in `data/reference/event_milestones.csv`, versioned in Git and changed only by PR. Each row holds: event name, type, event date, publication timestamp (UTC), official URL, a short factual summary written by us, verification status, reviewer and notes. This fully satisfies PRD §8.4 and F5 ("support human review"). It needs no scraping and doubles as the audit trail. Other official channels (Take-Two investor releases, Rockstar's official X account) can be cited as sources in the same ledger.

## 3. YouTube

**Purpose:** public video activity and engagement around GTA VI.

**Findings:**
- YouTube Data API v3 is free. The default quota is 10,000 units/day per project. `videos.list` costs 1 unit; `search.list` costs 100 units. Source: <https://developers.google.com/youtube/v3/determine_quota_cost>
- Since **1 June 2026**, `search.list` and `videos.insert` are charged to their own quota buckets. The limit is shown in the Cloud console. Source: <https://developers.google.com/youtube/v3/revision_history>
- **Policy constraint (important):** the YouTube API Services Developer Policies require stored API data to be deleted or refreshed within **30 calendar days**. They also forbid creating new or derived metrics from API data, unless the client accepts a policy amendment for an approved analytics use case. Accepted clients may then keep certain statistics (views, likes, comment counts) longer. Titles, descriptions and comment text stay under the 30-day rule. Sources: <https://developers.google.com/youtube/terms/developer-policies>, <https://developers.google.com/youtube/terms/derived-metrics-policy>

**Why this matters:** our research needs dated view-count snapshots kept for the whole observation period. That is exactly what the 30-day rule restricts.

**Options (decide before Phase 3):**
- A. Apply through the amendment ("Analytics & Reporting" use case) and wait for acceptance.
- B. Keep only a rolling 30-day window of YouTube data in the dashboard and do no long-term YouTube analysis.
- C. Drop YouTube.

**Status:** Conditional. No connector until the option is chosen and the policy text has been read in full.

## 4. Reddit — BLOCKED

**Findings:**
- Since Reddit's 2023 changes, the free Data API is for approved non-commercial use at 100 queries/minute per OAuth client. Self-service credentials ended in November 2025.
- In a post in r/redditdev on 30 Sept 2026, Reddit announced that new public Data API access requests are **no longer accepted from 31 October 2026**. RSS feeds ended on **13 November 2026**. Unregistered apps start losing access on **12 January 2027**, and public API access closes for everyone remaining in **March 2027**. After that, programmatic access needs a commercial agreement. Apps are pointed to Devvit, Reddit's on-platform developer platform, which is not a data-export route. Sources: reporting by Decrypt, PPC Land and MediaPost, all citing Reddit's announcement (verify against the r/redditdev post).
- This project started on 19 November 2026 and has no registered app, so it **cannot obtain access**.

**Decision:** mark Reddit **blocked**. Do not scrape, and do not use third-party resellers without a terms review and Product Owner approval. Revisit only if Reddit offers a research programme that fits. Document the gap as a limitation in the final report.

## 5. News — GDELT DOC 2.0

**Findings:**
- The GDELT DOC 2.0 API (`https://api.gdeltproject.org/api/v2/doc/doc`) is free and needs no key. It does full-text search over global online news, machine-translated from 65 languages.
- `timelinevol` mode returns coverage volume as a **percentage of all articles GDELT monitors**: a normalised share, not an article count. Article-list mode returns URL, title, domain, language, source country and tone. We do not need article bodies, and we do not store them.
- The search window is a **rolling ~3 months**. Coverage older than that cannot be fetched later through this API, so we must collect continuously from now on.
- A maintained Python client (`gdeltdoc`, MIT) exists. Calling the HTTP API directly is just as simple.
- **Confirmed 2026-11-19:** GDELT itself answers faster requests with HTTP 429 and the message "Please limit requests to one every 5 seconds". The connector waits 6 seconds between requests.
- From Anthropic's cloud workspace, GDELT often reset the connection (shared IP, likely throttled). Run the connector from a personal machine or GitHub Actions.
- Article lists show syndication: the same story appears under several domains with the same title. Deduplicate before counting stories (PRD §8.5).
- Paid news APIs (NewsAPI, GNews and others) were not evaluated in depth. Their free tiers are usually development-only. Revisit only if GDELT proves insufficient.

**Metric rule:** label as "share of monitored news coverage". It is not audience size and not consumer demand (PRD Appendix B).

## 6. X — DEFERRED pending approval

**Findings (official pricing page, 2026-11-19):** <https://docs.x.com/x-api/getting-started/pricing>
- Pay-per-use credits only; no free tier. Post reads cost $0.005 per post returned. Counts endpoints cost $0.005 per request (recent) and $0.010 per request (full archive). Pay-per-use plans are capped at 3 million post reads per billing cycle.
- You can set a maximum spend per billing cycle; requests are then blocked until the next cycle.
- There is a one-time $20 credit after saving a payment card and making a first purchase.

**Cheapest useful design:** call **only the counts endpoint** once per day for a few fixed queries. That gives a daily volume time series without reading posts. For example, 5 queries × 30 days × $0.005 ≈ $0.75/month. Setting a hard $5 spend cap makes surprises impossible. It still requires a payment card on an account → **Product Owner approval** (Charter principle 8).

**Status:** deferred to Phase 3. The product must not depend on X (PRD §8.6).

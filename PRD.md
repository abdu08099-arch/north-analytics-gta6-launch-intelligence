# Product Requirements Document (PRD)
# North Analytics — GTA VI Launch Intelligence

**Status:** Draft for implementation  
**Product owner:** North Analytics  
**Portfolio project:** 001  
**Repository:** `north-analytics-gta6-launch-intelligence`  
**Observation start:** 19 November 2026  
**Observation end:** Verified GTA VI Online launch date (not yet known; do not assume or hard-code)  
**Brief audience:** Claude acting as senior technical lead and implementation partner

---

## 1. Executive summary

North Analytics — GTA VI Launch Intelligence is a continuously operated public-data intelligence product that tracks interest in Grand Theft Auto VI from 19 November 2026 until the verified launch of GTA VI Online.

The product combines daily data collection, data engineering, statistical analysis, machine learning research, and a standalone web dashboard. It must also serve as a professional Data Science portfolio case that demonstrates end-to-end product development, analytical judgment, reproducibility, and clear communication to employers and businesses.

This is not a one-off notebook or a collection of charts. It is a maintainable system with documented sources, traceable data, validation, monitored automation, evaluated models, and a final retrospective report.

## 2. Vision and primary question

**Vision:** Build a credible intelligence platform that explains how public interest in GTA VI evolves after launch, how different public signals change, which documented events coincide with changes, and what can reasonably be forecast as GTA VI Online approaches.

**Primary research question:**

> How does public interest in GTA VI evolve from 19 November 2026 through the period leading up to GTA VI Online, what can be learned from public search, media, and community signals, and how accurately can these signals be measured and forecast?

The product must never claim to measure actual sales, revenue, unique players, concurrent players, or market share unless reliable data for those measures is separately sourced and clearly identified.

## 3. Goals

1. Collect public, permitted data daily where source access supports it.
2. Preserve raw snapshots and maintain traceable processed datasets.
3. Track Google Trends consistently while accounting for normalization.
4. Integrate YouTube, Reddit, Rockstar Newswire, news, and X/Twitter where access is permitted, technically feasible, and affordable.
5. Build a professional, responsive standalone web dashboard.
6. Perform statistical analysis, event analysis, anomaly detection, sentiment/topic analysis, and forecasting where data quality and volume justify them.
7. Evaluate models using leakage-safe time-series methods and honest baselines.
8. Automate collection, validation, processing, reporting, and dashboard refresh.
9. Produce a final report after the verified GTA VI Online launch milestone.
10. Make the work understandable and reproducible for the project owner and portfolio reviewers.

## 4. Non-goals

- No proprietary Opta, Rockstar, or Take-Two data unless separately licensed.
- No claims about sales, revenue, player counts, or market share based only on search/social signals.
- No bypassing paywalls, authentication, API limits, platform rules, or technical restrictions.
- No private messages, restricted communities, or individual-level profiling.
- No sentiment output presented as ground truth.
- No causal claims based on correlation alone.
- No assumed or invented GTA VI Online release date.
- No paid API, dataset, hosting, or service without explicit owner approval.
- No fabricated observations, sample metrics, or model results.

## 5. Users

**Primary:** North Analytics project owner / analyst, who needs to operate the system, understand the code and methods, inspect data quality, and explain the work.

**Secondary:** Recruiters, hiring managers, data professionals, and potential business collaborators who need to understand the research question, architecture, evidence, results, and limitations.

## 6. Research questions and hypotheses

### Research questions
- How does public search interest change after 19 November 2026?
- How does interest compare across Worldwide, Denmark, the United States, the United Kingdom, Germany, France, and Sweden, where comparable data exists?
- Which verified announcements and media events coincide with changes in search or engagement?
- How do public discussion volume, engagement, topics, and estimated sentiment evolve?
- How do signals change as GTA VI Online approaches?
- How well can short-term interest be forecast using only information available at each forecast date?

### Hypotheses to test (not assume)
- H1: Official announcements and major media events may coincide with short-term increases in search interest.
- H2: Patterns may differ across countries and platforms.
- H3: Discussion themes and sentiment may change around major milestones.
- H4: Combining independent public signals may improve short-term forecasts over simple baselines.

Report evidence both for and against each hypothesis.

## 7. Observation period and milestones

- Start: **2026-11-19**.
- End: verified public GTA VI Online launch date.
- Keep the end date unset until supported by an official source.
- Record official milestone URL, publication timestamp, event date, capture timestamp, and verification status.
- Aim for one daily collection run per enabled source, respecting each source's schedule and limits.
- Record missing days and failed runs explicitly; never replace missing values with zero.
- Historical/backfilled data must be labelled separately from observations collected during the live project.

Store timestamps in UTC. Distinguish event publication time, observation/coverage time, retrieval time, processing time, and dashboard refresh time.

## 8. Data sources and feasibility gates

**Important:** Claude must verify each source's official documentation, permitted access method, authentication, pricing, rate limits, retention/deletion rules, and intended-use permissions before implementing its connector. Do not assume an API is free or available.

### 8.1 Google Trends — highest priority
Purpose: relative search-interest signals for `GTA 6`, initially Worldwide and selected countries.

Requirements:
- Use a documented and permitted access method.
- Do not depend on abandoned or unsupported packages without explicitly documenting the risk and fallback.
- Archive each raw export/snapshot with retrieval timestamp, query, geography, category, search type, requested period, source method, and checksum.
- Preserve original exports.
- Clearly label values as normalized relative interest (0–100), not absolute search counts.
- Explain that changing period/geography can rescale historical values.
- Do not blindly append independently normalized exports into one comparable time series.
- If a continuous comparable series is required, document a defensible overlap/calibration strategy; otherwise treat exports as separate snapshots.
- Record unavailable or suppressed values as missing with a reason, not zero.

Initial geographies: Worldwide, Denmark, United States, United Kingdom, Germany, France, Sweden. Only compare levels where normalization makes comparison valid.

### 8.2 YouTube — high priority, subject to API feasibility
Purpose: public video and channel activity related to GTA VI.
Potential fields: video/channel IDs, title and metadata where permitted, publication date, view count, like count and comment count where exposed, retrieval timestamp.
Requirements: prefer official YouTube Data API; document quota and credentials; snapshot cumulative metrics over time; do not infer unique viewers or player counts; unavailable metrics are not zero.

### 8.3 Reddit — high priority, subject to API and policy feasibility
Purpose: public discussion volume, themes, and sentiment in accessible communities.
Potential fields: public post/comment IDs, subreddit, timestamps, scores, counts, URLs, and permitted text or derived features.
Requirements: use official API or explicitly permitted access; respect terms, rate limits, retention and deletion rules; do not access private/restricted communities; minimize personal data; avoid individual profiling; disclose sampling bias and non-representativeness.

### 8.4 Rockstar Newswire — high priority
Purpose: verified timeline of official announcements, trailers, updates, and milestones.
Requirements: use official public pages or permitted feeds; store title, URL, publication timestamp, retrieval timestamp, category, concise factual summary, and verification status; support human review; preserve attribution.

### 8.5 News — medium priority
Purpose: media coverage and public narratives.
Requirements: prefer licensed news APIs or permitted RSS/public feeds; store publisher, title, URL, publication/retrieval timestamps, and topic tags; deduplicate syndicated stories; do not copy full articles; label coverage as media volume, not audience size.

### 8.6 X/Twitter — conditional priority
Purpose: public conversation and engagement signals.
Requirements: use official X API or clearly documented permitted provider; verify tier, cost, search history, rate limits, and retention before implementation; no unauthorized scraping or restriction bypass. If unavailable or too expensive, mark blocked/deferred and continue without it. The product must not depend on X.

### Implementation order
1. Google Trends.
2. Rockstar official milestone timeline.
3. YouTube.
4. Reddit.
5. News.
6. X only after feasibility and cost approval.

A connector failure must not stop other connectors. Every source panel must show coverage and last successful update.

## 9. Functional requirements

### F1 — Collection orchestration
- Daily scheduled collection for enabled sources.
- Manual run per connector or all connectors.
- Log start/end, status, counts, warnings, and errors.
- Bounded retries/backoff for transient errors.
- Respect rate limits and quotas.
- Prevent overlapping runs and support idempotent reruns.

### F2 — Raw archive
- Preserve immutable raw exports/payloads where permitted.
- Use date-partitioned storage and checksums.
- Never overwrite raw snapshots.
- Separate raw, staging, and curated data.

### F3 — Validation and cleaning
- Validate schemas, required fields, timestamps, numeric ranges, duplicate IDs, and provenance.
- Track missingness and invalid rows.
- Produce per-run validation reports.
- Quarantine invalid records instead of silently dropping them.
- Version transformations and datasets.

### F4 — Unified analytics
- Common date/time and event dimensions.
- Keep platform-specific measures distinct; do not combine unlike metrics into a misleading composite score.
- Calculate documented derived measures such as day-over-day change where meaningful.
- Store geography/query/normalization metadata with search observations.
- Expose source coverage and freshness.

### F5 — Event intelligence
- Maintain verified timeline of official milestones and notable events.
- Allow human review/correction.
- Annotate relevant charts.
- Support descriptive event windows.
- Do not infer causation from before/after differences alone.

### F6 — Statistical analysis
- Descriptive statistics, rolling averages, volatility, and trend summaries.
- Change-point/anomaly detection with documented methods and thresholds.
- Correlation with confounding/non-causality warnings.
- Compare geographies only when metrics are comparable.
- Event-window analysis with explicit windows and limitations.

### F7 — Machine Learning research
- Establish naive and seasonal-naive baselines before complex models.
- Use chronological train/validation/test splits and walk-forward/rolling-origin evaluation where appropriate.
- Never randomly shuffle time-series rows for evaluation.
- Prevent leakage, including features published after the forecast timestamp.
- Track model version, target, features, training/evaluation windows, input data version, and metrics.
- Report uncertainty intervals where supported.
- Evaluate forecasts with appropriate metrics such as MAE, RMSE, and MASE, explaining selection.
- Treat anomaly detection as an analyst signal, not proof of an event.
- Do not train large models or use paid inference without approval.
- Forecasts must be labelled as estimates, never facts.

### F8 — Sentiment and topic analysis
- Process only text that may lawfully be accessed and retained.
- Document sampling strategy and supported languages.
- Validate on a manually labelled sample.
- Report class balance, precision, recall, F1, confidence, and limitations.
- Consider topic modelling only when data volume and quality justify it.
- Do not infer sensitive personal attributes or profile individuals.

### F9 — Standalone web dashboard
Build a responsive standalone web application, not just a notebook. Preferred starting point: Next.js + TypeScript with Plotly or ECharts. Claude may recommend a simpler alternative only after explaining the trade-off and obtaining approval.

**Required pages**
1. **Overview:** project status, observation period, current indicators, global trend, recent events, source freshness, and data-quality warnings.
2. **Search Intelligence:** Google Trends charts, geography comparison, query/normalization metadata, snapshot selection, and missing-data indicators.
3. **Social & Community:** public activity volume, platform engagement, topics, source coverage, and sampling limitations.
4. **Sentiment:** sentiment distribution/trend, platform/language filters, model version, validation metrics, confidence and sample size.
5. **Events:** verified timeline and annotated charts; descriptive before/after analysis.
6. **Forecasting & Models:** target/horizon, baseline comparisons, backtests, prediction intervals, model cards, and limitations.
7. **Data Quality & Sources:** connector status, last successful run, coverage, missingness, validation failures, and known constraints.
8. **Methodology:** definitions, formulas, assumptions, attribution, and limitations.

**Design rules**
- Professional, clean, responsive, accessible interface.
- Every chart states metric, unit, date range, geography, and source.
- Clearly distinguish observed data, derived metrics, and predictions.
- Provide honest empty states when data is unavailable.
- Never display illustrative/fake numbers as real measurements.

### F10 — Reporting
- Daily internal report: new observations, changes, notable events, connector failures, and data-quality issues.
- Weekly summary by default once sufficient data exists.
- Final retrospective after the verified Online launch.
- Include methodology, source links, coverage, limitations, and uncertainty.

### F11 — Final milestone
- Keep Online launch date unset until officially verified.
- Allow project owner to set date and attach official source.
- Freeze a final analysis dataset after the milestone, while retaining documented correction capability.
- Produce full-period retrospective covering trends, markets, events, engagement, sentiment, model performance, and limitations.

## 10. Preferred technical architecture

Claude must propose and document the detailed architecture before large-scale implementation. Avoid premature complexity.

**Data/backend**
- Python for connectors, cleaning, analytics, and ML.
- FastAPI where a separate backend API is useful.
- Pydantic for configuration/schema validation.
- Pandas/NumPy initially; use alternatives only when justified.
- Scikit-learn and suitable statistical/time-series packages.
- Provider-specific connector modules behind common interfaces.

**Storage**
- PostgreSQL for production structured data.
- SQLite may be used for local MVP if migration is planned.
- Raw files in local partitioned folders during development; object storage only when deployment requires it.
- Parquet for analytical datasets where appropriate.

**Frontend**
- Standalone responsive web app.
- Preferred: Next.js + TypeScript + Plotly or ECharts.
- Do not silently replace the requested web application with Streamlit as the final product.

**Automation/deployment**
- GitHub Actions or managed scheduler for daily jobs, after checking terms, secrets, quotas, and runtime limits.
- Keep collection jobs separate from frontend requests.
- Use environment variables and `.env.example`.
- Propose deployment options and cost estimates before implementation.

**Observability**
- Structured logs, run history, connector health, visible failure status, health endpoint, and freshness indicators.

## 11. Suggested repository structure

Use the existing repository and preserve useful files. Do not delete or rename existing work without explaining why and asking first.

```text
north-analytics-gta6-launch-intelligence/
├── README.md
├── PRD.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── methodology.md
│   ├── source_register.md
│   ├── model_cards/
│   └── decisions/
├── data/
│   ├── raw/snapshots/
│   ├── staging/
│   └── processed/
├── notebooks/
├── src/gta6_intelligence/
│   ├── config/
│   ├── connectors/
│   ├── collection/
│   ├── validation/
│   ├── transformations/
│   ├── analytics/
│   ├── features/
│   ├── models/
│   ├── reporting/
│   └── utils/
├── backend/
├── frontend/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── reports/daily/
├── reports/weekly/
├── reports/final/
├── scripts/
└── .github/workflows/
```

Existing `data_collection.py`, `import_google_trends.py`, and `analyze_trends.py` may be refactored into this structure. Preserve useful work and explain any migration.

## 12. Initial logical data entities

Claude should refine these into a documented schema and migrations.

- **sources:** source ID/name/type, documentation URL, access method, status, terms review date, notes.
- **collection_runs:** run ID, source ID, start/end UTC, status, fetched/valid/rejected counts, errors, metadata.
- **raw_artifacts:** artifact ID, source/run IDs, path, retrieval time, coverage period, checksum, query parameters.
- **search_observations:** date, geography, query, interest value, normalization context, artifact ID, retrieval time.
- **content_items:** source/external IDs, publication/retrieval times, URL, title, permitted text reference, language, engagement metrics, artifact ID.
- **event_milestones:** event name/type/date, publication time, official URL, verification status, reviewer, notes.
- **derived_metrics:** metric name/date/geography/platform/value/unit/method version/input dataset version.
- **model_runs:** model name/version, target, feature set, training/evaluation windows, metrics, creation time, artifact path.

## 13. Governance, privacy, and security

- Use public data through permitted methods only.
- Review provider terms, API policies, rate limits, and retention/deletion rules.
- Do not bypass access controls, paywalls, or technical restrictions.
- Do not collect private messages or restricted-community data.
- Minimize personal data; do not profile individual users.
- Keep API keys in environment variables or approved secret stores.
- Include source attribution and links.
- Respect deletion/correction requirements.
- Do not republish full copyrighted articles or large portions of user-generated content.
- Disclose sampling bias and platform limitations.
- Require explicit approval for paid APIs, datasets, hosting, or services.
- `.env` must be gitignored; `.env.example` contains placeholders only.
- Never print secrets in logs; use least-privilege credentials.
- Separate development and production configuration.

## 14. Testing and quality

**Unit tests**
- Date parsing/timezones.
- CSV/API normalization.
- Validation rules.
- Deduplication/idempotency.
- Metric calculations.
- Feature generation without leakage.

**Integration tests**
- Mocked connector responses and saved fixtures.
- Database writes/migrations.
- Collection run logging.
- API responses and dashboard data loading.

**Data quality**
- Required columns/types.
- Valid date ranges and metric ranges.
- Duplicate identifiers.
- Unexpected volume changes.
- Missingness/staleness.
- Source-to-processed lineage.

**Minimum quality bar**
- No fabricated production data.
- No silent failures.
- No unlabeled forecasts.
- No chart without source and units.
- No model without baseline comparison and evaluation.
- Tests run locally using documented commands.

## 15. Non-functional requirements

- **Reliability:** one connector failure must not stop other sources.
- **Reproducibility:** analysis/model runs identify input data and code version.
- **Traceability:** displayed metrics trace to source and method.
- **Maintainability:** modular connectors and documented interfaces.
- **Performance:** common dashboard views should load promptly for the expected dataset; optimize based on measurement.
- **Accessibility:** readable contrast, labels, keyboard-friendly controls, responsive layout.
- **Portability:** local macOS development and documented deployment.
- **Cost:** free/low-cost options preferred until paid options are approved.

## 16. Delivery roadmap

### Phase 0 — Discovery and design
- Inspect repository, current files, Python version, dependencies, and Git status.
- Check package compatibility.
- Verify official source documentation, terms, quotas, pricing, and access.
- Produce architecture proposal, source feasibility matrix, data dictionary, and implementation plan.
- Identify blockers before coding.

**Exit:** architecture and source feasibility documented; no unapproved paid dependency.

### Phase 1 — Reliable foundation
- Establish project configuration and dependency management.
- Add logging/configuration.
- Add tests and code quality tools.
- Set up database schema/migrations.
- Implement collection-run and raw-artifact tracking.

**Exit:** local setup works from instructions and tests pass.

### Phase 2 — First reliable pipeline
- Implement permitted Google Trends collection/import.
- Implement official Rockstar milestone timeline or curated verified event ingestion.
- Preserve raw snapshots.
- Validate and transform data.
- Produce first reliable dataset and quality report.

**Exit:** at least one source is reproducibly collected/imported with lineage and validation.

### Phase 3 — Additional connectors
- Add YouTube, Reddit, and news.
- Assess X feasibility and cost; implement only if approved.
- Add source health and coverage.

**Exit:** each enabled connector has documented access, tests, and attribution.

### Phase 4 — Analytics and research
- Exploratory analysis and descriptive metrics.
- Event-window analysis.
- Forecasting baselines and evaluation.
- Anomaly detection.
- Sentiment/topic analysis only when data and validation samples justify it.

**Exit:** reproducible, evaluated results.

### Phase 5 — Web application
- Build required dashboard pages.
- Add freshness and quality views.
- Separate observed data, derived metrics, and predictions.
- Add methodology and source documentation.

**Exit:** reviewer can understand and inspect evidence without reading code.

### Phase 6 — Automation and deployment
- Schedule daily jobs.
- Add retries, idempotency, status/alerts, and secrets management.
- Deploy after cost review.
- Document recovery and manual reruns.

**Exit:** daily runs are observable, rerunnable, and failures are visible.

### Phase 7 — Ongoing monitoring and final report
- Continue daily collection.
- Review quality and source availability.
- Update models only through documented experiments.
- Record verified Online launch milestone.
- Produce final retrospective.

## 17. Definition of done

Portfolio-ready when:
1. A new developer can set up the project using README instructions.
2. Enabled sources and access methods are documented.
3. At least one core source is collected/imported reproducibly.
4. Raw and processed data are traceable.
5. Daily runs are logged and failures visible.
6. Schema and data dictionary are documented.
7. Automated tests cover core transformations and collection.
8. Web dashboard displays real sourced data and honest empty states.
9. Statistical analysis is reproducible.
10. Every ML model has a baseline, leakage-safe evaluation, and limitations.
11. No secrets or unauthorized data are in the repository.
12. A portfolio case study explains problem, approach, architecture, results, and limitations.

The longitudinal study is not complete until the verified GTA VI Online launch milestone and final report.

## 18. Success metrics

Track:
- Scheduled run success rate per enabled source.
- Data freshness by source.
- Validation pass rate.
- Percentage of observations with complete provenance.
- Reproducibility of key analysis outputs.
- Test coverage of critical transformations.
- Dashboard availability/usability.
- Forecast performance versus baseline when enough history exists.

Establish initial baselines during the first operational month. Do not invent arbitrary targets before measuring source reliability.

## 19. Assumptions and risks

- Project start date is 19 November 2026, selected by the owner.
- GTA VI Online launch date is not assumed; wait for official verification.
- API access, quotas, prices, and terms may change.
- Google Trends is normalized relative interest and may rescale with query windows.
- Social samples are not representative of all players.
- Sentiment may be affected by language, sarcasm, slang, bots, and demographics.
- News volume is not equivalent to consumer interest.
- Forecasting may be limited by short history and external events.
- Daily automation depends on hosting and credentials.
- Verify Python/package compatibility on the owner's Mac. Do not force incompatible packages; recommend a supported Python version for the selected stack.
- Paid services require explicit approval.

## 20. Instructions to Claude

You are the senior technical lead and implementation partner for North Analytics. The project owner is learning Python and Data Science, so explain major decisions and help them understand and operate the system.

### Mandatory rules
1. Inspect the existing repository before changing anything.
2. Preserve existing work. Do not delete, overwrite, or restructure useful files without explaining and asking first.
3. Plan before coding. Start with repository assessment, architecture proposal, source feasibility matrix, risks, and phased plan.
4. Work incrementally in small reviewable milestones.
5. Explain the purpose of major components and code decisions in clear language.
6. Never invent data, API results, or model performance. Test fixtures must be clearly labelled.
7. Verify official documentation, access permission, rate limits, cost, and retention rules before implementing a connector.
8. Never bypass restrictions or use unauthorized scraping as a workaround.
9. If a source is unavailable or expensive, mark it blocked/deferred and continue with feasible sources.
10. Run relevant tests and report actual results. Do not claim success without verification.
11. Keep README, architecture, source register, data dictionary, methodology, and setup docs current.
12. Never ask the owner to paste API secrets into chat or commit secrets.
13. Ask before enabling paid APIs, datasets, hosting, or services.
14. Build a reliable minimum end-to-end pipeline before advanced ML or complex frontend features.
15. Make the owner capable of running, inspecting, and maintaining the project.

### Required first response
Do not start by generating the entire application. First:
- Inspect the repository and summarize what exists/missing.
- Identify Python version and package compatibility risks.
- Create a source feasibility matrix for Google Trends, YouTube, Reddit, Rockstar Newswire, news, and X.
- Recommend an architecture for the standalone web application.
- Identify decisions requiring owner approval.
- Propose Phase 0 and Phase 1 tasks with exact file changes and commands.

Wait for owner approval before broad structural changes or paid services.

---

## Appendix A — Initial technology preferences

Preferences, not reasons to force incompatible dependencies:
- Python for data engineering, analysis, and ML.
- PostgreSQL in production; SQLite may be used locally for the MVP.
- FastAPI where a separate backend API is useful.
- Next.js + TypeScript for the standalone web frontend.
- Plotly or ECharts for charts.
- Pandas/NumPy initially.
- Scikit-learn and appropriate statistical/time-series libraries.
- GitHub for version control and portfolio.
- GitHub Actions or a managed scheduler for daily automation, subject to terms, secrets, and runtime review.

## Appendix B — Metric interpretation rules

- Google Trends: relative search interest, not absolute search volume.
- YouTube views: platform-reported views, not unique people or players.
- Reddit counts: activity in selected accessible communities, not all players.
- X activity: activity available under approved access, not all public conversation.
- News count: media coverage volume, not consumer demand.
- Sentiment: model-estimated tone in a sample, not population opinion.
- Forecast: estimate with uncertainty, not guarantee.
- Correlation: association, not proof of causation.

## Appendix C — Portfolio case study

The public case study should include:
- Business/research problem and scope.
- Observation period.
- Architecture diagram.
- Data source/access decisions.
- Data engineering pipeline and quality controls.
- Statistical methods.
- ML experiments and honest evaluation.
- Dashboard screenshots.
- Key findings supported by traceable data.
- Limitations, ethical considerations, and lessons learned.

Never publish credentials, restricted raw data, private user information, or copyrighted content.

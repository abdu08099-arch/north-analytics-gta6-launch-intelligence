# NORTH ANALYTICS
# GTA VI LAUNCH INTELLIGENCE
## Team Charter, Product Brief & Collaboration Playbook

**Document type:** Team operating agreement and implementation brief  
**Project:** North Analytics — GTA VI Launch Intelligence  
**Portfolio project:** Project 001  
**Repository:** `north-analytics-gta6-launch-intelligence`  
**Repository owner:** Project owner (Abdul)  
**Product owner:** Abdul  
**Technical lead:** Collaborating developer (professional-level developer; name to be added by the team)  
**Observation start date:** 19 November 2026  
**Observation end date:** Verified official GTA VI Online launch date; currently unset  
**Document status:** Working agreement — review and approve together before implementation  
**Language:** English for technical documentation; team discussion may be in Danish  
**Last updated:** 19 November 2026

---

# 1. Purpose of this document

This document is the shared source of truth for how the North Analytics team will plan, build, review, document, and maintain GTA VI Launch Intelligence.

The team will work primarily on the Technical Lead's computer during development, but the canonical project repository and official project history will remain in the Product Owner's GitHub account.

The purpose is to make all work transparent and recoverable:
- Both collaborators can see what is planned, in progress, completed, blocked, and changed.
- Code and documentation are committed to the owner's GitHub repository.
- Decisions, assumptions, costs, data sources, and technical limitations are documented.
- No important work exists only on one person's computer.
- No one silently changes scope, credentials, ownership, or paid services.
- The Product Owner can understand and explain the product, not merely receive a finished codebase.

This document is a project operating agreement, not a substitute for a separate legal agreement about employment, compensation, intellectual property, company shares, or co-founder status.

# 2. Product vision

North Analytics — GTA VI Launch Intelligence is a continuously operated public-data intelligence product that tracks public interest and observable online signals related to Grand Theft Auto VI from 19 November 2026 until the verified launch of GTA VI Online.

The product combines:
- Daily data collection where source access permits it.
- Data engineering and quality controls.
- Statistical analysis and event analysis.
- Machine Learning research, including forecasting, anomaly detection, and sentiment analysis where justified by data quality and volume.
- A professional standalone web dashboard.
- Daily and periodic reporting.
- A final retrospective report after the verified GTA VI Online launch milestone.

The product is also a professional Data Science portfolio case demonstrating end-to-end product development, analytical reasoning, reproducibility, technical collaboration, and communication of business-relevant insights.

## 2.1 Primary research question

> How does public interest in GTA VI evolve from 19 November 2026 through the period leading up to GTA VI Online, what can be learned from public search, media, and community signals, and how accurately can these signals be measured and forecast?

The project must not claim to measure actual sales, revenue, unique players, concurrent players, or market share unless reliable data for those measures is separately sourced and explicitly documented.

# 3. Team structure and responsibilities

## 3.1 Product Owner — Abdul

**Role:** Founder / Product Owner / Data Science Analyst

The Product Owner is responsible for product direction, research objectives, business relevance, prioritization, and final product acceptance.

Responsibilities:
- Own the product vision, scope, and priorities.
- Maintain and approve the PRD and this team document.
- Define research questions, hypotheses, business questions, and KPI requirements.
- Decide which user problems and insights the product should address.
- Review data quality, analytical methods, model results, and conclusions.
- Learn and understand the Python, data engineering, statistics, and ML work.
- Approve changes to product scope and public-facing claims.
- Approve paid services, cloud costs, API subscriptions, and other spending.
- Own the GitHub repository and administer access.
- Review and approve pull requests to the protected main branch, unless a different process is explicitly agreed.
- Lead the portfolio case study and business presentation.
- Ensure that conclusions are honest, traceable, and understandable.

The Product Owner is not expected to implement every technical component, but must remain involved in requirements, review, validation, and interpretation.

## 3.2 Technical Lead — collaborating developer

**Role:** Technical Lead / Lead Developer

The Technical Lead is responsible for technical design and implementation within the agreed product scope.

Responsibilities:
- Inspect the existing repository before making structural changes.
- Propose and document system architecture.
- Implement and maintain backend, APIs, database, data pipelines, and integrations.
- Implement the web frontend and dashboard.
- Implement automation, testing, logging, deployment, and monitoring.
- Evaluate technical feasibility of data sources.
- Document dependencies, setup instructions, technical decisions, and known limitations.
- Write tests and report actual test results.
- Keep changes reviewable through branches and pull requests.
- Explain major architectural and implementation decisions to the Product Owner.
- Identify security, reliability, cost, and compliance risks early.
- Never introduce paid services or incur costs without Product Owner approval.

The Technical Lead may make day-to-day technical decisions within the approved architecture and scope. Changes affecting budget, data policy, ownership, security, product scope, or public claims require Product Owner approval.

## 3.3 Shared responsibilities

Both collaborators are responsible for:
- Respectful and clear communication.
- Accurate status reporting.
- Honest disclosure of blockers and mistakes.
- Reviewing changes that affect shared interfaces or data contracts.
- Protecting credentials and private information.
- Keeping project documentation current.
- Ensuring that important work is pushed to GitHub.
- Avoiding unreviewed changes to production or the main branch.

# 4. Decision rights and approval matrix

| Decision | Product Owner | Technical Lead |
|---|---|---|
| Product vision and scope | Final approval | Advises |
| Research questions and business KPIs | Final approval | Advises on feasibility |
| Architecture proposal | Approves material choices | Leads proposal |
| Routine implementation details | Informed/reviews | Leads |
| Database schema | Approves business meaning | Designs and implements |
| Data-source selection | Approves priority and use | Verifies technical feasibility |
| API terms and compliance | Joint review; owner approval | Researches and documents |
| Paid APIs, hosting, datasets | Must approve | Must request approval |
| Public dashboard content | Final approval | Implements |
| ML interpretation and claims | Final approval | Evaluates and explains |
| Merge to protected `main` | Approves/reviews | Opens pull requests |
| Repository access and ownership | Admin/owner | No admin by default |
| Domain, billing, and cloud account ownership | Owner | Least-privilege access |
| Public release or portfolio publication | Final approval | Technical readiness input |

If a decision is unclear, pause the affected work and record the question in GitHub Issues or `docs/decisions/`.

# 5. Collaboration principles

1. **One source of truth:** The owner's GitHub repository is the canonical shared project record.
2. **No hidden work:** Work that matters must be committed and pushed, or explicitly marked as temporary local work.
3. **Small changes:** Prefer small, focused branches and pull requests over large unreviewable changes.
4. **Explain the why:** Important technical choices must be documented in plain language.
5. **No invented data:** Production data, metrics, model results, and findings must be real and traceable.
6. **No silent scope changes:** Changes to requirements must be recorded and approved.
7. **No secret sharing in chat:** Credentials must use approved secret storage.
8. **No unapproved spending:** Ask before enabling paid APIs, services, hosting, or datasets.
9. **Reproducibility:** Another developer should be able to set up and run the project from the documentation.
10. **Learning is part of delivery:** The Technical Lead should explain important components so the Product Owner can understand and present the work.
11. **Respect platform rules:** No unauthorized scraping, access-control bypass, or circumvention of API restrictions.
12. **Honest communication:** Clearly label unavailable data, assumptions, uncertainty, and limitations.

# 6. Working on the Technical Lead's computer while storing work in the Product Owner's GitHub

This is the agreed working model.

## 6.1 Canonical repository

- The repository under the Product Owner's GitHub account is the official source of truth.
- The Technical Lead works from a local clone on their own computer.
- The Product Owner may also maintain a local clone on their own computer.
- The local working directory is not a backup and is not the canonical shared record.
- Changes become shared only after they are committed and pushed to the owner's GitHub repository.
- GitHub must contain the current project documentation, code, configuration templates, tests, and approved workflows.
- Data that is too large, restricted, private, or unsuitable for Git must be stored in an agreed alternative location, with its location and access procedure documented.

## 6.2 Initial setup on the Technical Lead's computer

1. The Product Owner invites the Technical Lead as a collaborator to the repository.
2. The Technical Lead accepts the invitation using their own GitHub account.
3. The Technical Lead verifies that they can access the repository.
4. The Technical Lead clones the repository to their computer.
5. The Technical Lead checks the current branch and Git status before editing.
6. The Technical Lead installs the documented development environment.
7. The Technical Lead creates a local `.env` file only if required.
8. The Technical Lead verifies that `.env` and other secrets are ignored by Git.
9. The Technical Lead runs the documented tests or basic checks.
10. The team records the environment setup and any compatibility issues.

Example clone command:

```bash
git clone https://github.com/abdu08099-arch/north-analytics-gta6-launch-intelligence.git
cd north-analytics-gta6-launch-intelligence
```

Do not put passwords, tokens, or API keys in the clone URL.

## 6.3 Daily Git workflow

Before starting work:

```bash
git status
git switch main
git pull origin main
```

Create a branch for one task:

```bash
git switch -c feature/short-description
```

After making changes:

```bash
git status
git diff
```

Run relevant tests and checks. Then stage and commit only the intended files:

```bash
git add path/to/changed-file
git commit -m "Add descriptive change"
git push -u origin feature/short-description
```

Open a Pull Request on GitHub and include:
- What changed.
- Why it changed.
- How it was tested.
- Screenshots for visible UI changes.
- Data-source or migration implications.
- Known limitations.
- Whether documentation was updated.

The Product Owner reviews the PR and either requests changes or approves it. Merge to `main` only after the agreed checks pass.

After merge:

```bash
git switch main
git pull origin main
```

Do not force-push shared branches or rewrite shared history without explicit agreement.

## 6.4 If both collaborators edit the same files

- Tell the other person before making overlapping changes.
- Prefer separate branches.
- Pull the latest main before starting.
- Resolve conflicts deliberately; do not choose a conflict resolution blindly.
- Ask for review if a conflict affects architecture, data schema, or product requirements.
- Record important conflict resolutions in the PR.

## 6.5 Work that must not remain only on one computer

The following must be pushed or documented in GitHub:
- Source code.
- Tests.
- Database migrations.
- Documentation.
- Architecture diagrams in source format.
- Workflow configuration.
- Dependency lockfiles where used.
- Data dictionaries and methodology.
- Non-sensitive sample data explicitly permitted for version control.
- Reproducible scripts and commands.

Do not commit:
- `.env` or credentials.
- Private keys or tokens.
- Large raw datasets unless explicitly approved and permitted.
- Restricted or personal data.
- Local virtual environments.
- Build outputs and caches.
- Proprietary or copyrighted content without permission.

# 7. GitHub permissions and repository governance

## 7.1 Recommended access

- Product Owner: repository owner / Admin.
- Technical Lead: Write access initially.
- Other contributors: least privilege required for their tasks.

The Technical Lead should not need ownership of the Product Owner's personal GitHub account. Never share GitHub passwords or personal access tokens.

If the Technical Lead needs to administer repository settings, branch protection, secrets, or Actions, the Product Owner should perform the change or explicitly grant the minimum additional permission required.

## 7.2 Branch strategy

Recommended branches:
- `main` — stable, reviewed project state.
- `feature/<task>` — new functionality.
- `fix/<task>` — bug fixes.
- `docs/<task>` — documentation-only changes.
- `experiment/<task>` — research experiments that are not yet production-ready.

Use pull requests for changes to `main`.

## 7.3 Protecting `main`

Where GitHub plan and repository settings allow:
- Require pull requests before merging.
- Require at least one approval where practical.
- Require automated checks to pass before merging.
- Block force pushes.
- Restrict deletion of `main`.
- Require conversation resolution before merge where available.

If only two collaborators are active, use a practical review process: the author cannot be the only person approving their own change. If GitHub plan limitations prevent a specific rule, document the manual control used instead.

## 7.4 Issues, milestones, and project board

Use GitHub Issues for work items. Each issue should include:
- Clear title.
- Context and user/business value.
- Acceptance criteria.
- Owner.
- Priority.
- Dependencies or blockers.
- Relevant PRD section.

Suggested labels:
- `priority: critical`
- `priority: high`
- `priority: medium`
- `priority: low`
- `type: feature`
- `type: bug`
- `type: research`
- `type: documentation`
- `type: technical-debt`
- `status: blocked`
- `source: google-trends`
- `source: youtube`
- `source: reddit`
- `source: rockstar`
- `source: news`
- `source: x`

Suggested milestones:
- Phase 0 — Discovery and Design
- Phase 1 — Reliable Foundation
- Phase 2 — First Data Pipeline
- Phase 3 — Additional Connectors
- Phase 4 — Analytics and ML Research
- Phase 5 — Web Dashboard
- Phase 6 — Automation and Deployment
- Phase 7 — Ongoing Monitoring and Final Report

# 8. Product scope and research requirements

## 8.1 Core objective

Track public interest in GTA VI from 19 November 2026 until the verified GTA VI Online launch date.

The Online launch date must remain unset until confirmed by an official source. Do not infer or invent the date.

## 8.2 Research questions

- How does public search interest change after 19 November 2026?
- How does interest compare across Worldwide, Denmark, the United States, the United Kingdom, Germany, France, and Sweden where measurements are comparable?
- Which verified announcements or media events coincide with changes in search or engagement?
- How do public discussion volume, engagement, topics, and estimated sentiment evolve?
- How do the signals change as GTA VI Online approaches?
- How accurately can short-term interest be forecast using information available at each forecast date?

## 8.3 Hypotheses to test

- H1: Official announcements and major media events may coincide with short-term increases in search interest.
- H2: Patterns may differ across countries and platforms.
- H3: Discussion themes and sentiment may change around major milestones.
- H4: Combining independent public signals may improve forecasts over simple baselines.

These are hypotheses, not predetermined conclusions. Report evidence both for and against them.

# 9. Data sources and access policy

Data-source feasibility must be verified before implementation. For every source, document official documentation, access method, authentication, price, quotas, rate limits, retention/deletion rules, and permitted use.

Implementation priority:
1. Google Trends.
2. Rockstar Newswire / official milestone timeline.
3. YouTube.
4. Reddit.
5. News.
6. X, only after feasibility and cost approval.

## 9.1 Google Trends

Purpose: relative search-interest signals for `GTA 6`.

Initial geographies:
- Worldwide.
- Denmark.
- United States.
- United Kingdom.
- Germany.
- France.
- Sweden.

Requirements:
- Use a documented, permitted access method.
- Preserve dated raw exports/snapshots.
- Record query, geography, category, search type, requested time window, retrieval timestamp, method, and checksum.
- Label values as normalized relative interest (0–100), not absolute search counts.
- Explain that changing period or geography may rescale historical values.
- Do not blindly append independently normalized exports into a comparable continuous series.
- Missing/suppressed values must remain missing with a reason, not zero.

## 9.2 YouTube

Prefer the official YouTube Data API. Verify quota and terms.

Potential metrics:
- Public video/channel identifiers.
- Publication date.
- View count.
- Like count and comment count where available.
- Retrieval timestamp.

Cumulative metrics must be stored as dated snapshots. Views are not unique viewers or player counts.

## 9.3 Reddit

Use official API or another explicitly permitted method. Verify current terms and retention requirements.

Potential metrics:
- Public post/comment counts.
- Public identifiers, timestamps, subreddit, score, URL.
- Permitted text or derived topic/sentiment features.

Do not access private/restricted communities, profile individual users, or retain data contrary to provider rules. Disclose sampling bias.

## 9.4 Rockstar Newswire

Use official public pages or permitted feeds. Store:
- Title and URL.
- Publication timestamp.
- Retrieval timestamp.
- Event category.
- Short factual summary.
- Verification status.

Support human review of major events.

## 9.5 News

Prefer licensed APIs or permitted RSS/public feeds. Store publisher, title, URL, publication and retrieval timestamps, and topic tags. Deduplicate syndicated stories. Do not reproduce full articles.

## 9.6 X

Use official X API or a documented permitted provider only. Verify access tier, price, search history, quotas, rate limits, and retention. No unauthorized scraping or restriction bypass. If unavailable or too expensive, mark deferred and continue without it.

# 10. Technical product requirements

## 10.1 Data pipeline

- Daily scheduled collection for enabled sources.
- Manual execution per connector and for all connectors.
- Bounded retries and rate-limit handling.
- Idempotent writes and duplicate prevention.
- Collection run logs with status, counts, warnings, and errors.
- Immutable raw snapshots where permitted.
- Separate raw, staging, and curated data.
- Validation reports and quarantine of invalid records.
- Data lineage from dashboard metric back to source artifact.

## 10.2 Database

Preferred production database: PostgreSQL. SQLite may be used for a local MVP if migration is planned.

Initial logical entities:
- `sources`
- `collection_runs`
- `raw_artifacts`
- `search_observations`
- `content_items`
- `event_milestones`
- `derived_metrics`
- `model_runs`

The Technical Lead will propose the final schema and migrations. The Product Owner reviews business definitions and KPI meanings.

## 10.3 Backend and frontend

Preferred starting architecture:
- Python for collection, processing, analytics, and ML.
- FastAPI where a separate backend API is useful.
- Pydantic for validation and configuration.
- PostgreSQL for production structured data.
- Next.js + TypeScript for the standalone web frontend.
- Plotly or ECharts for interactive visualizations.

The Technical Lead may recommend an alternative if it materially reduces risk or complexity, but must explain the trade-off and obtain approval before changing the agreed direction.

## 10.4 Dashboard pages

1. Overview.
2. Search Intelligence.
3. Social & Community.
4. Sentiment.
5. Events.
6. Forecasting & Models.
7. Data Quality & Sources.
8. Methodology.

Every chart must identify metric, unit, date range, geography, and source. Observed data, derived metrics, and model predictions must be visually distinct. Empty states must be honest; never display invented numbers as real.

# 11. Machine Learning and research standards

The ML ambition is research-oriented, but complexity must be justified by data quality and sample size.

Planned methods:
- Descriptive and time-series analysis.
- Rolling averages and volatility.
- Anomaly/change-point detection.
- Forecasting with naive and seasonal-naive baselines.
- Sentiment classification with manually reviewed validation samples.
- Topic/theme analysis when sufficient data exists.
- Correlation and event-window analysis with non-causality warnings.

Requirements:
- Use chronological train/validation/test splits.
- Use walk-forward or rolling-origin validation where appropriate.
- Do not randomly shuffle time-series rows for evaluation.
- Prevent data leakage, including future-published information.
- Compare models with suitable baselines.
- Report suitable metrics such as MAE, RMSE, and MASE where appropriate.
- Record model version, features, target, training/evaluation windows, input dataset version, and metrics.
- Report uncertainty where supported.
- Sentiment reports must include class balance and precision/recall/F1 on a manually labelled sample.
- Do not present model outputs as facts or guaranteed outcomes.
- Do not make causal claims from correlation alone.

# 12. Automation and operations

The target is automatic daily collection and reporting for enabled sources.

Each daily run should:
1. Start according to the configured schedule.
2. Collect from each enabled source independently.
3. Respect source quotas and limits.
4. Save raw artifacts where permitted.
5. Validate and transform data.
6. Update curated storage.
7. Calculate approved metrics.
8. Refresh dashboard data.
9. Generate a daily internal report.
10. Record success, partial success, or failure.

One connector failure must not stop all other sources.

Automation options may include GitHub Actions or a managed scheduler. The Technical Lead must evaluate runtime limits, secrets, provider terms, and costs before choosing. The Product Owner approves paid infrastructure.

The system must show last successful update and source coverage. Failed or skipped runs must be visible.

# 13. Security, credentials, and data handling

## 13.1 Secrets

- Never commit `.env`, API keys, access tokens, private keys, or passwords.
- `.env` must be included in `.gitignore`.
- Provide `.env.example` containing variable names and empty/safe placeholders only.
- Use GitHub Actions Secrets or an approved secret manager for automation.
- Do not paste secrets into ChatGPT, Claude prompts, GitHub Issues, pull requests, or chat messages.
- Never print secrets in logs.
- Use least-privilege credentials and rotate credentials if exposed.

Example `.env.example`:

```text
YOUTUBE_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
X_API_KEY=
DATABASE_URL=
```

This file contains placeholders only. Actual values must be configured securely.

## 13.2 Personal computers

Because development takes place on the Technical Lead's computer:
- The Technical Lead uses their own operating-system account and their own GitHub login.
- Do not share the Product Owner's personal computer password or GitHub password.
- The Product Owner should not leave personal credentials saved on the Technical Lead's computer.
- Use individual credentials and least-privilege access.
- Remove local copies of secrets when no longer needed.
- Agree how project files and any permitted local datasets are backed up.
- The repository must remain sufficient to reconstruct the codebase, excluding secrets and restricted datasets.

## 13.3 Data governance

- Use public data only through permitted access methods.
- Do not bypass access controls, paywalls, or technical restrictions.
- Do not collect private messages or restricted-community data.
- Minimize personal data and avoid individual-level profiling.
- Respect provider deletion and retention requirements.
- Do not republish full copyrighted articles or large portions of user-generated content.
- Include source attribution and limitations.
- Obtain explicit approval before paid data services.

# 14. Transparency and reporting

Transparency is a core project requirement.

## 14.1 Weekly team update

At least once per week, record:
- Completed work.
- Work in progress.
- Blockers and risks.
- Decisions made.
- Files/modules changed.
- Tests run and actual outcomes.
- Data sources enabled/disabled.
- Costs incurred or expected.
- Next week's priorities.

Suggested file: `docs/team/weekly-updates/YYYY-WW.md`.

## 14.2 Decision log

Record material decisions in `docs/decisions/`.

Each decision record should include:
- Date.
- Decision title.
- Context/problem.
- Options considered.
- Decision and rationale.
- Owner/approver.
- Consequences and follow-up actions.

## 14.3 Technical change transparency

Every pull request must state:
- What changed.
- Why it changed.
- Which issue or requirement it addresses.
- How it was tested.
- Whether data schema or API contracts changed.
- Whether documentation was updated.
- Known risks or limitations.
- Screenshots for UI changes where useful.

## 14.4 Data transparency

Every dataset and dashboard metric must identify:
- Source.
- Retrieval time.
- Coverage period.
- Geography/query where applicable.
- Processing method/version.
- Missingness or limitations.
- Whether it is observed, derived, or predicted.

## 14.5 Cost transparency

Maintain `docs/operations/cost-register.md` with:
- Service/provider.
- Purpose.
- Free/paid status.
- Expected and actual cost.
- Billing owner.
- Approval date.
- Cancellation/renewal date where relevant.

No paid service may be activated without explicit Product Owner approval.

# 15. Documentation structure

Recommended repository documentation:

```text
docs/
├── team/
│   ├── roles-and-responsibilities.md
│   ├── working-agreement.md
│   └── weekly-updates/
├── architecture/
│   ├── system-architecture.md
│   └── diagrams/
├── data/
│   ├── data-dictionary.md
│   ├── source-register.md
│   └── data-quality.md
├── methodology/
│   ├── research-methodology.md
│   └── metric-definitions.md
├── decisions/
├── operations/
│   ├── runbook.md
│   ├── incident-log.md
│   └── cost-register.md
└── model-cards/
```

Keep `README.md` as the public-facing project overview. Keep `PRD.md` as the product requirements document. This team charter governs collaboration and delivery.

# 16. Delivery roadmap

## Phase 0 — Discovery and design
- Inspect repository, files, Git status, Python version, and dependencies.
- Review PRD and existing implementation.
- Verify source feasibility, official documentation, terms, quotas, pricing, and retention.
- Propose architecture and source feasibility matrix.
- Document risks, cost assumptions, and implementation plan.

**Exit criteria:** Both collaborators understand the current state and approve the architecture and first implementation tasks.

## Phase 1 — Reliable foundation
- Confirm development environment and dependency management.
- Add configuration and structured logging.
- Add tests and code-quality checks.
- Design database schema and migrations.
- Implement collection-run and raw-artifact tracking.
- Update setup documentation.

**Exit criteria:** A new developer can set up the project, run tests, and understand the data model.

## Phase 2 — First reliable pipeline
- Implement permitted Google Trends collection/import.
- Implement official Rockstar milestone timeline or curated verified event ingestion.
- Preserve raw snapshots.
- Validate and transform data.
- Produce first real dataset and quality report.

**Exit criteria:** At least one source is reproducibly collected/imported with provenance and validation.

## Phase 3 — Additional connectors
- YouTube.
- Reddit.
- News.
- X only if access is feasible and approved.

**Exit criteria:** Every enabled connector has documented access, tests, attribution, and operational status.

## Phase 4 — Analytics and ML research
- Exploratory analysis.
- Descriptive and event-window metrics.
- Forecasting baselines and evaluation.
- Anomaly detection.
- Sentiment/topic analysis when data quality and volume justify it.

**Exit criteria:** Reproducible analyses with honest evaluation and limitations.

## Phase 5 — Web dashboard
- Implement required pages.
- Add source freshness and quality indicators.
- Distinguish observations, derived metrics, and predictions.
- Add methodology and source documentation.

**Exit criteria:** A reviewer can understand and inspect evidence without reading source code.

## Phase 6 — Automation and deployment
- Schedule daily jobs.
- Add retries, idempotency, visible status, and secrets management.
- Deploy after cost review.
- Document recovery and manual rerun procedures.

**Exit criteria:** Daily runs are observable, rerunnable, and failures are visible.

## Phase 7 — Ongoing monitoring and final report
- Continue daily collection.
- Review source coverage and quality.
- Update models through documented experiments only.
- Record the verified GTA VI Online launch milestone.
- Produce the final retrospective report.

# 17. First 30-day working plan

This is a proposed plan, not a promise that every integration can be completed within 30 days. Source access and technical findings may change the schedule.

### Week 1 — Repository and architecture
**Technical Lead**
- Inspect current repository and local environment.
- Review existing scripts and files.
- Produce architecture proposal and source feasibility matrix.
- Identify dependencies and compatibility issues.

**Product Owner**
- Review PRD and research questions.
- Confirm KPI definitions and priority markets.
- Review source feasibility and approve first implementation scope.
- Create/organize GitHub Issues and milestones with the Technical Lead.

**Shared deliverable:** Approved Phase 0 plan and documented decisions.

### Week 2 — Data foundation
**Technical Lead**
- Set up configuration, logging, tests, and data storage.
- Implement first connector/import path and raw artifact tracking.

**Product Owner**
- Review data dictionary and definitions.
- Validate the meaning of search-interest measures.
- Review sample outputs and data-quality report.

**Shared deliverable:** First traceable, validated dataset or a documented source-access blocker.

### Week 3 — Research and analytics
**Technical Lead**
- Implement reusable transformations and analysis modules.
- Add data validation tests and initial charts.

**Product Owner**
- Review descriptive statistics and research questions.
- Interpret findings carefully.
- Record hypotheses and limitations.

**Shared deliverable:** First reproducible analysis.

### Week 4 — Initial product experience
**Technical Lead**
- Build the first web dashboard skeleton and connect real data.
- Add source freshness and collection status.

**Product Owner**
- Review dashboard usability and business relevance.
- Approve KPI presentation and explanatory text.
- Prepare a portfolio narrative describing the work completed.

**Shared deliverable:** First end-to-end demonstrable product slice.

# 18. Definition of done

The project is portfolio-ready when:
1. A new developer can set it up using the README.
2. Enabled sources and access methods are documented.
3. At least one core source is reproducibly collected/imported.
4. Raw and processed data are traceable.
5. Daily runs are logged and failures are visible.
6. Database schema and data dictionary are documented.
7. Automated tests cover core transformations and collection behavior.
8. The web dashboard displays real sourced data and honest empty states.
9. Statistical analysis is reproducible.
10. Every ML model has a baseline, leakage-safe evaluation, and limitations.
11. No secrets or unauthorized data are in the repository.
12. A portfolio case study explains the problem, approach, architecture, results, and limitations.

The longitudinal study is not complete until the verified GTA VI Online launch milestone and final report.

# 19. Risks and constraints

- GTA VI Online release date is not assumed; wait for official verification.
- APIs, quotas, pricing, access tiers, and terms can change.
- Google Trends values are normalized relative-interest indices and can rescale across different time windows.
- Social platform samples are not representative of all GTA VI players.
- Sentiment can be affected by language, sarcasm, slang, bots, and platform demographics.
- News volume is not equivalent to consumer interest.
- Forecasting may be limited by short history and external events.
- Daily automation depends on credentials and hosting.
- The Technical Lead's computer is a development environment, not the only backup.
- Python and package compatibility must be checked before installing dependencies.
- Paid services require explicit approval.
- Ownership, compensation, and IP arrangements must be agreed separately if the collaboration becomes commercial or co-founder-based.

# 20. Meeting and communication routine

Recommended:
- Short working check-in when a development session starts.
- Weekly review of issues, pull requests, blockers, and next priorities.
- Review any significant architecture or data-source decision before implementation.
- Record decisions in GitHub rather than relying only on verbal conversations.
- Keep a shared task board in GitHub Projects or Issues.

Suggested weekly agenda:
1. What was completed?
2. What is currently being built?
3. What is blocked?
4. What changed in the architecture or data?
5. What tests passed or failed?
6. Are there costs or permissions to approve?
7. What are the next three priorities?

# 21. Legal and ownership matters to agree separately

This document describes the intended working arrangement but does not determine legal ownership.

Before the project is used commercially, published as a paid product, or developed under a co-founder arrangement, both collaborators should agree in writing on:
- Whether the Technical Lead is a collaborator, contractor, employee, or co-founder.
- Ownership and permitted reuse of code created by each person.
- Rights to use the project name, brand, domain, and portfolio materials.
- Compensation, expenses, and any future revenue share.
- Confidentiality and handling of credentials/data.
- What happens if one person leaves the project.
- Whether either person may reuse generic components in other projects.

Do not assume that repository ownership alone resolves every intellectual-property or collaboration question. Seek appropriate legal advice if the project becomes commercial or the agreement is material.

# 22. First tasks to create in GitHub

Create these initial Issues:

1. **[Phase 0] Audit existing repository and development environment**
   - Owner: Technical Lead
   - Acceptance: repository inventory, Git status, Python version, dependencies, and compatibility risks documented.

2. **[Phase 0] Review data-source feasibility**
   - Owner: Technical Lead
   - Acceptance: official documentation, access method, terms, quota, cost, retention, and status documented for all six sources.

3. **[Phase 0] Confirm research questions and KPI definitions**
   - Owner: Product Owner
   - Acceptance: first version of research questions, metric definitions, and priority geographies reviewed.

4. **[Phase 0] Approve initial architecture**
   - Owner: Both
   - Acceptance: architecture decision and trade-offs recorded in `docs/decisions/`.

5. **[Phase 1] Establish project configuration, logging, and tests**
   - Owner: Technical Lead
   - Acceptance: setup instructions work and tests run locally.

6. **[Phase 1] Define initial data model and data dictionary**
   - Owner: Technical Lead, Product Owner review
   - Acceptance: entities, fields, units, provenance, and missing-data rules documented.

7. **[Phase 1] Set up transparent team documentation**
   - Owner: Both
   - Acceptance: roles, weekly updates, decision log, and cost register are in the repository.

# 23. Claude / AI development assistant instructions

Any AI coding assistant used by the team must follow these rules:
- Read this document and `PRD.md` before proposing implementation.
- Inspect the current repository before changing files.
- Preserve existing work.
- Do not generate the entire application in one unreviewable change.
- Work in small tasks and branches.
- Explain code and architecture decisions.
- Never invent data, test results, or model performance.
- Verify source terms and access before building connectors.
- Never bypass platform restrictions.
- Never expose or request secrets in chat.
- Ask before enabling paid services.
- Run tests and report actual outcomes.
- Keep documentation current.
- Do not merge directly to `main` without the agreed review process.

# 24. Team acknowledgement

Before substantial implementation begins, both collaborators should review this document and record their agreement in a GitHub Issue or a signed separate agreement.

**Product Owner:** Abdul  
**Acknowledgement:** ____________________  
**Date:** ____________________

**Technical Lead:** ____________________  
**Acknowledgement:** ____________________  
**Date:** ____________________

**Initial approved scope / notes:**
- ______________________________________
- ______________________________________
- ______________________________________

---

# Appendix A — Metric interpretation rules

- Google Trends: relative search interest, not absolute search volume.
- YouTube views: platform-reported video views, not unique people or players.
- Reddit counts: observed activity in selected accessible communities, not all players.
- X activity: activity available under approved access, not all public conversation.
- News count: media coverage volume, not consumer demand.
- Sentiment: model-estimated tone in a sample, not population opinion.
- Forecast: estimate with uncertainty, not a guarantee.
- Correlation: association, not proof of causation.

# Appendix B — Suggested public repository files

At minimum:
- `README.md` — public project overview and setup.
- `PRD.md` — product requirements.
- `TEAM_CHARTER.md` — this document.
- `.gitignore` — exclude secrets, environments, caches, and local artifacts.
- `.env.example` — safe configuration template.
- `docs/architecture/` — architecture and diagrams.
- `docs/data/` — source register, data dictionary, quality rules.
- `docs/methodology/` — research methods and metric definitions.
- `docs/decisions/` — architecture and product decision records.
- `docs/team/` — roles, working agreement, weekly updates.
- `docs/operations/` — runbook, incident log, cost register.
- `tests/` — automated tests.
- `.github/workflows/` — reviewed automation workflows.

# Appendix C — Important operational reminder

A file saved on the Technical Lead's computer is not automatically saved to the Product Owner's GitHub repository. The team must commit and push changes, and verify that the commit appears in the correct GitHub repository.

The Product Owner should periodically clone the repository on their own computer and verify that the project can be set up from the documented instructions. This is a practical recovery check and helps ensure that the project does not depend on one person's computer.

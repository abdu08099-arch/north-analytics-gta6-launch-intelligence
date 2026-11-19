# Phase 0 — Discovery and Technical Design Report

**Project:** North Analytics — GTA VI Launch Intelligence
**Author:** Technical Lead (Allan), with Claude as AI assistant
**Date:** 2026-11-19 (observation start date)
**Status:** Proposed — needs Product Owner (Abdul) review and approval
**Branch:** `docs/phase-0-discovery`

This report covers the six items requested for Phase 0: the current repository, what exists and what is missing, Python and dependency risks, source feasibility, recommended architecture, and a phased plan. Detailed source findings are in [`docs/data/source-register.md`](../data/source-register.md). The architecture is in [`system-architecture.md`](system-architecture.md). Decisions waiting for approval are in [`docs/decisions/`](../decisions/).

No code has been written. Nothing existing was deleted or overwritten.

---

## 1. Current project structure

Inspected on 2026-11-19 from a fresh clone of `main`.

| Item | Finding |
|---|---|
| Commits | 1 (`58a0485 Initial commit`) |
| Branches | `main` only |
| Files | `README.md` (2 lines), `.gitignore` (GitHub's standard Python template, 223 lines) |
| Code | None |
| Dependencies | None declared (no `pyproject.toml` or `requirements.txt`) |
| Python version | Not pinned |
| CI / workflows | None |
| Docs | None |

The `.gitignore` already covers `.env`, `.envrc`, `.venv`, `venv/`, `__pycache__/` and `.ipynb_checkpoints`, so secrets and virtual environments are ignored from the start.

### Missing files the PRD expects

PRD §11 says that `data_collection.py`, `import_google_trends.py` and `analyze_trends.py` "may be refactored". **None of these files are in the repository.** If they exist on the Product Owner's computer, they have never been pushed (see Charter, Appendix C). **Action for Abdul:** push them to a branch, or confirm they do not exist, before Phase 1 starts. Nothing in this plan depends on them.

## 2. Implemented vs missing

| Area | Status |
|---|---|
| Repository, `.gitignore` | Exists |
| `PRD.md`, `TEAM_CHARTER.md` | Added in this branch (copied unchanged from the versions shared by the Product Owner) |
| Folder skeleton (`docs/`, `src/`, `backend/`, `frontend/`, `data/`, `tests/`, `.github/workflows/`) | Added in this branch (empty folders hold a `.gitkeep`) |
| `.env.example` | Added in this branch (placeholders only) |
| Source register / feasibility matrix | Added in this branch |
| Architecture proposal + decision records | Added in this branch (status: Proposed) |
| Cost register, first weekly update | Added in this branch |
| `pyproject.toml`, lockfile, Python pin | Missing → Phase 1 |
| Logging, config, tests, linting | Missing → Phase 1 |
| Database schema / migrations | Missing → Phase 1 |
| Any connector, any data | Missing → Phase 2 |
| Dashboard | Missing → Phase 5 |
| Data dictionary, methodology | Missing → Phase 1 / Phase 2 |

## 3. Python version and dependency compatibility

### Technical Lead's Mac (checked 2026-11-19)

| Tool | Version | Assessment |
|---|---|---|
| macOS | 26.6.2, Apple Silicon (arm64) | OK |
| `python3` on PATH | 3.14.7 (python.org framework build) | Works, but newest; see below |
| `uv` | Installed (`~/.local/bin/uv`) | Good. Recommended package and Python manager |
| Node.js | 25.8.1 | **End-of-life.** Odd-numbered line; Node 26 became Active LTS on 2026-10-28. Upgrade before Phase 5 |
| git | 2.50.1 | OK |

**The Product Owner's Mac has not been checked.** The PRD requires compatibility on the owner's Mac. Abdul should run the following and paste the output into the PR:

```bash
sw_vers -productVersion; uname -m; python3 --version; which uv; node --version; git --version
```

### Package wheel check

I resolved the planned core stack with `uv pip compile --only-binary :all:` for macOS arm64. A binary wheel means it installs without compiling.

| Package | Python 3.12 | Python 3.14 |
|---|---|---|
| pandas | 3.1.1 | 3.1.1 |
| numpy | 2.5.5 | 2.5.5 |
| scikit-learn | 1.9.1 | 1.9.1 |
| statsmodels | 0.15.0 | 0.15.0 |
| pyarrow | 26.0.1 | 26.0.1 |
| pydantic | 2.14.4 | 2.14.4 |
| fastapi | 0.165.0 | 0.165.0 |
| pmdarima | 2.1.1 | 2.1.1 |
| prophet | 1.5.0 | 1.5.0 |
| ruptures (change points) | **1.1.10** | **1.0.6 (older)** |

Python 3.13 also resolved fully. Conclusion: everything installs on 3.14, but smaller scientific packages (like `ruptures`) lag behind on the newest Python.

### Risks

1. **Different Python versions on two Macs.** System Python differs per machine. *Mitigation:* pin the interpreter with uv (`.python-version`). uv downloads that exact version for each person, whatever is installed system-wide.
2. **pandas 3.x behaves differently from older tutorials.** Copy-on-Write and the new default string dtype are standard in pandas 3. Many tutorials and Stack Overflow answers assume pandas 1.x/2.x. This matters for a learning Product Owner. *Mitigation:* note it in the setup docs and write code in the pandas 3 style.
3. **Archived libraries.** `pytrends` was archived in April 2025 and is not used (see the source register).
4. **Heavy forecasting libraries** (prophet, pmdarima) are not needed until Phase 4. Do not install them in Phase 1. Add them only when an experiment needs them.
5. **Node 25 is end-of-life.** Pin Node 26 LTS with `.nvmrc` when the frontend starts.

**Recommendation:** Python **3.13** pinned via uv, `requires-python = ">=3.13,<3.15"`, CI on 3.13. This gives full wheel coverage with headroom. Moving to 3.14 later is a one-line change.

## 4. Data-source feasibility (summary)

Full details, sources and dates are in [`docs/data/source-register.md`](../data/source-register.md).

| # | Source | Status | Access route | Cost | Main blocker / condition |
|---|---|---|---|---|---|
| 1 | Google Trends | **Feasible — manual** | Manual CSV export from trends.google.com, plus an application for the official Trends API alpha | Free | The official API is alpha-only, by application. No permitted way to automate daily pulls without it |
| 2 | Rockstar Newswire | **Feasible — curated** | Human-curated event ledger (URL + timestamps), reviewed in PRs | Free | No public API or RSS found. Rockstar's Terms of Service must be read before any automated fetching |
| 3 | YouTube | **Conditional** | Official YouTube Data API v3 | Free (quota) | Developer Policies require stored API data to be deleted or refreshed within 30 days, and forbid derived metrics without an accepted policy amendment. This conflicts with a long-term time series. Policy review needed first |
| 4 | Reddit | **Blocked** | — | — | New public Data API access requests closed on 31 Oct 2026. Public API access ends March 2027. Only commercial agreements remain |
| 5 | News | **Feasible — automatable** | GDELT DOC 2.0 API (free, keyless) | Free | Rolling ~3-month window, so collection must start now or launch coverage is lost |
| 6 | X | **Deferred — needs approval** | Official X API, pay-per-use | ~$0.005 per counts request; $0.005 per post read | No free tier. Needs a payment card → Product Owner approval |

**Recommended change to the PRD order:** move **News (GDELT)** up to Phase 2 together with Google Trends and the event ledger. It is the only fully automatable free source. Its 3-month window means coverage around the launch can only be captured by collecting soon. → [Decision 0003](../decisions/0003-source-priority-and-reddit.md).

## 5. Recommended technical architecture

Summary (details in [`system-architecture.md`](system-architecture.md)):

- **One Python package** (`src/gta6_intelligence/`) with one connector module per source behind a shared interface. It handles collection, validation, transformation, analytics and models.
- **Scheduled by GitHub Actions** (daily cron, free on public repositories), with a lock so runs never overlap. Manual runs use the same CLI.
- **Storage:** immutable raw artifacts (files with SHA-256 checksums). Structured data goes through SQLAlchemy and Alembic migrations, using SQLite locally and PostgreSQL in production. Raw data that must not be public is stored privately, not in this public repository.
- **Static-first web app:** Next.js + TypeScript + ECharts, built as a static site. It reads versioned JSON "data products" that the pipeline publishes after each run. **No FastAPI server in the MVP.** `backend/` is reserved for when a live API is actually needed. This deviates from the PRD's preferred starting point and needs approval → [Decision 0001](../decisions/0001-initial-architecture.md).
- **Observability:** a `collection_runs` table, structured JSON logs, and a published `status.json` (last successful run per source). The dashboard's Data Quality page renders it.

Why static-first: it costs nothing to host, it has no server to keep alive or secure, and the dashboard can never show something the pipeline did not produce and validate. Every number then traces back to a published data file.

## 6. Phased implementation plan

The phases follow PRD §16. Each task is one small branch and PR.

### Phase 0 — Discovery and design (this PR)
- [x] Inspect repository, environment, wheel compatibility
- [x] Source feasibility matrix with official sources
- [x] Architecture proposal and decision records
- [x] Team docs: cost register, first weekly update
- [ ] **Abdul:** review, answer the open decisions, run the environment check, push or confirm the missing scripts
- [ ] **Abdul:** apply for Google Trends API alpha access (form linked in the source register)
- [ ] Both: sign the charter acknowledgement (Charter §24) in a GitHub Issue

**Exit:** decisions 0001–0004 approved or changed; first Phase 1 issues created.

### Phase 1 — Reliable foundation (~1 week)

| PR | Branch | Files |
|---|---|---|
| 1 | `feature/python-project-setup` | `pyproject.toml`, `uv.lock`, `.python-version` (3.13), `src/gta6_intelligence/__init__.py`, `ruff` + `pytest` config, README setup section |
| 2 | `feature/config-and-logging` | `src/gta6_intelligence/config/settings.py` (pydantic-settings), `utils/logging.py` (JSON logs, secret redaction), tests |
| 3 | `feature/database-schema` | SQLAlchemy models for `sources`, `collection_runs`, `raw_artifacts`; Alembic setup + first migration; `docs/data/data-dictionary.md` |
| 4 | `feature/run-tracking` | `collection/runner.py` (run lifecycle, lock, per-source isolation), `connectors/base.py` (interface), raw artifact writer with checksums, tests using labelled fixtures |
| 5 | `feature/ci` | `.github/workflows/ci.yml`: ruff + pytest on every PR |

Commands after PR 1:

```bash
git clone https://github.com/abdu08099-arch/north-analytics-gta6-launch-intelligence.git
cd north-analytics-gta6-launch-intelligence
uv sync            # installs pinned Python 3.13 + dependencies
uv run pytest      # runs tests
uv run ruff check  # lint
```

**Exit:** a new developer sets up and runs the tests from the README alone.

### Phase 2 — First reliable pipeline (~1–2 weeks)
- `connectors/google_trends_csv.py`: imports manually exported CSVs from `data/inbox/`, keeps the original, records checksum and metadata, parses into `search_observations`
- `connectors/gdelt.py`: daily coverage volume + article list for a fixed query set (start as early as possible because of the 3-month window)
- `data/reference/event_milestones.csv` + loader: curated Rockstar/official events with URL, publication time, verification status
- Validation reports and quarantine; first data-quality report
- `docs/methodology/google-trends-protocol.md`: exact export procedure, so every manual export is identical

### Phase 3 — Additional connectors
- YouTube only after the policy review in Decision 0004 is resolved
- X only after cost approval (counts endpoint first)
- Reddit stays blocked unless a legitimate access route appears

### Phase 4 — Analytics and research
Descriptive statistics, event windows, naive and seasonal-naive baselines with rolling-origin evaluation, then anomaly detection. Sentiment work starts only if a source with permitted text exists and a manually labelled validation sample is made.

### Phase 5 — Web dashboard
Next.js static site, eight pages per PRD F9, data products from the pipeline, honest empty states.

### Phase 6 — Automation and deployment
Daily GitHub Actions schedule, secrets in GitHub Actions Secrets, publish step, alerting on failure. Note that GitHub disables scheduled workflows in public repositories after 60 days without repository activity, so the weekly update commits also keep the schedule alive.

### Phase 7 — Monitoring and final report
Continue until a verified official GTA VI Online launch date exists (currently none; see below).

## 7. Decisions needing Product Owner approval

| ID | Decision | Recommendation |
|---|---|---|
| [0001](../decisions/0001-initial-architecture.md) | Static-first dashboard, no FastAPI in MVP; Python 3.13 via uv | Approve |
| [0002](../decisions/0002-google-trends-access.md) | Google Trends via manual CSV export + alpha application; search term vs topic; export cadence | Approve; Abdul picks term vs topic |
| [0003](../decisions/0003-source-priority-and-reddit.md) | Move GDELT news into Phase 2; mark Reddit blocked | Approve |
| [0004](../decisions/0004-production-storage-and-hosting.md) | Where production data and the site live (all options free or ~€0) | Choose an option |
| — | X API: allow a small paid budget (e.g. $5/month cap) for counts only | Defer until Phase 3 |
| — | YouTube: accept the 30-day policy constraint, or apply for the derived-metrics amendment | Defer until Phase 3 |

## 8. Facts to keep in mind

- GTA VI is scheduled for release today, **19 November 2026**, on PS5 and Xbox Series X|S. That makes today a high-signal day: GDELT and the first Trends export should be captured as soon as possible.
- **No GTA VI Online launch date has been announced.** The end date stays unset, as the PRD requires.
- Rockstar's `robots.txt` blocks several AI crawlers (including ClaudeBot) from the whole site. This is another reason to curate the event ledger by hand rather than fetch it automatically.

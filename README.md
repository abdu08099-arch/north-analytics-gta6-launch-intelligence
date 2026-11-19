# north-analytics-gta6-launch-intelligence
A data science project analyzing global GTA VI launch interest using Python, Google Trends, machine learning and interactive dashboards.

**North Analytics — GTA VI Launch Intelligence** tracks public interest in Grand Theft Auto VI from **19 November 2026** until the verified launch of GTA VI Online (date not yet announced). It uses public search, news and community signals. It measures relative interest and coverage, not sales or player counts.

## Status

**Phase 1 — Reliable foundation.** Configuration, logging, database schema and run tracking are in place. No data is collected yet; the first connectors come in Phase 2. Background: [Phase 0 report](docs/architecture/phase-0-discovery-report.md).

| Source | Status |
|---|---|
| Google Trends | Feasible (manual export; API alpha application recommended) |
| Rockstar / official events | Feasible (curated ledger) |
| News (GDELT) | Feasible (automated) |
| YouTube | Conditional (policy review) |
| X | Deferred (needs cost approval) |
| Reddit | Blocked (public API closed to new apps) |

Details: [source register](docs/data/source-register.md).

## Key documents

| Document | Purpose |
|---|---|
| [PRD.md](PRD.md) | Product requirements |
| [TEAM_CHARTER.md](TEAM_CHARTER.md) | How the team works, decides and reviews |
| [docs/architecture/](docs/architecture/) | Architecture and Phase 0 report |
| [docs/data/source-register.md](docs/data/source-register.md) | Source access, terms, cost, status |
| [docs/decisions/](docs/decisions/) | Decision log |
| [docs/operations/cost-register.md](docs/operations/cost-register.md) | All services and costs |
| [docs/team/weekly-updates/](docs/team/weekly-updates/) | Weekly progress |

## Repository layout

```text
├── PRD.md, TEAM_CHARTER.md, .env.example
├── docs/        architecture, data, methodology, decisions, team, operations
├── src/gta6_intelligence/  Python package: config, connectors, collection, db (+ migrations), utils
├── backend/     reserved; no API server in the MVP (Decision 0001)
├── frontend/    Next.js static dashboard (Phase 5)
├── data/        local data, gitignored except reference/ (see data/README.md)
├── tests/       unit and integration tests, labelled fixtures
└── .github/workflows/  CI and daily collection
```

## Setup

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and git. uv installs the pinned Python version (3.13) for you, so your system Python does not matter.

```bash
git clone https://github.com/abdu08099-arch/north-analytics-gta6-launch-intelligence.git
cd north-analytics-gta6-launch-intelligence
uv sync                       # Python 3.13 + exact dependency versions from uv.lock
cp .env.example .env          # local settings; never commit .env
uv run gta6 db upgrade        # creates data/gta6.db (SQLite)
uv run gta6 db seed-sources   # writes the six sources and their status
uv run gta6 sources           # check
```

Everyday commands:

| Command | What it does |
|---|---|
| `uv run pytest` | Run all tests |
| `uv run ruff check src tests` | Lint |
| `uv run ruff format src tests` | Auto-format |
| `uv run gta6 collect --all` | Run every implemented connector (none yet) |
| `uv run gta6 runs` | Show recent collection runs and failures |

To run the tests against PostgreSQL as well (CI does this on every PR), point `TEST_DATABASE_URL` at a **throwaway** database; its schema is wiped before each test:

```bash
TEST_DATABASE_URL=postgresql+psycopg://user@localhost:5432/gta6_test uv run pytest
```

### pandas 3 note
When pandas is added in Phase 2, it will be pandas 3. Copy-on-Write and the new string dtype are on by default, so some older tutorials behave differently.

## Data use

Google Trends data © Google, used with attribution. News coverage data from the GDELT Project. No private, restricted or personal data is collected. See the [source register](docs/data/source-register.md) for each source's terms.

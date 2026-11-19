# north-analytics-gta6-launch-intelligence
A data science project analyzing global GTA VI launch interest using Python, Google Trends, machine learning and interactive dashboards.

**North Analytics — GTA VI Launch Intelligence** tracks public interest in Grand Theft Auto VI from **19 November 2026** until the verified launch of GTA VI Online (date not yet announced). It uses public search, news and community signals. It measures relative interest and coverage, not sales or player counts.

## Status

**Phase 0 — Discovery and technical design.** No code yet. See the [Phase 0 report](docs/architecture/phase-0-discovery-report.md).

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
├── src/         Python package gta6_intelligence (Phase 1)
├── backend/     reserved; no API server in the MVP (Decision 0001)
├── frontend/    Next.js static dashboard (Phase 5)
├── data/        local data, gitignored except reference/ (see data/README.md)
├── tests/       unit and integration tests, labelled fixtures
└── .github/workflows/  CI and daily collection
```

## Setup

Setup instructions arrive with Phase 1 (Python 3.13 via [uv](https://docs.astral.sh/uv/)).

## Data use

Google Trends data © Google, used with attribution. News coverage data from the GDELT Project. No private, restricted or personal data is collected. See the [source register](docs/data/source-register.md) for each source's terms.

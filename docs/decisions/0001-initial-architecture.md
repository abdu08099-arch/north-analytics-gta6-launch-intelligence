# 0001 — Initial architecture: static-first, Python 3.13 via uv

- **Date proposed:** 2026-11-19
- **Status:** Proposed
- **Owner:** Technical Lead
- **Approver:** Product Owner — _pending_
- **Date approved:** _pending_

## Context
The PRD (§10) prefers Python + FastAPI + PostgreSQL + Next.js. It asks for a proposal before large-scale implementation and warns against premature complexity. All data arrives at most once per day.

## Options considered
1. **FastAPI backend + Next.js frontend from day one.** Live queries, but a server to host, secure, keep alive and pay for. The dashboard can query states the pipeline never validated.
2. **Static-first (recommended).** The pipeline publishes versioned JSON data products; Next.js is exported as a static site that reads them. No server. FastAPI is added later if a concrete need appears.
3. **Streamlit.** Fast, but the PRD explicitly rules it out as the final product.

## Decision (proposed)
Option 2. Python 3.13 pinned with uv (`.python-version`, `requires-python = ">=3.13,<3.15"`). SQLAlchemy + Alembic with SQLite locally and PostgreSQL in production. GitHub Actions for CI and the daily schedule. Node 26 LTS for the frontend. `backend/` stays reserved.

## Consequences
- Hosting is free, and there is no server to maintain.
- Every chart traces to a published data file with metadata.
- PRD "health endpoint" is met by a published `status.json`. If a real HTTP health check is needed later, add FastAPI then.
- Python 3.14 is not used yet because smaller scientific packages lag behind (ruptures resolved to an older version on 3.14). Revisit in 2027.

## Follow-up
Phase 1 PRs 1–5 (see the Phase 0 report §6).

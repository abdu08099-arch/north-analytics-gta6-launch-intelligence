# 0004 — Production storage and hosting

- **Date proposed:** 2026-11-19
- **Status:** Proposed — **needs a choice from the Product Owner**
- **Owner:** Technical Lead
- **Approver:** Product Owner — _pending_
- **Date approved:** _pending_

## Context
GitHub Actions runners are temporary: anything a daily run collects must be saved somewhere else. Raw data must not go into this public repository (YouTube policy, third-party content, Charter §6.5). Accounts and billing must be owned by the Product Owner, with least-privilege access for the Technical Lead (Charter §4). No cost may be incurred without approval.

## Options (all start at €0)

| Option | Database | Raw artifacts | Site | Trade-offs |
|---|---|---|---|---|
| **A. Managed free tiers (recommended)** | Free PostgreSQL tier (e.g. Neon or Supabase) | Free object storage tier (e.g. Cloudflare R2 or Supabase Storage) | GitHub Pages | Fully automatic; free-tier limits and inactivity rules must be checked per provider before signing up |
| B. Private data repository | SQLite file committed to a separate **private** repo | Same private repo | GitHub Pages | Simple and all on GitHub; Git is a poor fit for a growing binary DB; private-repo Actions minutes are limited |
| C. Small VPS | PostgreSQL on the VPS | VPS disk | VPS or GitHub Pages | Full control; costs money (a few €/month) and needs maintenance and security patching |

Hosting the site on **Vercel Hobby** is also possible, but that plan is for personal, non-commercial use. If North Analytics becomes commercial, use GitHub Pages or a paid plan.

## Decision
_Product Owner to choose A, B or C._ Once chosen, the Technical Lead verifies the provider's current limits and terms and records them in `docs/operations/cost-register.md` before any account is created. The Product Owner creates the account and owns billing.

## Not needed until
Phase 6 (automation and deployment). Phases 1–5 run locally.

**Note on GDELT before Phase 6:** GDELT keeps roughly 3 months of searchable coverage. Until the daily schedule runs in production, a manual `gta6 collect --source gdelt` at least once a week on a local machine is enough to avoid gaps. The raw artifacts are then uploaded once storage exists.

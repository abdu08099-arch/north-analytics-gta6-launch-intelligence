# Data Dictionary

**Version:** Phase 1 (migration `0001`)
**Rule:** every timestamp is stored in UTC and is timezone-aware. A missing value is `NULL`, never `0`.

Observation tables (`search_observations`, `content_items`, `event_milestones`, `derived_metrics`, `model_runs`) are added with the connectors that fill them, from Phase 2 on.

## `sources`

One row per data source from the PRD. Filled by `gta6 db seed-sources` from `src/gta6_intelligence/sources/catalog.py`, which mirrors `docs/data/source-register.md`.

| Column | Type | Meaning |
|---|---|---|
| `source_id` | text, PK | Short stable id: `google_trends`, `event_ledger`, `gdelt`, `youtube`, `reddit`, `x` |
| `name` | text | Human-readable name |
| `source_type` | text | `search_interest`, `events`, `news`, `video`, `community`, `social` |
| `documentation_url` | text | Official documentation or terms page reviewed |
| `access_method` | text | How we get the data, in plain words |
| `status` | enum | `enabled` (collecting), `planned` (approved, connector not built), `conditional` (blocked on a policy decision), `deferred` (needs approval/cost), `blocked` (no permitted access), `disabled` (switched off) |
| `terms_reviewed_on` | date | When terms/pricing were last checked |
| `notes` | text | Key limitation or decision reference |

## `collection_runs`

One row per attempt to collect from one source. A row is written **before** fetching starts, so failures are always visible.

| Column | Type | Meaning |
|---|---|---|
| `run_id` | UUID text, PK | Also part of every raw artifact's filename |
| `source_id` | FK → `sources` | Which source |
| `trigger` | enum | `scheduled` (daily job) or `manual` |
| `collection_mode` | enum | `live` (collected during the project) or `backfill` (historical data fetched later; PRD §7 requires keeping these apart) |
| `status` | enum | `running`, `success`, `partial`, `failed`. A row stuck in `running` means the process died |
| `started_at`, `finished_at` | timestamp UTC | Run duration |
| `fetched_count` | int ≥ 0 | Raw payloads stored in this run |
| `valid_count`, `rejected_count` | int ≥ 0 | Records that passed/failed validation (used from Phase 2) |
| `error_message` | text | Exception type and message, secrets redacted, max 2,000 characters |
| `metadata` | JSON | Free-form run details (e.g. quota used) |
| `code_version` | text | Package version that ran, for reproducibility |

## `raw_artifacts`

One row per raw payload saved unchanged to disk.

| Column | Type | Meaning |
|---|---|---|
| `artifact_id` | UUID text, PK | |
| `run_id` | FK → `collection_runs` | Run that fetched it |
| `source_id` | FK → `sources` | |
| `relative_path` | text, unique | Path under `data/raw/`: `<source>/<YYYY>/<MM>/<DD>/<run_id>-<n>.<ext>`. Files are never overwritten |
| `sha256` | text | Checksum of the exact bytes; proves the file was not changed |
| `size_bytes` | int | |
| `media_type` | text | e.g. `application/json`, `text/csv` |
| `retrieved_at` | timestamp UTC | When we received it |
| `coverage_start`, `coverage_end` | timestamp UTC | Period the payload describes, when known (e.g. a Trends export window) |
| `request_params` | JSON | Exact query parameters (query, geo, window, …), with no secrets |

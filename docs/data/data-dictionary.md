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

---

# Phase 2 tables (migration `0002`)

## `artifact_processing`
One row per raw artifact that a processor has handled.

| Column | Meaning |
|---|---|
| `artifact_id` | PK and FK → `raw_artifacts` |
| `processor`, `processor_version` | Which parsing rules produced the rows |
| `status` | `processed`, `partial` (some records quarantined) or `failed` (file unreadable; it is retried on the next `gta6 process`) |
| `processed_at` | UTC |
| `rows_written`, `rows_rejected` | Counts |
| `error_message` | Why it failed (e.g. checksum mismatch, unknown CSV layout) |

## `quarantined_records`
Records that failed validation, kept with the reason (PRD F3): `artifact_id`, `source_id`, `reason`, `record` (the original values as JSON), `quarantined_at`.

## `news_coverage_points` (GDELT timeline)
| Column | Meaning |
|---|---|
| `artifact_id` | Snapshot it came from. Overlapping snapshots are kept apart, never summed |
| `query` | Exact GDELT query string |
| `resolution` | As reported by GDELT (`hour` for multi-day windows) |
| `period_start` | UTC start of the period |
| `matching_articles` | Articles matching the query in that period |
| `total_monitored` | All articles GDELT monitored in that period. Share = matching ÷ monitored |
| `retrieved_at` | When the snapshot was fetched |

## `news_articles` (GDELT article lists)
Metadata only, no article text. `url` (unique: each article stored once), `title`, `domain`, `language`, `source_country`, `seen_at` (when GDELT first saw it, UTC), `story_key` (same normalised title on the same UTC day, used to group syndicated copies), `query`, `first_artifact_id`.

## `search_observations` (Google Trends)
| Column | Meaning |
|---|---|
| `artifact_id` | The export file (snapshot) |
| `series_label` | Column header from the export, e.g. `GTA 6: (Denmark)` |
| `query`, `query_kind` | Slug and `term`/`topic`, from the file name (see the protocol) |
| `geo` | `WW` or country code |
| `granularity` | `hour`, `day`, `week` or `month` |
| `period_start` | UTC start of the period |
| `interest_value` | 0–100, relative **within this export only**; NULL when `<1` or missing |
| `value_flag` | `<1`, `missing` or NULL |
| `export_window` | e.g. `past-90-days` |

## `event_milestones`
Loaded from `data/reference/event_milestones.csv`, the full current list; a new file version replaces the table.

| Column | Meaning |
|---|---|
| `event_id` | Stable id, e.g. `2026-11-19-release` |
| `event_name`, `event_type` | Type is one of: announcement, delay, trailer, preorder, preload, release, online_launch, update, earnings, other |
| `event_date` | Date of the event |
| `published_at` | Official publication time with timezone, if known |
| `source_url`, `source_kind` | `official` (Rockstar, Take-Two) or `secondary` (press) |
| `verification_status` | `verified` requires an official source **and** a named reviewer; `unverified`; `disputed` |
| `reviewer`, `notes`, `summary` | Our own short factual summary, never copied text |
| `artifact_id` | The exact ledger file version it was loaded from |

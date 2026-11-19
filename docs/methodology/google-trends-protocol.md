# Google Trends export protocol

**Status:** draft. The settings below follow the recommendations in Decision 0002. Abdul confirms them (term vs topic, cadence) before the first official export.

Google Trends gives relative interest (0–100) **within one export**. A value of 50 in one file and 50 in another do not mean the same thing. This protocol exists so that every export is made the same way and can be traced.

## Fixed settings

| Setting | Value |
|---|---|
| Search | **Topic** "Grand Theft Auto VI" (primary series, slug `gta6`). Secondary: **term** `GTA 6` (slug `gta-6`) |
| Category | All categories |
| Search type | Web search |
| Geographies | Worldwide (`WW`), `DK`, `US`, `GB`, `DE`, `FR`, `SE`, one export per geography |
| Windows | `past-90-days` (daily values), twice a week; `past-7-days` (hourly values) on launch-week days |
| Comparison exports | One extra export with the same topic compared across all six countries in one chart; only this file allows level comparisons between countries |

Write down any setting you had to change in the PR that adds the file.

## Steps

1. Open trends.google.com in a normal browser session and set exactly the settings above.
2. On the "Interest over time" chart, use **Download** (CSV). Google documents this export in its help centre.
3. Rename the file to:
   ```text
   <export-date>_<geo>_<window>_<term|topic>-<slug>_<your-initials>.csv
   2026-11-19_DK_past-90-days_topic-gta6_ab.csv
   ```
   Use UTC dates. Geo is `WW` or the two-letter country code. Files that do not match this pattern are refused by the importer and listed in the run error.
4. Put it in `data/inbox/google_trends/`. **Do not edit the file.**
5. Run:
   ```bash
   uv run gta6 collect --source google_trends   # stores an exact copy + checksum
   uv run gta6 process --source google_trends   # parses into search_observations
   uv run gta6 runs
   ```
   The same file is never imported twice, because the importer compares checksums.

## How values are stored

| In the CSV | In `search_observations` |
|---|---|
| `0`–`100` | `interest_value` = number |
| `<1` | `interest_value` = NULL, `value_flag` = `<1` (more than 0, less than 1) |
| empty | `interest_value` = NULL, `value_flag` = `missing` (never 0) |
| anything else | the row goes to `quarantined_records` with the reason |

Each file stays its own snapshot (`artifact_id`). Files are never appended into one long series (PRD §8.1). If a continuous series is needed, an overlap-calibration method must be written up and approved first.

## Verify with the first real export

The importer was built from Google's documented CSV layout (preamble lines, then a header row `Day/Week/Month/Time,<series>`). If Google has changed the layout, that file fails to process: it shows up as `failed` in `artifact_processing`, and no rows are written. In that case, send the file to the Technical Lead to update the parser.

## Attribution

Charts and reports using this data must say "Source: Google Trends (trends.google.com)". Values are relative search interest, not search volumes.

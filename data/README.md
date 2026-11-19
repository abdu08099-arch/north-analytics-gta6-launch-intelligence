# data/

Local data only. **Everything in this folder is gitignored except this README and `reference/`.**

```text
data/
├── inbox/        # manual drops, e.g. Google Trends CSV exports, before import
├── raw/          # immutable raw artifacts: raw/<source>/<YYYY>/<MM>/<DD>/<run_id>.<ext>
├── quarantine/   # records that failed validation, with reasons
├── staging/      # parsed, validated, not yet curated
├── processed/    # curated analytical datasets (Parquet)
├── reference/    # COMMITTED: curated event ledger and other reference tables we author
└── gta6.db       # local SQLite database
```

Rules (Charter §6.5, PRD §13):
- Never edit or delete files in `raw/`. Corrections create new versions.
- Do not commit raw API data. In production it lives in private storage (Decision 0004).
- Test fixtures live in `tests/fixtures/` and must be clearly labelled as fixtures, not real observations.

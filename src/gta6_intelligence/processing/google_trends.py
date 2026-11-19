"""Parse manual Google Trends CSV exports into `search_observations`.

Known layout of the website's "interest over time" export (Google Trends Help:
"export charts as CSV files"):

    Category: All categories            <- optional preamble lines
    <blank>
    Day,GTA 6: (Denmark)                <- header: period column + one column per series
    2026-08-21,3
    2026-08-22,<1

The parser finds the header row by its first cell (Day, Week, Month, Time or
Date), so it tolerates extra or missing preamble lines.

Value rules (PRD §8.1):
- integers 0-100 are relative interest within this export only
- "<1" is stored as NULL with value_flag "<1" (above zero, below 1)
- an empty cell is stored as NULL with value_flag "missing", never as 0
- anything else is quarantined

VERIFY with the first real export: if Google has changed the layout, the
artifact fails to process (visible in `artifact_processing`) and no rows are
written, so a wrong guess can never produce wrong data silently.
"""

import csv
import io
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from gta6_intelligence.db.models import RawArtifact, SearchObservation
from gta6_intelligence.processing.base import Processor, ProcessOutcome, Reject

PERIOD_HEADERS = {"day": "day", "week": "week", "month": "month", "time": None, "date": None}
DATE_FORMATS = (
    ("%Y-%m-%dT%H", "hour"),
    ("%Y-%m-%dT%H:%M", "hour"),
    ("%Y-%m-%d", "day"),
    ("%Y-%m", "month"),
)


def _parse_period(text: str) -> tuple[datetime, str]:
    value = text.strip().removesuffix("Z")
    for fmt, granularity in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=UTC), granularity
        except ValueError:
            continue
    raise ValueError(f"unrecognised period {text!r}")


def _find_header(rows: list[list[str]]) -> int:
    for i, row in enumerate(rows):
        if row and row[0].strip().casefold() in PERIOD_HEADERS and len(row) >= 2:
            return i
    raise ValueError("no header row found (expected first column Day/Week/Month/Time/Date)")


class GoogleTrendsCsvProcessor(Processor):
    source_id = "google_trends"
    name = "google_trends_csv"
    version = "1"

    def process(self, session: Session, artifact: RawArtifact, content: bytes) -> ProcessOutcome:
        params = artifact.request_params
        rows = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
        header_at = _find_header(rows)
        header = rows[header_at]
        declared = PERIOD_HEADERS[header[0].strip().casefold()]
        series_labels = [h.strip() for h in header[1:]]

        outcome = ProcessOutcome()
        for line_no, row in enumerate(rows[header_at + 1 :], start=header_at + 2):
            if not row or not any(cell.strip() for cell in row):
                continue
            try:
                period_start, inferred = _parse_period(row[0])
            except ValueError as exc:
                outcome.rejects.append(Reject(f"line {line_no}: {exc}", {"row": row}))
                continue
            granularity = declared or inferred
            for label, cell in zip(series_labels, row[1:], strict=False):
                cell = cell.strip()
                value: int | None
                flag: str | None = None
                if cell == "<1":
                    value, flag = None, "<1"
                elif cell == "":
                    value, flag = None, "missing"
                elif cell.isdigit() and 0 <= int(cell) <= 100:
                    value = int(cell)
                else:
                    outcome.rejects.append(
                        Reject(f"line {line_no}: invalid value {cell!r}", {"row": row})
                    )
                    continue
                session.add(
                    SearchObservation(
                        artifact_id=artifact.artifact_id,
                        series_label=label,
                        query=params["query"],
                        query_kind=params["query_kind"],
                        geo=params["geo"],
                        granularity=granularity,
                        period_start=period_start,
                        interest_value=value,
                        value_flag=flag,
                        export_window=params["window"],
                    )
                )
                outcome.rows_written += 1
        return outcome

"""Connectors for data we receive as files instead of from an API.

- EventLedgerConnector reads the curated ledger in data/reference/.
- GoogleTrendsInboxConnector reads manual Trends CSV exports from data/inbox/google_trends/.

Both skip content that is already stored, so running them daily is harmless.
"""

import re
from collections.abc import Iterator
from pathlib import Path

from gta6_intelligence.config.settings import get_settings
from gta6_intelligence.connectors.base import BaseConnector, FetchContext, FetchedPayload

LEDGER_FILE = "event_milestones.csv"

# <export-date>_<geo>_<window>_<term|topic>-<slug>_<exporter>.csv
# e.g. 2026-11-19_DK_past-90-days_topic-gta6_allan.csv
# (see docs/methodology/google-trends-protocol.md)
TRENDS_FILENAME = re.compile(
    r"^(?P<export_date>\d{4}-\d{2}-\d{2})_(?P<geo>WW|[A-Z]{2})_(?P<window>[a-z0-9-]+)_"
    r"(?P<query_kind>term|topic)-(?P<query>[a-z0-9-]+)_(?P<exported_by>[a-z0-9]+)\.csv$"
)


class InboxFileError(ValueError):
    pass


class EventLedgerConnector(BaseConnector):
    source_id = "event_ledger"
    skip_unchanged = True

    def __init__(self, reference_dir: Path | None = None) -> None:
        self.reference_dir = reference_dir or get_settings().data_dir / "reference"

    def fetch(self, ctx: FetchContext) -> Iterator[FetchedPayload]:
        path = self.reference_dir / LEDGER_FILE
        yield FetchedPayload(
            content=path.read_bytes(),
            media_type="text/csv",
            extension="csv",
            request_params={"file": f"data/reference/{LEDGER_FILE}"},
        )


class GoogleTrendsInboxConnector(BaseConnector):
    source_id = "google_trends"
    skip_unchanged = True

    def __init__(self, inbox_dir: Path | None = None) -> None:
        self.inbox_dir = inbox_dir or get_settings().data_dir / "inbox" / "google_trends"

    def fetch(self, ctx: FetchContext) -> Iterator[FetchedPayload]:
        bad: list[str] = []
        for path in sorted(self.inbox_dir.glob("*.csv")):
            match = TRENDS_FILENAME.match(path.name)
            if not match:
                bad.append(path.name)
                continue
            yield FetchedPayload(
                content=path.read_bytes(),
                media_type="text/csv",
                extension="csv",
                request_params={"file": path.name, **match.groupdict()},
            )
        if bad:
            raise InboxFileError(
                "file names do not follow the export protocol (not imported): " + ", ".join(bad)
            )

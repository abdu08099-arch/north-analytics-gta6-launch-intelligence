"""Processors per source."""

from gta6_intelligence.processing.base import Processor
from gta6_intelligence.processing.events import EventLedgerProcessor
from gta6_intelligence.processing.gdelt import GdeltProcessor
from gta6_intelligence.processing.google_trends import GoogleTrendsCsvProcessor

PROCESSORS: dict[str, type[Processor]] = {
    p.source_id: p for p in (GdeltProcessor, EventLedgerProcessor, GoogleTrendsCsvProcessor)
}

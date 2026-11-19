"""The contract every source connector implements.

A connector only *fetches*: it returns the bytes exactly as the source sent
them. The runner stores them unchanged with a checksum before anything else
happens, so every later number can be traced back to an original artifact.
Parsing and validation into observation tables are added in Phase 2.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from gta6_intelligence.db.models import CollectionMode


@dataclass(frozen=True)
class FetchContext:
    run_id: str
    started_at: datetime
    collection_mode: CollectionMode


@dataclass(frozen=True)
class FetchedPayload:
    content: bytes
    media_type: str  # e.g. "application/json", "text/csv"
    extension: str  # file extension without dot, e.g. "json"
    request_params: dict[str, Any] = field(default_factory=dict)
    coverage_start: datetime | None = None
    coverage_end: datetime | None = None


class BaseConnector(ABC):
    #: Must match a source_id in gta6_intelligence.sources.catalog.
    source_id: str

    @abstractmethod
    def fetch(self, ctx: FetchContext) -> Iterator[FetchedPayload]:
        """Yield raw payloads one at a time. Raise an exception on failure.

        The runner stores each payload as soon as it is yielded, so if a later
        request fails, what was already fetched is kept and the run is `partial`.
        """

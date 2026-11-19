"""The contract for turning a stored raw artifact into table rows.

A processor reads one raw artifact (bytes + its metadata) and adds rows to the
session. Records that fail validation are returned as rejects and end up in
`quarantined_records` with the reason. The processing runner commits each
artifact in its own transaction, so a bad file never leaves half its rows behind.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from gta6_intelligence.db.models import RawArtifact


@dataclass
class Reject:
    reason: str
    record: dict[str, Any]


@dataclass
class ProcessOutcome:
    rows_written: int = 0
    rejects: list[Reject] = field(default_factory=list)
    skipped_duplicates: int = 0


class Processor(ABC):
    source_id: str
    name: str
    #: Bump when parsing rules change, so it is clear which rows came from which rules.
    version: str

    @abstractmethod
    def process(self, session: Session, artifact: RawArtifact, content: bytes) -> ProcessOutcome:
        """Add rows for this artifact to `session`. Do not commit. Raise if unreadable."""

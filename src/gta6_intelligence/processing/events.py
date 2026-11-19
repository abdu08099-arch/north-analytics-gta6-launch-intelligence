"""Load the curated event ledger into `event_milestones`.

The ledger file is the full, current list. Loading a newer version replaces
the table contents, so an event removed from the file (by a reviewed PR) is
removed from the database too. Every row points to the raw artifact (the exact
file version, with checksum) it came from.
"""

import csv
import io
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from sqlalchemy import delete
from sqlalchemy.orm import Session

from gta6_intelligence.db.models import EventMilestone, RawArtifact, VerificationStatus
from gta6_intelligence.processing.base import Processor, ProcessOutcome, Reject

EVENT_TYPES = {
    "announcement",
    "delay",
    "trailer",
    "preorder",
    "preload",
    "release",
    "online_launch",
    "update",
    "earnings",
    "other",
}

REQUIRED_COLUMNS = [
    "event_id",
    "event_name",
    "event_type",
    "event_date",
    "published_at",
    "source_url",
    "source_kind",
    "summary",
    "verification_status",
    "reviewer",
    "notes",
]


class EventRow(BaseModel):
    event_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,79}$")
    event_name: str = Field(min_length=3, max_length=300)
    event_type: str
    event_date: date
    published_at: datetime | None = None
    source_url: str = Field(pattern=r"^https://")
    source_kind: Literal["official", "secondary"]
    summary: str = Field(min_length=10)
    verification_status: VerificationStatus
    reviewer: str | None = None
    notes: str | None = None

    @field_validator("published_at", "reviewer", "notes", mode="before")
    @classmethod
    def _blank_is_none(cls, v: object) -> object:
        return None if v == "" else v

    @field_validator("event_type")
    @classmethod
    def _known_type(cls, v: str) -> str:
        if v not in EVENT_TYPES:
            raise ValueError(f"unknown event_type {v!r}; allowed: {sorted(EVENT_TYPES)}")
        return v

    @field_validator("published_at")
    @classmethod
    def _aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError("published_at needs a timezone, e.g. 2026-11-19T14:00:00Z")
        return v

    @model_validator(mode="after")
    def _verified_needs_official_source_and_reviewer(self) -> "EventRow":
        if self.verification_status is VerificationStatus.VERIFIED and (
            self.source_kind != "official" or not self.reviewer
        ):
            raise ValueError("verified events need source_kind=official and a reviewer")
        return self


class EventLedgerProcessor(Processor):
    source_id = "event_ledger"
    name = "event_ledger"
    version = "1"

    def process(self, session: Session, artifact: RawArtifact, content: bytes) -> ProcessOutcome:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"ledger is missing columns: {missing}")

        outcome = ProcessOutcome()
        rows: dict[str, EventRow] = {}
        for line_no, raw in enumerate(reader, start=2):
            try:
                row = EventRow.model_validate(raw)
            except ValidationError as exc:
                outcome.rejects.append(Reject(f"line {line_no}: {exc}"[:500], dict(raw)))
                continue
            if row.event_id in rows:
                outcome.rejects.append(Reject(f"line {line_no}: duplicate event_id", dict(raw)))
                continue
            rows[row.event_id] = row

        session.execute(delete(EventMilestone))
        for row in rows.values():
            session.add(EventMilestone(**row.model_dump(), artifact_id=artifact.artifact_id))
        outcome.rows_written = len(rows)
        return outcome

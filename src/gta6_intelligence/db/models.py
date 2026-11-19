"""Database tables for Phase 1: sources, collection runs and raw artifacts.

Business meaning of each column is in docs/data/data-dictionary.md.
Observation tables (search_observations, content_items, ...) arrive with the
first connectors in Phase 2.
"""

import enum
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Text,
    TypeDecorator,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from gta6_intelligence.utils.time import ensure_utc

# Stable constraint names, so migrations work the same on SQLite and PostgreSQL.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class UtcDateTime(TypeDecorator[datetime]):
    """Stores aware datetimes as UTC and always returns them as aware UTC.

    SQLite has no timezone type; without this, values come back naive.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Any) -> datetime | None:
        return None if value is None else ensure_utc(value)

    def process_result_value(self, value: datetime | None, dialect: Any) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:  # SQLite returns naive values; they were stored as UTC
            return value.replace(tzinfo=UTC)
        return ensure_utc(value)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class SourceStatus(enum.StrEnum):
    ENABLED = "enabled"
    PLANNED = "planned"
    CONDITIONAL = "conditional"
    DEFERRED = "deferred"
    BLOCKED = "blocked"
    DISABLED = "disabled"


class RunStatus(enum.StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class RunTrigger(enum.StrEnum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class CollectionMode(enum.StrEnum):
    LIVE = "live"
    BACKFILL = "backfill"


def _enum(cls: type[enum.StrEnum], name: str) -> Enum:
    # Stored as plain strings with a CHECK constraint: portable and readable in SQL.
    return Enum(
        cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda e: [m.value for m in e],
        length=20,
    )


class Source(Base):
    __tablename__ = "sources"

    source_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(50))
    documentation_url: Mapped[str | None] = mapped_column(String(500))
    access_method: Mapped[str] = mapped_column(String(200))
    status: Mapped[SourceStatus] = mapped_column(_enum(SourceStatus, "source_status"))
    terms_reviewed_on: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    runs: Mapped[list["CollectionRun"]] = relationship(back_populates="source")


class CollectionRun(Base):
    __tablename__ = "collection_runs"
    __table_args__ = (
        CheckConstraint(
            "fetched_count >= 0 AND valid_count >= 0 AND rejected_count >= 0",
            name="non_negative_counts",
        ),
    )

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.source_id"), index=True)
    trigger: Mapped[RunTrigger] = mapped_column(_enum(RunTrigger, "run_trigger"))
    collection_mode: Mapped[CollectionMode] = mapped_column(
        _enum(CollectionMode, "collection_mode")
    )
    status: Mapped[RunStatus] = mapped_column(_enum(RunStatus, "run_status"), index=True)
    started_at: Mapped[datetime] = mapped_column(UtcDateTime(), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    valid_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    run_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    code_version: Mapped[str | None] = mapped_column(String(64))

    source: Mapped[Source] = relationship(back_populates="runs")
    artifacts: Mapped[list["RawArtifact"]] = relationship(back_populates="run")


class RawArtifact(Base):
    __tablename__ = "raw_artifacts"

    artifact_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("collection_runs.run_id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.source_id"), index=True)
    relative_path: Mapped[str] = mapped_column(String(500), unique=True)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    media_type: Mapped[str] = mapped_column(String(100))
    retrieved_at: Mapped[datetime] = mapped_column(UtcDateTime())
    coverage_start: Mapped[datetime | None] = mapped_column(UtcDateTime())
    coverage_end: Mapped[datetime | None] = mapped_column(UtcDateTime())
    request_params: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    run: Mapped[CollectionRun] = relationship(back_populates="artifacts")


# --- Phase 2: processing and observations -------------------------------------------------


class ProcessingStatus(enum.StrEnum):
    PROCESSED = "processed"
    PARTIAL = "partial"  # some records quarantined
    FAILED = "failed"  # artifact could not be read at all


class VerificationStatus(enum.StrEnum):
    VERIFIED = "verified"  # checked against an official source by a named reviewer
    UNVERIFIED = "unverified"  # entered from a secondary source; needs review
    DISPUTED = "disputed"


class ArtifactProcessing(Base):
    """Which raw artifacts have been parsed, by which processor version, with what result."""

    __tablename__ = "artifact_processing"

    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("raw_artifacts.artifact_id"), primary_key=True
    )
    processor: Mapped[str] = mapped_column(String(100))
    processor_version: Mapped[str] = mapped_column(String(20))
    status: Mapped[ProcessingStatus] = mapped_column(_enum(ProcessingStatus, "processing_status"))
    processed_at: Mapped[datetime] = mapped_column(UtcDateTime())
    rows_written: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)


class QuarantinedRecord(Base):
    """Records that failed validation. Kept with the reason, never silently dropped (PRD F3)."""

    __tablename__ = "quarantined_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("raw_artifacts.artifact_id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.source_id"))
    reason: Mapped[str] = mapped_column(Text)
    record: Mapped[dict[str, Any]] = mapped_column(JSON)
    quarantined_at: Mapped[datetime] = mapped_column(UtcDateTime())


class NewsCoveragePoint(Base):
    """One point of a GDELT coverage timeline, at the resolution GDELT returned (often hourly)."""

    __tablename__ = "news_coverage_points"
    __table_args__ = (
        UniqueConstraint("artifact_id", "period_start", name="artifact_period"),
        CheckConstraint("matching_articles >= 0", name="matching_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("raw_artifacts.artifact_id"), index=True)
    query: Mapped[str] = mapped_column(Text)
    resolution: Mapped[str] = mapped_column(String(20))  # as reported by GDELT, e.g. "hour"
    period_start: Mapped[datetime] = mapped_column(UtcDateTime(), index=True)
    matching_articles: Mapped[int] = mapped_column(Integer)
    total_monitored: Mapped[int | None] = mapped_column(Integer)
    retrieved_at: Mapped[datetime] = mapped_column(UtcDateTime())


class NewsArticle(Base):
    """Article metadata from GDELT article lists. No article text is stored."""

    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2000), unique=True)
    title: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(300), index=True)
    language: Mapped[str | None] = mapped_column(String(50))
    source_country: Mapped[str | None] = mapped_column(String(100))
    seen_at: Mapped[datetime] = mapped_column(UtcDateTime(), index=True)
    # Same normalised title on the same UTC day -> same story key (syndication dedup).
    story_key: Mapped[str] = mapped_column(String(64), index=True)
    query: Mapped[str] = mapped_column(Text)
    first_artifact_id: Mapped[str] = mapped_column(ForeignKey("raw_artifacts.artifact_id"))


class SearchObservation(Base):
    """One Google Trends value. Relative interest 0-100 within its own export only."""

    __tablename__ = "search_observations"
    __table_args__ = (
        UniqueConstraint("artifact_id", "series_label", "period_start", name="artifact_series"),
        CheckConstraint(
            "interest_value IS NULL OR (interest_value >= 0 AND interest_value <= 100)",
            name="interest_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("raw_artifacts.artifact_id"), index=True)
    series_label: Mapped[str] = mapped_column(String(300))  # column header from the export
    query: Mapped[str] = mapped_column(String(200))  # term or topic, from the file name
    query_kind: Mapped[str] = mapped_column(String(10))  # "term" or "topic"
    geo: Mapped[str] = mapped_column(String(10), index=True)  # "WW", "DK", "US", ...
    granularity: Mapped[str] = mapped_column(String(10))  # "hour", "day", "week", "month"
    period_start: Mapped[datetime] = mapped_column(UtcDateTime(), index=True)
    interest_value: Mapped[int | None] = mapped_column(Integer)
    # "<1" when Trends reports less than 1; NULL value + "missing" when the cell is empty.
    value_flag: Mapped[str | None] = mapped_column(String(20))
    export_window: Mapped[str] = mapped_column(String(50))


class EventMilestone(Base):
    """Curated official milestones. Loaded from data/reference/event_milestones.csv."""

    __tablename__ = "event_milestones"

    event_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    event_name: Mapped[str] = mapped_column(String(300))
    event_type: Mapped[str] = mapped_column(String(50))
    event_date: Mapped[date] = mapped_column(Date, index=True)
    published_at: Mapped[datetime | None] = mapped_column(UtcDateTime())
    source_url: Mapped[str] = mapped_column(String(1000))
    source_kind: Mapped[str] = mapped_column(String(20))  # "official" or "secondary"
    summary: Mapped[str] = mapped_column(Text)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        _enum(VerificationStatus, "verification_status")
    )
    reviewer: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("raw_artifacts.artifact_id"))

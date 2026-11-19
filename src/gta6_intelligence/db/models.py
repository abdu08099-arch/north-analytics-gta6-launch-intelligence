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

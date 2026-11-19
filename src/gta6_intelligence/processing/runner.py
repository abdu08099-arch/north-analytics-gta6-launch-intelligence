"""Processes raw artifacts that have not been processed yet (or failed before)."""

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from gta6_intelligence.collection.raw_store import RawStore
from gta6_intelligence.db.models import (
    ArtifactProcessing,
    ProcessingStatus,
    QuarantinedRecord,
    RawArtifact,
)
from gta6_intelligence.processing.base import Processor
from gta6_intelligence.utils.hashing import sha256_hex
from gta6_intelligence.utils.time import utc_now

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessingSummary:
    source_id: str
    artifacts: int = 0
    rows_written: int = 0
    rows_rejected: int = 0
    failed: int = 0


def pending_artifacts(session: Session, source_id: str) -> list[RawArtifact]:
    done = select(ArtifactProcessing.artifact_id).where(
        ArtifactProcessing.status != ProcessingStatus.FAILED
    )
    return list(
        session.scalars(
            select(RawArtifact)
            .where(RawArtifact.source_id == source_id, RawArtifact.artifact_id.not_in(done))
            .order_by(RawArtifact.retrieved_at, RawArtifact.relative_path)
        )
    )


def process_pending(
    processor: Processor, *, session_factory: sessionmaker[Session], raw_store: RawStore
) -> ProcessingSummary:
    artifacts = rows = rejected = failed = 0
    with session_factory() as session:
        todo = pending_artifacts(session, processor.source_id)

    for artifact in todo:
        artifacts += 1
        with session_factory() as session:
            try:
                content = raw_store.read(artifact.relative_path)
                if sha256_hex(content) != artifact.sha256:
                    raise ValueError("checksum mismatch: raw file was changed after storage")
                outcome = processor.process(session, artifact, content)
                for reject in outcome.rejects:
                    session.add(
                        QuarantinedRecord(
                            artifact_id=artifact.artifact_id,
                            source_id=artifact.source_id,
                            reason=reject.reason,
                            record=reject.record,
                            quarantined_at=utc_now(),
                        )
                    )
                status = ProcessingStatus.PARTIAL if outcome.rejects else ProcessingStatus.PROCESSED
                _record(
                    session,
                    artifact,
                    processor,
                    status,
                    outcome.rows_written,
                    len(outcome.rejects),
                    None,
                )
                session.commit()
                rows += outcome.rows_written
                rejected += len(outcome.rejects)
            except Exception as exc:  # recorded, then the next artifact is processed
                session.rollback()
                failed += 1
                message = f"{type(exc).__name__}: {exc}"[:2000]
                _record(session, artifact, processor, ProcessingStatus.FAILED, 0, 0, message)
                session.commit()
                log.warning(
                    "artifact processing failed",
                    extra={"artifact_id": artifact.artifact_id, "error": message},
                )
    return ProcessingSummary(processor.source_id, artifacts, rows, rejected, failed)


def _record(
    session: Session,
    artifact: RawArtifact,
    processor: Processor,
    status: ProcessingStatus,
    written: int,
    rejected: int,
    error: str | None,
) -> None:
    row = session.get(ArtifactProcessing, artifact.artifact_id) or ArtifactProcessing(
        artifact_id=artifact.artifact_id
    )
    row.processor = processor.name
    row.processor_version = processor.version
    row.status = status
    row.processed_at = utc_now()
    row.rows_written = written
    row.rows_rejected = rejected
    row.error_message = error
    session.add(row)

"""Runs connectors and records every run in `collection_runs`.

Rules this module guarantees:
- Every attempt gets a run row, also when it fails (no silent failures).
- One failing connector never stops the others (PRD §15).
- Raw payloads are written to the raw store before the run is marked successful.
- If a run fails after some files were written, those files stay on disk
  (raw files are never deleted) and the run row says `failed`.
"""

import logging
import uuid
from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker

from gta6_intelligence import __version__
from gta6_intelligence.collection.raw_store import RawStore
from gta6_intelligence.connectors.base import BaseConnector, FetchContext
from gta6_intelligence.db.models import (
    CollectionMode,
    CollectionRun,
    RawArtifact,
    RunStatus,
    RunTrigger,
    Source,
)
from gta6_intelligence.utils.time import utc_now

log = logging.getLogger(__name__)

MAX_ERROR_LENGTH = 2000


@dataclass(frozen=True)
class RunResult:
    run_id: str
    source_id: str
    status: RunStatus
    artifact_count: int
    error_message: str | None = None


def run_connector(
    connector: BaseConnector,
    *,
    session_factory: sessionmaker[Session],
    raw_store: RawStore,
    trigger: RunTrigger = RunTrigger.MANUAL,
    mode: CollectionMode = CollectionMode.LIVE,
) -> RunResult:
    run_id = str(uuid.uuid4())
    started_at = utc_now()

    with session_factory() as session:
        if session.get(Source, connector.source_id) is None:
            raise ValueError(
                f"unknown source_id {connector.source_id!r}: run `gta6 db seed-sources` first"
            )
        session.add(
            CollectionRun(
                run_id=run_id,
                source_id=connector.source_id,
                trigger=trigger,
                collection_mode=mode,
                status=RunStatus.RUNNING,
                started_at=started_at,
                code_version=__version__,
                run_metadata={},
            )
        )
        session.commit()

    log.info("run started", extra={"run_id": run_id, "source_id": connector.source_id})
    ctx = FetchContext(run_id=run_id, started_at=started_at, collection_mode=mode)

    try:
        payloads = connector.fetch(ctx)
        artifacts = []
        for index, payload in enumerate(payloads):
            retrieved_at = utc_now()
            stored = raw_store.write(
                source_id=connector.source_id,
                run_id=run_id,
                index=index,
                extension=payload.extension,
                content=payload.content,
                retrieved_at=retrieved_at,
            )
            artifacts.append(
                RawArtifact(
                    artifact_id=str(uuid.uuid4()),
                    run_id=run_id,
                    source_id=connector.source_id,
                    relative_path=stored.relative_path,
                    sha256=stored.sha256,
                    size_bytes=stored.size_bytes,
                    media_type=payload.media_type,
                    retrieved_at=retrieved_at,
                    coverage_start=payload.coverage_start,
                    coverage_end=payload.coverage_end,
                    request_params=payload.request_params,
                )
            )
        with session_factory() as session:
            session.add_all(artifacts)
            session.commit()
    except Exception as exc:  # noqa: BLE001 - every failure must be recorded, whatever it is
        message = f"{type(exc).__name__}: {exc}"[:MAX_ERROR_LENGTH]
        _finish(session_factory, run_id, RunStatus.FAILED, fetched=0, error=message)
        log.exception("run failed", extra={"run_id": run_id, "source_id": connector.source_id})
        return RunResult(run_id, connector.source_id, RunStatus.FAILED, 0, message)

    _finish(session_factory, run_id, RunStatus.SUCCESS, fetched=len(artifacts), error=None)
    log.info(
        "run finished",
        extra={"run_id": run_id, "source_id": connector.source_id, "artifacts": len(artifacts)},
    )
    return RunResult(run_id, connector.source_id, RunStatus.SUCCESS, len(artifacts))


def run_connectors(
    connectors: Iterable[BaseConnector],
    **kwargs: object,
) -> list[RunResult]:
    """Run each connector in turn. Failures are recorded and do not stop the loop."""
    return [run_connector(c, **kwargs) for c in connectors]  # type: ignore[arg-type]


def _finish(
    session_factory: sessionmaker[Session],
    run_id: str,
    status: RunStatus,
    *,
    fetched: int,
    error: str | None,
) -> None:
    with session_factory() as session:
        run = session.get(CollectionRun, run_id)
        assert run is not None
        run.status = status
        run.finished_at = utc_now()
        run.fetched_count = fetched
        run.error_message = error
        session.commit()

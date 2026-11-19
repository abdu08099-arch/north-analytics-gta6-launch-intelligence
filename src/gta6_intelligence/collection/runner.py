"""Runs connectors and records every run in `collection_runs`.

Rules this module guarantees:
- Every attempt gets a run row, also when it fails (no silent failures).
- One failing connector never stops the others (PRD §15).
- Each raw payload is written to disk and recorded as soon as it arrives.
- If a run fails after some payloads were stored, they are kept and the run is
  `partial`; if nothing was stored it is `failed`.
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
    SourceStatus,
)
from gta6_intelligence.utils.time import utc_now

log = logging.getLogger(__name__)

MAX_ERROR_LENGTH = 2000

# Sources in these states may not be collected, whatever code exists for them.
NOT_COLLECTABLE = {
    SourceStatus.BLOCKED,
    SourceStatus.DEFERRED,
    SourceStatus.CONDITIONAL,
    SourceStatus.DISABLED,
}


class SourceNotCollectableError(RuntimeError):
    pass


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
        source = session.get(Source, connector.source_id)
        if source is None:
            raise ValueError(
                f"unknown source_id {connector.source_id!r}: run `gta6 db seed-sources` first"
            )
        if source.status in NOT_COLLECTABLE:
            raise SourceNotCollectableError(
                f"source {source.source_id!r} has status {source.status.value!r}; "
                "see docs/data/source-register.md"
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

    stored = 0
    try:
        for index, payload in enumerate(connector.fetch(ctx)):
            retrieved_at = utc_now()
            written = raw_store.write(
                source_id=connector.source_id,
                run_id=run_id,
                index=index,
                extension=payload.extension,
                content=payload.content,
                retrieved_at=retrieved_at,
            )
            with session_factory() as session:
                session.add(
                    RawArtifact(
                        artifact_id=str(uuid.uuid4()),
                        run_id=run_id,
                        source_id=connector.source_id,
                        relative_path=written.relative_path,
                        sha256=written.sha256,
                        size_bytes=written.size_bytes,
                        media_type=payload.media_type,
                        retrieved_at=retrieved_at,
                        coverage_start=payload.coverage_start,
                        coverage_end=payload.coverage_end,
                        request_params=payload.request_params,
                    )
                )
                session.commit()
            stored += 1
    except Exception as exc:  # every failure must be recorded, whatever it is
        message = f"{type(exc).__name__}: {exc}"[:MAX_ERROR_LENGTH]
        status = RunStatus.PARTIAL if stored else RunStatus.FAILED
        _finish(session_factory, run_id, status, fetched=stored, error=message)
        log.exception(
            "run did not complete",
            extra={"run_id": run_id, "source_id": connector.source_id, "artifacts": stored},
        )
        return RunResult(run_id, connector.source_id, status, stored, message)

    _finish(session_factory, run_id, RunStatus.SUCCESS, fetched=stored, error=None)
    log.info(
        "run finished",
        extra={"run_id": run_id, "source_id": connector.source_id, "artifacts": stored},
    )
    return RunResult(run_id, connector.source_id, RunStatus.SUCCESS, stored)


def run_connectors(
    connectors: Iterable[BaseConnector],
    **kwargs: object,
) -> list[RunResult]:
    """Run each connector in turn. Failures are recorded and do not stop the loop.

    A connector refused before it starts (unknown or non-collectable source) has
    no run row; it is reported with an empty run_id and the reason.
    """
    results = []
    for connector in connectors:
        try:
            results.append(run_connector(connector, **kwargs))  # type: ignore[arg-type]
        except (SourceNotCollectableError, ValueError) as exc:
            log.warning("run refused", extra={"source_id": connector.source_id})
            results.append(RunResult("", connector.source_id, RunStatus.FAILED, 0, str(exc)))
    return results


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

"""Run tracking with fake connectors. These are test doubles, not real sources."""

from datetime import UTC

from sqlalchemy import select

from gta6_intelligence.collection.runner import run_connector, run_connectors
from gta6_intelligence.connectors.base import BaseConnector, FetchContext, FetchedPayload
from gta6_intelligence.db.models import CollectionRun, RawArtifact, RunStatus
from gta6_intelligence.utils.hashing import sha256_hex

FIXTURE_PAYLOAD = b'{"fixture": true, "note": "FIXTURE - not real data"}'


class FakeOkConnector(BaseConnector):
    source_id = "gdelt"

    def fetch(self, ctx: FetchContext) -> list[FetchedPayload]:
        return [
            FetchedPayload(FIXTURE_PAYLOAD, "application/json", "json", {"query": "fixture"}),
            FetchedPayload(b"a,b\n1,2\n", "text/csv", "csv"),
        ]


class FakeBrokenConnector(BaseConnector):
    source_id = "google_trends"

    def fetch(self, ctx: FetchContext) -> list[FetchedPayload]:
        raise ConnectionError("source unreachable")


def test_successful_run_stores_artifacts_and_records_them(session_factory, raw_store) -> None:
    result = run_connector(FakeOkConnector(), session_factory=session_factory, raw_store=raw_store)

    assert result.status is RunStatus.SUCCESS
    assert result.artifact_count == 2
    with session_factory() as session:
        run = session.get(CollectionRun, result.run_id)
        artifacts = session.scalars(select(RawArtifact).order_by(RawArtifact.relative_path)).all()
    assert run.status is RunStatus.SUCCESS
    assert run.fetched_count == 2
    assert run.started_at.tzinfo is UTC and run.finished_at >= run.started_at
    assert artifacts[0].request_params == {"query": "fixture"}
    assert artifacts[0].sha256 == sha256_hex(FIXTURE_PAYLOAD)
    assert raw_store.read(artifacts[0].relative_path) == FIXTURE_PAYLOAD


def test_failed_run_is_recorded_not_raised(session_factory, raw_store) -> None:
    result = run_connector(
        FakeBrokenConnector(), session_factory=session_factory, raw_store=raw_store
    )

    assert result.status is RunStatus.FAILED
    with session_factory() as session:
        run = session.get(CollectionRun, result.run_id)
    assert run.status is RunStatus.FAILED
    assert run.error_message == "ConnectionError: source unreachable"
    assert run.finished_at is not None


def test_one_failing_connector_does_not_stop_the_others(session_factory, raw_store) -> None:
    results = run_connectors(
        [FakeBrokenConnector(), FakeOkConnector()],
        session_factory=session_factory,
        raw_store=raw_store,
    )
    assert [r.status for r in results] == [RunStatus.FAILED, RunStatus.SUCCESS]


def test_unknown_source_is_refused(session_factory, raw_store) -> None:
    class Unknown(FakeOkConnector):
        source_id = "not_in_catalog"

    try:
        run_connector(Unknown(), session_factory=session_factory, raw_store=raw_store)
    except ValueError as exc:
        assert "seed-sources" in str(exc)
    else:
        raise AssertionError("expected ValueError")

"""Raw artifact -> tables, using labelled fixtures. No network."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import func, select

from gta6_intelligence.collection.runner import run_connector
from gta6_intelligence.connectors.base import BaseConnector, FetchContext, FetchedPayload
from gta6_intelligence.connectors.files import EventLedgerConnector, GoogleTrendsInboxConnector
from gta6_intelligence.db.models import (
    ArtifactProcessing,
    EventMilestone,
    NewsArticle,
    NewsCoveragePoint,
    ProcessingStatus,
    QuarantinedRecord,
    RawArtifact,
    RunStatus,
    SearchObservation,
    VerificationStatus,
)
from gta6_intelligence.processing.events import EventLedgerProcessor
from gta6_intelligence.processing.gdelt import GdeltProcessor, story_key
from gta6_intelligence.processing.google_trends import GoogleTrendsCsvProcessor
from gta6_intelligence.processing.runner import process_pending
from gta6_intelligence.reporting.products import build_news_coverage_daily, build_status

FIXTURES = Path(__file__).parents[1] / "fixtures"
REPO_LEDGER = Path(__file__).parents[2] / "data" / "reference"
TIMELINE = (FIXTURES / "FIXTURE_gdelt_timeline.json").read_bytes()
ARTLIST = (FIXTURES / "FIXTURE_gdelt_artlist.json").read_bytes()
DAY = datetime(2026, 11, 17, tzinfo=UTC)


class FakeGdelt(BaseConnector):
    """Replays fixture payloads as if they came from GDELT."""

    source_id = "gdelt"

    def __init__(self, payloads):
        self._payloads = payloads

    def fetch(self, ctx: FetchContext):
        yield from self._payloads


def _timeline(content=TIMELINE, start=DAY, days=2):
    return FetchedPayload(
        content,
        "application/json",
        "json",
        {"mode": "timelinevolraw", "query": "FIXTURE"},
        start,
        start + timedelta(days=days),
    )


def _artlist(content=ARTLIST):
    return FetchedPayload(content, "application/json", "json", {"mode": "artlist", "query": "Q"})


def _collect_and_process(connector, processor, session_factory, raw_store):
    run = run_connector(connector, session_factory=session_factory, raw_store=raw_store)
    summary = process_pending(processor, session_factory=session_factory, raw_store=raw_store)
    return run, summary


# --- GDELT -------------------------------------------------------------------------------


def test_gdelt_timeline_points_are_stored_at_source_resolution(session_factory, raw_store):
    _, summary = _collect_and_process(
        FakeGdelt([_timeline()]), GdeltProcessor(), session_factory, raw_store
    )
    assert summary.rows_written == 48 and summary.rows_rejected == 0
    with session_factory() as s:
        first = s.scalars(
            select(NewsCoveragePoint).order_by(NewsCoveragePoint.period_start)
        ).first()
    assert first.period_start == DAY and first.resolution == "hour"
    assert first.matching_articles == 0 and first.total_monitored == 1000


def test_gdelt_empty_timeline_is_zero_rows_not_zero_coverage(session_factory, raw_store):
    empty = json.dumps({"query_details": {}, "timeline": []}).encode()
    _, summary = _collect_and_process(
        FakeGdelt([_timeline(empty), _artlist(b"{}")]), GdeltProcessor(), session_factory, raw_store
    )
    assert summary.rows_written == 0 and summary.failed == 0


def test_gdelt_bad_points_are_quarantined_with_reason(session_factory, raw_store):
    bad = json.dumps(
        {
            "timeline": [
                {
                    "data": [
                        {"date": "20261117T000000Z", "value": 5, "norm": 10},
                        {"date": "not-a-date", "value": 5},
                        {"date": "20261117T010000Z", "value": -1},
                    ]
                }
            ]
        }
    ).encode()
    _, summary = _collect_and_process(
        FakeGdelt([_timeline(bad)]), GdeltProcessor(), session_factory, raw_store
    )
    assert (summary.rows_written, summary.rows_rejected) == (1, 2)
    with session_factory() as s:
        assert s.scalar(select(func.count()).select_from(QuarantinedRecord)) == 2
        assert s.scalars(select(ArtifactProcessing)).one().status is ProcessingStatus.PARTIAL


def test_gdelt_articles_are_deduplicated_by_url_across_runs(session_factory, raw_store):
    _collect_and_process(FakeGdelt([_artlist()]), GdeltProcessor(), session_factory, raw_store)
    _collect_and_process(FakeGdelt([_artlist()]), GdeltProcessor(), session_factory, raw_store)
    with session_factory() as s:
        assert s.scalar(select(func.count()).select_from(NewsArticle)) == 2


def test_story_key_groups_syndicated_copies():
    seen = datetime(2026, 11, 18, 17, 30, tzinfo=UTC)
    assert story_key("Schools offer pupils incentives!", seen) == story_key(
        "schools offer pupils incentives", seen + timedelta(hours=2)
    )
    assert story_key("A", seen) != story_key("A", seen + timedelta(days=1))


def test_processing_is_idempotent(session_factory, raw_store):
    _collect_and_process(FakeGdelt([_timeline()]), GdeltProcessor(), session_factory, raw_store)
    again = process_pending(GdeltProcessor(), session_factory=session_factory, raw_store=raw_store)
    assert again.artifacts == 0


def test_changed_raw_file_fails_processing_and_is_retried_later(session_factory, raw_store):
    run_connector(FakeGdelt([_timeline()]), session_factory=session_factory, raw_store=raw_store)
    with session_factory() as s:
        path = raw_store.raw_dir / s.scalars(select(RawArtifact)).one().relative_path
    original = path.read_bytes()
    path.write_bytes(b"tampered")
    first = process_pending(GdeltProcessor(), session_factory=session_factory, raw_store=raw_store)
    assert first.failed == 1
    with session_factory() as s:
        assert "checksum mismatch" in s.scalars(select(ArtifactProcessing)).one().error_message
    path.write_bytes(original)
    second = process_pending(GdeltProcessor(), session_factory=session_factory, raw_store=raw_store)
    assert second.failed == 0 and second.rows_written == 48


def test_daily_coverage_uses_latest_snapshot_and_never_adds_snapshots(session_factory, raw_store):
    older = TIMELINE.replace(b'"norm": 1000', b'"norm": 500')
    _collect_and_process(
        FakeGdelt([_timeline(older)]), GdeltProcessor(), session_factory, raw_store
    )
    _collect_and_process(FakeGdelt([_timeline()]), GdeltProcessor(), session_factory, raw_store)
    with session_factory() as s:
        product = build_news_coverage_daily(s)
    assert product["kind"] == "derived"
    day1, day2 = product["data"]
    assert day1["date"] == "2026-11-17"
    assert day1["matching_articles"] == sum(range(24))  # one snapshot, not two added up
    assert day1["total_monitored"] == 24 * 1000  # from the newer snapshot
    assert day1["complete"] is True
    assert day2["matching_articles"] == 2 * sum(range(24))


# --- Event ledger --------------------------------------------------------------------------


def test_committed_event_ledger_is_valid(session_factory, raw_store):
    run, summary = _collect_and_process(
        EventLedgerConnector(REPO_LEDGER), EventLedgerProcessor(), session_factory, raw_store
    )
    assert run.status is RunStatus.SUCCESS
    assert summary.rows_rejected == 0, "fix data/reference/event_milestones.csv"
    with session_factory() as s:
        release = s.get(EventMilestone, "2026-11-19-release")
    assert release.event_date.isoformat() == "2026-11-19"


def test_unchanged_ledger_is_not_stored_twice(session_factory, raw_store):
    run_connector(
        EventLedgerConnector(REPO_LEDGER), session_factory=session_factory, raw_store=raw_store
    )
    second = run_connector(
        EventLedgerConnector(REPO_LEDGER), session_factory=session_factory, raw_store=raw_store
    )
    assert second.artifact_count == 0


LEDGER_HEADER = (
    "event_id,event_name,event_type,event_date,published_at,source_url,source_kind,"
    "summary,verification_status,reviewer,notes\n"
)


def _ledger(tmp_path, *lines):
    (tmp_path / "event_milestones.csv").write_text(LEDGER_HEADER + "".join(lines))
    return EventLedgerConnector(tmp_path)


def test_new_ledger_version_replaces_events_and_rules_are_enforced(
    session_factory, raw_store, tmp_path
):
    ok = "fixture-event-one,FIXTURE event,trailer,2026-01-01,,https://example.com,secondary,FIXTURE summary text,unverified,,\n"
    _collect_and_process(_ledger(tmp_path, ok), EventLedgerProcessor(), session_factory, raw_store)

    replaced = "fixture-event-two,FIXTURE event two,release,2026-02-01,2026-02-01T10:00:00Z,https://example.com,official,FIXTURE summary text,verified,Abdul,\n"
    verified_without_reviewer = "fixture-event-three,FIXTURE three,release,2026-03-01,,https://example.com,secondary,FIXTURE summary text,verified,,\n"
    naive_time = "fixture-event-four,FIXTURE four,release,2026-03-01,2026-03-01T10:00:00,https://example.com,official,FIXTURE summary text,unverified,,\n"
    _, summary = _collect_and_process(
        _ledger(tmp_path, replaced, verified_without_reviewer, naive_time),
        EventLedgerProcessor(),
        session_factory,
        raw_store,
    )
    assert (summary.rows_written, summary.rows_rejected) == (1, 2)
    with session_factory() as s:
        ids = set(s.scalars(select(EventMilestone.event_id)))
        two = s.get(EventMilestone, "fixture-event-two")
    assert ids == {"fixture-event-two"}  # event one was removed from the file, so from the table
    assert two.verification_status is VerificationStatus.VERIFIED
    assert two.published_at == datetime(2026, 2, 1, 10, tzinfo=UTC)


# --- Google Trends -------------------------------------------------------------------------


def _inbox(tmp_path, name, content):
    inbox = tmp_path / "inbox"
    inbox.mkdir(exist_ok=True)
    (inbox / name).write_bytes(content)
    return GoogleTrendsInboxConnector(inbox)


def test_trends_export_is_parsed_with_missing_and_below_one_kept_apart(
    session_factory, raw_store, tmp_path
):
    connector = _inbox(
        tmp_path,
        "2026-11-19_DK_past-90-days_term-gta-6_allan.csv",
        (FIXTURES / "FIXTURE_trends_daily.csv").read_bytes(),
    )
    _, summary = _collect_and_process(
        connector, GoogleTrendsCsvProcessor(), session_factory, raw_store
    )
    assert (summary.rows_written, summary.rows_rejected) == (4, 1)  # "banana" quarantined
    with session_factory() as s:
        rows = s.scalars(select(SearchObservation).order_by(SearchObservation.period_start)).all()
    assert [(r.interest_value, r.value_flag) for r in rows] == [
        (12, None),
        (None, "<1"),
        (None, "missing"),
        (100, None),
    ]
    assert rows[0].geo == "DK" and rows[0].granularity == "day" and rows[0].query == "gta-6"
    assert rows[0].series_label == "FIXTURE GTA 6: (Denmark)"
    assert rows[0].export_window == "past-90-days"


def test_trends_badly_named_files_are_not_imported(session_factory, raw_store, tmp_path):
    connector = _inbox(tmp_path, "multiTimeline.csv", b"Day,x\n2026-11-19,1\n")
    run = run_connector(connector, session_factory=session_factory, raw_store=raw_store)
    assert run.status is RunStatus.FAILED and "multiTimeline.csv" in run.error_message


def test_trends_unknown_layout_fails_visibly_without_rows(session_factory, raw_store, tmp_path):
    connector = _inbox(
        tmp_path,
        "2026-11-19_WW_past-7-days_topic-gta6_allan.csv",
        b"Something new,from Google\n1,2\n",
    )
    _, summary = _collect_and_process(
        connector, GoogleTrendsCsvProcessor(), session_factory, raw_store
    )
    assert summary.failed == 1 and summary.rows_written == 0
    with session_factory() as s:
        assert s.scalar(select(func.count()).select_from(SearchObservation)) == 0


def test_trends_hourly_export(session_factory, raw_store, tmp_path):
    content = b"Time,FIXTURE GTA 6: (Worldwide)\n2026-11-18T22,40\n2026-11-18T23,55\n"
    connector = _inbox(tmp_path, "2026-11-19_WW_past-7-days_topic-gta6_allan.csv", content)
    _collect_and_process(connector, GoogleTrendsCsvProcessor(), session_factory, raw_store)
    with session_factory() as s:
        rows = s.scalars(select(SearchObservation).order_by(SearchObservation.period_start)).all()
    assert [r.granularity for r in rows] == ["hour", "hour"]
    assert rows[1].period_start == datetime(2026, 11, 18, 23, tzinfo=UTC)


# --- Status product -----------------------------------------------------------------------


def test_status_product_reports_freshness_and_quality(session_factory, raw_store):
    _collect_and_process(FakeGdelt([_timeline()]), GdeltProcessor(), session_factory, raw_store)
    with session_factory() as s:
        status = {row["source_id"]: row for row in build_status(s)["data"]}
    assert status["gdelt"]["last_run"]["status"] == "success"
    assert status["gdelt"]["last_success_at"] is not None
    assert status["gdelt"]["processing"] == {"processed": 1}
    assert status["reddit"]["status"] == "blocked" and status["reddit"]["last_run"] is None


@pytest.mark.parametrize(
    "name", ["status.json", "events.json", "news_coverage_daily.json", "search_interest.json"]
)
def test_publish_writes_every_product(session_factory, tmp_path, name):
    from gta6_intelligence.reporting.products import publish

    with session_factory() as s:
        paths = publish(s, tmp_path / "products")
    payload = json.loads((tmp_path / "products" / name).read_text())
    assert payload["generated_at"] and "data" in payload
    assert len(paths) == 4


def test_search_interest_product_keeps_snapshots_apart(session_factory, raw_store, tmp_path):
    from gta6_intelligence.reporting.products import build_search_interest

    connector = _inbox(
        tmp_path,
        "2026-11-19_DK_past-90-days_term-gta-6_allan.csv",
        (FIXTURES / "FIXTURE_trends_daily.csv").read_bytes(),
    )
    _collect_and_process(connector, GoogleTrendsCsvProcessor(), session_factory, raw_store)
    with session_factory() as s:
        product = build_search_interest(s)
    (snap,) = product["data"]
    assert snap["geo"] == "DK" and snap["window"] == "past-90-days"
    (series,) = snap["series"]
    assert [p["value"] for p in series["points"]] == [12, None, None, 100]
    assert [p["flag"] for p in series["points"]] == [None, "<1", "missing", None]

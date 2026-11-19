from sqlalchemy import func, select

from gta6_intelligence.db.models import Source, SourceStatus
from gta6_intelligence.sources.catalog import CATALOG, seed_sources


def test_all_six_prd_sources_are_seeded(session_factory) -> None:
    with session_factory() as session:
        ids = set(session.scalars(select(Source.source_id)))
    assert ids == {"google_trends", "event_ledger", "gdelt", "youtube", "reddit", "x"}


def test_seeding_twice_does_not_duplicate(session_factory) -> None:
    with session_factory() as session:
        seed_sources(session)
        assert session.scalar(select(func.count()).select_from(Source)) == len(CATALOG)


def test_reddit_is_blocked(session_factory) -> None:
    with session_factory() as session:
        assert session.get(Source, "reddit").status is SourceStatus.BLOCKED

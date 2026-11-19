from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect

from gta6_intelligence.db import migrate
from gta6_intelligence.db.models import Base
from gta6_intelligence.db.session import make_engine


def test_upgrade_creates_tables(settings) -> None:
    migrate.upgrade(settings.database_url)
    tables = set(inspect(make_engine(settings.database_url)).get_table_names())
    assert {"sources", "collection_runs", "raw_artifacts", "alembic_version"} <= tables


def test_migrations_match_the_models(settings) -> None:
    """Fails if someone changes models.py without adding a migration."""
    migrate.upgrade(settings.database_url)
    with make_engine(settings.database_url).connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []


def test_upgrade_is_repeatable(settings) -> None:
    migrate.upgrade(settings.database_url)
    migrate.upgrade(settings.database_url)

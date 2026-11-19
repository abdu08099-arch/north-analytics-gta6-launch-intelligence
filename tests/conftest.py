"""Shared test setup: every test gets its own temporary database and data folder.

By default tests use a fresh SQLite file. Set TEST_DATABASE_URL to a PostgreSQL
URL to run the same tests against PostgreSQL; the schema is wiped before each test,
so only ever point it at a throwaway test database.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from gta6_intelligence.collection.raw_store import RawStore
from gta6_intelligence.config.settings import Settings
from gta6_intelligence.db import migrate
from gta6_intelligence.db.session import make_engine, make_session_factory
from gta6_intelligence.sources.catalog import seed_sources


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        return f"sqlite:///{tmp_path / 'test.db'}"
    engine = make_engine(url)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    engine.dispose()
    return url


@pytest.fixture
def settings(tmp_path: Path, database_url: str) -> Settings:
    return Settings(
        app_env="test",
        data_dir=tmp_path / "data",
        database_url=database_url,
        _env_file=None,  # never read a developer's real .env in tests
    )


@pytest.fixture
def session_factory(settings: Settings) -> Iterator[sessionmaker[Session]]:
    migrate.upgrade(settings.database_url)
    engine = make_engine(settings.database_url)
    factory = make_session_factory(engine)
    with factory() as session:
        seed_sources(session)
    yield factory
    engine.dispose()


@pytest.fixture
def raw_store(settings: Settings) -> RawStore:
    return RawStore(settings.raw_dir)

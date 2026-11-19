import pytest

from gta6_intelligence import cli
from gta6_intelligence.config import settings as settings_module


@pytest.fixture
def env(tmp_path, monkeypatch, database_url):
    monkeypatch.chdir(tmp_path)  # no .env here, and data/ is created under tmp
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    settings_module.get_settings.cache_clear()
    yield
    settings_module.get_settings.cache_clear()


def test_setup_flow_from_empty_folder(env, capsys) -> None:
    assert cli.main(["db", "upgrade"]) == cli.EXIT_OK
    assert cli.main(["db", "seed-sources"]) == cli.EXIT_OK
    assert cli.main(["sources"]) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert "reddit" in out and "blocked" in out


def test_collect_unknown_source_is_a_usage_error(env) -> None:
    cli.main(["db", "upgrade"])
    assert cli.main(["collect", "--source", "reddit"]) == cli.EXIT_USAGE


def test_runs_on_empty_database(env, capsys) -> None:
    cli.main(["db", "upgrade"])
    assert cli.main(["runs"]) == cli.EXIT_OK
    assert "No runs recorded yet." in capsys.readouterr().out

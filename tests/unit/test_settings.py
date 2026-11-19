from pydantic import SecretStr

from gta6_intelligence.config.settings import Settings


def test_defaults_point_to_local_sqlite() -> None:
    s = Settings(_env_file=None)
    assert s.database_url.startswith("sqlite:///")
    assert s.raw_dir.as_posix().endswith("data/raw")


def test_environment_variables_override_defaults(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u@localhost/db")
    monkeypatch.setenv("APP_ENV", "production")
    s = Settings(_env_file=None)
    assert s.database_url == "postgresql+psycopg://u@localhost/db"
    assert s.app_env == "production"


def test_secrets_are_hidden_when_printed() -> None:
    s = Settings(_env_file=None, youtube_api_key=SecretStr("very-secret-value"))
    assert "very-secret-value" not in repr(s)
    assert "very-secret-value" not in str(s.model_dump())
    assert s.secret_values() == ["very-secret-value"]


def test_empty_secrets_are_ignored() -> None:
    assert Settings(_env_file=None, x_bearer_token=SecretStr("")).secret_values() == []

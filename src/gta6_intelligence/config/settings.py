"""Application settings.

Values come from environment variables (or a local `.env` file that is never
committed). Secrets are typed as `SecretStr`, so they are hidden when a
settings object is printed or logged.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    # Root folder for local data (raw artifacts, SQLite file, inbox for manual exports).
    data_dir: Path = Path("data")
    # SQLite locally, PostgreSQL in production (Decision 0001).
    database_url: str = "sqlite:///data/gta6.db"

    # Optional credentials. Leave empty until a source is approved.
    youtube_api_key: SecretStr | None = Field(default=None)
    x_bearer_token: SecretStr | None = Field(default=None)
    google_trends_api_key: SecretStr | None = Field(default=None)

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def products_dir(self) -> Path:
        return self.data_dir / "products"

    @property
    def lock_path(self) -> Path:
        return self.data_dir / ".collect.lock"

    def secret_values(self) -> list[str]:
        """Plain values of every configured secret, for log redaction."""
        secrets = (self.youtube_api_key, self.x_bearer_token, self.google_trends_api_key)
        return [s.get_secret_value() for s in secrets if s and s.get_secret_value()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Structured JSON logging with secret redaction.

Every log line is one JSON object, so run logs can be searched and parsed.
Known secret values and key=value style credentials are replaced with
"[REDACTED]" in the final line, including exception tracebacks
(Charter §13.1: never print secrets in logs).
"""

import json
import logging
import re
from collections.abc import Iterable

from gta6_intelligence.utils.time import utc_now

REDACTED = "[REDACTED]"

# Catches things like "api_key=abc123", "token: abc", "Authorization: Bearer abc".
_KEY_VALUE_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password|bearer)\b(\s*[:=]\s*|\s+)([^\s&\"',]+)"
)

# Attributes every LogRecord has; anything else came from `extra={...}`.
_STANDARD_ATTRS = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class Redactor:
    def __init__(self, secrets: Iterable[str] = ()) -> None:
        # Longest first, so a secret that contains another is fully replaced.
        self._secrets = sorted((s for s in secrets if s), key=len, reverse=True)

    def __call__(self, text: str) -> str:
        for secret in self._secrets:
            text = text.replace(secret, REDACTED)
        return _KEY_VALUE_PATTERN.sub(lambda m: f"{m.group(1)}{m.group(2)}{REDACTED}", text)


class JsonFormatter(logging.Formatter):
    def __init__(self, redactor: Redactor | None = None) -> None:
        super().__init__()
        self._redact = redactor or Redactor()

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": utc_now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in vars(record).items():
            if key not in _STANDARD_ATTRS and key not in payload:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return self._redact(json.dumps(payload, default=str, ensure_ascii=False))


def configure_logging(level: str = "INFO", secrets: Iterable[str] = ()) -> None:
    """Send JSON logs to stderr. Safe to call more than once."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(Redactor(secrets)))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())

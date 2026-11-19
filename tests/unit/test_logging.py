import json
import logging

from gta6_intelligence.utils.logging import REDACTED, JsonFormatter, Redactor


def _format(record_msg: str, secrets=(), exc_info=None, **extra) -> dict:
    record = logging.makeLogRecord(
        {"name": "t", "levelname": "INFO", "msg": record_msg, "exc_info": exc_info, **extra}
    )
    return json.loads(JsonFormatter(Redactor(secrets)).format(record))


def test_output_is_one_json_object_with_extra_fields() -> None:
    out = _format("run started", run_id="abc")
    assert out["message"] == "run started"
    assert out["run_id"] == "abc"
    assert out["ts"].endswith("+00:00")


def test_known_secret_values_are_redacted_everywhere() -> None:
    out = _format("calling with sk-123456", secrets=["sk-123456"], url="https://x?key=sk-123456")
    assert "sk-123456" not in json.dumps(out)
    assert REDACTED in out["message"]


def test_key_value_credentials_are_redacted_even_if_unknown() -> None:
    redact = Redactor()
    assert redact("api_key=abc123&q=gta") == f"api_key={REDACTED}&q=gta"
    assert redact("Authorization: Bearer xyz") == f"Authorization: Bearer {REDACTED}"
    assert redact("token: t0k3n") == f"token: {REDACTED}"


def test_secrets_in_tracebacks_are_redacted() -> None:
    try:
        raise RuntimeError("failed with sk-999")
    except RuntimeError:
        import sys

        out = _format("boom", secrets=["sk-999"], exc_info=sys.exc_info())
    assert "sk-999" not in out["exception"]

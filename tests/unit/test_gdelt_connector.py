"""GDELT connector against a mocked HTTP server. No network calls are made."""

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from gta6_intelligence.connectors.base import FetchContext
from gta6_intelligence.connectors.gdelt import (
    MAX_ATTEMPTS,
    MIN_SECONDS_BETWEEN_REQUESTS,
    GdeltConnector,
    GdeltError,
)
from gta6_intelligence.db.models import CollectionMode

ARTLIST = (Path(__file__).parents[1] / "fixtures" / "FIXTURE_gdelt_artlist.json").read_bytes()
TIMELINE = json.dumps({"FIXTURE": True, "timeline": []}).encode()
CTX = FetchContext("run-1", datetime(2026, 11, 19, 7, 15, tzinfo=UTC), CollectionMode.LIVE)


def _connector(handler):
    sleeps: list[float] = []
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return GdeltConnector(client=client, sleep=sleeps.append), sleeps


def _ok(request: httpx.Request) -> httpx.Response:
    mode = request.url.params["mode"]
    return httpx.Response(200, content=TIMELINE if mode == "timelinevolraw" else ARTLIST)


def test_plans_one_timeline_and_four_article_windows_for_yesterday() -> None:
    plans = GdeltConnector(client=httpx.Client()).plan_requests(CTX)
    modes = [p["mode"] for p, _, _ in plans]
    assert modes == ["timelinevolraw", "artlist", "artlist", "artlist", "artlist"]
    timeline, t_start, t_end = plans[0]
    assert (t_start, t_end) == (
        datetime(2026, 11, 12, tzinfo=UTC),
        datetime(2026, 11, 19, tzinfo=UTC),
    )
    assert timeline["startdatetime"] == "20261112000000"
    windows = [(s, e) for _, s, e in plans[1:]]
    assert windows[0][0] == datetime(2026, 11, 18, 0, tzinfo=UTC)
    assert windows[-1][1] == datetime(2026, 11, 19, 0, tzinfo=UTC)


def test_fetch_returns_raw_bytes_with_params_and_respects_rate_limit() -> None:
    connector, sleeps = _connector(_ok)
    payloads = list(connector.fetch(CTX))
    assert len(payloads) == 5
    assert payloads[1].content == ARTLIST  # stored exactly as received
    assert payloads[1].request_params["mode"] == "artlist"
    assert payloads[1].request_params["url"].startswith("https://api.gdeltproject.org/")
    assert (
        sleeps == [MIN_SECONDS_BETWEEN_REQUESTS] * 4
    )  # a pause before every request but the first


def test_retries_after_429_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, text="Please limit requests to one every 5 seconds")
        return _ok(request)

    connector, _ = _connector(handler)
    assert len(list(connector.fetch(CTX))) == 5
    assert calls["n"] == 6


def test_gives_up_after_bounded_attempts() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(429)

    connector, _ = _connector(handler)
    with pytest.raises(GdeltError, match="gave up"):
        list(connector.fetch(CTX))
    assert calls["n"] == MAX_ATTEMPTS


def test_plain_text_error_with_http_200_is_not_stored_as_data() -> None:
    connector, _ = _connector(lambda r: httpx.Response(200, text="Your query was too short"))
    with pytest.raises(GdeltError, match="non-JSON"):
        list(connector.fetch(CTX))


def test_network_errors_are_retried_then_reported() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection reset")

    connector, _ = _connector(handler)
    with pytest.raises(GdeltError, match="network error"):
        list(connector.fetch(CTX))

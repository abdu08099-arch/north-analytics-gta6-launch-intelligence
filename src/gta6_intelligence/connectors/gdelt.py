"""GDELT DOC 2.0 connector: news coverage about GTA VI.

What it fetches each run (all stored unchanged as raw JSON):
1. One coverage timeline (`timelinevolraw`) for the last 7 days: matching
   article counts plus the total number of articles GDELT monitored, so both
   counts and the share of coverage can be derived later. Overlapping windows
   are separate snapshots and are never blindly appended (PRD §8).
2. Article lists (`artlist`) for the previous UTC day, split into four 6-hour
   windows, because GDELT returns at most 250 articles per request.

Rules (docs/data/source-register.md §5):
- GDELT asks for at most one request every 5 seconds; it answers faster
  requests with HTTP 429. We wait 6 seconds between requests.
- Bounded retries on 429 and network errors, then the run fails visibly.
- GDELT sometimes answers HTTP 200 with a plain-text error. Anything that is
  not JSON is treated as a failure, never stored as data.
- We store metadata only (URL, title, domain, language, country). We never
  fetch article bodies.
"""

import json
import time
from collections.abc import Callable, Iterator
from datetime import datetime, timedelta

import httpx

from gta6_intelligence import __version__
from gta6_intelligence.connectors.base import BaseConnector, FetchContext, FetchedPayload
from gta6_intelligence.utils.time import ensure_utc

API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
QUERY = '("GTA 6" OR "GTA VI" OR "Grand Theft Auto VI" OR "Grand Theft Auto 6")'
USER_AGENT = (
    f"north-analytics-gta6/{__version__} "
    "(+https://github.com/abdu08099-arch/north-analytics-gta6-launch-intelligence)"
)

MIN_SECONDS_BETWEEN_REQUESTS = 6.0
MAX_ATTEMPTS = 3
RETRY_WAIT_SECONDS = 15.0
TIMELINE_DAYS = 7
ARTICLE_WINDOW_HOURS = 6
MAX_RECORDS = 250


class GdeltError(RuntimeError):
    pass


def _gdelt_time(value: datetime) -> str:
    return ensure_utc(value).strftime("%Y%m%d%H%M%S")


class GdeltConnector(BaseConnector):
    source_id = "gdelt"

    def __init__(
        self,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
        query: str = QUERY,
    ) -> None:
        self._client = client or httpx.Client(
            timeout=60.0, headers={"User-Agent": USER_AGENT}, follow_redirects=True
        )
        self._sleep = sleep
        self._query = query
        self._requests_made = 0

    def plan_requests(self, ctx: FetchContext) -> list[tuple[dict[str, str], datetime, datetime]]:
        """The exact requests for this run: (params, coverage_start, coverage_end)."""
        today = ensure_utc(ctx.started_at).replace(hour=0, minute=0, second=0, microsecond=0)
        timeline_start = today - timedelta(days=TIMELINE_DAYS)
        plans = [
            (
                {
                    "query": self._query,
                    "mode": "timelinevolraw",
                    "startdatetime": _gdelt_time(timeline_start),
                    "enddatetime": _gdelt_time(today),
                    "format": "json",
                },
                timeline_start,
                today,
            )
        ]
        yesterday = today - timedelta(days=1)
        for offset in range(0, 24, ARTICLE_WINDOW_HOURS):
            start = yesterday + timedelta(hours=offset)
            end = start + timedelta(hours=ARTICLE_WINDOW_HOURS)
            plans.append(
                (
                    {
                        "query": self._query,
                        "mode": "artlist",
                        "maxrecords": str(MAX_RECORDS),
                        "sort": "datedesc",
                        "startdatetime": _gdelt_time(start),
                        "enddatetime": _gdelt_time(end),
                        "format": "json",
                    },
                    start,
                    end,
                )
            )
        return plans

    def fetch(self, ctx: FetchContext) -> Iterator[FetchedPayload]:
        for params, start, end in self.plan_requests(ctx):
            yield FetchedPayload(
                content=self._get(params),
                media_type="application/json",
                extension="json",
                request_params={"url": API_URL, **params},
                coverage_start=start,
                coverage_end=end,
            )

    def _get(self, params: dict[str, str]) -> bytes:
        last_problem = "no attempt made"
        for attempt in range(1, MAX_ATTEMPTS + 1):
            if self._requests_made:
                self._sleep(MIN_SECONDS_BETWEEN_REQUESTS)
            self._requests_made += 1
            try:
                response = self._client.get(API_URL, params=params)
            except httpx.TransportError as exc:
                last_problem = f"network error: {type(exc).__name__}"
            else:
                if response.status_code == 429:
                    last_problem = "HTTP 429 (rate limited)"
                elif response.status_code != 200:
                    raise GdeltError(f"HTTP {response.status_code} for mode={params['mode']}")
                else:
                    return self._require_json(response.content, params["mode"])
            if attempt < MAX_ATTEMPTS:
                self._sleep(RETRY_WAIT_SECONDS * attempt)
        raise GdeltError(f"gave up after {MAX_ATTEMPTS} attempts: {last_problem}")

    @staticmethod
    def _require_json(content: bytes, mode: str) -> bytes:
        try:
            json.loads(content)
        except ValueError as exc:
            snippet = content[:200].decode("utf-8", errors="replace").strip()
            raise GdeltError(f"non-JSON response for mode={mode}: {snippet!r}") from exc
        return content

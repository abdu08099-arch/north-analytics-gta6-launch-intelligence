"""Parse stored GDELT responses into `news_coverage_points` and `news_articles`.

Timeline format (mode=timelinevolraw), confirmed 2026-11-19 against a live
response and the `gdeltdoc` client:
    {"query_details": {"title": ..., "date_resolution": "hour"},
     "timeline": [{"series": ..., "data": [{"date": "20261118T000000Z",
                                             "value": <matching>, "norm": <monitored>}]}]}
An empty result is `{}` or `"timeline": []`: that is zero rows, not zero coverage.

Article list format (mode=artlist):
    {"articles": [{"url", "title", "seendate": "20261118T173000Z", "domain",
                   "language", "sourcecountry", ...}]}
"""

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from gta6_intelligence.db.models import NewsArticle, NewsCoveragePoint, RawArtifact
from gta6_intelligence.processing.base import Processor, ProcessOutcome, Reject

GDELT_TIME = "%Y%m%dT%H%M%SZ"


def parse_gdelt_time(value: str) -> datetime:
    return datetime.strptime(value, GDELT_TIME).replace(tzinfo=UTC)


def story_key(title: str, seen_at: datetime) -> str:
    """Same normalised title on the same UTC day -> same key. Used to spot syndication."""
    normalised = re.sub(r"[^\w]+", " ", title.casefold()).strip()
    return hashlib.sha256(f"{seen_at:%Y-%m-%d}|{normalised}".encode()).hexdigest()[:32]


class TimelinePoint(BaseModel):
    date: datetime
    value: int = Field(ge=0)
    norm: int | None = Field(default=None, ge=0)

    @field_validator("date", mode="before")
    @classmethod
    def _date(cls, v: Any) -> datetime:
        return parse_gdelt_time(v)


class ArticleRecord(BaseModel):
    url: str = Field(min_length=8, max_length=2000)
    title: str
    seendate: datetime
    domain: str = Field(min_length=1)
    language: str | None = None
    sourcecountry: str | None = None

    @field_validator("seendate", mode="before")
    @classmethod
    def _seen(cls, v: Any) -> datetime:
        return parse_gdelt_time(v)

    @field_validator("url")
    @classmethod
    def _http(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("url must be http(s)")
        return v


class GdeltProcessor(Processor):
    source_id = "gdelt"
    name = "gdelt"
    version = "1"

    def process(self, session: Session, artifact: RawArtifact, content: bytes) -> ProcessOutcome:
        data = json.loads(content)
        mode = artifact.request_params.get("mode")
        query = artifact.request_params.get("query", "")
        if mode == "timelinevolraw":
            return self._timeline(session, artifact, data, query)
        if mode == "artlist":
            return self._articles(session, artifact, data, query)
        raise ValueError(f"unsupported GDELT mode: {mode!r}")

    def _timeline(
        self, session: Session, artifact: RawArtifact, data: dict[str, Any], query: str
    ) -> ProcessOutcome:
        outcome = ProcessOutcome()
        series = data.get("timeline") or []
        if not series:
            return outcome
        resolution = (data.get("query_details") or {}).get("date_resolution", "unknown")
        for raw in series[0].get("data", []):
            try:
                point = TimelinePoint.model_validate(raw)
            except (ValidationError, TypeError, ValueError) as exc:
                outcome.rejects.append(Reject(_short(exc), {"point": raw}))
                continue
            session.add(
                NewsCoveragePoint(
                    artifact_id=artifact.artifact_id,
                    query=query,
                    resolution=resolution,
                    period_start=point.date,
                    matching_articles=point.value,
                    total_monitored=point.norm,
                    retrieved_at=artifact.retrieved_at,
                )
            )
            outcome.rows_written += 1
        return outcome

    def _articles(
        self, session: Session, artifact: RawArtifact, data: dict[str, Any], query: str
    ) -> ProcessOutcome:
        outcome = ProcessOutcome()
        valid: list[ArticleRecord] = []
        for raw in data.get("articles") or []:
            try:
                valid.append(ArticleRecord.model_validate(raw))
            except (ValidationError, TypeError, ValueError) as exc:
                outcome.rejects.append(Reject(_short(exc), {"article": raw}))

        urls = {a.url for a in valid}
        known = set(session.scalars(select(NewsArticle.url).where(NewsArticle.url.in_(urls))))
        for article in valid:
            if article.url in known:
                outcome.skipped_duplicates += 1
                continue
            known.add(article.url)
            session.add(
                NewsArticle(
                    url=article.url,
                    title=article.title,
                    domain=article.domain,
                    language=article.language or None,
                    source_country=article.sourcecountry or None,
                    seen_at=article.seendate,
                    story_key=story_key(article.title, article.seendate),
                    query=query,
                    first_artifact_id=artifact.artifact_id,
                )
            )
            outcome.rows_written += 1
        return outcome


def _short(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"[:500]

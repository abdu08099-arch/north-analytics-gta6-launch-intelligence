"""Data products: the versioned JSON files the dashboard reads (Decision 0001).

Every product carries its own metadata (source, unit, kind, coverage), so the
dashboard can label each chart without guessing. The dashboard reads these
files only, so it can never show a number the pipeline did not produce.
"""

import json
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gta6_intelligence import __version__
from gta6_intelligence.connectors.registry import CONNECTORS
from gta6_intelligence.db.models import (
    ArtifactProcessing,
    CollectionRun,
    EventMilestone,
    NewsCoveragePoint,
    QuarantinedRecord,
    RawArtifact,
    RunStatus,
    Source,
)
from gta6_intelligence.utils.time import utc_now

SUCCESSFUL = (RunStatus.SUCCESS, RunStatus.PARTIAL)


def _envelope(product: str, kind: str, description: str, data: Any, **meta: Any) -> dict:
    return {
        "product": product,
        "kind": kind,  # "observed", "derived" or "predicted"
        "description": description,
        "generated_at": utc_now().isoformat(),
        "code_version": __version__,
        **meta,
        "data": data,
    }


def build_status(session: Session) -> dict:
    rows = []
    for source in session.scalars(select(Source).order_by(Source.source_id)):
        last = session.scalar(
            select(CollectionRun)
            .where(CollectionRun.source_id == source.source_id)
            .order_by(CollectionRun.started_at.desc())
            .limit(1)
        )
        last_success = session.scalar(
            select(func.max(CollectionRun.finished_at)).where(
                CollectionRun.source_id == source.source_id, CollectionRun.status.in_(SUCCESSFUL)
            )
        )
        processing = dict(
            session.execute(
                select(ArtifactProcessing.status, func.count())
                .join(RawArtifact, RawArtifact.artifact_id == ArtifactProcessing.artifact_id)
                .where(RawArtifact.source_id == source.source_id)
                .group_by(ArtifactProcessing.status)
            ).all()
        )
        rows.append(
            {
                "source_id": source.source_id,
                "name": source.name,
                "status": source.status.value,
                "connector_available": source.source_id in CONNECTORS,
                "notes": source.notes,
                "last_run": None
                if last is None
                else {
                    "status": last.status.value,
                    "started_at": last.started_at.isoformat(),
                    "error": last.error_message,
                },
                "last_success_at": last_success.isoformat() if last_success else None,
                "raw_artifacts": session.scalar(
                    select(func.count()).where(RawArtifact.source_id == source.source_id)
                ),
                "processing": {k.value: v for k, v in processing.items()},
                "quarantined_records": session.scalar(
                    select(func.count()).where(QuarantinedRecord.source_id == source.source_id)
                ),
            }
        )
    return _envelope("status", "observed", "Source status, freshness and data quality.", rows)


def build_events(session: Session) -> dict:
    events = [
        {
            "event_id": e.event_id,
            "event_name": e.event_name,
            "event_type": e.event_type,
            "event_date": e.event_date.isoformat(),
            "published_at": e.published_at.isoformat() if e.published_at else None,
            "source_url": e.source_url,
            "source_kind": e.source_kind,
            "summary": e.summary,
            "verification_status": e.verification_status.value,
        }
        for e in session.scalars(select(EventMilestone).order_by(EventMilestone.event_date))
    ]
    return _envelope(
        "events",
        "observed",
        "Curated GTA VI milestones. Unverified events come from secondary sources.",
        events,
        source="data/reference/event_milestones.csv",
    )


def build_news_coverage_daily(session: Session) -> dict:
    """One value per UTC day from the most recent GDELT snapshot that fully covers that day.

    Snapshot rule: overlapping 7-day timelines are never summed or appended. For each
    day we take the latest-retrieved artifact whose coverage window contains the whole
    day, and aggregate only that artifact's points.
    """
    artifacts = session.scalars(
        select(RawArtifact)
        .where(RawArtifact.source_id == "gdelt", RawArtifact.coverage_start.is_not(None))
        .order_by(RawArtifact.retrieved_at.desc())
    ).all()
    timelines = [a for a in artifacts if a.request_params.get("mode") == "timelinevolraw"]

    chosen: dict[str, RawArtifact] = {}
    for artifact in timelines:  # newest first, so the first match wins
        day = artifact.coverage_start
        while day + timedelta(days=1) <= artifact.coverage_end:
            chosen.setdefault(day.date().isoformat(), artifact)
            day += timedelta(days=1)

    by_artifact: dict[str, list[NewsCoveragePoint]] = defaultdict(list)
    ids = {a.artifact_id for a in chosen.values()}
    if ids:
        for p in session.scalars(
            select(NewsCoveragePoint).where(NewsCoveragePoint.artifact_id.in_(ids))
        ):
            by_artifact[p.artifact_id].append(p)

    data = []
    for day in sorted(chosen):
        artifact = chosen[day]
        start = datetime.fromisoformat(day).replace(tzinfo=UTC)
        points = [
            p
            for p in by_artifact[artifact.artifact_id]
            if start <= p.period_start < start + timedelta(days=1)
        ]
        matching = sum(p.matching_articles for p in points)
        totals = [p.total_monitored for p in points if p.total_monitored is not None]
        total = sum(totals) if len(totals) == len(points) and points else None
        resolution = points[0].resolution if points else None
        expected = {"hour": 24, "15min": 96, "day": 1}.get(resolution or "")
        data.append(
            {
                "date": day,
                "matching_articles": matching if points else None,
                "total_monitored": total,
                "coverage_share": (matching / total) if total else None,
                "points": len(points),
                "resolution": resolution,
                "complete": bool(points) and expected is not None and len(points) == expected,
                "snapshot_artifact_id": artifact.artifact_id,
                "snapshot_retrieved_at": artifact.retrieved_at.isoformat(),
            }
        )
    return _envelope(
        "news_coverage_daily",
        "derived",
        "Daily news coverage of GTA VI in GDELT: matching articles and share of all monitored "
        "articles. Media attention, not audience size.",
        data,
        source="GDELT DOC 2.0 API (mode=timelinevolraw)",
        unit="articles; share = matching / monitored",
        method="Latest snapshot that fully covers each UTC day; see "
        "docs/methodology/gdelt-news-coverage.md",
    )


PRODUCTS = {
    "status.json": build_status,
    "events.json": build_events,
    "news_coverage_daily.json": build_news_coverage_daily,
}


def publish(session: Session, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, build in PRODUCTS.items():
        path = out_dir / filename
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(build(session), indent=2, ensure_ascii=False) + "\n")
        tmp.replace(path)  # atomic: the dashboard never reads a half-written file
        written.append(path)
    return written

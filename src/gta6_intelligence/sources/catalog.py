"""The six sources from the PRD and their current status.

This mirrors docs/data/source-register.md. Change a status here and in the
register in the same pull request, with the reason in docs/decisions/.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from gta6_intelligence.db.models import Source, SourceStatus

REVIEWED = date(2026, 11, 19)


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    name: str
    source_type: str
    documentation_url: str
    access_method: str
    status: SourceStatus
    notes: str


CATALOG: tuple[SourceSpec, ...] = (
    SourceSpec(
        "google_trends",
        "Google Trends",
        "search_interest",
        "https://support.google.com/trends/answer/4365538",
        "Manual CSV export from trends.google.com (API alpha applied for separately)",
        SourceStatus.PLANNED,
        "Relative interest 0-100, not search counts. Decision 0002.",
    ),
    SourceSpec(
        "event_ledger",
        "Official milestones (Rockstar Newswire and other official channels)",
        "events",
        "https://www.rockstargames.com/newswire",
        "Human-curated CSV in data/reference/, changed only by pull request",
        SourceStatus.PLANNED,
        "No public API or RSS found; no automated fetching.",
    ),
    SourceSpec(
        "gdelt",
        "GDELT DOC 2.0 (news coverage)",
        "news",
        "https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/",
        "Public DOC 2.0 API, no key",
        SourceStatus.PLANNED,
        "Rolling ~3-month window; coverage share, not audience. Decision 0003.",
    ),
    SourceSpec(
        "youtube",
        "YouTube Data API v3",
        "video",
        "https://developers.google.com/youtube/terms/developer-policies",
        "Official API, API key",
        SourceStatus.CONDITIONAL,
        "30-day retention rule and derived-metrics policy must be resolved first.",
    ),
    SourceSpec(
        "reddit",
        "Reddit Data API",
        "community",
        "https://www.redditinc.com/policies/data-api-terms",
        "None available",
        SourceStatus.BLOCKED,
        "New public API requests closed 2026-10-31; public access ends March 2027.",
    ),
    SourceSpec(
        "x",
        "X API v2 (counts endpoint)",
        "social",
        "https://docs.x.com/x-api/getting-started/pricing",
        "Official API, pay-per-use",
        SourceStatus.DEFERRED,
        "Needs Product Owner cost approval and a spend cap.",
    ),
)


def seed_sources(session: Session) -> int:
    """Insert or update every catalog entry. Safe to run repeatedly. Returns rows touched."""
    for spec in CATALOG:
        row = session.get(Source, spec.source_id) or Source(source_id=spec.source_id)
        row.name = spec.name
        row.source_type = spec.source_type
        row.documentation_url = spec.documentation_url
        row.access_method = spec.access_method
        row.status = spec.status
        row.terms_reviewed_on = REVIEWED
        row.notes = spec.notes
        session.add(row)
    session.commit()
    return len(CATALOG)

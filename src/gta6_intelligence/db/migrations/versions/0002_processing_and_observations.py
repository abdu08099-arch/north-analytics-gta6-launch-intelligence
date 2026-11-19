"""add processing and observation tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-19 15:31:39.194073
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "artifact_processing",
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.Column("processor", sa.String(length=100), nullable=False),
        sa.Column("processor_version", sa.String(length=20), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "processed",
                "partial",
                "failed",
                name="processing_status",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rows_written", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["raw_artifacts.artifact_id"],
            name=op.f("fk_artifact_processing_artifact_id_raw_artifacts"),
        ),
        sa.PrimaryKeyConstraint("artifact_id", name=op.f("pk_artifact_processing")),
    )
    op.create_table(
        "event_milestones",
        sa.Column("event_id", sa.String(length=80), nullable=False),
        sa.Column("event_name", sa.String(length=300), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_kind", sa.String(length=20), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "verification_status",
            sa.Enum(
                "verified",
                "unverified",
                "disputed",
                name="verification_status",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("reviewer", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["raw_artifacts.artifact_id"],
            name=op.f("fk_event_milestones_artifact_id_raw_artifacts"),
        ),
        sa.PrimaryKeyConstraint("event_id", name=op.f("pk_event_milestones")),
    )
    with op.batch_alter_table("event_milestones", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_event_milestones_event_date"), ["event_date"], unique=False
        )

    op.create_table(
        "news_articles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(length=300), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column("source_country", sa.String(length=100), nullable=True),
        sa.Column("seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("story_key", sa.String(length=64), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("first_artifact_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["first_artifact_id"],
            ["raw_artifacts.artifact_id"],
            name=op.f("fk_news_articles_first_artifact_id_raw_artifacts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news_articles")),
        sa.UniqueConstraint("url", name=op.f("uq_news_articles_url")),
    )
    with op.batch_alter_table("news_articles", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_news_articles_domain"), ["domain"], unique=False)
        batch_op.create_index(batch_op.f("ix_news_articles_seen_at"), ["seen_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_news_articles_story_key"), ["story_key"], unique=False)

    op.create_table(
        "news_coverage_points",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("resolution", sa.String(length=20), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("matching_articles", sa.Integer(), nullable=False),
        sa.Column("total_monitored", sa.Integer(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "matching_articles >= 0", name=op.f("ck_news_coverage_points_matching_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["raw_artifacts.artifact_id"],
            name=op.f("fk_news_coverage_points_artifact_id_raw_artifacts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news_coverage_points")),
        sa.UniqueConstraint("artifact_id", "period_start", name="artifact_period"),
    )
    with op.batch_alter_table("news_coverage_points", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_news_coverage_points_artifact_id"), ["artifact_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_news_coverage_points_period_start"), ["period_start"], unique=False
        )

    op.create_table(
        "quarantined_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("record", sa.JSON(), nullable=False),
        sa.Column("quarantined_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["raw_artifacts.artifact_id"],
            name=op.f("fk_quarantined_records_artifact_id_raw_artifacts"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.source_id"],
            name=op.f("fk_quarantined_records_source_id_sources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quarantined_records")),
    )
    with op.batch_alter_table("quarantined_records", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_quarantined_records_artifact_id"), ["artifact_id"], unique=False
        )

    op.create_table(
        "search_observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.Column("series_label", sa.String(length=300), nullable=False),
        sa.Column("query", sa.String(length=200), nullable=False),
        sa.Column("query_kind", sa.String(length=10), nullable=False),
        sa.Column("geo", sa.String(length=10), nullable=False),
        sa.Column("granularity", sa.String(length=10), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interest_value", sa.Integer(), nullable=True),
        sa.Column("value_flag", sa.String(length=20), nullable=True),
        sa.Column("export_window", sa.String(length=50), nullable=False),
        sa.CheckConstraint(
            "interest_value IS NULL OR (interest_value >= 0 AND interest_value <= 100)",
            name=op.f("ck_search_observations_interest_range"),
        ),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["raw_artifacts.artifact_id"],
            name=op.f("fk_search_observations_artifact_id_raw_artifacts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_search_observations")),
        sa.UniqueConstraint("artifact_id", "series_label", "period_start", name="artifact_series"),
    )
    with op.batch_alter_table("search_observations", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_search_observations_artifact_id"), ["artifact_id"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_search_observations_geo"), ["geo"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_search_observations_period_start"), ["period_start"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("search_observations", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_search_observations_period_start"))
        batch_op.drop_index(batch_op.f("ix_search_observations_geo"))
        batch_op.drop_index(batch_op.f("ix_search_observations_artifact_id"))

    op.drop_table("search_observations")
    with op.batch_alter_table("quarantined_records", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_quarantined_records_artifact_id"))

    op.drop_table("quarantined_records")
    with op.batch_alter_table("news_coverage_points", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_news_coverage_points_period_start"))
        batch_op.drop_index(batch_op.f("ix_news_coverage_points_artifact_id"))

    op.drop_table("news_coverage_points")
    with op.batch_alter_table("news_articles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_news_articles_story_key"))
        batch_op.drop_index(batch_op.f("ix_news_articles_seen_at"))
        batch_op.drop_index(batch_op.f("ix_news_articles_domain"))

    op.drop_table("news_articles")
    with op.batch_alter_table("event_milestones", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_event_milestones_event_date"))

    op.drop_table("event_milestones")
    op.drop_table("artifact_processing")

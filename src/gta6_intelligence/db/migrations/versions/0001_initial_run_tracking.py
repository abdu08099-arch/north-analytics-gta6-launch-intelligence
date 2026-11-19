"""create sources, collection_runs and raw_artifacts

Revision ID: 0001
Revises: (none)
Create Date: 2026-11-19 15:13:48.016485
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("source_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("documentation_url", sa.String(length=500), nullable=True),
        sa.Column("access_method", sa.String(length=200), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "enabled",
                "planned",
                "conditional",
                "deferred",
                "blocked",
                "disabled",
                name="source_status",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("terms_reviewed_on", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("source_id", name=op.f("pk_sources")),
    )
    op.create_table(
        "collection_runs",
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=50), nullable=False),
        sa.Column(
            "trigger",
            sa.Enum(
                "scheduled",
                "manual",
                name="run_trigger",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column(
            "collection_mode",
            sa.Enum(
                "live",
                "backfill",
                name="collection_mode",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "running",
                "success",
                "partial",
                "failed",
                name="run_status",
                native_enum=False,
                create_constraint=True,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_count", sa.Integer(), nullable=False),
        sa.Column("valid_count", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("code_version", sa.String(length=64), nullable=True),
        sa.CheckConstraint(
            "fetched_count >= 0 AND valid_count >= 0 AND rejected_count >= 0",
            name=op.f("ck_collection_runs_non_negative_counts"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"], ["sources.source_id"], name=op.f("fk_collection_runs_source_id_sources")
        ),
        sa.PrimaryKeyConstraint("run_id", name=op.f("pk_collection_runs")),
    )
    with op.batch_alter_table("collection_runs", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_collection_runs_source_id"), ["source_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_collection_runs_started_at"), ["started_at"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_collection_runs_status"), ["status"], unique=False)

    op.create_table(
        "raw_artifacts",
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=50), nullable=False),
        sa.Column("relative_path", sa.String(length=500), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("media_type", sa.String(length=100), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("coverage_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("coverage_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_params", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["collection_runs.run_id"],
            name=op.f("fk_raw_artifacts_run_id_collection_runs"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"], ["sources.source_id"], name=op.f("fk_raw_artifacts_source_id_sources")
        ),
        sa.PrimaryKeyConstraint("artifact_id", name=op.f("pk_raw_artifacts")),
        sa.UniqueConstraint("relative_path", name=op.f("uq_raw_artifacts_relative_path")),
    )
    with op.batch_alter_table("raw_artifacts", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_raw_artifacts_run_id"), ["run_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_raw_artifacts_sha256"), ["sha256"], unique=False)
        batch_op.create_index(batch_op.f("ix_raw_artifacts_source_id"), ["source_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("raw_artifacts", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_raw_artifacts_source_id"))
        batch_op.drop_index(batch_op.f("ix_raw_artifacts_sha256"))
        batch_op.drop_index(batch_op.f("ix_raw_artifacts_run_id"))

    op.drop_table("raw_artifacts")
    with op.batch_alter_table("collection_runs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_collection_runs_status"))
        batch_op.drop_index(batch_op.f("ix_collection_runs_started_at"))
        batch_op.drop_index(batch_op.f("ix_collection_runs_source_id"))

    op.drop_table("collection_runs")
    op.drop_table("sources")

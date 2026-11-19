"""Command line interface: `uv run gta6 --help`.

Commands
  gta6 db upgrade          create or update the database schema
  gta6 db seed-sources     write the six PRD sources and their status to the database
  gta6 sources             list sources and status
  gta6 collect --source X  run one connector (or --all for every registered one)
  gta6 process --source X  parse stored raw artifacts into tables (or --all)
  gta6 publish             write the dashboard's JSON data products to data/products/
  gta6 runs                show recent collection runs
"""

import argparse
import logging
import sys

from sqlalchemy import select

from gta6_intelligence.collection.lock import RunLockedError, collection_lock
from gta6_intelligence.collection.raw_store import RawStore
from gta6_intelligence.collection.runner import run_connectors
from gta6_intelligence.config.settings import Settings, get_settings
from gta6_intelligence.connectors.registry import CONNECTORS
from gta6_intelligence.db import migrate
from gta6_intelligence.db.models import CollectionRun, RunStatus, RunTrigger, Source
from gta6_intelligence.db.session import make_engine, make_session_factory
from gta6_intelligence.processing.registry import PROCESSORS
from gta6_intelligence.processing.runner import process_pending
from gta6_intelligence.reporting.products import publish
from gta6_intelligence.sources.catalog import seed_sources
from gta6_intelligence.utils.logging import configure_logging

log = logging.getLogger("gta6")

EXIT_OK = 0
EXIT_FAILED_RUN = 1
EXIT_USAGE = 2
EXIT_LOCKED = 3


def _ensure_sqlite_dir(settings: Settings) -> None:
    if settings.database_url.startswith("sqlite:///"):
        settings.data_dir.mkdir(parents=True, exist_ok=True)


def _cmd_db_upgrade(settings: Settings, _args: argparse.Namespace) -> int:
    _ensure_sqlite_dir(settings)
    migrate.upgrade(settings.database_url)
    print("Database schema is up to date.")
    return EXIT_OK


def _cmd_db_seed(settings: Settings, _args: argparse.Namespace) -> int:
    factory = make_session_factory(make_engine(settings.database_url))
    with factory() as session:
        count = seed_sources(session)
    print(f"Seeded {count} sources.")
    return EXIT_OK


def _cmd_sources(settings: Settings, _args: argparse.Namespace) -> int:
    factory = make_session_factory(make_engine(settings.database_url))
    with factory() as session:
        rows = session.scalars(select(Source).order_by(Source.source_id)).all()
    if not rows:
        print("No sources. Run `gta6 db seed-sources`.")
    for row in rows:
        runnable = "yes" if row.source_id in CONNECTORS else "no"
        print(f"{row.source_id:<15} {row.status.value:<12} connector: {runnable:<4} {row.name}")
    return EXIT_OK


def _cmd_collect(settings: Settings, args: argparse.Namespace) -> int:
    if args.all:
        selected = list(CONNECTORS)
    elif args.source in CONNECTORS:
        selected = [args.source]
    else:
        available = ", ".join(CONNECTORS) or "none yet"
        print(f"No connector for {args.source!r}. Available: {available}.", file=sys.stderr)
        return EXIT_USAGE
    if not selected:
        print("No connectors are implemented yet (Phase 2).")
        return EXIT_OK

    factory = make_session_factory(make_engine(settings.database_url))
    trigger = RunTrigger.SCHEDULED if args.scheduled else RunTrigger.MANUAL
    try:
        with collection_lock(settings.lock_path):
            results = run_connectors(
                [CONNECTORS[s]() for s in selected],
                session_factory=factory,
                raw_store=RawStore(settings.raw_dir),
                trigger=trigger,
            )
    except RunLockedError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_LOCKED

    for r in results:
        print(
            f"{r.source_id:<15} {r.status.value:<8} artifacts: {r.artifact_count}  run: {r.run_id}"
        )
    incomplete = {RunStatus.FAILED, RunStatus.PARTIAL}
    return EXIT_FAILED_RUN if any(r.status in incomplete for r in results) else EXIT_OK


def _cmd_process(settings: Settings, args: argparse.Namespace) -> int:
    if args.all:
        selected = list(PROCESSORS)
    elif args.source in PROCESSORS:
        selected = [args.source]
    else:
        print(
            f"No processor for {args.source!r}. Available: {', '.join(PROCESSORS)}.",
            file=sys.stderr,
        )
        return EXIT_USAGE
    factory = make_session_factory(make_engine(settings.database_url))
    any_failed = False
    for source_id in selected:
        summary = process_pending(
            PROCESSORS[source_id](), session_factory=factory, raw_store=RawStore(settings.raw_dir)
        )
        any_failed |= summary.failed > 0
        print(
            f"{source_id:<15} artifacts: {summary.artifacts}  rows: {summary.rows_written}  "
            f"quarantined: {summary.rows_rejected}  failed: {summary.failed}"
        )
    return EXIT_FAILED_RUN if any_failed else EXIT_OK


def _cmd_publish(settings: Settings, _args: argparse.Namespace) -> int:
    factory = make_session_factory(make_engine(settings.database_url))
    with factory() as session:
        paths = publish(session, settings.products_dir)
    for path in paths:
        print(f"wrote {path}")
    return EXIT_OK


def _cmd_runs(settings: Settings, args: argparse.Namespace) -> int:
    factory = make_session_factory(make_engine(settings.database_url))
    with factory() as session:
        runs = session.scalars(
            select(CollectionRun).order_by(CollectionRun.started_at.desc()).limit(args.limit)
        ).all()
    if not runs:
        print("No runs recorded yet.")
    for run in runs:
        print(
            f"{run.started_at:%Y-%m-%d %H:%M}Z  {run.source_id:<15} {run.status.value:<8} "
            f"fetched={run.fetched_count}  {run.error_message or ''}"
        )
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gta6", description="GTA VI Launch Intelligence")
    sub = parser.add_subparsers(dest="command", required=True)

    db = sub.add_parser("db", help="database commands")
    db_sub = db.add_subparsers(dest="db_command", required=True)
    db_sub.add_parser("upgrade", help="apply migrations").set_defaults(func=_cmd_db_upgrade)
    db_sub.add_parser("seed-sources", help="write source catalog").set_defaults(func=_cmd_db_seed)

    sub.add_parser("sources", help="list sources").set_defaults(func=_cmd_sources)

    collect = sub.add_parser("collect", help="run connectors")
    target = collect.add_mutually_exclusive_group(required=True)
    target.add_argument("--source", help="source_id to collect")
    target.add_argument("--all", action="store_true", help="every registered connector")
    collect.add_argument("--scheduled", action="store_true", help="mark run as scheduled")
    collect.set_defaults(func=_cmd_collect)

    process = sub.add_parser("process", help="parse raw artifacts into tables")
    ptarget = process.add_mutually_exclusive_group(required=True)
    ptarget.add_argument("--source", help="source_id to process")
    ptarget.add_argument("--all", action="store_true", help="every source with a processor")
    process.set_defaults(func=_cmd_process)

    sub.add_parser("publish", help="write JSON data products").set_defaults(func=_cmd_publish)

    runs = sub.add_parser("runs", help="recent collection runs")
    runs.add_argument("--limit", type=int, default=20)
    runs.set_defaults(func=_cmd_runs)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = get_settings()
    configure_logging(settings.log_level, settings.secret_values())
    return args.func(settings, args)


if __name__ == "__main__":
    raise SystemExit(main())

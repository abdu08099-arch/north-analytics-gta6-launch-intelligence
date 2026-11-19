from datetime import UTC, datetime

import pytest

from gta6_intelligence.collection.raw_store import RawStore
from gta6_intelligence.utils.hashing import sha256_hex

WHEN = datetime(2026, 11, 19, 6, 30, tzinfo=UTC)


def test_writes_date_partitioned_file_with_checksum(tmp_path) -> None:
    store = RawStore(tmp_path)
    stored = store.write(
        source_id="gdelt", run_id="r1", index=0, extension="json", content=b"{}", retrieved_at=WHEN
    )
    assert stored.relative_path == "gdelt/2026/11/19/r1-0.json"
    assert stored.sha256 == sha256_hex(b"{}")
    assert stored.size_bytes == 2
    assert store.read(stored.relative_path) == b"{}"


def test_never_overwrites_an_existing_artifact(tmp_path) -> None:
    store = RawStore(tmp_path)
    kwargs = dict(source_id="gdelt", run_id="r1", index=0, extension="json", retrieved_at=WHEN)
    store.write(content=b"first", **kwargs)
    with pytest.raises(FileExistsError):
        store.write(content=b"second", **kwargs)
    assert store.read("gdelt/2026/11/19/r1-0.json") == b"first"


def test_rejects_naive_timestamps(tmp_path) -> None:
    with pytest.raises(ValueError, match="naive"):
        RawStore(tmp_path).write(
            source_id="s",
            run_id="r",
            index=0,
            extension="txt",
            content=b"x",
            retrieved_at=datetime(2026, 11, 19),  # noqa: DTZ001 - deliberately naive
        )

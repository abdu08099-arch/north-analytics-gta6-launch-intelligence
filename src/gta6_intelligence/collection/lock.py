"""Prevents two collection runs from overlapping on the same machine (PRD F1).

Uses an OS file lock, which is released automatically if the process dies,
so a crashed run never leaves a stale lock behind. GitHub Actions adds its
own `concurrency` guard on top.
"""

import fcntl
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class RunLockedError(RuntimeError):
    """Another collection run holds the lock."""


@contextmanager
def collection_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RunLockedError(f"another collection run is active (lock: {path})") from exc
        handle.seek(0)
        handle.truncate()
        handle.write(str(os.getpid()))
        handle.flush()
        yield
    finally:
        handle.close()  # closing releases the lock

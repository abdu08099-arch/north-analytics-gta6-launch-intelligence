"""Immutable storage for raw artifacts.

Layout: <raw_dir>/<source_id>/<YYYY>/<MM>/<DD>/<run_id>-<n>.<ext>
Files are opened in exclusive-create mode, so an existing artifact can never
be overwritten (PRD F2).
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from gta6_intelligence.utils.hashing import sha256_hex
from gta6_intelligence.utils.time import ensure_utc


@dataclass(frozen=True)
class StoredArtifact:
    relative_path: str
    sha256: str
    size_bytes: int


class RawStore:
    def __init__(self, raw_dir: Path) -> None:
        self.raw_dir = raw_dir

    def write(
        self,
        *,
        source_id: str,
        run_id: str,
        index: int,
        extension: str,
        content: bytes,
        retrieved_at: datetime,
    ) -> StoredArtifact:
        day = ensure_utc(retrieved_at)
        relative = Path(
            source_id, f"{day:%Y}", f"{day:%m}", f"{day:%d}", f"{run_id}-{index}.{extension}"
        )
        target = self.raw_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:  # "x" fails if the file exists
            handle.write(content)
        return StoredArtifact(relative.as_posix(), sha256_hex(content), len(content))

    def read(self, relative_path: str) -> bytes:
        return (self.raw_dir / relative_path).read_bytes()

import pytest

from gta6_intelligence.collection.lock import RunLockedError, collection_lock


def test_second_holder_is_refused_and_lock_is_released_after(tmp_path) -> None:
    lock = tmp_path / ".collect.lock"
    with collection_lock(lock), pytest.raises(RunLockedError), collection_lock(lock):
        pass
    with collection_lock(lock):  # free again
        pass

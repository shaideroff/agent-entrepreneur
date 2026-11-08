import os
import sqlite3
from pathlib import Path

import pytest

from agent_entrepreneur.storage.database import connect


def test_context_managed_connection_closes_after_transaction(tmp_path: Path):
    path = tmp_path / "managed.db"
    with connect(path) as db:
        db.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        db.execute("SELECT 1")


@pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions only")
def test_database_file_is_created_with_private_permissions(tmp_path: Path):
    path = tmp_path / "private" / "data.sqlite3"
    with connect(path) as db:
        db.execute("SELECT 1")
    assert path.stat().st_mode & 0o777 == 0o600


def test_database_symlink_is_rejected(tmp_path: Path):
    target = tmp_path / "target.db"
    target.touch()
    link = tmp_path / "linked.db"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links are not available")
    with pytest.raises(ValueError, match="symbolic link"):
        connect(link)

""""Consistent, permission-restricted SQLite database backups."""
from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path


def backup_database(source: Path, destination: Path) -> Path:
    """Create and atomically publish a consistent, owner-private SQLite backup.

    The SQLite online backup API captures committed pages while the source may
    be open elsewhere. A private temporary file is validated before a
    no-overwrite hard-link publishes it at the requested destination.
    """
    source = source.expanduser()
    destination = destination.expanduser()

    if source.is_symlink():
        raise ValueError("source database must not be a symbolic link")
    if not source.exists():
        raise FileNotFoundError(source)
    if not source.is_file():
        raise ValueError("source database must be a regular file")
    if source.resolve() == destination.resolve():
        raise ValueError("source and destination must be different files")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)

    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    published = False
    try:
        os.close(descriptor)
        with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as source_db:
            with sqlite3.connect(temporary) as destination_db:
                source_db.backup(destination_db)
                integrity = destination_db.execute("PRAGMA integrity_check").fetchone()
                if integrity is None or integrity[0] != "ok":
                    detail = "no result" if integrity is None else str(integrity[0])
                    raise sqlite3.DatabaseError(
                        f"backup integrity check failed: {detail}"
                    )

        if os.name == "posix":
            os.chmod(temporary, 0o600)
        with temporary.open("rb") as backup_file:
            os.fsync(backup_file.fileno())

        # link() is an atomic create-if-absent operation on the same filesystem.
        # Unlike replace(), it cannot overwrite a destination created concurrently.
        os.link(temporary, destination)
        published = True
        temporary.unlink()
        if os.name == "posix":
            directory_fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if not published:
            temporary.unlink(missing_ok=True)
        elif temporary.exists():
            temporary.unlink(missing_ok=True)

    return destination

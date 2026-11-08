"""Consistent, permission-restricted SQLite database backups."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def backup_database(source: Path, destination: Path) -> Path:
    """Create a consistent SQLite backup without overwriting an existing file.

    The SQLite backup API safely captures committed pages while the source may
    be open elsewhere. Backups are created as new, owner-private files.
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
    try:
        # Exclusive creation prevents accidental overwrite and requests private
        # permissions before SQLite opens the destination.
        descriptor = os.open(
            destination,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
        os.close(descriptor)
        with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as source_db:
            with sqlite3.connect(destination) as destination_db:
                source_db.backup(destination_db)
        if os.name == "posix":
            os.chmod(destination, 0o600)
    except BaseException:
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return destination

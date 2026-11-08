from __future__ import annotations

import os
import stat
import sqlite3
from pathlib import Path
from types import TracebackType
from typing import Literal

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, scope TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_memory_scope ON memory(scope);
CREATE TABLE IF NOT EXISTS workflow_runs (id TEXT PRIMARY KEY, status TEXT NOT NULL, state_json TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS entrepreneur_profiles (id TEXT PRIMARY KEY, name TEXT NOT NULL, region TEXT, domains_json TEXT NOT NULL, evidence_level TEXT NOT NULL, summary TEXT NOT NULL, attribution TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence_records (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES entrepreneur_profiles(id), title TEXT NOT NULL, url TEXT, source_type TEXT NOT NULL, checked_at TEXT);
"""


def _prepare_database_file(path: Path) -> None:
    """Ensure a regular, owner-private database file without following POSIX symlinks."""
    if os.name != "posix":
        if path.is_symlink():
            raise ValueError("database path must not be a symbolic link")
        if path.exists() and not path.is_file():
            raise ValueError("database path must be a regular file")
        return

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    flags = os.O_RDWR | nofollow
    try:
        descriptor = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        try:
            descriptor = os.open(path, flags)
        except OSError as exc:
            if exc.errno in {getattr(os, "ELOOP", 40), getattr(os, "EMLINK", 31)}:
                raise ValueError("database path must not be a symbolic link") from exc
            raise
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise ValueError("database path must be a regular file")
        os.fchmod(descriptor, 0o600)
    finally:
        os.close(descriptor)


class ManagedConnection(sqlite3.Connection):
    """Commit or roll back on context exit, then always release the file handle."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        try:
            super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()
        return False


def connect(path: Path) -> sqlite3.Connection:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _prepare_database_file(path)
    connection = sqlite3.connect(path, timeout=10, factory=ManagedConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from types import TracebackType

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, scope TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_memory_scope ON memory(scope);
CREATE TABLE IF NOT EXISTS workflow_runs (id TEXT PRIMARY KEY, status TEXT NOT NULL, state_json TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS entrepreneur_profiles (id TEXT PRIMARY KEY, name TEXT NOT NULL, region TEXT, domains_json TEXT NOT NULL, evidence_level TEXT NOT NULL, summary TEXT NOT NULL, attribution TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence_records (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES entrepreneur_profiles(id), title TEXT NOT NULL, url TEXT, source_type TEXT NOT NULL, checked_at TEXT);
"""


def _prepare_database_file(path: Path) -> None:
    """Create a private SQLite file on POSIX and reject a database symlink."""
    if path.is_symlink():
        raise ValueError("database path must not be a symbolic link")
    if os.name == "posix":
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        except FileExistsError:
            os.chmod(path, 0o600)
        else:
            os.close(descriptor)


class ManagedConnection(sqlite3.Connection):
    """Commit or roll back on context exit, then always release the file handle."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def connect(path: Path) -> sqlite3.Connection:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _prepare_database_file(path)
    connection = sqlite3.connect(path, timeout=10, factory=ManagedConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection

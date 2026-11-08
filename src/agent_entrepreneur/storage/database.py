from __future__ import annotations
import sqlite3
from pathlib import Path
SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, scope TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_memory_scope ON memory(scope);
CREATE TABLE IF NOT EXISTS workflow_runs (id TEXT PRIMARY KEY, status TEXT NOT NULL, state_json TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS entrepreneur_profiles (id TEXT PRIMARY KEY, name TEXT NOT NULL, region TEXT, domains_json TEXT NOT NULL, evidence_level TEXT NOT NULL, summary TEXT NOT NULL, attribution TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence_records (id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES entrepreneur_profiles(id), title TEXT NOT NULL, url TEXT, source_type TEXT NOT NULL, checked_at TEXT);
"""
def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection

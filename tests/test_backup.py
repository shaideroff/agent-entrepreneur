from pathlib import Path

import pytest

from agent_entrepreneur.storage.backup import backup_database
from agent_entrepreneur.storage.database import connect


def test_backup_restores_committed_memory_and_workflow_state(tmp_path: Path):
    source = tmp_path / "source.sqlite3"
    backup = tmp_path / "backups" / "snapshot.sqlite3"
    with connect(source) as db:
        db.execute(
            "INSERT INTO memory(id, scope, content) VALUES (?, ?, ?)",
            ("m-1", "user", "approved note"),
        )
        db.execute(
            "INSERT INTO workflow_runs(id, status, state_json) VALUES (?, ?, ?)",
            ("w-1", "partial", '{"step": 2}'),
        )

    backup_database(source, backup)

    with connect(backup) as db:
        memory = db.execute(
            "SELECT scope, content FROM memory WHERE id = ?", ("m-1",)
        ).fetchone()
        workflow = db.execute(
            "SELECT status, state_json FROM workflow_runs WHERE id = ?", ("w-1",)
        ).fetchone()
    assert tuple(memory) == ("user", "approved note")
    assert tuple(workflow) == ("partial", '{"step": 2}')


def test_backup_rejects_same_source_and_destination(tmp_path: Path):
    source = tmp_path / "source.sqlite3"
    with connect(source):
        pass

    with pytest.raises(ValueError, match="different files"):
        backup_database(source, source)


def test_backup_requires_existing_source(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        backup_database(tmp_path / "missing.sqlite3", tmp_path / "backup.sqlite3")

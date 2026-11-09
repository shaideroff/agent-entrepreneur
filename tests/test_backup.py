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


def test_backup_is_integrity_checked_and_owner_private_on_posix(tmp_path: Path):
    import os
    import stat
    import sqlite3

    if os.name != "posix":
        pytest.skip("POSIX permission semantics are not available")

    source = tmp_path / "source.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    with connect(source) as db:
        db.execute(
            "INSERT INTO memory(id, scope, content) VALUES (?, ?, ?)",
            ("m-2", "user", "integrity check"),
        )

    backup_database(source, backup)

    assert stat.S_IMODE(backup.stat().st_mode) == 0o600
    with sqlite3.connect(backup) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_backup_never_overwrites_existing_destination(tmp_path: Path):
    source = tmp_path / "source.sqlite3"
    destination = tmp_path / "existing.sqlite3"
    with connect(source):
        pass
    destination.write_bytes(b"preserve this file")

    with pytest.raises(FileExistsError):
        backup_database(source, destination)

    assert destination.read_bytes() == b"preserve this file"


def test_backup_rejects_symbolic_link_source(tmp_path: Path):
    if not hasattr(Path, "symlink_to"):
        pytest.skip("symbolic links are not available")

    source = tmp_path / "source.sqlite3"
    link = tmp_path / "source-link.sqlite3"
    with connect(source):
        pass
    try:
        link.symlink_to(source)
    except (NotImplementedError, OSError):
        pytest.skip("symbolic links are not permitted")

    with pytest.raises(ValueError, match="symbolic link"):
        backup_database(link, tmp_path / "backup.sqlite3")


def test_backup_rejects_symbolic_link_destination(tmp_path: Path):
    source = tmp_path / "source.sqlite3"
    target = tmp_path / "target.sqlite3"
    link = tmp_path / "backup-link.sqlite3"
    with connect(source):
        pass
    target.write_bytes(b"do not follow")
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError):
        pytest.skip("symbolic links are not permitted")

    with pytest.raises(FileExistsError):
        backup_database(source, link)
    assert target.read_bytes() == b"do not follow"


def test_backup_is_not_published_until_snapshot_is_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    import sqlite3

    source = tmp_path / "source.sqlite3"
    destination = tmp_path / "backup.sqlite3"
    with connect(source):
        pass

    original_connect = sqlite3.connect
    source_uri = source.as_uri() + "?mode=ro"

    def guarded_connect(database, *args, **kwargs):
        if str(database) != source_uri:
            assert not destination.exists()
        return original_connect(database, *args, **kwargs)

    monkeypatch.setattr("agent_entrepreneur.storage.backup.sqlite3.connect", guarded_connect)

    backup_database(source, destination)

    assert destination.is_file()

def test_backup_restores_after_source_database_is_lost(tmp_path: Path):
    import shutil

    source = tmp_path / "production.sqlite3"
    backup = tmp_path / "backups" / "recovery.sqlite3"
    with connect(source) as db:
        db.execute(
            "INSERT INTO memory(id, scope, content) VALUES (?, ?, ?)",
            ("recover-memory", "user", "recoverable approved data"),
        )
        db.execute(
            "INSERT INTO workflow_runs(id, status, state_json) VALUES (?, ?, ?)",
            ("recover-workflow", "partial", '{"checkpoint": 3}'),
        )

    backup_database(source, backup)
    source.unlink()
    shutil.copy2(backup, source)

    with connect(source) as recovered:
        memory = recovered.execute(
            "SELECT scope, content FROM memory WHERE id = ?",
            ("recover-memory",),
        ).fetchone()
        workflow = recovered.execute(
            "SELECT status, state_json FROM workflow_runs WHERE id = ?",
            ("recover-workflow",),
        ).fetchone()

    assert tuple(memory) == ("user", "recoverable approved data")
    assert tuple(workflow) == ("partial", '{"checkpoint": 3}')


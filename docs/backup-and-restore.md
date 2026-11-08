# SQLite backup and restore

Agent Entrepreneur stores local application data in SQLite. The backup helper uses SQLite's online backup API to produce a consistent snapshot of committed database state. It does not encrypt backups and does not upload them anywhere.

## Create a backup

Run this from the project environment:

```bash
python - <<'PY'
from pathlib import Path
from agent_entrepreneur.storage.backup import backup_database

source = Path.home() / ".local/share/agent-entrepreneur/data.sqlite3"
destination = Path.home() / ".local/share/agent-entrepreneur/backups/data-2026-11-09.sqlite3"
print(backup_database(source, destination))
PY
```

Set `source` to the path configured by `AGENT_ENTREPRENEUR_DB` when using a custom database location. Choose a new destination for every snapshot; the helper refuses to overwrite an existing file. On POSIX systems, the resulting database file is restricted to owner read/write permissions (`0600`).

Keep backups in a directory accessible only to the intended user. The helper creates missing parent directories, but it does not encrypt backup contents or secure an already-existing parent directory. Treat the backup as sensitive business data.

## Verify a backup

Before relying on a snapshot, run SQLite's integrity check:

```bash
python - <<'PY'
import sqlite3
from pathlib import Path

backup = Path.home() / ".local/share/agent-entrepreneur/backups/data-2026-11-09.sqlite3"
with sqlite3.connect(backup) as db:
    result = db.execute("PRAGMA integrity_check").fetchone()[0]
if result != "ok":
    raise SystemExit(f"Backup integrity check failed: {result}")
print("Backup integrity check: ok")
PY
```

Also test restoration periodically in a separate, disposable location. A successful integrity check is not a substitute for a restore test.

## Restore

1. Stop every Agent Entrepreneur process using the target database. Do not replace a database while the server is running.
2. Preserve the current database and any relevant sidecar files in a separate recovery directory before changing anything.
3. Verify the selected backup with `PRAGMA integrity_check`.
4. Copy the verified backup to the configured database path. Do not overwrite the only copy of the current database.
5. On POSIX systems, set the restored database file to owner-only permissions: `chmod 600 /path/to/data.sqlite3`.
6. Restart Agent Entrepreneur and validate the expected memory/workflow records and application behavior.

For a safer rehearsal, restore to a temporary database path first by setting `AGENT_ENTREPRENEUR_DB` to that path, then start the application against the temporary copy and inspect it. Never point a test restore at the live database.

## Operational limitations

- Backups are unencrypted. Use encrypted storage or an encrypted volume when backups leave the local machine.
- The helper refuses symbolic-link source paths and existing destinations; keep the parent directory trusted and not writable by untrusted users.
- A backup file is created at its destination before the SQLite copy finishes. Do not treat a destination as a valid snapshot until the operation returns successfully and the integrity check passes.
- No automated retention, scheduling, off-site replication or restore command is provided in v0.1.
- This backup utility snapshots the configured SQLite database only. It does not back up application code, environment variables, credentials or external provider state.

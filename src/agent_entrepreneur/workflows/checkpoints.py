from __future__ import annotations

import json
from pathlib import Path

from agent_entrepreneur.agents.models import WorkflowCheckpoint
from agent_entrepreneur.storage.database import connect


class CheckpointStore:
    """SQLite-backed workflow checkpoint store; stores task state, never model chain-of-thought."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def save(self, run: WorkflowCheckpoint) -> WorkflowCheckpoint:
        payload = json.dumps(run.state, ensure_ascii=False, sort_keys=True)
        with connect(self.database_path) as db:
            db.execute(
                """
                INSERT INTO workflow_runs(id, status, state_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    state_json = excluded.state_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (run.workflow_id, run.status, payload),
            )
        return run

    def resume(self, run_id: str) -> WorkflowCheckpoint | None:
        with connect(self.database_path) as db:
            row = db.execute(
                "SELECT id, status, state_json FROM workflow_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return WorkflowCheckpoint(
            workflow_id=row["id"],
            status=row["status"],
            state=json.loads(row["state_json"]),
        )

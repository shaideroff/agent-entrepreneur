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
        if not run.workflow_id.strip():
            raise ValueError("workflow_id must not be empty")
        if run.status not in {"running", "completed", "partial", "failed"}:
            raise ValueError("checkpoint status is invalid")
        if not isinstance(run.state, dict):
            raise ValueError("checkpoint state must be an object")
        try:
            payload = json.dumps(run.state, ensure_ascii=False, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("checkpoint state must contain valid JSON values") from exc
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
        if row["status"] not in {"running", "completed", "partial", "failed"}:
            raise ValueError("stored checkpoint status is invalid")
        try:
            state = json.loads(row["state_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("stored checkpoint JSON is corrupt") from exc
        if not isinstance(state, dict):
            raise ValueError("stored checkpoint state must be an object")
        return WorkflowCheckpoint(
            workflow_id=row["id"],
            status=row["status"],
            state=state,
        )

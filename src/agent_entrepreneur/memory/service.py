from __future__ import annotations
import uuid
from pathlib import Path
from typing import Any
from agent_entrepreneur.storage.database import connect
class MemoryService:
    def __init__(self, database_path: Path) -> None: self.database_path = database_path
    def save(self, content: str, *, scope: str = "user", consent: bool = False) -> str:
        if not consent: raise PermissionError("Memory writes require explicit user consent.")
        record_id = str(uuid.uuid4())
        with connect(self.database_path) as db: db.execute("INSERT INTO memory(id, scope, content) VALUES (?, ?, ?)", (record_id, scope, content))
        return record_id
    def search(self, query: str = "", *, scope: str = "user") -> list[dict[str, Any]]:
        with connect(self.database_path) as db: rows = db.execute("SELECT id, scope, content, created_at FROM memory WHERE scope = ? AND content LIKE ? ORDER BY created_at DESC", (scope, f"%{query}%")).fetchall()
        return [dict(row) for row in rows]
    def export(self, *, scope: str = "user") -> dict[str, Any]: return {"scope": scope, "records": self.search(scope=scope)}
    def delete(self, record_id: str) -> bool:
        with connect(self.database_path) as db: cursor = db.execute("DELETE FROM memory WHERE id = ?", (record_id,))
        return cursor.rowcount > 0

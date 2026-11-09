from pathlib import Path
import pytest
from agent_entrepreneur.memory.service import MemoryService

def test_memory_requires_explicit_consent(tmp_path: Path):
    service = MemoryService(tmp_path / "memory.db")
    with pytest.raises(PermissionError): service.save("private strategy", consent=False)

def test_memory_save_search_export_delete(tmp_path: Path):
    service = MemoryService(tmp_path / "memory.db")
    record_id = service.save("pricing experiment", consent=True)
    assert service.search("pricing")
    assert service.export()["records"]
    assert service.delete(record_id)
    assert service.search("pricing") == []

def test_memory_search_and_export_are_scope_isolated(tmp_path: Path):
    service = MemoryService(tmp_path / "memory.db")
    user_record = service.save("user-only strategy", scope="user", consent=True)
    project_record = service.save("project-only pricing", scope="project:alpha", consent=True)

    assert [item["id"] for item in service.search(scope="user")] == [user_record]
    assert [item["id"] for item in service.search(scope="project:alpha")] == [project_record]
    assert service.search("project-only", scope="user") == []
    assert service.export(scope="user")["records"] == service.search(scope="user")


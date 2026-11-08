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

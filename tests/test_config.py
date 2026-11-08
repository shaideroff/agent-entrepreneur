from pathlib import Path
import pytest
from agent_entrepreneur.config import Settings

def test_defaults_to_stdio_and_local_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("AGENT_ENTREPRENEUR_DB", str(tmp_path / "data.sqlite3"))
    settings = Settings.from_env()
    assert settings.transport == "stdio" and settings.host == "127.0.0.1"

def test_rejects_unsafe_remote_http_binding(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("AGENT_ENTREPRENEUR_DB", str(tmp_path / "data.sqlite3"))
    monkeypatch.setenv("AGENT_ENTREPRENEUR_TRANSPORT", "streamable-http")
    monkeypatch.setenv("AGENT_ENTREPRENEUR_HOST", "0.0.0.0")
    with pytest.raises(ValueError, match="Non-loopback"): Settings.from_env()

from pathlib import Path

import pytest

from agent_entrepreneur.config import Settings, is_loopback_host


def configure_http(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, host: str = "127.0.0.1") -> None:
    monkeypatch.setenv("AGENT_ENTREPRENEUR_DB", str(tmp_path / "data.sqlite3"))
    monkeypatch.setenv("AGENT_ENTREPRENEUR_TRANSPORT", "streamable-http")
    monkeypatch.setenv("AGENT_ENTREPRENEUR_HOST", host)


def test_defaults_to_stdio_and_local_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("AGENT_ENTREPRENEUR_DB", str(tmp_path / "data.sqlite3"))
    settings = Settings.from_env()
    assert settings.transport == "stdio" and settings.host == "127.0.0.1"


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "LOCALHOST", "::1"])
def test_accepts_loopback_http_binding(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, host: str):
    configure_http(monkeypatch, tmp_path, host)
    assert Settings.from_env().host == host


def test_rejects_unsafe_remote_http_binding(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    configure_http(monkeypatch, tmp_path, "0.0.0.0")
    with pytest.raises(ValueError, match="Non-loopback"):
        Settings.from_env()


def test_rejects_remote_http_even_with_legacy_opt_in(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    configure_http(monkeypatch, tmp_path, "192.0.2.10")
    monkeypatch.setenv("AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP", "true")
    with pytest.raises(ValueError, match="authentication is configured"):
        Settings.from_env()


@pytest.mark.parametrize("host", ["", " bad host ", "example..com", "https://example.com", "[::1]", "bad_host"])
def test_rejects_malformed_host(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, host: str):
    configure_http(monkeypatch, tmp_path, host)
    with pytest.raises(ValueError, match="valid IP address or hostname"):
        Settings.from_env()


@pytest.mark.parametrize("port", ["abc", "0", "65536", "-1"])
def test_rejects_invalid_port(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, port: str):
    configure_http(monkeypatch, tmp_path)
    monkeypatch.setenv("AGENT_ENTREPRENEUR_PORT", port)
    with pytest.raises(ValueError, match="AGENT_ENTREPRENEUR_PORT"):
        Settings.from_env()


def test_rejects_unknown_transport(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("AGENT_ENTREPRENEUR_DB", str(tmp_path / "data.sqlite3"))
    monkeypatch.setenv("AGENT_ENTREPRENEUR_TRANSPORT", "http")
    with pytest.raises(ValueError, match="AGENT_ENTREPRENEUR_TRANSPORT"):
        Settings.from_env()


def test_rejects_ambiguous_remote_opt_in(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    configure_http(monkeypatch, tmp_path, "192.0.2.10")
    monkeypatch.setenv("AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP", "yes")
    with pytest.raises(ValueError, match="ALLOW_REMOTE_HTTP"):
        Settings.from_env()


def test_loopback_detection_does_not_trust_arbitrary_hostnames():
    assert is_loopback_host("::1")
    assert is_loopback_host("localhost")
    assert not is_loopback_host("localhost.example.com")
    assert not is_loopback_host("0.0.0.0")

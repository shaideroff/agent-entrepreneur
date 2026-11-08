"""Environment-backed application settings."""
from __future__ import annotations

import ipaddress
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast


def is_loopback_host(host: str) -> bool:
    """Return whether a host is a valid loopback IP or localhost name."""
    normalized = host.strip().rstrip(".").casefold()
    if normalized == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def _validate_host(host: str) -> None:
    if not host or host != host.strip() or any(char.isspace() for char in host):
        raise ValueError("AGENT_ENTREPRENEUR_HOST must be a valid IP address or hostname")
    try:
        ipaddress.ip_address(host)
        return
    except ValueError:
        pass
    normalized = host.rstrip(".")
    if len(normalized) > 253 or not normalized:
        raise ValueError("AGENT_ENTREPRENEUR_HOST must be a valid IP address or hostname")
    labels = normalized.split(".")
    if any(
        not label
        or len(label) > 63
        or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
        for label in labels
    ):
        raise ValueError("AGENT_ENTREPRENEUR_HOST must be a valid IP address or hostname")


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path
    transport: Literal["stdio", "streamable-http"] = "stdio"
    host: str = "127.0.0.1"
    port: int = 8765
    allow_remote_http: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        default_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        database_path = Path(os.environ.get("AGENT_ENTREPRENEUR_DB", default_dir / "agent-entrepreneur" / "data.sqlite3"))
        transport_raw = os.environ.get("AGENT_ENTREPRENEUR_TRANSPORT", "stdio").lower()
        if transport_raw not in {"stdio", "streamable-http"}:
            raise ValueError("AGENT_ENTREPRENEUR_TRANSPORT must be 'stdio' or 'streamable-http'")
        transport = cast(Literal["stdio", "streamable-http"], transport_raw)
        host = os.environ.get("AGENT_ENTREPRENEUR_HOST", "127.0.0.1")
        _validate_host(host)
        try:
            port = int(os.environ.get("AGENT_ENTREPRENEUR_PORT", "8765"))
        except ValueError as exc:
            raise ValueError("AGENT_ENTREPRENEUR_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("AGENT_ENTREPRENEUR_PORT must be between 1 and 65535")
        allow_remote_raw = os.environ.get("AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP", "false").casefold()
        if allow_remote_raw not in {"true", "false"}:
            raise ValueError("AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP must be 'true' or 'false'")
        allow_remote = allow_remote_raw == "true"
        if transport == "streamable-http" and not is_loopback_host(host):
            raise ValueError(
                "Non-loopback HTTP binding is disabled until authentication is configured"
            )
        parent = database_path.expanduser().parent
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ValueError(f"Database directory is not writable: {parent}") from exc
        return cls(database_path=database_path.expanduser(), transport=transport, host=host, port=port, allow_remote_http=allow_remote)

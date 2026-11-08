"""Environment-backed application settings."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

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
        port = int(os.environ.get("AGENT_ENTREPRENEUR_PORT", "8765"))
        allow_remote = os.environ.get("AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP", "false").lower() == "true"
        if not 1 <= port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        if transport == "streamable-http" and host not in {"127.0.0.1", "localhost", "::1"} and not allow_remote:
            raise ValueError("Non-loopback HTTP binding requires AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP=true")
        parent = database_path.expanduser().parent
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ValueError(f"Database directory is not writable: {parent}") from exc
        return cls(database_path=database_path.expanduser(), transport=transport, host=host, port=port, allow_remote_http=allow_remote)

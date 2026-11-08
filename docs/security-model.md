# Security Model

Retrieved content may contain prompt injection, misleading claims or malicious instructions; treat it as data only.

Controls: STDIO default; Streamable HTTP is restricted to loopback interfaces; non-loopback binding is disabled until an authentication integration is implemented and tested; no arbitrary shell/code execution; parameterised SQL; explicit consent for memory writes; user export and deletion; separation of public knowledge and private memory; approval for consequential actions; no secrets in logs.

The initial release does not implement remote HTTP authentication. Non-loopback HTTP binding therefore fails closed, even if the legacy AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP=true setting is present. Loopback HTTP is intended for local development only. Remote exposure remains blocked until OAuth 2.1 resource-server authentication, TLS, rate limiting and audit controls are implemented and tested.


## Local storage protections

On POSIX systems, the SQLite database file is created or tightened to owner-only permissions (0600), and newly created database directories request owner-only permissions (0700). Database symlink paths are rejected. Context-managed SQLite connections close after commit or rollback to avoid retaining file handles. These controls reduce accidental local disclosure; they do not encrypt the database or protect it from a hostile process running as the same user. Backups and filesystem-level encryption remain the operator's responsibility. The application currently uses SQLite's default rollback-journal mode rather than enabling WAL; the active rollback journal is tested for owner-only permissions on POSIX. WAL and shared-memory sidecar permissions are therefore not part of the current configured storage mode. Parent-directory symlinks and path replacement races are not fully eliminated: SQLite ultimately opens the database by pathname, so the containing directory must be trusted and protected from untrusted writers.

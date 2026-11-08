# MCP Client Setup and Compatibility

Agent Entrepreneur is a **Model Context Protocol (MCP) server**. It is designed to work with MCP-compatible clients rather than one specific model vendor. The client supplies model reasoning and any external research capability; this server exposes structured tools, resources, prompts, workflow checkpoints and local knowledge.

## Compatibility status

The configurations below are setup guidance based on each client's documented MCP configuration model. **They are not a declaration that every client/version has been integration-tested against this repository.** A client is marked Verified only after a reproducible connection test, tool discovery, representative tool calls, error-path checks and a recorded client/server version.

| Client | Configuration path | Current status | Release-gate test |
|---|---|---|---|
| OpenAI Codex CLI / IDE | `~/.codex/config.toml` or trusted project `.codex/config.toml` | Setup documented; runtime verification pending | Discover all tools/resources/prompts; execute a core workflow and resume |
| Claude Code | Project `.mcp.json` or supported user MCP configuration | Setup documented; runtime verification pending | Discover tools; run plan/complete/resume; validate permissions and errors |
| Claude Desktop | `claude_desktop_config.json` | Setup documented; runtime verification pending | Local STDIO startup, discovery, memory consent and restart |
| Cursor | `.cursor/mcp.json` or `~/.cursor/mcp.json` | Setup documented; runtime verification pending | Workspace/global config, discovery, representative tool calls |
| ChatGPT desktop / other MCP hosts | Client-specific MCP settings | Compatibility not yet certified | Validate supported transport and host-specific authentication/configuration |

Do not infer compatibility from MCP protocol support alone. Host implementations differ in configuration, supported protocol revisions, resource/prompt UX, timeout behavior and approval handling.

## 1. Install

Python 3.11 or newer is required.

### macOS / Linux

```bash
python3 -m venv ~/.venvs/agent-entrepreneur
~/.venvs/agent-entrepreneur/bin/python -m pip install --upgrade pip
~/.venvs/agent-entrepreneur/bin/python -m pip install agent-entrepreneur
```

### Windows (PowerShell)

```powershell
py -3.11 -m venv "$env:USERPROFILE\\.venvs\\agent-entrepreneur"
& "$env:USERPROFILE\\.venvs\\agent-entrepreneur\\Scripts\\python.exe" -m pip install --upgrade pip
& "$env:USERPROFILE\\.venvs\\agent-entrepreneur\\Scripts\\python.exe" -m pip install agent-entrepreneur
```

For a source checkout, install from the repository root with `python -m pip install .`. Use the absolute path to the installed executable in client configuration. The examples below use illustrative paths; replace them with the path on your machine.

## 2. OpenAI Codex

Codex supports MCP configuration in `~/.codex/config.toml`; trusted projects may also use `.codex/config.toml`. Add:

```toml
[mcp_servers.agent_entrepreneur]
command = "/home/YOUR_USER/.venvs/agent-entrepreneur/bin/agent-entrepreneur"
args = []
startup_timeout_sec = 20
tool_timeout_sec = 120
```

On Windows, use the absolute path to `agent-entrepreneur.exe` in your virtual environment's `Scripts` directory. Alternatively, register the server using the Codex CLI's `codex mcp add` command with the executable as the STDIO command.

Verify with:

```bash
codex mcp list
```

In the Codex TUI, use `/mcp` to inspect the active server and its available tools. Codex CLI and its IDE integration share the Codex MCP configuration.

## 3. Claude Code

Claude Code supports project-scoped MCP configuration. Create or update `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "agent-entrepreneur": {
      "command": "/home/YOUR_USER/.venvs/agent-entrepreneur/bin/agent-entrepreneur",
      "args": [],
      "env": {
        "AGENT_ENTREPRENEUR_TRANSPORT": "stdio"
      }
    }
  }
}
```

Use the matching absolute executable path on Windows or macOS. Start Claude Code from the project directory and inspect its MCP server/tool status. For one-off sessions, Claude Code also supports loading an MCP configuration file with its `--mcp-config` option. Do not use broad permission bypass flags to make the server appear to work.

## 4. Claude Desktop

Add the server under `mcpServers` in Claude Desktop's developer configuration file:

```json
{
  "mcpServers": {
    "agent-entrepreneur": {
      "command": "/home/YOUR_USER/.venvs/agent-entrepreneur/bin/agent-entrepreneur",
      "args": [],
      "env": {
        "AGENT_ENTREPRENEUR_TRANSPORT": "stdio"
      }
    }
  }
}
```

Typical configuration locations are:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`

Restart Claude Desktop after saving. Use its connectors/developer settings to confirm the server is connected and inspect available tools. Local STDIO configuration is distinct from remote custom connectors.

## 5. Cursor

Create or update `.cursor/mcp.json` in the project for workspace configuration, or `~/.cursor/mcp.json` for a personal global configuration:

```json
{
  "mcpServers": {
    "agent-entrepreneur": {
      "command": "/home/YOUR_USER/.venvs/agent-entrepreneur/bin/agent-entrepreneur",
      "args": [],
      "env": {
        "AGENT_ENTREPRENEUR_TRANSPORT": "stdio"
      }
    }
  }
}
```

Restart/reload Cursor and inspect the MCP server list in Customize. Cursor's approval controls should remain enabled for tools that write memory or change workflow state.

## 6. Verify a connection

A release-gating client test must verify all of the following, not merely that the process starts:

1. Server initializes over STDIO without protocol errors.
2. The host discovers all expected tools, resources and prompts.
3. The six core tools are discoverable: `understand_business`, `research_market`, `analyse_business`, `evaluate_decision`, `create_execution_plan`, `review_outcomes`.
4. Specialist workflow tools are discoverable: `plan_specialist_workflow`, `complete_specialist_workflow`, `resume_specialist_workflow`.
5. Knowledge/memory tools are discoverable: `search_entrepreneurs`, `save_memory`, `search_memory`, `delete_memory`.
6. The host can complete a plan/complete workflow with valid structured responses and evidence references.
7. A partial workflow can resume without changing its original request fingerprint.
8. Invalid inputs and malformed responses fail safely and return useful errors.
9. `save_memory` without explicit `consent=true` is rejected; deletion removes the selected memory record.
10. Restarting the client/server does not corrupt local SQLite state.

A successful MCP handshake does not prove all workflow behavior works. Record the client name/version, operating system, Python version, package version or commit, protocol SDK version, test date and pass/fail results before marking a client Verified.

## 7. Transport and security boundary

- STDIO is the supported default for local clients.
- Streamable HTTP is restricted to loopback; it is for local development only.
- Non-loopback HTTP is deliberately disabled. Do not expose the server publicly or rely on the legacy remote opt-in environment variable.
- Remote deployment is not currently supported as a production service. It requires implemented and tested authentication (including an appropriate OAuth 2.1 resource-server design), TLS, rate limiting, audit controls and deployment threat modelling.
- SQLite memory is local and not application-encrypted. Protect the host account, database path and backups.
- Keep client approval prompts enabled. Memory writes require explicit consent; consequential external actions remain outside the server's authority.

## 8. Troubleshooting

- **Executable not found:** configure the absolute path to the virtual environment executable.
- **Dependency/import errors:** install the package in the same environment referenced by the client.
- **Server exits immediately:** inspect the host's MCP logs and validate the configuration syntax.
- **Database permission error:** choose a writable, user-owned path; do not put the database in a shared or web-served directory.
- **No live market findings:** the core server does not bundle live web research. The tool reports that limitation rather than inventing current data.
- **Tool call timeout:** first reproduce with a smaller input and inspect host/server logs; do not increase timeouts to conceal a hang.

## 9. Release verification policy

The repository's CI protocol tests are necessary but not sufficient for third-party client certification. Each client entry remains **Setup documented / runtime verification pending** until a reproducible integration test is run and recorded. Client support claims must name tested versions and dates, and should be rechecked when either the client or MCP SDK changes.

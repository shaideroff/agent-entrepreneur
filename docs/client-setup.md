# MCP Client Setup

Agent Entrepreneur communicates with an MCP host over **STDIO**. The host starts the server as a local subprocess; do not launch a second server manually when using this mode.

## 1. Install in an isolated environment

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

For a source checkout instead of a package release, install with `python -m pip install .` from the repository root.

## 2. Configure your MCP host

Add a server entry to the host's MCP configuration. The example below uses the common `mcpServers` / `command` / `args` STDIO configuration shape. The exact configuration file location and reload procedure depend on your MCP host.

### macOS / Linux example

```json
{
  "mcpServers": {
    "agent-entrepreneur": {
      "command": "/home/YOUR_USER/.venvs/agent-entrepreneur/bin/agent-entrepreneur",
      "args": [],
      "env": {
        "AGENT_ENTREPRENEUR_TRANSPORT": "stdio",
        "AGENT_ENTREPRENEUR_DB": "/home/YOUR_USER/.local/share/agent-entrepreneur/data.sqlite3"
      }
    }
  }
}
```

Replace `/home/YOUR_USER` with the actual absolute path for your account. On macOS, use the equivalent path under `/Users/YOUR_USER`.

### Windows example

```json
{
  "mcpServers": {
    "agent-entrepreneur": {
      "command": "C:\\Users\\YOUR_USER\\.venvs\\agent-entrepreneur\\Scripts\\agent-entrepreneur.exe",
      "args": [],
      "env": {
        "AGENT_ENTREPRENEUR_TRANSPORT": "stdio",
        "AGENT_ENTREPRENEUR_DB": "C:\\Users\\YOUR_USER\\AppData\\Local\\agent-entrepreneur\\data.sqlite3"
      }
    }
  }
}
```

Replace `YOUR_USER` with the Windows account directory. If your host does not support an `env` map, set the variables in its launch environment and keep the command as an absolute executable path.

## 3. Verify the connection

After saving the host configuration, restart or reload the host. Confirm that it discovers:

- Core tools: `understand_business`, `research_market`, `analyse_business`, `evaluate_decision`, `create_execution_plan`, `review_outcomes`.
- Specialist workflow tools: `plan_specialist_workflow`, `complete_specialist_workflow`, `resume_specialist_workflow`.
- Knowledge and memory tools: `search_entrepreneurs`, `save_memory`, `search_memory`, `delete_memory`.
- Resources: `agent-entrepreneur://knowledge/specialists` and `agent-entrepreneur://knowledge/entrepreneurs`.
- Prompts: `business_diagnosis`, `market_entry_assessment`, `founder_execution_review`.

A successful connection only confirms MCP protocol connectivity. The host performs specialist reasoning between the planning and completion calls; Agent Entrepreneur does not embed a model provider or bundled client. `save_memory` requires `consent=true`. The server does not provide live web research, external integrations, or permission to execute consequential business actions.

## Troubleshooting

- **Executable not found:** use the full absolute path to the virtual environment's executable.
- **Python or dependency errors:** install the package using the same virtual environment referenced by the executable.
- **Server starts and immediately exits:** inspect the MCP host's server logs and validate the JSON configuration.
- **Database permission error:** choose a writable path owned by your user account; do not place the database in a shared or publicly served directory.
- **No live market findings:** the core server does not include a live research provider. The tool reports this limitation rather than inventing current data.

## Transport and security boundary

STDIO is the supported default. Local Streamable HTTP is loopback-only. Non-loopback HTTP binding is disabled until an authenticated remote deployment is implemented and tested. Do not expose the server to a network by changing the bind host or relying on the legacy remote opt-in setting.

Use the [specialist workflow protocol](specialist-workflows.md) for the plan/complete/resume lifecycle, structured findings and provenance requirements. Client-specific configuration locations and compatibility vary by client release. The repository's protocol tests validate the MCP STDIO contract against MCP SDK 1.9.0 and the latest SDK in CI; they do not certify every third-party host/version combination.

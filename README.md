# Agent Entrepreneur

**A local-first, model-independent MCP server for entrepreneurial intelligence.**

Agent Entrepreneur helps a connected AI client structure business context, prepare market research, analyse supplied metrics, evaluate decisions, create execution plans and review outcomes. Its knowledge registry and specialist catalogue provide evidence-linked entrepreneurial reference material without impersonating real people.

> **Status: early development (v0.1.0).** This is an initial implementation, not a production-ready autonomous agent platform. Live market research, model reasoning and broad client compatibility depend on the connected client and its configured tools.

## Principles

- MCP server only; the connected AI client supplies model reasoning.
- No mandatory model-provider API key, hosted account or subscription.
- Local-first SQLite storage; memory writes require explicit consent.
- Facts, assumptions, unknowns and recommendations remain distinguishable.
- Entrepreneur profiles include attribution and evidence levels.
- No impersonation, implied endorsement or fabricated founder experience.
- No autonomous spending, customer contact, publishing or binding decisions.
- Retrieved content is untrusted input; consequential actions require human approval.

## Capabilities

Six core MCP tools: `understand_business`, `research_market`, `analyse_business`, `evaluate_decision`, `create_execution_plan`, `review_outcomes`.

The server also exposes entrepreneur and specialist catalogue resources plus reusable business-diagnosis, market-entry and founder-execution prompts.

## Requirements and install

Python 3.11+ and an MCP-compatible AI client.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e '.[dev]'
agent-entrepreneur
```

STDIO is the default transport. SQLite defaults to `~/.local/share/agent-entrepreneur/data.sqlite3` (or `$XDG_DATA_HOME`). Override with `AGENT_ENTREPRENEUR_DB`.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `AGENT_ENTREPRENEUR_DB` | platform data directory | SQLite database path |
| `AGENT_ENTREPRENEUR_TRANSPORT` | `stdio` | `stdio` or `streamable-http` |
| `AGENT_ENTREPRENEUR_HOST` | `127.0.0.1` | HTTP bind host |
| `AGENT_ENTREPRENEUR_PORT` | `8765` | HTTP port |
| `AGENT_ENTREPRENEUR_ALLOW_REMOTE_HTTP` | `false` | Explicit opt-in for non-loopback binding |

HTTP mode is not enabled by default. Do not expose it publicly without authenticated TLS protection and a deployment-specific security review.

## Development checks

```bash
pytest -q
ruff check .
ruff format --check .
mypy src
```

## Evidence levels

- **A:** strong primary evidence plus independent corroboration.
- **B:** credible, traceable documentation; corroboration may be incomplete.
- **C:** emerging or limited public evidence; verify before relying on claims.
- **unverified:** discovery candidate or founder-contributed material not independently corroborated.

Labels are triage aids, not blanket validation of every claim. Each substantive claim should be tied to its own source. S Haider's founder-contributed `Built from Zero` material is attributed and marked unverified until corroborated.

## Limitations

The core server does not itself browse the live web, call an LLM, execute code, contact customers or perform transactions. `research_market` reports when no research provider is configured rather than inventing current findings. The specialist orchestration module prepares bounded specialist tasks; the connected client performs the reasoning.

See [SECURITY.md](SECURITY.md), [docs/security-model.md](docs/security-model.md) and [docs/knowledge-and-evidence.md](docs/knowledge-and-evidence.md).

## Licence

Apache-2.0. See [LICENSE](LICENSE).

# Architecture

Agent Entrepreneur is an MCP server. The connected MCP host supplies model inference and user interaction. The server provides typed workflow preparation, local persistence, entrepreneur knowledge resources, prompts and bounded specialist task planning.

Layers: `domain` (Pydantic contracts), `services` (deterministic workflows), `knowledge` (attributed profiles), `agents` (bounded specialist planning), `memory` and `storage` (local SQLite), `security` (approval policy), and `server` (MCP registration).

Request lifecycle: validate input; perform deterministic checks; return structured facts, assumptions and evidence gaps; let the connected client reason; require approval before consequential actions.

Specialists are versionable role definitions, not simulated identities. The current orchestrator prepares specialist tasks; it does not claim to run autonomous model subagents.

Public seed data is shipped with the package. User memory and workflow state are local. Private memory is never automatically added to shared knowledge.

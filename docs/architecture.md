# Architecture

Agent Entrepreneur is an MCP server. The connected MCP host supplies model inference and user interaction. The server provides typed workflow preparation, local persistence, entrepreneur knowledge resources, prompts and bounded specialist task planning.

Layers: `domain` (Pydantic contracts), `services` (deterministic workflows), `knowledge` (attributed profiles), `agents` (bounded specialist planning), `memory` and `storage` (local SQLite), `security` (approval policy), and `server` (MCP registration).

Request lifecycle: validate input; perform deterministic checks; return structured facts, assumptions and evidence gaps; let the connected client reason; require approval before consequential actions.

Specialists are versionable role definitions, not simulated identities. The current orchestrator prepares specialist tasks; it does not claim to run autonomous model subagents.

Public seed data is shipped with the package. User memory and workflow state are local. Private memory is never automatically added to shared knowledge.


## Specialist orchestration runtime

The `agents` package provides a bounded, role-based orchestration layer. The caller supplies an executor callback backed by its connected model/client; the MCP server does not embed a model provider or pretend to run independent hidden LLM instances. Specialist assignments carry the role, documented methodology, objective, task context and a separately labelled untrusted-material field.

The orchestrator runs selected specialists sequentially, validates response attribution, consolidates findings, recommendations, risks, challenges/disagreements, unknowns and evidence references, and preserves completed work if a later specialist fails. Selection and step limits are enforced in code. Role definitions are not impersonations of the entrepreneurs or practitioners whose documented methods inform them.

`CheckpointStore` persists workflow state in the existing SQLite `workflow_runs` table. Checkpoints contain execution state and structured specialist outputs only; they must not contain hidden chain-of-thought or silently capture raw conversations. The current runtime creates resumable records and supports lookup by workflow ID; automatic continuation/replay of unfinished specialist tasks is a subsequent enhancement.


Partial specialist workflows retain structured outputs in SQLite. `Orchestrator.resume(...)` reloads those outputs, verifies their attribution against the supplied specialist plan, skips completed specialists and continues from the next unfinished assignment under the same workflow ID. Completed workflows cannot be resumed. The caller must provide the same ordered specialist plan and request context; checkpoints do not persist credentials, private model chain-of-thought or arbitrary provider state.


Checkpoint recovery validates the stored status and JSON shape before exposing state to the orchestrator. Corrupt JSON, non-object state and invalid statuses are rejected. Resume is bound to the exact saved objective and revalidates all persisted specialist findings against the evidence registry supplied by the caller. These checks protect against accidental corruption and cross-task reuse; SQLite checkpoint files remain local application data and are not cryptographically tamper-proof against a hostile local user.

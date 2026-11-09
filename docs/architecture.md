# Architecture

Agent Entrepreneur is a public, model-independent MCP server. The connected MCP host supplies model inference, live research tools and user interaction. Agent Entrepreneur provides six core business capabilities, a twelve-discipline specialist catalogue, source-aware entrepreneur knowledge, consent-gated local memory, workflow checkpoints and structured result validation.

Layers:
- `domain`: typed business contracts.
- `services`: deterministic business workflow logic.
- `knowledge`: attributed entrepreneur profiles and claim-level evidence.
- `agents`: bounded specialist planning, response validation and synthesis.
- `memory` and `storage`: local SQLite persistence.
- `workflows`: durable checkpoint state and safe continuation.
- `security`: approval policy and fail-closed transport configuration.
- `server`: MCP tool, resource and prompt registration.

## Request lifecycle

1. The MCP client calls a core business tool or asks the server to plan a specialist workflow.
2. The server validates input and returns structured business context, evidence gaps or specialist assignments.
3. The connected client performs reasoning and any permitted research; retrieved content remains untrusted data.
4. The client submits structured specialist findings and claim records to the server.
5. The server verifies that completion matches the original plan, validates specialist attribution and claim/source identifiers, persists checkpoints and consolidates findings, recommendations, risks, disagreements, unknowns and limitations.
6. The client presents the result and obtains user approval before any consequential external action.

## Specialist orchestration

The `agents` package provides twelve analytical disciplines. Roles are reusable methods and evaluation rubrics, not simulated identities or endorsements. The caller supplies the reasoning; the server does not embed an LLM provider or claim hidden autonomous model subagents.

The MCP workflow tools are:
- `plan_specialist_workflow`: deterministic, bounded role selection and assignment; persists the planned request fingerprint.
- `complete_specialist_workflow`: accept one structured response per planned specialist, validate provenance and persist progress.
- `resume_specialist_workflow`: validate the original request and ordered plan, reload completed work, and execute only unfinished specialists.

Checkpoint identity is bound to a SHA-256 fingerprint of the objective, context, untrusted material, execution limits, ordered specialist assignments and canonicalised evidence claim/source registry. A mismatched request or plan is rejected. Legacy empty checkpoints can resume only when their objective matches and no specialist output has been completed. Recovery is at-least-once: an interrupted specialist may be invoked again if it had not yet been checkpointed. Executor callbacks must therefore be analysis-only and side-effect-free.

## Knowledge and evidence

Entrepreneur profiles carry region, expertise, ventures, methods, decisions, outcomes, evidence level, confidence, attribution, update date and source metadata. The current seed contains 18 profiles across eight regions; the 100-profile catalogue is a longer-term research target. Empty methods, decisions or outcomes mean they have not yet been researched and are not to be invented.

Evidence claims use explicit claim status, evidence level, scope, source metadata, limitations and contradictions. The server enforces identifier-level provenance, not semantic entailment: it does not prove that a source logically entails a finding. A reviewer or connected model must assess source relevance and truth.

## Memory and privacy

Local memory writes require explicit consent. Memory and workflow checkpoints share the configured SQLite database but remain separate from the public entrepreneur knowledge registry. The server exposes memory search and deletion. SQLite is not encrypted by the application; operators must protect local files and backups. Do not store credentials or secrets.

## Transport and deployment

STDIO is the supported default. Streamable HTTP is restricted to loopback. Non-loopback binding is disabled until an authenticated remote deployment with TLS, rate limiting and audit controls is implemented and tested.

The core server does not browse the live web, execute arbitrary code, contact customers, publish content, spend money or make binding business decisions. Market research sources must be supplied by the connected client or a separately configured research integration.

## Entrepreneur experience agents (v1.1 development)

The additive `agents.experience_catalogue` layer exposes a twelve-entry public directory and loads versioned JSON dossiers from package data. Six pilot dossiers currently exist: Built from Zero (first-party founder-contributed material), Sara Blakely, Jeff Bezos, Warren Buffett, Jensen Huang and Brian Chesky. All entries remain Preview pending evaluation and release gates.

MCP tools expose discovery, profile retrieval, dossier-grounded individual work packets, bounded Lead shortlist routing, Lead-selected council work packets and council synthesis. Lead routing is currently a deterministic keyword/domain heuristic and returns its inferred domains and limitations. Council preparation produces independent assignments and a host-executable challenge protocol without claiming the server runs agent models. It is not semantic LLM reasoning. The connected host performs independent agent analysis and generates any adversarial challenges. The server validates claim-level fact-to-source mappings, challenge participants and evidence references, and binds each challenged statement to a statement in the target contribution before preserving it in synthesis.

Dossiers validate source references and unique source, principle and decision-case identifiers. Configured dossier files fail closed when missing or malformed. The server does not assert that a source semantically proves a claim; it preserves provenance so the connected host and human reviewer can assess relevance.

# Agent Entrepreneur v1.1 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a backward-compatible global entrepreneur experience-agent layer with six evidence-gated pilot agents, direct agent selection, and a neutral Lead Entrepreneur council workflow.

**Architecture:** Extend the existing Python MCP server rather than replacing it. Reuse the current agent registry, orchestration runtime, knowledge/evidence registry, workflow checkpoints and security approval boundaries; add versioned experience-agent dossiers and typed interfaces around them. Keep the twelve-person founding cohort as catalogue metadata, but expose only dossiers that pass the evidence and evaluation gates as active agents.

**Tech Stack:** Python 3.11+, Pydantic v2, MCP SDK 1.x, SQLite/current storage abstractions, JSON package data, pytest, Ruff and mypy.

## Implementation status (2026-11-09)

This plan is the approved target architecture; the implementation is being delivered incrementally on PR #14. The current branch contains:
- Typed Pydantic experience-agent, dossier, challenge and council contracts.
- Twelve-entry public catalogue; six versioned Preview dossiers (Built from Zero, Sara Blakely, Jeff Bezos, Warren Buffett, Jensen Huang and Brian Chesky).
- Claim/source linkage, unique identifier validation and fail-closed handling for missing configured dossiers.
- MCP discovery, profile, work-packet, deterministic Lead shortlist and host-supplied council challenge/synthesis tools.
- Structural evaluation fixtures covering six scenario classes for each pilot.
- Updated public docs and package-data inclusion.

**Not yet certified:** independent agent execution, semantic/model-based Lead reasoning, automatic challenge generation, scenario-based evaluation of a connected model, third-party client end-to-end runs, secure remote hosting, full CI verification and stable release certification. The server intentionally remains local-first and does not expose unauthenticated remote HTTP.

The task checkboxes below are a historical implementation checklist; they are not evidence that tests ran. Mark a verification step complete only after its command or CI check has actually passed.

## Global Constraints

- Preserve the v1.0 MCP foundation and all existing tool names, input/output contracts and behaviour.
- Keep the current generic specialist disciplines as reusable skills; do not expose them as named entrepreneur personas.
- Offer two equal entry points: direct work with a named Experience Agent and work with the neutral Lead Entrepreneur. Support an explicit Expert Council mode.
- Named agents are AI research assistants applying publicly documented experience. They must not claim to be the real person, speak for them, imply endorsement, fabricate private thoughts, or use deceptive first-person roleplay.
- Every material claim about an entrepreneur's methods, decisions or outcomes must have claim-level source provenance. Preserve evidence labels: verified, corroborated, partially supported, unverified and disputed.
- Dossiers must include counter-evidence, failures/setbacks, transfer conditions, limitations, source registry, evaluation set and version metadata. Success-only biographies are insufficient.
- The proposed founding roster has twelve entries; the six pilot entries are S Haider, Sara Blakely, Jeff Bezos, Warren Buffett, Jensen Huang and Brian Chesky. A catalogue entry is not active merely because it exists.
- S Haider is the named founder and public-facing entrepreneur behind Built from Zero. Attribute material from S Haider's own journey as first-party founder experience; apply provenance and evidence status at the individual claim level. Do not assign a profile-level verification status or require independent corroboration for profile recognition.
- The Lead selects the smallest useful council, explains agent selection, obtains independent analysis before challenge, preserves disagreement and produces one synthesis.
- Cross-agent memory sharing is opt-in, task-scoped and provenance-preserving. Sensitive personal data and secrets must not be stored.
- No external consequential action may be taken without user approval. No autonomous spending, publishing, customer contact or binding decision-making.
- Do not ingest copyrighted books or paid-course material as substitutes for original research. Use concise original summaries with citations.
- No new hosted service, web UI, vector database or mandatory external API is introduced in this increment.

---

### Task 1: Define the experience-agent and dossier contracts

**Files:**
- Create: `src/agent_entrepreneur/agents/experience_models.py`
- Create: `src/agent_entrepreneur/knowledge/dossier_models.py`
- Create: `tests/test_experience_models.py`
- Create: `tests/test_dossier_models.py`
- Modify: `src/agent_entrepreneur/agents/__init__.py`
- Modify: `src/agent_entrepreneur/knowledge/__init__.py`

**Interfaces:**
- Produce `ExperienceAgentStatus`, `ExperienceAgentRecord`, `ExperienceAgentSelection`, `ExperienceAgentResponse` and `CouncilSynthesis` Pydantic models.
- Produce `EvidenceStatus`, `SourceRecord`, `PrincipleRecord`, `DecisionCaseRecord`, `CounterEvidenceRecord`, `TransferCondition` and `ExperienceDossier` Pydantic models.
- Dossier references must be stable IDs; source references must be resolvable within the dossier or its source registry.
- Model fields should represent the approved specification without inventing additional mandatory profile facts.

- [ ] **Step 1: Add the focused failing tests**

Test valid and invalid evidence status values; required source identifiers; principle-to-source references; dossier version metadata; explicit non-endorsement text; preview versus active status; response separation of documented fact, interpretation, analogy and recommendation; and round-trip JSON serialization.

- [ ] **Step 2: Verify the relevant failure**

Run: `pytest tests/test_experience_models.py tests/test_dossier_models.py -q`

Expected: collection fails because the new model modules and interfaces do not yet exist.

- [ ] **Step 3: Implement the minimum contracts**

Use Pydantic v2 models and typed enums/literals. Keep provenance references explicit. Do not add database behaviour or network access to these model modules. Export the stable public types from package initializers.

- [ ] **Step 4: Verify the focused pass**

Run: `pytest tests/test_experience_models.py tests/test_dossier_models.py -q`

Expected: all model and serialization assertions pass.

- [ ] **Step 5: Run affected integration checks**

Run: `pytest tests/test_profile_schema.py tests/test_evidence.py tests/test_evidence_boundary.py -q`

Expected: existing profile and evidence contracts remain unchanged and pass.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add src/agent_entrepreneur/agents/experience_models.py src/agent_entrepreneur/knowledge/dossier_models.py src/agent_entrepreneur/agents/__init__.py src/agent_entrepreneur/knowledge/__init__.py tests/test_experience_models.py tests/test_dossier_models.py
git commit -m "feat: define entrepreneur experience agent contracts"
```

### Task 2: Add the versioned experience-agent registry and pilot dossiers

**Files:**
- Create: `src/agent_entrepreneur/agents/experience_registry.py`
- Create: `src/agent_entrepreneur/knowledge/dossier_registry.py`
- Create: `src/agent_entrepreneur/knowledge/seed_data/experience_agents.json`
- Create: `src/agent_entrepreneur/knowledge/seed_data/dossiers/` (one JSON dossier per pilot agent)
- Create: `tests/test_experience_registry.py`
- Create: `tests/test_dossier_registry.py`
- Modify: `pyproject.toml` only if package-data patterns need to include nested dossier JSON files.

**Interfaces:**
- `list_experience_agents(status: ExperienceAgentStatus | None = None) -> list[ExperienceAgentRecord]`
- `get_experience_agent(agent_id: str) -> ExperienceAgentRecord | None`
- `get_experience_dossier(agent_id: str, version: str | None = None) -> ExperienceDossier | None`
- `get_agent_evidence_coverage(agent_id: str) -> EvidenceCoverage`
- Registry loaders consume packaged JSON and produce the typed models from Task 1.

- [ ] **Step 1: Add the focused failing tests**

Assert that the twelve proposed roster entries have stable IDs and catalogue metadata; only evidence-gated pilot dossiers are active; preview agents cannot be selected for production work; dossier versions resolve deterministically; missing or malformed dossier files fail closed; every material principle/case has source references; and claim-level evidence statuses are preserved without assigning a profile-level verification status to S Haider.

- [ ] **Step 2: Verify the relevant failure**

Run: `pytest tests/test_experience_registry.py tests/test_dossier_registry.py -q`

Expected: collection fails because registry modules and catalogue data do not yet exist.

- [ ] **Step 3: Implement the minimum registry and research records**

Create a machine-readable twelve-entry catalogue. Seed dossier records for the six pilot agents only after source research is completed and recorded. Each dossier must include documented principles, dated cases, counter-evidence/failures, transfer conditions, out-of-scope domains, source registry, evaluation references and review metadata. Mark incomplete or insufficiently supported dossiers as Preview; do not invent evidence to make an agent Active. Keep each dossier self-contained and traceable to public sources.

- [ ] **Step 4: Verify the focused pass**

Run: `pytest tests/test_experience_registry.py tests/test_dossier_registry.py -q`

Expected: registry selection, version resolution, provenance and fail-closed assertions pass.

- [ ] **Step 5: Run affected integration checks**

Run: `pytest tests/test_knowledge_agents.py tests/test_profile_schema.py tests/test_evidence.py -q`

Expected: legacy entrepreneur profile search and knowledge retrieval remain compatible.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add src/agent_entrepreneur/agents/experience_registry.py src/agent_entrepreneur/knowledge/dossier_registry.py src/agent_entrepreneur/knowledge/seed_data/experience_agents.json src/agent_entrepreneur/knowledge/seed_data/dossiers pyproject.toml tests/test_experience_registry.py tests/test_dossier_registry.py
git commit -m "feat: add evidence-gated experience agent catalogue"
```

### Task 3: Integrate direct agent work and Lead Entrepreneur council orchestration

**Files:**
- Create: `src/agent_entrepreneur/agents/experience_runtime.py`
- Create: `src/agent_entrepreneur/agents/lead_entrepreneur.py`
- Modify: `src/agent_entrepreneur/agents/orchestrator.py`
- Modify: `src/agent_entrepreneur/server.py`
- Modify: `src/agent_entrepreneur/workflows/checkpoints.py` only for additive, backward-compatible checkpoint state.
- Create: `tests/test_experience_runtime.py`
- Create: `tests/test_lead_entrepreneur.py`
- Create: `tests/test_experience_mcp_tools.py`

**Interfaces:**
- `prepare_experience_agent_work(agent_id: str, objective: str, context: dict[str, object]) -> ExperienceAgentWorkPacket`
- `select_experience_council(objective: str, context: dict[str, object], requested_agent_ids: list[str] | None = None) -> ExperienceAgentSelection`
- `synthesise_experience_council(objective: str, contributions: list[ExperienceAgentResponse]) -> CouncilSynthesis`
- Additive MCP tools: `list_experience_agents`, `get_experience_agent`, `work_with_experience_agent`, `plan_experience_council`, `complete_experience_council`.
- These tools prepare and coordinate work for the connected model/client; they do not embed a new LLM or claim that the server itself generated model reasoning.

- [ ] **Step 1: Add the focused failing tests**

Test direct selection of an active agent; rejection of unknown and Preview agents for active work; dossier context and citations included in work packets; Lead selection rationale; one-agent simple work; bounded council selection; explicit user-selected council; independent contribution ordering; challenge references to concrete claims; preservation of disagreement; missing contribution handling; workflow checkpoint/resume; and unchanged v1.0 MCP tool schemas.

- [ ] **Step 2: Verify the relevant failure**

Run: `pytest tests/test_experience_runtime.py tests/test_lead_entrepreneur.py tests/test_experience_mcp_tools.py -q`

Expected: collection fails because the experience runtime and additive MCP tools do not yet exist.

- [ ] **Step 3: Implement the additive runtime**

Build work packets from dossier-backed principles and evidence. Use the existing specialist workflow machinery for reusable methods, but keep named Experience Agents distinct from generic disciplines. Lead selection must use declared domain/capability metadata, return a reason for every selected agent and choose the smallest useful set. Council flow must capture independent outputs before challenge, preserve disagreement and identify unresolved evidence. Add tools without renaming or changing existing v1.0 tools. Reuse existing approval gates for consequential actions and existing checkpoint semantics for resumability.

- [ ] **Step 4: Verify the focused pass**

Run: `pytest tests/test_experience_runtime.py tests/test_lead_entrepreneur.py tests/test_experience_mcp_tools.py -q`

Expected: all direct-agent, council, provenance, checkpoint and tool-schema assertions pass.

- [ ] **Step 5: Run affected integration checks**

Run: `pytest tests/test_orchestration_runtime.py tests/test_resume_integrity.py tests/test_security_approvals.py tests/test_mcp_protocol.py -q`

Expected: legacy orchestration, resume integrity, approval boundaries and MCP protocol compatibility pass.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add src/agent_entrepreneur/agents/experience_runtime.py src/agent_entrepreneur/agents/lead_entrepreneur.py src/agent_entrepreneur/agents/orchestrator.py src/agent_entrepreneur/server.py src/agent_entrepreneur/workflows/checkpoints.py tests/test_experience_runtime.py tests/test_lead_entrepreneur.py tests/test_experience_mcp_tools.py
git commit -m "feat: add lead entrepreneur and experience council"
```

### Task 4: Add evaluation gates, documentation and v1.1 release verification

**Files:**
- Create: `tests/evaluations/experience_agents/` (one versioned evaluation set per active pilot agent)
- Create: `tests/test_experience_evaluations.py`
- Create: `docs/experience-agents.md`
- Create: `docs/lead-entrepreneur-council.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/architecture.md`
- Modify: `docs/knowledge-and-evidence.md`

**Interfaces:**
- Evaluation cases consume an agent ID, dossier version and objective/context fixture; they assert required reasoning traits and prohibited claims, not exact generative wording.
- Documentation describes the MCP tools, status/evidence semantics, council lifecycle, privacy boundaries and known limitations.

- [ ] **Step 1: Add the focused failing tests**

Create evaluation fixtures for each pilot covering an in-domain problem, an out-of-domain problem, a principle-transfer mismatch, contradictory evidence, a known failure/counterexample, missing sources, and a prompt that attempts deceptive impersonation. Assert claim attribution, limitation disclosure, refusal to invent private knowledge, and appropriate escalation. Add a regression fixture ensuring legacy tools and profile workflows remain available.

- [ ] **Step 2: Verify the relevant failure**

Run: `pytest tests/test_experience_evaluations.py -q`

Expected: collection fails until the evaluation runner and fixtures are present.

- [ ] **Step 3: Implement evaluation and user-facing documentation**

Add deterministic structural evaluation for dossier provenance, agent status, evidence coverage and required response fields. Add scenario-based tests against the connected-model contract without requiring a live model in CI. Document that model-generated quality still depends on the MCP client/model and that no actual entrepreneur is speaking. Update README and changelog only after the features and gates exist.

- [ ] **Step 4: Verify the focused pass**

Run: `pytest tests/test_experience_evaluations.py -q`

Expected: all dossier and behavioural regression cases pass.

- [ ] **Step 5: Run full quality and compatibility checks**

Run:
```bash
pytest
ruff check .
mypy src
python -m build
```

Expected: full test suite passes with the configured coverage threshold; Ruff and mypy report no errors; package build completes. Then run the repository's existing CI and MCP compatibility workflows on the release candidate.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add tests/evaluations/experience_agents tests/test_experience_evaluations.py docs/experience-agents.md docs/lead-entrepreneur-council.md README.md CHANGELOG.md docs/architecture.md docs/knowledge-and-evidence.md
git commit -m "docs: document and validate experience agent release"
```

---

## Unresolved externally observable decisions

1. **Public catalogue exposure:** Should all twelve roster entries be visible immediately as Preview, or should the public directory show only the six pilot agents until the remaining dossiers are researched? Recommendation: show all twelve with explicit Preview status, and allow active work only with evidence-gated agents.
2. **Evidence coverage display:** Which public-facing scale should be used (percentage, source-count bands, or qualitative labels)? Recommendation: use qualitative labels plus last-verified date; do not present a numeric score until its calculation is validated.
3. **Lead council size:** The product specification calls for the smallest useful council but does not set a hard maximum. Recommendation: default to one agent for simple requests, two to four for cross-functional work, and cap automatic selection at five unless the user explicitly asks for more.
4. **Custom user-authored agents:** Whether to include private agents built from a user's own documents in v1.1 or defer them. Recommendation: defer to a later increment after consent, source provenance, tenant isolation and deletion controls are designed.

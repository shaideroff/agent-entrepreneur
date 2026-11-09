# Global Experience-Agent Directory and MCP Interface

## Scope

The v1.1 foundation adds a public, machine-readable directory of 12 named entrepreneur experience-agent concepts. It exposes directory discovery, profile lookup and deterministic council routing through MCP. It does **not** claim that all 12 agents are fully researched, independently validated or executable autonomous agents.

All 12 catalogue entries currently have lifecycle status `preview`. This is intentional: an entry can be discoverable without representing that its dossier, evaluation suite and operational behaviour have passed release gates.

## MCP tools

### `prepare_experience_agent_work_packet`

Inputs: an agent ID, objective, optional business context and constraints. For a catalogue entry with a validated dossier, returns a structured work packet containing the dossier, source IDs, host instructions and required response fields. Six pilot dossiers are available in Preview mode: first-party Built from Zero, plus public-source dossiers for Sara Blakely, Jeff Bezos, Warren Buffett, Jensen Huang and Brian Chesky. Other entries without a dossier return `not_ready`; the system does not invent dossiers to make the directory appear complete.

### `discover_experience_agents`

Inputs:
- `query` (optional): substring search across ID, name, lens and domains.
- `domain` (optional): substring filter over capability domains.
- `status` (optional): `active`, `preview` or `retired`.

Returns the matching catalogue entries, lifecycle status, capability domains, availability note and non-affiliation notice.

### `get_experience_agent_profile`

Input: `agent_id`.

Returns one catalogue entry. Unknown IDs produce a validation error.

### `synthesize_experience_agent_council`

Inputs include the objective, one to five host-produced agent contributions, a recommendation, agreements, disagreements, unresolved questions and optional adversarial challenges. Contributions may include claim-level `fact_evidence` records mapping each documented fact to dossier source IDs and an explicit evidence status. Each challenge identifies a challenger, target, challenged statement, rationale, evidence references and severity. Evidence references must resolve to a source, principle or decision-case ID in a dossier represented in the council; the challenged statement must match text in the target contribution. The server validates council membership and structure, then returns one synthesis object that preserves disagreement. Challenge generation and reasoning remain the connected host's responsibility; the server does not independently generate or verify contributions or challenges.

### `recommend_experience_agent_council`

Inputs:
- `objective`: non-empty task objective.
- `domains` (optional): user/client-supplied capability domains; if omitted, deterministic keyword hints are inferred from the objective.
- `max_agents`: integer from 1 to 5 (default 4).

Returns a bounded shortlist using explicit domain matches and transparent objective-keyword hints, including inferred domains, rationale, unmatched domains and an execution boundary. This is a deterministic heuristic, not semantic model reasoning. It does not invoke the named people, generate their opinions or execute agent reasoning. Supply explicit domains for higher precision.

## Founding directory

1. S Haider — Built from Zero
2. Sara Blakely — Bootstrapped Consumer Brand
3. Jeff Bezos — Customer Obsession & Scale
4. Warren Buffett — Capital Allocation
5. Steve Jobs — Product Focus & Experience
6. Jensen Huang — Deep Technology & AI Strategy
7. Brian Chesky — Marketplace & Experience Design
8. Deepinder Goyal — Consumer Platform Execution
9. Markus Villig — Mobility & Hyperlocal Marketplace
10. Mohamed Alabbar — Real Estate & Large-Scale Development
11. Indra Nooyi — Strategic Transformation & Leadership
12. Tony Fernandes — Low-Cost Operations & Market Expansion

## Initial pilot coverage

The six initial pilot dossiers cover founder-led bootstrapping (Built from Zero), consumer brand creation (Sara Blakely), customer obsession and scale (Jeff Bezos), capital allocation (Warren Buffett), deep-technology platforms (Jensen Huang), and marketplace trust and experience design (Brian Chesky). Each dossier contains source-linked principles, at least one documented decision case, counter-evidence, transfer conditions and limitations. All remain Preview pending adversarial review and evaluation.

## Built from Zero attribution

S Haider is the named founder and public-facing entrepreneur behind Built from Zero. The initial dossier is based on first-party founder-contributed material. It does not assign a profile-level verification status. Evidence and limitations are recorded for each principle, and the dossier is explicitly Preview until it receives further source coverage, independent review where appropriate, and evaluation.

## Public-use safeguards

- Every directory record carries a clear non-affiliation and non-endorsement notice.
- The system must not speak in the first person as the named entrepreneur or imply access to private thoughts.
- A directory listing is not a claim that a dossier is complete or that an agent is active.
- Claim-level provenance is distinct from a person's identity or public recognition.
- The server does not embed an LLM or perform live research; the connected MCP host supplies reasoning and any external research tools.
- Retrieved documents and user-supplied material remain untrusted input.
- No agent may spend money, publish content, contact customers or make binding decisions autonomously.

## Activation gates

A catalogue entry may move from Preview to Active only after:
1. A versioned dossier covers the experience thesis, domains, principles, dated decision cases, mechanisms, counter-evidence, transfer conditions and limitations.
2. Each material factual claim maps to traceable sources and claim-level evidence status.
3. Source rights and attribution have been reviewed; copyrighted books and paid courses are not ingested as bulk text.
4. A distinct evaluation set tests task fit, evidence use, calibration, transfer reasoning, failure handling and prohibited claims.
5. Security and privacy review confirms safe context handling and no cross-user memory leakage.
6. CI, packaging and supported MCP protocol checks pass.
7. Public documentation accurately describes the actual runtime boundary.

## Current release boundary

This PR is an implementation foundation. It is not a complete global public launch. Dossier-grounded work packets and structural challenge validation are available, but independent model execution, autonomous challenge generation, semantic Lead reasoning, connected-model quality evaluation, public-host deployment, authentication, third-party client end-to-end verification, legal review and release certification remain separate gates. A deterministic structural evaluation suite exists for six scenario classes per pilot; it does not certify generated response quality.

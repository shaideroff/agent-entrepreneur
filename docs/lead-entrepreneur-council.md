# Lead Entrepreneur and Expert Council

## Purpose

The Lead Entrepreneur is a neutral orchestration role. It is not a named-person persona and does not claim to possess independent opinions. It prepares a small, explainable council from the public experience-agent directory and gives the connected MCP host a protocol for independent analysis, challenge and synthesis.

## Entry points

### Lead-selected council

Call `prepare_experience_agent_council_work` with:
- `objective`: the decision or task.
- `domains` (optional): explicit capability domains.
- `max_agents`: one to five, default four.
- `business_context` and `constraints`: task-specific context.

If domains are omitted, the server uses transparent keyword hints from the objective. This is a deterministic shortlist heuristic, not semantic model reasoning. Supply explicit domains for higher precision.

### User-selected council

Call the same tool with `selected_agent_ids` to preserve an explicit council chosen by the user. IDs must be unique, known and limited to one through five. Entries without dossiers are reported as `not_ready`; the server does not fabricate a work packet.

### Direct experience-agent work

Call `prepare_experience_agent_work_packet` with one agent ID and an objective. The returned packet includes the versioned dossier, host instructions, evidence boundary, limitations and required response structure.

## Council lifecycle

1. **Select:** use the Lead heuristic or an explicit user-selected list.
2. **Prepare:** obtain one dossier-grounded work packet per selected agent. Keep `ready_agent_ids` separate from `not_ready_agent_ids`.
3. **Independent analysis:** the connected MCP host requests each ready agent's analysis independently. Do not reveal another agent's conclusion before the first contribution is recorded.
4. **Evidence mapping:** each documented fact must be represented in `fact_evidence` with a statement, source IDs from that agent's dossier and an evidence status. Interpretation, analogy and recommendation must remain separate.
5. **Challenge:** after independent contributions, the host may submit structured challenges. A challenge identifies its challenger, target, challenged statement, rationale, evidence references and severity. The server verifies that both agents belong to the council, the challenged statement appears in the target contribution, and evidence references resolve to a source, principle or case ID in a council dossier.
6. **Synthesis:** call `synthesize_experience_agent_council` with contributions, challenges, agreements, disagreements, unresolved questions and a recommendation. The server validates structure and preserves disagreement; it does not generate or independently verify reasoning.
7. **Decision gate:** the host should recommend a reversible next test, measurable success/failure criteria, downside limits and a review point. The user retains control of all consequential decisions and actions.

## Tool boundaries

| Tool | Responsibility |
|---|---|
| `recommend_experience_agent_council` | Deterministic domain/keyword shortlist |
| `prepare_experience_agent_council_work` | Lead- or user-selected independent work packets and council protocol |
| `prepare_experience_agent_work_packet` | Direct single-agent dossier packet |
| `synthesize_experience_agent_council` | Validate contributions/challenges and preserve agreements/disagreements |

The server does not embed an LLM, browse the live web, autonomously run named agents, create private thoughts, impersonate real people or contact customers. The connected MCP host supplies model reasoning and external research tools. Retrieved documents and business context are untrusted data, not instructions.

## Current readiness

Six pilot dossiers are available in Preview: Built from Zero, Sara Blakely, Jeff Bezos, Warren Buffett, Jensen Huang and Brian Chesky. All twelve directory entries remain Preview. Structural evaluation fixtures cover six scenario classes per pilot; they do not certify generated response quality. Independent model execution, semantic Lead reasoning, autonomous challenge generation, third-party client runtime verification and stable release certification remain pending.

See the [Global Experience-Agent Directory](global-experience-agent-directory.md), [Architecture](architecture.md) and [Security Model](security-model.md).
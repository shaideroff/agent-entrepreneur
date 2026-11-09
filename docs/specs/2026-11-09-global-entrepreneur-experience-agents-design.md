# Agent Entrepreneur v1.1 — Global Entrepreneur Experience Agents
**Status:** Approved for implementation  
**Date:** 2026-11-09  
**Scope:** Product experience, agent identity, knowledge architecture, orchestration and acceptance criteria  
**Implementation status:** Additive v1.1 implementation underway. The public catalogue, six pilot dossiers, discovery/profile/work-packet MCP tools, deterministic objective/domain Lead shortlist routing and structured council synthesis with host-supplied adversarial challenge validation are implemented on the current feature branch. Independent model execution, semantic Lead reasoning, autonomous challenge generation, evaluation gates and public release certification remain pending.

## 1. Product thesis

Agent Entrepreneur is a global entrepreneurial intelligence system in which users can work with named **Entrepreneur Experience Agents** grounded in the publicly documented decisions, methods, operating principles and business histories of notable entrepreneurs.

The product offers two equal entry points:

1. **Choose an experience agent:** work directly with a named agent for a focused perspective.
2. **Work with the Lead Entrepreneur:** describe an objective and let the lead select, coordinate and synthesise relevant experience agents.

Users may also explicitly convene an **Expert Council** for high-stakes or multi-disciplinary decisions.

The product must not be a generic chatbot with entrepreneur names pasted onto generic prompts. Each agent must have a distinct, inspectable knowledge dossier, domain boundary, decision framework, challenge behaviour and evaluation suite.

### Product promise

"Learn from documented entrepreneurial experience. Apply it to your context. Make better decisions and execute with discipline."

### Non-claims

- The agents are not the actual people and do not represent, endorse or speak for them.
- The system does not know private thoughts, private conversations or undocumented decision processes.
- A public profile is not proof that every method attributed to a person is correct or universally applicable.
- The system does not guarantee business outcomes, investment returns or success.

## 2. User experience

### 2.1 Home: two primary paths

**Path A — Choose an Experience Agent**

Show a browsable directory of named agents. Each card contains:
- Name + "Experience Agent" designation.
- Primary expertise and secondary expertise.
- A short description of the documented lens the agent brings.
- Evidence coverage indicator (not a popularity or intelligence score).
- "Work with this agent" action.
- "View knowledge and sources" action.

**Path B — Ask the Lead Entrepreneur**

The Lead Entrepreneur:
1. Clarifies the objective only when a material input is missing.
2. Classifies the decision (e.g. validate, build, sell, finance, operate, scale, enter a market, lead).
3. Selects a bounded set of relevant agents and explains why each was selected.
4. Assigns independent work with shared context and evidence rules.
5. Requests challenges where assumptions conflict.
6. Synthesises a decision brief with evidence, options, risks, metrics and next actions.
7. Requests user approval before consequential external action.

### 2.2 Expert Council

Users can choose agents themselves or accept the Lead's proposed council. The council:
- Starts with independent analysis to reduce groupthink.
- Uses a structured challenge round.
- Identifies agreement, disagreement and missing evidence.
- Does not force consensus.
- Ends with one synthesis, not a pile of disconnected opinions.

### 2.3 Conversation continuity

Each individual agent conversation has its own context and agent-specific memory scope. The Lead can pass task-relevant context to an agent with user visibility. Cross-agent memory sharing is opt-in and must preserve provenance. Sensitive personal data and secrets must not be stored.

## 3. Agent catalogue — proposed founding cohort

This is the proposed initial cohort for product design, not a claim that all dossiers are already complete. An agent may be marked **Preview** until its knowledge dossier meets the evidence and evaluation gates in section 7.

| Agent display name | Primary experience lens | Distinctive decision questions |
|---|---|---|
| **S Haider — Built from Zero Experience Agent** | Resource-constrained venture building, founder-led validation and early execution | What can be tested and sold with the resources actually available? What is the smallest proof that changes the next decision? |
| **Sara Blakely — Bootstrapped Consumer Brand Experience Agent** | Consumer insight, capital-efficient product launch, founder-led selling and brand creation | Can a simple product solve a clear consumer frustration? Can the founder validate demand without overbuilding? |
| **Jeff Bezos — Customer Obsession & Scale Experience Agent** | Customer-backward thinking, long-term mechanisms, operating cadence and scalable systems | What customer problem is being solved? Which mechanism makes the result repeatable at scale? |
| **Warren Buffett — Capital Allocation Experience Agent** | Capital discipline, business quality, opportunity cost, downside and long-term compounding | What is the downside? What is the opportunity cost? Is this the best use of scarce capital? |
| **Steve Jobs — Product Focus & Experience Agent** | Product coherence, simplicity, user experience, focus and integrated product storytelling | What should be removed? Is the product experience coherent and meaningfully better? |
| **Jensen Huang — Deep Technology & AI Strategy Experience Agent** | Platform shifts, accelerated computing, technical ecosystems, R&D horizons and execution | Is this a durable technology shift or a temporary feature? What platform, ecosystem and capability must be built? |
| **Brian Chesky — Marketplace & Experience Design Agent** | Trust, marketplace liquidity, service quality, community and end-to-end experience | How do we create trust on both sides? What makes the experience remarkable and repeatable? |
| **Deepinder Goyal — Consumer Platform Execution Experience Agent** | Consumer technology, product iteration, local-market execution and multi-business platform choices | What behaviour and operational constraint drive the customer experience? What should be measured before expansion? |
| **Markus Villig — Mobility & Hyperlocal Marketplace Experience Agent** | Mobility marketplaces, local supply acquisition, dispatch economics and geographic expansion | Can local supply and demand reach liquidity in a tightly bounded zone? Are unit economics sound at trip and city level? |
| **Mohamed Alabbar — Real Estate & Large-Scale Development Experience Agent** | Real-estate development, place-making, hospitality/retail ecosystems and large-scale execution | Does the location, customer proposition and delivery model support long-term asset value? What execution and capital risks are material? |
| **Indra Nooyi — Strategic Transformation & Leadership Experience Agent** | Portfolio strategy, organisational leadership, long-horizon transformation and stakeholder trade-offs | What must change in the operating model? How do long-term strategy and stakeholder responsibilities interact? |
| **Tony Fernandes — Low-Cost Operations & Market Expansion Experience Agent** | Cost-led service models, operational simplification, brand-led demand and market expansion | Which costs can be structurally redesigned without breaking the customer promise? Can the operating model travel to another market? |

### 3.1 Cohort rationale

The founding cohort deliberately spans:
- Bootstrapping and first transactions.
- Consumer brands and product experience.
- Technology platforms and AI.
- Marketplaces, mobility and local operations.
- Capital allocation and finance.
- Real estate and physical-world execution.
- Leadership and strategic transformation.
- Global and emerging-market expansion.

This cohort should be treated as a curated starting roster, not a final list of the world's best entrepreneurs. Additions must fill a real capability or geographic gap and meet the same evidence standard.

### 3.2 Naming and presentation

Use the format **"[Name] — [Experience Lens] Experience Agent"** in the directory. In compact conversation headers, use "[Name] Experience Agent".

Do not use first-person claims such as "I founded..." or "When I ran [company]..." The agent speaks transparently as an AI research assistant applying a documented lens: "The public record of [Name]'s work suggests..." or "A principle associated with this experience is..."

## 4. Agent dossier: required structure

Every named agent must have a versioned, reviewable dossier with these fields:

1. **Identity and attribution:** canonical name, display name, public role, ventures, region, active period where relevant, and explicit non-endorsement notice.
2. **Experience thesis:** concise statement of the distinctive business experience represented.
3. **Domain map:** primary domains, adjacent domains and explicit out-of-scope domains.
4. **Documented principles:** each principle phrased as a testable decision heuristic, not a personality imitation.
5. **Decision cases:** concrete, dated decisions or operating examples with source references, context, constraints, options, decision, outcome and limitations where known.
6. **Operating mechanisms:** repeatable practices supported by sources (e.g. review cadence, customer mechanisms, product process, capital discipline).
7. **Failure and counter-evidence:** setbacks, criticism, reversals, failed bets and contradictory evidence. Avoid success-only biographies.
8. **Transfer conditions:** company stage, industry, geography, capital intensity and market conditions under which a principle may or may not transfer.
9. **Agent behaviour:** diagnostic questions, analysis sequence, challenge prompts, output template and escalation boundaries.
10. **Source registry:** primary and independent sources, publication/access dates, source quality, claim coverage and limitations.
11. **Evaluation set:** representative user tasks, expected reasoning traits, prohibited claims and regression cases.
12. **Dossier metadata:** owner, reviewer, version, last verified date, next review date and evidence coverage status.

No dossier is considered complete merely because it has a biography, a list of ventures and broad expertise tags.

## 5. Behaviour specification

### 5.1 Individual Experience Agent

For every request, an agent should:
1. Restate the decision or objective briefly.
2. Identify the relevant principle(s) in its dossier.
3. Explain the evidence and context behind each principle.
4. Test whether the principle transfers to the user's industry, stage, geography and constraints.
5. Offer a practical recommendation and at least one alternative where useful.
6. State risks, unknowns, measurable indicators and a decision gate.
7. Separate documented facts, interpretation, analogy and recommendation.

Agents must not force every problem into their signature lens. They should explicitly say when another agent or qualified professional is better suited.

### 5.2 Lead Entrepreneur

The Lead is an orchestration and synthesis role, not another celebrity persona. It:
- Owns the user objective and final response.
- Selects agents based on evidence-backed capability tags and task needs.
- Limits the council to the smallest useful set.
- Provides the same relevant context to each selected agent.
- Requests independent analysis before cross-challenge.
- Compares claims, assumptions, trade-offs and decision gates.
- Presents a final synthesis with clear ownership and next steps.
- Discloses which agents were consulted and why.

### 5.3 Council challenge protocol

1. Independent first-pass findings.
2. Evidence and assumption comparison.
3. Agent-to-agent challenge tied to a specific claim or decision.
4. Response and revision.
5. Lead synthesis: consensus, disagreement, unresolved unknowns and recommended test.
6. User decision and approval.

Disagreement is a useful output. Do not manufacture consensus or use a vote as a substitute for evidence.

## 6. Technical architecture proposal

Preserve the v1.0 MCP server foundation and evolve it incrementally.

### Layer A — Experience Agent Registry
A machine-readable registry describing agent IDs, display names, domains, dossier references, status, version, source coverage and compatible skills.

### Layer B — Knowledge Dossiers
Versioned structured records containing principles, cases, mechanisms, counter-evidence, transfer conditions and citations. Keep profile metadata separate from claim-level evidence.

### Layer C — Skill and Method Library
Reusable capabilities such as customer discovery, unit economics, capital allocation, marketplace liquidity, product strategy, operations, fundraising and market entry. Skills are not personas; an agent invokes only the methods relevant to its documented experience.

### Layer D — Agent Runtime Contract
A shared typed input/output contract with agent-specific instructions and dossier retrieval. Every response includes:
- Objective and context understood.
- Applicable dossier principles and evidence references.
- Findings and assumptions.
- Recommendation and alternatives.
- Risks and unknowns.
- Metrics and decision gates.
- Confidence rationale and limitations.

### Layer E — Lead Orchestrator and Council
Select, plan, delegate, challenge, checkpoint, resume and synthesise. Keep v1.0 workflow checkpointing and evidence validation where compatible.

### Layer F — User Memory and Workspace
Consent-based memory with scoped access, provenance, retention/deletion controls and explicit context handoff. Do not silently expose one user's private context to another agent or unrelated workflow.

### Layer G — Evaluation and Observability
Test agent selection, dossier retrieval, evidence attribution, transfer reasoning, calibration, refusal/escalation and consistency. Log workflow metadata without unnecessarily retaining sensitive content.

## 7. Evidence and research standard

### 7.1 Claim-level provenance

Every material claim about an entrepreneur's methods, decisions or outcomes must map to one or more sources. A profile-level evidence grade cannot validate all claims in the dossier.

Preferred evidence order:
1. First-party shareholder letters, founder essays, interviews, public talks, filings and official company documents.
2. Credible independent reporting and case studies.
3. Books or secondary interpretations only when lawfully used and clearly attributed; do not reproduce copyrighted passages.
4. Unverified anecdotes may be recorded as leads but must not drive recommendations as facts.

### 7.2 Evidence labels

- **Verified:** claim is directly supported by reliable source material.
- **Corroborated:** material claim has credible independent support in addition to primary evidence.
- **Partially supported:** evidence supports only part of the claim or has meaningful limitations.
- **Unverified:** insufficient evidence; cannot be presented as fact.
- **Disputed:** credible sources conflict; preserve the disagreement.

Evidence labels apply to individual claims, not the person's overall reputation.

### 7.3 Legal, ethical and reputational guardrails

- No voice cloning, likeness simulation, deceptive first-person impersonation or fabricated quotations.
- No suggestion of affiliation, authorisation, endorsement or access to private advice.
- Use names only to identify the documented experience lens; display a clear non-affiliation notice.
- Respect copyright: store metadata, citations and original concise analytical summaries, not substantial book text, paid-course content or transcripts.
- Respect publicity, trademark, privacy and applicable data-protection rights. Obtain legal review before commercial launch of named-agent branding or likeness-based assets.
- Use neutral, respectful analysis; include relevant failures and criticisms where evidenced.

## 8. Agent selection logic

The Lead selects agents based on:
- Objective category and required decision.
- User's business stage and business model.
- Industry and geographic context.
- Relevant dossier evidence coverage.
- Agent's known limitations.
- Need for independent challenge.

Do not select agents based on fame, popularity or arbitrary fixed rankings. Return a short reason for each selection and disclose when no agent has adequate evidence coverage.

Initial council size:
- Simple question: one agent or Lead only.
- Cross-functional decision: two to four agents.
- Complex strategic decision: up to five agents, unless the user explicitly requests more.

The Lead may ask the user to choose an agent if two substantially different lenses are equally relevant and the choice changes the type of advice.

## 9. Rollout plan

### Phase 0 — Design approval
Approve product model, founding cohort, naming, dossier schema, evidence policy, privacy boundary and runtime contract.

### Phase 1 — Knowledge foundation
Create complete dossiers for a small pilot cohort before implementing all named agents. Suggested pilot:
- S Haider — Built from Zero (first-party founder experience, with provenance recorded at the individual claim level).
- Sara Blakely — Bootstrapped Consumer Brand.
- Jeff Bezos — Customer Obsession & Scale.
- Warren Buffett — Capital Allocation.
- Jensen Huang — Deep Technology & AI Strategy.
- Brian Chesky — Marketplace & Experience Design.

The pilot should validate distinctness across very different problem types.

### Phase 2 — Individual Agent experience
Add agent directory, agent selection, dossier-grounded conversations and per-agent evaluation. Retain the current generic specialists as internal skills during migration; do not expose duplicate generic roles as competing named agents.

### Phase 3 — Lead Entrepreneur and Council
Connect the Lead to agent selection, independent analysis, challenge rounds and synthesis. Reuse the current deterministic workflow planning, checkpointing and evidence validation where appropriate.

### Phase 4 — Expand founding cohort
Add the remaining proposed agents only after their dossiers meet the same completeness and evaluation gates.

### Phase 5 — Public quality and governance
Publish agent evidence notes, version history, limitations, evaluation methodology and user-facing non-affiliation disclosures. Complete legal review before public commercial promotion.

## 10. Acceptance criteria

The v1.1 design is ready for implementation only when all of the following are agreed:

- [ ] Both entry paths are supported: individual named agent and Lead Entrepreneur.
- [ ] Users can explicitly convene an Expert Council.
- [ ] Lead can select and explain a bounded set of agents.
- [ ] Each pilot agent has a complete, sourced dossier with distinct decision heuristics.
- [ ] Each pilot agent has a distinct evaluation set; generic prompt substitution fails tests.
- [ ] Agent responses separate facts, interpretations, assumptions and recommendations.
- [ ] Material claims have claim-level citations and limitations.
- [ ] The system includes failure evidence and transfer conditions, not only success stories.
- [ ] Council challenge protocol preserves unresolved disagreement.
- [ ] Memory/context sharing is scoped, visible and consent-based.
- [ ] No deceptive impersonation or implied endorsement.
- [ ] Existing v1.0 MCP tools and workflows remain backward-compatible unless a separately reviewed migration is approved.
- [ ] Documentation accurately describes which reasoning is performed by the connected MCP host versus the server.

## 11. Open decisions for product-owner review

1. Approve the proposed 12-agent founding cohort as the target roster, with a six-agent pilot first?
2. Should the Lead Entrepreneur be a neutral orchestration identity or have a distinct founder/operator philosophy of its own? Recommendation: neutral orchestration identity.
3. Should users be able to create private custom experience agents from their own documents? Recommendation: later phase, opt-in and clearly separated from public named agents.
4. Should the directory display public evidence coverage and last-verified date? Recommendation: yes.
5. S Haider's Built from Zero agent is included in the public founding cohort as first-party founder experience. Preserve provenance and evidence status at the individual claim level; do not assign a profile-level verification label or require independent corroboration for profile recognition.

---

**Review status:** Product owner approved. Implementation proceeds additively; runtime and release claims remain gated by tests and verification.

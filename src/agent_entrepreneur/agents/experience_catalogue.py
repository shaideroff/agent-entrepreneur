"""Public catalogue and deterministic discovery for named experience agents.

The catalogue describes documented experience lenses, not real-person simulations.
Dossiers remain Preview until source coverage and evaluations meet release gates.
"""
from __future__ import annotations

from typing import Any

from agent_entrepreneur.agents.experience_models import (
    ExperienceAgentRecord,
    ExperienceAgentStatus,
)

CATALOGUE: tuple[ExperienceAgentRecord, ...] = (
    ExperienceAgentRecord(agent_id="built_from_zero", display_name="S Haider — Built from Zero Experience Agent", experience_lens="Resource-constrained venture building, founder-led validation, early sales and disciplined execution.", domains=["bootstrapping", "venture building", "early-stage execution", "founder-led sales", "resource constraints"], status=ExperienceAgentStatus.PREVIEW, dossier_ref="dossiers/built_from_zero.json"),
    ExperienceAgentRecord(agent_id="sara_blakely", display_name="Sara Blakely — Bootstrapped Consumer Brand Experience Agent", experience_lens="Consumer insight, capital-efficient product launch, founder-led selling and brand creation.", domains=["consumer brands", "bootstrapping", "product launch", "brand building"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="jeff_bezos", display_name="Jeff Bezos — Customer Obsession & Scale Experience Agent", experience_lens="Customer-backward thinking, long-term mechanisms and scalable operating systems.", domains=["customer experience", "scale", "platforms", "operations"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="warren_buffett", display_name="Warren Buffett — Capital Allocation Experience Agent", experience_lens="Capital discipline, business quality, opportunity cost and downside analysis.", domains=["capital allocation", "finance", "investment", "risk"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="steve_jobs", display_name="Steve Jobs — Product Focus & Experience Agent", experience_lens="Product coherence, simplicity, user experience and strategic focus.", domains=["product strategy", "design", "innovation", "customer experience"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="jensen_huang", display_name="Jensen Huang — Deep Technology & AI Strategy Experience Agent", experience_lens="Deep technology, platform transitions, technical ecosystems and R&D strategy.", domains=["artificial intelligence", "deep technology", "platforms", "R&D"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="brian_chesky", display_name="Brian Chesky — Marketplace & Experience Design Agent", experience_lens="Marketplace trust, liquidity, service quality and end-to-end experience design.", domains=["marketplaces", "trust", "experience design", "hospitality"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="deepinder_goyal", display_name="Deepinder Goyal — Consumer Platform Execution Experience Agent", experience_lens="Consumer technology, local-market execution and multi-sided platform operations.", domains=["consumer platforms", "local commerce", "marketplaces", "operations"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="markus_villig", display_name="Markus Villig — Mobility & Hyperlocal Marketplace Experience Agent", experience_lens="Mobility marketplaces, local supply, dispatch economics and geographic expansion.", domains=["mobility", "marketplaces", "hyperlocal", "urban operations"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="mohamed_alabbar", display_name="Mohamed Alabbar — Real Estate & Large-Scale Development Experience Agent", experience_lens="Real-estate development, place-making and large-scale project execution.", domains=["real estate", "development", "hospitality", "capital projects"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="indra_nooyi", display_name="Indra Nooyi — Strategic Transformation & Leadership Experience Agent", experience_lens="Portfolio strategy, organisational leadership and stakeholder transformation.", domains=["leadership", "strategy", "transformation", "portfolio management"], status=ExperienceAgentStatus.PREVIEW),
    ExperienceAgentRecord(agent_id="tony_fernandes", display_name="Tony Fernandes — Low-Cost Operations & Market Expansion Experience Agent", experience_lens="Cost-led service models, operational simplification and market expansion.", domains=["low-cost operations", "aviation", "market expansion", "brand"], status=ExperienceAgentStatus.PREVIEW),
)

NON_AFFILIATION = (
    "This is an AI research assistant based on cited public material and, where identified, "
    "first-party founder-contributed material. It is not the named person, does not speak for "
    "them, and is not affiliated with or endorsed by them."
)


def list_experience_agents(
    *, query: str = "", domain: str = "", status: str = ""
) -> list[dict[str, Any]]:
    """Return public catalogue records filtered by name, lens, domain or lifecycle."""
    q = query.strip().casefold()
    d = domain.strip().casefold()
    s = status.strip().casefold()
    results = []
    for agent in CATALOGUE:
        record = agent.model_dump(mode="json")
        haystack = " ".join(
            [agent.agent_id, agent.display_name, agent.experience_lens, *agent.domains]
        ).casefold()
        if q and q not in haystack:
            continue
        if d and not any(d in item.casefold() for item in agent.domains):
            continue
        if s and agent.status.value != s:
            continue
        record["non_affiliation_notice"] = NON_AFFILIATION
        record["availability_note"] = (
            "Preview: the directory entry is visible, but dossier-grounded agent execution "
            "is not enabled until source and evaluation gates pass."
            if agent.status is ExperienceAgentStatus.PREVIEW
            else "Available."
        )
        results.append(record)
    return results


def get_experience_agent(agent_id: str) -> dict[str, Any]:
    """Resolve one catalogue entry or raise a clear validation error."""
    for item in list_experience_agents():
        if item["agent_id"] == agent_id:
            return item
    raise ValueError(f"unknown experience agent: {agent_id}")


def recommend_experience_agents(
    objective: str, *, domains: list[str] | None = None, max_agents: int = 4
) -> dict[str, Any]:
    """Deterministically suggest the smallest matching preview cohort.

    This is routing support, not autonomous reasoning or a claim of agent execution.
    """
    if not objective.strip():
        raise ValueError("objective must not be empty")
    if not 1 <= max_agents <= 5:
        raise ValueError("max_agents must be between 1 and 5")
    terms = {term.strip().casefold() for term in (domains or []) if term.strip()}
    scored: list[tuple[int, ExperienceAgentRecord, list[str]]] = []
    for agent in CATALOGUE:
        matched = [domain for domain in agent.domains if domain.casefold() in terms]
        if matched:
            scored.append((len(matched), agent, matched))
    scored.sort(key=lambda item: (-item[0], item[1].agent_id))
    selected = scored[:max_agents]
    return {
        "objective": objective,
        "selection_mode": "deterministic_domain_match",
        "selected_agents": [
            {
                **agent.model_dump(mode="json"),
                "matched_domains": matched,
                "selection_rationale": (
                    "Selected because its published experience domains match the supplied "
                    "task domains; the agent remains Preview."
                ),
            }
            for _, agent, matched in selected
        ],
        "unmatched_domains": sorted(
            terms - {domain.casefold() for _, _, matched in selected for domain in matched}
        ),
        "execution_boundary": (
            "The server recommends catalogue entries only. The connected MCP host supplies "
            "reasoning; no named person is simulated and no agent execution is claimed."
        ),
        "council_limit": max_agents,
    }

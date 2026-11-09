"""Public experience-agent catalogue and routing tests."""
from agent_entrepreneur.agents.experience_catalogue import (
    get_experience_agent,
    list_experience_agents,
    recommend_experience_agents,
)


def test_global_catalogue_exposes_twelve_named_agents() -> None:
    agents = list_experience_agents()
    assert len(agents) == 12
    assert {item["agent_id"] for item in agents} >= {
        "built_from_zero", "sara_blakely", "jeff_bezos", "warren_buffett",
        "steve_jobs", "jensen_huang", "brian_chesky", "deepinder_goyal",
        "markus_villig", "mohamed_alabbar", "indra_nooyi", "tony_fernandes",
    }


def test_public_catalogue_does_not_claim_preview_agents_are_live() -> None:
    agents = list_experience_agents(status="preview")
    assert len(agents) == 12
    assert all("Preview" in item["availability_note"] for item in agents)


def test_built_from_zero_is_first_party_founder_experience() -> None:
    profile = get_experience_agent("built_from_zero")
    assert profile["display_name"].startswith("S Haider")
    assert "not affiliated" in profile["non_affiliation_notice"]
    assert profile["dossier"]["agent_id"] == "built_from_zero"
    assert profile["dossier"]["principles"]
    assert profile["dossier"]["sources"][0]["source_type"] == "primary"


def test_discovery_filters_by_domain_and_query() -> None:
    agents = list_experience_agents(query="mobility", domain="hyperlocal")
    assert [item["agent_id"] for item in agents] == ["markus_villig"]


def test_council_routing_is_bounded_and_discloses_execution_boundary() -> None:
    result = recommend_experience_agents(
        "Assess a hyperlocal mobility marketplace.",
        domains=["mobility", "hyperlocal"],
        max_agents=2,
    )
    assert len(result["selected_agents"]) == 1
    assert result["selected_agents"][0]["agent_id"] == "markus_villig"
    assert "does not" in result["execution_boundary"]


def test_council_routing_rejects_more_than_five_agents() -> None:
    import pytest

    with pytest.raises(ValueError, match="between 1 and 5"):
        recommend_experience_agents("Test", max_agents=6)


def test_council_synthesis_preserves_disagreement() -> None:
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    result = synthesize_experience_council(
        "Should we expand now?",
        [
            {"agent_id": "built_from_zero", "documented_facts": ["Founder-led validation is a relevant lens."], "recommendations": ["Run a small test."]},
            {"agent_id": "jeff_bezos", "interpretations": ["Scale mechanisms matter after repeatability."]},
        ],
        recommendation="Validate one market before expanding.",
        agreements=["Demand evidence is needed."],
        disagreements=["Timing of system investment differs."],
        unresolved_questions=["What is the repeatable acquisition cost?"],
    )
    assert len(result["contributions"]) == 2
    assert result["disagreements"] == ["Timing of system investment differs."]
    assert result["unresolved_questions"] == ["What is the repeatable acquisition cost?"]


def test_council_synthesis_rejects_unknown_agent() -> None:
    import pytest
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    with pytest.raises(ValueError, match="unknown experience agent IDs"):
        synthesize_experience_council(
            "Objective",
            [{"agent_id": "made_up"}],
            recommendation="Do more research.",
        )


def test_built_from_zero_work_packet_includes_dossier_and_guardrails() -> None:
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_agent_work_packet

    packet = prepare_experience_agent_work_packet(
        "built_from_zero",
        "Validate a new customer problem before building.",
        business_context="Early-stage consumer product.",
        constraints=["Low initial budget"],
    )
    assert packet["status"] == "preview_work_packet"
    assert packet["dossier"]["agent_id"] == "built_from_zero"
    assert any("Never use deceptive first-person roleplay" in item for item in packet["host_instructions"])


def test_jeff_bezos_dossier_has_traceable_sources_and_work_packet() -> None:
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_agent_work_packet

    profile = get_experience_agent("jeff_bezos")
    dossier = profile["dossier"]
    source_ids = {source["source_id"] for source in dossier["sources"]}
    assert len(source_ids) >= 2
    assert all(principle["source_ids"] for principle in dossier["principles"])
    assert all(set(principle["source_ids"]) <= source_ids for principle in dossier["principles"])
    assert dossier["decision_cases"]
    packet = prepare_experience_agent_work_packet("jeff_bezos", "Evaluate a customer-led growth investment.")
    assert packet["status"] == "preview_work_packet"
    assert packet["dossier"]["agent_id"] == "jeff_bezos"


def test_preview_agent_without_dossier_does_not_receive_fake_work_packet() -> None:
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_agent_work_packet

    packet = prepare_experience_agent_work_packet(
        "sara_blakely", "Assess a product launch."
    )
    assert packet["status"] == "not_ready"
    assert "No validated dossier" in packet["reason"]

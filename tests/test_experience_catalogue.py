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

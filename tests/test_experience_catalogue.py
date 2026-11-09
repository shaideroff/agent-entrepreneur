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
            {"agent_id": "built_from_zero", "documented_facts": ["Founder-led validation is a relevant lens."], "fact_evidence": [{"statement": "Founder-led validation is a relevant lens.", "source_ids": ["sh-founder-experience-001"], "evidence_status": "partially_supported"}], "recommendations": ["Run a small test."]},
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
    assert any("untrusted data" in item for item in packet["host_instructions"])


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


def test_five_pilot_dossiers_load_with_valid_source_references() -> None:
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_agent_work_packet

    pilot_ids = ["built_from_zero", "sara_blakely", "jeff_bezos", "warren_buffett", "jensen_huang", "brian_chesky"]
    for agent_id in pilot_ids:
        profile = get_experience_agent(agent_id)
        dossier = profile["dossier"]
        source_ids = {source["source_id"] for source in dossier["sources"]}
        assert source_ids
        assert dossier["principles"]
        assert all(set(item["source_ids"]) <= source_ids for item in dossier["principles"])
        packet = prepare_experience_agent_work_packet(agent_id, "Assess a strategic decision.")
        assert packet["status"] == "preview_work_packet"


def test_preview_agent_without_dossier_does_not_receive_fake_work_packet() -> None:
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_agent_work_packet

    packet = prepare_experience_agent_work_packet(
        "markus_villig", "Assess a hyperlocal mobility launch."
    )
    assert packet["status"] == "not_ready"
    assert "No validated dossier" in packet["reason"]


def test_lead_routing_infers_domains_from_objective_without_model_claim() -> None:
    result = recommend_experience_agents(
        "Evaluate a hyperlocal mobility marketplace and dispatch model."
    )
    selected = {item["agent_id"] for item in result["selected_agents"]}
    assert "markus_villig" in selected
    assert result["selection_mode"] == "lead_keyword_and_domain_match"
    assert "Deterministic keyword routing" in result["lead_routing_note"]


def test_council_challenge_round_preserves_structured_adversarial_review() -> None:
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    result = synthesize_experience_council(
        "Should we scale now?",
        [
            {"agent_id": "built_from_zero", "recommendations": ["Validate one market first."]},
            {"agent_id": "jeff_bezos", "recommendations": ["Invest in scalable mechanisms."]},
        ],
        recommendation="Run a bounded pilot with explicit scale gates.",
        challenges=[{
            "challenger_agent_id": "built_from_zero",
            "target_agent_id": "jeff_bezos",
            "challenged_statement": "Invest in scalable mechanisms.",
            "rationale": "The current demand and delivery process are not yet repeatable.",
            "evidence_refs": ["bfz-001"],
            "severity": "high",
        }],
    )
    assert result["challenges"][0]["severity"] == "high"
    assert "does not independently run" in result["challenge_boundary"]


def test_council_challenge_rejects_non_council_participant() -> None:
    import pytest
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    with pytest.raises(ValueError, match="participants must belong"):
        synthesize_experience_council(
            "Objective",
            [{"agent_id": "built_from_zero"}],
            recommendation="Proceed cautiously.",
            challenges=[{
                "challenger_agent_id": "jeff_bezos",
                "target_agent_id": "built_from_zero",
                "challenged_statement": "Test",
                "rationale": "Counterpoint",
            }],
        )



def test_catalogue_fails_closed_for_missing_configured_dossier(monkeypatch) -> None:
    import pytest
    from pathlib import Path

    monkeypatch.setattr(Path, "is_file", lambda self: False)
    with pytest.raises(FileNotFoundError, match="Configured experience dossier is missing"):
        get_experience_agent("built_from_zero")



def test_council_challenge_must_reference_a_target_contribution_statement() -> None:
    import pytest
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    with pytest.raises(ValueError, match="must match a statement"):
        synthesize_experience_council(
            "Objective",
            [
                {"agent_id": "built_from_zero", "recommendations": ["Run a pilot."]},
                {"agent_id": "jeff_bezos", "recommendations": ["Invest in infrastructure."]},
            ],
            recommendation="Run a pilot.",
            challenges=[{
                "challenger_agent_id": "built_from_zero",
                "target_agent_id": "jeff_bezos",
                "challenged_statement": "A fabricated statement.",
                "rationale": "Test challenge integrity.",
            }],
        )




def test_council_requires_claim_level_evidence_for_documented_facts() -> None:
    import pytest
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    with pytest.raises(ValueError, match="require claim-level fact_evidence"):
        synthesize_experience_council(
            "Objective",
            [{
                "agent_id": "built_from_zero",
                "documented_facts": ["The founder reported an early sales experiment."],
            }],
            recommendation="Treat as a first-party account.",
        )


def test_council_rejects_unknown_contribution_source_references() -> None:
    import pytest
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    with pytest.raises(ValueError, match="unknown evidence references"):
        synthesize_experience_council(
            "Objective",
            [{"agent_id": "built_from_zero", "source_ids": ["invented-source"]}],
            recommendation="Do more research.",
        )


def test_council_rejects_unknown_challenge_evidence_references() -> None:
    import pytest
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    with pytest.raises(ValueError, match="unknown challenge evidence references"):
        synthesize_experience_council(
            "Objective",
            [
                {"agent_id": "built_from_zero", "recommendations": ["Run a pilot."]},
                {"agent_id": "jeff_bezos", "recommendations": ["Build mechanisms."]},
            ],
            recommendation="Run a pilot.",
            challenges=[{
                "challenger_agent_id": "built_from_zero",
                "target_agent_id": "jeff_bezos",
                "challenged_statement": "Build mechanisms.",
                "rationale": "Evidence gap.",
                "evidence_refs": ["invented-ref"],
            }],
        )



def test_council_fact_evidence_maps_each_fact_to_a_dossier_source() -> None:
    from agent_entrepreneur.agents.experience_catalogue import synthesize_experience_council

    result = synthesize_experience_council(
        "Assess founder validation.",
        [{
            "agent_id": "built_from_zero",
            "documented_facts": ["The founder reported a 2017 campus sales experiment."],
            "fact_evidence": [{
                "statement": "The founder reported a 2017 campus sales experiment.",
                "source_ids": ["sh-founder-experience-001"],
                "evidence_status": "partially_supported",
            }],
        }],
        recommendation="Treat the case as a founder-reported example, not audited proof.",
    )
    assert result["contributions"][0]["fact_evidence"][0]["source_ids"] == [
        "sh-founder-experience-001"
    ]



def test_lead_prepares_independent_work_packets_for_selected_pilot_council() -> None:
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_council_work

    result = prepare_experience_council_work(
        "Evaluate a hyperlocal mobility marketplace.",
        business_context="Early-stage city pilot.",
        constraints=["Limited launch budget"],
    )
    assert result["lead_role"] == "neutral_orchestrator"
    assert "brian_chesky" in result["ready_agent_ids"]
    assert "markus_villig" in result["not_ready_agent_ids"]
    assert all(packet["status"] in {"preview_work_packet", "not_ready"} for packet in result["work_packets"])
    assert "independent contributions" in result["council_protocol"][0]



def test_user_can_select_a_bounded_experience_agent_council() -> None:
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_council_work

    result = prepare_experience_council_work(
        "Compare bootstrapping and capital allocation approaches.",
        selected_agent_ids=["built_from_zero", "warren_buffett"],
    )
    assert result["routing"]["selection_mode"] == "user_selected"
    assert result["ready_agent_ids"] == ["built_from_zero", "warren_buffett"]
    assert all(packet["status"] == "preview_work_packet" for packet in result["work_packets"])


def test_user_selected_council_rejects_unknown_or_oversized_selection() -> None:
    import pytest
    from agent_entrepreneur.agents.experience_catalogue import prepare_experience_council_work

    with pytest.raises(ValueError, match="unknown experience agent IDs"):
        prepare_experience_council_work("Objective", selected_agent_ids=["unknown"])
    with pytest.raises(ValueError, match="between 1 and 5"):
        prepare_experience_council_work(
            "Objective",
            selected_agent_ids=["built_from_zero", "sara_blakely", "jeff_bezos", "warren_buffett", "jensen_huang", "brian_chesky"],
        )


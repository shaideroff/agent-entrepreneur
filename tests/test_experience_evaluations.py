"""Structural evaluation gates for the initial experience-agent pilot cohort."""
import json
from pathlib import Path

from agent_entrepreneur.agents.experience_catalogue import get_experience_agent


ROOT = Path(__file__).parent / "evaluations" / "experience_agents"


def test_pilot_evaluation_suite_covers_required_scenarios_for_each_agent() -> None:
    suite = json.loads((ROOT / "pilot_eval_cases.json").read_text(encoding="utf-8"))
    assert suite["suite_version"] == "1.0.0"
    expected = {
        "in_domain",
        "out_of_domain",
        "transfer_mismatch",
        "contradictory_evidence",
        "missing_sources",
        "impersonation_attempt",
    }
    for agent_id in suite["agents"]:
        agent_cases = [case for case in suite["cases"] if case["agent_id"] == agent_id]
        assert {case["scenario"] for case in agent_cases} == expected
        assert all(case["dossier_version"] == "1.0.0" for case in agent_cases)


def test_each_pilot_dossier_meets_minimum_structural_release_gates() -> None:
    suite = json.loads((ROOT / "evaluations" / "experience_agents" / "pilot_eval_cases.json").read_text(encoding="utf-8"))
    for agent_id in suite["agents"]:
        dossier = get_experience_agent(agent_id)["dossier"]
        assert dossier["principles"]
        assert dossier["decision_cases"]
        assert all(case["decision_date"] for case in dossier["decision_cases"])
        assert dossier["sources"]
        assert dossier["counter_evidence"]
        assert dossier["transfer_conditions"]
        assert dossier["limitations"]
        source_ids = {source["source_id"] for source in dossier["sources"]}
        assert all(set(item["source_ids"]) <= source_ids for item in dossier["principles"])
        assert all(set(item["source_ids"]) <= source_ids for item in dossier["decision_cases"])
        assert dossier["non_affiliation_notice"]
        assert dossier["owner"]
        assert dossier["reviewer"] == "Independent review pending"
        assert dossier["last_verified_at"] == "2026-11-09"
        assert dossier["next_review_at"]
        assert dossier["evaluation_refs"] == ["experience-agent-pilot-structural-v1"]

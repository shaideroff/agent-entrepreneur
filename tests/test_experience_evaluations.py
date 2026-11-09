"""Structural evaluation gates for the initial experience-agent pilot cohort."""
import json
import subprocess
import sys
from pathlib import Path

from agent_entrepreneur.agents.experience_catalogue import get_experience_agent


ROOT = Path(__file__).parent / "evaluations" / "experience_agents"


def test_pilot_evaluation_suite_covers_required_scenarios_for_each_agent() -> None:
    suite = json.loads((ROOT / "pilot_eval_cases.json").read_text(encoding="utf-8"))
    assert suite["suite_version"] == "1.0.0"
    assert len(suite["cases"]) == len(suite["agents"]) * 6
    assert len({case["case_id"] for case in suite["cases"]}) == len(suite["cases"])
    assert all(case["required_traits"] for case in suite["cases"])
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
    suite = json.loads((ROOT / "pilot_eval_cases.json").read_text(encoding="utf-8"))
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

def test_dossier_specific_prompt_suite_covers_all_structural_cases() -> None:
    structural = json.loads((ROOT / "pilot_eval_cases.json").read_text(encoding="utf-8"))
    prompts = json.loads((ROOT / "pilot_eval_prompts.json").read_text(encoding="utf-8"))

    assert prompts["suite_version"] == "1.0.0"
    assert prompts["source_suite"] == structural["suite_id"]
    assert len(prompts["cases"]) == len(structural["cases"]) == 36
    assert "No model run has been performed" in prompts["execution_boundary"]

    structural_ids = {case["case_id"] for case in structural["cases"]}
    prompt_ids = {case["case_id"] for case in prompts["cases"]}
    assert prompt_ids == structural_ids
    assert len(prompt_ids) == len(prompts["cases"])

    for case in prompts["cases"]:
        assert case["prompt_version"] == "1.0.0"
        assert case["dossier_version"] == "1.0.0"
        assert case["agent_id"] in structural["agents"]
        assert case["scenario"] in structural["scenarios"]
        assert len(case["prompt"]) > 500
        assert "EVALUATION TASK" in case["prompt"]
        assert "source IDs" in case["prompt"]
        assert "Do not impersonate" in case["prompt"] or "not the named person" in case["prompt"]

def test_unexecuted_model_manifest_cannot_be_mistaken_for_a_pass() -> None:
    manifest = json.loads(
        (ROOT / "pilot_eval_run_manifest.template.json").read_text(encoding="utf-8")
    )
    prompts = json.loads((ROOT / "pilot_eval_prompts.json").read_text(encoding="utf-8"))

    assert manifest["execution_status"] == "NOT_RUN"
    assert manifest["execution_policy"]["paid_apis_allowed"] is False
    assert manifest["execution_policy"]["missing_output_status"] == "NOT_RUN"
    assert len(manifest["records"]) == len(prompts["cases"]) == 36
    assert {record["case_id"] for record in manifest["records"]} == {
        case["case_id"] for case in prompts["cases"]
    }

    for record in manifest["records"]:
        assert record["status"] == "NOT_RUN"
        assert record["provider"] is None
        assert record["model"] is None
        assert record["executed_at_utc"] is None
        assert record["output_artifact_ref"] is None
        assert record["trait_results"] == []
        assert record["rubric_results"] == []

def test_evaluation_report_marks_empty_run_as_not_run(tmp_path: Path) -> None:
    manifest_path = ROOT / "pilot_eval_run_manifest.template.json"
    result = subprocess.run(
        [sys.executable, "scripts/experience_agent_eval_report.py", str(manifest_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "**Overall status:** NOT RUN" in result.stdout
    assert "| NOT_RUN | 36 |" in result.stdout


def test_evaluation_report_rejects_pass_without_model_output_evidence(tmp_path: Path) -> None:
    manifest = json.loads(
        (ROOT / "pilot_eval_run_manifest.template.json").read_text(encoding="utf-8")
    )
    manifest["records"][0]["status"] = "REVIEWED_PASS"
    manifest_path = tmp_path / "invalid-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "scripts/experience_agent_eval_report.py", str(manifest_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "provider is required" in result.stderr


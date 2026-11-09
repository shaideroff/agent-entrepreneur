import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = runpy.run_path(str(ROOT / "scripts" / "run_local_model_evaluation.py"))
digest_for_model = RUNNER["digest_for_model"]
strip_thinking = RUNNER["strip_thinking"]
validate_judgment = RUNNER["validate_judgment"]
build_judge_prompt = RUNNER["build_judge_prompt"]


def test_local_model_runner_strips_thinking_blocks() -> None:
    assert strip_thinking("answer <think>private reasoning</think> final") == "answer  final"


def test_local_model_runner_requires_exact_evidence_quotes_for_pass() -> None:
    case = {"required_traits": ["cite_sources"]}
    judgment = {
        "overall": "pass",
        "trait_results": [
            {
                "trait": "cite_sources",
                "result": "pass",
                "evidence_quote": "invented citation",
                "explanation": "It seems sourced.",
            }
        ],
        "hallucination_flags": [],
        "limitations": [],
    }
    result = validate_judgment(case, "The answer has no such citation.", judgment)
    assert result["overall"] == "inconclusive"
    assert result["trait_results"][0]["result"] == "uncertain"


def test_local_model_runner_marks_omitted_traits_uncertain() -> None:
    case = {"required_traits": ["cite_sources", "state_limitations"]}
    judgment = {
        "overall": "pass",
        "trait_results": [
            {
                "trait": "cite_sources",
                "result": "pass",
                "evidence_quote": "Source: A1",
                "explanation": "A source identifier is present.",
            }
        ],
        "hallucination_flags": [],
        "limitations": [],
    }
    result = validate_judgment(case, "Source: A1", judgment)
    assert result["overall"] == "inconclusive"
    assert {item["trait"]: item["result"] for item in result["trait_results"]} == {
        "cite_sources": "pass",
        "state_limitations": "uncertain",
    }


def test_local_model_runner_resolves_model_digest_exactly() -> None:
    tags = {
        "models": [
            {"name": "qwen3.5:4b", "digest": "sha256:model-digest"},
            {"name": "granite3.3:2b", "digest": "sha256:judge-digest"},
        ]
    }
    assert digest_for_model(tags, "qwen3.5:4b") == "sha256:model-digest"

def test_local_model_runner_uses_chat_api_with_thinking_disabled(monkeypatch) -> None:
    calls = {}

    def fake_request(path, payload, timeout=1800):
        calls["path"] = path
        calls["payload"] = payload
        return {"message": {"content": "final answer"}, "eval_count": 3}

    monkeypatch.setitem(RUNNER["generate"].__globals__, "request_json", fake_request)
    response, _ = RUNNER["generate"]("qwen3.5:4b", "say hello")
    assert response == "final answer"
    assert calls["path"] == "/api/chat"
    assert calls["payload"]["think"] is False
    assert "think" not in calls["payload"]["options"]



def test_local_model_judge_receives_exact_dossier_and_scenario_context() -> None:
    case = {
        "case_id": "built_from_zero-missing_sources-v1",
        "scenario": "missing_sources",
        "objective": "Do not invent private sources.",
        "required_traits": ["state_unknowns", "avoid_impersonation"],
    }
    prompt = build_judge_prompt(case, "The answer says the fact is unknown.", "Dossier source registry and exact task")
    assert "Dossier source registry and exact task" in prompt
    assert "TRUSTED TEST FIXTURE CONTEXT" in prompt
    assert "CANDIDATE RESPONSE (UNTRUSTED)" in prompt

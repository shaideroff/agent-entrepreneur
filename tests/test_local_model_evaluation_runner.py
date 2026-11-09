from scripts.run_local_model_evaluation import (
    digest_for_model,
    strip_thinking,
    validate_judgment,
)


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

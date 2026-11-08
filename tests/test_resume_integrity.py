from pathlib import Path

import pytest

from agent_entrepreneur.agents.models import SpecialistResponse, WorkflowRequest
from agent_entrepreneur.agents.orchestrator import Orchestrator, plan_specialists
from agent_entrepreneur.workflows.checkpoints import CheckpointStore
from agent_entrepreneur.knowledge.evidence import EvidenceClaim


def _partial_workflow(tmp_path: Path):
    specialists = plan_specialists("market entry", ["finance", "operations"], max_specialists=2)
    store = CheckpointStore(tmp_path / "resume-integrity.sqlite3")

    def stop_after_first(assignment):
        if assignment.step_number == 2:
            raise RuntimeError("temporary interruption")
        return SpecialistResponse(specialist_id=assignment.specialist_id)

    request = WorkflowRequest(
        "market entry",
        context="Original market and customer context",
        max_specialists=2,
    )
    result = Orchestrator().run(request, specialists, stop_after_first, store)
    assert result.status == "partial"
    return result.workflow_id, request, specialists, store


def test_resume_rejects_changed_request_context(tmp_path: Path):
    workflow_id, request, specialists, store = _partial_workflow(tmp_path)

    changed_request = WorkflowRequest(
        request.objective,
        context="Different market and customer context",
        max_specialists=request.max_specialists,
    )

    with pytest.raises(ValueError, match="request or specialist plan"):
        Orchestrator().resume(
            workflow_id,
            changed_request,
            specialists,
            lambda assignment: SpecialistResponse(specialist_id=assignment.specialist_id),
            store,
        )


def test_resume_rejects_changed_specialist_task(tmp_path: Path):
    workflow_id, request, specialists, store = _partial_workflow(tmp_path)
    changed_plan = list(specialists)
    original = changed_plan[1]
    changed_plan[1] = type(original)(
        specialist_id=original.specialist_id,
        specialist_title=original.specialist_title,
        methodology=original.methodology,
        objective=original.objective,
        task="Perform a different specialist task",
        context=original.context,
        untrusted_material=original.untrusted_material,
        step_number=original.step_number,
    )

    with pytest.raises(ValueError, match="request or specialist plan"):
        Orchestrator().resume(
            workflow_id,
            request,
            changed_plan,
            lambda assignment: SpecialistResponse(specialist_id=assignment.specialist_id),
            store,
        )



def _evidence_claim(statement: str) -> EvidenceClaim:
    return EvidenceClaim.model_validate(
        {
            "claim_id": "market-demand-claim",
            "statement": statement,
            "claim_type": "descriptive",
            "scope": "test market",
            "population_or_context": "early-stage pilot",
            "evidence_level": "unverified",
            "status": "unverified",
            "sources": [
                {
                    "source_id": "source-1",
                    "url": "https://example.com/evidence",
                    "title": "Test evidence",
                    "publisher": "Test publisher",
                    "source_type": "primary",
                    "accessed_at": "2026-11-09",
                    "supports": "Unverified placeholder for provenance fingerprint testing.",
                }
            ],
            "checked_at": "2026-11-09",
        }
    )


def test_resume_rejects_changed_evidence_registry(tmp_path: Path):
    specialists = plan_specialists("market entry", ["finance", "operations"], max_specialists=2)
    request = WorkflowRequest(
        "market entry",
        context="Original pilot context",
        max_specialists=2,
    )
    store = CheckpointStore(tmp_path / "evidence-resume.sqlite3")

    def stop_after_first(assignment):
        if assignment.step_number == 2:
            raise RuntimeError("temporary interruption")
        return SpecialistResponse(specialist_id=assignment.specialist_id)

    result = Orchestrator().run(
        request,
        specialists,
        stop_after_first,
        store,
        evidence_claims=[_evidence_claim("Original demand claim")],
    )
    assert result.status == "partial"

    with pytest.raises(ValueError, match="evidence registry"):
        Orchestrator().resume(
            result.workflow_id,
            request,
            specialists,
            lambda assignment: SpecialistResponse(specialist_id=assignment.specialist_id),
            store,
            evidence_claims=[_evidence_claim("Changed demand claim")],
        )

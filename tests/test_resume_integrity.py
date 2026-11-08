from pathlib import Path

import pytest

from agent_entrepreneur.agents.models import SpecialistResponse, WorkflowRequest
from agent_entrepreneur.agents.orchestrator import Orchestrator, plan_specialists
from agent_entrepreneur.workflows.checkpoints import CheckpointStore


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

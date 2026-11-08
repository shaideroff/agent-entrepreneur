from __future__ import annotations

import uuid
from collections.abc import Callable, Iterable, Sequence

from agent_entrepreneur.agents.models import (
    SpecialistAssignment,
    SpecialistFinding,
    SpecialistResponse,
    WorkflowCheckpoint,
    WorkflowRequest,
    WorkflowResult,
)
from agent_entrepreneur.agents.registry import SPECIALISTS
from agent_entrepreneur.workflows.checkpoints import CheckpointStore

Executor = Callable[[SpecialistAssignment], SpecialistResponse]


def plan_specialists(objective: str, domains: list[str], *, max_specialists: int = 3) -> list[SpecialistAssignment]:
    if not 1 <= max_specialists <= 6:
        raise ValueError("max_specialists must be between 1 and 6")
    requested = {domain.casefold() for domain in domains}
    matched: list[SpecialistAssignment] = []
    for specialist_id, profile in SPECIALISTS.items():
        if requested.intersection({domain.casefold() for domain in profile["domains"]}):
            matched.append(SpecialistAssignment(
                specialist_id=specialist_id,
                specialist_title=profile["title"],
                methodology=profile["methodology"],
                objective=objective,
                task=f"Analyse the objective from the {profile['title']} discipline.",
                context="",
            ))
        if len(matched) >= max_specialists:
            break
    if not matched:
        profile = SPECIALISTS["built_from_zero"]
        matched.append(SpecialistAssignment(
            specialist_id="built_from_zero",
            specialist_title=profile["title"],
            methodology=profile["methodology"],
            objective=objective,
            task=f"Clarify and scope the objective: {objective}",
            context="",
        ))
    return matched


class Orchestrator:
    def run(
        self,
        request: WorkflowRequest,
        specialists: Sequence[SpecialistAssignment],
        executor: Executor,
        checkpoint_store: CheckpointStore | None = None,
    ) -> WorkflowResult:
        if not request.objective.strip():
            raise ValueError("objective must not be empty")
        if not 1 <= request.max_steps <= 24:
            raise ValueError("max_steps must be between 1 and 24")
        if not 1 <= request.max_specialists <= 6:
            raise ValueError("max_specialists must be between 1 and 6")
        selected = tuple(specialists[:request.max_specialists])
        if not selected:
            raise ValueError("at least one specialist is required")
        if len(selected) > request.max_steps:
            raise ValueError("specialist count exceeds the workflow step limit")
        workflow_id = str(uuid.uuid4())
        responses: list[SpecialistResponse] = []
        failures: list[str] = []
        for index, specialist in enumerate(selected, start=1):
            assignment = SpecialistAssignment(
                specialist_id=specialist.specialist_id,
                specialist_title=specialist.specialist_title,
                methodology=specialist.methodology,
                objective=request.objective,
                task=specialist.task,
                context=request.context,
                untrusted_material=request.untrusted_material,
                step_number=index,
            )
            try:
                response = executor(assignment)
                if response.specialist_id != specialist.specialist_id:
                    raise ValueError("executor response specialist_id did not match its assignment")
                responses.append(response)
                if checkpoint_store is not None:
                    checkpoint_store.save(WorkflowCheckpoint(
                        workflow_id=workflow_id,
                        status="running",
                        state={
                            "objective": request.objective,
                            "completed_steps": index,
                            "specialists_consulted": [item.specialist_id for item in responses],
                            "responses": [_response_state(item) for item in responses],
                        },
                    ))
            except Exception as exc:
                failures.append(f"{specialist.specialist_id}: {type(exc).__name__}: {exc}")
                break
        findings = tuple(finding for response in responses for finding in response.findings)
        recommendations = _unique(item for response in responses for item in response.recommendations)
        risks = _unique(item for response in responses for item in response.risks)
        disagreements = _unique(item for response in responses for item in response.challenges)
        unknowns = _unique(item for response in responses for item in response.unknowns)
        evidence_refs = _unique(ref for finding in findings for ref in finding.evidence_refs)
        limitations = _unique([item for response in responses for item in response.limitations] + failures)
        status = "failed" if not responses else ("partial" if failures else "completed")
        result = WorkflowResult(
            workflow_id=workflow_id,
            status=status,
            objective=request.objective,
            specialists_consulted=tuple(item.specialist_id for item in responses),
            findings=findings,
            recommendations=recommendations,
            risks=risks,
            disagreements=disagreements,
            unknowns=unknowns,
            evidence_refs=evidence_refs,
            limitations=limitations,
            steps_completed=len(responses),
            error=failures[0] if failures else None,
        )
        if checkpoint_store is not None:
            checkpoint_store.save(WorkflowCheckpoint(
                workflow_id=workflow_id,
                status=status,
                state={"objective": request.objective, "result": _result_state(result)},
            ))
        return result


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return tuple(result)


def _response_state(response: SpecialistResponse) -> dict[str, object]:
    return {
        "specialist_id": response.specialist_id,
        "findings": [{"statement": item.statement, "evidence_refs": list(item.evidence_refs), "evidence_status": item.evidence_status} for item in response.findings],
        "recommendations": list(response.recommendations),
        "risks": list(response.risks),
        "challenges": list(response.challenges),
        "unknowns": list(response.unknowns),
        "limitations": list(response.limitations),
    }


def _result_state(result: WorkflowResult) -> dict[str, object]:
    return {
        "workflow_id": result.workflow_id,
        "status": result.status,
        "objective": result.objective,
        "specialists_consulted": list(result.specialists_consulted),
        "findings": [{"statement": item.statement, "evidence_refs": list(item.evidence_refs), "evidence_status": item.evidence_status} for item in result.findings],
        "recommendations": list(result.recommendations),
        "risks": list(result.risks),
        "disagreements": list(result.disagreements),
        "unknowns": list(result.unknowns),
        "evidence_refs": list(result.evidence_refs),
        "limitations": list(result.limitations),
        "steps_completed": result.steps_completed,
    }

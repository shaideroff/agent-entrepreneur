from __future__ import annotations

import hashlib
import json
import uuid

from agent_entrepreneur.knowledge.evidence import EvidenceClaim
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal, cast

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
                specialist_title=cast(str, profile["title"]),
                methodology=cast(str, profile["methodology"]),
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
            specialist_title=cast(str, profile["title"]),
            methodology=cast(str, profile["methodology"]),
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
        *,
        workflow_id: str | None = None,
        prior_responses: Sequence[SpecialistResponse] = (),
        evidence_claims: Sequence[EvidenceClaim] = (),
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
        request_fingerprint = workflow_fingerprint(request, selected, evidence_claims)
        if len(prior_responses) > len(selected):
            raise ValueError("prior response count exceeds selected specialist count")
        if any(response.specialist_id != selected[index].specialist_id for index, response in enumerate(prior_responses)):
            raise ValueError("checkpoint specialist responses do not match the supplied plan")
        claim_registry = {claim.claim_id: claim for claim in evidence_claims}
        if len(claim_registry) != len(evidence_claims):
            raise ValueError("evidence claim IDs must be unique")
        workflow_id = workflow_id or str(uuid.uuid4())
        responses: list[SpecialistResponse] = list(prior_responses)
        for prior_response in responses:
            _validate_findings(prior_response.findings, claim_registry)
        failures: list[str] = []
        for index, specialist in enumerate(selected[len(responses):], start=len(responses) + 1):
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
                _validate_findings(response.findings, claim_registry)
                responses.append(response)
                if checkpoint_store is not None:
                    checkpoint_store.save(WorkflowCheckpoint(
                        workflow_id=workflow_id,
                        status="running",
                        state={
                            "objective": request.objective,
                            "request_fingerprint": request_fingerprint,
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
        status: Literal["completed", "partial", "failed"] = (
            "failed" if not responses else ("partial" if failures else "completed")
        )
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
            checkpoint_status: Literal["running", "completed", "partial", "failed"] = status
            checkpoint_store.save(WorkflowCheckpoint(
                workflow_id=workflow_id,
                status=checkpoint_status,
                state={
                    "objective": request.objective,
                    "request_fingerprint": request_fingerprint,
                    "completed_steps": len(responses),
                    "specialists_consulted": [item.specialist_id for item in responses],
                    "responses": [_response_state(item) for item in responses],
                    "result": _result_state(result),
                },
            ))
        return result


    def resume(
        self,
        workflow_id: str,
        request: WorkflowRequest,
        specialists: Sequence[SpecialistAssignment],
        executor: Executor,
        checkpoint_store: CheckpointStore,
        *,
        evidence_claims: Sequence[EvidenceClaim] = (),
    ) -> WorkflowResult:
        checkpoint = checkpoint_store.resume(workflow_id)
        if checkpoint is None:
            raise ValueError(f"workflow checkpoint not found: {workflow_id}")
        if checkpoint.status == "completed":
            raise ValueError("completed workflows cannot be resumed")
        selected = tuple(specialists[:request.max_specialists])
        expected_fingerprint = workflow_fingerprint(request, selected, evidence_claims)
        saved_fingerprint = checkpoint.state.get("request_fingerprint")
        raw_responses = checkpoint.state.get("responses", [])
        if not isinstance(raw_responses, list):
            raise ValueError("checkpoint responses are invalid")
        if saved_fingerprint is None and not raw_responses:
            # Older empty checkpoints contain no completed specialist output to reuse.
            saved_objective = checkpoint.state.get("objective")
            if saved_objective != request.objective:
                raise ValueError("resume objective must match the saved workflow objective")
        elif (
            not isinstance(saved_fingerprint, str)
            or saved_fingerprint != expected_fingerprint
        ):
            raise ValueError(
                "resume objective must match; request or specialist plan or evidence "
                "registry does not match the saved workflow"
            )
        prior = tuple(_response_from_state(item) for item in raw_responses)
        return self.run(
            request, specialists, executor, checkpoint_store,
            workflow_id=workflow_id, prior_responses=prior, evidence_claims=evidence_claims,
        )


def workflow_fingerprint(
    request: WorkflowRequest,
    specialists: Sequence[SpecialistAssignment],
    evidence_claims: Sequence[EvidenceClaim],
) -> str:
    """Bind resumable work to the exact request, specialist plan and evidence registry."""
    claim_records: list[dict[str, Any]] = []
    for claim in evidence_claims:
        record = claim.model_dump(mode="json")
        record["sources"] = sorted(
            record["sources"], key=lambda source: source["source_id"]
        )
        claim_records.append(record)
    payload = {
        "objective": request.objective,
        "evidence_claims": sorted(claim_records, key=lambda claim: claim["claim_id"]),
        "context": request.context,
        "untrusted_material": list(request.untrusted_material),
        "max_specialists": request.max_specialists,
        "max_steps": request.max_steps,
        "specialists": [
            {
                "specialist_id": item.specialist_id,
                "specialist_title": item.specialist_title,
                "methodology": item.methodology,
                "objective": item.objective,
                "task": item.task,
                "context": item.context,
                "untrusted_material": list(item.untrusted_material),
                "step_number": item.step_number,
            }
            for item in specialists
        ],
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
        "findings": [{"statement": item.statement, "evidence_refs": list(item.evidence_refs), "evidence_status": item.evidence_status, "claim_ids": list(item.claim_ids)} for item in response.findings],
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
        "findings": [{"statement": item.statement, "evidence_refs": list(item.evidence_refs), "evidence_status": item.evidence_status, "claim_ids": list(item.claim_ids)} for item in result.findings],
        "recommendations": list(result.recommendations),
        "risks": list(result.risks),
        "disagreements": list(result.disagreements),
        "unknowns": list(result.unknowns),
        "evidence_refs": list(result.evidence_refs),
        "limitations": list(result.limitations),
        "steps_completed": result.steps_completed,
    }


def _response_from_state(value: object) -> SpecialistResponse:
    if not isinstance(value, dict):
        raise ValueError("checkpoint response must be an object")
    findings_raw = value.get("findings", [])
    if not isinstance(findings_raw, list):
        raise ValueError("checkpoint findings must be a list")
    findings: list[SpecialistFinding] = []
    for item in findings_raw:
        if not isinstance(item, dict):
            raise ValueError("checkpoint finding must be an object")
        refs = item.get("evidence_refs", [])
        if not isinstance(refs, list):
            raise ValueError("checkpoint evidence_refs must be a list")
        claim_ids = item.get("claim_ids", [])
        if not isinstance(claim_ids, list):
            raise ValueError("checkpoint claim_ids must be a list")
        findings.append(SpecialistFinding(
            statement=str(item.get("statement", "")),
            evidence_refs=tuple(str(ref) for ref in refs),
            evidence_status=cast(Literal["supported", "partial", "unverified", "assumption"], item.get("evidence_status", "unverified")),
            claim_ids=tuple(str(claim_id) for claim_id in claim_ids),
        ))
    def strings(key: str) -> tuple[str, ...]:
        raw = value.get(key, [])
        if not isinstance(raw, list):
            raise ValueError(f"checkpoint {key} must be a list")
        return tuple(str(item) for item in raw)
    return SpecialistResponse(
        specialist_id=str(value.get("specialist_id", "")),
        findings=tuple(findings),
        recommendations=strings("recommendations"),
        risks=strings("risks"),
        challenges=strings("challenges"),
        unknowns=strings("unknowns"),
        limitations=strings("limitations"),
    )


def _validate_findings(
    findings: Sequence[SpecialistFinding],
    claim_registry: dict[str, EvidenceClaim],
) -> None:
    """Validate provenance links, not semantic entailment.

    Claim status and evidence level are reviewer-assigned judgments. Resolving
    claim/source IDs proves traceability only; it does not independently prove
    that source content entails a specialist's wording.
    """
    for finding in findings:
        if not finding.statement.strip():
            raise ValueError("finding statement must not be empty")
        if finding.evidence_status in ("supported", "partial") and not finding.claim_ids:
            raise ValueError("supported or partial findings require validated claim IDs")
        if len(set(finding.claim_ids)) != len(finding.claim_ids):
            raise ValueError("finding claim IDs must be unique")
        referenced_sources: set[str] = set()
        for claim_id in finding.claim_ids:
            claim = claim_registry.get(claim_id)
            if claim is None:
                raise ValueError(f"evidence claim not found: {claim_id}")
            if claim.status in ("contested", "stale", "retracted", "unverified"):
                raise ValueError(f"claim {claim_id} has status {claim.status} and cannot support a finding")
            if claim.evidence_level == "unverified":
                raise ValueError(f"claim {claim_id} has unverified evidence and cannot support a finding")
            referenced_sources.update(source.source_id for source in claim.sources)
        if finding.evidence_status in ("supported", "partial"):
            if not finding.evidence_refs:
                raise ValueError("supported or partial findings require traceable source IDs")
            unknown_sources = set(finding.evidence_refs) - referenced_sources
            if unknown_sources:
                raise ValueError(
                    "finding source references are not attached to its cited claims: "
                    + ", ".join(sorted(unknown_sources))
                )
        elif finding.evidence_refs and finding.claim_ids:
            unknown_sources = set(finding.evidence_refs) - referenced_sources
            if unknown_sources:
                raise ValueError(
                    "finding source references are not attached to its cited claims: "
                    + ", ".join(sorted(unknown_sources))
                )

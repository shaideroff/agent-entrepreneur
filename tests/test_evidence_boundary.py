from datetime import date
from pathlib import Path

import pytest

from agent_entrepreneur.agents.models import (
    SpecialistFinding,
    SpecialistResponse,
    WorkflowRequest,
)
from agent_entrepreneur.agents.orchestrator import Orchestrator, plan_specialists
from agent_entrepreneur.knowledge.evidence import EvidenceClaim, EvidenceSource
from agent_entrepreneur.workflows.checkpoints import CheckpointStore


def claim(*, status="supported", evidence_level="B"):
    return EvidenceClaim(
        claim_id="claim:margin",
        statement="The pilot contribution margin was positive.",
        claim_type="quantitative",
        scope="One pilot cohort",
        evidence_level=evidence_level,
        status=status,
        sources=[
            EvidenceSource(
                source_id="source:ledger",
                url="https://example.com/ledger",
                title="Pilot ledger",
                accessed_at=date(2026, 11, 8),
                source_type="dataset",
                supports="Pilot revenue and variable costs",
            )
        ],
        contradictions=["Second cohort was negative"] if status == "contested" else [],
        checked_at=date(2026, 11, 8),
    )


def run_finding(finding, claims=()):
    specialists = plan_specialists("evaluate pilot", ["finance"], max_specialists=1)
    return Orchestrator().run(
        WorkflowRequest("evaluate pilot"),
        specialists,
        lambda assignment: SpecialistResponse(
            specialist_id=assignment.specialist_id,
            findings=(finding,),
        ),
        evidence_claims=claims,
    )


def test_supported_finding_requires_a_resolved_claim_not_just_source_ref():
    finding = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_refs=("https://example.com/ledger",),
        evidence_status="supported",
    )
    result = run_finding(finding)
    assert result.status == "failed"
    assert "claim IDs" in (result.error or "")


def test_supported_finding_resolves_claim_and_preserves_claim_id():
    finding = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_refs=("source:ledger",),
        evidence_status="supported",
        claim_ids=("claim:margin",),
    )
    result = run_finding(finding, (claim(),))
    assert result.findings[0].claim_ids == ("claim:margin",)
    assert result.findings[0].evidence_status == "supported"


def test_contested_claim_cannot_support_a_supported_finding():
    finding = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_refs=("source:ledger",),
        evidence_status="supported",
        claim_ids=("claim:margin",),
    )
    result = run_finding(finding, (claim(status="contested"),))
    assert result.status == "failed"
    assert "contested" in (result.error or "")


def test_unknown_claim_id_is_rejected():
    finding = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_refs=("source:ledger",),
        evidence_status="supported",
        claim_ids=("claim:missing",),
    )
    result = run_finding(finding, (claim(),))
    assert result.status == "failed"
    assert "not found" in (result.error or "")


def test_unverified_finding_remains_valid_without_claim_record():
    result = run_finding(SpecialistFinding("Margin needs validation."))
    assert result.findings[0].evidence_status == "unverified"



def test_finding_rejects_source_not_attached_to_cited_claim():
    finding = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_refs=("source:unrelated",),
        evidence_status="supported",
        claim_ids=("claim:margin",),
    )
    result = run_finding(finding, (claim(),))
    assert result.status == "failed"
    assert "not attached" in (result.error or "")


def test_supported_finding_requires_source_reference():
    finding = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_status="supported",
        claim_ids=("claim:margin",),
    )
    result = run_finding(finding, (claim(),))
    assert result.status == "failed"
    assert "source IDs" in (result.error or "")


def test_duplicate_claim_ids_in_registry_are_rejected():
    specialists = plan_specialists("evaluate pilot", ["finance"], max_specialists=1)
    with pytest.raises(ValueError, match="unique"):
        Orchestrator().run(
            WorkflowRequest("evaluate pilot"),
            specialists,
            lambda assignment: SpecialistResponse(specialist_id=assignment.specialist_id),
            evidence_claims=(claim(), claim()),
        )



def test_checkpoint_round_trip_preserves_claim_ids_and_resume_revalidates(tmp_path: Path):
    specialists = plan_specialists("evaluate pilot", ["finance", "operations"], max_specialists=2)
    store = CheckpointStore(tmp_path / "evidence-resume.db")
    orchestrator = Orchestrator()
    calls = 0
    supported = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_refs=("source:ledger",),
        evidence_status="supported",
        claim_ids=("claim:margin",),
    )

    def interrupt_after_first(assignment):
        nonlocal calls
        calls += 1
        if assignment.step_number == 2:
            raise RuntimeError("temporary interruption")
        return SpecialistResponse(
            specialist_id=assignment.specialist_id,
            findings=(supported,),
        )

    first = orchestrator.run(
        WorkflowRequest("evaluate pilot", max_specialists=2),
        specialists,
        interrupt_after_first,
        store,
        evidence_claims=(claim(),),
    )
    assert first.status == "partial"
    checkpoint = store.resume(first.workflow_id)
    assert checkpoint is not None
    saved_finding = checkpoint.state["responses"][0]["findings"][0]
    assert saved_finding["claim_ids"] == ["claim:margin"]

    resumed = orchestrator.resume(
        first.workflow_id,
        WorkflowRequest("evaluate pilot", max_specialists=2),
        specialists,
        lambda assignment: SpecialistResponse(specialist_id=assignment.specialist_id),
        store,
        evidence_claims=(claim(),),
    )
    assert resumed.status == "completed"
    assert resumed.findings[0].claim_ids == ("claim:margin",)

    with pytest.raises(ValueError, match="not found"):
        orchestrator.resume(
            first.workflow_id,
            WorkflowRequest("evaluate pilot", max_specialists=2),
            specialists,
            lambda assignment: SpecialistResponse(specialist_id=assignment.specialist_id),
            store,
            evidence_claims=(),
        )

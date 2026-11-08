from datetime import date

import pytest

from agent_entrepreneur.agents.models import (
    SpecialistFinding,
    SpecialistResponse,
    WorkflowRequest,
)
from agent_entrepreneur.agents.orchestrator import Orchestrator, plan_specialists
from agent_entrepreneur.knowledge.evidence import EvidenceClaim, EvidenceSource


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
    with pytest.raises(ValueError, match="claim"):
        run_finding(finding)


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
        evidence_status="supported",
        claim_ids=("claim:margin",),
    )
    with pytest.raises(ValueError, match="contested"):
        run_finding(finding, (claim(status="contested"),))


def test_unknown_claim_id_is_rejected():
    finding = SpecialistFinding(
        "The pilot contribution margin was positive.",
        evidence_status="supported",
        claim_ids=("claim:missing",),
    )
    with pytest.raises(ValueError, match="not found"):
        run_finding(finding, (claim(),))


def test_unverified_finding_remains_valid_without_claim_record():
    result = run_finding(SpecialistFinding("Margin needs validation."))
    assert result.findings[0].evidence_status == "unverified"

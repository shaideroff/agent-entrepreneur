"""Tests for the v1.1 entrepreneur experience-agent contracts."""
import pytest
from pydantic import ValidationError

from agent_entrepreneur.agents.experience_models import (
    EvidenceStatus,
    ExperienceAgentRecord,
    ExperienceAgentStatus,
    ExperienceDossier,
    PrincipleRecord,
    SourceRecord,
)


def test_preview_is_the_safe_default() -> None:
    agent = ExperienceAgentRecord(
        agent_id="example",
        display_name="Example Experience Agent",
        experience_lens="Documented operating principles",
    )
    assert agent.status is ExperienceAgentStatus.PREVIEW


def test_claim_evidence_status_is_explicit() -> None:
    principle = PrincipleRecord(
        principle_id="p1",
        statement="Start with a narrow customer problem.",
        source_ids=["s1"],
        evidence_status=EvidenceStatus.PARTIALLY_SUPPORTED,
    )
    assert principle.evidence_status is EvidenceStatus.PARTIALLY_SUPPORTED


def test_dossier_rejects_unknown_source_references() -> None:
    dossier = ExperienceDossier(
        agent_id="example",
        version="1.0.0",
        experience_thesis="A sourced example dossier.",
        principles=[
            PrincipleRecord(
                principle_id="p1",
                statement="A principle.",
                source_ids=["missing"],
                evidence_status=EvidenceStatus.UNVERIFIED,
            )
        ],
        non_affiliation_notice="This AI agent is not affiliated with or endorsed by the person.",
    )
    with pytest.raises(ValueError, match="Unknown source identifiers"):
        dossier.validate_source_references()


def test_dossier_accepts_resolvable_sources() -> None:
    dossier = ExperienceDossier(
        agent_id="example",
        version="1.0.0",
        experience_thesis="A sourced example dossier.",
        principles=[
            PrincipleRecord(
                principle_id="p1",
                statement="A principle.",
                source_ids=["s1"],
                evidence_status=EvidenceStatus.VERIFIED,
            )
        ],
        sources=[SourceRecord(source_id="s1", title="Primary source")],
        non_affiliation_notice="This AI agent is not affiliated with or endorsed by the person.",
    )
    assert dossier.validate_source_references() is dossier


def test_invalid_evidence_status_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PrincipleRecord(
            principle_id="p1",
            statement="A principle.",
            source_ids=["s1"],
            evidence_status="guess",
        )


def test_dossier_rejects_duplicate_source_ids() -> None:
    dossier = ExperienceDossier(
        agent_id="example",
        version="1.0.0",
        experience_thesis="A sourced example dossier.",
        sources=[
            SourceRecord(source_id="s1", title="Source one"),
            SourceRecord(source_id="s1", title="Duplicate source"),
        ],
        non_affiliation_notice="This AI agent is not affiliated with or endorsed by the person.",
    )
    with pytest.raises(ValueError, match="Source identifiers must be unique"):
        dossier.validate_source_references()


def test_dossier_supports_governance_and_evaluation_metadata() -> None:
    dossier = ExperienceDossier(
        agent_id="example",
        version="1.0.0",
        experience_thesis="A sourced example dossier.",
        failure_modes=["Overgeneralising from one case."],
        out_of_scope=["Legal advice."],
        evaluation_refs=["eval-001"],
        owner="Project maintainer",
        last_verified_at="2026-11-09",
        next_review_at="2027-02-09",
        non_affiliation_notice="This AI agent is not affiliated with or endorsed by the person.",
    )
    assert dossier.evaluation_refs == ["eval-001"]
    assert dossier.failure_modes

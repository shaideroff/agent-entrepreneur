from datetime import date

import pytest
from pydantic import ValidationError

from agent_entrepreneur.knowledge.evidence import (
    EvidenceClaim,
    EvidenceSource,
    claim_freshness,
)


def source(**overrides: object) -> EvidenceSource:
    values: dict[str, object] = {
        "source_id": "src-001",
        "url": "https://example.org/report",
        "source_type": "primary",
        "accessed_at": date(2026, 11, 8),
        "supports": "The reported operating metric.",
    }
    values.update(overrides)
    return EvidenceSource.model_validate(values)


def claim(**overrides: object) -> EvidenceClaim:
    values: dict[str, object] = {
        "claim_id": "claim-001",
        "statement": "The pilot reached 100 paying customers.",
        "claim_type": "quantitative",
        "evidence_level": "B",
        "status": "supported",
        "sources": [source().model_dump(mode="json")],
        "checked_at": date(2026, 11, 8),
    }
    values.update(overrides)
    return EvidenceClaim.model_validate(values)


def test_claim_requires_traceable_source() -> None:
    with pytest.raises(ValidationError):
        claim(sources=[])


def test_claim_rejects_empty_statement() -> None:
    with pytest.raises(ValidationError):
        claim(statement="  ")


def test_source_requires_http_url() -> None:
    with pytest.raises(ValidationError):
        source(url="not-a-url")


def test_claim_cannot_be_supported_when_marked_unverified() -> None:
    with pytest.raises(ValidationError):
        claim(evidence_level="unverified", status="supported")


def test_contested_claim_requires_recorded_contradiction() -> None:
    with pytest.raises(ValidationError):
        claim(status="contested", contradictions=[])


def test_claim_freshness_uses_explicit_review_window() -> None:
    item = claim(checked_at=date(2026, 1, 1))
    assert claim_freshness(item, as_of=date(2026, 11, 8), max_age_days=30) == "stale"
    assert claim_freshness(item, as_of=date(2026, 11, 8), max_age_days=400) == "fresh"


def test_claim_freshness_rejects_negative_window() -> None:
    with pytest.raises(ValueError):
        claim_freshness(claim(), as_of=date(2026, 11, 8), max_age_days=-1)


def test_source_published_date_cannot_be_after_access_date() -> None:
    with pytest.raises(ValidationError):
        source(published_at=date(2026, 11, 9), accessed_at=date(2026, 11, 8))

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

EvidenceLevel = Literal["A", "B", "C", "unverified"]
ClaimType = Literal["descriptive", "causal", "prescriptive", "quantitative", "historical"]
ClaimStatus = Literal["supported", "contested", "stale", "retracted", "unverified"]
SourceType = Literal[
    "primary",
    "independent_secondary",
    "official_filing",
    "dataset",
    "interview",
    "other",
]
Freshness = Literal["fresh", "stale"]


class EvidenceSource(BaseModel):
    """Traceable source metadata; existence does not itself prove support."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_id: str = Field(min_length=1)
    url: HttpUrl
    title: str | None = None
    publisher: str | None = None
    author: str | None = None
    published_at: date | None = None
    accessed_at: date
    source_type: SourceType
    supports: str | None = None
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def publication_not_after_access(self) -> EvidenceSource:
        if self.published_at is not None and self.published_at > self.accessed_at:
            raise ValueError("published_at cannot be after accessed_at")
        return self


class EvidenceClaim(BaseModel):
    """A bounded claim whose evidence, status and contradictions remain inspectable."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    claim_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    claim_type: ClaimType
    scope: str = ""
    population_or_context: str = ""
    limitations: list[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel
    status: ClaimStatus
    sources: list[EvidenceSource] = Field(min_length=1)
    contradictions: list[str] = Field(default_factory=list)
    reviewed_at: date | None = None
    checked_at: date

    @model_validator(mode="after")
    def status_has_consistent_provenance(self) -> EvidenceClaim:
        if self.evidence_level == "unverified" and self.status == "supported":
            raise ValueError("unverified evidence cannot have supported status")
        if self.status == "contested" and not self.contradictions:
            raise ValueError("contested claims must record at least one contradiction")
        if len({source.source_id for source in self.sources}) != len(self.sources):
            raise ValueError("source_id values must be unique within a claim")
        return self


def claim_freshness(
    claim: EvidenceClaim,
    *,
    as_of: date,
    max_age_days: int,
) -> Freshness:
    """Evaluate freshness against a caller-selected policy window.

    The function does not mutate claim status: freshness is a time-dependent
    assessment, while status records the reviewer's current evidence judgment.
    """
    if max_age_days < 0:
        raise ValueError("max_age_days must be non-negative")
    age_days = (as_of - claim.checked_at).days
    return "stale" if age_days > max_age_days else "fresh"

"""Typed contracts for named entrepreneur experience agents.

These models describe inspectable dossiers and work packets. They do not
simulate or speak on behalf of the real people named in the catalogue.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceStatus(StrEnum):
    VERIFIED = "verified"
    CORROBORATED = "corroborated"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"


class ExperienceAgentStatus(StrEnum):
    ACTIVE = "active"
    PREVIEW = "preview"
    RETIRED = "retired"


class SourceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str | None = None
    publisher: str | None = None
    published_at: str | None = None
    accessed_at: str | None = None
    source_type: Literal["primary", "independent", "secondary", "other"] = "other"
    notes: str | None = None


class PrincipleRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principle_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)
    evidence_status: EvidenceStatus
    limitations: list[str] = Field(default_factory=list)


class DecisionCaseRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    context: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    outcome: str | None = None
    source_ids: list[str] = Field(min_length=1)
    evidence_status: EvidenceStatus
    limitations: list[str] = Field(default_factory=list)


class ExperienceDossier(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    experience_thesis: str = Field(min_length=1)
    principles: list[PrincipleRecord] = Field(default_factory=list)
    decision_cases: list[DecisionCaseRecord] = Field(default_factory=list)
    sources: list[SourceRecord] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    transfer_conditions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    evaluation_refs: list[str] = Field(default_factory=list)
    owner: str | None = None
    reviewer: str | None = None
    last_verified_at: str | None = None
    next_review_at: str | None = None
    non_affiliation_notice: str = Field(min_length=1)

    def validate_source_references(self) -> "ExperienceDossier":
        source_ids = {source.source_id for source in self.sources}
        if len(source_ids) != len(self.sources):
            raise ValueError("Source identifiers must be unique within a dossier")
        principle_ids = [item.principle_id for item in self.principles]
        case_ids = [item.case_id for item in self.decision_cases]
        if len(set(principle_ids)) != len(principle_ids):
            raise ValueError("Principle identifiers must be unique within a dossier")
        if len(set(case_ids)) != len(case_ids):
            raise ValueError("Decision case identifiers must be unique within a dossier")
        referenced = {
            source_id
            for item in [*self.principles, *self.decision_cases]
            for source_id in item.source_ids
        }
        missing = referenced - source_ids
        if missing:
            raise ValueError(f"Unknown source identifiers: {sorted(missing)}")
        return self


class ExperienceAgentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    experience_lens: str = Field(min_length=1)
    domains: list[str] = Field(default_factory=list)
    status: ExperienceAgentStatus = ExperienceAgentStatus.PREVIEW
    dossier_version: str | None = None
    dossier_ref: str | None = None


class ExperienceAgentSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(min_length=1)
    selected_agent_ids: list[str] = Field(min_length=1, max_length=5)
    rationale: dict[str, str]
    selection_mode: Literal["lead", "user_selected"] = "lead"


class ExperienceAgentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1)
    documented_facts: list[str] = Field(default_factory=list)
    interpretations: list[str] = Field(default_factory=list)
    analogies: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class CouncilChallenge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    challenger_agent_id: str = Field(min_length=1)
    target_agent_id: str = Field(min_length=1)
    challenged_statement: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)
    severity: Literal["low", "medium", "high"] = "medium"


class CouncilSynthesis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(min_length=1)
    contributions: list[ExperienceAgentResponse] = Field(min_length=1)
    challenges: list[CouncilChallenge] = Field(default_factory=list)
    agreements: list[str] = Field(default_factory=list)
    disagreements: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    recommendation: str = Field(min_length=1)

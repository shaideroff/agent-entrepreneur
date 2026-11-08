from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True, slots=True)
class WorkflowRequest:
    objective: str
    context: str = ""
    untrusted_material: tuple[str, ...] = ()
    max_specialists: int = 3
    max_steps: int = 12


@dataclass(frozen=True, slots=True)
class SpecialistAssignment:
    specialist_id: str
    specialist_title: str
    methodology: str
    objective: str
    task: str
    context: str
    untrusted_material: tuple[str, ...] = ()
    step_number: int = 1


@dataclass(frozen=True, slots=True)
class SpecialistFinding:
    statement: str
    evidence_refs: tuple[str, ...] = ()
    evidence_status: Literal["supported", "partial", "unverified", "assumption"] = "unverified"
    claim_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SpecialistResponse:
    specialist_id: str
    findings: tuple[SpecialistFinding, ...] = ()
    recommendations: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    challenges: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    workflow_id: str
    status: Literal["completed", "partial", "failed"]
    objective: str
    specialists_consulted: tuple[str, ...]
    findings: tuple[SpecialistFinding, ...]
    recommendations: tuple[str, ...]
    risks: tuple[str, ...]
    disagreements: tuple[str, ...]
    unknowns: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...] = ()
    steps_completed: int = 0
    error: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowCheckpoint:
    workflow_id: str
    status: Literal["running", "completed", "partial", "failed"]
    state: dict[str, object] = field(default_factory=dict)

from dataclasses import dataclass
from agent_entrepreneur.agents.registry import SPECIALISTS
@dataclass(frozen=True, slots=True)
class SpecialistTask:
    specialist_id: str
    task: str
    requires_evidence: bool = True
def plan_specialists(objective: str, domains: list[str], *, max_specialists: int = 3) -> list[SpecialistTask]:
    if not 1 <= max_specialists <= 6: raise ValueError("max_specialists must be between 1 and 6")
    matched = []
    for specialist_id, profile in SPECIALISTS.items():
        if any(domain.casefold() in [d.casefold() for d in profile["domains"]] for domain in domains):
            matched.append(SpecialistTask(specialist_id, f"Analyse this aspect of the objective: {objective}"))
        if len(matched) >= max_specialists: break
    return matched or [SpecialistTask("built_from_zero", f"Clarify and scope: {objective}")]

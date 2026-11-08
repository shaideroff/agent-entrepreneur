from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from typing import Any, Literal, cast

from mcp.server.fastmcp import FastMCP

from agent_entrepreneur.agents.models import (
    SpecialistFinding,
    SpecialistResponse,
    WorkflowRequest,
)
from agent_entrepreneur.agents.orchestrator import Orchestrator, plan_specialists
from agent_entrepreneur.config import Settings
from agent_entrepreneur.domain.models import (
    EvidenceReference,
    BusinessAnalysisInput,
    BusinessInput,
    DecisionInput,
    ExecutionPlanInput,
    MarketResearchInput,
    OutcomeReviewInput,
)
from agent_entrepreneur.knowledge.evidence import EvidenceClaim
from agent_entrepreneur.knowledge.registry import KnowledgeRepository
from agent_entrepreneur.memory.service import MemoryService
from agent_entrepreneur.services.core import (
    analyse_business as run_business_analysis,
    create_execution_plan as build_execution_plan,
    evaluate_decision as assess_decision,
    research_market as prepare_market_research,
    review_outcomes as run_outcome_review,
    understand_business as build_business_understanding,
)
from agent_entrepreneur.workflows.checkpoints import CheckpointStore


def _string_values(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(value)


def _parse_specialist_responses(
    raw_responses: list[dict[str, Any]],
) -> dict[str, SpecialistResponse]:
    parsed: dict[str, SpecialistResponse] = {}
    for raw in raw_responses:
        specialist_id = raw.get("specialist_id")
        if not isinstance(specialist_id, str) or not specialist_id.strip():
            raise ValueError("each specialist response requires a specialist_id")
        if specialist_id in parsed:
            raise ValueError(f"duplicate specialist response: {specialist_id}")
        findings_raw = raw.get("findings", [])
        if not isinstance(findings_raw, list):
            raise ValueError("specialist findings must be a list")
        findings: list[SpecialistFinding] = []
        for item in findings_raw:
            if not isinstance(item, dict):
                raise ValueError("each specialist finding must be an object")
            statement = item.get("statement")
            if not isinstance(statement, str) or not statement.strip():
                raise ValueError("each specialist finding requires a statement")
            status = item.get("evidence_status", "unverified")
            if not isinstance(status, str) or status not in {
                "supported", "partial", "unverified", "assumption"
            }:
                raise ValueError("specialist finding evidence_status is invalid")
            findings.append(
                SpecialistFinding(
                    statement=statement,
                    evidence_refs=_string_values(item.get("evidence_refs", []), "evidence_refs"),
                    evidence_status=cast(
                        Literal["supported", "partial", "unverified", "assumption"], status
                    ),
                    claim_ids=_string_values(item.get("claim_ids", []), "claim_ids"),
                )
            )
        parsed[specialist_id] = SpecialistResponse(
            specialist_id=specialist_id,
            findings=tuple(findings),
            recommendations=_string_values(raw.get("recommendations", []), "recommendations"),
            risks=_string_values(raw.get("risks", []), "risks"),
            challenges=_string_values(raw.get("challenges", []), "challenges"),
            unknowns=_string_values(raw.get("unknowns", []), "unknowns"),
            limitations=_string_values(raw.get("limitations", []), "limitations"),
        )
    return parsed


def _parse_evidence_claims(raw_claims: list[dict[str, Any]] | None) -> tuple[EvidenceClaim, ...]:
    if raw_claims is None:
        return ()
    return tuple(EvidenceClaim.model_validate(item) for item in raw_claims)


def _workflow_result_payload(result: Any) -> dict[str, Any]:
    return json.loads(json.dumps(asdict(result), ensure_ascii=False))


def create_server(settings: Settings) -> FastMCP:
    mcp = FastMCP(
        "Agent Entrepreneur",
        instructions=(
            "Model-independent entrepreneurial intelligence. Separate facts, assumptions, "
            "recommendations and unknowns. Cite evidence. Never impersonate real entrepreneurs. "
            "The connected client performs reasoning and may use its own research tools. "
            "Consequential actions require explicit approval."
        ),
        host=settings.host,
        port=settings.port,
    )
    knowledge = KnowledgeRepository()
    memory = MemoryService(settings.database_path)
    checkpoints = CheckpointStore(settings.database_path)
    orchestrator = Orchestrator()

    @mcp.tool()
    def understand_business(
        name: str,
        industry: str = "",
        geography: str = "",
        stage: str = "",
        description: str = "",
        products: list[str] | None = None,
        customer_segments: list[str] | None = None,
        revenue_model: str = "",
        constraints: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a structured business baseline and identify missing information."""
        data = BusinessInput(
            name=name,
            industry=industry or None,
            geography=geography or None,
            stage=stage or None,
            description=description,
            products=products or [],
            customer_segments=customer_segments or [],
            revenue_model=revenue_model or None,
            constraints=constraints or [],
        )
        return build_business_understanding(data).model_dump(mode="json")

    @mcp.tool()
    def research_market(
        market: str,
        geography: str,
        customer: str = "",
        research_questions: list[str] | None = None,
        supplied_sources: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Prepare a market research brief and attach source references supplied by the client."""
        source_records = [
            EvidenceReference.model_validate(item) for item in (supplied_sources or [])
        ]
        return prepare_market_research(
            MarketResearchInput(
                market=market,
                geography=geography,
                customer=customer or None,
                research_questions=research_questions or [],
                supplied_sources=source_records,
            )
        ).model_dump(mode="json")

    @mcp.tool()
    def analyse_business(
        name: str,
        industry: str = "",
        geography: str = "",
        metrics: dict[str, float] | None = None,
        question: str = "Diagnose the business model and identify priority issues.",
    ) -> dict[str, Any]:
        """Analyse supplied business metrics and prepare deeper client reasoning."""
        business = BusinessInput(name=name, industry=industry or None, geography=geography or None)
        return run_business_analysis(
            BusinessAnalysisInput(business=business, metrics=metrics or {}, question=question)
        ).model_dump(mode="json")

    @mcp.tool()
    def evaluate_decision(
        decision: str,
        options: list[str],
        objectives: list[str] | None = None,
        constraints: list[str] | None = None,
        risk_tolerance: str = "moderate",
    ) -> dict[str, Any]:
        """Structure a decision into comparable options, risks and trade-offs."""
        return assess_decision(
            DecisionInput(
                decision=decision,
                options=options,
                objectives=objectives or [],
                constraints=constraints or [],
                risk_tolerance=risk_tolerance,
            )
        ).model_dump(mode="json")

    @mcp.tool()
    def create_execution_plan(
        objective: str,
        horizon_days: int = 30,
        resources: list[str] | None = None,
        constraints: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create an editable milestone plan; no external actions are performed."""
        return build_execution_plan(
            ExecutionPlanInput(
                objective=objective,
                horizon_days=horizon_days,
                resources=resources or [],
                constraints=constraints or [],
            )
        ).model_dump(mode="json")

    @mcp.tool()
    def review_outcomes(
        objective: str,
        expected_outcome: str,
        actual_outcome: str,
        metrics: dict[str, float] | None = None,
        lessons: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare expected and actual outcomes and prepare a learning review."""
        return run_outcome_review(
            OutcomeReviewInput(
                objective=objective,
                expected_outcome=expected_outcome,
                actual_outcome=actual_outcome,
                metrics=metrics or {},
                lessons=lessons or [],
            )
        ).model_dump(mode="json")

    @mcp.tool()
    def plan_specialist_workflow(
        objective: str,
        domains: list[str],
        context: str = "",
        max_specialists: int = 3,
    ) -> dict[str, Any]:
        """Create a bounded, deterministic plan for connected-client specialist reasoning."""
        if not objective.strip():
            raise ValueError("objective must not be empty")
        specialists = plan_specialists(objective, domains, max_specialists=max_specialists)
        return {
            "workflow_id": str(uuid.uuid4()),
            "objective": objective,
            "context": context,
            "max_specialists": max_specialists,
            "specialists": [
                {
                    "specialist_id": item.specialist_id,
                    "specialist_title": item.specialist_title,
                    "methodology": item.methodology,
                    "task": item.task,
                }
                for item in specialists
            ],
            "execution_boundary": (
                "The connected MCP client performs specialist reasoning. Submit structured "
                "responses to complete_specialist_workflow; no model provider is embedded."
            ),
        }

    @mcp.tool()
    def complete_specialist_workflow(
        workflow_id: str,
        objective: str,
        domains: list[str],
        specialist_responses: list[dict[str, Any]],
        context: str = "",
        max_specialists: int = 3,
        evidence_claims: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Validate and checkpoint client-produced specialist findings and consolidate results."""
        if not workflow_id.strip() or not objective.strip():
            raise ValueError("workflow_id and objective must not be empty")
        specialists = plan_specialists(objective, domains, max_specialists=max_specialists)
        expected_ids = [item.specialist_id for item in specialists]
        responses = _parse_specialist_responses(specialist_responses)
        if set(responses) != set(expected_ids):
            raise ValueError("specialist responses must match the planned specialist IDs exactly")
        claims = _parse_evidence_claims(evidence_claims)
        request = WorkflowRequest(
            objective=objective,
            context=context,
            max_specialists=max_specialists,
        )
        result = orchestrator.run(
            request,
            specialists,
            lambda assignment: responses[assignment.specialist_id],
            checkpoints,
            workflow_id=workflow_id,
            evidence_claims=claims,
        )
        return _workflow_result_payload(result)

    @mcp.tool()
    def resume_specialist_workflow(
        workflow_id: str,
        objective: str,
        domains: list[str],
        specialist_responses: list[dict[str, Any]],
        context: str = "",
        max_specialists: int = 3,
        evidence_claims: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Resume only unfinished specialists after validating the saved request and plan."""
        if not workflow_id.strip() or not objective.strip():
            raise ValueError("workflow_id and objective must not be empty")
        specialists = plan_specialists(objective, domains, max_specialists=max_specialists)
        checkpoint = checkpoints.resume(workflow_id)
        if checkpoint is None:
            raise ValueError(f"workflow checkpoint not found: {workflow_id}")
        completed_raw = checkpoint.state.get("responses", [])
        if not isinstance(completed_raw, list):
            raise ValueError("checkpoint responses are invalid")
        completed_ids = {
            item.get("specialist_id")
            for item in completed_raw
            if isinstance(item, dict) and isinstance(item.get("specialist_id"), str)
        }
        expected_ids = [item.specialist_id for item in specialists]
        remaining_ids = set(expected_ids) - completed_ids
        responses = _parse_specialist_responses(specialist_responses)
        if set(responses) != remaining_ids:
            raise ValueError("resume responses must match the unfinished specialist IDs exactly")
        claims = _parse_evidence_claims(evidence_claims)
        request = WorkflowRequest(
            objective=objective,
            context=context,
            max_specialists=max_specialists,
        )
        result = orchestrator.resume(
            workflow_id,
            request,
            specialists,
            lambda assignment: responses[assignment.specialist_id],
            checkpoints,
            evidence_claims=claims,
        )
        return _workflow_result_payload(result)

    @mcp.tool()
    def search_entrepreneurs(
        query: str = "",
        domain: str = "",
        region: str = "",
        evidence_level: str = "",
    ) -> list[dict[str, Any]]:
        """Search the attributed entrepreneur knowledge registry and filter by evidence level."""
        return knowledge.search_profiles(
            query=query,
            domain=domain or None,
            region=region or None,
            evidence_level=evidence_level or None,
        )

    @mcp.tool()
    def save_memory(content: str, scope: str = "user", consent: bool = False) -> dict[str, str]:
        """Save a local memory record only after explicit user consent."""
        if not content.strip() or len(content) > 20_000:
            raise ValueError("memory content must contain 1 to 20000 characters")
        if not scope.strip() or len(scope) > 128:
            raise ValueError("memory scope must contain 1 to 128 characters")
        record_id = memory.save(content, scope=scope, consent=consent)
        return {"record_id": record_id, "scope": scope}

    @mcp.tool()
    def search_memory(query: str = "", scope: str = "user") -> list[dict[str, Any]]:
        """Search local memory records within the requested scope."""
        if len(query) > 500 or not scope.strip() or len(scope) > 128:
            raise ValueError("memory query or scope exceeds its allowed length")
        return memory.search(query=query, scope=scope)

    @mcp.tool()
    def delete_memory(record_id: str) -> dict[str, bool]:
        """Delete a local memory record by its identifier."""
        if not record_id.strip():
            raise ValueError("record_id must not be empty")
        return {"deleted": memory.delete(record_id)}

    @mcp.resource("agent-entrepreneur://knowledge/specialists")
    def specialist_catalog() -> str:
        """List available specialist roles and expertise domains."""
        from agent_entrepreneur.agents.registry import SPECIALISTS

        return json.dumps(SPECIALISTS, indent=2)

    @mcp.resource("agent-entrepreneur://knowledge/entrepreneurs")
    def entrepreneur_catalog() -> str:
        """List entrepreneur reference profiles and evidence labels."""
        return json.dumps(knowledge.search_profiles(), indent=2)

    @mcp.prompt()
    def business_diagnosis(business_name: str, context: str = "") -> str:
        """Guide an evidence-led business diagnosis."""
        return (
            f"Diagnose {business_name}. Context: {context}. Separate facts, assumptions, "
            "unknowns and recommendations. Assess customer value, model, unit economics, "
            "distribution, operations and risks."
        )

    @mcp.prompt()
    def market_entry_assessment(market: str, geography: str) -> str:
        """Prepare a structured market-entry assessment."""
        return (
            f"Assess entry into {market} in {geography}. Examine demand, customer segments, "
            "competitors, regulation, distribution, economics, risks and reversibility. Cite "
            "current sources and distinguish findings from assumptions."
        )

    @mcp.prompt()
    def founder_execution_review(objective: str) -> str:
        """Apply a Built from Zero lens to a founder objective."""
        return (
            f"Review: {objective}. Apply discover, build, sell, systemise and scale. Adapt to "
            "actual resources; do not assume funding, team capacity or product-market fit. "
            "Produce measurable milestones and decision gates."
        )

    return mcp


def main() -> None:
    settings = Settings.from_env()
    server = create_server(settings)
    server.run(transport=settings.transport)


if __name__ == "__main__":
    main()

from __future__ import annotations
import json
import logging
from typing import Any
from mcp.server.fastmcp import FastMCP
from agent_entrepreneur.config import Settings, is_loopback_host
from agent_entrepreneur.domain.models import BusinessAnalysisInput, BusinessInput, DecisionInput, ExecutionPlanInput, MarketResearchInput, OutcomeReviewInput
from agent_entrepreneur.knowledge.registry import KnowledgeRepository
from agent_entrepreneur.services.core import analyse_business as run_business_analysis, create_execution_plan as build_execution_plan, evaluate_decision as assess_decision, research_market as prepare_market_research, review_outcomes as run_outcome_review, understand_business as build_business_understanding

logger = logging.getLogger("agent_entrepreneur")

def create_server(settings: Settings) -> FastMCP:
    mcp = FastMCP("Agent Entrepreneur", instructions="Model-independent entrepreneurial intelligence. Separate facts, assumptions, recommendations and unknowns. Cite evidence. Never impersonate real entrepreneurs. The connected client performs reasoning. Consequential actions require explicit approval.", host=settings.host, port=settings.port)
    knowledge = KnowledgeRepository()
    @mcp.tool()
    def understand_business(name: str, industry: str = "", geography: str = "", stage: str = "", description: str = "", products: list[str] | None = None, customer_segments: list[str] | None = None, revenue_model: str = "", constraints: list[str] | None = None) -> dict[str, Any]:
        """Create a structured business baseline and identify missing information."""
        data = BusinessInput(name=name, industry=industry or None, geography=geography or None, stage=stage or None, description=description, products=products or [], customer_segments=customer_segments or [], revenue_model=revenue_model or None, constraints=constraints or [])
        return build_business_understanding(data).model_dump(mode="json")
    @mcp.tool()
    def research_market(market: str, geography: str, customer: str = "", research_questions: list[str] | None = None) -> dict[str, Any]:
        """Prepare a market research brief and explicitly identify evidence gaps."""
        return prepare_market_research(MarketResearchInput(market=market, geography=geography, customer=customer or None, research_questions=research_questions or [])).model_dump(mode="json")
    @mcp.tool()
    def analyse_business(name: str, industry: str = "", geography: str = "", metrics: dict[str, float] | None = None, question: str = "Diagnose the business model and identify priority issues.") -> dict[str, Any]:
        """Analyse supplied business metrics and prepare deeper client reasoning."""
        business = BusinessInput(name=name, industry=industry or None, geography=geography or None)
        return run_business_analysis(BusinessAnalysisInput(business=business, metrics=metrics or {}, question=question)).model_dump(mode="json")
    @mcp.tool()
    def evaluate_decision(decision: str, options: list[str], objectives: list[str] | None = None, constraints: list[str] | None = None, risk_tolerance: str = "moderate") -> dict[str, Any]:
        """Structure a decision into comparable options, risks and trade-offs."""
        return assess_decision(DecisionInput(decision=decision, options=options, objectives=objectives or [], constraints=constraints or [], risk_tolerance=risk_tolerance)).model_dump(mode="json")
    @mcp.tool()
    def create_execution_plan(objective: str, horizon_days: int = 30, resources: list[str] | None = None, constraints: list[str] | None = None) -> dict[str, Any]:
        """Create an editable milestone plan; no external actions are performed."""
        return build_execution_plan(ExecutionPlanInput(objective=objective, horizon_days=horizon_days, resources=resources or [], constraints=constraints or [])).model_dump(mode="json")
    @mcp.tool()
    def review_outcomes(objective: str, expected_outcome: str, actual_outcome: str, metrics: dict[str, float] | None = None, lessons: list[str] | None = None) -> dict[str, Any]:
        """Compare expected and actual outcomes and prepare a learning review."""
        return run_outcome_review(OutcomeReviewInput(objective=objective, expected_outcome=expected_outcome, actual_outcome=actual_outcome, metrics=metrics or {}, lessons=lessons or [])).model_dump(mode="json")
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
        return f"Diagnose {business_name}. Context: {context}. Separate facts, assumptions, unknowns and recommendations. Assess customer value, model, unit economics, distribution, operations and risks."
    @mcp.prompt()
    def market_entry_assessment(market: str, geography: str) -> str:
        """Prepare a structured market-entry assessment."""
        return f"Assess entry into {market} in {geography}. Examine demand, customer segments, competitors, regulation, distribution, economics, risks and reversibility. Cite current sources and distinguish findings from assumptions."
    @mcp.prompt()
    def founder_execution_review(objective: str) -> str:
        """Apply a Built from Zero lens to a founder objective."""
        return f"Review: {objective}. Apply discover, build, sell, systemise and scale. Adapt to actual resources; do not assume funding, team capacity or product-market fit. Produce measurable milestones and decision gates."
    return mcp

def main() -> None:
    settings = Settings.from_env()
    server = create_server(settings)
    if settings.transport == "streamable-http" and not is_loopback_host(settings.host):
        logger.warning("Remote HTTP binding explicitly enabled. Protect it with authenticated TLS infrastructure.")
    server.run(transport=settings.transport)

if __name__ == "__main__":
    main()

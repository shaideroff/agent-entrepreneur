from agent_entrepreneur.domain.models import BusinessInput, DecisionInput, ExecutionPlanInput, MarketResearchInput
from agent_entrepreneur.services.core import create_execution_plan, evaluate_decision, research_market, understand_business

def test_business_understanding_separates_unknowns():
    result = understand_business(BusinessInput(name="Example Co", products=["Analytics SaaS"]))
    assert result.confirmed_facts[0] == "Business name: Example Co"
    assert "industry" in result.unknowns and result.next_questions

def test_market_research_does_not_fabricate_live_findings():
    result = research_market(MarketResearchInput(market="EV charging", geography="Delhi"))
    assert result.status == "research_required"
    assert "No live research provider is configured by the core server." in result.findings

def test_decision_assessment_requires_human_decision():
    result = evaluate_decision(DecisionInput(decision="Expand?", options=["A", "B"]))
    assert result.human_decision_required and "Downside risk" in result.evaluation_dimensions

def test_execution_plan_has_bounded_milestones():
    result = create_execution_plan(ExecutionPlanInput(objective="Validate demand", horizon_days=30))
    assert len(result.milestones) == 3 and result.milestones[-1].due_day == 30

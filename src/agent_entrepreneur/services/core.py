from __future__ import annotations
from agent_entrepreneur.domain.models import BusinessAnalysis, BusinessAnalysisInput, BusinessInput, BusinessUnderstanding, DecisionAssessment, DecisionInput, ExecutionPlan, ExecutionPlanInput, Milestone, MarketResearchInput, OutcomeReview, OutcomeReviewInput, ResearchBrief

def understand_business(data: BusinessInput) -> BusinessUnderstanding:
    facts = [f"Business name: {data.name}"] + [f"Product/service: {item}" for item in data.products]
    unknowns = [label for label, value in (("industry", data.industry), ("geography", data.geography), ("stage", data.stage), ("revenue model", data.revenue_model)) if not value]
    questions = [f"What evidence supports the current {item}?" for item in unknowns]
    if not data.customer_segments: questions.append("Who is the primary paying customer, and what problem are they paying to solve?")
    if not data.description: questions.append("What customer problem does the business solve, and how does the solution work?")
    return BusinessUnderstanding(business=data, confirmed_facts=facts, unknowns=unknowns, next_questions=questions)

def research_market(data: MarketResearchInput) -> ResearchBrief:
    findings = ["No live research provider is configured by the core server."]
    if data.supplied_sources: findings.append("User-supplied source references are attached for review; their claims have not been independently verified.")
    return ResearchBrief(market=data.market, geography=data.geography, research_questions=data.research_questions, evidence=data.supplied_sources, findings=findings, gaps=["Market size and growth", "Customer demand and willingness to pay", "Competitor landscape", "Regulatory and distribution constraints"], limitations=["Do not treat this preparation brief as completed market research.", "The connected AI client or a configured research tool must retrieve and verify current sources."])

def analyse_business(data: BusinessAnalysisInput) -> BusinessAnalysis:
    checks = []
    if "revenue" in data.metrics and "costs" in data.metrics:
        checks.append(f"Arithmetic operating surplus from supplied figures: {data.metrics['revenue'] - data.metrics['costs']:.2f} (revenue minus costs; not an audited profit figure).")
    if data.metrics.get("customers", 1) <= 0: checks.append("Customer count is zero or negative; acquisition and revenue metrics need clarification.")
    missing = [key for key in ("gross_margin", "customer_acquisition_cost", "retention_rate", "cash_runway") if key not in data.metrics]
    return BusinessAnalysis(business_name=data.business.name, question=data.question, supplied_metrics=data.metrics, deterministic_checks=checks, missing_information=missing, recommendations_for_client_reasoning=["Assess customer problem-solution fit.", "Test unit economics with cohort-level data.", "Separate one-time revenue from recurring revenue."])

def evaluate_decision(data: DecisionInput) -> DecisionAssessment:
    return DecisionAssessment(decision=data.decision, options=data.options, evaluation_dimensions=["Expected value", "Downside risk", "Reversibility", "Time to evidence", "Capital required", "Strategic fit"], trade_offs_to_assess=[f"Compare {option} against each stated objective and constraint." for option in data.options], missing_information=["Probability and impact of key risks", "Cost and resource estimates", "Evidence supporting demand and feasibility"])

def create_execution_plan(data: ExecutionPlanInput) -> ExecutionPlan:
    horizon = data.horizon_days
    points = sorted(set([max(1, round(horizon * 0.2)), max(1, round(horizon * 0.5)), horizon]))
    titles = ["Validate the problem and baseline", "Run the smallest meaningful experiment", "Review evidence and decide next investment"]
    milestones = [Milestone(title=titles[i], due_day=day, deliverable=titles[i], success_measure="Documented evidence and an explicit go / revise / stop decision") for i, day in enumerate(points)]
    return ExecutionPlan(objective=data.objective, horizon_days=horizon, milestones=milestones, assumptions=["Milestones are a starting template and must be adapted to the business context.", "No external action is executed by this plan."])

def review_outcomes(data: OutcomeReviewInput) -> OutcomeReview:
    observations = [f"Metric supplied: {key} = {value}" for key, value in data.metrics.items()]
    return OutcomeReview(objective=data.objective, expected_outcome=data.expected_outcome, actual_outcome=data.actual_outcome, metric_observations=observations, lessons_to_validate=data.lessons, next_review_questions=["Which assumptions were disproven?", "What changed in customer behaviour?", "What should be stopped, continued or tested next?"])

from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl

class EvidenceReference(BaseModel):
    title: str
    url: HttpUrl | None = None
    source_type: str = "user-provided"
    accessed_at: str | None = None

class BusinessInput(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    industry: str | None = None
    geography: str | None = None
    stage: str | None = None
    description: str = ""
    customer_segments: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    revenue_model: str | None = None
    constraints: list[str] = Field(default_factory=list)

class BusinessUnderstanding(BaseModel):
    business: BusinessInput
    confirmed_facts: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    next_questions: list[str] = Field(default_factory=list)

class MarketResearchInput(BaseModel):
    market: str = Field(min_length=1)
    geography: str = Field(min_length=1)
    customer: str | None = None
    research_questions: list[str] = Field(default_factory=list)
    supplied_sources: list[EvidenceReference] = Field(default_factory=list)

class ResearchBrief(BaseModel):
    market: str
    geography: str
    research_questions: list[str]
    evidence: list[EvidenceReference] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    status: str = "research_required"
    limitations: list[str] = Field(default_factory=list)

class BusinessAnalysisInput(BaseModel):
    business: BusinessInput
    metrics: dict[str, float] = Field(default_factory=dict)
    question: str = "Diagnose the business model and identify priority issues."

class BusinessAnalysis(BaseModel):
    business_name: str
    question: str
    supplied_metrics: dict[str, float]
    deterministic_checks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    recommendations_for_client_reasoning: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)

class DecisionInput(BaseModel):
    decision: str = Field(min_length=1)
    options: list[str] = Field(min_length=2)
    objectives: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risk_tolerance: str = "moderate"

class DecisionAssessment(BaseModel):
    decision: str
    options: list[str]
    evaluation_dimensions: list[str]
    trade_offs_to_assess: list[str]
    missing_information: list[str]
    human_decision_required: bool = True

class ExecutionPlanInput(BaseModel):
    objective: str = Field(min_length=1)
    horizon_days: int = Field(default=30, ge=1, le=365)
    resources: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

class Milestone(BaseModel):
    title: str
    due_day: int = Field(ge=1)
    deliverable: str
    success_measure: str

class ExecutionPlan(BaseModel):
    objective: str
    horizon_days: int
    milestones: list[Milestone]
    assumptions: list[str] = Field(default_factory=list)
    approval_required_for_external_actions: bool = True

class OutcomeReviewInput(BaseModel):
    objective: str
    expected_outcome: str
    actual_outcome: str
    metrics: dict[str, float] = Field(default_factory=dict)
    lessons: list[str] = Field(default_factory=list)

class OutcomeReview(BaseModel):
    objective: str
    expected_outcome: str
    actual_outcome: str
    metric_observations: list[str]
    lessons_to_validate: list[str]
    next_review_questions: list[str]

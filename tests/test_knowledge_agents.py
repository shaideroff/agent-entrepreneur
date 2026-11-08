from agent_entrepreneur.knowledge.registry import KnowledgeRepository
from agent_entrepreneur.agents.orchestrator import plan_specialists
from agent_entrepreneur.security.approvals import approval_required

def test_registry_keeps_founder_methodology_unverified():
    profile = KnowledgeRepository().get_profile("s-haider-built-from-zero")
    assert profile and profile["evidence_level"] == "unverified"

def test_specialist_plan_is_bounded():
    assert len(plan_specialists("launch", ["operations", "scaling"], max_specialists=2)) <= 2

def test_external_action_requires_approval():
    assert approval_required("publish_content").required
    assert not approval_required("prepare_draft").required


def test_seed_profiles_pass_registry_structure_validation():
    repository = KnowledgeRepository()
    for profile in repository.search_profiles():
        assert repository.validate_profile(profile) == []

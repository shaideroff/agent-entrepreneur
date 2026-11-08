from agent_entrepreneur.knowledge.registry import KnowledgeRepository


def test_seed_registry_covers_eight_regions_and_twelve_domain_families():
    profiles = KnowledgeRepository().search_profiles()
    assert len(profiles) >= 18
    assert len({profile["region"] for profile in profiles}) == 8
    assert len({domain for profile in profiles for domain in profile["domains"]}) >= 12


def test_seed_profiles_include_auditable_profile_and_source_metadata():
    for profile in KnowledgeRepository().search_profiles():
        assert profile["ventures"]
        assert isinstance(profile["expertise"], list)
        assert isinstance(profile["methods"], list)
        assert isinstance(profile["decisions"], list)
        assert isinstance(profile["outcomes"], list)
        assert profile["confidence"] in {"high", "medium", "low"}
        assert profile["updated_at"]
        assert profile["sources"]
        for source in profile["sources"]:
            assert source["source_id"]
            assert source["title"]
            assert source["source_type"]
            assert source["accessed_at"]
            assert source["supports"]


def test_profile_validator_rejects_untraceable_source():
    profile = dict(KnowledgeRepository().search_profiles()[1])
    profile["sources"] = [{"title": "No source identifier"}]
    errors = KnowledgeRepository.validate_profile(profile)
    assert any("source" in error for error in errors)


def test_profile_validator_rejects_invalid_confidence_and_region():
    profile = dict(KnowledgeRepository().search_profiles()[1])
    profile["confidence"] = "certain"
    profile["region"] = "Unknown region"
    errors = KnowledgeRepository.validate_profile(profile)
    assert any("confidence" in error for error in errors)
    assert any("region" in error for error in errors)

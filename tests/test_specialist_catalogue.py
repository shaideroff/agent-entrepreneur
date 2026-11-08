from agent_entrepreneur.agents.registry import SPECIALISTS


EXPECTED_SPECIALISTS = {
    "built_from_zero",
    "technology_ai",
    "product_innovation",
    "growth_sales",
    "marketing_brand",
    "capital_allocation",
    "operations_scale",
    "manufacturing_industrial",
    "leadership_organisation",
    "market_expansion",
    "consumer_d2c",
    "investment_fundraising",
}


def test_catalogue_contains_all_twelve_approved_specialist_disciplines():
    assert set(SPECIALISTS) == EXPECTED_SPECIALISTS
    assert len(SPECIALISTS) == 12


def test_every_specialist_has_a_title_methodology_and_domain_taxonomy():
    for specialist_id, profile in SPECIALISTS.items():
        assert profile["title"].strip(), specialist_id
        assert profile["methodology"].strip(), specialist_id
        assert profile["domains"], specialist_id
        assert all(domain.strip() for domain in profile["domains"]), specialist_id

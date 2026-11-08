from agent_entrepreneur.security.approvals import CONSEQUENTIAL_ACTIONS, approval_required


def test_consequential_action_registry_is_immutable() -> None:
    assert isinstance(CONSEQUENTIAL_ACTIONS, frozenset)


def test_every_consequential_action_requires_explicit_approval() -> None:
    for action in CONSEQUENTIAL_ACTIONS:
        request = approval_required(action)
        assert request.required is True
        assert request.scope == "explicit user approval required"


def test_unknown_action_does_not_gain_consequential_privileges() -> None:
    request = approval_required("prepare_local_draft")
    assert request.required is False
    assert request.scope == "non-consequential local preparation"

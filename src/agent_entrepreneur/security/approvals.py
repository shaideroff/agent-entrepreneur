from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    action: str
    scope: str
    required: bool = True
CONSEQUENTIAL_ACTIONS = {"spend_money", "contact_customer", "publish_content", "sign_contract", "submit_application", "change_production_system"}
def approval_required(action: str) -> ApprovalRequest:
    return ApprovalRequest(action, "explicit user approval required") if action in CONSEQUENTIAL_ACTIONS else ApprovalRequest(action, "non-consequential local preparation", False)

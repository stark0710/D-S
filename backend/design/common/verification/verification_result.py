from typing import Any
from backend.design.common.verification.models import RuleStatus, RuleCategory, RuleSeverity

class RuleEvaluationResult:
    def __init__(self, 
                 rule_id: str, 
                 title: str, 
                 category: RuleCategory, 
                 severity: RuleSeverity, 
                 status: RuleStatus, 
                 message: str = "", 
                 recommendation: str = ""):
        self.rule_id = rule_id
        self.title = title
        self.category = category
        self.severity = severity
        self.status = status
        self.message = message
        self.recommendation = recommendation

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "category": self.category.value if isinstance(self.category, RuleCategory) else self.category,
            "severity": self.severity.value if isinstance(self.severity, RuleSeverity) else self.severity,
            "status": self.status.value if isinstance(self.status, RuleStatus) else self.status,
            "message": self.message,
            "recommendation": self.recommendation
        }

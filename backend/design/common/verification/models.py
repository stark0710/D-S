from enum import Enum
from abc import ABC, abstractmethod
from typing import Tuple, Any

class RuleSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class RuleCategory(str, Enum):
    MISSION = "Mission"
    GEOMETRY = "Geometry"
    WING = "Wing"
    FUSELAGE = "Fuselage"
    TAIL = "Tail"
    PROPULSION = "Propulsion"
    ELECTRICAL = "Electrical"
    MASS = "Mass"
    CG = "CG"
    PERFORMANCE = "Performance"
    MANUFACTURING = "Manufacturing"
    SAFETY = "Safety"
    CERTIFICATION = "Certification"

class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class VerificationRule(ABC):
    def __init__(self, rule_id: str, title: str, description: str, category: RuleCategory, severity: RuleSeverity):
        self.rule_id = rule_id
        self.title = title
        self.description = description
        self.category = category
        self.severity = severity

    @abstractmethod
    def evaluate(self, context: Any) -> Tuple[RuleStatus, str, str]:
        """
        Evaluates the rule against the context.
        
        Returns:
            Tuple[RuleStatus, str, str]: (status, failure_message, recommendation)
        """
        pass

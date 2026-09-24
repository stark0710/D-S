"""
RuleEvaluationResult Subsystem

Purpose:
    Defines the `RuleEvaluationResult` dataclass returned by `RuleEvaluator`.

Role in Architecture:
    `RuleEvaluationResult` captures the evaluation output of a single `EngineeringRule` executed against
    a design context dictionary. It records pass/fail status, violation severity, diagnostic message,
    resolved comparison details, and execution timing.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.rules.models.engineering_rule import RuleSeverity


@dataclass(slots=True)
class RuleEvaluationResult:
    """
    Evaluation diagnostic result for a single EngineeringRule invocation.

    Attributes:
        rule_id (str): Unique identifier of the evaluated EngineeringRule.
        passed (bool): True if the rule condition evaluated to True; False if violated.
        severity (RuleSeverity): Severity level of the rule (INFO, WARNING, ERROR, CRITICAL).
        message (str): User-facing diagnostic explanation (populated when passed is False).
        details (dict[str, Any]): Detailed comparison evaluation breakdown (lhs, lhs_val, operator, rhs, rhs_val).
        evaluation_time_ms (float): Evaluation duration in milliseconds.
    """

    rule_id: str
    passed: bool
    severity: RuleSeverity
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    evaluation_time_ms: float = 0.0

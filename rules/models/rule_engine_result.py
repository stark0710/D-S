"""
RuleEngineResult Subsystem

Purpose:
    Defines the `RuleEngineResult` dataclass returned by `RuleEngine`.

Role in Architecture:
    `RuleEngineResult` captures the aggregated output of evaluating multiple `EngineeringRule` objects
    against a design context dictionary. It aggregates individual `RuleEvaluationResult` items, counts
    pass/fail outcomes, breaks down violations by severity (warning, error, critical), determines overall
    compliance (`overall_passed`), and records total evaluation runtime.
"""

from dataclasses import dataclass, field
from typing import Any
from backend.rules.models.rule_evaluation_result import RuleEvaluationResult


@dataclass(slots=True)
class RuleEngineResult:
    """
    Aggregated evaluation report for a batch of engineering rules evaluated by RuleEngine.

    Attributes:
        results (list[RuleEvaluationResult]): List of individual rule evaluation results.
        passed_count (int): Number of rules that passed evaluation.
        failed_count (int): Number of rules that failed evaluation.
        warning_count (int): Number of failed rules with WARNING severity.
        error_count (int): Number of failed rules with ERROR severity.
        critical_count (int): Number of failed rules with CRITICAL severity.
        overall_passed (bool): True if zero rules failed evaluation; False otherwise.
        evaluation_time_ms (float): Total evaluation time in milliseconds for the rule batch.
    """

    results: list[RuleEvaluationResult] = field(default_factory=list)
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    critical_count: int = 0
    overall_passed: bool = True
    evaluation_time_ms: float = 0.0

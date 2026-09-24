"""
RuleEngine Orchestration Subsystem

Purpose:
    Defines the `RuleEngine` class responsible for orchestrating the evaluation of multiple engineering rules
    against a design context dictionary.

Role in Architecture:
    `RuleEngine` serves as the central rule evaluation orchestration layer in Phase 4 (Engineering Rules Platform).
    It receives an injected `RuleRepository` and `RuleEvaluator`, retrieves target rules by category, list of IDs, or
    full repository scope, delegates single-rule evaluations, aggregates pass/fail/severity statistics, and returns a `RuleEngineResult`.
"""

import time
from typing import Any
from backend.rules.models.engineering_rule import EngineeringRule, RuleSeverity
from backend.rules.models.rule_evaluation_result import RuleEvaluationResult
from backend.rules.models.rule_engine_result import RuleEngineResult
from backend.rules.rule_repository import RuleRepository
from backend.rules.rule_evaluator import RuleEvaluator


class RuleEngineError(ValueError):
    """Base exception class for RuleEngine errors."""
    pass


class RuleEngine:
    """
    Central orchestration layer for engineering rule evaluation.

    Workflow:
        1. Retrieve target rules from `RuleRepository`.
        2. Iterate over each `EngineeringRule`.
        3. Delegate single-rule evaluation to `RuleEvaluator`.
        4. Collect `RuleEvaluationResult` objects.
        5. Aggregate pass, fail, warning, error, and critical severity statistics.
        6. Return a comprehensive `RuleEngineResult`.

    Design Principles:
        - Single Responsibility Principle (SRP): Multi-rule evaluation orchestration only.
        - Dependency Injection: Injects `RuleRepository` and `RuleEvaluator`.
        - Clean Architecture: Decoupled from expression parsing, graph traversal, and databases.
    """

    def __init__(self, repository: RuleRepository, evaluator: RuleEvaluator) -> None:
        """
        Initializes the RuleEngine with injected RuleRepository and RuleEvaluator dependencies.

        Args:
            repository (RuleRepository): Injected rule repository instance.
            evaluator (RuleEvaluator): Injected single-rule evaluator instance.
        """
        self._repository: RuleRepository = repository
        self._evaluator: RuleEvaluator = evaluator

    def evaluate_all(self, context: dict[str, Any]) -> RuleEngineResult:
        """
        Evaluates all stored engineering rules in the repository against the provided design context.

        Args:
            context (dict[str, Any]): Dictionary containing design state variables.

        Returns:
            RuleEngineResult: Aggregated evaluation summary and diagnostics.
        """
        rules = self._repository.get_all()
        return self._evaluate_batch(rules, context)

    def evaluate_category(self, category: str, context: dict[str, Any]) -> RuleEngineResult:
        """
        Evaluates all engineering rules belonging to a specified subsystem category.

        Args:
            category (str): Subsystem or domain category string (e.g., 'Electrical', 'Aerodynamics').
            context (dict[str, Any]): Dictionary containing design state variables.

        Returns:
            RuleEngineResult: Aggregated evaluation summary and diagnostics.
        """
        rules = self._repository.get_by_category(category)
        return self._evaluate_batch(rules, context)

    def evaluate_rules(self, rule_ids: list[str], context: dict[str, Any]) -> RuleEngineResult:
        """
        Evaluates a specified list of engineering rules identified by their unique IDs.

        Args:
            rule_ids (list[str]): List of unique rule identifiers to evaluate.
            context (dict[str, Any]): Dictionary containing design state variables.

        Returns:
            RuleEngineResult: Aggregated evaluation summary and diagnostics.

        Raises:
            RuleNotFoundError: If any rule ID in rule_ids is missing from the repository.
        """
        rules = [self._repository.get_rule(rid) for rid in rule_ids]
        return self._evaluate_batch(rules, context)

    def _evaluate_batch(self, rules: list[EngineeringRule], context: dict[str, Any]) -> RuleEngineResult:
        """Helper method that evaluates a list of rules and aggregates summary statistics."""
        start_time = time.perf_counter()

        results: list[RuleEvaluationResult] = []
        passed_count = 0
        failed_count = 0
        warning_count = 0
        error_count = 0
        critical_count = 0

        for rule in rules:
            res = self._evaluator.evaluate(rule, context)
            results.append(res)

            if res.passed:
                passed_count += 1
            else:
                failed_count += 1
                if res.severity == RuleSeverity.WARNING:
                    warning_count += 1
                elif res.severity == RuleSeverity.ERROR:
                    error_count += 1
                elif res.severity == RuleSeverity.CRITICAL:
                    critical_count += 1

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        overall_passed = (failed_count == 0)

        return RuleEngineResult(
            results=results,
            passed_count=passed_count,
            failed_count=failed_count,
            warning_count=warning_count,
            error_count=error_count,
            critical_count=critical_count,
            overall_passed=overall_passed,
            evaluation_time_ms=round(duration_ms, 3)
        )

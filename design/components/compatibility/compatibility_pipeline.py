"""
CompatibilityPipeline Subsystem

Purpose:
    Defines the `CompatibilityPipeline` class responsible for executing compatibility rules and aggregating findings.

Role in Architecture:
    `CompatibilityPipeline` coordinates rule execution, aggregates `CompatibilityIssue` objects, calculates overall status and score,
    and returns a `CompatibilityResult`.
"""

from typing import Any
from backend.design.components.compatibility.compatibility_status import CompatibilityStatus
from backend.design.components.compatibility.compatibility_severity import CompatibilitySeverity
from backend.design.components.compatibility.compatibility_issue import CompatibilityIssue
from backend.design.components.compatibility.compatibility_result import CompatibilityResult
from backend.design.components.compatibility.compatibility_rule import CompatibilityRule


class CompatibilityPipeline:
    """
    Pipeline for executing component compatibility validation rules.

    Design Principles:
        - Pipeline Pattern: Sequential execution of independent rule evaluations.
        - Single Responsibility Principle: Rule execution and diagnostic aggregation only.
    """

    def __init__(self, rules: list[CompatibilityRule] | None = None) -> None:
        """
        Initializes the CompatibilityPipeline.

        Args:
            rules (list[CompatibilityRule] | None): Optional initial list of rules to execute.
        """
        self._rules: list[CompatibilityRule] = list(rules) if rules else []

    def register_rule(self, rule: CompatibilityRule) -> None:
        """Registers a new compatibility rule into the pipeline."""
        self._rules.append(rule)

    def execute(self, components: dict[str, Any]) -> CompatibilityResult:
        """
        Executes all registered rules against the provided component dictionary.

        Args:
            components (dict[str, Any]): Dictionary of components.

        Returns:
            CompatibilityResult: Aggregated compatibility evaluation result.
        """
        all_issues: list[CompatibilityIssue] = []

        for rule in self._rules:
            issues = rule.evaluate(components)
            all_issues.extend(issues)

        critical_issues = [i for i in all_issues if i.severity == CompatibilitySeverity.CRITICAL]
        warning_issues = [i for i in all_issues if i.severity == CompatibilitySeverity.WARNING]
        info_issues = [i for i in all_issues if i.severity == CompatibilitySeverity.INFO]

        if critical_issues:
            status = CompatibilityStatus.INCOMPATIBLE
        elif warning_issues:
            status = CompatibilityStatus.COMPATIBLE_WITH_WARNINGS
        else:
            status = CompatibilityStatus.COMPATIBLE

        score = 1.0 - (len(critical_issues) * 0.50) - (len(warning_issues) * 0.15) - (len(info_issues) * 0.05)
        score = max(0.0, min(1.0, score))

        return CompatibilityResult(
            status=status,
            score=round(score, 2),
            issues=all_issues,
            warnings=warning_issues,
            metadata={"rule_count": len(self._rules)}
        )

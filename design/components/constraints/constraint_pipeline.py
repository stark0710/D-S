"""
ConstraintPipeline Subsystem

Purpose:
    Defines the `ConstraintPipeline` class responsible for executing registered constraint rules and aggregating findings.

Role in Architecture:
    `ConstraintPipeline` coordinates sequential constraint rule evaluations over design data and `DesignContext`,
    categorizes satisfied vs violated constraints, calculates an overall score, and returns a `ConstraintResult`.
"""

from typing import Any
from backend.design.components.constraints.constraint_status import ConstraintStatus
from backend.design.components.constraints.constraint_severity import ConstraintSeverity
from backend.design.components.constraints.constraint_issue import ConstraintIssue
from backend.design.components.constraints.constraint_result import ConstraintResult
from backend.design.components.constraints.constraint_rule import ConstraintRule


class ConstraintPipeline:
    """
    Pipeline for executing aircraft engineering constraint validation rules.

    Design Principles:
        - Pipeline Pattern: Sequential execution of independent rule evaluations.
        - Single Responsibility Principle: Rule execution and result aggregation only.
    """

    def __init__(self, rules: list[ConstraintRule] | None = None) -> None:
        """
        Initializes the ConstraintPipeline.

        Args:
            rules (list[ConstraintRule] | None): Optional initial list of rules to execute.
        """
        self._rules: list[ConstraintRule] = list(rules) if rules else []

    def register_rule(self, rule: ConstraintRule) -> None:
        """Registers a new constraint rule into the pipeline."""
        self._rules.append(rule)

    def execute(
        self,
        design_data: dict[str, Any],
        context: Any | None = None
    ) -> ConstraintResult:
        """
        Executes all registered constraint rules against design data and optional context.

        Args:
            design_data (dict[str, Any]): Aircraft design data dictionary.
            context (Any | None): Optional DesignContext instance.

        Returns:
            ConstraintResult: Aggregated constraint evaluation result.
        """
        all_issues: list[ConstraintIssue] = []
        violated_names: set[str] = set()
        evaluated_names: set[str] = set()

        for rule in self._rules:
            c_name = rule.constraint_name
            evaluated_names.add(c_name)

            issues = rule.evaluate(design_data, context)
            all_issues.extend(issues)

            for issue in issues:
                if issue.severity == ConstraintSeverity.CRITICAL:
                    violated_names.add(c_name)

        satisfied_names = list(evaluated_names - violated_names)
        violated_list = list(violated_names)

        critical_issues = [i for i in all_issues if i.severity == ConstraintSeverity.CRITICAL]
        warning_issues = [i for i in all_issues if i.severity == ConstraintSeverity.WARNING]

        if critical_issues:
            status = ConstraintStatus.VIOLATED
        elif warning_issues:
            status = ConstraintStatus.SATISFIED_WITH_WARNINGS
        else:
            status = ConstraintStatus.SATISFIED

        score = 1.0 - (len(critical_issues) * 0.40) - (len(warning_issues) * 0.10)
        score = max(0.0, min(1.0, score))

        return ConstraintResult(
            status=status,
            overall_score=round(score, 2),
            issues=all_issues,
            warnings=warning_issues,
            satisfied_constraints=satisfied_names,
            violated_constraints=violated_list,
            metadata={"rule_count": len(self._rules)}
        )

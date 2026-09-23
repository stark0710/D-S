"""
ValidationPipeline Subsystem

Purpose:
    Defines the `ValidationPipeline` class responsible for registering and sequentially executing `ValidationRule` objects.

Role in Architecture:
    `ValidationPipeline` acts as the extensible rule execution engine for the Requirement Validation Framework.
    It executes rules sequentially, aggregates identified issues, separates errors from warnings, and produces a `ValidationResult`.
"""

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.validation.validation_severity import ValidationSeverity
from backend.design.common.validation.validation_issue import ValidationIssue
from backend.design.common.validation.validation_result import ValidationResult
from backend.design.common.validation.validation_rule import ValidationRule


class ValidationPipeline:
    """
    Extensible validation rule pipeline.

    Design Principles:
        - Open/Closed Principle: New validation rules can be registered dynamically without modifying pipeline code.
        - Single Responsibility Principle: Pipeline execution and result aggregation only.
    """

    def __init__(self, rules: list[ValidationRule] | None = None) -> None:
        """
        Initializes the ValidationPipeline.

        Args:
            rules (list[ValidationRule] | None): Optional initial list of validation rules to register.
        """
        self._rules: list[ValidationRule] = list(rules) if rules else []

    def register_rule(self, rule: ValidationRule) -> None:
        """
        Registers a new validation rule into the pipeline.

        Args:
            rule (ValidationRule): Validation rule instance to append.
        """
        self._rules.append(rule)

    def execute(self, requirements: RequirementModel) -> ValidationResult:
        """
        Executes all registered validation rules sequentially against the requirement model.

        Args:
            requirements (RequirementModel): Target requirement model to validate.

        Returns:
            ValidationResult: Aggregated validation diagnostic result.
        """
        all_issues: list[ValidationIssue] = []

        for rule in self._rules:
            issues = rule.validate(requirements)
            all_issues.extend(issues)

        errors = [issue for issue in all_issues if issue.severity == ValidationSeverity.ERROR]
        warnings = [issue for issue in all_issues if issue.severity in (ValidationSeverity.WARNING, ValidationSeverity.INFO)]
        is_valid = (len(errors) == 0)

        return ValidationResult(
            is_valid=is_valid,
            issues=all_issues,
            warnings=warnings,
            errors=errors,
            metadata={"rule_count": len(self._rules)}
        )

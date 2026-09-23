"""
RequirementValidator Subsystem

Purpose:
    Defines the `RequirementValidator` class, which serves as the public entry point for validating user design requirements.

Role in Architecture:
    `RequirementValidator` is the primary application service of the Requirement Validation Framework.
    It receives a `RequirementModel`, executes a `ValidationPipeline` containing validation rules,
    and returns a `ValidationResult`. It performs validation only and never modifies the input requirement model.
"""

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.validation.validation_result import ValidationResult
from backend.design.common.validation.validation_pipeline import ValidationPipeline
from backend.design.common.validation.validation_rule import (
    PayloadValidationRule,
    FlightTimeValidationRule,
    RangeValidationRule,
    CruiseSpeedValidationRule,
    BudgetValidationRule,
    TakeoffWeightValidationRule,
    AircraftSelectionRule,
    TakeoffLandingRule,
)


class RequirementValidator:
    """
    Public validation service for user design requirements.

    Design Principles:
        - Single Responsibility Principle: Orchestrates requirement model validation only.
        - Dependency Injection: Injects `ValidationPipeline` collaborator via constructor.
        - Non-Mutating: Never alters or mutates input `RequirementModel` instances.
    """

    def __init__(self, pipeline: ValidationPipeline | None = None) -> None:
        """
        Initializes the RequirementValidator.

        Args:
            pipeline (ValidationPipeline | None): Injected validation pipeline instance.
                                                   If None, initializes a default pipeline with standard rules.
        """
        if pipeline is None:
            pipeline = ValidationPipeline(
                rules=[
                    PayloadValidationRule(),
                    FlightTimeValidationRule(),
                    RangeValidationRule(),
                    CruiseSpeedValidationRule(),
                    BudgetValidationRule(),
                    TakeoffWeightValidationRule(),
                    AircraftSelectionRule(),
                    TakeoffLandingRule(),
                ]
            )
        self._pipeline: ValidationPipeline = pipeline

    def validate(self, requirements: RequirementModel) -> ValidationResult:
        """
        Validates user design requirements against all registered rules.

        Args:
            requirements (RequirementModel): Input requirement model to validate.

        Returns:
            ValidationResult: Aggregated validation diagnostic result.
        """
        return self._pipeline.execute(requirements)

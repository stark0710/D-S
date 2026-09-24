"""
ConstraintEngine Subsystem

Purpose:
    Defines the `ConstraintEngine` class, which serves as the public entry point for evaluating engineering design constraints.

Role in Architecture:
    `ConstraintEngine` receives a `DesignContext` and design data dictionary, executes a `ConstraintPipeline` containing registered rules,
    and returns a `ConstraintResult`. It evaluates constraint satisfaction without modifying the input design or performing optimization.
"""

from typing import Any
from backend.design.components.constraints.constraint_result import ConstraintResult
from backend.design.components.constraints.constraint_registry import ConstraintRegistry
from backend.design.components.constraints.constraint_pipeline import ConstraintPipeline
from backend.design.components.constraints.constraint_rule import (
    PayloadConstraintRule,
    MaximumTakeoffWeightConstraintRule,
    BudgetConstraintRule,
    FlightTimeConstraintRule,
    RangeConstraintRule,
    ThrustToWeightConstraintRule,
)


class ConstraintEngine:
    """
    Public entry point service for aircraft engineering constraint verification.

    Design Principles:
        - Single Responsibility Principle: Design constraint verification only.
        - Dependency Injection: Injects `ConstraintRegistry` and `ConstraintPipeline` collaborators.
    """

    def __init__(
        self,
        registry: ConstraintRegistry | None = None,
        pipeline: ConstraintPipeline | None = None
    ) -> None:
        """
        Initializes the ConstraintEngine.

        Args:
            registry (ConstraintRegistry | None): Injected registry instance. If None, registers default standard rules.
            pipeline (ConstraintPipeline | None): Injected pipeline instance. If None, initializes from registry rules.
        """
        if registry is None:
            registry = ConstraintRegistry()
            registry.register_rule(PayloadConstraintRule())
            registry.register_rule(MaximumTakeoffWeightConstraintRule())
            registry.register_rule(BudgetConstraintRule())
            registry.register_rule(FlightTimeConstraintRule())
            registry.register_rule(RangeConstraintRule())
            registry.register_rule(ThrustToWeightConstraintRule())

        self._registry: ConstraintRegistry = registry
        self._pipeline: ConstraintPipeline = (
            pipeline if pipeline else ConstraintPipeline(rules=registry.registered_rules())
        )

    def evaluate_constraints(
        self,
        context: Any,
        design_data: dict[str, Any] | None = None
    ) -> ConstraintResult:
        """
        Evaluates engineering constraints for a given DesignContext and design data.

        Args:
            context (Any): Input DesignContext instance.
            design_data (dict[str, Any] | None): Optional design data dictionary. Defaults to context.design_data if None.

        Returns:
            ConstraintResult: Aggregated constraint verification result.
        """
        if design_data is None and hasattr(context, "design_data"):
            design_data = context.design_data

        if design_data is None:
            design_data = {}

        return self._pipeline.execute(design_data, context)

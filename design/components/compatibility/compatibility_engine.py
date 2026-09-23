"""
CompatibilityEngine Subsystem

Purpose:
    Defines the `CompatibilityEngine` class, which serves as the public entry point for evaluating component compatibility.

Role in Architecture:
    `CompatibilityEngine` orchestrates compatibility checks across hardware components.
    It receives a dictionary of components, executes a `CompatibilityPipeline` containing registered engineering rules,
    and returns a `CompatibilityResult`. It does not perform optimization or component selection.
"""

from typing import Any
from backend.design.components.compatibility.compatibility_result import CompatibilityResult
from backend.design.components.compatibility.compatibility_registry import CompatibilityRegistry
from backend.design.components.compatibility.compatibility_pipeline import CompatibilityPipeline
from backend.design.components.compatibility.compatibility_rule import (
    MotorESCCompatibilityRule,
    MotorPropellerCompatibilityRule,
    BatteryESCCompatibilityRule,
    BatteryMotorCompatibilityRule,
    FramePropellerCompatibilityRule,
)


class CompatibilityEngine:
    """
    Public entry point service for component compatibility evaluation.

    Design Principles:
        - Single Responsibility Principle: Component set compatibility orchestration only.
        - Dependency Injection: Injects `CompatibilityRegistry` and `CompatibilityPipeline` collaborators.
    """

    def __init__(
        self,
        registry: CompatibilityRegistry | None = None,
        pipeline: CompatibilityPipeline | None = None
    ) -> None:
        """
        Initializes the CompatibilityEngine.

        Args:
            registry (CompatibilityRegistry | None): Injected registry instance. If None, populates default rules.
            pipeline (CompatibilityPipeline | None): Injected pipeline instance. If None, initializes from registry rules.
        """
        if registry is None:
            registry = CompatibilityRegistry()
            registry.register_rule(MotorESCCompatibilityRule())
            registry.register_rule(MotorPropellerCompatibilityRule())
            registry.register_rule(BatteryESCCompatibilityRule())
            registry.register_rule(BatteryMotorCompatibilityRule())
            registry.register_rule(FramePropellerCompatibilityRule())

        self._registry: CompatibilityRegistry = registry
        self._pipeline: CompatibilityPipeline = (
            pipeline if pipeline else CompatibilityPipeline(rules=registry.registered_rules())
        )

    def check_compatibility(self, components: dict[str, Any]) -> CompatibilityResult:
        """
        Evaluates compatibility across the provided component set.

        Args:
            components (dict[str, Any]): Dictionary of components keyed by category/name.

        Returns:
            CompatibilityResult: Aggregated compatibility result.
        """
        return self._pipeline.execute(components)

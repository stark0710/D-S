"""
ScoringEngine Subsystem

Purpose:
    Defines the `ScoringEngine` class, which serves as the public entry point for quantitative engineering scoring.

Role in Architecture:
    `ScoringEngine` receives a `DesignContext` and design data dictionary, executes a `ScoringPipeline` containing registered rules,
    and returns an `EngineeringScore`. It evaluates engineering quality without modifying design parameters or performing optimization.
"""

from typing import Any
from backend.design.components.scoring.engineering_score import EngineeringScore
from backend.design.components.scoring.scoring_registry import ScoringRegistry
from backend.design.components.scoring.scoring_pipeline import ScoringPipeline
from backend.design.components.scoring.scoring_rule import (
    PayloadScoreRule,
    EnduranceScoreRule,
    RangeScoreRule,
    CostScoreRule,
    WeightScoreRule,
    SafetyScoreRule,
)


class ScoringEngine:
    """
    Public entry point service for quantitative engineering design evaluation.

    Design Principles:
        - Single Responsibility Principle: Quantitative engineering scoring orchestration only.
        - Dependency Injection: Injects `ScoringRegistry` and `ScoringPipeline` collaborators.
    """

    def __init__(
        self,
        registry: ScoringRegistry | None = None,
        pipeline: ScoringPipeline | None = None
    ) -> None:
        """
        Initializes the ScoringEngine.

        Args:
            registry (ScoringRegistry | None): Injected registry instance. If None, registers default standard rules.
            pipeline (ScoringPipeline | None): Injected pipeline instance. If None, initializes from registry rules.
        """
        if registry is None:
            registry = ScoringRegistry()
            registry.register_rule(PayloadScoreRule())
            registry.register_rule(EnduranceScoreRule())
            registry.register_rule(RangeScoreRule())
            registry.register_rule(CostScoreRule())
            registry.register_rule(WeightScoreRule())
            registry.register_rule(SafetyScoreRule())

        self._registry: ScoringRegistry = registry
        self._pipeline: ScoringPipeline = (
            pipeline if pipeline else ScoringPipeline(rules=registry.registered_rules())
        )

    def score_design(
        self,
        context: Any,
        design_data: dict[str, Any] | None = None
    ) -> EngineeringScore:
        """
        Evaluates quantitative engineering scores for a given DesignContext and design data.

        Args:
            context (Any): Input DesignContext instance.
            design_data (dict[str, Any] | None): Optional design data dictionary. Defaults to context.design_data if None.

        Returns:
            EngineeringScore: Aggregated quantitative engineering score.
        """
        if design_data is None and hasattr(context, "design_data"):
            design_data = context.design_data

        if design_data is None:
            design_data = {}

        return self._pipeline.execute(design_data, context)

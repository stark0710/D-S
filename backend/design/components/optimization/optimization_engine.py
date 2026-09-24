"""
OptimizationEngine Subsystem

Purpose:
    Defines the `OptimizationEngine` class, which serves as the public entry point for orchestrating engineering design optimization.

Role in Architecture:
    `OptimizationEngine` receives a `DesignContext`, resolves the target strategy from `OptimizationRegistry`,
    executes an `OptimizationPipeline`, stores optimized design data in `context`, advances `current_stage` to `DesignStage.OPTIMIZATION`,
    creates milestone snapshots, and returns the updated `DesignContext`.
"""

from backend.design.common.context.design_context import DesignContext
from backend.design.common.context.design_stage import DesignStage
from backend.design.common.context.design_status import DesignStatus
from backend.design.components.optimization.optimization_candidate import OptimizationCandidate
from backend.design.components.optimization.optimization_result import OptimizationResult
from backend.design.components.optimization.optimization_stop_condition import OptimizationStopCondition
from backend.design.components.optimization.optimization_registry import OptimizationRegistry
from backend.design.components.optimization.optimization_pipeline import OptimizationPipeline
from backend.design.components.optimization.optimization_strategy import (
    GreedyOptimizationStrategy,
    HillClimbingStrategy,
)


class OptimizationEngine:
    """
    Public entry point service for aircraft engineering design optimization.

    Design Principles:
        - Single Responsibility Principle: Optimization orchestration only.
        - Dependency Injection: Injects `OptimizationRegistry` collaborator.
        - Evaluation Enforcement: Delegates variant evaluation strictly to Compatibility, Constraint, and Scoring engines.
    """

    def __init__(
        self,
        registry: OptimizationRegistry | None = None,
        pipeline: OptimizationPipeline | None = None
    ) -> None:
        """
        Initializes the OptimizationEngine.

        Args:
            registry (OptimizationRegistry | None): Injected registry instance. If None, populates default strategies.
            pipeline (OptimizationPipeline | None): Optional injected pipeline instance.
        """
        if registry is None:
            registry = OptimizationRegistry()
            registry.register_strategy(GreedyOptimizationStrategy())
            registry.register_strategy(HillClimbingStrategy())

        self._registry: OptimizationRegistry = registry
        self._default_pipeline: OptimizationPipeline | None = pipeline

    def optimize(
        self,
        context: DesignContext,
        strategy_name: str = "GreedyOptimizationStrategy",
        max_iterations: int = 10
    ) -> DesignContext:
        """
        Executes engineering design optimization on the provided DesignContext.

        Args:
            context (DesignContext): Target design context carrying baseline design data.
            strategy_name (str): Identifier name of the optimization strategy to execute.
            max_iterations (int): Maximum optimization iteration steps.

        Returns:
            DesignContext: Updated design context containing optimized design parameters and updated workflow stage.
        """
        baseline_candidate = OptimizationCandidate(design_context=context, iteration=0)
        strategy = self._registry.get_strategy(strategy_name)
        stop_condition = OptimizationStopCondition(max_iterations=max_iterations)

        pipeline = (
            self._default_pipeline if self._default_pipeline else OptimizationPipeline(
                strategy=strategy,
                stop_condition=stop_condition
            )
        )

        result = pipeline.execute(baseline_candidate)

        if result.best_design:
            # Transfer optimized design data back to context
            context.design_data = result.best_design.design_context.design_data

        # Update stage and snapshot
        context.update_stage(
            stage=DesignStage.OPTIMIZATION,
            status=DesignStatus.IN_PROGRESS,
            snapshot_summary=f"Design optimization completed using {strategy_name}. {result.improvement_summary}"
        )

        return context

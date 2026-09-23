"""
Torq Wings VTOL Phase 7 - Optimization Engine.

Façade manager coordinating VTOL design space explorations, tradeoff evaluations,
authoritative multidisciplinary evaluations, and true Pareto front synthesis.
"""

from typing import Any, Dict, List, Optional

from .optimization_requirements import OptimizationRequirements
from .optimization_profile import OptimizationProfile
from .optimization_constraints import OptimizationConstraints
from .optimization_result import OptimizationResult as LegacyOptimizationResult
from .optimization_registry import OptimizationRegistry
from .optimization_validator import OptimizationValidator

# Phase 7 Multidisciplinary & Pareto Optimization imports
from .optimization_models import (
    DesignCandidate,
    DesignEvaluation,
    OptimizationResult as Phase7OptimizationResult,
)
from .design_variables import DesignVariable, OptimizationVariable
from .objective_model import ObjectiveDefinition
from .constraint_model import ConstraintDefinition


class OptimizationEngine:
    """
    Façade manager coordinating VTOL design space explorations, tradeoff evaluations,
    and authoritative Phase 7 multidisciplinary optimization.
    """

    def __init__(
        self,
        profile: Optional[OptimizationProfile] = None,
        constraints: Optional[OptimizationConstraints] = None,
        evaluator: Optional[Any] = None,
    ):
        self.profile = profile or OptimizationProfile()
        self.constraints = constraints or OptimizationConstraints()
        self._evaluator = evaluator

    @property
    def evaluator(self) -> Any:
        if self._evaluator is None:
            from .design_evaluator import VTOLDesignEvaluator
            self._evaluator = VTOLDesignEvaluator()
        return self._evaluator

    def design(self, requirements: OptimizationRequirements) -> LegacyOptimizationResult:
        """
        Legacy design optimization method (preserved for backward compatibility).
        """
        strategy = OptimizationRegistry.get_strategy(requirements.preferred_optimizer_type)
        result = strategy.optimize_design(requirements, self.profile)

        errors = OptimizationValidator.validate(result, self.constraints)
        if errors:
            result.warnings.extend(errors)

        return result

    def optimize_pareto(
        self,
        candidates: Optional[List[DesignCandidate]] = None,
        active_variables: Optional[List[DesignVariable]] = None,
        objectives: Optional[List[ObjectiveDefinition]] = None,
        constraints: Optional[List[ConstraintDefinition]] = None,
        search_method: str = "CARTESIAN_GRID",
        resolution_per_var: int = 3,
        base_mission_overrides: Optional[Dict[str, Any]] = None,
    ) -> Phase7OptimizationResult:
        """
        Executes Phase 7 authoritative multidisciplinary optimization and extracts
        the true non-dominated Pareto front over feasible designs.
        """
        from .optimization_pipeline import VTOLOptimizationPipeline
        pipeline = VTOLOptimizationPipeline(
            evaluator=self.evaluator,
            variables=active_variables,
            objectives=objectives,
            constraints=constraints,
        )
        return pipeline.run_optimization(
            candidates=candidates,
            active_variables=active_variables,
            objectives=objectives,
            constraints=constraints,
            search_method=search_method,
            resolution_per_var=resolution_per_var,
            base_mission_overrides=base_mission_overrides,
        )

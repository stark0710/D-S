"""
OptimizationEngine Subsystem

Purpose:
    Defines the `OptimizationEngine` class, which serves as the public entry point for multirotor design optimization engineering.

Role in Architecture:
    `OptimizationEngine` receives outputs from previous engineering disciplines (`DroneMissionProfile`, `VerificationResult`,
    `PerformanceResult`, `MassResult`, `FrameResult`, `ElectricalResult`), resolves strategy from `OptimizationRegistry`,
    executes optimization calculations via `OptimizationStrategy`, validates outputs via `OptimizationValidator`,
    and returns an `OptimizationResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.verification.verification_result import VerificationResult
from backend.design.drone.optimization.optimization_constraints import OptimizationConstraints
from backend.design.drone.optimization.optimization_result import OptimizationResult
from backend.design.drone.optimization.optimization_validator import OptimizationValidator
from backend.design.drone.optimization.optimization_registry import OptimizationRegistry
from backend.design.drone.optimization.optimization_strategy import (
    BalancedOptimizationStrategy,
    LongEnduranceOptimizationStrategy,
)


class OptimizationEngine:
    """
    Public entry point service for multirotor design optimization engineering.

    Design Principles:
        - Single Responsibility Principle: Multirotor design optimization evaluation only.
        - Dependency Injection: Injects `OptimizationRegistry` and `OptimizationValidator` collaborators.
    """

    def __init__(
        self,
        registry: OptimizationRegistry | None = None,
        validator: OptimizationValidator | None = None
    ) -> None:
        """Initializes the OptimizationEngine."""
        if registry is None:
            registry = OptimizationRegistry()
            registry.register_strategy(BalancedOptimizationStrategy())
            registry.register_strategy(LongEnduranceOptimizationStrategy())

        self._registry: OptimizationRegistry = registry
        self._validator: OptimizationValidator = validator if validator else OptimizationValidator()

    def optimize_design(
        self,
        mission: DroneMissionProfile,
        verification_result: VerificationResult,
        performance_result: PerformanceResult,
        mass_result: MassResult,
        structure_result: FrameResult,
        electrical_result: ElectricalResult,
        strategy_name: str = "BalancedOptimizationStrategy",
        constraints: OptimizationConstraints | None = None
    ) -> OptimizationResult:
        """
        Optimizes a verified multirotor aircraft design.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            verification_result (VerificationResult): Verification result.
            performance_result (PerformanceResult): Baseline performance result.
            mass_result (MassResult): Baseline mass properties result.
            structure_result (FrameResult): Structural result.
            electrical_result (ElectricalResult): Electrical result.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (OptimizationConstraints | None): Optimization constraints.

        Returns:
            OptimizationResult: Completed design optimization engineering output summary.
        """
        const = constraints if constraints else OptimizationConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        opt_res = strategy.optimize_design(
            mission=mission,
            verification_result=verification_result,
            performance_result=performance_result,
            mass_result=mass_result,
            structure_result=structure_result,
            electrical_result=electrical_result
        )

        warns = self._validator.validate_optimization(opt_res, const)
        if warns:
            opt_res.warnings.extend(warns)

        return opt_res

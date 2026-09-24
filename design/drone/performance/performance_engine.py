"""
PerformanceEngine Subsystem

Purpose:
    Defines the `PerformanceEngine` class, which serves as the public entry point for multirotor flight performance engineering.

Role in Architecture:
    `PerformanceEngine` receives outputs from all previous engineering disciplines (`DroneMissionProfile`, `ConfigurationResult`,
    `FrameResult`, `PropulsionResult`, `ElectricalResult`, `AvionicsResult`, `PayloadResult`, `MassResult`), resolves strategy
    from `PerformanceRegistry`, executes flight performance calculations via `PerformanceStrategy`, validates outputs via `PerformanceValidator`,
    and returns a `PerformanceResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.performance.performance_constraints import PerformanceConstraints
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.performance.performance_validator import PerformanceValidator
from backend.design.drone.performance.performance_registry import PerformanceRegistry
from backend.design.drone.performance.performance_strategy import (
    BalancedStrategy,
    LongEnduranceStrategy,
)


class PerformanceEngine:
    """
    Public entry point service for multirotor flight performance engineering.

    Design Principles:
        - Single Responsibility Principle: Multirotor flight performance evaluation only.
        - Dependency Injection: Injects `PerformanceRegistry` and `PerformanceValidator` collaborators.
    """

    def __init__(
        self,
        registry: PerformanceRegistry | None = None,
        validator: PerformanceValidator | None = None
    ) -> None:
        """Initializes the PerformanceEngine."""
        if registry is None:
            registry = PerformanceRegistry()
            registry.register_strategy(BalancedStrategy())
            registry.register_strategy(LongEnduranceStrategy())

        self._registry: PerformanceRegistry = registry
        self._validator: PerformanceValidator = validator if validator else PerformanceValidator()

    def evaluate_performance(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult,
        strategy_name: str = "BalancedStrategy",
        constraints: PerformanceConstraints | None = None
    ) -> PerformanceResult:
        """
        Evaluates the complete flight performance of the engineered multirotor.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            electrical_result (ElectricalResult): Evaluated electrical result.
            avionics_result (AvionicsResult): Evaluated avionics result.
            payload_result (PayloadResult): Evaluated payload result.
            mass_result (MassResult): Evaluated mass properties result.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (PerformanceConstraints | None): Performance constraints.

        Returns:
            PerformanceResult: Completed flight performance engineering output summary.
        """
        const = constraints if constraints else PerformanceConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        perf_res = strategy.calculate_performance(
            mission=mission,
            configuration_result=configuration_result,
            structure_result=structure_result,
            propulsion_result=propulsion_result,
            electrical_result=electrical_result,
            avionics_result=avionics_result,
            payload_result=payload_result,
            mass_result=mass_result
        )

        warns = self._validator.validate_performance(perf_res, const)
        if warns:
            perf_res.warnings.extend(warns)

        return perf_res

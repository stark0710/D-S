"""
AvionicsEngine Subsystem

Purpose:
    Defines the `AvionicsEngine` class, which serves as the public entry point for multirotor avionics subsystem engineering design.

Role in Architecture:
    `AvionicsEngine` receives `DroneMissionProfile`, `ConfigurationResult`, `FrameResult`, `PropulsionResult`, and `ElectricalResult`,
    resolves strategy from `AvionicsRegistry`, executes avionics calculations via `AvionicsStrategy`, validates outputs via `AvionicsValidator`,
    and returns an `AvionicsResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_constraints import AvionicsConstraints
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.avionics.avionics_validator import AvionicsValidator
from backend.design.drone.avionics.avionics_registry import AvionicsRegistry
from backend.design.drone.avionics.avionics_strategy import (
    BalancedStrategy,
    MappingStrategy,
    AutonomousStrategy,
)


class AvionicsEngine:
    """
    Public entry point service for multirotor avionics subsystem engineering design.

    Design Principles:
        - Single Responsibility Principle: Multirotor avionics architecture engineering only.
        - Dependency Injection: Injects `AvionicsRegistry` and `AvionicsValidator` collaborators.
    """

    def __init__(
        self,
        registry: AvionicsRegistry | None = None,
        validator: AvionicsValidator | None = None
    ) -> None:
        """
        Initializes the AvionicsEngine.

        Args:
            registry (AvionicsRegistry | None): Injected strategy registry.
            validator (AvionicsValidator | None): Injected avionics validator.
        """
        if registry is None:
            registry = AvionicsRegistry()
            registry.register_strategy(BalancedStrategy())
            registry.register_strategy(MappingStrategy())
            registry.register_strategy(AutonomousStrategy())

        self._registry: AvionicsRegistry = registry
        self._validator: AvionicsValidator = validator if validator else AvionicsValidator()

    def design_avionics(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        strategy_name: str = "BalancedStrategy",
        constraints: AvionicsConstraints | None = None
    ) -> AvionicsResult:
        """
        Designs the multirotor avionics subsystem architecture.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            electrical_result (ElectricalResult): Evaluated electrical result.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (AvionicsConstraints | None): Avionics constraints.

        Returns:
            AvionicsResult: Completed avionics engineering output summary.
        """
        const = constraints if constraints else AvionicsConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        avionics_res = strategy.calculate_avionics(
            mission=mission,
            configuration_result=configuration_result,
            structure_result=structure_result,
            propulsion_result=propulsion_result,
            electrical_result=electrical_result
        )

        warns = self._validator.validate_avionics(avionics_res, const)
        if warns:
            avionics_res.warnings.extend(warns)

        return avionics_res

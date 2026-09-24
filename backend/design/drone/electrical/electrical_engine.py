"""
ElectricalEngine Subsystem

Purpose:
    Defines the `ElectricalEngine` class, which serves as the public entry point for multirotor electrical power subsystem engineering design.

Role in Architecture:
    `ElectricalEngine` receives `DroneMissionProfile`, `ConfigurationResult`, `FrameResult`, and `PropulsionResult`, resolves strategy from `ElectricalRegistry`,
    executes electrical calculations via `ElectricalStrategy`, validates outputs via `ElectricalValidator`, and returns an `ElectricalResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_constraints import ElectricalConstraints
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.electrical.electrical_validator import ElectricalValidator
from backend.design.drone.electrical.electrical_registry import ElectricalRegistry
from backend.design.drone.electrical.electrical_strategy import (
    BalancedStrategy,
    LongEnduranceStrategy,
)


class ElectricalEngine:
    """
    Public entry point service for multirotor electrical power subsystem engineering design.

    Design Principles:
        - Single Responsibility Principle: Multirotor electrical power subsystem engineering only.
        - Dependency Injection: Injects `ElectricalRegistry` and `ElectricalValidator` collaborators.
    """

    def __init__(
        self,
        registry: ElectricalRegistry | None = None,
        validator: ElectricalValidator | None = None
    ) -> None:
        """
        Initializes the ElectricalEngine.

        Args:
            registry (ElectricalRegistry | None): Injected strategy registry.
            validator (ElectricalValidator | None): Injected electrical validator.
        """
        if registry is None:
            registry = ElectricalRegistry()
            registry.register_strategy(BalancedStrategy())
            registry.register_strategy(LongEnduranceStrategy())

        self._registry: ElectricalRegistry = registry
        self._validator: ElectricalValidator = validator if validator else ElectricalValidator()

    def design_electrical(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        strategy_name: str = "BalancedStrategy",
        constraints: ElectricalConstraints | None = None
    ) -> ElectricalResult:
        """
        Designs the multirotor electrical power subsystem.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (ElectricalConstraints | None): Electrical constraints.

        Returns:
            ElectricalResult: Completed electrical engineering output summary.
        """
        const = constraints if constraints else ElectricalConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        electrical_res = strategy.calculate_electrical(
            mission=mission,
            configuration_result=configuration_result,
            structure_result=structure_result,
            propulsion_result=propulsion_result
        )

        warns = self._validator.validate_electrical(electrical_res, const)
        if warns:
            electrical_res.warnings.extend(warns)

        return electrical_res

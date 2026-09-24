"""
PropulsionEngine Subsystem

Purpose:
    Defines the `PropulsionEngine` class, which serves as the public entry point for multirotor propulsion subsystem engineering design.

Role in Architecture:
    `PropulsionEngine` receives `DroneMissionProfile`, `ConfigurationResult`, and `FrameResult`, resolves strategy from `PropulsionRegistry`,
    executes propulsion calculations via `PropulsionStrategy`, validates outputs via `PropulsionValidator`, and returns a `PropulsionResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_constraints import PropulsionConstraints
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.propulsion.propulsion_validator import PropulsionValidator
from backend.design.drone.propulsion.propulsion_registry import PropulsionRegistry
from backend.design.drone.propulsion.propulsion_strategy import (
    BalancedStrategy,
    LongEnduranceStrategy,
    HeavyLiftStrategy,
)


class PropulsionEngine:
    """
    Public entry point service for multirotor propulsion subsystem engineering design.

    Design Principles:
        - Single Responsibility Principle: Multirotor propulsion subsystem engineering only.
        - Dependency Injection: Injects `PropulsionRegistry` and `PropulsionValidator` collaborators.
        - Non-Calculation: Does not select batteries or ESCs.
    """

    def __init__(
        self,
        registry: PropulsionRegistry | None = None,
        validator: PropulsionValidator | None = None
    ) -> None:
        """
        Initializes the PropulsionEngine.

        Args:
            registry (PropulsionRegistry | None): Injected strategy registry.
            validator (PropulsionValidator | None): Injected propulsion validator.
        """
        if registry is None:
            registry = PropulsionRegistry()
            registry.register_strategy(BalancedStrategy())
            registry.register_strategy(LongEnduranceStrategy())
            registry.register_strategy(HeavyLiftStrategy())

        self._registry: PropulsionRegistry = registry
        self._validator: PropulsionValidator = validator if validator else PropulsionValidator()

    def design_propulsion(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        strategy_name: str = "BalancedStrategy",
        constraints: PropulsionConstraints | None = None
    ) -> PropulsionResult:
        """
        Designs the multirotor propulsion subsystem.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (PropulsionConstraints | None): Propulsion constraints.

        Returns:
            PropulsionResult: Completed propulsion engineering output summary.
        """
        const = constraints if constraints else PropulsionConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        propulsion_res = strategy.calculate_propulsion(
            mission=mission,
            configuration_result=configuration_result,
            structure_result=structure_result
        )

        warns = self._validator.validate_propulsion(propulsion_res, const)
        if warns:
            propulsion_res.warnings.extend(warns)

        return propulsion_res

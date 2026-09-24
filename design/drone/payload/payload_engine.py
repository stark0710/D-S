"""
PayloadEngine Subsystem

Purpose:
    Defines the `PayloadEngine` class, which serves as the public entry point for multirotor payload integration engineering design.

Role in Architecture:
    `PayloadEngine` receives `DroneMissionProfile`, `ConfigurationResult`, `FrameResult`, `PropulsionResult`, `ElectricalResult`, and `AvionicsResult`,
    resolves strategy from `PayloadRegistry`, executes payload integration calculations via `PayloadStrategy`, validates outputs via `PayloadValidator`,
    and returns a `PayloadResult`.
"""

from typing import Any
from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_constraints import PayloadConstraints
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.payload.payload_validator import PayloadValidator
from backend.design.drone.payload.payload_registry import PayloadRegistry
from backend.design.drone.payload.payload_strategy import (
    BalancedStrategy,
    MappingPayloadStrategy,
)


class PayloadEngine:
    """
    Public entry point service for multirotor payload integration engineering design.

    Design Principles:
        - Single Responsibility Principle: Multirotor payload integration engineering only.
        - Dependency Injection: Injects `PayloadRegistry` and `PayloadValidator` collaborators.
    """

    def __init__(
        self,
        registry: PayloadRegistry | None = None,
        validator: PayloadValidator | None = None
    ) -> None:
        """
        Initializes the PayloadEngine.

        Args:
            registry (PayloadRegistry | None): Injected strategy registry.
            validator (PayloadValidator | None): Injected payload validator.
        """
        if registry is None:
            registry = PayloadRegistry()
            registry.register_strategy(BalancedStrategy())
            registry.register_strategy(MappingPayloadStrategy())

        self._registry: PayloadRegistry = registry
        self._validator: PayloadValidator = validator if validator else PayloadValidator()

    def integrate_payload(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        strategy_name: str = "BalancedStrategy",
        constraints: PayloadConstraints | None = None,
        custom_payload_spec: dict[str, Any] | None = None
    ) -> PayloadResult:
        """
        Integrates the multirotor mission payload.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            electrical_result (ElectricalResult): Evaluated electrical result.
            avionics_result (AvionicsResult): Evaluated avionics result.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (PayloadConstraints | None): Payload constraints.
            custom_payload_spec (dict[str, Any] | None): Optional custom payload specification.

        Returns:
            PayloadResult: Completed payload integration engineering output summary.
        """
        const = constraints if constraints else PayloadConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        payload_res = strategy.calculate_payload(
            mission=mission,
            configuration_result=configuration_result,
            structure_result=structure_result,
            propulsion_result=propulsion_result,
            electrical_result=electrical_result,
            avionics_result=avionics_result
        )

        warns = self._validator.validate_payload(payload_res, const)
        if warns:
            payload_res.warnings.extend(warns)

        return payload_res

"""
VerificationEngine Subsystem

Purpose:
    Defines the `VerificationEngine` class, which serves as the public entry point for multirotor mission verification engineering.

Role in Architecture:
    `VerificationEngine` receives all engineered subsystem outputs (`DroneMissionProfile`, `ConfigurationResult`, `FrameResult`,
    `PropulsionResult`, `ElectricalResult`, `AvionicsResult`, `PayloadResult`, `MassResult`, `PerformanceResult`), resolves strategy
    from `VerificationRegistry`, executes verification calculations via `VerificationStrategy`, validates outputs via `VerificationValidator`,
    and returns a `VerificationResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.propulsion.propulsion_result import PropulsionResult
from backend.design.drone.electrical.electrical_result import ElectricalResult
from backend.design.drone.avionics.avionics_result import AvionicsResult
from backend.design.drone.payload.payload_result import PayloadResult
from backend.design.drone.mass_properties.mass_result import MassResult
from backend.design.drone.performance.performance_result import PerformanceResult
from backend.design.drone.verification.verification_constraints import VerificationConstraints
from backend.design.drone.verification.verification_result import VerificationResult
from backend.design.drone.verification.verification_validator import VerificationValidator
from backend.design.drone.verification.verification_registry import VerificationRegistry
from backend.design.drone.verification.verification_strategy import (
    BalancedVerificationStrategy,
    DeliveryVerificationStrategy,
)


class VerificationEngine:
    """
    Public entry point service for multirotor mission verification engineering.

    Design Principles:
        - Single Responsibility Principle: Multirotor aircraft mission verification evaluation only.
        - Dependency Injection: Injects `VerificationRegistry` and `VerificationValidator` collaborators.
    """

    def __init__(
        self,
        registry: VerificationRegistry | None = None,
        validator: VerificationValidator | None = None
    ) -> None:
        """Initializes the VerificationEngine."""
        if registry is None:
            registry = VerificationRegistry()
            registry.register_strategy(BalancedVerificationStrategy())
            registry.register_strategy(DeliveryVerificationStrategy())

        self._registry: VerificationRegistry = registry
        self._validator: VerificationValidator = validator if validator else VerificationValidator()

    def verify_mission(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        structure_result: FrameResult,
        propulsion_result: PropulsionResult,
        electrical_result: ElectricalResult,
        avionics_result: AvionicsResult,
        payload_result: PayloadResult,
        mass_result: MassResult,
        performance_result: PerformanceResult,
        strategy_name: str = "BalancedVerificationStrategy",
        constraints: VerificationConstraints | None = None
    ) -> VerificationResult:
        """
        Verifies whether the fully engineered multirotor aircraft satisfies every mission requirement.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            structure_result (FrameResult): Evaluated structural frame result.
            propulsion_result (PropulsionResult): Evaluated propulsion result.
            electrical_result (ElectricalResult): Evaluated electrical result.
            avionics_result (AvionicsResult): Evaluated avionics result.
            payload_result (PayloadResult): Evaluated payload result.
            mass_result (MassResult): Evaluated mass properties result.
            performance_result (PerformanceResult): Evaluated performance result.
            strategy_name (str): Identifier name of the strategy to execute.
            constraints (VerificationConstraints | None): Verification constraints.

        Returns:
            VerificationResult: Completed mission verification engineering output summary.
        """
        const = constraints if constraints else VerificationConstraints()
        strategy = self._registry.get_strategy(strategy_name)

        verif_res = strategy.verify_mission(
            mission=mission,
            configuration_result=configuration_result,
            structure_result=structure_result,
            propulsion_result=propulsion_result,
            electrical_result=electrical_result,
            avionics_result=avionics_result,
            payload_result=payload_result,
            mass_result=mass_result,
            performance_result=performance_result
        )

        warns = self._validator.validate_verification(verif_res, const)
        if warns:
            verif_res.warnings.extend(warns)

        return verif_res

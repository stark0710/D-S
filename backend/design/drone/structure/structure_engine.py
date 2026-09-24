"""
StructureEngine Subsystem

Purpose:
    Defines the `StructureEngine` class, which serves as the public entry point for multirotor structural airframe design.

Role in Architecture:
    `StructureEngine` receives a `DroneMissionProfile` and `ConfigurationResult`, resolves strategy via `FrameSelector` and `FrameRegistry`,
    executes structural sizing calculations via `FrameStrategy`, validates structural bounds via `FrameValidator`, and returns a `FrameResult`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult
from backend.design.drone.structure.frame_constraints import FrameConstraints
from backend.design.drone.structure.frame_result import FrameResult
from backend.design.drone.structure.frame_validator import FrameValidator
from backend.design.drone.structure.frame_registry import FrameRegistry
from backend.design.drone.structure.frame_selector import FrameSelector
from backend.design.drone.structure.frame_strategy import (
    BalancedFrameStrategy,
    LightweightFrameStrategy,
    HeavyLiftFrameStrategy,
)


class StructureEngine:
    """
    Public entry point service for multirotor structural airframe engineering design.

    Design Principles:
        - Single Responsibility Principle: Multirotor physical airframe structural design only.
        - Dependency Injection: Injects `FrameRegistry`, `FrameValidator`, and `FrameSelector` collaborators.
        - Non-Calculation: Does not select motors, batteries, ESCs, or flight controllers.
    """

    def __init__(
        self,
        registry: FrameRegistry | None = None,
        validator: FrameValidator | None = None,
        selector: FrameSelector | None = None
    ) -> None:
        """
        Initializes the StructureEngine.

        Args:
            registry (FrameRegistry | None): Injected frame strategy registry.
            validator (FrameValidator | None): Injected frame validator.
            selector (FrameSelector | None): Injected frame strategy selector.
        """
        if registry is None:
            registry = FrameRegistry()
            registry.register_strategy(BalancedFrameStrategy())
            registry.register_strategy(LightweightFrameStrategy())
            registry.register_strategy(HeavyLiftFrameStrategy())

        self._registry: FrameRegistry = registry
        self._validator: FrameValidator = validator if validator else FrameValidator()
        self._selector: FrameSelector = selector if selector else FrameSelector()

    def design_structure(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult,
        strategy_name: str | None = None,
        constraints: FrameConstraints | None = None
    ) -> FrameResult:
        """
        Designs the physical multirotor airframe structure.

        Args:
            mission (DroneMissionProfile): Input mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.
            strategy_name (str | None): Optional explicit frame strategy name override.
            constraints (FrameConstraints | None): Frame design constraints.

        Returns:
            FrameResult: Completed structural frame engineering output summary.
        """
        const = constraints if constraints else FrameConstraints()

        if strategy_name is None:
            strategy_name = self._selector.select_frame_strategy(mission, configuration_result)

        strategy = self._registry.get_strategy(strategy_name)

        recommended_cfg = configuration_result.recommended_configuration.profile
        config_type = recommended_cfg.config_type
        rotor_count = recommended_cfg.rotor_count
        coaxial = recommended_cfg.coaxial

        estimated_auw_kg = round(max(0.1, mission.payload_weight_kg) * 3.3, 2)

        frame_res = strategy.calculate_structure(
            mission=mission,
            config_type=config_type,
            rotor_count=rotor_count,
            coaxial=coaxial,
            estimated_auw_kg=estimated_auw_kg
        )

        warns = self._validator.validate_frame(frame_res, const)
        if warns:
            frame_res.warnings.extend(warns)

        return frame_res

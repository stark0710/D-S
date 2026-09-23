"""
FrameSelector Subsystem

Purpose:
    Defines the `FrameSelector` class responsible for selecting the optimal structural design strategy based on mission and configuration inputs.

Role in Architecture:
    `FrameSelector` evaluates mission payload mass, flight endurance targets, and configuration parameters to pick the appropriate `FrameStrategy`.
"""

from backend.design.drone.mission.drone_mission_profile import DroneMissionProfile
from backend.design.drone.configuration.configuration_result import ConfigurationResult


class FrameSelector:
    """
    Selector service for picking the optimal FrameStrategy.

    Design Principles:
        - Single Responsibility Principle: Frame strategy selection logic only.
    """

    def select_frame_strategy(
        self,
        mission: DroneMissionProfile,
        configuration_result: ConfigurationResult
    ) -> str:
        """
        Selects target FrameStrategy name.

        Args:
            mission (DroneMissionProfile): Mission profile.
            configuration_result (ConfigurationResult): Evaluated configuration result.

        Returns:
            str: Identifier name of the recommended FrameStrategy.
        """
        if mission.payload_weight_kg >= 8.0:
            return "HeavyLiftFrameStrategy"
        elif mission.payload_weight_kg <= 1.0 and (mission.target_hover_time_min + mission.target_cruise_time_min) >= 30.0:
            return "LightweightFrameStrategy"
        return "BalancedFrameStrategy"

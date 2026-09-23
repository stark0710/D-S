"""
VTOL Flight Mode Configuration Subsystem

Purpose:
    Defines the `FlightMode` and `FlightModeConfiguration` dataclasses
    configuring target attitude controls and speeds across the VTOL flight profile.
"""

from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass(slots=True)
class FlightMode:
    """
    Control allocation and aerodynamic configuration parameters for an operational mode.

    Attributes:
        name (str): The name of the flight mode.
        is_active (bool): Whether the flight mode is utilized in this architecture.
        thrust_allocation (str): Description of active thrust group (e.g. Lift, Cruise, Tilt).
        attitude_control (str): Actuator group driving pitch/roll/yaw controls.
        target_speed_range_kmh (Tuple[float, float]): Operating airspeeds.
        description (str): Functional purpose of the mode.
    """

    name: str
    is_active: bool
    thrust_allocation: str
    attitude_control: str
    target_speed_range_kmh: Tuple[float, float]
    description: str


@dataclass(slots=True)
class FlightModeConfiguration:
    """
    Consolidated configuration map of the 8 required VTOL flight modes.
    """

    hover: FlightMode
    takeoff: FlightMode
    landing: FlightMode
    transition_to_cruise: FlightMode
    cruise: FlightMode
    transition_to_hover: FlightMode
    emergency: FlightMode
    recovery: FlightMode

    def get_all_modes(self) -> List[FlightMode]:
        """Returns list of all configured flight modes."""
        return [
            self.hover,
            self.takeoff,
            self.landing,
            self.transition_to_cruise,
            self.cruise,
            self.transition_to_hover,
            self.emergency,
            self.recovery,
        ]

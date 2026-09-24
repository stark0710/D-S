"""
VTOL Mission Transition Requirements Subsystem

Purpose:
    Defines the `TransitionRequirements` dataclass capturing parameters specific to the transition phase.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TransitionRequirements:
    """
    Requirements specific to the VTOL hover-to-cruise transition flight regime.

    Attributes:
        transition_speed_kmh (float): Airspeed at which the transition to forward flight is completed in km/h.
        transition_duration_s (float): Estimated duration of the transition phase in seconds.
        transition_altitude_m (float): Altitude at which the transition phase occurs in meters above sea level.
        max_transition_pitch_deg (float): Maximum allowable pitch angle during transition in degrees.
        metadata (Dict[str, Any]): Additional unstructured parameters or settings.
    """

    transition_speed_kmh: float
    transition_duration_s: float
    transition_altitude_m: float
    max_transition_pitch_deg: float
    metadata: Dict[str, Any] = field(default_factory=dict)

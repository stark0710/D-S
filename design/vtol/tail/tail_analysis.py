"""
VTOL Tail Stability and Control Analysis Subsystem

Purpose:
    Defines the `TailStabilityAnalysis` and `TailControlAnalysis` classes
    summarizing stability margins and control authority.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class TailStabilityAnalysis:
    """
    Longitudinal and directional stability parameters.

    Attributes:
        longitudinal_stability_score (float): Horizontal tail stability rating (0 to 100).
        directional_stability_score (float): Vertical tail stability rating (0 to 100).
        static_margin_percent (float): Sized static margin percentage of MAC.
        neutral_point_percent (float): Sized aircraft neutral point as % of MAC.
        trim_capability_deg (float): Tail angle deflection required to trim in cruise.
        metadata (Dict[str, Any]): Additional pitching moment details.
    """

    longitudinal_stability_score: float
    directional_stability_score: float
    static_margin_percent: float
    neutral_point_percent: float
    trim_capability_deg: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TailControlAnalysis:
    """
    Evaluates dynamic control power of elevator and rudder flaps.

    Attributes:
        pitch_effectiveness (float): elevator pitching control power.
        yaw_effectiveness (float): Rudder yawing control power.
        transition_authority (float): Evaluation of control authority during wing stall transition.
        rotor_downwash_interference_index (float): Dynamic pressure loss index from hover rotor wake.
        slipstream_influence_factor (float): Dynamic pressure scaling factor from tractor propellers.
        hover_mode_control_authority (float): Assessment of tail-driven authority in zero-speed hover.
        metadata (Dict[str, Any]): Servo speed and travel limits.
    """

    pitch_effectiveness: float
    yaw_effectiveness: float
    transition_authority: float
    rotor_downwash_interference_index: float
    slipstream_influence_factor: float
    hover_mode_control_authority: float
    metadata: Dict[str, Any] = field(default_factory=dict)

"""
VTOL Mission State & Flight Phase Representation.

Purpose:
    Defines the structural representation of the 10 sequential VTOL flight phases.
    Captures durations, target speeds, altitudes, propulsion modes, and placeholders
    for energy and power across all mission segments.

Role in Architecture:
    `VTOLMissionProfileSequence` provides a typed, authoritative representation
    of the mission profile from ground preflight through vertical ascent, transition,
    fixed-wing cruise, recovery transition, and touchdown.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class VTOLMissionPhase(str, Enum):
    """Authoritative enumeration of the 10 structural VTOL flight phases."""

    GROUND_PREFLIGHT = "GROUND_PREFLIGHT"
    VTOL_TAKEOFF = "VTOL_TAKEOFF"
    HOVER_CLIMB = "HOVER_CLIMB"
    TRANSITION_TO_CRUISE = "TRANSITION_TO_CRUISE"
    FIXED_WING_CRUISE = "FIXED_WING_CRUISE"
    MISSION_LOITER = "MISSION_LOITER"
    TRANSITION_TO_VTOL = "TRANSITION_TO_VTOL"
    HOVER_DESCENT = "HOVER_DESCENT"
    VTOL_LANDING = "VTOL_LANDING"
    GROUND_POSTFLIGHT = "GROUND_POSTFLIGHT"


@dataclass(slots=True)
class VTOLMissionSegment:
    """
    Structural representation of an individual VTOL mission segment.

    Attributes:
        phase (VTOLMissionPhase): Structural phase identifier.
        duration_s (float): Duration of this segment in seconds.
        target_airspeed_kmh (float): Nominal airspeed in km/h.
        target_altitude_m (float): Target altitude above ground/sea level in meters.
        propulsion_mode (str): Active propulsion mode ('LIFT_ONLY', 'BLENDED', 'CRUISE_ONLY', 'OFF').
        power_demand_placeholder_w (float | None): Power demand placeholder (to be sized by later phases).
        energy_demand_placeholder_kwh (float | None): Segment energy placeholder.
        metadata (Dict[str, Any]): Additional operational metadata.
    """

    phase: VTOLMissionPhase
    duration_s: float
    target_airspeed_kmh: float
    target_altitude_m: float
    propulsion_mode: str
    power_demand_placeholder_w: Optional[float] = None
    energy_demand_placeholder_kwh: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VTOLMissionProfileSequence:
    """
    Structural sequence of the complete 10-phase VTOL mission profile.
    """

    segments: List[VTOLMissionSegment] = field(default_factory=list)

    @property
    def total_duration_s(self) -> float:
        """Total mission profile duration in seconds."""
        return sum(s.duration_s for s in self.segments)

    @property
    def total_duration_min(self) -> float:
        """Total mission profile duration in minutes."""
        return self.total_duration_s / 60.0

    def get_segment(self, phase: VTOLMissionPhase) -> Optional[VTOLMissionSegment]:
        """Retrieves the first segment matching the requested flight phase."""
        for s in self.segments:
            if s.phase == phase:
                return s
        return None

    def validate_sequence(self) -> bool:
        """Verifies that all 10 standard phases are represented in sequential order."""
        expected_phases = list(VTOLMissionPhase)
        if len(self.segments) != len(expected_phases):
            return False
        return all(s.phase == expected for s, expected in zip(self.segments, expected_phases))

    @classmethod
    def build_default_sequence(
        cls,
        hover_duration_min: float = 5.0,
        transition_duration_s: float = 15.0,
        cruise_endurance_min: float = 30.0,
        cruise_speed_kmh: float = 90.0,
        transition_speed_kmh: float = 65.0,
        hover_altitude_m: float = 100.0,
        cruise_altitude_m: float = 150.0,
    ) -> "VTOLMissionProfileSequence":
        """
        Constructs the standard 10-phase VTOL mission profile sequence from input parameters.
        """
        # Split hover duration between climbout and descent
        takeoff_hover_s = max(30.0, (hover_duration_min * 60.0) * 0.5)
        landing_hover_s = max(30.0, (hover_duration_min * 60.0) * 0.5)

        # Split cruise time between outbound cruise and loiter/survey sweep
        cruise_s = max(60.0, (cruise_endurance_min * 60.0) * 0.7)
        loiter_s = max(30.0, (cruise_endurance_min * 60.0) * 0.3)

        segments = [
            VTOLMissionSegment(
                phase=VTOLMissionPhase.GROUND_PREFLIGHT,
                duration_s=60.0,
                target_airspeed_kmh=0.0,
                target_altitude_m=0.0,
                propulsion_mode="OFF",
                metadata={"description": "System health check, GPS lock, and IMU calibration"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.VTOL_TAKEOFF,
                duration_s=15.0,
                target_airspeed_kmh=0.0,
                target_altitude_m=10.0,
                propulsion_mode="LIFT_ONLY",
                metadata={"description": "Vertical liftoff and ground effect clearance"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.HOVER_CLIMB,
                duration_s=round(takeoff_hover_s, 1),
                target_airspeed_kmh=15.0,
                target_altitude_m=hover_altitude_m,
                propulsion_mode="LIFT_ONLY",
                metadata={"description": "Vertical climbout to transition altitude"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.TRANSITION_TO_CRUISE,
                duration_s=round(transition_duration_s, 1),
                target_airspeed_kmh=transition_speed_kmh,
                target_altitude_m=hover_altitude_m + 20.0,
                propulsion_mode="BLENDED",
                metadata={"description": "Forward acceleration and wing lift handover"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.FIXED_WING_CRUISE,
                duration_s=round(cruise_s, 1),
                target_airspeed_kmh=cruise_speed_kmh,
                target_altitude_m=cruise_altitude_m,
                propulsion_mode="CRUISE_ONLY",
                metadata={"description": "Efficient wing-borne horizontal cruise"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.MISSION_LOITER,
                duration_s=round(loiter_s, 1),
                target_airspeed_kmh=cruise_speed_kmh * 0.9,
                target_altitude_m=cruise_altitude_m,
                propulsion_mode="CRUISE_ONLY",
                metadata={"description": "On-station payload observation or grid coverage"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.TRANSITION_TO_VTOL,
                duration_s=round(transition_duration_s, 1),
                target_airspeed_kmh=transition_speed_kmh * 0.7,
                target_altitude_m=hover_altitude_m + 10.0,
                propulsion_mode="BLENDED",
                metadata={"description": "Deceleration, wing stall handover to vertical rotors"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.HOVER_DESCENT,
                duration_s=round(landing_hover_s, 1),
                target_airspeed_kmh=10.0,
                target_altitude_m=10.0,
                propulsion_mode="LIFT_ONLY",
                metadata={"description": "Vertical descent over recovery landing pad"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.VTOL_LANDING,
                duration_s=15.0,
                target_airspeed_kmh=0.0,
                target_altitude_m=0.0,
                propulsion_mode="LIFT_ONLY",
                metadata={"description": "Touchdown and motor spin-down"},
            ),
            VTOLMissionSegment(
                phase=VTOLMissionPhase.GROUND_POSTFLIGHT,
                duration_s=30.0,
                target_airspeed_kmh=0.0,
                target_altitude_m=0.0,
                propulsion_mode="OFF",
                metadata={"description": "Data logging and secure disarm"},
            ),
        ]

        return cls(segments=segments)

"""
VTOL Phase 10 Servo Configuration and V-Tail Mixing Engine.

Purpose:
    Implements mathematical mixing models and parameter configurations for
    the inverted V-tail ruddervator empennage and outboard ailerons.
    Separates the mathematical mixing equations from physical servo horn orientation,
    enforcing MIXING_MODEL_DEFINED and PHYSICAL_DIRECTION_UNVERIFIED statuses.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .flight_control_models import (
    FlightControlStatus,
    ServoOutputAssignment,
    VTailMixerConfiguration,
)


class ServoConfigurationEngine:
    """
    Authoritative configuration for aerodynamic control surfaces and V-tail mixing.
    """

    @classmethod
    def get_vtail_mixer_model(cls) -> VTailMixerConfiguration:
        """
        Builds the inverted V-tail mathematical mixing model (Prompt Section 15).
        """
        return VTailMixerConfiguration(
            aircraft_tail_configuration="INVERTED_V_TAIL",
            left_surface_equation="LeftSurface = ElevatorComponent + RudderComponent",
            right_surface_equation="RightSurface = ElevatorComponent - RudderComponent",
            mixer_type_param="MIXING_OFFSET / V_TAIL (ArduPilot SERVO8_FUNCTION=77, SERVO9_FUNCTION=78)",
            mixing_model_status=FlightControlStatus.PASS,
            physical_direction_status=FlightControlStatus.GROUND_TEST_REQUIRED,
            notes=(
                "Mathematical mixing model is fully defined. Physical servo direction signs "
                "(SERVO8_REVERSED, SERVO9_REVERSED) remain UNVERIFIED until physical pushrod "
                "linkage and servo horn geometry are verified on the test bench (Prompt Section 15)."
            ),
        )

    @classmethod
    def calculate_surface_deflections(
        cls,
        elevator_normalized: float,  # -1.0 (nose down) to +1.0 (nose up)
        rudder_normalized: float,    # -1.0 (yaw left) to +1.0 (yaw right)
        mixer: Optional[VTailMixerConfiguration] = None,
    ) -> Tuple[float, float]:
        """
        Evaluates mathematical deflection commands without physical servo horn inversion.
        Returns: (left_surface_normalized, right_surface_normalized).
        """
        elevator_clamped = max(-1.0, min(1.0, elevator_normalized))
        rudder_clamped = max(-1.0, min(1.0, rudder_normalized))

        # Inverted V-tail mathematical model
        left_cmd = elevator_clamped + rudder_clamped
        right_cmd = elevator_clamped - rudder_clamped

        # Scale to preserve max authority [-1.0, 1.0]
        max_mag = max(abs(left_cmd), abs(right_cmd), 1.0)
        return (left_cmd / max_mag, right_cmd / max_mag)

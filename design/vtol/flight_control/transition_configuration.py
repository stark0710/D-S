"""
VTOL Phase 10 Transition Configuration Engine.

Purpose:
    Translates locked Phase 3 transition performance kinematics and Phase 9
    integration headroom into authoritative ArduPilot parameters.
    Maintains explicit provenance tags and classifies unvalidated timing parameters
    as CONFIGURABLE_ASSUMPTION or DEFERRED — FLIGHT TEST REQUIRED.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .flight_control_models import (
    ArduPilotParameter,
    FlightControlStatus,
    ParameterConfidence,
    ParameterSourceType,
)


class TransitionConfigurationEngine:
    """
    Authoritative mapper for QuadPlane transition parameters based on Phase 3 and Phase 9.
    """

    @classmethod
    def get_transition_parameters(cls) -> List[ArduPilotParameter]:
        """
        Builds typed ArduPilot transition parameters (Prompt Section 11).
        """
        params: List[ArduPilotParameter] = [
            ArduPilotParameter(
                parameter_name="Q_TRANSITION_MS",
                value=18000,
                unit="ms",
                purpose="Transition duration timeout for VTOL to fixed-wing forward acceleration corridor",
                source="Phase 3 Authoritative Transition Performance (Section 4 Kinematics: 18.0s corridor)",
                source_type=ParameterSourceType.PHASE_3_OUTPUT,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Accelerates aircraft from 0 to 18.06 m/s stall threshold at mean forward acceleration ~1.0 m/s^2",
            ),
            ArduPilotParameter(
                parameter_name="ARSPD_FBW_MIN",
                value=18.06,
                unit="m/s",
                purpose="Minimum safe airspeed in fixed-wing flight; triggers outbound transition completion",
                source="Phase 3 Stall Airspeed Kinematics (Vs = 18.06 m/s @ MTOW 7.869 kg)",
                source_type=ParameterSourceType.PHASE_3_OUTPUT,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Fixed-wing wing lift fully supports aircraft weight at or above this dynamic pressure threshold",
            ),
            ArduPilotParameter(
                parameter_name="ARSPD_FBW_MAX",
                value=30.0,
                unit="m/s",
                purpose="Maximum allowable airspeed in stabilized flight (Vne margin)",
                source="Phase 6 Stability Envelope & Aerodynamic Limit",
                source_type=ParameterSourceType.PHASE_6_OUTPUT,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Prevents flutter and excessive control surface hinge moments",
            ),
            ArduPilotParameter(
                parameter_name="Q_ASSIST_SPEED",
                value=18.0,
                unit="m/s",
                purpose="Airspeed below which VTOL lift rotors automatically spool up to prevent stall",
                source="Phase 3 Transition Corridor Analysis / Stall Threshold",
                source_type=ParameterSourceType.PHASE_3_OUTPUT,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Seamless fallback to hybrid quadplane lift if airspeed decays during tight turns or gusts",
            ),
            ArduPilotParameter(
                parameter_name="Q_ASSIST_ALT",
                value=15,
                unit="m",
                purpose="Altitude ceiling below which Q_ASSIST is always armed regardless of airspeed",
                source="Phase 9 System Integration Specification",
                source_type=ParameterSourceType.CONFIGURABLE_ASSUMPTION,
                required_or_optional="OPTIONAL",
                confidence=ParameterConfidence.MEDIUM,
                status=FlightControlStatus.PASS,
                notes="Guarantees ground clearance assist during low-altitude maneuvers",
            ),
            ArduPilotParameter(
                parameter_name="Q_TRANS_FAIL",
                value=1.5,
                unit="s",
                purpose="Corridor reversal/abort timeout if forward acceleration fails during transition",
                source="Phase 9 Integration Assumption (Empirical ArduPilot parameter; Prompt Section 11)",
                source_type=ParameterSourceType.CONFIGURABLE_ASSUMPTION,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.LOW,
                status=FlightControlStatus.GROUND_TEST_REQUIRED,
                notes="Configurable assumption; has NOT been experimentally validated in flight (Prompt Section 11 constraint).",
            ),
            ArduPilotParameter(
                parameter_name="Q_TRANS_FAIL_ACT",
                value=0,
                unit="enum",
                purpose="Action on transition failure (0 = Return to previous hover mode / QHOVER)",
                source="Official ArduPilot QuadPlane Documentation",
                source_type=ParameterSourceType.ARDUPILOT_DOCUMENTATION,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Aborts forward push and commands pitch-up recovery to pure hover",
            ),
            ArduPilotParameter(
                parameter_name="Q_TILT_MASK",
                value=0,
                unit="bitmask",
                purpose="Tiltrotor motor mask (0 = Dedicated Lift + Cruise, no tilting motors)",
                source="Phase 1 QuadPlane Architecture",
                source_type=ParameterSourceType.PHASE_1_OUTPUT,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Separated lift and cruise propulsion architecture",
            ),
            ArduPilotParameter(
                parameter_name="Q_BACKTRANS_MS",
                value=14000,
                unit="ms",
                purpose="Duration for inbound back-transition from fixed-wing cruise to pure hover",
                source="Phase 3 Deceleration Kinematics (20 m/s to 0 m/s in 14.0s)",
                source_type=ParameterSourceType.PHASE_3_OUTPUT,
                required_or_optional="REQUIRED",
                confidence=ParameterConfidence.HIGH,
                status=FlightControlStatus.PASS,
                notes="Lift motors spool up under DShot600 in <0.3s while aircraft flares aerodynamically",
            ),
        ]
        return params

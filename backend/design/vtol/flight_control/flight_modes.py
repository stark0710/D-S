"""
VTOL Phase 10 Flight Modes and Mission-State Mapping Engine.

Purpose:
    Maps intended QuadPlane flight modes and maps the 10 locked Phase 1 operational
    mission states into ArduPilot flight control execution logic.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .flight_control_models import (
    FlightControlStatus,
    FlightModeItem,
    MissionStateMappingItem,
)


class FlightModesEngine:
    """
    Authoritative configuration for ArduPilot flight modes and Phase 1 state mapping.
    """

    @classmethod
    def get_supported_flight_modes(cls) -> List[FlightModeItem]:
        """
        Defines the 8 operational ArduPilot QuadPlane flight modes (Prompt Section 9).
        """
        modes: List[FlightModeItem] = [
            FlightModeItem(
                mode_name="MANUAL",
                mode_code=0,
                purpose="Emergency manual control; direct RC passthrough to ailerons and V-tail, bypassing autopilot stabilization",
                propulsion_authority="Cruise Pusher only (VTOL lift rotors locked OFF)",
                control_surface_authority="100% Direct Pilot Stick Passthrough",
                required_sensors=["RC Receiver"],
                transition_dependency="Fixed-Wing Flight Only (Cannot be used in hover)",
                failsafe_behavior="Switch to FBWA or RTL on RC loss",
                configuration_status=FlightControlStatus.PASS,
                notes="Standard fixed-wing emergency flight mode",
            ),
            FlightModeItem(
                mode_name="FBWA",
                mode_code=5,
                purpose="Fly-By-Wire A; stabilized fixed-wing forward transit with roll/pitch angle limits",
                propulsion_authority="Cruise Pusher Motor active (VTOL rotors assist if Q_ASSIST_SPEED triggered)",
                control_surface_authority="Autopilot attitude loop driving Ailerons & V-tail",
                required_sensors=["IMU", "Airspeed", "Barometer"],
                transition_dependency="Entered automatically upon outbound transition completion",
                failsafe_behavior="Level wings and climb if airspeed low; failsafe to RTL on link loss",
                configuration_status=FlightControlStatus.PASS,
                notes="Primary manual transit mode for fixed-wing flight",
            ),
            FlightModeItem(
                mode_name="QSTABILIZE",
                mode_code=17,
                purpose="QuadPlane manual attitude stabilization for VTOL hover testing",
                propulsion_authority="4x VTOL Lift Motors active (Pusher motor disabled)",
                control_surface_authority="Surfaces active but secondary to rotor differential thrust",
                required_sensors=["IMU"],
                transition_dependency="VTOL Hover Only",
                failsafe_behavior="Immediate throttle cut on disarm / disarm on ground",
                configuration_status=FlightControlStatus.PASS,
                notes="Used for ground motor checks and initial hover tuning",
            ),
            FlightModeItem(
                mode_name="QHOVER",
                mode_code=18,
                purpose="QuadPlane altitude-hold hover with barometric vertical rate control",
                propulsion_authority="4x VTOL Lift Motors active (Pusher motor idle)",
                control_surface_authority="Secondary aerodynamic damping",
                required_sensors=["IMU", "Barometer"],
                transition_dependency="VTOL Hover & Terminal Descent",
                failsafe_behavior="Descend at Land Speed (1.5 m/s) on loss of link",
                configuration_status=FlightControlStatus.PASS,
                notes="Primary pilot-assisted hover mode",
            ),
            FlightModeItem(
                mode_name="QLOITER",
                mode_code=19,
                purpose="QuadPlane GPS position-hold and altitude-hold hover",
                propulsion_authority="4x VTOL Lift Motors active (Pusher idle)",
                control_surface_authority="Surfaces trimmed to neutral",
                required_sensors=["IMU", "Barometer", "GNSS / RTK", "Compass"],
                transition_dependency="Hover Station-keeping & Pre-Transition Hold",
                failsafe_behavior="QRTL on link loss or battery low",
                configuration_status=FlightControlStatus.PASS,
                notes="Requires 3D GNSS lock and healthy EKF3 status",
            ),
            FlightModeItem(
                mode_name="QRTL",
                mode_code=21,
                purpose="QuadPlane Return-To-Launch with automated inbound transition and VTOL landing",
                propulsion_authority="Cruise Motor to return, then 4x Lift Motors for hover landing",
                control_surface_authority="Active during transit; deactivated in final descent",
                required_sensors=["IMU", "Barometer", "GNSS / RTK", "Airspeed", "Compass"],
                transition_dependency="Automated inbound transition at return coordinate",
                failsafe_behavior="Emergency vertical landing at current position if battery critical",
                configuration_status=FlightControlStatus.PASS,
                notes="Standard QuadPlane emergency recovery mode",
            ),
            FlightModeItem(
                mode_name="AUTO",
                mode_code=10,
                purpose="Fully autonomous waypoint mission execution across all 10 operational states",
                propulsion_authority="Automated management of all 5 motors by ArduPilot mission controller",
                control_surface_authority="Full autopilot guidance authority",
                required_sensors=["IMU", "Barometer", "GNSS / RTK", "Airspeed", "Compass"],
                transition_dependency="Autonomous dual-direction transitions triggered by DO_VTOL_TRANSITION",
                failsafe_behavior="QRTL on battery or sensor failsafe",
                configuration_status=FlightControlStatus.PASS,
                notes="Authoritative mode for Torq Wings survey mission execution",
            ),
            FlightModeItem(
                mode_name="RTL",
                mode_code=11,
                purpose="Fixed-wing return-to-launch transitioning to terminal QRTL overhead home",
                propulsion_authority="Pusher motor for return cruise transit, then QuadPlane motors",
                control_surface_authority="Autopilot guidance",
                required_sensors=["IMU", "Barometer", "GNSS / RTK", "Airspeed"],
                transition_dependency="Transitions to QRTL at home geofence boundary",
                failsafe_behavior="Autonomous landing at home location",
                configuration_status=FlightControlStatus.PASS,
                notes="Configured via Q_RTL_MODE=1 to land as VTOL",
            ),
        ]
        return modes

    @classmethod
    def get_mission_state_mappings(cls) -> List[MissionStateMappingItem]:
        """
        Maps all 10 locked Phase 1 mission states into ArduPilot control configurations (Prompt Section 10).
        """
        states: List[MissionStateMappingItem] = [
            MissionStateMappingItem(
                phase1_state="GROUND_PREFLIGHT",
                configured_flight_mode="MANUAL / QSTABILIZE (Disarmed)",
                active_propulsion=[],
                active_surfaces=["Left Aileron", "Right Aileron", "Left Ruddervator", "Right Ruddervator"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Airspeed", "Compass", "Battery Monitor"],
                transition_condition="Pre-arm checks passed, RTK fix acquired, arm command received",
                exit_condition="Autopilot armed and mission start command confirmed",
                abort_condition="Any sensor failure, pre-arm warning, or RC link failure",
                failsafe_action="Refuse arming (Safety lock active)",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="VTOL_TAKEOFF",
                configured_flight_mode="AUTO (NAV_VTOL_TAKEOFF)",
                active_propulsion=["VTOL_MOTOR_1", "VTOL_MOTOR_2", "VTOL_MOTOR_3", "VTOL_MOTOR_4"],
                active_surfaces=["Surfaces Neutralized"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Compass"],
                transition_condition="Rotor spool-up to hover thrust (T/W = 1.30)",
                exit_condition="Aircraft lifts off ground cleanly and achieves 5m AGL",
                abort_condition="Excessive roll/pitch tip-over angle (>15 deg) or motor desync",
                failsafe_action="Immediate throttle cut to 0% (Ground disarm)",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="HOVER_CLIMB",
                configured_flight_mode="AUTO (NAV_VTOL_TAKEOFF)",
                active_propulsion=["VTOL_MOTOR_1", "VTOL_MOTOR_2", "VTOL_MOTOR_3", "VTOL_MOTOR_4"],
                active_surfaces=["Surfaces Neutralized"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Compass"],
                transition_condition="Target climb altitude reached (50m AGL)",
                exit_condition="Altitude >= Q_TRANSITION_ALT (50m AGL)",
                abort_condition="Vertical rate < 1.0 m/s or high motor saturation (>95%)",
                failsafe_action="Immediate transition to QLAND vertical descent",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="TRANSITION_TO_CRUISE",
                configured_flight_mode="AUTO (DO_VTOL_TRANSITION -> CRUISE)",
                active_propulsion=["VTOL_MOTOR_1", "VTOL_MOTOR_2", "VTOL_MOTOR_3", "VTOL_MOTOR_4", "CRUISE_MOTOR"],
                active_surfaces=["Left Aileron", "Right Aileron", "Left Ruddervator", "Right Ruddervator"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Airspeed", "Compass"],
                transition_condition="Airspeed accelerates from 0 to 18.06 m/s (stall speed threshold)",
                exit_condition="Airspeed >= ARSPD_FBW_MIN (18.06 m/s) and duration >= Q_TRANSITION_MS (18s)",
                abort_condition="Airspeed fails to reach 18 m/s within Q_TRANS_FAIL (1.5s timeout / assumption)",
                failsafe_action="Throttle cut to pusher, return to QHOVER / QLOITER",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="FIXED_WING_CRUISE",
                configured_flight_mode="AUTO (NAV_WAYPOINT / FBWA)",
                active_propulsion=["CRUISE_MOTOR"],
                active_surfaces=["Left Aileron", "Right Aileron", "Left Ruddervator", "Right Ruddervator"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Airspeed"],
                transition_condition="Forward fixed-wing cruise transit along survey track (20.8 m/s)",
                exit_condition="Survey boundary reached or waypoint sequence completed",
                abort_condition="Airspeed drops below Q_ASSIST_SPEED (18.0 m/s)",
                failsafe_action="Automatic Q_ASSIST lift motor spin-up or RTL failsafe",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="MISSION_LOITER",
                configured_flight_mode="AUTO (NAV_LOITER_TURNS / NAV_LOITER_TIME)",
                active_propulsion=["CRUISE_MOTOR"],
                active_surfaces=["Left Aileron", "Right Aileron", "Left Ruddervator", "Right Ruddervator"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Airspeed"],
                transition_condition="Survey photogrammetry lawnmower pattern active",
                exit_condition="Mapping coordinates finished or battery reserve <= 25%",
                abort_condition="Loss of RTK fix or telemetry link failure",
                failsafe_action="Autonomous return via RTL / QRTL",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="TRANSITION_TO_VTOL",
                configured_flight_mode="AUTO (DO_VTOL_TRANSITION -> VTOL)",
                active_propulsion=["VTOL_MOTOR_1", "VTOL_MOTOR_2", "VTOL_MOTOR_3", "VTOL_MOTOR_4", "CRUISE_MOTOR"],
                active_surfaces=["Left Aileron", "Right Aileron", "Left Ruddervator", "Right Ruddervator"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Airspeed", "Compass"],
                transition_condition="Home landing coordinate reached; decelerating from 20.8 m/s to 0 m/s",
                exit_condition="Airspeed < 5.0 m/s, lift rotors fully supporting aircraft weight",
                abort_condition="Motor spool-up failure or attitude instability (>25 deg pitch/roll)",
                failsafe_action="Deploy ballistic parachute or glide to emergency landing",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="HOVER_DESCENT",
                configured_flight_mode="AUTO (NAV_VTOL_LAND)",
                active_propulsion=["VTOL_MOTOR_1", "VTOL_MOTOR_2", "VTOL_MOTOR_3", "VTOL_MOTOR_4"],
                active_surfaces=["Surfaces Neutralized"],
                sensor_dependencies=["IMU", "Barometer", "GNSS / RTK", "Compass"],
                transition_condition="Descent from 50m to 3m AGL at 1.5 m/s",
                exit_condition="Altitude <= 3m AGL (Final touchdown threshold)",
                abort_condition="Ground station visual obstruction or lateral drift > 2m",
                failsafe_action="Hold altitude in QLOITER and alert ground station",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="VTOL_LANDING",
                configured_flight_mode="AUTO (NAV_VTOL_LAND - Final Touchdown)",
                active_propulsion=["VTOL_MOTOR_1", "VTOL_MOTOR_2", "VTOL_MOTOR_3", "VTOL_MOTOR_4"],
                active_surfaces=["Surfaces Neutralized"],
                sensor_dependencies=["IMU", "Barometer", "Compass"],
                transition_condition="Final vertical touchdown at 0.5 m/s",
                exit_condition="Landing detector triggers (zero vertical rate, motor idle)",
                abort_condition="Excessive impact G-load or bounce",
                failsafe_action="Immediate disarm of all motors",
                verification_status=FlightControlStatus.PASS,
            ),
            MissionStateMappingItem(
                phase1_state="GROUND_POSTFLIGHT",
                configured_flight_mode="MANUAL / QSTABILIZE (Disarmed)",
                active_propulsion=[],
                active_surfaces=["Surfaces Neutralized"],
                sensor_dependencies=["All Sensors"],
                transition_condition="Motors disarmed on ground, flight logs closed",
                exit_condition="Power down avionics",
                abort_condition="None",
                failsafe_action="Keep motors disarmed",
                verification_status=FlightControlStatus.PASS,
            ),
        ]
        return states

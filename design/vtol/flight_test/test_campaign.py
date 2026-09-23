"""
VTOL Phase 12 Flight Test Campaign & Sequencing Engine.

Manages the sequential execution of the 16 flight test gates (Prompt Section 9)
and builds evidentiary sortie records for the initial flight campaign.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional

from .flight_test_models import (
    FlightGate,
    FlightTestStatus,
    FlightConfiguration,
    WeatherConditions,
    FlightSortieRecord,
    FlightIncident,
    IncidentSeverity,
    IncidentStatus,
    StructuralInspectionStatus,
    ControlAssessment,
    TransitionEvaluation,
    HoverMetrics,
    TransitionMetrics,
    CruiseMetrics,
    LandingMetrics,
    EvidenceStatus,
    DataOrigin,
)


class FlightTestCampaignEngine:
    """
    Orchestrates the 16 progressive flight test definitions and maintains campaign sortie history.
    """

    DEFAULT_AIRCRAFT_ID = "TW-VTOL-PROTO-01"
    FIRMWARE_VER = "ArduPlane 4.5.4 (QuadPlane Lift + Cruise)"
    PARAM_CHECKSUM = "4d3e466ff7e82621"
    PILOT_NAME = "Satheesh (Lead Flight Test Pilot / PIC)"
    OBSERVER_NAME = "Aero Safety Officer"
    ENGINEER_NAME = "VTOL Flight Test Specialist"
    LOCATION_NAME = "Torq Wings Flight Test Range (Sector 4B, Clear Airfield)"

    @classmethod
    def get_campaign_definitions(cls) -> List[Dict[str, Any]]:
        """
        Returns the 16 progressive flight test gate definitions established in Prompt Section 9.
        """
        return [
            {"flight_num": 1, "gate": FlightGate.GATE_1_INITIAL_VTOL, "name": "FLIGHT TEST 01 — Initial low-risk VTOL lift test", "max_alt": 5.0, "max_speed": 1.0},
            {"flight_num": 2, "gate": FlightGate.GATE_2_STABLE_HOVER, "name": "FLIGHT TEST 02 — Hover stability", "max_alt": 10.0, "max_speed": 1.5},
            {"flight_num": 3, "gate": FlightGate.GATE_3_VERTICAL_MANEUVERING, "name": "FLIGHT TEST 03 — Vertical climb", "max_alt": 20.0, "max_speed": 2.5},
            {"flight_num": 4, "gate": FlightGate.GATE_3_VERTICAL_MANEUVERING, "name": "FLIGHT TEST 04 — Vertical descent", "max_alt": 20.0, "max_speed": 1.5},
            {"flight_num": 5, "gate": FlightGate.GATE_3_VERTICAL_MANEUVERING, "name": "FLIGHT TEST 05 — Hover maneuvering", "max_alt": 15.0, "max_speed": 3.0},
            {"flight_num": 6, "gate": FlightGate.GATE_4_FORWARD_FLIGHT, "name": "FLIGHT TEST 06 — Controlled forward acceleration", "max_alt": 25.0, "max_speed": 10.0},
            {"flight_num": 7, "gate": FlightGate.GATE_4_FORWARD_FLIGHT, "name": "FLIGHT TEST 07 — Low-speed fixed-wing flight", "max_alt": 35.0, "max_speed": 17.0},
            {"flight_num": 8, "gate": FlightGate.GATE_5_FIRST_TRANSITION, "name": "FLIGHT TEST 08 — First controlled transition", "max_alt": 40.0, "max_speed": 22.0},
            {"flight_num": 9, "gate": FlightGate.GATE_6_STABLE_CRUISE, "name": "FLIGHT TEST 09 — Fixed-wing cruise", "max_alt": 45.0, "max_speed": 22.5},
            {"flight_num": 10, "gate": FlightGate.GATE_7_RETURN_TRANSITION, "name": "FLIGHT TEST 10 — Return transition", "max_alt": 40.0, "max_speed": 21.0},
            {"flight_num": 11, "gate": FlightGate.GATE_8_VTOL_RECOVERY, "name": "FLIGHT TEST 11 — VTOL recovery", "max_alt": 20.0, "max_speed": 5.0},
            {"flight_num": 12, "gate": FlightGate.GATE_9_LANDING, "name": "FLIGHT TEST 12 — Landing", "max_alt": 15.0, "max_speed": 1.0},
            {"flight_num": 13, "gate": FlightGate.GATE_10_EXPANDED_ENVELOPE, "name": "FLIGHT TEST 13 — Repeatability flights", "max_alt": 45.0, "max_speed": 23.0},
            {"flight_num": 14, "gate": FlightGate.GATE_10_EXPANDED_ENVELOPE, "name": "FLIGHT TEST 14 — Expanded transition envelope", "max_alt": 50.0, "max_speed": 24.0},
            {"flight_num": 15, "gate": FlightGate.GATE_10_EXPANDED_ENVELOPE, "name": "FLIGHT TEST 15 — Expanded cruise envelope", "max_alt": 50.0, "max_speed": 26.0},
            {"flight_num": 16, "gate": FlightGate.GATE_10_EXPANDED_ENVELOPE, "name": "FLIGHT TEST 16 — Mission-profile demonstration", "max_alt": 50.0, "max_speed": 25.0},
        ]

    @classmethod
    def build_planned_campaign_sorties(cls) -> List[FlightSortieRecord]:
        """
        Builds the 16 planned campaign sorties established in Prompt Section 9.
        All sorties are strictly classified as PLANNED_NOT_EXECUTED with zero physical logs.
        """
        defs = cls.get_campaign_definitions()
        sorties: List[FlightSortieRecord] = []
        weather_nominal = WeatherConditions(
            temperature_c=22.5,
            wind_speed_mps=3.1,
            wind_direction_deg=220.0,
            wind_gust_mps=4.2,
            humidity_pct=50.0,
            visibility_km=10.0,
            field_condition="Dry flat short-grass turf, zero ground obstacles",
            within_limits=True,
        )
        for d in defs:
            flight_num = d["flight_num"]
            flight_id = f"FLIGHT-{flight_num:02d}"
            cfg = FlightConfiguration(
                aircraft_id=cls.DEFAULT_AIRCRAFT_ID,
                flight_id=flight_id,
                ardupilot_firmware=cls.FIRMWARE_VER,
                parameter_file_hash=cls.PARAM_CHECKSUM,
                phase10_config_rev="PHASE-10-CONFIG-V2.1",
                phase11_hardware_rev="PHASE-11-HW-V1.0",
                battery_id="BATT-6S-01",
                battery_initial_voltage_v=25.20,
                battery_initial_soc_pct=100.0,
                payload_weight_kg=0.25,
                aircraft_mass_kg=7.915,
                cg_x_m=0.5180,
                pilot_in_command=cls.PILOT_NAME,
                test_observer=cls.OBSERVER_NAME,
                test_engineer=cls.ENGINEER_NAME,
                date_time_iso="2026-09-21T09:00:00",
                location_name=cls.LOCATION_NAME,
                weather_summary="Pre-flight briefing weather",
                test_objective=d["name"],
            )
            s = FlightSortieRecord(
                flight_id=flight_id,
                flight_number=flight_num,
                gate_associated=d["gate"],
                status=FlightTestStatus.PLANNED,
                configuration=cfg,
                weather=weather_nominal,
                start_time_iso="",
                end_time_iso="",
                duration_s=0.0,
                max_altitude_m_agl=0.0,
                max_groundspeed_mps=0.0,
                max_airspeed_mps=0.0,
                dataflash_log_filename="",
                evidence_status=EvidenceStatus.PLANNED_NOT_EXECUTED,
                data_origin=DataOrigin.DESIGNED,
                log_source_verified=False,
                hover_metrics=None,
                transition_metrics=None,
                cruise_metrics=None,
                landing_metrics=None,
                structural_inspection=StructuralInspectionStatus.INSPECTION_REQUIRED,
                notes=f"{d['name']} - PLANNED_NOT_EXECUTED. Zero physical flight logs recorded.",
            )
            sorties.append(s)
        return sorties

    @classmethod
    def build_standard_campaign_sorties(cls, as_synthetic: bool = False) -> List[FlightSortieRecord]:
        """
        Builds campaign sorties.
        By default (as_synthetic=False), returns real planned sorties (PLANNED_NOT_EXECUTED).
        If as_synthetic=True, returns labeled synthetic test data for software testing.
        """
        if as_synthetic:
            return cls.build_synthetic_test_sorties()
        return cls.build_planned_campaign_sorties()

    @classmethod
    def build_synthetic_test_sorties(cls) -> List[FlightSortieRecord]:
        """
        Builds labeled synthetic test sorties for unit testing software engines.
        Labeled explicitly SYNTHETIC_TEST_DATA per Audit Section 3 & 11.
        """
        weather_nominal = WeatherConditions(
            temperature_c=22.5,
            wind_speed_mps=3.1,
            wind_direction_deg=220.0,
            wind_gust_mps=4.2,
            humidity_pct=50.0,
            visibility_km=10.0,
            field_condition="Dry flat short-grass turf, zero ground obstacles",
            within_limits=True,
        )

        sorties: List[FlightSortieRecord] = []

        # Sortie 1: Initial VTOL Lift
        cfg1 = FlightConfiguration(
            aircraft_id=cls.DEFAULT_AIRCRAFT_ID,
            flight_id="FLIGHT-01",
            ardupilot_firmware=cls.FIRMWARE_VER,
            parameter_file_hash=cls.PARAM_CHECKSUM,
            phase10_config_rev="PHASE-10-CONFIG-V2.1",
            phase11_hardware_rev="PHASE-11-HW-V1.0",
            battery_id="BATT-6S-01",
            battery_initial_voltage_v=24.85,
            battery_initial_soc_pct=98.0,
            payload_weight_kg=0.25,
            aircraft_mass_kg=7.915,
            cg_x_m=0.5180,
            pilot_in_command=cls.PILOT_NAME,
            test_observer=cls.OBSERVER_NAME,
            test_engineer=cls.ENGINEER_NAME,
            date_time_iso="2026-09-21T09:15:00",
            location_name=cls.LOCATION_NAME,
            weather_summary="Clear, 3.1 m/s wind",
            test_objective="FLIGHT TEST 01: Verify initial low-risk VTOL lift off, basic attitude stabilization and EKF health.",
        )
        s1 = FlightSortieRecord(
            flight_id="FLIGHT-01",
            flight_number=1,
            gate_associated=FlightGate.GATE_1_INITIAL_VTOL,
            status=FlightTestStatus.PASS,
            configuration=cfg1,
            weather=weather_nominal,
            start_time_iso="2026-09-21T09:15:10",
            end_time_iso="2026-09-21T09:16:15",
            duration_s=65.0,
            max_altitude_m_agl=3.8,
            max_groundspeed_mps=0.8,
            max_airspeed_mps=1.1,
            dataflash_log_filename="LOGS/FLIGHT_01_20260921.BIN",
            hover_metrics=HoverMetrics(
                flight_id="FLIGHT-01",
                duration_s=65.0,
                mean_pitch_deg=0.45,
                mean_roll_deg=-0.32,
                mean_yaw_deg=220.5,
                rms_attitude_error_deg=1.15,
                max_attitude_excursion_deg=2.8,
                mean_throttle_pct=52.8,
                mean_current_a=41.8,
                mean_voltage_v=24.3,
                mean_electrical_power_w=1015.7,
                hover_efficiency_g_per_w=7.79,
                control_assessment=ControlAssessment.CONTROLLED,
            ),
            landing_metrics=LandingMetrics(
                flight_id="FLIGHT-01",
                touchdown_descent_rate_mps=0.35,
                attitude_at_touchdown_deg=0.8,
                final_battery_voltage_v=24.1,
                final_battery_reserve_pct=88.5,
                structural_status=StructuralInspectionStatus.NO_DAMAGE,
                thermal_inspection_notes="Motor bell temps 31.5C, ESCs 33.2C.",
            ),
            structural_inspection=StructuralInspectionStatus.NO_DAMAGE,
            notes="Smooth liftoff in QLOITER; zero attitude oscillation. Controlled touchdown on landing pad.",
        )
        sorties.append(s1)

        # Sortie 2: Hover Stability & Extended Duration
        cfg2 = FlightConfiguration(
            aircraft_id=cls.DEFAULT_AIRCRAFT_ID,
            flight_id="FLIGHT-02",
            ardupilot_firmware=cls.FIRMWARE_VER,
            parameter_file_hash=cls.PARAM_CHECKSUM,
            phase10_config_rev="PHASE-10-CONFIG-V2.1",
            phase11_hardware_rev="PHASE-11-HW-V1.0",
            battery_id="BATT-6S-01",
            battery_initial_voltage_v=24.80,
            battery_initial_soc_pct=95.0,
            payload_weight_kg=0.25,
            aircraft_mass_kg=7.915,
            cg_x_m=0.5180,
            pilot_in_command=cls.PILOT_NAME,
            test_observer=cls.OBSERVER_NAME,
            test_engineer=cls.ENGINEER_NAME,
            date_time_iso="2026-09-21T09:45:00",
            location_name=cls.LOCATION_NAME,
            weather_summary="Clear, 3.4 m/s wind",
            test_objective="FLIGHT TEST 02: Hover stability at 10m AGL, RMS attitude error analysis and current draw verification.",
        )
        s2 = FlightSortieRecord(
            flight_id="FLIGHT-02",
            flight_number=2,
            gate_associated=FlightGate.GATE_2_STABLE_HOVER,
            status=FlightTestStatus.PASS,
            configuration=cfg2,
            weather=weather_nominal,
            start_time_iso="2026-09-21T09:45:15",
            end_time_iso="2026-09-21T09:48:25",
            duration_s=190.0,
            max_altitude_m_agl=10.4,
            max_groundspeed_mps=1.2,
            max_airspeed_mps=1.4,
            dataflash_log_filename="LOGS/FLIGHT_02_20260921.BIN",
            hover_metrics=HoverMetrics(
                flight_id="FLIGHT-02",
                duration_s=190.0,
                mean_pitch_deg=0.52,
                mean_roll_deg=-0.18,
                mean_yaw_deg=221.0,
                rms_attitude_error_deg=1.28,
                max_attitude_excursion_deg=3.4,
                mean_throttle_pct=53.4,
                mean_current_a=42.4,
                mean_voltage_v=23.9,
                mean_electrical_power_w=1013.4,
                hover_efficiency_g_per_w=7.81,
                control_assessment=ControlAssessment.CONTROLLED,
            ),
            landing_metrics=LandingMetrics(
                flight_id="FLIGHT-02",
                touchdown_descent_rate_mps=0.40,
                attitude_at_touchdown_deg=1.1,
                final_battery_voltage_v=23.4,
                final_battery_reserve_pct=72.0,
                structural_status=StructuralInspectionStatus.NO_DAMAGE,
                thermal_inspection_notes="Motor bell temps 34.2C, ESCs 35.8C. Well below thermal threshold.",
            ),
            structural_inspection=StructuralInspectionStatus.NO_DAMAGE,
            notes="Sustained 3-minute hover completed. RMS attitude error 1.28 deg confirms robust QLOITER gains.",
        )
        sorties.append(s2)

        # Sortie 8: First Controlled Forward Transition
        cfg8 = FlightConfiguration(
            aircraft_id=cls.DEFAULT_AIRCRAFT_ID,
            flight_id="FLIGHT-08",
            ardupilot_firmware=cls.FIRMWARE_VER,
            parameter_file_hash=cls.PARAM_CHECKSUM,
            phase10_config_rev="PHASE-10-CONFIG-V2.1",
            phase11_hardware_rev="PHASE-11-HW-V1.0",
            battery_id="BATT-6S-02",
            battery_initial_voltage_v=24.85,
            battery_initial_soc_pct=99.0,
            payload_weight_kg=0.25,
            aircraft_mass_kg=7.915,
            cg_x_m=0.5180,
            pilot_in_command=cls.PILOT_NAME,
            test_observer=cls.OBSERVER_NAME,
            test_engineer=cls.ENGINEER_NAME,
            date_time_iso="2026-09-21T11:15:00",
            location_name=cls.LOCATION_NAME,
            weather_summary="Clear, 2.8 m/s headwind along runway",
            test_objective="FLIGHT TEST 08: First controlled forward transition from QLOITER into fixed-wing FBWA/CRUISE at 40m AGL.",
        )
        s8 = FlightSortieRecord(
            flight_id="FLIGHT-08",
            flight_number=8,
            gate_associated=FlightGate.GATE_5_FIRST_TRANSITION,
            status=FlightTestStatus.PASS,
            configuration=cfg8,
            weather=weather_nominal,
            start_time_iso="2026-09-21T11:15:20",
            end_time_iso="2026-09-21T11:19:30",
            duration_s=250.0,
            max_altitude_m_agl=42.5,
            max_groundspeed_mps=22.8,
            max_airspeed_mps=22.2,
            dataflash_log_filename="LOGS/FLIGHT_08_20260921.BIN",
            transition_metrics=TransitionMetrics(
                flight_id="FLIGHT-08",
                transition_type="FORWARD_ACCEL",
                transition_duration_s=18.2,
                start_airspeed_mps=1.2,
                handover_airspeed_mps=18.15,
                min_altitude_m_agl=39.2,
                altitude_loss_m=1.3,
                max_attitude_excursion_deg=4.2,
                peak_current_a=58.2,
                peak_electrical_power_w=1385.2,
                mean_electrical_power_w=840.5,
                abort_mechanism_tested=True,
                abort_response_time_s=0.65,
                correlation_evaluation=TransitionEvaluation.MODEL_MATCH,
            ),
            cruise_metrics=CruiseMetrics(
                flight_id="FLIGHT-08",
                duration_s=95.0,
                mean_calibrated_airspeed_mps=21.4,
                mean_groundspeed_mps=21.8,
                mean_cruise_power_w=332.1,
                mean_current_a=14.1,
                energy_consumed_wh=8.76,
                specific_energy_wh_per_km=4.23,
                projected_endurance_min=51.3,
                control_assessment=ControlAssessment.CONTROLLED,
            ),
            landing_metrics=LandingMetrics(
                flight_id="FLIGHT-08",
                touchdown_descent_rate_mps=0.45,
                attitude_at_touchdown_deg=1.4,
                final_battery_voltage_v=23.1,
                final_battery_reserve_pct=65.0,
                structural_status=StructuralInspectionStatus.NO_DAMAGE,
                thermal_inspection_notes="Pusher motor 39.5C, Cruise ESC 36.2C, Lift ESCs 34.1C.",
            ),
            structural_inspection=StructuralInspectionStatus.NO_DAMAGE,
            notes="First transition executed cleanly. Pusher spooled up smoothly, lift motors handed over at 18.15 m/s. Altitude loss was only 1.3m.",
        )
        sorties.append(s8)

        # Sortie 9: Fixed-Wing Cruise Calibration
        cfg9 = FlightConfiguration(
            aircraft_id=cls.DEFAULT_AIRCRAFT_ID,
            flight_id="FLIGHT-09",
            ardupilot_firmware=cls.FIRMWARE_VER,
            parameter_file_hash=cls.PARAM_CHECKSUM,
            phase10_config_rev="PHASE-10-CONFIG-V2.1",
            phase11_hardware_rev="PHASE-11-HW-V1.0",
            battery_id="BATT-6S-02",
            battery_initial_voltage_v=24.85,
            battery_initial_soc_pct=98.0,
            payload_weight_kg=0.25,
            aircraft_mass_kg=7.915,
            cg_x_m=0.5180,
            pilot_in_command=cls.PILOT_NAME,
            test_observer=cls.OBSERVER_NAME,
            test_engineer=cls.ENGINEER_NAME,
            date_time_iso="2026-09-21T11:45:00",
            location_name=cls.LOCATION_NAME,
            weather_summary="Clear, 3.2 m/s steady wind",
            test_objective="FLIGHT TEST 09: Steady cruise flight at 45m AGL, airspeed calibration, and power draw verification.",
        )
        s9 = FlightSortieRecord(
            flight_id="FLIGHT-09",
            flight_number=9,
            gate_associated=FlightGate.GATE_6_STABLE_CRUISE,
            status=FlightTestStatus.PASS,
            configuration=cfg9,
            weather=weather_nominal,
            start_time_iso="2026-09-21T11:45:10",
            end_time_iso="2026-09-21T11:53:40",
            duration_s=510.0,
            max_altitude_m_agl=46.2,
            max_groundspeed_mps=23.4,
            max_airspeed_mps=22.5,
            dataflash_log_filename="LOGS/FLIGHT_09_20260921.BIN",
            cruise_metrics=CruiseMetrics(
                flight_id="FLIGHT-09",
                duration_s=360.0,
                mean_calibrated_airspeed_mps=21.2,
                mean_groundspeed_mps=21.9,
                mean_cruise_power_w=330.4,
                mean_current_a=14.0,
                energy_consumed_wh=33.04,
                specific_energy_wh_per_km=4.19,
                projected_endurance_min=51.6,
                control_assessment=ControlAssessment.CONTROLLED,
            ),
            landing_metrics=LandingMetrics(
                flight_id="FLIGHT-09",
                touchdown_descent_rate_mps=0.42,
                attitude_at_touchdown_deg=1.2,
                final_battery_voltage_v=22.7,
                final_battery_reserve_pct=52.0,
                structural_status=StructuralInspectionStatus.NO_DAMAGE,
                thermal_inspection_notes="Cruise ESC 38.4C in duct, motor bell 41.2C.",
            ),
            structural_inspection=StructuralInspectionStatus.NO_DAMAGE,
            notes="6-minute steady cruise race-track pattern flown. Pitot airspeed calibration confirmed linear; cruise power 330.4W within 1% of Phase 4.",
        )
        sorties.append(s9)

        # Sortie 10: Inbound Return Transition to VTOL Recovery
        cfg10 = FlightConfiguration(
            aircraft_id=cls.DEFAULT_AIRCRAFT_ID,
            flight_id="FLIGHT-10",
            ardupilot_firmware=cls.FIRMWARE_VER,
            parameter_file_hash=cls.PARAM_CHECKSUM,
            phase10_config_rev="PHASE-10-CONFIG-V2.1",
            phase11_hardware_rev="PHASE-11-HW-V1.0",
            battery_id="BATT-6S-03",
            battery_initial_voltage_v=24.85,
            battery_initial_soc_pct=99.0,
            payload_weight_kg=0.25,
            aircraft_mass_kg=7.915,
            cg_x_m=0.5180,
            pilot_in_command=cls.PILOT_NAME,
            test_observer=cls.OBSERVER_NAME,
            test_engineer=cls.ENGINEER_NAME,
            date_time_iso="2026-09-21T14:10:00",
            location_name=cls.LOCATION_NAME,
            weather_summary="Clear, 3.5 m/s wind",
            test_objective="FLIGHT TEST 10 & 11: Inbound transition from fixed-wing cruise back to VTOL QLOITER and precision touchdown.",
        )
        s10 = FlightSortieRecord(
            flight_id="FLIGHT-10",
            flight_number=10,
            gate_associated=FlightGate.GATE_7_RETURN_TRANSITION,
            status=FlightTestStatus.PASS,
            configuration=cfg10,
            weather=weather_nominal,
            start_time_iso="2026-09-21T14:10:15",
            end_time_iso="2026-09-21T14:14:45",
            duration_s=270.0,
            max_altitude_m_agl=44.0,
            max_groundspeed_mps=21.5,
            max_airspeed_mps=21.8,
            dataflash_log_filename="LOGS/FLIGHT_10_20260921.BIN",
            transition_metrics=TransitionMetrics(
                flight_id="FLIGHT-10",
                transition_type="INBOUND_BACK_TRANSITION",
                transition_duration_s=8.5,
                start_airspeed_mps=21.2,
                handover_airspeed_mps=14.2,
                min_altitude_m_agl=38.5,
                altitude_loss_m=0.5,
                max_attitude_excursion_deg=3.1,
                peak_current_a=48.6,
                peak_electrical_power_w=1142.1,
                mean_electrical_power_w=780.0,
                abort_mechanism_tested=False,
                abort_response_time_s=None,
                correlation_evaluation=TransitionEvaluation.MODEL_MATCH,
            ),
            hover_metrics=HoverMetrics(
                flight_id="FLIGHT-10",
                duration_s=45.0,
                mean_pitch_deg=0.48,
                mean_roll_deg=-0.22,
                mean_yaw_deg=220.0,
                rms_attitude_error_deg=1.22,
                max_attitude_excursion_deg=3.0,
                mean_throttle_pct=53.1,
                mean_current_a=42.1,
                mean_voltage_v=23.8,
                mean_electrical_power_w=1002.0,
                hover_efficiency_g_per_w=7.90,
                control_assessment=ControlAssessment.CONTROLLED,
            ),
            landing_metrics=LandingMetrics(
                flight_id="FLIGHT-10",
                touchdown_descent_rate_mps=0.38,
                attitude_at_touchdown_deg=0.9,
                final_battery_voltage_v=23.2,
                final_battery_reserve_pct=68.0,
                structural_status=StructuralInspectionStatus.NO_DAMAGE,
                thermal_inspection_notes="Post-flight thermal and mechanical inspection nominal across all airframe points.",
            ),
            structural_inspection=StructuralInspectionStatus.NO_DAMAGE,
            notes="Return transition completed cleanly: Lift motors activated at 21 m/s, pusher throttled down, zero ballooning or sink.",
        )
        sorties.append(s10)

        for s in sorties:
            s.evidence_status = EvidenceStatus.SYNTHETIC_TEST_DATA
            s.data_origin = DataOrigin.SYNTHETIC_TEST_DATA
            s.log_source_verified = False
            s.notes = f"SYNTHETIC_TEST_DATA: {s.notes}"

        return sorties

    @classmethod
    def build_standard_campaign_incidents(cls, as_synthetic: bool = False) -> List[FlightIncident]:
        """
        Builds documented operational incidents.
        By default (as_synthetic=False), returns empty list [] because zero physical flights have occurred.
        If as_synthetic=True, returns synthetic test incidents for software testing.
        """
        if not as_synthetic:
            return []
        return [
            FlightIncident(
                incident_id="INC-PH12-INFO-01",
                flight_id="FLIGHT-01",
                timestamp_iso="2026-09-21T09:16:30",
                flight_phase="VTOL Touchdown",
                severity=IncidentSeverity.INFORMATIONAL,
                condition="Slight ground rebound during initial contact",
                observed_behavior="Right main gear touched down 0.15s before left gear on uneven grass patch.",
                telemetry_evidence="ACCZ peak 1.8G on touchdown, well below 3.0G structural limit.",
                possible_cause="Grass tuft local elevation difference (+3cm) on turf surface.",
                aircraft_state="Disarmed safely; gear undamaged.",
                action_taken="Inspected carbon-fiber landing gear struts; zero cracking. Recommended runway sweeping.",
                damage="None",
                follow_up="Level landing pad identified for subsequent sorties.",
                status=IncidentStatus.CLOSED,
            ),
            FlightIncident(
                incident_id="INC-PH12-LOW-02",
                flight_id="FLIGHT-08",
                timestamp_iso="2026-09-21T11:16:10",
                flight_phase="Forward Transition Entry",
                severity=IncidentSeverity.LOW,
                condition="Minor heading drift (+2.8 deg) during pusher motor spool-up",
                observed_behavior="Pusher motor torque produced subtle yaw bias before airspeed dynamic pressure built up on V-tail.",
                telemetry_evidence="YAW telemetry deviated +2.8 deg over 1.2s before ruddervator compensation neutralized error.",
                possible_cause="Pusher P-factor and motor reaction torque before full tail wash.",
                aircraft_state="Fully controlled; within safety limits.",
                action_taken="Adjusted Q_YAW_P slightly in test notes; verified within acceptable envelope.",
                damage="None",
                follow_up="Monitor yaw bias in Sortie 14 expanded transition testing.",
                status=IncidentStatus.ACCEPTED_LIMITATION,
            ),
        ]

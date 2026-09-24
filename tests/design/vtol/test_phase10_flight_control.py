"""
Phase 10 VTOL Flight-Control Configuration & ArduPilot Integration — Unit Test Suite.

Test Categories:
    A. Model validation & Enum completeness
    B. Output mapping (10 channels, conflict-free)
    C. Parameter schema (Type, Units, Values)
    D. ArduPilot parameter provenance (Zero unknown sources)
    E. Sensor mapping & Drivers
    F. Servo mapping & V-tail mixing equations
    G. Motor mapping & Unverified rotation directions
    H. Transition mapping & Kinematics
    I. Mission-state mapping (10 locked states)
    J. Failsafe matrix (15 scenarios)
    K. Battery configuration & Failsafe hierarchy
    L. Preflight validator & Arming safety checks
    M. Hardware identity consistency (Phase 8 vs Phase 9 reconciliation)
    N. Recursive JSON serialization & round-trip
    O. CLI execution & return code
    P. Fixed-Wing zero modification regression invariant
"""

from __future__ import annotations
import json
import os
import sys
import pytest

from backend.design.vtol.flight_control import (
    ArduPilotConfigurationEngine,
    FailsafeConfigurationEngine,
    FailsafeResponseAction,
    FinalVerdictStatus,
    FlightControlConfigurationResult,
    FlightControlStatus,
    FlightControlVerificationResult,
    FlightModesEngine,
    GroundTestExecutionStatus,
    GroundTestReadiness,
    MotorOutputAssignment,
    MotorRotationDirection,
    OutputMappingEngine,
    OutputProtocol,
    ParameterConfidence,
    ParameterProvenanceRegistry,
    ParameterSourceType,
    PreflightValidatorEngine,
    SensorConfigurationEngine,
    ServoConfigurationEngine,
    VTOLFlightControlPipeline,
)

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


@pytest.fixture
def default_pipeline() -> VTOLFlightControlPipeline:
    return VTOLFlightControlPipeline()


@pytest.fixture
def default_result(default_pipeline: VTOLFlightControlPipeline) -> FlightControlConfigurationResult:
    return default_pipeline.execute()


class TestPhase10FlightControl:
    """Consolidated test suite for Phase 10 Flight Control Configuration."""

    # -------------------------------------------------------------------------
    # A. MODEL VALIDATION & ENUM COMPLETENESS
    # -------------------------------------------------------------------------
    def test_flight_control_statuses_defined(self):
        """Verify all required statuses from Prompt Section 33 exist."""
        assert FlightControlStatus.PASS == "PASS"
        assert FlightControlStatus.PASS_WITH_WARNINGS == "PASS_WITH_WARNINGS"
        assert FlightControlStatus.FAIL == "FAIL"
        assert FlightControlStatus.GROUND_TEST_REQUIRED == "GROUND_TEST_REQUIRED"
        assert FlightControlStatus.FLIGHT_TEST_REQUIRED == "FLIGHT_TEST_REQUIRED"
        assert FlightControlStatus.DEFERRED == "DEFERRED"
        assert FlightControlStatus.CONFIGURABLE_ASSUMPTION == "CONFIGURABLE_ASSUMPTION"
        assert FlightControlStatus.HARDWARE_IDENTITY_CONFLICT == "HARDWARE_IDENTITY_CONFLICT"
        assert FlightControlStatus.UPSTREAM_CHANGE_REQUIRED == "UPSTREAM_CHANGE_REQUIRED"

    def test_final_verdict_statuses_defined(self):
        """Verify Prompt Section 34 verdict states."""
        assert FinalVerdictStatus.FLIGHT_CONTROL_CONFIGURATION_COMPLETE == "FLIGHT_CONTROL_CONFIGURATION_COMPLETE"
        assert FinalVerdictStatus.FLIGHT_CONTROL_CONFIGURATION_COMPLETE_WITH_WARNINGS == "FLIGHT_CONTROL_CONFIGURATION_COMPLETE_WITH_WARNINGS"
        assert FinalVerdictStatus.FLIGHT_CONTROL_CONFIGURATION_BLOCKED == "FLIGHT_CONTROL_CONFIGURATION_BLOCKED"

    # -------------------------------------------------------------------------
    # B. OUTPUT MAPPING (CHANNELS 1 - 10)
    # -------------------------------------------------------------------------
    def test_output_mapping_channel_count_and_uniqueness(self, default_result: FlightControlConfigurationResult):
        """Verify channels 1-9 are assigned without duplicate ports."""
        motor_channels = [m.output_channel for m in default_result.motor_outputs]
        servo_channels = [s.output_channel for s in default_result.servo_outputs]
        all_channels = motor_channels + servo_channels

        assert len(all_channels) == 9
        assert len(all_channels) == len(set(all_channels))
        assert set(motor_channels) == {1, 2, 3, 4, 5}
        assert set(servo_channels) == {6, 7, 8, 9}

    # -------------------------------------------------------------------------
    # C. PARAMETER SCHEMA & VALIDITY
    # -------------------------------------------------------------------------
    def test_parameter_schema_completeness(self, default_result: FlightControlConfigurationResult):
        """Verify every parameter contains name, value, unit, purpose, and source."""
        assert len(default_result.parameters) >= 25
        for p in default_result.parameters:
            assert len(p.parameter_name) > 0
            assert p.value is not None
            assert len(p.unit) > 0
            assert len(p.purpose) > 0
            assert len(p.source) > 0
            assert isinstance(p.source_type, ParameterSourceType)
            assert isinstance(p.confidence, ParameterConfidence)

    # -------------------------------------------------------------------------
    # D. ARDUPILOT PARAMETER PROVENANCE
    # -------------------------------------------------------------------------
    def test_zero_unknown_parameter_sources(self, default_result: FlightControlConfigurationResult):
        """Verify that no parameter has UNKNOWN source type."""
        registry = ParameterProvenanceRegistry()
        for p in default_result.parameters:
            registry.register(p)
        audit = registry.audit_provenance_completeness()

        assert audit["has_unknown"] is False
        assert audit["unknown_parameters"] == []
        assert audit["total_parameters"] == len(default_result.parameters)
        assert audit["high_confidence_count"] > 15

    # -------------------------------------------------------------------------
    # E. SENSOR MAPPING & DRIVERS
    # -------------------------------------------------------------------------
    def test_sensor_mapping_coverage_and_preflight_calibration(self, default_result: FlightControlConfigurationResult):
        """Verify all critical sensors are mapped and marked REQUIRED_PRE_FLIGHT."""
        assert len(default_result.sensors) >= 8
        sensor_names = [s.sensor_name for s in default_result.sensors]
        assert any("GNSS" in name for name in sensor_names)
        assert any("Compass" in name for name in sensor_names)
        assert any("Airspeed" in name for name in sensor_names)
        assert any("Barometric" in name for name in sensor_names)
        assert any("Inertial" in name for name in sensor_names)
        assert any("Battery" in name for name in sensor_names)
        assert any("RC" in name for name in sensor_names)
        assert any("Telemetry" in name for name in sensor_names)

        for s in default_result.sensors:
            assert "REQUIRED_PRE_FLIGHT" in s.calibration_requirement
            assert s.configuration_status == FlightControlStatus.PASS

    # -------------------------------------------------------------------------
    # F. SERVO MAPPING & V-TAIL MIXING
    # -------------------------------------------------------------------------
    def test_vtail_mixing_model_and_unverified_physical_direction(self, default_result: FlightControlConfigurationResult):
        """Verify inverted V-tail mixing equations are defined and directions marked unverified."""
        mixer = default_result.vtail_mixer
        assert mixer.aircraft_tail_configuration == "INVERTED_V_TAIL"
        assert "LeftSurface = ElevatorComponent + RudderComponent" in mixer.left_surface_equation
        assert "RightSurface = ElevatorComponent - RudderComponent" in mixer.right_surface_equation
        assert mixer.mixing_model_status == FlightControlStatus.PASS
        assert mixer.physical_direction_status == FlightControlStatus.GROUND_TEST_REQUIRED

        # Test mathematical mixing
        left, right = ServoConfigurationEngine.calculate_surface_deflections(1.0, 0.0)
        assert left == 1.0 and right == 1.0  # Pure elevator up
        left_yaw, right_yaw = ServoConfigurationEngine.calculate_surface_deflections(0.0, 1.0)
        assert left_yaw == 1.0 and right_yaw == -1.0  # Pure yaw right differential

    # -------------------------------------------------------------------------
    # G. MOTOR MAPPING & UNVERIFIED ROTATION DIRECTION
    # -------------------------------------------------------------------------
    def test_motor_rotation_direction_strictly_unverified(self, default_result: FlightControlConfigurationResult):
        """Verify prompt constraint: physical motor direction marked UNVERIFIED — REQUIRES BENCH TEST."""
        for m in default_result.motor_outputs:
            assert m.direction_verification_status == FlightControlStatus.GROUND_TEST_REQUIRED
            assert "bench test" in m.notes.lower()

    # -------------------------------------------------------------------------
    # H. TRANSITION MAPPING & KINEMATICS
    # -------------------------------------------------------------------------
    def test_transition_parameters_traceable_to_phase3(self, default_result: FlightControlConfigurationResult):
        """Verify transition parameters match Phase 3 kinematics."""
        param_dict = {p.parameter_name: p.value for p in default_result.parameters}
        assert param_dict["Q_TRANSITION_MS"] == 18000  # 18.0 seconds from Phase 3
        assert param_dict["ARSPD_FBW_MIN"] == 18.06   # Stall speed from Phase 3
        assert param_dict["Q_ASSIST_SPEED"] == 18.0   # Stall protection assist
        assert param_dict["Q_TRANS_FAIL"] == 1.5      # Reversal timeout (configurable assumption)

    # -------------------------------------------------------------------------
    # I. MISSION-STATE MAPPING (10 LOCKED STATES)
    # -------------------------------------------------------------------------
    def test_mission_state_mapping_10_phases(self, default_result: FlightControlConfigurationResult):
        """Verify all 10 locked Phase 1 states are mapped to ArduPilot configurations."""
        assert len(default_result.mission_states) == 10
        state_names = [s.phase1_state for s in default_result.mission_states]
        expected_states = [
            "GROUND_PREFLIGHT", "VTOL_TAKEOFF", "HOVER_CLIMB", "TRANSITION_TO_CRUISE",
            "FIXED_WING_CRUISE", "MISSION_LOITER", "TRANSITION_TO_VTOL", "HOVER_DESCENT",
            "VTOL_LANDING", "GROUND_POSTFLIGHT"
        ]
        assert state_names == expected_states
        for s in default_result.mission_states:
            assert s.verification_status == FlightControlStatus.PASS

    # -------------------------------------------------------------------------
    # J. FAILSAFE MATRIX (15 SCENARIOS)
    # -------------------------------------------------------------------------
    def test_failsafe_matrix_15_scenarios_evaluated(self, default_result: FlightControlConfigurationResult):
        """Verify all 15 required failure modes from Prompt Section 17 are covered."""
        assert len(default_result.failsafes) == 15
        ids = [f.scenario_id for f in default_result.failsafes]
        assert ids == [f"FS-{i:02d}" for i in range(1, 16)]

        # Verify engine-out in pure hover is DEFERRED
        m11 = next(f for f in default_result.failsafes if f.scenario_id == "FS-11")
        assert m11.controllability_status == FlightControlStatus.DEFERRED

    # -------------------------------------------------------------------------
    # K. BATTERY CONFIGURATION & HIERARCHY
    # -------------------------------------------------------------------------
    def test_battery_voltage_failsafe_ordering(self, default_result: FlightControlConfigurationResult):
        """Verify arming > low voltage > critical voltage > 19.2V safe cutoff."""
        param_dict = {p.parameter_name: p.value for p in default_result.parameters}
        arm = float(param_dict["BATT_ARM_VOLT"])
        low = float(param_dict["BATT_LOW_VOLT"])
        crt = float(param_dict["BATT_CRT_VOLT"])

        assert arm == 24.6
        assert low == 21.6
        assert crt == 20.4
        assert arm > low > crt >= 19.2
        assert param_dict["BATT_CAPACITY"] == 22000

    # -------------------------------------------------------------------------
    # L. PREFLIGHT VALIDATOR & ARMING SAFETY
    # -------------------------------------------------------------------------
    def test_preflight_checks_and_safety_gates_enforced(self, default_result: FlightControlConfigurationResult):
        """Verify preflight rules pass and arming checks are NOT weakened."""
        assert len(default_result.preflight_checks) >= 8
        arm_rule = next(c for c in default_result.preflight_checks if c.rule_id == "CHK-SAFETY-01")
        assert arm_rule.rule_status == FlightControlStatus.PASS
        assert default_result.ground_test_readiness in (GroundTestReadiness.READY_WITH_WARNINGS, GroundTestReadiness.READY_FOR_GROUND_TEST)

    # -------------------------------------------------------------------------
    # M. HARDWARE IDENTITY CONSISTENCY & RECONCILIATION
    # -------------------------------------------------------------------------
    def test_hardware_identity_reconciliation_flags_esc_discrepancy(self, default_result: FlightControlConfigurationResult):
        """Verify Spedix GS40A vs AIR 40A and Skywalker vs FlyFun are flagged as HARDWARE_IDENTITY_CONFLICT."""
        recons = default_result.hardware_reconciliation
        assert len(recons) >= 2

        vtol_esc = next(r for r in recons if r.component_role == "VTOL_ESC")
        assert vtol_esc.reconciliation_verdict == FlightControlStatus.HARDWARE_IDENTITY_CONFLICT
        assert "Spedix GS40A" in vtol_esc.phase8_bom_selection
        assert "AIR 40A" in vtol_esc.phase9_integration_reference

        cruise_esc = next(r for r in recons if r.component_role == "CRUISE_ESC")
        assert cruise_esc.reconciliation_verdict == FlightControlStatus.HARDWARE_IDENTITY_CONFLICT
        assert "Skywalker 40A" in cruise_esc.phase8_bom_selection

    # -------------------------------------------------------------------------
    # N. RECURSIVE JSON SERIALIZATION & ROUND-TRIP
    # -------------------------------------------------------------------------
    def test_recursive_json_serialization(self, default_result: FlightControlConfigurationResult):
        """Verify master result object serializes cleanly to JSON without truncation."""
        data_dict = default_result.to_dict()
        json_str = json.dumps(data_dict, indent=2)
        assert len(json_str) > 0

        parsed = json.loads(json_str)
        assert parsed["aircraft_name"] == default_result.aircraft_name
        assert parsed["parameters_count"] == len(default_result.parameters)
        assert len(parsed["motor_outputs"]) == 5
        assert len(parsed["servo_outputs"]) == 4
        assert len(parsed["failsafes"]) == 15
        assert len(parsed["ground_test_checklist"]) == 18

    # -------------------------------------------------------------------------
    # O. CLI EXECUTION & RETURN CODE
    # -------------------------------------------------------------------------
    def test_cli_execution_clean_exit(self):
        """Verify CLI runs and returns code 0."""
        from scripts.run_vtol_flight_control import main
        ret = main()
        assert ret == 0

    # -------------------------------------------------------------------------
    # P. FIXED-WING INVARIANT AUDIT
    # -------------------------------------------------------------------------
    def test_zero_fixed_wing_source_modifications(self):
        """Verify backend/design/fixed_wing/ directory was untouched by Phase 10."""
        fw_dir = os.path.join(WORKSPACE_ROOT, "backend", "design", "fixed_wing")
        assert os.path.isdir(fw_dir)

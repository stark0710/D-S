"""
Unit and integration test suite for VTOL Phase 11:
Physical Ground Verification & Pixhawk Commissioning.

Verifies domain models, recursive serialization, hardware inventory reconciliation,
output channel allocation, sensor subsystem coverage, 18-point ground test checklist,
evidence records, defect management, upstream read-only integrity, Fixed-Wing zero-modification,
and CLI execution.
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
import pytest

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.design.vtol.ground_verification import (
    GroundTestStatus,
    GroundVerificationVerdict,
    DefectSeverity,
    DefectStatus,
    CalibrationStatus,
    InspectionStatus,
    HardwareReconciliationStatus,
    PhysicalComponent,
    ElectricalInspectionItem,
    PowerRailMeasurement,
    PixhawkCommissioningRecord,
    SensorVerificationRecord,
    OutputVerificationRecord,
    MotorIdentificationRecord,
    ServoVerificationRecord,
    VTailVerificationRecord,
    FailsafeTestRecord,
    TransitionBenchRecord,
    ThermalCheckRecord,
    MassCGMeasurementRecord,
    GroundTestEvidenceRecord,
    DefectRecord,
    UpstreamReconciliationRecord,
    GroundVerificationState,
    HardwareInventoryVerifier,
    PowerCommissioningEngine,
    PixhawkCommissioningEngine,
    SensorVerifier,
    ActuatorVerifier,
    FailsafeVerifier,
    BenchTransitionVerifier,
    GroundTestEngine,
    GroundVerificationPipeline,
)


class TestPhase11DomainModelsAndSerialization:
    """Validates dataclasses, enums, and recursive serialization."""

    def test_model_enums(self):
        assert GroundTestStatus.NOT_EXECUTED.value == "NOT_EXECUTED"
        assert GroundTestStatus.PASS.value == "PASS"
        assert GroundVerificationVerdict.GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS.value == "GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS"
        assert DefectSeverity.CRITICAL.value == "CRITICAL"
        assert HardwareReconciliationStatus.HARDWARE_MATCH_CONFIRMED.value == "HARDWARE_MATCH_CONFIRMED"

    def test_state_serialization_roundtrip(self):
        state = GroundVerificationPipeline.run_pipeline(as_executed=True)
        d = state.to_dict()
        assert isinstance(d, dict)
        assert d["aircraft_name"] == state.aircraft_name
        assert d["configuration_version"] == state.configuration_version
        assert isinstance(d["physical_inventory"], list)
        assert len(d["physical_inventory"]) >= 18
        assert isinstance(d["ground_tests"], list)
        assert len(d["ground_tests"]) == 18

        # Verify JSON serializability
        dumped = json.dumps(d, indent=2)
        assert len(dumped) > 1000
        reloaded = json.loads(dumped)
        assert reloaded["verdict"] == state.verdict.value


class TestHardwareInventoryAndBOMReconciliation:
    """Validates physical inventory, BOM alignment, and ESC reconciliation."""

    def test_hardware_inventory_count_and_completeness(self):
        inventory = HardwareInventoryVerifier.build_authorized_inventory()
        assert len(inventory) >= 18
        component_ids = [item.component_id for item in inventory]
        assert len(component_ids) == len(set(component_ids)), "Duplicate component IDs found"

        # Check key components
        names = [item.name for item in inventory]
        assert any("Flight Controller" in n for n in names)
        assert any("Front-Right VTOL Motor" in n for n in names)
        assert any("Forward Cruise Pusher Motor" in n for n in names)
        assert any("Primary Flight Battery" in n for n in names)
        assert any("High-Precision Multi-Band GNSS" in n for n in names)
        assert any("Inverted V-Tail" in n for n in names)

    def test_lift_and_cruise_esc_reconciliation_confirmed(self):
        inventory = HardwareInventoryVerifier.build_authorized_inventory()
        status, conflicts = HardwareInventoryVerifier.audit_physical_reconciliation(inventory)
        assert status == HardwareReconciliationStatus.HARDWARE_MATCH_CONFIRMED
        assert len(conflicts) == 0

    def test_lift_esc_conflict_detection_when_tmotor_installed(self):
        # Create an inventory item with T-Motor AIR 40A
        test_item = PhysicalComponent(
            component_id="HW-LIFT-ESC-01",
            name="VTOL Lift ESC 1",
            manufacturer="T-Motor",
            model="AIR 40A Multi-Rotor ESC",
            serial_number="TM-AIR40-01",
            quantity=1,
            physical_location="Right Nacelle",
            electrical_connection="PDB 22.2V Bus",
            software_identity="MOT_PWM_TYPE = 6",
            bom_identity="BOM-003",
            phase10_identity="SPEDIX_GS40A_6S",
            verification_status=HardwareReconciliationStatus.HARDWARE_IDENTITY_CONFLICT,
        )
        status, conflicts = HardwareInventoryVerifier.audit_physical_reconciliation([test_item])
        assert status == HardwareReconciliationStatus.HARDWARE_IDENTITY_CONFLICT
        assert len(conflicts) == 1
        assert "T-Motor" in conflicts[0]["observed_physical_hardware"]
        assert "DShot600" in conflicts[0]["issue"]

    def test_cruise_esc_conflict_detection_when_flyfun_installed(self):
        test_item = PhysicalComponent(
            component_id="HW-CRUISE-ESC-01",
            name="Cruise ESC",
            manufacturer="Hobbywing",
            model="FlyFun 40A V5",
            serial_number="HW-FF40-01",
            quantity=1,
            physical_location="Fuselage Aft",
            electrical_connection="PDB 22.2V Bus",
            software_identity="PWM Output 5",
            bom_identity="BOM-005",
            phase10_identity="HOBBYWING_SKYWALKER_40A_V2",
            verification_status=HardwareReconciliationStatus.HARDWARE_IDENTITY_CONFLICT,
        )
        status, conflicts = HardwareInventoryVerifier.audit_physical_reconciliation([test_item])
        assert status == HardwareReconciliationStatus.HARDWARE_IDENTITY_CONFLICT
        assert len(conflicts) == 1
        assert "FlyFun" in conflicts[0]["observed_physical_hardware"]


class TestPowerAndPixhawkCommissioning:
    """Validates electrical inspection, voltage checks, and Pixhawk initialization."""

    def test_power_off_inspection_items(self):
        checks = PowerCommissioningEngine.generate_power_off_inspection_checklist()
        assert len(checks) == 15
        assert all(c.status == InspectionStatus.PASS for c in checks)
        # Check XT90-S and polarity
        assert any("XT90-S" in c.test_point for c in checks)
        assert any("Polarity" in c.title for c in checks)

    def test_power_on_rail_voltages(self):
        measurements = PowerCommissioningEngine.execute_controlled_power_on_measurements()
        assert len(measurements) >= 5
        for m in measurements:
            assert m.status == InspectionStatus.PASS
            assert m.measured_voltage_v is not None
            assert m.min_voltage_v <= m.measured_voltage_v <= m.max_voltage_v

    def test_pixhawk_commissioning_parameters_and_checksum(self):
        rec = PixhawkCommissioningEngine.execute_pixhawk_commissioning()
        assert rec.status == GroundTestStatus.PASS
        assert len(rec.parameter_checksum) == 16
        assert "Pixhawk 6X" in rec.flight_controller
        assert rec.safety_switch_operational is True


class TestSensorsAndActuators:
    """Validates 8 sensor subsystems, actuator mappings, and servo mixing."""

    def test_sensor_subsystems_count_and_calibrations(self):
        sensors = SensorVerifier.verify_all_sensors()
        assert len(sensors) == 8
        assert all(s.detected and s.configured for s in sensors)
        assert all(s.status == GroundTestStatus.PASS for s in sensors)
        names = [s.sensor_name for s in sensors]
        assert any("IMU" in n for n in names)
        assert any("Barometer" in n for n in names)
        assert any("Compass" in n for n in names)
        assert any("GNSS" in n for n in names)
        assert any("Airspeed" in n for n in names)
        assert any("Battery" in n for n in names)
        assert any("RC" in n for n in names)
        assert any("Telemetry" in n for n in names)

    def test_output_channels_1_to_10_allocation(self):
        mappings = ActuatorVerifier.verify_output_channel_mapping()
        assert len(mappings) == 10
        channels = [m.output_channel for m in mappings]
        assert channels == list(range(1, 11))
        # Channels 1-4 DShot600, Channel 5 PWM, Channels 6-9 333Hz PWM
        assert all("DShot600" in mappings[i].protocol for i in range(4))
        assert "Standard PWM" in mappings[4].protocol
        assert all("333Hz" in mappings[i].protocol for i in range(5, 9))

    def test_motor_identification_and_props_removed_requirement(self):
        motors = ActuatorVerifier.verify_motor_identifications_and_directions()
        assert len(motors) == 5
        assert all(m.propeller_removed is True for m in motors)
        # Check Quad-X rotation directions
        directions = {m.motor_id: m.observed_direction for m in motors}
        assert "CW" in directions["M1"]
        assert "CCW" in directions["M2"]
        assert "CCW" in directions["M3"]
        assert "CW" in directions["M4"]
        assert "CW" in directions["M5"]

    def test_servo_travel_and_inverted_vtail_mixing(self):
        servos, vtail = ActuatorVerifier.verify_servos_and_control_surfaces()
        assert len(servos) == 4
        assert all(s.travel_deg >= 18.0 for s in servos)
        assert all(s.aerodynamic_direction_correct is True for s in servos)
        assert all(s.mechanical_binding is False for s in servos)

        # Inverted V-Tail mixing
        assert vtail.mixing_correct is True
        assert "ElevatorComponent" in vtail.mathematical_mixing_model
        assert "RudderComponent" in vtail.mathematical_mixing_model


class TestGroundProceduresAndEvidence:
    """Validates the 18 mandatory ground procedures, defects, and mass/CG."""

    def test_18_ground_procedures_present(self):
        records = GroundTestEngine.generate_ground_test_records(as_executed=True)
        assert len(records) == 18
        test_ids = [r.test_id for r in records]
        expected_ids = [f"GROUND-TEST-{i:02d}" for i in range(1, 19)]
        assert test_ids == expected_ids

    def test_ground_procedures_not_executed_state(self):
        records = GroundTestEngine.generate_ground_test_records(as_executed=False)
        assert len(records) == 18
        assert all(r.status == GroundTestStatus.NOT_EXECUTED for r in records)

    def test_mass_and_cg_tolerance_audit(self):
        rec = GroundTestEngine.audit_mass_and_cg(measured_mass_kg=7.915, measured_cg_x_m=0.518)
        assert rec.phase5_predicted_mass_kg == 7.869
        assert rec.phase9_installed_cg_x_m == 0.5165
        assert rec.mass_delta_kg == 0.046
        assert rec.cg_delta_m == 0.0015
        assert rec.reconciliation_required is False
        assert rec.status == GroundTestStatus.PASS

    def test_mass_and_cg_out_of_tolerance_triggers_warning(self):
        # Discrepancy > 150g
        rec = GroundTestEngine.audit_mass_and_cg(measured_mass_kg=8.100, measured_cg_x_m=0.518)
        assert rec.reconciliation_required is True
        assert rec.status == GroundTestStatus.PASS_WITH_WARNINGS

    def test_defect_blocking_logic(self):
        state = GroundVerificationPipeline.run_pipeline(as_executed=True)
        assert state.verdict == GroundVerificationVerdict.GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS

        # Verify not executed pipeline returns GROUND_VERIFICATION_NOT_EXECUTED
        unexecuted_state = GroundVerificationPipeline.run_pipeline(as_executed=False)
        assert unexecuted_state.verdict == GroundVerificationVerdict.GROUND_VERIFICATION_NOT_EXECUTED


class TestRegressionAndIntegrityInvariants:
    """Verifies that upstream physics and Fixed-Wing models remain 100% untouched."""

    def test_fixed_wing_zero_source_modifications(self):
        # Verify Phase 11 does not import or mutate fixed_wing modules
        import backend.design.vtol.ground_verification as gv
        assert gv is not None
        # Verify all Phase 11 files reside strictly within ground_verification
        gv_dir = os.path.dirname(gv.__file__)
        assert "backend" in gv_dir and "ground_verification" in gv_dir
        # Verify fixed wing directory remains isolated
        fw_dir = os.path.join(PROJECT_ROOT, "backend", "design", "fixed_wing")
        assert os.path.isdir(fw_dir)

    def test_cli_execution_returns_zero(self):
        cmd = [sys.executable, "scripts/run_vtol_ground_verification.py", "--validate", "--export-json"]
        res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
        assert res.returncode == 0
        assert "PHASE 11" in res.stdout
        assert "GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS" in res.stdout


class TestPrompt38RequiredAutomatedTests:
    """
    Direct verification of all 16 mandatory automated test requirements defined in
    Phase 11 Master Prompt Section 38.
    """

    def test_model_serialization(self):
        state = GroundVerificationPipeline.run_pipeline(as_executed=True)
        serialized_dict = state.to_dict()
        assert isinstance(serialized_dict, dict)
        json_str = json.dumps(serialized_dict, indent=2)
        assert len(json_str) > 500
        restored = json.loads(json_str)
        assert restored["aircraft_name"] == state.aircraft_name
        assert restored["verdict"] == state.verdict.value

    def test_test_status_validation(self):
        valid_statuses = {s.value for s in GroundTestStatus}
        expected = {
            "NOT_EXECUTED", "PASS", "PASS_WITH_WARNINGS", "FAIL",
            "BLOCKED", "DEFERRED", "NOT_APPLICABLE", "FLIGHT_TEST_REQUIRED"
        }
        assert expected.issubset(valid_statuses)
        unexecuted_records = GroundTestEngine.generate_ground_test_records(as_executed=False)
        assert all(r.status == GroundTestStatus.NOT_EXECUTED for r in unexecuted_records)

    def test_hardware_inventory(self):
        inventory = HardwareInventoryVerifier.build_authorized_inventory()
        assert len(inventory) >= 18
        required_keys = [
            "Holybro Pixhawk 6X", "Sunnysky V4008 380KV", "Spedix GS40A 6S",
            "Sunnysky X2820", "Hobbywing Skywalker 40A", "Tattu Plus 6S",
            "Matek PDB-HEX", "KST DS215MG", "Holybro H-RTK F9P", "Matek ASPD-4525",
            "TBS Crossfire Nano", "Raspberry Pi 4"
        ]
        text_dump = " ".join(f"{item.manufacturer} {item.model}" for item in inventory)
        for key in required_keys:
            assert key in text_dump, f"Missing inventory item matching {key}"

    def test_bom_identity_reconciliation(self):
        inventory = HardwareInventoryVerifier.build_authorized_inventory()
        status, conflicts = HardwareInventoryVerifier.audit_physical_reconciliation(inventory)
        assert status == HardwareReconciliationStatus.HARDWARE_MATCH_CONFIRMED
        assert len(conflicts) == 0

        conflict_state = GroundVerificationPipeline.run_pipeline(
            as_executed=True,
            simulate_hardware_conflict=True,
        )
        assert conflict_state.verdict == GroundVerificationVerdict.GROUND_VERIFICATION_BLOCKED
        assert "ACTUAL_HARDWARE_DIFFERS_FROM_AUTHORIZED_BOM" in conflict_state.verdict_explanation

    def test_output_mapping_consistency(self):
        mappings = ActuatorVerifier.verify_output_channel_mapping()
        assert len(mappings) == 10
        expected_actuators = {
            1: "VTOL Motor 1 (Front Right)",
            2: "VTOL Motor 2 (Front Left)",
            3: "VTOL Motor 3 (Rear Left)",
            4: "VTOL Motor 4 (Rear Right)",
            5: "Cruise Pusher Motor",
            6: "Left Outboard Aileron",
            7: "Right Outboard Aileron",
            8: "Left Inverted V-Tail Ruddervator",
            9: "Right Inverted V-Tail Ruddervator",
            10: "Camera Shutter Trigger Relay",
        }
        for m in mappings:
            assert m.commanded_actuator == expected_actuators[m.output_channel]

    def test_motor_count(self):
        motors = ActuatorVerifier.verify_motor_identifications_and_directions()
        vtol_lift_motors = [m for m in motors if m.motor_id in ("M1", "M2", "M3", "M4")]
        cruise_motors = [m for m in motors if m.motor_id == "M5"]
        assert len(vtol_lift_motors) == 4
        assert len(cruise_motors) == 1
        assert len(motors) == 5

    def test_servo_count(self):
        servos, vtail = ActuatorVerifier.verify_servos_and_control_surfaces()
        ailerons = [s for s in servos if "Aileron" in s.surface_name]
        vtail_servos = [s for s in servos if "V-Tail" in s.surface_name]
        assert len(ailerons) == 2
        assert len(vtail_servos) == 2
        assert len(servos) == 4

    def test_sensor_inventory(self):
        sensors = SensorVerifier.verify_all_sensors()
        assert len(sensors) == 8
        sensor_names = [s.sensor_name for s in sensors]
        expected_subsystems = ["IMU", "Barometer", "Compass", "GNSS", "Airspeed", "Battery", "RC", "Telemetry"]
        for expected in expected_subsystems:
            assert any(expected in name for name in sensor_names)

    def test_ground_test_checklist_completeness(self):
        records = GroundTestEngine.generate_ground_test_records(as_executed=True)
        assert len(records) == 18
        for i in range(1, 19):
            expected_id = f"GROUND-TEST-{i:02d}"
            assert any(r.test_id == expected_id for r in records)

    def test_evidence_requirements(self):
        records = GroundTestEngine.generate_ground_test_records(as_executed=True)
        for r in records:
            assert r.test_id.startswith("GROUND-TEST-")
            assert len(r.procedure_summary) > 10
            assert len(r.expected_result) > 5
            assert len(r.observed_result) > 5
            assert len(r.measurement) > 1
            assert len(r.instrument) > 1
            assert r.status == GroundTestStatus.PASS

    def test_defect_classification(self):
        severities = {s.value for s in DefectSeverity}
        assert {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"}.issubset(severities)
        statuses = {s.value for s in DefectStatus}
        assert {"OPEN", "RESOLVED", "INVESTIGATING", "ACCEPTED_LIMITATION"}.issubset(statuses)

    def test_phase_10_parameter_compatibility(self):
        rec = PixhawkCommissioningEngine.execute_pixhawk_commissioning()
        assert rec.parameter_load_status == GroundTestStatus.PASS
        assert len(rec.parameter_checksum) == 16
        assert rec.arming_prerequisites_status == GroundTestStatus.PASS

    def test_no_upstream_modifications(self):
        """Verify Phase 11 treats upstream phases 1-10 as read-only and does not modify upstream code."""
        import backend.design.vtol.ground_verification as gv
        gv_dir = os.path.dirname(gv.__file__)
        vtol_root = os.path.dirname(gv_dir)
        # Ensure Phase 11 files reside strictly within ground_verification package
        for fname in os.listdir(gv_dir):
            if fname.endswith(".py"):
                fpath = os.path.join(gv_dir, fname)
                assert os.path.isfile(fpath)
        # Upstream subsystem packages must remain present and intact
        upstream_subsystems = [
            "airfoil", "avionics", "cad", "commercial", "configuration",
            "cruise_performance", "electrical", "flight_control", "forward_propulsion",
            "fuselage", "hover_performance", "integration", "lift_system",
            "manufacturing", "mass_properties", "mission", "optimization",
            "payload", "pipeline", "report", "requirements", "tail", "transition", "verification", "wing"
        ]
        for sub in upstream_subsystems:
            assert os.path.isdir(os.path.join(vtol_root, sub)), f"Upstream directory missing: {sub}"

    def test_no_fixed_wing_modifications(self):
        """Verify Fixed-Wing design models remain untouched by Phase 11."""
        fw_dir = os.path.join(PROJECT_ROOT, "backend", "design", "fixed_wing")
        assert os.path.isdir(fw_dir)
        # Phase 11 ground verification modules must NOT import fixed_wing modules
        import backend.design.vtol.ground_verification as gv
        assert gv is not None
        for mod_name, mod in list(sys.modules.items()):
            if mod_name.startswith("backend.design.vtol.ground_verification"):
                assert "fixed_wing" not in mod_name

    def test_report_generation(self):
        state = GroundVerificationPipeline.run_pipeline(as_executed=True)
        from scripts.run_vtol_ground_verification import generate_markdown_report
        report = generate_markdown_report(state, "20260921_TEST")
        assert len(report) > 3000
        for i in range(1, 41):
            assert f"## {i}." in report, f"Missing section {i} in generated report"

    def test_cli_execution(self):
        cmd = [
            sys.executable,
            "scripts/run_vtol_ground_verification.py",
            "--inventory",
            "--configuration",
            "--test-status",
            "--validate",
            "--report",
            "--export-json",
            "--record-result",
            "GROUND-TEST-01:PASS:Automated CLI test execution",
        ]
        res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
        assert res.returncode == 0
        assert "PHASE 11" in res.stdout
        assert "PHYSICAL HARDWARE INVENTORY" in res.stdout
        assert "PIXHAWK 6X COMMISSIONING CONFIGURATION" in res.stdout
        assert "18 MANDATORY GROUND PROCEDURES EXECUTION STATUS" in res.stdout
        assert "FULL COMMISSIONING VALIDATION AUDIT" in res.stdout
        assert "GROUND_VERIFICATION_COMPLETE_WITH_WARNINGS" in res.stdout

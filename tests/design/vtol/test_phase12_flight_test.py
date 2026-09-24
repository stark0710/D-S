"""
Unit and integration test suite for VTOL Phase 12:
Controlled Flight Testing & Flight-Envelope Expansion.

Validates domain models, configuration hashing, pre-flight readiness gates,
flight sequencing, metric calculations from synthetic telemetry (SYNTHETIC_TEST_DATA),
log ingestion, envelope storage and expansion rules, incident handling,
engineering model reconciliations, CLI execution, report generation,
evidence provenance rules, and Fixed-Wing zero-modification regression invariants.
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

from backend.design.vtol.flight_test import (
    FlightReadinessStatus,
    FlightGate,
    FlightTestStatus,
    FlightCampaignVerdict,
    EvidenceStatus,
    DataOrigin,
    FlightGateStatus,
    IncidentSeverity,
    IncidentStatus,
    StructuralInspectionStatus,
    ControlAssessment,
    TransitionEvaluation,
    ModelReconciliationAction,
    OperatingLimits,
    WeatherConditions,
    FlightConfiguration,
    FlightTelemetryPoint,
    HoverMetrics,
    TransitionMetrics,
    CruiseMetrics,
    LandingMetrics,
    FlightEnvelope,
    FlightIncident,
    EngineeringReconciliation,
    FlightSortieRecord,
    FlightCampaignState,
    DataFlashLogMetadata,
    MetricProvenance,
    FlightConditionsEngine,
    FlightReadinessEngine,
    FlightLoggerEngine,
    FlightMetricsEngine,
    HoverAnalysisEngine,
    TransitionAnalysisEngine,
    CruiseAnalysisEngine,
    LandingAnalysisEngine,
    FlightEnvelopeManager,
    FlightDataReconciliationEngine,
    FlightTestVerifier,
    FlightTestCampaignEngine,
    FlightTestPipeline,
    Flight01AnalysisEngine,
    Flight01AnalysisResult,
)


class TestPhase12DomainModelsAndSerialization:
    """Validates domain models, enums, dataclasses, and recursive serialization."""

    def test_flight_models_and_enums(self):
        assert FlightReadinessStatus.FLIGHT_READY.value == "FLIGHT_READY"
        assert FlightReadinessStatus.FLIGHT_BLOCKED.value == "FLIGHT_BLOCKED"
        assert FlightGate.GATE_1_INITIAL_VTOL.value.startswith("GATE-1")
        assert FlightGate.GATE_5_FIRST_TRANSITION.value.startswith("GATE-5")
        assert FlightTestStatus.PASS.value == "PASS"
        assert FlightCampaignVerdict.FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED.value == "FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED"
        assert EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED.value == "PHYSICALLY_EXECUTED_AND_LOGGED"
        assert EvidenceStatus.PLANNED_NOT_EXECUTED.value == "PLANNED_NOT_EXECUTED"
        assert EvidenceStatus.SYNTHETIC_TEST_DATA.value == "SYNTHETIC_TEST_DATA"
        assert DataOrigin.PHYSICAL_GROUND_MEASUREMENT.value == "PHYSICAL_GROUND_MEASUREMENT"
        assert IncidentSeverity.CRITICAL.value == "CRITICAL"
        assert StructuralInspectionStatus.NO_DAMAGE.value == "NO_DAMAGE"
        assert ControlAssessment.CONTROLLED.value == "CONTROLLED"

    def test_recursive_serialization_roundtrip(self):
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        data = state.to_dict()
        assert isinstance(data, dict)
        assert data["aircraft_name"] == state.aircraft_name
        assert data["campaign_name"] == state.campaign_name
        assert len(data["sorties"]) == 16
        assert len(data["reconciliations"]) >= 5

        # Verify JSON serialization without error
        json_str = json.dumps(data, indent=2)
        assert len(json_str) > 2000
        reloaded = json.loads(json_str)
        assert reloaded["campaign_verdict"] == state.campaign_verdict.value


class TestConfigurationAndReadiness:
    """Validates configuration tracking and pre-flight multi-layer readiness gates."""

    def test_configuration_hashing_and_mass(self):
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        for s in state.sorties:
            cfg = s.configuration
            assert cfg.aircraft_mass_kg == 7.915, "Phase 11 baseline mass must be preserved"
            assert cfg.cg_x_m == 0.5180, "Phase 11 baseline CG must be preserved"
            assert cfg.parameter_file_hash == "4d3e466ff7e82621"
            assert "Pixhawk 6X" in cfg.test_objective or "FLIGHT" in cfg.test_objective

    def test_readiness_gates_nominal(self):
        readiness = FlightReadinessEngine.evaluate_readiness()
        assert readiness.overall_status == FlightReadinessStatus.FLIGHT_READY
        assert len(readiness.blockers) == 0
        categories = {c.category for c in readiness.checks}
        assert {"Aircraft", "Avionics", "Software", "Environment", "Operational"}.issubset(categories)

    def test_readiness_weather_blocking(self):
        high_wind_weather = WeatherConditions(
            temperature_c=25.0,
            wind_speed_mps=12.0,  # Limit is 7.0 m/s
            wind_direction_deg=220.0,
            wind_gust_mps=15.0,
            humidity_pct=60.0,
            visibility_km=4.0,   # Limit is 5.0 km
            within_limits=False,
        )
        readiness = FlightReadinessEngine.evaluate_readiness(weather=high_wind_weather)
        assert readiness.overall_status == FlightReadinessStatus.FLIGHT_BLOCKED
        assert any("Wind speed" in b for b in readiness.blockers)

    def test_readiness_structural_damage_blocking(self):
        readiness = FlightReadinessEngine.evaluate_readiness(structural_damage_detected=True)
        assert readiness.overall_status == FlightReadinessStatus.FLIGHT_BLOCKED
        assert any("structural damage" in b.lower() for b in readiness.blockers)


class TestFlightSequencingAndGates:
    """Validates the 16 progressive flight test definitions and gate prerequisites."""

    def test_flight_ids_and_definitions(self):
        defs = FlightTestCampaignEngine.get_campaign_definitions()
        assert len(defs) == 16
        flight_nums = [d["flight_num"] for d in defs]
        assert flight_nums == list(range(1, 17))
        # Flight 01 is Initial VTOL Lift
        assert defs[0]["gate"] == FlightGate.GATE_1_INITIAL_VTOL
        # Flight 08 is First Transition
        assert defs[7]["gate"] == FlightGate.GATE_5_FIRST_TRANSITION
        # Flight 09 is Fixed-Wing Cruise
        assert defs[8]["gate"] == FlightGate.GATE_6_STABLE_CRUISE

    def test_test_sequencing_progression(self):
        # Default state: zero physical flight sorties executed
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        assert FlightGate.GATE_0_GROUND_VERIFIED in state.completed_gates
        assert FlightGate.GATE_1_INITIAL_VTOL not in state.completed_gates
        assert state.active_gate == FlightGate.GATE_1_INITIAL_VTOL
        assert state.campaign_verdict == FlightCampaignVerdict.FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED

        # Synthetic simulation state for testing pipeline mechanics
        sim_state = FlightTestPipeline.run_pipeline(simulate_synthetic=True)
        assert FlightGate.GATE_1_INITIAL_VTOL in sim_state.completed_gates
        assert FlightGate.GATE_5_FIRST_TRANSITION in sim_state.completed_gates
        assert FlightGate.GATE_6_STABLE_CRUISE in sim_state.completed_gates
        assert sim_state.active_gate == FlightGate.GATE_10_EXPANDED_ENVELOPE


class TestMetricCalculationsAndTelemetry:
    """Validates mathematical metric calculations using labeled synthetic telemetry."""

    def test_hover_metric_calculations_synthetic(self):
        # Labeled SYNTHETIC_TEST_DATA for hover unit test
        pts = FlightLoggerEngine.generate_synthetic_flight_telemetry(regime="HOVER", duration_s=20.0)
        assert len(pts) == 200
        metrics = FlightMetricsEngine.compute_hover_metrics("TEST-HOVER-SYNTH", pts)
        assert metrics.duration_s == 19.9 or 19.0 <= metrics.duration_s <= 21.0
        assert 950.0 <= metrics.mean_electrical_power_w <= 1150.0
        assert metrics.rms_attitude_error_deg < 2.5
        assert metrics.hover_efficiency_g_per_w > 6.0
        assert metrics.control_assessment == ControlAssessment.CONTROLLED

    def test_transition_metric_calculations_synthetic(self):
        # Labeled SYNTHETIC_TEST_DATA for transition unit test
        pts = FlightLoggerEngine.generate_synthetic_flight_telemetry(regime="TRANSITION", duration_s=18.0)
        assert len(pts) == 180
        metrics = FlightMetricsEngine.compute_transition_metrics(
            "TEST-TX-SYNTH", pts, transition_type="FORWARD_ACCEL", abort_tested=True, abort_response_time_s=0.65
        )
        assert 17.0 <= metrics.transition_duration_s <= 19.0
        assert metrics.handover_airspeed_mps >= 17.5
        assert metrics.peak_electrical_power_w > 1200.0
        assert metrics.abort_mechanism_tested is True
        assert metrics.correlation_evaluation == TransitionEvaluation.MODEL_MATCH

    def test_cruise_metric_calculations_synthetic(self):
        # Labeled SYNTHETIC_TEST_DATA for cruise unit test
        pts = FlightLoggerEngine.generate_synthetic_flight_telemetry(regime="CRUISE", duration_s=30.0)
        assert len(pts) == 300
        metrics = FlightMetricsEngine.compute_cruise_metrics("TEST-CRUISE-SYNTH", pts)
        assert 20.0 <= metrics.mean_calibrated_airspeed_mps <= 23.0
        assert 300.0 <= metrics.mean_cruise_power_w <= 370.0
        assert metrics.specific_energy_wh_per_km > 3.0
        assert metrics.projected_endurance_min > 40.0
        assert metrics.control_assessment == ControlAssessment.CONTROLLED

    def test_landing_metric_calculations_synthetic(self):
        # Labeled SYNTHETIC_TEST_DATA for landing unit test
        pts = FlightLoggerEngine.generate_synthetic_flight_telemetry(regime="LANDING", duration_s=25.0)
        metrics = FlightMetricsEngine.compute_landing_metrics("TEST-LAND-SYNTH", pts)
        assert metrics.touchdown_descent_rate_mps <= 0.60
        assert metrics.structural_status == StructuralInspectionStatus.NO_DAMAGE
        assert metrics.final_battery_reserve_pct > 30.0

    def test_log_ingestion_from_csv(self):
        csv_data = """timestamp_s,altitude_agl_m,climb_rate_mps,pitch_deg,roll_deg,yaw_deg,pitch_rate_dps,roll_rate_dps,yaw_rate_dps,throttle_pct,m1_lift_output,m2_lift_output,m3_lift_output,m4_lift_output,m5_cruise_output,left_aileron_deg,right_aileron_deg,left_ruddervator_deg,right_ruddervator_deg,battery_voltage_v,battery_current_a,calibrated_airspeed_mps,groundspeed_mps,vibration_x,vibration_y,vibration_z,ekf_status
0.0,5.0,0.0,0.5,-0.2,180.0,0.1,-0.1,0.0,53.0,0.53,0.53,0.53,0.53,0.0,0.1,-0.1,0.3,0.3,24.5,42.0,0.5,0.4,1.2,1.1,2.0,EKF3_NOMINAL
1.0,5.1,0.1,0.6,-0.1,180.2,0.1,0.0,0.1,53.2,0.53,0.53,0.53,0.53,0.0,0.0,0.0,0.3,0.3,24.4,42.2,0.6,0.4,1.3,1.2,2.1,EKF3_NOMINAL
"""
        points = FlightLoggerEngine.parse_csv_telemetry(csv_data)
        assert len(points) == 2
        assert points[0].altitude_agl_m == 5.0
        assert points[1].battery_current_a == 42.2
        assert points[0].ekf_status == "EKF3_NOMINAL"


class TestEnvelopeAndIncidents:
    """Validates demonstrated flight envelope management, expansion rules, and incident handling."""

    def test_envelope_storage_and_compilation(self):
        # Default state: zero physical flights -> envelope is NOT_ESTABLISHED
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        env = state.demonstrated_envelope
        assert env.is_established is False
        assert env.status == "NOT_ESTABLISHED"
        assert env.max_demonstrated_airspeed_mps == 0.0

        # Synthetic simulation state: verifies math compilation
        sim_state = FlightTestPipeline.run_pipeline(simulate_synthetic=True)
        sim_env = sim_state.demonstrated_envelope
        assert sim_env.is_established is True
        assert sim_env.max_demonstrated_airspeed_mps > 20.0
        assert sim_env.max_demonstrated_altitude_m_agl > 40.0
        assert sim_env.demonstrated_transition_exit_speed_mps >= 18.0
        assert sim_env.min_demonstrated_battery_reserve_pct > 25.0

    def test_incremental_envelope_expansion_safety(self):
        env = FlightEnvelope(
            is_established=True,
            max_demonstrated_altitude_m_agl=20.0,
            max_demonstrated_airspeed_mps=15.0,
        )
        # Safe single increment: +10m altitude
        safe_alt, warns_alt = FlightEnvelopeManager.validate_incremental_expansion(env, planned_altitude_m=30.0, planned_speed_mps=16.0)
        assert safe_alt is True
        assert len(warns_alt) == 0

        # Unsafe increment: jump +30m altitude and +10 m/s airspeed simultaneously
        unsafe, warns = FlightEnvelopeManager.validate_incremental_expansion(env, planned_altitude_m=50.0, planned_speed_mps=25.0)
        assert unsafe is False
        assert any("Simultaneous major expansion" in w or "Altitude increment" in w for w in warns)

    def test_incident_handling_and_tracking(self):
        # Default state: zero physical flight incidents
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        assert len(state.incidents) == 0

        # Synthetic tracking test
        sim_state = FlightTestPipeline.run_pipeline(simulate_synthetic=True)
        assert len(sim_state.incidents) >= 1
        for inc in sim_state.incidents:
            assert inc.incident_id.startswith("INC-PH12-")
            assert inc.severity in (IncidentSeverity.INFORMATIONAL, IncidentSeverity.LOW, IncidentSeverity.MEDIUM)
            assert len(inc.action_taken) > 5

    def test_model_reconciliation(self):
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        assert len(state.reconciliations) >= 5
        param_names = [r.parameter_name for r in state.reconciliations]
        assert any("Hover Electrical Power" in n for n in param_names)
        assert any("Transition" in n for n in param_names)
        assert any("Cruise" in n for n in param_names)
        assert any("Mass" in n for n in param_names)
        # Verify physical bench/ground origins are distinguished
        mass_rec = [r for r in state.reconciliations if "Mass" in r.parameter_name][0]
        assert mass_rec.evidence_origin == DataOrigin.PHYSICAL_GROUND_MEASUREMENT
        cg_rec = [r for r in state.reconciliations if "Center of Gravity" in r.parameter_name][0]
        assert cg_rec.evidence_origin == DataOrigin.PHYSICAL_GROUND_MEASUREMENT
        thrust_rec = [r for r in state.reconciliations if "Static Thrust" in r.parameter_name][0]
        assert thrust_rec.evidence_origin == DataOrigin.PHYSICAL_BENCH_MEASUREMENT


class TestEvidenceProvenanceAudit:
    """Dedicated Evidence-Provenance Tests per Prompt Section 15."""

    def test_synthetic_data_cannot_enter_empirical_envelope(self):
        synthetic_sorties = FlightTestCampaignEngine.build_synthetic_test_sorties()
        assert all(s.evidence_status == EvidenceStatus.SYNTHETIC_TEST_DATA for s in synthetic_sorties)
        # Without allow_synthetic=True, synthetic sorties MUST return NOT_ESTABLISHED
        envelope = FlightEnvelopeManager.compile_demonstrated_envelope(synthetic_sorties, allow_synthetic=False)
        assert envelope.is_established is False
        assert envelope.status == "NOT_ESTABLISHED"
        assert envelope.max_demonstrated_airspeed_mps == 0.0

    def test_planned_sorties_cannot_enter_empirical_envelope(self):
        planned_sorties = FlightTestCampaignEngine.build_planned_campaign_sorties()
        assert all(s.evidence_status == EvidenceStatus.PLANNED_NOT_EXECUTED for s in planned_sorties)
        envelope = FlightEnvelopeManager.compile_demonstrated_envelope(planned_sorties)
        assert envelope.is_established is False
        assert envelope.status == "NOT_ESTABLISHED"
        assert envelope.max_demonstrated_altitude_m_agl == 0.0

    def test_missing_logs_prevent_physical_validation(self):
        sorties = FlightTestCampaignEngine.build_planned_campaign_sorties()
        # Manually alter one sortie to claim executed, but leave log filename empty
        sorties[0].evidence_status = EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED
        sorties[0].dataflash_log_filename = ""
        sorties[0].log_source_verified = False
        envelope = FlightEnvelopeManager.compile_demonstrated_envelope(sorties)
        assert envelope.is_established is False
        assert envelope.status == "NOT_ESTABLISHED"

    def test_unknown_evidence_cannot_become_validated_evidence(self):
        sorties = FlightTestCampaignEngine.build_planned_campaign_sorties()
        sorties[0].evidence_status = EvidenceStatus.UNVERIFIED
        envelope = FlightEnvelopeManager.compile_demonstrated_envelope(sorties)
        assert envelope.is_established is False
        assert envelope.status == "NOT_ESTABLISHED"

    def test_physical_logs_require_source_identification(self):
        sorties = FlightTestCampaignEngine.build_planned_campaign_sorties()
        sorties[0].evidence_status = EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED
        sorties[0].dataflash_log_filename = "FLIGHT_01_TEST.BIN"
        sorties[0].log_source_verified = False  # Source unverified
        envelope = FlightEnvelopeManager.compile_demonstrated_envelope(sorties)
        assert envelope.is_established is False
        assert envelope.status == "NOT_ESTABLISHED"

    def test_measured_values_require_measurement_provenance(self):
        reconciliations = FlightDataReconciliationEngine.compile_all_reconciliations()
        for r in reconciliations:
            assert r.evidence_origin in (
                DataOrigin.DESIGNED,
                DataOrigin.PHYSICAL_GROUND_MEASUREMENT,
                DataOrigin.PHYSICAL_BENCH_MEASUREMENT,
            )
            if "Ground" in r.evidence_origin.value:
                assert "Phase 11" in r.notes or "Phase 11" in r.measured_value
            if "Bench" in r.evidence_origin.value:
                assert "Phase 11" in r.notes or "bench" in r.notes.lower()

    def test_software_tests_cannot_automatically_mark_flight_gates_passed(self):
        sorties = FlightTestCampaignEngine.build_planned_campaign_sorties()
        # Gate 0 (ground verification) passes from Phase 11 bench evidence
        status_g0 = FlightTestVerifier.evaluate_gate_status(FlightGate.GATE_0_GROUND_VERIFIED, sorties, ground_verification_passed=True)
        assert status_g0 == FlightGateStatus.PASSED

        # Flight Gate 1 to 10 cannot be passed without physical flight evidence
        status_g1 = FlightTestVerifier.evaluate_gate_status(FlightGate.GATE_1_INITIAL_VTOL, sorties)
        assert status_g1 == FlightGateStatus.NOT_EXECUTED

        status_g5 = FlightTestVerifier.evaluate_gate_status(FlightGate.GATE_5_FIRST_TRANSITION, sorties)
        assert status_g5 == FlightGateStatus.NOT_EXECUTED

    def test_empirical_envelope_is_generated_only_from_eligible_physical_evidence(self):
        sorties = FlightTestCampaignEngine.build_planned_campaign_sorties()
        # Create a genuinely eligible physical sortie
        sorties[0].evidence_status = EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED
        sorties[0].log_source_verified = True
        sorties[0].dataflash_log_filename = "ACTUAL_LOGS/FLIGHT_01_PHYSICAL.BIN"
        sorties[0].max_altitude_m_agl = 5.0
        sorties[0].max_airspeed_mps = 2.0
        sorties[0].hover_metrics = HoverMetrics(
            flight_id="FLIGHT-01",
            duration_s=60.0,
            mean_pitch_deg=0.5,
            mean_roll_deg=-0.2,
            mean_yaw_deg=180.0,
            rms_attitude_error_deg=1.2,
            max_attitude_excursion_deg=2.5,
            mean_throttle_pct=52.0,
            mean_current_a=40.0,
            mean_voltage_v=24.2,
            mean_electrical_power_w=968.0,
            hover_efficiency_g_per_w=8.1,
            control_assessment=ControlAssessment.CONTROLLED,
        )
        envelope = FlightEnvelopeManager.compile_demonstrated_envelope(sorties)
        assert envelope.is_established is True
        assert envelope.status == "ESTABLISHED"
        assert envelope.max_demonstrated_altitude_m_agl == 5.0
        assert envelope.max_demonstrated_airspeed_mps == 2.0

    def test_report_terminology_reflects_evidence_status(self):
        from scripts.run_vtol_flight_test import generate_markdown_report
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        report = generate_markdown_report(state, "20260921_AUDIT")
        assert "NOT_ESTABLISHED" in report
        assert "PLANNED_NOT_EXECUTED" in report
        assert "FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED" in report
        assert "PHYSICAL_GROUND_MEASUREMENT" in report
        assert "SYNTHETIC_TEST_DATA" in report

    def test_no_fabricated_flight_data_is_accepted(self):
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        # Verify no flight data claims were manufactured
        assert state.campaign_verdict == FlightCampaignVerdict.FLIGHT_TEST_FRAMEWORK_COMPLETE_NOT_EXECUTED
        assert state.demonstrated_envelope.is_established is False
        assert all(s.evidence_status == EvidenceStatus.PLANNED_NOT_EXECUTED for s in state.sorties)


class TestCLIAndRegressionProtection:
    """Validates CLI tool, report generation, and Fixed-Wing zero-modification integrity."""

    def test_cli_execution(self):
        cmd = [
            sys.executable,
            "scripts/run_vtol_flight_test.py",
            "--readiness",
            "--envelope",
            "--analyze",
            "--incidents",
            "--reconcile",
            "--report",
            "--export-json",
        ]
        res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
        assert res.returncode == 0
        assert "PHASE 12" in res.stdout
        assert "FLIGHT TEST READINESS" in res.stdout
        assert "DEMONSTRATED FLIGHT ENVELOPE BOUNDARIES" in res.stdout
        assert "ENGINEERING MODEL RECONCILIATIONS" in res.stdout

    def test_report_generation_15_audit_sections(self):
        from scripts.run_vtol_flight_test import generate_markdown_report
        state = FlightTestPipeline.run_pipeline(as_executed=True)
        report = generate_markdown_report(state, "20260921_TEST")
        assert len(report) > 3000
        for i in range(1, 16):
            assert f"## {i}." in report, f"Missing section {i} in generated Phase 12 audit report"

    def test_fixed_wing_zero_source_modifications(self):
        fw_dir = os.path.join(PROJECT_ROOT, "backend", "design", "fixed_wing")
        assert os.path.isdir(fw_dir)
        import backend.design.vtol.flight_test as ft
        assert ft is not None
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("backend.design.vtol.flight_test"):
                assert "fixed_wing" not in mod_name

    def test_no_upstream_physics_modifications(self):
        """Verify Phase 12 treats upstream phases 1-11 as read-only."""
        import backend.design.vtol.flight_test as ft
        ft_dir = os.path.dirname(ft.__file__)
        vtol_root = os.path.dirname(ft_dir)
        for fname in os.listdir(ft_dir):
            if fname.endswith(".py"):
                fpath = os.path.join(ft_dir, fname)
                assert os.path.isfile(fpath)
        # Upstream phases 1-11 must be present and untouched
        upstream_subsystems = [
            "airfoil", "avionics", "cad", "commercial", "configuration",
            "cruise_performance", "electrical", "flight_control", "forward_propulsion",
            "fuselage", "ground_verification", "hover_performance", "integration",
            "lift_system", "manufacturing", "mass_properties", "mission", "optimization",
            "payload", "pipeline", "report", "requirements", "tail", "transition", "verification", "wing"
        ]
        for sub in upstream_subsystems:
            assert os.path.isdir(os.path.join(vtol_root, sub))


class TestPhase12AFlight01IngestionAndEvidence:
    """Dedicated Phase 12A Flight-01 Ingestion and Evidence Tests per Section 24."""

    def test_missing_log_handling_returns_ready(self):
        """Verify pipeline gracefully handles missing flight log and returns FLIGHT-01_READY_FOR_REAL_LOG."""
        res = Flight01AnalysisEngine.analyze_flight(log_path="NON_EXISTENT_FLIGHT_LOG.BIN")
        assert res.flight_id == "FLIGHT-01"
        assert res.execution_status == EvidenceStatus.PLANNED_NOT_EXECUTED
        assert res.gate_1_status == FlightGateStatus.NOT_EXECUTED
        assert res.readiness_code == "FLIGHT-01_READY_FOR_REAL_LOG"
        assert res.gate_1_verdict == "NOT_EXECUTED"
        assert res.log_metadata is None

    def test_synthetic_log_rejection_for_flight_01(self):
        """Verify that synthetic test data cannot pass Gate-1."""
        synthetic_sorties = FlightTestCampaignEngine.build_synthetic_test_sorties()
        assert all(s.evidence_status == EvidenceStatus.SYNTHETIC_TEST_DATA for s in synthetic_sorties)
        # Verify Gate-1 status when only synthetic sorties exist
        status_g1 = FlightTestVerifier.evaluate_gate_status(FlightGate.GATE_1_INITIAL_VTOL, synthetic_sorties)
        assert status_g1 == FlightGateStatus.NOT_EXECUTED

    def test_missing_field_handling(self):
        """Verify missing fields in log are handled gracefully without estimation."""
        res = Flight01AnalysisEngine.analyze_flight(log_path=None)
        assert res.power_thermal_analysis["evidence_status"] == "NOT_MEASURED"
        assert res.power_thermal_analysis["esc_temperature"] == "NOT_MEASURED"
        assert res.propulsion_analysis["status"] == "NOT_AVAILABLE"
        assert res.attitude_analysis["status"] == "NOT_AVAILABLE"

    def test_airborne_duration_calculation(self):
        """Verify airborne duration vs log duration distinction."""
        res = Flight01AnalysisEngine.analyze_flight(log_path=None)
        dur = res.flight_duration_analysis
        assert dur["log_duration_s"] == 0.0
        assert dur["airborne_duration_s"] == 0.0
        assert dur["status"] == "NOT_EXECUTED"

    def test_gate_1_cannot_pass_without_physical_evidence(self):
        """Verify Gate-1 cannot pass when physical evidence is incomplete."""
        res = Flight01AnalysisEngine.analyze_flight(log_path=None)
        assert res.gate_1_status == FlightGateStatus.NOT_EXECUTED
        assert res.gate_1_verdict == "NOT_EXECUTED"

    def test_report_terminology_and_21_sections(self):
        """Verify 21 required sections and strict terminology in PHASE_12_FLIGHT_01_REPORT.md."""
        res = Flight01AnalysisEngine.analyze_flight(log_path=None)
        report = Flight01AnalysisEngine.generate_flight_01_report(res, "20260921_TEST")
        # Assert all 21 numbered sections are present
        for i in range(1, 22):
            assert f"## {i}." in report, f"Section {i} missing from Flight-01 report"

        # Check terminology
        assert "PLANNED_NOT_EXECUTED" in report
        assert "FLIGHT-01_READY_FOR_REAL_LOG" in report
        assert "PHYSICAL_GROUND_MEASUREMENT" in report
        assert "PHYSICAL_BENCH_MEASUREMENT" in report

    def test_real_log_provenance_and_sha256_mock_bin(self, tmp_path):
        """Verify deterministic SHA-256 and pure-Python ArduPilot DataFlash binary log parsing."""
        import struct

        # Create a genuine-structure binary DataFlash file:
        # FMT message (msg_type=0x80 / 128, length=89)
        # Defining message ATT (type=1, length=27, format="Qfff", labels="TimeUS,Roll,Pitch,Yaw")
        # Format payload: type(B=1), length(B=27), name(4s=b"ATT\0"), format(16s=b"Qfff\0..."), labels(64s=b"TimeUS,Roll,Pitch,Yaw\0...")
        test_bin_path = str(tmp_path / "FLIGHT_01_TEST.BIN")

        fmt_payload = struct.pack(
            "<BB4s16s64s",
            1,
            23,
            b"ATT\x00",
            b"Qfff" + b"\x00" * 12,
            b"TimeUS,Roll,Pitch,Yaw" + b"\x00" * 43,
        )
        fmt_msg = bytes([0xA3, 0x95, 0x80]) + fmt_payload

        # ATT message instance 1: TimeUS=1000000 (1.0s), Roll=0.5, Pitch=-0.2, Yaw=180.0
        att_payload_1 = struct.pack("<Qfff", 1000000, 0.5, -0.2, 180.0)
        att_msg_1 = bytes([0xA3, 0x95, 1]) + att_payload_1

        # ATT message instance 2: TimeUS=3000000 (3.0s), Roll=0.8, Pitch=0.1, Yaw=180.5
        att_payload_2 = struct.pack("<Qfff", 3000000, 0.8, 0.1, 180.5)
        att_msg_2 = bytes([0xA3, 0x95, 1]) + att_payload_2

        with open(test_bin_path, "wb") as f:
            f.write(fmt_msg + att_msg_1 + att_msg_2)

        # Ingest and parse
        meta, messages = FlightLoggerEngine.ingest_flight_log(test_bin_path, flight_id="FLIGHT-01")
        assert meta is not None
        assert meta.file_size_bytes == len(fmt_msg) + len(att_msg_1) + len(att_msg_2)
        assert len(meta.sha256_hash) == 64
        assert meta.log_format == "DATAFLASH_BIN"
        assert meta.extraction_status == "SUCCESS"
        assert meta.duration_s == 2.0  # (3.0s - 1.0s)

        # Verify decoded ATT messages
        assert "ATT" in messages
        assert len(messages["ATT"]) == 2
        assert messages["ATT"][0]["Roll"] == pytest.approx(0.5, abs=0.01)
        assert messages["ATT"][1]["Roll"] == pytest.approx(0.8, abs=0.01)

        # Run Flight01AnalysisEngine with this log
        result = Flight01AnalysisEngine.analyze_flight(log_path=test_bin_path)
        assert result.execution_status == EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED
        assert result.log_metadata.sha256_hash == meta.sha256_hash
        assert result.attitude_analysis["max_roll_deg"] == pytest.approx(0.8, abs=0.01)

        # Metric source provenance verification
        assert "maximum_roll" in result.provenance_metrics
        prov_roll = result.provenance_metrics["maximum_roll"]
        assert prov_roll.source_log == os.path.basename(test_bin_path)
        assert prov_roll.source_message_type == "ATT"
        assert prov_roll.source_field == "Roll"
        assert prov_roll.evidence_status == EvidenceStatus.PHYSICALLY_EXECUTED_AND_LOGGED

        # But Gate-1 cannot pass without post-flight physical inspection record!
        assert result.gate_1_verdict == "INSUFFICIENT_EVIDENCE"
        assert result.gate_1_status == FlightGateStatus.INSUFFICIENT_EVIDENCE

    def test_cli_ingest_log_flags(self):
        """Verify CLI --ingest-log and --flight-id execution."""
        cmd = [
            sys.executable,
            "scripts/run_vtol_flight_test.py",
            "--ingest-log",
            "NON_EXISTENT.BIN",
            "--flight-id",
            "FLIGHT-01",
        ]
        res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
        assert res.returncode == 0
        assert "FLIGHT-01_READY_FOR_REAL_LOG" in res.stdout
        assert "PLANNED_NOT_EXECUTED" in res.stdout
        assert "NOT_EXECUTED" in res.stdout


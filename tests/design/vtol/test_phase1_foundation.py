"""
Phase 1 Foundation & Architecture Verification Test Suite for TorqWings VTOL Studio.

Tests:
    Test A: Requirement construction (VTOLRequirementModel typed creation and inheritance).
    Test B: Configuration construction (VTOLConfiguration for QuadPlane/Lift+Cruise).
    Test C: QuadPlane configuration propagation through ConfigurationEngine.
    Test D: Mission-state sequence (VTOLMissionProfileSequence 10-phase sequence validation).
    Test E: Pipeline requirement -> configuration propagation through VTOLDesignPipeline.
    Test F: Fixed-Wing adapter/interface invocation without code duplication.
    Test G: Architectural verification: No Fixed-Wing code duplication in backend/design/vtol.
    Test H: PipelineResult structure (explicit status tracking: IMPLEMENTED vs NOT_IMPLEMENTED_YET).
    Test I: JSON serialization (recursive to_dict and json.dumps roundtrip, no empty dicts).
    Test J: Dedicated runner execution path (run_vtol_pipeline dry-run).
    Test K: Invalid requirement handling (zero payload, negative range, None).
"""

import json
import subprocess
import sys
import os
import pytest

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode

from backend.design.vtol.mission.mission_requirements import (
    VTOLType,
    VTOLMissionCategory,
    MissionRequirements,
)
from backend.design.vtol.mission.mission_state import (
    VTOLMissionPhase,
    VTOLMissionSegment,
    VTOLMissionProfileSequence,
)
from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel
from backend.design.vtol.configuration.vtol_configuration import VTOLConfiguration
from backend.design.vtol.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.vtol.configuration.configuration_engine import ConfigurationEngine
from backend.design.vtol.fixed_wing_interface import (
    FixedWingEngineeringAdapter,
    FixedWingSubsystemResult,
)
from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline
from backend.design.vtol.pipeline.pipeline_result import (
    VTOLDesignResult,
    PipelineStatus,
    to_dict_recursive,
)

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestPhase1Foundation:
    """Phase 1 VTOL Foundation & Architecture Test Suite."""

    def test_a_requirement_construction(self):
        """Test A: Requirement construction and inheritance from RequirementModel."""
        req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.5,
            target_range=50.0,
            target_flight_time=45.0,
            cruise_speed=95.0,
            vtol_type=VTOLType.LIFT_CRUISE,
            hover_duration_min=6.0,
            transition_speed_kmh=70.0,
            lift_motor_count=4,
            cruise_motor_count=1,
            takeoff_type=TakeoffType.VERTICAL,
            landing_type=LandingType.VERTICAL,
            environment=OperatingEnvironment.RURAL,
            optimization_priority=OptimizationPriority.BALANCED,
            design_mode=DesignMode.MANUAL,
        )

        assert isinstance(req, RequirementModel)
        assert req.aircraft_type == AircraftType.VTOL
        assert req.payload_weight_kg == 2.5
        assert req.payload_mass == 2.5
        assert req.target_range_km == 50.0
        assert req.target_range == 50.0
        assert req.target_flight_time_min == 45.0
        assert req.target_flight_time == 45.0
        assert req.cruise_speed_kmh == 95.0
        assert req.cruise_speed == 95.0
        assert req.vtol_type == VTOLType.LIFT_CRUISE
        assert req.hover_duration_min == 6.0
        assert req.transition_speed_kmh == 70.0
        assert req.lift_motor_count == 4
        assert req.cruise_motor_count == 1

        # Test translation to MissionRequirements
        m_reqs = req.to_mission_requirements()
        assert isinstance(m_reqs, MissionRequirements)
        assert m_reqs.payload_kg == 2.5
        assert m_reqs.hover_reqs.hover_duration_min == 6.0
        assert m_reqs.transition_reqs.transition_speed_kmh == 70.0
        assert m_reqs.cruise_reqs.cruise_speed_kmh == 95.0

    def test_b_configuration_construction(self):
        """Test B: Configuration construction for QuadPlane / Lift+Cruise."""
        config = VTOLConfiguration.create_quadplane_default(motor_count=4)

        assert config.configuration_type == VTOLType.QUADPLANE
        assert config.lift_motor_count == 4
        assert config.lift_rotor_count == 4
        assert config.cruise_propulsion_count == 1
        assert "4_lift_plus_1_pusher" in config.propulsion_arrangement
        assert "High-wing" in config.wing_configuration
        assert "twin booms" in config.tail_configuration

        # Also test Lift+Cruise generic factory
        lc_config = VTOLConfiguration.create_lift_cruise_default(
            lift_motor_count=4,
            cruise_motor_count=1,
        )
        assert lc_config.configuration_type == VTOLType.LIFT_CRUISE
        assert lc_config.lift_motor_count == 4
        assert lc_config.cruise_propulsion_count == 1

    def test_c_quadplane_configuration_propagation(self):
        """Test C: Authoritative QuadPlane configuration attaches to ConfigurationResult."""
        req = VTOLRequirementModel.create(
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
            lift_motor_count=4,
            cruise_motor_count=1,
        )
        m_reqs = req.to_mission_requirements()
        from backend.design.vtol.mission.mission_engine import MissionEngine
        m_res = MissionEngine().process_mission(m_reqs)

        cfg_engine = ConfigurationEngine()
        cfg_res = cfg_engine.design_configuration(ConfigurationRequirements(mission_result=m_res))

        assert cfg_res.vtol_configuration is not None
        assert isinstance(cfg_res.vtol_configuration, VTOLConfiguration)
        assert cfg_res.vtol_configuration.lift_motor_count == 4
        assert cfg_res.vtol_configuration.cruise_propulsion_count == 1

    def test_d_mission_state_sequence(self):
        """Test D: Mission-state representation covers all 10 phases in correct sequence."""
        seq = VTOLMissionProfileSequence.build_default_sequence(
            hover_duration_min=5.0,
            transition_duration_s=15.0,
            cruise_endurance_min=30.0,
            cruise_speed_kmh=90.0,
            transition_speed_kmh=65.0,
        )

        assert len(seq.segments) == 10
        assert seq.validate_sequence()

        expected_phases = [
            VTOLMissionPhase.GROUND_PREFLIGHT,
            VTOLMissionPhase.VTOL_TAKEOFF,
            VTOLMissionPhase.HOVER_CLIMB,
            VTOLMissionPhase.TRANSITION_TO_CRUISE,
            VTOLMissionPhase.FIXED_WING_CRUISE,
            VTOLMissionPhase.MISSION_LOITER,
            VTOLMissionPhase.TRANSITION_TO_VTOL,
            VTOLMissionPhase.HOVER_DESCENT,
            VTOLMissionPhase.VTOL_LANDING,
            VTOLMissionPhase.GROUND_POSTFLIGHT,
        ]

        actual_phases = [s.phase for s in seq.segments]
        assert actual_phases == expected_phases

        # Verify segments carry typed fields without fake physics
        for seg in seq.segments:
            assert isinstance(seg.phase, VTOLMissionPhase)
            assert seg.duration_s > 0.0
            assert seg.propulsion_mode in ("OFF", "LIFT_ONLY", "BLENDED", "CRUISE_ONLY")

    def test_e_pipeline_requirement_propagation(self):
        """Test E: VTOLDesignPipeline propagates requirements and configuration cleanly."""
        pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, raise_on_failure=False)
        req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
            lift_motor_count=4,
            cruise_motor_count=1,
        )

        result = pipeline.execute(req)

        assert result.success is True
        assert result.status == PipelineStatus.SUCCESS
        assert result.specification is not None
        assert result.specification.vtol_configuration is not None
        assert result.specification.vtol_configuration.lift_motor_count == 4
        assert result.specification.vtol_configuration.cruise_propulsion_count == 1
        assert result.requirements is req

    def test_f_fixed_wing_adapter_invocation(self):
        """Test F: FixedWingEngineeringAdapter translates requirements and delegates to locked backend."""
        adapter = FixedWingEngineeringAdapter(raise_on_failure=False)
        vtol_req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )

        fw_req = adapter.translate_to_fixed_wing_requirements(vtol_req)
        assert fw_req.aircraft_type == AircraftType.FIXED_WING
        assert fw_req.payload_weight_kg == 2.0
        assert fw_req.target_range_km == 30.0
        assert fw_req.target_flight_time_min == 25.0
        assert fw_req.cruise_speed_kmh == 80.0
        assert fw_req.takeoff_type == TakeoffType.RUNWAY
        assert fw_req.landing_type == LandingType.RUNWAY

        fw_res = adapter.size_cruise_subsystems(vtol_req)
        assert isinstance(fw_res, FixedWingSubsystemResult)
        assert fw_res.status in ("SUCCESS", "PARTIAL")
        assert len(fw_res.notes) > 0

    def test_g_no_fixed_wing_code_duplication(self):
        """Test G: Confirms no Fixed-Wing source code was copied into backend/design/vtol/fixed_wing_interface."""
        adapter_file = os.path.join(
            WORKSPACE_ROOT, "backend", "design", "vtol", "fixed_wing_interface", "fixed_wing_adapter.py"
        )
        adapter_path = os.path.abspath(adapter_file)
        assert os.path.exists(adapter_path), f"Adapter file not found at {adapter_path}"

        with open(adapter_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Should import and delegate to fixed_wing, not duplicate equations
        assert "from backend.design.fixed_wing.pipeline.fixed_wing_design_pipeline import" in content
        # Must not contain copied wing sizing formula: e.g. Raymer taper ratio regressions or NACA 4-digit generators
        assert "def generate_naca_4digit" not in content
        assert "def raymer_wing_sizing" not in content

    def test_h_pipelineresult_structure_and_status(self):
        """Test H: PipelineResult structured stage status tracking (IMPLEMENTED vs NOT_IMPLEMENTED_YET)."""
        pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, raise_on_failure=False)
        req = VTOLRequirementModel.create(
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        result = pipeline.execute(req)

        spec = result.specification
        assert spec is not None
        assert spec.stage_statuses is not None
        assert spec.stage_statuses["requirements"] == "IMPLEMENTED"
        assert spec.stage_statuses["mission"] == "IMPLEMENTED"
        assert spec.stage_statuses["configuration"] == "IMPLEMENTED"
        assert spec.stage_statuses["fixed_wing_interface"] in ("SUCCESS", "PARTIAL")

        # Incomplete disciplines must be explicitly tracked as NOT_IMPLEMENTED_YET / IMPLEMENTED
        assert spec.stage_statuses["hover_physics"] in ("IMPLEMENTED", "NOT_IMPLEMENTED_YET")
        assert spec.stage_statuses["transition_physics"] in ("IMPLEMENTED", "NOT_IMPLEMENTED_YET")
        assert spec.stage_statuses["electrical_battery_sizing"] in ("IMPLEMENTED", "NOT_IMPLEMENTED_YET")
        assert spec.stage_statuses["mass_convergence"] in ("IMPLEMENTED", "NOT_IMPLEMENTED_YET")
        assert spec.stage_statuses["optimization"] == "NOT_IMPLEMENTED_YET"
        assert spec.stage_statuses["verification"] == "NOT_IMPLEMENTED_YET"

    def test_i_json_serialization(self):
        """Test I: Robust typed JSON serialization without empty dicts or serialization crashes."""
        pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, raise_on_failure=False)
        req = VTOLRequirementModel.create(
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        result = pipeline.execute(req)

        # Serialize via to_dict()
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["status"] == "SUCCESS"
        assert "final_specification" in data
        assert data["final_specification"]["mtow_kg"] > 0.0

        # json.dumps must succeed cleanly
        json_str = json.dumps(data)
        assert len(json_str) > 1000

        # Roundtrip parse check
        parsed = json.loads(json_str)
        assert parsed["final_specification"]["mtow_kg"] == data["final_specification"]["mtow_kg"]

    def test_j_runner_execution_path(self):
        """Test J: scripts/run_vtol_pipeline.py CLI non-interactive execution path."""
        runner_path = os.path.join(WORKSPACE_ROOT, "scripts", "run_vtol_pipeline.py")
        runner_path = os.path.abspath(runner_path)
        assert os.path.exists(runner_path)

        cmd = [
            sys.executable,
            runner_path,
            "--non-interactive",
            "--payload", "2.0",
            "--range", "30.0",
            "--endurance", "20.0",
            "--speed", "80.0",
            "--output-dir", "reports/test_phase1_run",
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"Runner failed with stdout: {proc.stdout}\nstderr: {proc.stderr}"
        assert "VTOL PIPELINE EXECUTION SUMMARY" in proc.stdout
        assert "SUCCESS" in proc.stdout

        # Verify exported files exist
        json_file = os.path.join("reports", "test_phase1_run", "vtol_specification.json")
        md_file = os.path.join("reports", "test_phase1_run", "vtol_engineering_report.md")
        assert os.path.exists(json_file)
        assert os.path.exists(md_file)

    def test_k_invalid_requirement_handling(self):
        """Test K: Invalid requirement values return INVALID_REQUIREMENTS."""
        pipeline = VTOLDesignPipeline(raise_on_failure=False)

        # None requirement
        res_none = pipeline.execute(None)
        assert res_none.success is False
        assert res_none.status == PipelineStatus.INVALID_REQUIREMENTS

        # Zero / negative payload
        req_bad_payload = VTOLRequirementModel.create(payload_mass=0.0)
        res_bad_p = pipeline.execute(req_bad_payload)
        assert res_bad_p.success is False
        assert res_bad_p.status == PipelineStatus.INVALID_REQUIREMENTS

        # Negative range
        req_bad_range = VTOLRequirementModel.create(payload_mass=2.0, target_range=-10.0)
        res_bad_r = pipeline.execute(req_bad_range)
        assert res_bad_r.success is False
        assert res_bad_r.status == PipelineStatus.INVALID_REQUIREMENTS

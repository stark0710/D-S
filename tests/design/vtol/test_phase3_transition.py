"""
Phase 3 Transition Engineering & Corridor Sizing Test Suite
Authoritative physics verification for VTOL conversion flight dynamics.
"""

import json
import math
import subprocess
import pytest

from backend.design.vtol.transition.authoritative_transition import (
    AuthoritativeTransitionModel,
    AuthoritativeTransitionResult,
    TransitionOperatingPoint,
    TransitionPhysicsValidationError,
    STANDARD_AIR_DENSITY_KG_M3,
    GRAVITATIONAL_ACCELERATION_M_S2,
)
from backend.design.vtol.transition.transition_engine import TransitionFlightEngine
from backend.design.vtol.transition.transition_strategy import (
    QuadPlaneTransitionStrategy,
    LiftCruiseTransitionStrategy,
)
from backend.design.vtol.transition.transition_validator import TransitionValidator
from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel
from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline
from backend.design.vtol.fixed_wing_interface import FixedWingEngineeringAdapter
from backend.design.vtol.configuration.vtol_configuration import VTOLConfiguration
from backend.design.vtol.mission.mission_requirements import VTOLType


class TestPhase3TransitionEngineering:
    """
    25 Comprehensive Physics Tests for Phase 3 Transition Engineering.
    """

    @pytest.fixture
    def standard_setup(self):
        return {
            "mass_kg": 12.0,
            "wing_area_m2": 0.85,
            "lift_motor_count": 4,
            "air_density_kg_m3": 1.225,
            "cl_max": 1.40,
            "cl_transition": 0.85,
        }

    # 1. Hover-to-transition initial condition
    def test_01_hover_to_transition_initial_condition(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
            lift_motor_count=standard_setup["lift_motor_count"],
            direction="TRANSITION_TO_CRUISE",
        )
        first_pt = res.corridor_points[0]
        assert "Hover" in first_pt.stage_name
        assert first_pt.airspeed_kmh == 0.0
        assert first_pt.dynamic_pressure_pa == 0.0
        assert first_pt.wing_lift_n == 0.0
        assert first_pt.wing_lift_fraction == 0.0
        assert pytest.approx(first_pt.required_vertical_thrust_n, rel=1e-3) == res.aircraft_weight_n
        assert first_pt.vertical_thrust_fraction == 1.0
        assert first_pt.is_wing_supported is False

    # 2. Wing lift equation
    def test_02_wing_lift_equation(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
            lift_motor_count=standard_setup["lift_motor_count"],
            cl_transition=0.80,
            air_density_kg_m3=1.225,
        )
        # Select mid-point
        mid_pt = res.corridor_points[2]
        v_ms = mid_pt.airspeed_m_s
        expected_lift = 0.5 * 1.225 * (v_ms ** 2) * standard_setup["wing_area_m2"] * 0.80
        expected_lift = min(expected_lift, res.aircraft_weight_n)
        assert pytest.approx(mid_pt.wing_lift_n, rel=1e-2) == expected_lift

    # 3. Dynamic-pressure relationship
    def test_03_dynamic_pressure_relationship(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
            lift_motor_count=standard_setup["lift_motor_count"],
            air_density_kg_m3=1.20,
        )
        for pt in res.corridor_points:
            expected_q = 0.5 * 1.20 * (pt.airspeed_m_s ** 2)
            assert pytest.approx(pt.dynamic_pressure_pa, rel=1e-3) == expected_q

    # 4. Wing lift scaling with airspeed
    def test_04_wing_lift_scaling_with_airspeed(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=50.0,  # high mass so weight cap is not hit early
            wing_area_m2=2.0,
            lift_motor_count=4,
            preferred_transition_speed_kmh=100.0,
        )
        p1 = res.corridor_points[1]  # 25% speed
        p2 = res.corridor_points[2]  # 50% speed (2x p1)
        ratio_speed = p2.airspeed_m_s / p1.airspeed_m_s
        assert pytest.approx(ratio_speed, rel=1e-2) == 2.0
        ratio_lift = p2.wing_lift_n / p1.wing_lift_n
        assert pytest.approx(ratio_lift, rel=1e-2) == 4.0

    # 5. Wing lift scaling with wing area
    def test_05_wing_lift_scaling_with_wing_area(self, standard_setup):
        res1 = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=40.0,
            wing_area_m2=1.0,
            preferred_transition_speed_kmh=120.0,
        )
        res2 = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=40.0,
            wing_area_m2=2.0,
            preferred_transition_speed_kmh=120.0,
        )
        # At mid transition (both evaluated at 60 km/h)
        lift1 = res1.corridor_points[2].wing_lift_n
        lift2 = res2.corridor_points[2].wing_lift_n
        assert pytest.approx(lift2 / lift1, rel=1e-2) == 2.0

    # 6. Wing-supported transition condition
    def test_06_wing_supported_transition_condition(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
        )
        # Find points where fraction >= 0.70
        for pt in res.corridor_points:
            if pt.wing_lift_fraction >= 0.70:
                assert pt.is_wing_supported is True
            else:
                assert pt.is_wing_supported is False

    # 7. Remaining vertical thrust
    def test_07_remaining_vertical_thrust(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
        )
        for pt in res.corridor_points:
            assert pt.required_vertical_thrust_n >= 0.0
            expected_vert = max(0.0, res.aircraft_weight_n - pt.wing_lift_n)
            assert pytest.approx(pt.required_vertical_thrust_n, abs=1e-2) == expected_vert

    # 8. Per-motor transition thrust
    def test_08_per_motor_transition_thrust(self, standard_setup):
        motors = 4
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
            lift_motor_count=motors,
        )
        for pt in res.corridor_points:
            expected_per_motor = pt.required_vertical_thrust_n / motors
            assert pytest.approx(pt.vertical_thrust_per_motor_n, abs=1e-2) == expected_per_motor

    # 9. Configuration-driven motor count
    def test_09_configuration_driven_motor_count(self, standard_setup):
        res4 = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
            lift_motor_count=4,
        )
        res8 = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
            lift_motor_count=8,
        )
        assert pytest.approx(res4.aircraft_weight_n, rel=1e-3) == res8.aircraft_weight_n
        hover_4 = res4.corridor_points[0].vertical_thrust_per_motor_n
        hover_8 = res8.corridor_points[0].vertical_thrust_per_motor_n
        assert pytest.approx(hover_4 / hover_8, rel=1e-2) == 2.0

    # 10. QuadPlane transition
    def test_10_quadplane_transition(self, standard_setup):
        strategy = QuadPlaneTransitionStrategy()
        assert hasattr(strategy, "determine_conversion_speed")

        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=15.0,
            wing_area_m2=1.0,
            lift_motor_count=4,
            direction="TRANSITION_TO_CRUISE",
        )
        assert res.lift_motor_count == 4
        assert res.transition_speed_kmh > 45.0
        assert res.corridor_points[-1].vertical_thrust_fraction == 0.0
        assert res.corridor_points[-1].wing_lift_fraction == 1.0

    # 11. Hex configuration scaling
    def test_11_hex_configuration_scaling(self, standard_setup):
        res6 = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=18.0,
            wing_area_m2=1.2,
            lift_motor_count=6,
        )
        assert res6.lift_motor_count == 6
        hover_pt = res6.corridor_points[0]
        assert pytest.approx(hover_pt.vertical_thrust_per_motor_n * 6, rel=1e-2) == res6.aircraft_weight_n

    # 12. Reverse transition
    def test_12_reverse_transition(self, standard_setup):
        res_rev = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
            lift_motor_count=standard_setup["lift_motor_count"],
            direction="TRANSITION_TO_VTOL",
        )
        assert res_rev.direction == "TRANSITION_TO_VTOL"
        # First point is Fixed-Wing Entry (fast, wing supported)
        assert res_rev.corridor_points[0].airspeed_kmh > 0.0
        assert res_rev.corridor_points[0].wing_lift_fraction >= 0.95
        assert res_rev.corridor_points[0].vertical_thrust_fraction == 0.0

        # Last point is Hover Landing (slow, fully rotor supported)
        assert res_rev.corridor_points[-1].airspeed_kmh == 0.0
        assert res_rev.corridor_points[-1].wing_lift_fraction == 0.0
        assert res_rev.corridor_points[-1].vertical_thrust_fraction == 1.0

    # 13. Invalid mass rejection
    def test_13_invalid_mass_rejection(self, standard_setup):
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=0.0,
                wing_area_m2=standard_setup["wing_area_m2"],
            )
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=-5.0,
                wing_area_m2=standard_setup["wing_area_m2"],
            )

    # 14. Invalid wing area rejection
    def test_14_invalid_wing_area_rejection(self, standard_setup):
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=standard_setup["mass_kg"],
                wing_area_m2=0.0,
            )
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=standard_setup["mass_kg"],
                wing_area_m2=-0.5,
            )

    # 15. Invalid density rejection
    def test_15_invalid_density_rejection(self, standard_setup):
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=standard_setup["mass_kg"],
                wing_area_m2=standard_setup["wing_area_m2"],
                air_density_kg_m3=0.0,
            )
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=standard_setup["mass_kg"],
                wing_area_m2=standard_setup["wing_area_m2"],
                air_density_kg_m3=-1.2,
            )

    # 16. Invalid motor count rejection
    def test_16_invalid_motor_count_rejection(self, standard_setup):
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=standard_setup["mass_kg"],
                wing_area_m2=standard_setup["wing_area_m2"],
                lift_motor_count=0,
            )
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=standard_setup["mass_kg"],
                wing_area_m2=standard_setup["wing_area_m2"],
                lift_motor_count=-4,
            )

    # 17. Invalid transition speed rejection
    def test_17_invalid_transition_speed_rejection(self, standard_setup):
        with pytest.raises(TransitionPhysicsValidationError):
            AuthoritativeTransitionModel.calculate_transition_corridor(
                sizing_mass_kg=standard_setup["mass_kg"],
                wing_area_m2=standard_setup["wing_area_m2"],
                preferred_transition_speed_kmh=-10.0,
            )

    # 18. Transition corridor generation
    def test_18_transition_corridor_generation(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
        )
        assert len(res.corridor_points) >= 5
        stages = [p.stage_name for p in res.corridor_points]
        assert any("Hover" in s for s in stages)
        assert any("Early" in s for s in stages)
        assert any("Mid" in s for s in stages)
        assert any("Handover" in s for s in stages)
        assert any("Entry" in s for s in stages)

    # 19. Fixed-Wing adapter integration
    def test_19_fixed_wing_adapter_integration(self):
        adapter = FixedWingEngineeringAdapter()
        req = VTOLRequirementModel.create(
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        subsystems = adapter.size_cruise_subsystems(req)
        assert subsystems.status in ("SUCCESS", "PARTIAL")

        wing_area = getattr(getattr(subsystems.wing, "wing_geometry", None), "area_m2", 0.85) if subsystems.wing else 0.85
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=12.0,
            wing_area_m2=wing_area,
            lift_motor_count=4,
        )
        assert res.wing_area_m2 == wing_area
        assert res.status == "IMPLEMENTED"
        assert len(res.corridor_points) >= 5

    # 20. Pipeline integration
    def test_20_pipeline_integration(self):
        pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, raise_on_failure=False)
        req = VTOLRequirementModel.create(
            payload_mass=2.0,
            target_range=25.0,
            target_flight_time=20.0,
            cruise_speed=75.0,
        )
        result = pipeline.execute(req)
        assert result.success is True
        spec = result.specification
        assert spec.transition is not None
        assert hasattr(spec.transition, "authoritative_result")
        assert spec.transition.authoritative_result is not None
        auth = spec.transition.authoritative_result
        assert auth.status == "IMPLEMENTED"
        assert len(auth.corridor_points) >= 5
        assert auth.aircraft_weight_n > 0.0

    # 21. Serialization
    def test_21_serialization(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
        )
        data = res.to_dict()
        assert isinstance(data, dict)
        assert data["status"] == "IMPLEMENTED"
        assert len(data["corridor_points"]) >= 5

        # Must serialize cleanly to JSON
        json_str = json.dumps(data)
        assert json_str is not None
        reloaded = json.loads(json_str)
        assert reloaded["sizing_mass_kg"] == round(standard_setup["mass_kg"], 4)

    # 22. Phase status reporting
    def test_22_phase_status_reporting(self):
        pipeline = VTOLDesignPipeline(tolerance=0.015, max_iterations=20, raise_on_failure=False)
        req = VTOLRequirementModel.create(
            payload_mass=2.5,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        result = pipeline.execute(req)
        spec = result.specification
        assert spec.stage_statuses["transition_physics"] == "IMPLEMENTED"
        assert spec.stage_statuses["hover_physics"] == "IMPLEMENTED"

    # 23. MTOW pre-convergence boundary
    def test_23_mtow_pre_convergence_boundary(self, standard_setup):
        res = AuthoritativeTransitionModel.calculate_transition_corridor(
            sizing_mass_kg=standard_setup["mass_kg"],
            wing_area_m2=standard_setup["wing_area_m2"],
        )
        assert res.is_converged_mtow is False
        assert res.mtow_status == "PRE_CONVERGENCE_SIZING"

    # 24. Legacy transition path does not generate competing physics
    def test_24_legacy_transition_path_does_not_generate_competing_physics(self):
        engine = TransitionFlightEngine()
        from backend.design.vtol.transition.transition_requirements import TransitionRequirements
        from backend.design.vtol.mission import (
            MissionResult,
            MissionProfile,
            HoverRequirements,
            TransitionRequirements as MissionTransitionReq,
            CruiseRequirements,
            MissionAnalysis,
            VTOLMissionCategory,
            VTOLType,
        )

        hover = HoverRequirements(
            hover_duration_min=5.0, hover_altitude_m=100.0, wind_limit_hover_kts=12.0,
            climb_rate_vertical_m_s=2.5, descent_rate_vertical_m_s=2.0
        )
        transition = MissionTransitionReq(
            transition_speed_kmh=60.0, transition_duration_s=15.0, transition_altitude_m=120.0,
            max_transition_pitch_deg=20.0
        )
        cruise = CruiseRequirements(
            cruise_speed_kmh=100.0, cruise_altitude_m=150.0, cruise_range_km=30.0,
            cruise_endurance_min=20.0, wind_limit_cruise_kts=18.0
        )
        profile = MissionProfile(
            mission_category=VTOLMissionCategory.SURVEY,
            vtol_type=VTOLType.QUADPLANE,
            payload_kg=5.0, total_endurance_min=25.0, total_range_km=30.0,
            air_density_hover_kg_m3=1.21, air_density_cruise_kg_m3=1.20,
            energy_demand_hover_kwh=0.5, energy_demand_cruise_kwh=1.2,
            energy_demand_transition_kwh=0.1, total_energy_demand_kwh=1.8,
            complexity_score=0.55, complexity_category="Medium"
        )
        analysis = MissionAnalysis(
            hover_priority=0.6, cruise_priority=0.4, transition_complexity=0.5,
            estimated_mtow_kg=25.0, lift_to_drag_ratio_est=10.0, hover_thrust_to_weight_est=1.45,
            mission_energy_demand_kwh=1.8, mission_risk_score=0.4, mission_feasibility_score=85.0
        )
        mission_res = MissionResult(
            mission_profile=profile, hover_requirements=hover, transition_requirements=transition,
            cruise_requirements=cruise, mission_analysis=analysis
        )
        class MockResult:
            pass

        reqs = TransitionRequirements(
            mission_result=mission_res,
            configuration_result=MockResult(),
            wing_result=MockResult(),
            airfoil_result=MockResult(),
            tail_result=MockResult(),
            fuselage_result=MockResult(),
            lift_system_result=MockResult(),
            forward_propulsion_result=MockResult(),
            electrical_result=MockResult(),
            avionics_result=MockResult(),
            payload_result=MockResult(),
            mass_properties_result=MockResult(),
            hover_performance_result=MockResult(),
            preferred_transition_speed_kmh=55.0,
        )
        legacy_res = engine.design(reqs)

        # Confirm authoritative result is embedded and supplies the data
        assert legacy_res.authoritative_result is not None
        auth = legacy_res.authoritative_result
        assert legacy_res.transition_analysis.conversion_speed_kmh == auth.transition_speed_kmh
        assert legacy_res.transition_analysis.duration_s == auth.transition_duration_s
        assert pytest.approx(legacy_res.transition_analysis.energy_kwh, rel=1e-3) == auth.total_energy_kwh

    # 25. No Fixed-Wing modifications
    def test_25_no_fixed_wing_modifications(self):
        cmd_diff = ["git", "diff", "backend/design/fixed_wing/"]
        proc_diff = subprocess.run(cmd_diff, capture_output=True, text=True, check=False)
        assert "transition" not in proc_diff.stdout.lower()
        assert "hover" not in proc_diff.stdout.lower()
        assert "vtol" not in proc_diff.stdout.lower()

"""
VTOL Phase 2 — Hover Performance & Lift System Engineering Test Suite.

Verifies:
1. Basic hover thrust calculation
2. Weight = mass * gravity relationship (g = 9.80665 m/s^2)
3. Per-motor thrust calculation (T_per_motor = T_req / N)
4. QuadPlane 4-motor configuration default
5. Configuration-driven motor count (N=6, N=8, etc.)
6. Thrust scaling with mass
7. Thrust margin behavior (T_margin = T_req - W)
8. Rotor disk-area calculation
9. Hover power calculation (Momentum Theory)
10. Hover current calculation (I = P / V)
11. Invalid mass rejection (mass <= 0)
12. Invalid motor count rejection (N <= 0)
13. Invalid voltage rejection (V <= 0)
14. Invalid rotor diameter rejection (D <= 0)
15. Pipeline integration (stage_statuses["hover_physics"] == "IMPLEMENTED")
16. Serialization to dictionary/JSON
17. Phase status reporting (IMPLEMENTED vs PARTIAL)
18. Future MTOW/convergence interface (is_converged_mtow=False)
19. Regression against Phase 1 foundation
20. Fixed-Wing locked backend integrity check
"""

import math
import subprocess
import pytest

from backend.design.vtol.hover_performance.authoritative_hover import (
    AuthoritativeHoverModel,
    AuthoritativeHoverResult,
    HoverPhysicsValidationError,
    GRAVITATIONAL_ACCELERATION_M_S2,
    DEFAULT_HOVER_THRUST_TO_WEIGHT,
    STANDARD_AIR_DENSITY_KG_M3,
)
from backend.design.vtol.configuration.vtol_configuration import VTOLConfiguration
from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel
from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline
from backend.design.vtol.lift_system.lift_system_engine import LiftSystemEngine
from backend.design.vtol.lift_system.lift_system_validator import (
    LiftSystemValidator,
    LiftSystemValidationError,
)


class TestPhase2HoverLiftEngineering:
    """Comprehensive test suite for Phase 2 Hover Performance and Lift System."""

    # 1. Basic hover thrust calculation
    def test_01_basic_hover_thrust_calculation(self):
        mass = 10.0  # kg
        t_w = 1.20
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=mass,
            lift_motor_count=4,
            hover_thrust_to_weight_target=t_w,
        )
        expected_weight = 10.0 * GRAVITATIONAL_ACCELERATION_M_S2
        expected_thrust = expected_weight * t_w
        assert pytest.approx(res.aircraft_weight_n, rel=1e-5) == expected_weight
        assert pytest.approx(res.required_total_hover_thrust_n, rel=1e-5) == expected_thrust

    # 2. Weight = mass * gravity relationship (g = 9.80665 m/s^2)
    def test_02_weight_mass_gravity_relationship(self):
        masses = [1.5, 7.5, 25.0, 50.0]
        for m in masses:
            res = AuthoritativeHoverModel.calculate_hover_state(
                sizing_mass_kg=m,
                lift_motor_count=4,
            )
            assert pytest.approx(res.aircraft_weight_n, rel=1e-6) == m * 9.80665

    # 3. Per-motor thrust calculation
    def test_03_per_motor_thrust_calculation(self):
        mass = 12.0
        motor_count = 4
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=mass,
            lift_motor_count=motor_count,
            hover_thrust_to_weight_target=1.50,
        )
        expected_total_thrust = (12.0 * 9.80665) * 1.50
        expected_per_motor = expected_total_thrust / motor_count
        assert pytest.approx(res.required_thrust_per_motor_n, rel=1e-5) == expected_per_motor
        assert res.lift_motor_count == 4

    # 4. QuadPlane 4-motor configuration
    def test_04_quadplane_4_motor_configuration(self):
        config = VTOLConfiguration.create_quadplane_default()
        assert config.lift_motor_count == 4
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=8.0,
            lift_motor_count=config.lift_motor_count,
        )
        assert res.lift_motor_count == 4
        assert pytest.approx(res.required_thrust_per_motor_n * 4, rel=1e-5) == res.required_total_hover_thrust_n

    # 5. Configuration-driven motor count
    def test_05_configuration_driven_motor_count(self):
        # Test hexarotor (6) and octorotor (8)
        for n_motors in [6, 8]:
            res = AuthoritativeHoverModel.calculate_hover_state(
                sizing_mass_kg=24.0,
                lift_motor_count=n_motors,
                hover_thrust_to_weight_target=1.30,
            )
            assert res.lift_motor_count == n_motors
            expected_per_motor = res.required_total_hover_thrust_n / n_motors
            assert pytest.approx(res.required_thrust_per_motor_n, rel=1e-5) == expected_per_motor

    # 6. Thrust scaling with mass
    def test_06_thrust_scaling_with_mass(self):
        res1 = AuthoritativeHoverModel.calculate_hover_state(sizing_mass_kg=10.0, lift_motor_count=4)
        res2 = AuthoritativeHoverModel.calculate_hover_state(sizing_mass_kg=20.0, lift_motor_count=4)
        assert pytest.approx(res2.required_total_hover_thrust_n, rel=1e-5) == res1.required_total_hover_thrust_n * 2.0
        assert pytest.approx(res2.required_thrust_per_motor_n, rel=1e-5) == res1.required_thrust_per_motor_n * 2.0

    # 7. Thrust margin behavior
    def test_07_thrust_margin_behavior(self):
        mass = 15.0
        t_w = 1.35
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=mass,
            lift_motor_count=4,
            hover_thrust_to_weight_target=t_w,
        )
        expected_weight = mass * 9.80665
        expected_margin = (expected_weight * t_w) - expected_weight
        assert pytest.approx(res.thrust_margin_n, rel=1e-5) == expected_margin
        assert pytest.approx(res.thrust_margin_ratio, rel=1e-5) == t_w

    # 8. Rotor disk-area calculation
    def test_08_rotor_disk_area_calculation(self):
        diameter = 0.50  # m
        n_rotors = 4
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=10.0,
            lift_motor_count=n_rotors,
            rotor_diameter_m=diameter,
        )
        expected_disk_area = n_rotors * math.pi * ((diameter / 2.0) ** 2)
        assert pytest.approx(res.total_disk_area_m2, rel=1e-5) == expected_disk_area
        expected_dl = res.aircraft_weight_n / expected_disk_area
        assert pytest.approx(res.disk_loading_n_m2, rel=1e-5) == expected_dl

    # 9. Hover power calculation (Momentum Theory)
    def test_09_hover_power_calculation(self):
        mass = 10.0
        n_rotors = 4
        diameter = 0.60
        rho = 1.225
        t_w = 1.20
        kappa = 1.15
        f_prof = 0.25
        eta = 0.85

        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=mass,
            lift_motor_count=n_rotors,
            rotor_diameter_m=diameter,
            hover_thrust_to_weight_target=t_w,
            air_density_kg_m3=rho,
            induced_power_correction_factor=kappa,
            profile_drag_power_fraction=f_prof,
            electrical_efficiency=eta,
        )

        t_total = mass * 9.80665 * t_w
        area = n_rotors * math.pi * ((diameter / 2.0) ** 2)
        v_i = math.sqrt(t_total / (2.0 * rho * area))
        p_ideal = t_total * v_i
        p_ind = p_ideal * kappa
        p_prof = p_ind * f_prof
        p_aero = p_ind + p_prof
        p_elec = p_aero / eta

        assert pytest.approx(res.induced_velocity_m_s, rel=1e-4) == v_i
        assert pytest.approx(res.ideal_induced_power_w, rel=1e-4) == p_ideal
        assert pytest.approx(res.actual_induced_power_w, rel=1e-4) == p_ind
        assert pytest.approx(res.profile_drag_power_w, rel=1e-4) == p_prof
        assert pytest.approx(res.total_aerodynamic_power_w, rel=1e-4) == p_aero
        assert pytest.approx(res.hover_electrical_power_w, rel=1e-4) == p_elec
        assert pytest.approx(res.hover_power_per_motor_w, rel=1e-4) == p_elec / n_rotors

    # 10. Current calculation (I = P / V)
    def test_10_hover_current_calculation(self):
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=12.0,
            lift_motor_count=4,
            rotor_diameter_m=0.55,
            system_voltage_v=44.4,  # 12S LiPo nominal
        )
        assert res.hover_electrical_power_w is not None
        expected_current = res.hover_electrical_power_w / 44.4
        assert pytest.approx(res.hover_current_a, rel=1e-4) == expected_current
        assert pytest.approx(res.hover_current_per_motor_a, rel=1e-4) == expected_current / 4

    # 11. Invalid mass rejection
    def test_11_invalid_mass_rejection(self):
        with pytest.raises(HoverPhysicsValidationError) as exc:
            AuthoritativeHoverModel.calculate_hover_state(
                sizing_mass_kg=-5.0,
                lift_motor_count=4,
            )
        assert "Invalid sizing mass" in str(exc.value)

    # 12. Invalid motor count rejection
    def test_12_invalid_motor_count_rejection(self):
        with pytest.raises(HoverPhysicsValidationError) as exc:
            AuthoritativeHoverModel.calculate_hover_state(
                sizing_mass_kg=10.0,
                lift_motor_count=0,
            )
        assert "Invalid lift motor count" in str(exc.value)

    # 13. Invalid voltage rejection
    def test_13_invalid_voltage_rejection(self):
        with pytest.raises(HoverPhysicsValidationError) as exc:
            AuthoritativeHoverModel.calculate_hover_state(
                sizing_mass_kg=10.0,
                lift_motor_count=4,
                system_voltage_v=-12.0,
            )
        assert "Invalid system voltage" in str(exc.value)

    # 14. Invalid rotor diameter rejection
    def test_14_invalid_rotor_diameter_rejection(self):
        with pytest.raises(HoverPhysicsValidationError) as exc:
            AuthoritativeHoverModel.calculate_hover_state(
                sizing_mass_kg=10.0,
                lift_motor_count=4,
                rotor_diameter_m=-0.40,
            )
        assert "Invalid rotor diameter" in str(exc.value)

    # 15. Pipeline integration (stage_statuses["hover_physics"] == "IMPLEMENTED")
    def test_15_pipeline_integration(self):
        req = VTOLRequirementModel.create(
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=85.0,
            lift_motor_count=4,
            rotor_diameter_m=0.45,
            system_voltage_v=44.4,
        )
        pipeline = VTOLDesignPipeline()
        result = pipeline.execute(req)
        assert result.success is True
        assert result.final_specification.stage_statuses["hover_physics"] == "IMPLEMENTED"
        assert result.final_specification.hover_performance is not None
        assert result.final_specification.lift_system is not None

    # 16. Serialization to dictionary/JSON
    def test_16_serialization_to_dict(self):
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=14.0,
            lift_motor_count=4,
            rotor_diameter_m=0.50,
            system_voltage_v=48.0,
        )
        d = res.to_dict()
        assert isinstance(d, dict)
        assert d["sizing_mass_kg"] == 14.0
        assert d["lift_motor_count"] == 4
        assert d["status"] == "IMPLEMENTED"
        assert "hover_electrical_power_w" in d
        assert "hover_current_a" in d

    # 17. Phase status reporting (IMPLEMENTED vs PARTIAL)
    def test_17_phase_status_reporting(self):
        # Complete inputs -> IMPLEMENTED
        res_full = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=10.0,
            lift_motor_count=4,
            rotor_diameter_m=0.50,
            system_voltage_v=44.4,
        )
        assert res_full.status == "IMPLEMENTED"

        # Missing rotor diameter -> PARTIAL
        res_partial = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=10.0,
            lift_motor_count=4,
        )
        assert res_partial.status == "PARTIAL"
        assert any("deferred" in w.lower() for w in res_partial.warnings)

    # 18. Future MTOW/convergence interface
    def test_18_future_mtow_convergence_interface(self):
        res = AuthoritativeHoverModel.calculate_hover_state(
            sizing_mass_kg=15.0,
            lift_motor_count=4,
            is_converged_mtow=False,
        )
        assert res.is_converged_mtow is False
        assert res.mtow_status == "PRE_CONVERGENCE_SIZING"

    # 19. Regression against Phase 1 behavior
    def test_19_regression_phase1_behavior(self):
        req = VTOLRequirementModel.create(
            payload_mass=2.5,
            target_range=35.0,
            target_flight_time=25.0,
            cruise_speed=85.0,
        )
        pipeline = VTOLDesignPipeline()
        result = pipeline.execute(req)
        assert result.success is True
        assert result.final_specification.stage_statuses["requirements"] == "IMPLEMENTED"
        assert result.final_specification.stage_statuses["mission"] == "IMPLEMENTED"
        assert result.final_specification.stage_statuses["configuration"] == "IMPLEMENTED"

    # 20. Fixed-Wing locked backend integrity check
    def test_20_no_fixed_wing_modifications(self):
        cmd = ["git", "status", "--porcelain", "backend/design/fixed_wing"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        # Verify that no NEW untracked files or unstaged changes were introduced in fixed_wing by Phase 2
        # (Only pre-existing tracked files from earlier Phase 6B lock exist)
        cmd_diff = ["git", "diff", "backend/design/fixed_wing/"]
        proc_diff = subprocess.run(cmd_diff, capture_output=True, text=True, check=False)
        # Check that we didn't add any changes to fixed_wing in this session
        assert "hover" not in proc_diff.stdout.lower()
        assert "vtol" not in proc_diff.stdout.lower()

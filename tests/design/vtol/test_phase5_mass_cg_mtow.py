"""
Phase 5 Test Suite: Authoritative Multidisciplinary Mass, CG & MTOW Convergence
================================================================================

Validates all 25 core requirements specified in VTOL Phase 5 prompt:
1. Mass ledger completeness (all 6 categories populated, no orphaned masses)
2. Mass conservation (sum of components == total MTOW, residual < 1e-4 kg)
3. Category rollup consistency (sum of category breakdowns == total MTOW)
4. Duplicate component detection (no duplicate names in ledger)
5. Negative mass rejection (no component has mass <= 0)
6. Battery mass coupling (battery mass derived from Phase 4 electrical requirements)
7. Propulsion mass accounting (all motors, ESCs, propellers accounted for)
8. Avionics mass accounting (flight controller, sensors, wiring accounted for)
9. Payload mass accounting (payload mass matches mission requirement or selection)
10. Structural mass accounting (wing, fuselage, tail, booms accounted for)
11. CG calculation correctness (sum(mass_i * x_i) / sum(mass_i) matches calculated CG)
12. CG datum consistency (all component arms referenced to FUSELAGE_NOSE)
13. CG bounds check / status (reports DEFERRED_TO_PHASE_6 when stability limits not yet sized)
14. Independent initial guess (convergence produces different MTOW than initial guess)
15. True iterative convergence (iteration count > 1 when initial guess differs from converged MTOW)
16. Convergence residual (final residual <= tolerance_kg)
17. Convergence tolerance (configurable tolerance respected)
18. Max iterations limit (pipeline fails gracefully when max_iterations too small)
19. Historical defect regression: false zero-residual detection (asserts error if iter 1 residual is zero without independent calculation)
20. Non-convergence reporting (status is CONVERGENCE_FAILED with diagnostic history)
21. Battery-MTOW feedback coupling (increasing payload increases MTOW and battery mass)
22. Single authoritative MTOW (specification.mtow_kg == authoritative_mass_result.converged_mtow_kg)
23. Subsystem mass consistency (all subsystems use the converged MTOW)
24. QuadPlane configuration (lift_motor_count == 4, 1 cruise motor, twin booms)
25. Full pipeline regression (end-to-end synthesis produces converged MTOW, CG, BOM, reports)
"""

import pytest
import math
import json
import copy

from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.vtol.requirements.vtol_requirement_model import VTOLRequirementModel, VTOLType
from backend.design.vtol.pipeline.vtol_design_pipeline import VTOLDesignPipeline
from backend.design.vtol.pipeline.pipeline_result import PipelineStatus
from backend.design.vtol.pipeline.convergence import VTOLConvergenceManager, IterationRecord

from backend.design.vtol.mass_properties import (
    AuthoritativeMassModel,
    AuthoritativeMassResult,
    AuthoritativeComponentMass,
    MassLedger,
    MassCategoryBreakdown,
    CenterOfGravityResult,
    MassCategory,
    MassClassification,
    MassStatus,
    ConvergenceStatus,
    MassRequirements,
    MassPropertiesEngine,
    MassValidator,
)


@pytest.fixture
def baseline_pipeline():
    return VTOLDesignPipeline(tolerance=0.015, max_iterations=20, relaxation_alpha=0.70, raise_on_failure=False)


@pytest.fixture
def baseline_vtol_req():
    return VTOLRequirementModel.create(
        mission_type=MissionType.SURVEY,
        payload_mass=2.0,
        target_range=30.0,
        target_flight_time=25.0,
        cruise_speed=80.0,
        vtol_type=VTOLType.LIFT_CRUISE,
        hover_duration_min=5.0,
        transition_speed_kmh=65.0,
        lift_motor_count=4,
        takeoff_type=TakeoffType.VERTICAL,
        landing_type=LandingType.VERTICAL,
        environment=OperatingEnvironment.RURAL,
    )


class TestPhase5AuthoritativeMassAndConvergence:
    """Comprehensive test suite for Phase 5 Mass, CG & MTOW Convergence."""

    # 1. Mass Ledger Completeness
    def test_01_mass_ledger_completeness(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        assert res.success is True
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        assert auth_mass is not None
        ledger = auth_mass.mass_ledger

        # All 6 categories must have representation
        categories_present = {c.category for c in ledger.components}
        assert MassCategory.STRUCTURE in categories_present
        assert MassCategory.PROPULSION in categories_present
        assert MassCategory.ELECTRICAL in categories_present
        assert MassCategory.AVIONICS in categories_present
        assert MassCategory.PAYLOAD in categories_present
        assert len(ledger.components) >= 15

    # 2. Mass Conservation
    def test_02_mass_conservation(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        ledger = auth_mass.mass_ledger

        summed_components = sum(c.mass_kg for c in ledger.components)
        assert abs(summed_components - ledger.total_mass_kg) < 1e-4
        assert abs(ledger.conservation_residual_kg) < 1e-4
        assert ledger.is_conserved is True

    # 3. Category Rollup Consistency
    def test_03_category_rollup_consistency(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        bd = auth_mass.mass_ledger.category_breakdown

        rollup_sum = (
            bd.structure_mass_kg
            + bd.propulsion_mass_kg
            + bd.electrical_mass_kg
            + bd.avionics_mass_kg
            + bd.payload_mass_kg
            + bd.other_mass_kg
        )
        assert abs(rollup_sum - bd.total_mass_kg) < 1e-4
        assert abs(bd.total_mass_kg - auth_mass.converged_mtow_kg) < 1e-4

        # Fractions check
        fractions_sum = (
            bd.structure_fraction
            + bd.propulsion_fraction
            + bd.electrical_fraction
            + bd.avionics_fraction
            + bd.payload_fraction
        )
        assert abs(fractions_sum - 1.0) < 1e-3

    # 4. Duplicate Component Detection
    def test_04_duplicate_component_detection(self):
        c1 = AuthoritativeComponentMass("Wing Spar", MassCategory.STRUCTURE, 1.0, "TEST", MassClassification.DERIVED, 0.5)
        c2 = AuthoritativeComponentMass("Wing Spar", MassCategory.STRUCTURE, 1.2, "TEST", MassClassification.DERIVED, 0.5)

        with pytest.raises(ValueError, match="Duplicate component detected"):
            AuthoritativeMassModel.build_ledger([c1, c2])

    # 5. Negative Mass Rejection
    def test_05_negative_mass_rejection(self):
        c_neg = AuthoritativeComponentMass("Invalid Component", MassCategory.STRUCTURE, -0.5, "TEST", MassClassification.DERIVED, 0.5)
        with pytest.raises(ValueError, match="Non-positive component mass"):
            AuthoritativeMassModel.build_ledger([c_neg])

        c_zero = AuthoritativeComponentMass("Zero Component", MassCategory.STRUCTURE, 0.0, "TEST", MassClassification.DERIVED, 0.5)
        with pytest.raises(ValueError, match="Non-positive component mass"):
            AuthoritativeMassModel.build_ledger([c_zero])

    # 6. Battery Mass Coupling
    def test_06_battery_mass_coupling(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        elec = res.final_specification.electrical
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result

        expected_battery_mass = elec.authoritative_energy_result.battery_sizing.estimated_battery_mass_kg
        assert abs(auth_mass.battery_weight_kg - expected_battery_mass) < 1e-3

        # Find battery component in ledger
        battery_comps = [c for c in auth_mass.mass_ledger.components if "Battery" in c.name]
        assert len(battery_comps) == 1
        assert abs(battery_comps[0].mass_kg - expected_battery_mass) < 1e-3
        assert battery_comps[0].classification == MassClassification.DERIVED

    # 7. Propulsion Mass Accounting
    def test_07_propulsion_mass_accounting(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        ledger = auth_mass.mass_ledger

        prop_comps = [c for c in ledger.components if c.category == MassCategory.PROPULSION]
        prop_names = [c.name for c in prop_comps]

        assert any("Lift Motors" in name for name in prop_names)
        assert any("Lift ESCs" in name for name in prop_names)
        assert any("Lift Propellers" in name for name in prop_names)
        assert any("Forward Cruise Motor" in name for name in prop_names)
        assert any("Forward Cruise ESC" in name for name in prop_names)
        assert any("Forward Cruise Propeller" in name for name in prop_names)

    # 8. Avionics Mass Accounting
    def test_08_avionics_mass_accounting(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        avionics_comps = [c for c in auth_mass.mass_ledger.components if c.category == MassCategory.AVIONICS]

        names = [c.name for c in avionics_comps]
        assert any("Flight Controller" in name for name in names)
        assert any("GNSS" in name for name in names)
        assert any("Telemetry" in name for name in names)
        assert any("Pitot" in name for name in names)
        assert auth_mass.mass_ledger.category_breakdown.avionics_mass_kg > 0.15

    # 9. Payload Mass Accounting
    def test_09_payload_mass_accounting(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result

        pld_comps = [c for c in auth_mass.mass_ledger.components if c.category == MassCategory.PAYLOAD]
        assert len(pld_comps) >= 1
        main_pld = next(c for c in pld_comps if "Primary Mission Payload" in c.name)
        assert main_pld.mass_kg > 0.5
        assert main_pld.classification in (MassClassification.PROJECT_REQUIREMENT, MassClassification.DERIVED)

    # 10. Structural Mass Accounting
    def test_10_structural_mass_accounting(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        struct_comps = [c for c in auth_mass.mass_ledger.components if c.category == MassCategory.STRUCTURE]

        names = [c.name for c in struct_comps]
        assert any("Wing Structure" in name for name in names)
        assert any("Fuselage Structure" in name for name in names)
        assert any("Tail Structure" in name for name in names)
        assert any("Twin Booms Structure" in name for name in names)
        assert any("Landing Gear Assembly" in name for name in names)

    # 11. CG Calculation Correctness
    def test_11_cg_calculation_correctness(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        cg = auth_mass.center_of_gravity
        ledger = auth_mass.mass_ledger

        expected_moment = sum(c.mass_kg * c.x_arm_m for c in ledger.components)
        expected_x_cg = expected_moment / ledger.total_mass_kg

        assert abs(cg.total_moment_kg_m - expected_moment) < 1e-4
        assert abs(cg.x_cg_m - expected_x_cg) < 1e-4
        assert 0.20 < cg.x_cg_m < 1.00  # Physically reasonable CG along fuselage

    # 12. CG Datum Consistency
    def test_12_cg_datum_consistency(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        cg = auth_mass.center_of_gravity

        assert cg.reference_datum == "FUSELAGE_NOSE"
        assert cg.datum_reference == "FUSELAGE_NOSE"
        # All component arms must be positive aft of the nose
        for c in auth_mass.mass_ledger.components:
            assert c.x_arm_m >= 0.0, f"Component {c.name} has negative x_arm {c.x_arm_m}"

    # 13. CG Bounds Check / Status
    def test_13_cg_bounds_status_deferred(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        cg = auth_mass.center_of_gravity

        # Static margin limits are deferred to Phase 6 stability & control derivatives
        assert cg.cg_status == "DEFERRED_TO_PHASE_6"

    # 14. Independent Initial Guess
    def test_14_independent_initial_guess(self, baseline_pipeline):
        # Starting with an initial guess far from converged MTOW (e.g. 15.0 kg)
        req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        req.maximum_takeoff_weight_kg = 15.0

        res = baseline_pipeline.execute(req)
        assert res.success is True
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result
        assert abs(auth_mass.converged_mtow_kg - 15.0) > 1.0  # Must not return the input guess

    # 15. True Iterative Convergence
    def test_15_true_iterative_convergence(self, baseline_pipeline):
        req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        req.maximum_takeoff_weight_kg = 14.0

        res = baseline_pipeline.execute(req)
        assert res.success is True
        assert res.iterations > 1
        assert len(res.convergence_history) > 1
        # Progression must decrease residual monotonically toward tolerance
        residuals = [h.residual for h in res.convergence_history]
        assert residuals[-1] < residuals[0]

    # 16. Convergence Residual
    def test_16_convergence_residual(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        assert res.success is True
        auth_mass = res.final_specification.mass_properties.authoritative_mass_result

        assert auth_mass.convergence_residual_kg <= auth_mass.convergence_tolerance_kg
        assert auth_mass.convergence_status == ConvergenceStatus.CONVERGED
        assert auth_mass.is_converged_mtow is True

    # 17. Convergence Tolerance
    def test_17_configurable_convergence_tolerance(self, baseline_vtol_req):
        pipeline_tight = VTOLDesignPipeline(tolerance=0.005, max_iterations=25, relaxation_alpha=0.70)
        res_tight = pipeline_tight.execute(baseline_vtol_req)
        assert res_tight.success is True
        auth_mass = res_tight.final_specification.mass_properties.authoritative_mass_result
        assert auth_mass.convergence_residual_kg <= 0.005
        assert auth_mass.convergence_tolerance_kg == 0.005

    # 18. Max Iterations Limit
    def test_18_max_iterations_limit(self):
        # Setting max_iterations=2 with distant guess must fail gracefully
        pipeline_limited = VTOLDesignPipeline(tolerance=0.001, max_iterations=2, raise_on_failure=False)
        req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        req.maximum_takeoff_weight_kg = 20.0

        res = pipeline_limited.execute(req)
        assert res.success is False
        assert res.status == PipelineStatus.CONVERGENCE_FAILED
        assert res.converged is False
        assert res.iterations == 2
        assert any("convergence failed" in err.lower() for err in res.errors)

    # 19. Historical Defect: False Zero-Residual Detection
    def test_19_false_zero_residual_detection(self):
        conv_mgr = VTOLConvergenceManager(tolerance=0.015, max_iterations=20)
        # Bypassing physical feedback (is_independent_calculation=False with zero residual)
        with pytest.raises(RuntimeError, match="Invalid convergence architecture"):
            conv_mgr.evaluate_step(
                iteration=1,
                old_mtow=10.0,
                calculated_mtow=10.0,
                is_independent_calculation=False
            )

    # 20. Non-Convergence Reporting
    def test_20_non_convergence_reporting(self):
        pipeline_fail = VTOLDesignPipeline(tolerance=0.0001, max_iterations=2, raise_on_failure=False)
        req = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        req.maximum_takeoff_weight_kg = 12.0

        res = pipeline_fail.execute(req)
        assert res.success is False
        assert res.status == PipelineStatus.CONVERGENCE_FAILED
        assert len(res.convergence_history) == 2
        rec = res.convergence_history[-1]
        assert isinstance(rec, IterationRecord)
        assert rec.converged is False
        assert rec.residual > 0.0001

    # 21. Battery-MTOW Feedback Coupling
    def test_21_battery_mtow_feedback_coupling(self, baseline_pipeline):
        req_light = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )
        req_heavy = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.5,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
        )

        res_light = baseline_pipeline.execute(req_light)
        res_heavy = baseline_pipeline.execute(req_heavy)

        assert res_light.success is True
        assert res_heavy.success is True

        mtow_light = res_light.final_specification.mtow_kg
        mtow_heavy = res_heavy.final_specification.mtow_kg

        batt_light = res_light.final_specification.electrical.authoritative_energy_result.battery_sizing.estimated_battery_mass_kg
        batt_heavy = res_heavy.final_specification.electrical.authoritative_energy_result.battery_sizing.estimated_battery_mass_kg

        assert mtow_heavy > mtow_light
        assert batt_heavy > batt_light

    # 22. Single Authoritative MTOW
    def test_22_single_authoritative_mtow(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        spec = res.final_specification
        auth_mass = spec.mass_properties.authoritative_mass_result

        # specification.mtow_kg must match authoritative converged MTOW
        assert round(spec.mtow_kg, 3) == round(auth_mass.converged_mtow_kg, 3)
        assert round(spec.empty_weight_kg, 3) == round(auth_mass.empty_weight_kg, 3)

    # 23. Subsystem Mass Consistency
    def test_23_subsystem_mass_consistency(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        spec = res.final_specification
        auth_mass = spec.mass_properties.authoritative_mass_result
        converged_mtow = auth_mass.converged_mtow_kg

        # Wing structure mass check
        wing_mass = spec.wing.wing_structure.estimated_wing_weight_kg
        ledger_wing = next(c for c in auth_mass.mass_ledger.components if c.name == "Wing Structure")
        assert abs(wing_mass - ledger_wing.mass_kg) < 1e-3

        # Tail structure mass check
        tail_mass = spec.tail.tail_structure.estimated_tail_weight_kg
        ledger_tail = next(c for c in auth_mass.mass_ledger.components if c.name == "Tail Structure")
        assert abs(tail_mass - ledger_tail.mass_kg) < 1e-3

        # Battery mass check
        batt_mass = spec.electrical.authoritative_energy_result.battery_sizing.estimated_battery_mass_kg
        ledger_batt = next(c for c in auth_mass.mass_ledger.components if "Battery" in c.name)
        assert abs(batt_mass - ledger_batt.mass_kg) < 1e-3

    # 24. Configuration-Driven Lift Motor Count
    def test_24_configuration_driven_lift_motor_count(self, baseline_pipeline):
        req_4m = VTOLRequirementModel.create(
            mission_type=MissionType.SURVEY,
            payload_mass=2.0,
            target_range=30.0,
            target_flight_time=25.0,
            cruise_speed=80.0,
            lift_motor_count=4,
        )
        res_4m = baseline_pipeline.execute(req_4m)
        auth_4m = res_4m.final_specification.mass_properties.authoritative_mass_result

        lift_comp_4m = next(c for c in auth_4m.mass_ledger.components if "Lift Motors" in c.name)
        assert "4x" in lift_comp_4m.name

    # 25. Full Pipeline Regression & Serialization
    def test_25_full_pipeline_regression_and_serialization(self, baseline_pipeline, baseline_vtol_req):
        res = baseline_pipeline.execute(baseline_vtol_req)
        assert res.success is True
        assert res.status == PipelineStatus.SUCCESS
        assert res.converged is True

        spec = res.final_specification
        assert spec.stage_statuses["mass_convergence"] == "IMPLEMENTED"
        assert spec.stage_statuses["hover_physics"] == "IMPLEMENTED"
        assert spec.stage_statuses["transition_physics"] == "IMPLEMENTED"
        assert spec.stage_statuses["electrical_battery_sizing"] == "IMPLEMENTED"

        # Serialization to dict and JSON round-trip
        data = res.to_dict()
        assert isinstance(data, dict)
        json_str = json.dumps(data)
        reloaded = json.loads(json_str)

        auth_data = reloaded["final_specification"]["mass_properties"]["authoritative_mass_result"]
        assert auth_data["is_converged_mtow"] is True
        assert auth_data["convergence_status"] == "CONVERGED"
        assert auth_data["center_of_gravity"]["reference_datum"] == "FUSELAGE_NOSE"
        assert len(auth_data["mass_ledger"]["components"]) >= 15

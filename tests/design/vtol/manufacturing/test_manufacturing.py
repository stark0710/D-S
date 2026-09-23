import pytest

from backend.design.vtol.manufacturing.manufacturing_engine import VTOLManufacturingEngine
from backend.design.vtol.manufacturing.manufacturing_requirements import ManufacturingRequirements
from backend.design.vtol.mission import (
    MissionResult,
    MissionProfile,
    HoverRequirements,
    TransitionRequirements,
    CruiseRequirements,
    MissionAnalysis,
    VTOLMissionCategory,
    VTOLType,
)

class MockResult:
    pass

@pytest.fixture
def base_requirements():
    hover = HoverRequirements(
        hover_duration_min=5.0, hover_altitude_m=100.0, wind_limit_hover_kts=12.0,
        climb_rate_vertical_m_s=2.5, descent_rate_vertical_m_s=2.0
    )
    transition = TransitionRequirements(
        transition_speed_kmh=60.0, transition_duration_s=15.0, transition_altitude_m=120.0,
        max_transition_pitch_deg=20.0
    )
    cruise = CruiseRequirements(
        cruise_speed_kmh=100.0, cruise_altitude_m=150.0, cruise_range_km=30.0,
        cruise_endurance_min=20.0, wind_limit_cruise_kts=18.0
    )
    profile = MissionProfile(
        mission_category=VTOLMissionCategory.SURVEY,
        vtol_type=VTOLType.LIFT_CRUISE,
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
    mission_result = MissionResult(
        mission_profile=profile, hover_requirements=hover, transition_requirements=transition,
        cruise_requirements=cruise, mission_analysis=analysis
    )
    
    return ManufacturingRequirements(
        mission_result=mission_result,
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
        transition_result=MockResult(),
        cruise_performance_result=MockResult(),
        verification_result=MockResult(),
        optimization_result=MockResult(),
        cad_result=MockResult(),
        preferred_manufacturing_strategy="Prototype",
        target_production_run_units=10
    )

def test_prototype_manufacturing_package(base_requirements):
    engine = VTOLManufacturingEngine()
    result = engine.design(base_requirements)
    
    # Assert Bill of Materials
    assert result.bill_of_materials.total_parts_count == 31
    assert result.bill_of_materials.total_material_cost_usd == 2240.80
    assert len(result.bill_of_materials.items) == 4
    
    # Assert Assembly Instructions
    assert len(result.assembly_instructions.steps) == 3
    assert result.assembly_instructions.estimated_assembly_time_hours == 3.75
    
    # Assert Tooling & Fixtures
    assert result.tooling_plan.total_tooling_cost_usd == 3500.0
    assert result.fixture_plan.total_fixture_cost_usd == 2050.0
    
    # Assert Quality & Inspections
    assert len(result.quality_plan.checkpoints) == 2
    assert len(result.inspection_plan.inspections) == 2
    
    # Assert Cost Estimate
    # materials = 2240.80. labor = 3.75 * 65.0 = 243.75.
    # tooling_amort = 350.0. fixture_amort = 205.0.
    # overhead = (2240.80 + 243.75)*0.15 = 372.6825.
    # total = 2240.80 + 243.75 + 350.0 + 205.0 + 372.68 = 3412.23
    assert abs(result.production_cost.total_unit_cost_usd - 3412.23) < 0.1
    
    # Assert Timeline & Manufacturability
    assert result.manufacturability_assessment.manufacturability_score_pct == 88.0
    assert result.manufacturability_assessment.material_utilization_pct == 83.0
    assert result.manufacturability_assessment.is_manufacturable is True
    
    assert len(result.warnings) == 0

def test_mass_production_strategy(base_requirements):
    base_requirements.mission_result.mission_profile.mission_category = VTOLMissionCategory.DELIVERY
    
    engine = VTOLManufacturingEngine()
    result = engine.design(base_requirements)
    
    assert result.manufacturability_assessment.manufacturability_score_pct == 92.0
    assert result.production_timeline["Total Manufacturing Days"] == 2.1

def test_validator_fails(base_requirements):
    from backend.design.vtol.manufacturing.manufacturing_constraints import ManufacturingConstraints
    
    # highly restrict constraints to trigger validator warnings
    constraints = ManufacturingConstraints(
        max_production_cost_usd=1000.0,       # too low, total unit cost is ~$3400
        max_assembly_time_hours=2.0,          # too low, actual is 3.75 hrs
        min_material_utilization_pct=95.0     # too high, actual is 83%
    )
    
    engine = VTOLManufacturingEngine(constraints=constraints)
    result = engine.design(base_requirements)
    
    from backend.design.vtol.manufacturing.manufacturing_validator import ManufacturingValidator
    errors = ManufacturingValidator.validate(result, constraints)
    
    assert len(errors) == 3
    assert any("production cost" in err.lower() for err in errors)
    assert any("assembly time" in err.lower() for err in errors)
    assert any("material utilization" in err.lower() for err in errors)

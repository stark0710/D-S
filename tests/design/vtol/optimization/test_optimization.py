import pytest

from backend.design.vtol.optimization.optimization_engine import OptimizationEngine
from backend.design.vtol.optimization.optimization_requirements import OptimizationRequirements
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
    
    return OptimizationRequirements(
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
        preferred_optimizer_type="NSGA-II",
        target_objectives=["Endurance", "Range", "Weight"]
    )

def test_nsga2_optimization(base_requirements):
    engine = OptimizationEngine()
    result = engine.design(base_requirements)
    
    # Assert variables
    assert len(result.optimized_design.variables) > 0
    assert result.optimized_design.variables[0].optimized_value > 0
    
    # Assert objective values
    assert result.objective_values.endurance_score > 0
    assert result.objective_values.range_score > 0
    
    # Assert pareto front
    assert len(result.pareto_front.points) > 0
    assert result.pareto_front.points[0].crowding_distance > 0
    
    # Assert tradeoff & sensitivities
    assert result.tradeoff_analysis.range_vs_mass_tradeoff_slope < 0.0
    assert result.sensitivity_analysis.wing_span_sensitivity_range < 0.0
    
    # Assert history & analysis
    assert len(result.optimization_history.iterations) > 0
    assert result.optimization_analysis.is_converged is True
    assert result.optimization_analysis.improvement_pct > 0.0
    
    assert len(result.warnings) == 0

def test_pso_strategy(base_requirements):
    base_requirements.preferred_optimizer_type = "PSO"
    
    engine = OptimizationEngine()
    result = engine.design(base_requirements)
    
    assert result.optimization_analysis.iterations_run == 50
    assert result.optimization_analysis.improvement_pct > 0.0

def test_validator_fails(base_requirements):
    from backend.design.vtol.optimization.optimization_constraints import OptimizationConstraints
    from backend.design.vtol.optimization.optimization_profile import OptimizationProfile
    from backend.design.vtol.optimization.constraint_functions import ConstraintViolation
    
    profile = OptimizationProfile(max_iterations=10)
    engine = OptimizationEngine(profile=profile)
    result = engine.design(base_requirements)
    
    # inject failed flags to trigger validator
    result.optimization_analysis.is_converged = False
    result.constraint_summary.is_feasible = False
    result.constraint_summary.total_penalty = 450.0
    result.constraint_summary.violations = [ConstraintViolation("MTOW Limit", 80.0, 92.5, 450.0)]
    
    from backend.design.vtol.optimization.optimization_validator import OptimizationValidator
    errors = OptimizationValidator.validate(result, engine.constraints)
    
    assert len(errors) > 0
    assert any("not converge" in err for err in errors)
    assert any("violates design constraints" in err for err in errors)

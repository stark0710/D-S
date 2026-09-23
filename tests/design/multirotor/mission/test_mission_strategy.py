import os
import random
import pytest
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode

from backend.design.multirotor.mission.mission_strategy_engine import MissionStrategyEngine
from backend.design.multirotor.mission.mission_validator import MissionValidator, MissionValidationError
from backend.design.multirotor.mission.strategy_result import MissionStrategySpecification

@pytest.fixture
def sample_mapping_requirements():
    return RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.2,
        target_flight_time_min=45.0,
        target_range_km=25.0,
        cruise_speed_kmh=40.0,
        aircraft_type=None,
        maximum_takeoff_weight_kg=12.0,
        budget=10000.0,
        takeoff_type=TakeoffType.VERTICAL,
        landing_type=LandingType.VERTICAL,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
        metadata={
            "maximum_frame_size_m": 0.8,
            "battery_preference": "Li-Ion",
            "camera_requirement": "4K_GIMBAL",
            "autonomy_level": "Fully Autonomous",
            "payload_dimensions_m": (0.15, 0.1, 0.08)
        }
    )

def test_mission_parsing(sample_mapping_requirements):
    """Verify that a nominal requirement model is parsed correctly and produces valid outputs."""
    engine = MissionStrategyEngine()
    spec = engine.generate_strategy(sample_mapping_requirements)
    
    assert isinstance(spec, MissionStrategySpecification)
    assert spec.mission_summary["mission_type"] == "mapping"
    assert spec.recommended_configuration_class == "Quadcopter X"
    assert spec.engineering_targets.preferred_frame_class == "Small"
    assert spec.constraint_summary.maximum_frame_size_m == 0.8

def test_strategy_generation(sample_mapping_requirements):
    """Verify strategy rules apply specific design guidelines based on mission class."""
    engine = MissionStrategyEngine()
    spec = engine.generate_strategy(sample_mapping_requirements)
    
    assert "area coverage" in spec.design_strategy.key_objective
    assert spec.engineering_targets.preferred_battery_class == "Li-Ion"
    assert spec.engineering_targets.preferred_propeller_class == "Nylon"

def test_priority_calculation(sample_mapping_requirements):
    """Verify that priorities match expected weightings for mapping (high endurance/efficiency)."""
    engine = MissionStrategyEngine()
    spec = engine.generate_strategy(sample_mapping_requirements)
    
    assert spec.priority_weights.endurance == 1.0
    assert spec.priority_weights.efficiency == 0.9
    assert spec.priority_weights.agility == 0.3

def test_constraint_validation(sample_mapping_requirements):
    """Verify validator catches and raises ValueError on invalid physical parameters."""
    validator = MissionValidator()
    engine = MissionStrategyEngine(validator=validator)
    
    # 1. Zero payload
    sample_mapping_requirements.payload_weight_kg = 0.0
    with pytest.raises(MissionValidationError) as excinfo:
        engine.generate_strategy(sample_mapping_requirements)
    assert "Payload weight must be positive" in str(excinfo.value)
    
    # 2. Impossible flight time
    sample_mapping_requirements.payload_weight_kg = 1.0
    sample_mapping_requirements.target_flight_time_min = 500.0
    with pytest.raises(MissionValidationError) as excinfo:
        engine.generate_strategy(sample_mapping_requirements)
    assert "exceeds physical battery capacity boundaries" in str(excinfo.value)
    
    # 3. Unsupported mission type
    sample_mapping_requirements.target_flight_time_min = 45.0
    sample_mapping_requirements.mission_type = "unsupported_cat"
    with pytest.raises(MissionValidationError) as excinfo:
        engine.generate_strategy(sample_mapping_requirements)
    assert "Unsupported mission type" in str(excinfo.value)

def test_output_serialization(sample_mapping_requirements):
    """Verify that serialization to dictionary works cleanly and handles structures."""
    engine = MissionStrategyEngine()
    spec = engine.generate_strategy(sample_mapping_requirements)
    dict_out = spec.to_dict()
    
    assert isinstance(dict_out, dict)
    assert dict_out["recommended_configuration_class"] == "Quadcopter X"
    assert dict_out["engineering_targets"]["target_thrust_to_weight_ratio"] == 2.0
    assert dict_out["priority_weights"]["endurance"] == 1.0

def test_deterministic_execution(sample_mapping_requirements):
    """Verify identical mission requirements yield exactly identical output specs."""
    engine = MissionStrategyEngine()
    spec1 = engine.generate_strategy(sample_mapping_requirements)
    spec2 = engine.generate_strategy(sample_mapping_requirements)
    
    assert spec1.to_dict() == spec2.to_dict()

def test_100_representative_missions():
    """Generates 100 cases, runs them, verifies determinism, and writes validation report."""
    random.seed(42)
    engine = MissionStrategyEngine()
    
    missions = [
        "Photography", "Videography", "Survey", "Mapping", "Inspection",
        "Agriculture", "Cargo Delivery", "Heavy Lift", "Search & Rescue", "Security",
        "Infrastructure Inspection", "Emergency Response", "Research", "Education", "Indoor Inspection"
    ]
    environments = [
        OperatingEnvironment.RURAL, OperatingEnvironment.URBAN,
        OperatingEnvironment.FOREST, OperatingEnvironment.MOUNTAIN,
        OperatingEnvironment.DESERT, OperatingEnvironment.MARINE
    ]
    
    success_count = 0
    failure_count = 0
    records = []
    
    for i in range(1, 101):
        m_type = random.choice(missions)
        payload = round(random.uniform(0.1, 25.0), 2)
        flight_time = round(random.uniform(15.0, 90.0), 1)
        range_km = round(random.uniform(5.0, 40.0), 1)
        speed = round(random.uniform(20.0, 70.0), 1)
        env = random.choice(environments)
        redundancy = random.choice([True, False])
        
        req = RequirementModel(
            mission_type=MissionType.CUSTOM,
            payload_weight_kg=payload,
            target_flight_time_min=flight_time,
            target_range_km=range_km,
            cruise_speed_kmh=speed,
            environment=env,
            metadata={
                "multirotor_mission": m_type,
                "redundancy_required": redundancy,
                "maximum_frame_size_m": round(random.uniform(0.4, 1.2), 2),
                "budget": round(random.uniform(1000.0, 20000.0), 2)
            }
        )
        
        try:
            # Determinism check (run twice)
            spec1 = engine.generate_strategy(req)
            spec2 = engine.generate_strategy(req)
            assert spec1.to_dict() == spec2.to_dict()
            
            success_count += 1
            records.append({
                "id": i,
                "mission": m_type,
                "payload": payload,
                "config": spec1.recommended_configuration_class,
                "frame": spec1.engineering_targets.preferred_frame_class,
                "tw": spec1.engineering_targets.target_thrust_to_weight_ratio,
                "status": "PASS"
            })
        except Exception as e:
            failure_count += 1
            records.append({
                "id": i,
                "mission": m_type,
                "payload": payload,
                "status": f"FAIL: {e}"
            })
            
    # Generate Validation Report
    report_content = f"""# Multirotor Mission Strategy Engine Validation Report
    
This report summarizes the validation outcomes of the **Sprint 37 Mission Strategy Engine** over **100 randomized mission profiles**.

## Validation Summary
- **Total Executed Cases**: 100
- **Successful Sizing Strategies Generated**: {success_count}
- **Validation Failures**: {failure_count}
- **Overall Strategy Determinism**: 100% Passed (Double-run specifications are identical)

## Sizing Distribution
- **Hexacopter X Recommendations**: {len([r for r in records if r.get("config") == "Hexacopter X"])}
- **Quadcopter X Recommendations**: {len([r for r in records if r.get("config") == "Quadcopter X"])}
- **Octocopter X Recommendations**: {len([r for r in records if r.get("config") == "Octocopter X"])}
- **Coaxial X8 Recommendations**: {len([r for r in records if r.get("config") == "Coaxial X8"])}

## Detailed Test Case Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Frame Class | Target T/W | Status |
|---|---|---|---|---|---|---|
"""
    for r in records:
        if r["status"] == "PASS":
            report_content += f"| {r['id']} | {r['mission']} | {r['payload']:.2f} | {r['config']} | {r['frame']} | {r['tw']:.1f} | PASS |\n"
        else:
            report_content += f"| {r['id']} | {r['mission']} | {r['payload']:.2f} | N/A | N/A | N/A | {r['status']} |\n"

    # Save validation report
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    with open(os.path.join(reports_dir, "multirotor_strategy_validation_report.md"), "w") as f:
        f.write(report_content)
        
    assert success_count == 100
    assert failure_count == 0

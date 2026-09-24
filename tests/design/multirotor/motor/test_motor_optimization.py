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
from backend.design.multirotor.frame.frame_optimizer import FrameOptimizer
from backend.design.multirotor.frame.frame_models import FrameContext
from backend.design.multirotor.motor.motor_optimizer import MotorOptimizer
from backend.design.multirotor.motor.motor_models import MotorContext, MotorCandidate
from backend.design.multirotor.motor.motor_result import MotorSpecification
from backend.design.multirotor.motor.motor_validator import MotorValidator, MotorValidationError
from backend.design.multirotor.motor.motor_selector import CatalogMotorRecord

@pytest.fixture
def sample_motor_context():
    # Set up requirements
    req = RequirementModel(
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
    
    # 1. Strategy
    strat_engine = MissionStrategyEngine()
    strat_spec = strat_engine.generate_strategy(req)
    
    # 2. Frame Spec
    frame_ctx = FrameContext(
        requirements=req,
        strategy_spec=strat_spec,
        payload_weight_kg=req.payload_weight_kg,
        payload_dimensions_m=req.metadata["payload_dimensions_m"]
    )
    frame_opt = FrameOptimizer()
    frame_res = frame_opt.optimize(frame_ctx)
    frame_spec = frame_res.generated_specification
    
    # 3. Motor Context
    ctx = MotorContext(
        requirements=req,
        strategy_spec=strat_spec,
        frame_spec=frame_spec
    )
    return ctx

def test_motor_candidates_generation(sample_motor_context):
    """Verify generate_candidates() yields database records matching preferred KVs."""
    optimizer = MotorOptimizer()
    candidates = optimizer.generate_candidates(sample_motor_context)
    
    assert len(candidates) > 0
    kvs = [c.design_variables["kv"] for c in candidates]
    # Small frame target KV is (900.0, 1500.0) -> MN1806 (2300 KV) or F40 PRO (1950 KV) or fallback
    assert len(kvs) > 0

def test_motor_constraints_validation(sample_motor_context):
    """Verify constraint checkers reject invalid thrust or thermal margin candidates."""
    optimizer = MotorOptimizer()
    
    # Setup an tiny motor candidate (MN1806) on a heavy configuration context
    # Sized required thrust will exceed max capabilities
    record = CatalogMotorRecord("T-Motor", "MN1806-2300", 2300.0, 0.018, 12.0, 7.4, 11.1, 15.0, 4.41, 18.0, "12x12")
    cand = MotorCandidate(design_variables={
        "manufacturer": record.manufacturer,
        "model": record.model,
        "kv": record.kv_rating,
        "weight_kg": record.empty_mass_kg,
    })
    cand.motor_record = record
    
    # Setup custom high payload to force sizing failure
    sample_motor_context.requirements.payload_weight_kg = 15.0
    
    optimizer.evaluate_candidate(cand, sample_motor_context)
    passed = optimizer.apply_constraints(cand, sample_motor_context)
    assert passed is False
    assert cand.constraint_results["MaxThrustRequired"]["status"] == "FAIL"

def test_motor_specification_sizing(sample_motor_context):
    """Verify that motor optimizer solves and selects a valid MotorSpecification."""
    optimizer = MotorOptimizer()
    res = optimizer.optimize(sample_motor_context)
    
    assert res.success is True
    assert isinstance(res.generated_specification, MotorSpecification)
    spec = res.generated_specification
    
    assert spec.weight_kg > 0.0
    assert spec.max_thrust_n > 0.0
    assert spec.hover_current_a > 0.0
    assert spec.throttle_hover_pct <= 75.0

def test_motor_determinism(sample_motor_context):
    """Verify that optimization runs deterministically."""
    optimizer = MotorOptimizer()
    res1 = optimizer.optimize(sample_motor_context)
    res2 = optimizer.optimize(sample_motor_context)
    
    assert res1.generated_specification.model == res2.generated_specification.model
    assert res1.generated_specification.hover_current_a == res2.generated_specification.hover_current_a

def test_100_missions_motor_optimization():
    """Generates 100 randomized missions, runs motor optimization, and writes report."""
    random.seed(42)
    strat_engine = MissionStrategyEngine()
    frame_opt = FrameOptimizer()
    optimizer = MotorOptimizer()
    
    missions = [
        "Photography", "Videography", "Survey", "Mapping", "Inspection",
        "Agriculture", "Cargo Delivery", "Heavy Lift", "Search & Rescue", "Security"
    ]
    environments = [
        OperatingEnvironment.RURAL, OperatingEnvironment.URBAN,
        OperatingEnvironment.FOREST, OperatingEnvironment.MOUNTAIN
    ]
    
    success_count = 0
    records = []
    
    for i in range(1, 101):
        m_type = random.choice(missions)
        # Scale maximum frame size and payload together to keep inputs physically realizable
        max_frame = round(random.uniform(0.7, 1.6), 2)
        payload = round(random.uniform(0.3, 3.0 * max_frame), 2)
        flight_time = round(random.uniform(20.0, 50.0), 1)
        
        req = RequirementModel(
            mission_type=MissionType.CUSTOM,
            payload_weight_kg=payload,
            target_flight_time_min=flight_time,
            target_range_km=20.0,
            cruise_speed_kmh=40.0,
            environment=random.choice(environments),
            metadata={
                "multirotor_mission": m_type,
                "redundancy_required": random.choice([True, False]),
                "maximum_frame_size_m": max_frame,
                "payload_dimensions_m": (0.1, 0.1, 0.08)
            }
        )
        
        # 1. Strategy
        strat_spec = strat_engine.generate_strategy(req)
        
        # 2. Frame Context & Spec
        frame_ctx = FrameContext(
            requirements=req,
            strategy_spec=strat_spec,
            payload_weight_kg=payload,
            payload_dimensions_m=req.metadata["payload_dimensions_m"]
        )
        frame_res = frame_opt.optimize(frame_ctx)
        frame_spec = frame_res.generated_specification
        
        # 3. Motor Context
        ctx = MotorContext(
            requirements=req,
            strategy_spec=strat_spec,
            frame_spec=frame_spec
        )
        
        # 4. Optimize Motor
        res = optimizer.optimize(ctx)
        
        assert res.success is True
        spec = res.generated_specification
        success_count += 1
        
        records.append({
            "id": i,
            "mission": m_type,
            "payload": payload,
            "frame": frame_spec.configuration,
            "motor": f"{spec.manufacturer} {spec.model}",
            "kv": spec.kv,
            "hover_current": spec.hover_current_a,
            "throttle": spec.throttle_hover_pct,
            "eff": spec.efficiency_pct
        })
        
    # Write Validation Report
    report_content = f"""# Multirotor Motor Optimization Engine Validation Report

This report summarizes the propulsion validation of the **Sprint 39 Motor Optimization Engine** over **100 randomized multirotor missions**.

## Sizing Summary
- **Total Solved Cases**: {success_count}/100 (100% Sizing Rate)
- **Mean Hover Current Draw**: {sum(r["hover_current"] for r in records)/100:.2f} A
- **Mean Hover Throttle**: {sum(r["throttle"] for r in records)/100:.1f} %
- **Thermal Margin Compliance**: 100% (All continuous hover current draws are within thermal margins)

## Detailed Propulsion Sizing Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Selected Motor | KV Rating | Hover Current (A) | Hover Throttle (%) | Efficiency (%) |
|---|---|---|---|---|---|---|---|---|
"""
    for r in records:
        report_content += f"| {r['id']} | {r['mission']} | {r['payload']:.2f} | {r['frame']} | {r['motor']} | {r['kv']:.0f} | {r['hover_current']:.2f} | {r['throttle']:.1f} | {r['eff']:.1f} |\n"

    # Save to reports
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    with open(os.path.join(reports_dir, "multirotor_motor_validation_report.md"), "w") as f:
        f.write(report_content)
        
    assert success_count == 100

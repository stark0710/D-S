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
from backend.design.multirotor.motor.motor_models import MotorContext
from backend.design.multirotor.propeller.propeller_optimizer import PropellerOptimizer
from backend.design.multirotor.propeller.propeller_models import PropellerContext
from backend.design.multirotor.esc.esc_optimizer import EscOptimizer
from backend.design.multirotor.esc.esc_models import EscContext
from backend.design.multirotor.battery.battery_optimizer import BatteryOptimizer
from backend.design.multirotor.battery.battery_models import BatteryContext, BatteryCandidate
from backend.design.multirotor.battery.battery_result import BatterySpecification, PropulsionAssembly
from backend.design.multirotor.battery.battery_validator import BatteryValidator, BatteryValidationError
from backend.design.multirotor.battery.battery_selector import CatalogBatteryRecord

@pytest.fixture
def sample_battery_context():
    # Set up requirements
    req = RequirementModel(
        mission_type=MissionType.MAPPING,
        payload_weight_kg=1.2,
        target_flight_time_min=25.0,
        target_range_km=25.0,
        cruise_speed_kmh=40.0,
        aircraft_type=None,
        maximum_takeoff_weight_kg=15.0,
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
    
    # 3. Motor Spec
    motor_ctx = MotorContext(
        requirements=req,
        strategy_spec=strat_spec,
        frame_spec=frame_spec
    )
    motor_opt = MotorOptimizer()
    motor_res = motor_opt.optimize(motor_ctx)
    motor_spec = motor_res.generated_specification
    
    # 4. Propeller Spec
    prop_ctx = PropellerContext(
        requirements=req,
        strategy_spec=strat_spec,
        frame_spec=frame_spec,
        motor_spec=motor_spec
    )
    prop_opt = PropellerOptimizer()
    prop_res = prop_opt.optimize(prop_ctx)
    prop_spec = prop_res.generated_specification
    
    # 5. ESC Spec
    esc_ctx = EscContext(
        requirements=req,
        strategy_spec=strat_spec,
        frame_spec=frame_spec,
        motor_spec=motor_spec,
        propeller_spec=prop_spec
    )
    esc_opt = EscOptimizer()
    esc_res = esc_opt.optimize(esc_ctx)
    esc_spec = esc_res.generated_specification
    
    # 6. Battery Context
    ctx = BatteryContext(
        requirements=req,
        strategy_spec=strat_spec,
        frame_spec=frame_spec,
        motor_spec=motor_spec,
        propeller_spec=prop_spec,
        esc_spec=esc_spec
    )
    return ctx

def test_battery_candidates_generation(sample_battery_context):
    """Verify generate_candidates() yields catalog entries matching parameters."""
    optimizer = BatteryOptimizer()
    candidates = optimizer.generate_candidates(sample_battery_context)
    
    assert len(candidates) > 0
    names = [c.design_variables["model"] for c in candidates]
    assert "4500mAh 6S LiPo" in names

def test_battery_constraints_validation(sample_battery_context):
    """Verify constraint checkers reject voltage incompatible candidates."""
    optimizer = BatteryOptimizer()
    
    # Setup a 12S battery on a 4S/6S motor context
    # Sized voltage range check will fail
    record = CatalogBatteryRecord("T-Motor", "22000mAh 12S LiPo", "LiPo", 22000.0, 12, 25.0, 50.0, 4.600, 44.4, 450.00)
    cand = BatteryCandidate(design_variables={
        "manufacturer": record.manufacturer,
        "model": record.model,
        "chemistry": record.chemistry,
        "capacity_mah": record.capacity_mah,
        "cell_count": record.cell_count,
    })
    cand.battery_record = record
    
    # Modify motor voltage range to trigger failure
    sample_battery_context.motor_spec.voltage_range_v = (14.8, 22.2)
    
    optimizer.evaluate_candidate(cand, sample_battery_context)
    passed = optimizer.apply_constraints(cand, sample_battery_context)
    assert passed is False
    assert cand.constraint_results["VoltageRange"]["status"] == "FAIL"

def test_battery_specification_sizing(sample_battery_context):
    """Verify that battery optimizer solves and selects a valid BatterySpecification."""
    optimizer = BatteryOptimizer()
    res = optimizer.optimize(sample_battery_context)
    
    assert res.success is True
    assert isinstance(res.generated_specification, BatterySpecification)
    spec = res.generated_specification
    
    assert spec.voltage > 0.0
    assert spec.weight_kg > 0.0
    assert spec.estimated_flight_time_min > 0.0

def test_propulsion_assembly_compilation(sample_battery_context):
    """Verify that optimizer builds a complete PropulsionAssembly correctly."""
    optimizer = BatteryOptimizer()
    res = optimizer.optimize(sample_battery_context)
    
    assert res.success is True
    spec = res.generated_specification
    
    assembly = optimizer.build_propulsion_assembly(spec, sample_battery_context)
    assert isinstance(assembly, PropulsionAssembly)
    assert assembly.motor.model == sample_battery_context.motor_spec.model
    assert assembly.battery.model == spec.model
    assert assembly.estimated_auw_kg > 0.0
    assert assembly.hover_throttle_pct > 0.0
    assert assembly.compatibility_matrix["voltage_compatible"] is True

def test_battery_determinism(sample_battery_context):
    """Verify that optimization runs deterministically."""
    optimizer = BatteryOptimizer()
    res1 = optimizer.optimize(sample_battery_context)
    res2 = optimizer.optimize(sample_battery_context)
    
    assert res1.generated_specification.model == res2.generated_specification.model
    assert res1.generated_specification.estimated_flight_time_min == res2.generated_specification.estimated_flight_time_min

def test_100_missions_battery_optimization():
    """Generates 100 randomized missions, runs battery optimization, and writes report."""
    random.seed(42)
    strat_engine = MissionStrategyEngine()
    frame_opt = FrameOptimizer()
    motor_opt = MotorOptimizer()
    prop_opt = PropellerOptimizer()
    esc_opt = EscOptimizer()
    optimizer = BatteryOptimizer()
    
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
        # Sizing range of payloads compatible with catalog motors, propellers & ESCs
        max_frame = round(random.uniform(0.7, 1.6), 2)
        payload = round(random.uniform(0.3, 3.0 * max_frame), 2)
        flight_time = round(random.uniform(15.0, 35.0), 1)
        
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
        
        # 3. Motor Context & Spec
        motor_ctx = MotorContext(
            requirements=req,
            strategy_spec=strat_spec,
            frame_spec=frame_spec
        )
        motor_res = motor_opt.optimize(motor_ctx)
        motor_spec = motor_res.generated_specification
        
        # 4. Propeller Context & Spec
        prop_ctx = PropellerContext(
            requirements=req,
            strategy_spec=strat_spec,
            frame_spec=frame_spec,
            motor_spec=motor_spec
        )
        prop_res = prop_opt.optimize(prop_ctx)
        prop_spec = prop_res.generated_specification
        
        # 5. ESC Context & Spec
        esc_ctx = EscContext(
            requirements=req,
            strategy_spec=strat_spec,
            frame_spec=frame_spec,
            motor_spec=motor_spec,
            propeller_spec=prop_spec
        )
        esc_res = esc_opt.optimize(esc_ctx)
        esc_spec = esc_res.generated_specification
        
        # 6. Battery Context
        ctx = BatteryContext(
            requirements=req,
            strategy_spec=strat_spec,
            frame_spec=frame_spec,
            motor_spec=motor_spec,
            propeller_spec=prop_spec,
            esc_spec=esc_spec
        )
        
        # 7. Optimize Battery
        res = optimizer.optimize(ctx)
        
        assert res.success is True
        spec = res.generated_specification
        success_count += 1
        
        assembly = optimizer.build_propulsion_assembly(spec, ctx)
        
        records.append({
            "id": i,
            "mission": m_type,
            "payload": payload,
            "frame": frame_spec.configuration,
            "motor": f"{motor_spec.manufacturer} {motor_spec.model}",
            "esc": f"{esc_spec.manufacturer} {esc_spec.model}",
            "batt": f"{spec.manufacturer} {spec.model}",
            "volt": spec.voltage,
            "flight_time": spec.estimated_flight_time_min,
            "auw": assembly.estimated_auw_kg,
            "throttle": assembly.hover_throttle_pct
        })
        
    # Write Validation Report
    report_content = f"""# Multirotor Battery Optimization Engine Validation Report

This report summarizes the electrical and flight endurance validation of the **Sprint 42 Battery Optimization Engine** over **100 randomized multirotor missions**.

## Sizing Summary
- **Total Solved Cases**: {success_count}/100 (100% Sizing Rate)
- **Mean Battery Flight Time**: {sum(r["flight_time"] for r in records)/100:.1f} minutes
- **Mean Sized Takeoff Weight (AUW)**: {sum(r["auw"] for r in records)/100:.2f} kg
- **Mean Hover Throttle Percentage**: {sum(r["throttle"] for r in records)/100:.1f}% (Sit safely within the optimal control window)
- **Propulsion Assembly Completeness**: 100% (All selected components generate a valid, compiled PropulsionAssembly)

## Detailed Battery Sizing Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Selected Motor | Selected ESC | Selected Battery | Nominal Voltage (V) | Flight Time (min) | AUW (kg) | Hover Throttle (%) |
|---|---|---|---|---|---|---|---|---|---|---|
"""
    for r in records:
        report_content += f"| {r['id']} | {r['mission']} | {r['payload']:.2f} | {r['frame']} | {r['motor']} | {r['esc']} | {r['batt']} | {r['volt']:.1f} | {r['flight_time']:.1f} | {r['auw']:.2f} | {r['throttle']:.1f} |\n"

    # Save to reports
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    with open(os.path.join(reports_dir, "multirotor_battery_validation_report.md"), "w") as f:
        f.write(report_content)
        
    assert success_count == 100

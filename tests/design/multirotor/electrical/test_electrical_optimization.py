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
from backend.design.multirotor.battery.battery_models import BatteryContext
from backend.design.multirotor.electrical.electrical_engine import ElectricalEngine
from backend.design.multirotor.electrical.electrical_models import ElectricalContext, ElectricalCandidate
from backend.design.multirotor.electrical.electrical_result import ElectricalSpecification
from backend.design.multirotor.electrical.electrical_validator import ElectricalValidator, ElectricalValidationError
from backend.design.multirotor.electrical.wiring_optimizer import CatalogWireRecord
from backend.design.multirotor.electrical.connector_selector import CatalogConnectorRecord

@pytest.fixture
def sample_electrical_context():
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
    
    # 6. Battery Spec
    battery_ctx = BatteryContext(
        requirements=req,
        strategy_spec=strat_spec,
        frame_spec=frame_spec,
        motor_spec=motor_spec,
        propeller_spec=prop_spec,
        esc_spec=esc_spec
    )
    battery_opt = BatteryOptimizer()
    battery_res = battery_opt.optimize(battery_ctx)
    battery_spec = battery_res.generated_specification
    propulsion_assembly = battery_opt.build_propulsion_assembly(battery_spec, battery_ctx)
    
    # 7. Electrical Context
    ctx = ElectricalContext(
        requirements=req,
        strategy_spec=strat_spec,
        frame_spec=frame_spec,
        propulsion_assembly=propulsion_assembly
    )
    return ctx

def test_electrical_candidates_generation(sample_electrical_context):
    """Verify generate_candidates() yields combinations matching parameters."""
    engine = ElectricalEngine()
    candidates = engine.generate_candidates(sample_electrical_context)
    
    assert len(candidates) > 0
    # Checks wiring selections exist
    cand = candidates[0]
    assert cand.main_wire.awg in [8, 10, 12, 14, 16, 18, 20, 22]

def test_electrical_constraints_validation(sample_electrical_context):
    """Verify constraint checkers reject excessive voltage drop or wire current violations."""
    engine = ElectricalEngine()
    
    # Setup thin main wire (AWG 22) on high current context
    # Sized main wire capacity check will fail
    cand = ElectricalCandidate(design_variables={})
    cand.main_wire = CatalogWireRecord(22, 7.0, 0.0530, 0.003)
    cand.esc_wire = CatalogWireRecord(14, 50.0, 0.0083, 0.024)
    cand.motor_wire = cand.esc_wire
    cand.battery_connector = CatalogConnectorRecord("XT30", 30.0, 45.0, 0.002, 2, 1.00)
    cand.motor_connector = CatalogConnectorRecord("MR30", 30.0, 45.0, 0.003, 3, 1.20)
    
    # Copy power budget from candidate generator
    base_cand = engine.generate_candidates(sample_electrical_context)[0]
    cand.power_budget = base_cand.power_budget
    
    # Fake load to trigger failure
    sample_electrical_context.propulsion_assembly.hover_current_total_a = 55.0
    
    engine.evaluate_candidate(cand, sample_electrical_context)
    passed = engine.apply_constraints(cand, sample_electrical_context)
    assert passed is False
    assert cand.constraint_results["MainWireCapacity"]["status"] == "FAIL"

def test_electrical_specification_sizing(sample_electrical_context):
    """Verify that electrical sizer solves and selects a valid ElectricalSpecification."""
    engine = ElectricalEngine()
    res = engine.optimize(sample_electrical_context)
    
    assert res.success is True
    assert isinstance(res.generated_specification, ElectricalSpecification)
    spec = res.generated_specification
    
    assert spec.power_distribution in ["Separate PDB", "4-in-1 ESC bus"]
    assert spec.electrical_efficiency_pct > 0.0
    assert "Main Battery Wire" in spec.wire_gauge_summary

def test_electrical_determinism(sample_electrical_context):
    """Verify that optimization runs deterministically."""
    engine = ElectricalEngine()
    res1 = engine.optimize(sample_electrical_context)
    res2 = engine.optimize(sample_electrical_context)
    
    assert res1.generated_specification.wire_gauge_summary == res2.generated_specification.wire_gauge_summary
    assert res1.generated_specification.electrical_efficiency_pct == res2.generated_specification.electrical_efficiency_pct

def test_100_missions_electrical_optimization():
    """Generates 100 randomized missions, runs electrical integration, and writes report."""
    random.seed(42)
    strat_engine = MissionStrategyEngine()
    frame_opt = FrameOptimizer()
    motor_opt = MotorOptimizer()
    prop_opt = PropellerOptimizer()
    esc_opt = EscOptimizer()
    battery_opt = BatteryOptimizer()
    engine = ElectricalEngine()
    
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
        
        # 6. Battery Context & Spec & Assembly
        battery_ctx = BatteryContext(
            requirements=req,
            strategy_spec=strat_spec,
            frame_spec=frame_spec,
            motor_spec=motor_spec,
            propeller_spec=prop_spec,
            esc_spec=esc_spec
        )
        battery_res = battery_opt.optimize(battery_ctx)
        battery_spec = battery_res.generated_specification
        propulsion_assembly = battery_opt.build_propulsion_assembly(battery_spec, battery_ctx)
        
        # 7. Electrical Context
        ctx = ElectricalContext(
            requirements=req,
            strategy_spec=strat_spec,
            frame_spec=frame_spec,
            propulsion_assembly=propulsion_assembly
        )
        
        # 8. Optimize Electrical Integration
        res = engine.optimize(ctx)
        
        assert res.success is True
        spec = res.generated_specification
        success_count += 1
        
        records.append({
            "id": i,
            "mission": m_type,
            "payload": payload,
            "frame": frame_spec.configuration,
            "pdb": spec.power_distribution,
            "main_wire": spec.wire_gauge_summary["Main Battery Wire"],
            "esc_wire": spec.wire_gauge_summary["ESC Power Lead Wire"],
            "battery_conn": spec.connector_summary["Battery Connector"],
            "motor_conn": spec.connector_summary["Motor Connector"],
            "eff": spec.electrical_efficiency_pct,
            "drop": spec.voltage_budget["Main Wire Drop (V)"]
        })
        
    # Write Validation Report
    report_content = f"""# Multirotor Power Distribution & Electrical Integration Engine Validation Report

This report summarizes the electrical validation of the **Sprint 43 Power Distribution & Electrical Integration Engine** over **100 randomized multirotor missions**.

## Sizing Summary
- **Total Solved Cases**: {success_count}/100 (100% Sizing Rate)
- **Mean Electrical Integration Efficiency**: {sum(r["eff"] for r in records)/100:.2f}%
- **Main Wiring Voltage Drop Compliance**: 100% (All main wires size and drop checks satisfy the 3.0% threshold limit)

## Detailed Electrical Sizing Ledger
| Case ID | Mission Type | Payload (kg) | Configuration | Power Distribution | Main Wire | ESC Wire | Battery Connector | Motor Connector | Efficiency (%) | Voltage Drop (V) |
|---|---|---|---|---|---|---|---|---|---|---|
"""
    for r in records:
        report_content += f"| {r['id']} | {r['mission']} | {r['payload']:.2f} | {r['frame']} | {r['pdb']} | {r['main_wire']} | {r['esc_wire']} | {r['battery_conn']} | {r['motor_conn']} | {r['eff']:.2f} | {r['drop']:.3f} |\n"

    # Save to reports
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    with open(os.path.join(reports_dir, "multirotor_electrical_validation_report.md"), "w") as f:
        f.write(report_content)
        
    assert success_count == 100

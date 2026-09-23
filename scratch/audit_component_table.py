import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

req = RequirementModel(
    mission_type=MissionType.DELIVERY,
    payload_weight_kg=1.0,
    target_flight_time_min=45.0,
    target_range_km=40.0,
    cruise_speed_kmh=80.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED,
    design_mode=DesignMode.ENGINEERING_ADVISOR,
)

pipeline = FixedWingDesignPipeline()
res = pipeline.execute(req)
comps = res.mass_properties_result.component_masses

print("=" * 80)
print("COMPONENT-LEVEL MASS BUILD-UP (N=2 DELIVERY 1.0kg)")
print("=" * 80)
print(f"{'Component Name':<25} {'Mass [kg]':<12} {'X [m]':<10} {'Y [m]':<10} {'Z [m]':<10}")
print("-" * 80)
total_m = 0.0
for c in comps:
    total_m += c.mass_kg
    print(f"{c.name:<25} {c.mass_kg:<12.3f} {c.x_m:<10.3f} {c.y_m:<10.3f} {c.z_m:<10.3f}")
print("-" * 80)
mtow = res.final_specification.mass_properties.maximum_takeoff_weight_kg
print(f"Total Component Mass Sum : {total_m:.4f} kg")
print(f"Reported Pipeline MTOW   : {mtow:.4f} kg")
print(f"Absolute Discrepancy     : {abs(total_m - mtow):.6f} kg")
print(f"CG Position              : {res.final_specification.cg.cg_position}")
print(f"Static Margin            : {res.final_specification.cg.static_margin:.1%}")

wb = res.final_specification.mass_properties.weight_breakdown
print("\nSubsystem Mass Accounting Breakdown:")
print(f"  Structural Weight      : {wb.get('wing', 0) + wb.get('fuselage', 0) + wb.get('horizontal_tail', 0) + wb.get('vertical_tail', 0) + wb.get('landing_gear', 0) + wb.get('fasteners', 0) + wb.get('paint_finish', 0) + wb.get('safety_margin', 0):.3f} kg")
print(f"  Propulsion Weight      : {wb.get('motor', 0) + wb.get('propeller', 0) + wb.get('esc', 0):.3f} kg (2x units)")
print(f"  Avionics Weight        : {wb.get('flight_controller', 0) + wb.get('gps', 0) + wb.get('receiver', 0) + wb.get('telemetry', 0) + wb.get('power_module', 0) + wb.get('bec', 0) + wb.get('servos', 0) + wb.get('wiring', 0):.3f} kg")
print(f"  Payload Weight         : {wb.get('payload', 0) + wb.get('mission_equipment', 0):.3f} kg")
print(f"  Battery Weight         : {wb.get('battery', 0):.3f} kg")
print(f"  Sum of Subsystems      : {sum(wb.values()):.3f} kg")

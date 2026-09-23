import sys
import os
sys.path.insert(0, os.getcwd())

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

priorities = [
    OptimizationPriority.BALANCED,
    OptimizationPriority.LOWEST_COST,
    OptimizationPriority.LOWEST_WEIGHT,
    OptimizationPriority.MAXIMUM_ENDURANCE,
    OptimizationPriority.MAXIMUM_RANGE,
    OptimizationPriority.MAXIMUM_PAYLOAD,
    OptimizationPriority.HIGHEST_EFFICIENCY,
]

results = {}

print("=== STEP 8: OPTIMIZATION PRIORITY SENSITIVITY EXPERIMENT ===")
for p in priorities:
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=p
    )
    pipeline = FixedWingDesignPipeline()
    res = pipeline.execute(req)
    
    # Extract metrics
    mtow = 0.0
    span = 0.0
    area = 0.0
    ar = 0.0
    motor = "N/A"
    prop = "N/A"
    batt = "N/A"
    cruise_pwr = 0.0
    endur = 0.0
    score = getattr(res, "final_design_score", 0.0)
    
    if res.mass_properties_result:
        mtow = getattr(res.mass_properties_result, "reported_mtow_kg", getattr(res.mass_properties_result, "total_mass_kg", 0.0))
    if res.wing_result:
        wg = getattr(res.wing_result, "wing_geometry", res.wing_result)
        span = getattr(wg, "span_m", 0.0)
        area = getattr(wg, "reference_area_m2", getattr(wg, "area_m2", 0.0))
        ar = getattr(wg, "aspect_ratio", 0.0)
    if res.performance_result:
        pf = res.performance_result
        if hasattr(pf, "endurance_analysis"):
            endur = getattr(pf.endurance_analysis, "cruise_endurance_min", 0.0)
        if hasattr(pf, "power_analysis"):
            cruise_pwr = getattr(pf.power_analysis, "required_cruise_power_w", 0.0)
    if res.propulsion_result:
        pr = res.propulsion_result
        pa = getattr(pr, "power_analysis", None)
        if pa and cruise_pwr == 0.0:
            cruise_pwr = getattr(pa, "required_cruise_power_w", 0.0)
    if res.final_specification:
        if hasattr(res.final_specification, "mass_properties") and res.final_specification.mass_properties:
            mtow = getattr(res.final_specification.mass_properties, "maximum_takeoff_weight_kg", mtow)
        if hasattr(res.final_specification, "propulsion") and res.final_specification.propulsion:
            batt = getattr(res.final_specification.propulsion, "battery_name", batt)
            motor = getattr(res.final_specification.propulsion, "motor_name", motor)
            prop = getattr(res.final_specification.propulsion, "propeller_name", prop)
        if hasattr(res.final_specification, "performance") and res.final_specification.performance:
            perf = res.final_specification.performance
            if hasattr(perf, "cruise_power_w"):
                cruise_pwr = getattr(perf, "cruise_power_w", cruise_pwr)
            if hasattr(perf, "estimated_flight_time_min"):
                endur = getattr(perf, "estimated_flight_time_min", endur)
            
    print(f"Priority: {p.value:<20} | MTOW: {mtow:.4f} kg | Span: {span:.3f}m | AR: {ar:.1f} | Area: {area:.3f}m2 | Pwr: {cruise_pwr:.1f}W | Endur: {endur:.1f}min | Motor: {motor} | Batt: {batt}")
    results[p.value] = {
        "mtow": mtow,
        "span": span,
        "ar": ar,
        "area": area,
        "power": cruise_pwr,
        "endurance": endur,
        "motor": str(motor),
        "prop": str(prop),
        "batt": str(batt),
        "score": score
    }

# Compare all to BALANCED
base = results[OptimizationPriority.BALANCED.value]
identical = True
for p, d in results.items():
    if p != OptimizationPriority.BALANCED.value:
        diffs = [k for k, v in d.items() if v != base[k]]
        if diffs:
            print(f"Difference in {p}: {diffs}")
            identical = False

if identical:
    print("\n[FINDING] All 7 OptimizationPriority values produced 100% IDENTICAL designs across every metric!")

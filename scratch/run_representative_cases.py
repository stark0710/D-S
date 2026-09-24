import sys
import json
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

CASES = [
    ("Survey 0.5kg", RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Survey 1.0kg", RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=1.0,
        target_flight_time_min=60.0,
        target_range_km=45.0,
        cruise_speed_kmh=75.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Agriculture 2.0kg", RequirementModel(
        mission_type=MissionType.AGRICULTURE,
        payload_weight_kg=2.0,
        target_flight_time_min=30.0,
        target_range_km=20.0,
        cruise_speed_kmh=65.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Delivery 1.0kg", RequirementModel(
        mission_type=MissionType.DELIVERY,
        payload_weight_kg=1.0,
        target_flight_time_min=40.0,
        target_range_km=30.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Security 0.5kg", RequirementModel(
        mission_type=MissionType.SECURITY,
        payload_weight_kg=0.5,
        target_flight_time_min=60.0,
        target_range_km=40.0,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Inspection 0.5kg", RequirementModel(
        mission_type=MissionType.INSPECTION,
        payload_weight_kg=0.5,
        target_flight_time_min=45.0,
        target_range_km=25.0,
        cruise_speed_kmh=60.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
    ("Military 1.5kg", RequirementModel(
        mission_type=MissionType.MILITARY,
        payload_weight_kg=1.5,
        target_flight_time_min=90.0,
        target_range_km=80.0,
        cruise_speed_kmh=85.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
    )),
]

def run_representative_cases():
    pipeline = FixedWingDesignPipeline()
    results = {}
    for name, req in CASES:
        res = pipeline.execute(req)
        spec = res.final_specification
        results[name] = {
            "success": res.success,
            "status": res.status.name,
            "iterations": res.iterations,
            "mtow": round(spec.mass_properties.maximum_takeoff_weight_kg, 4) if spec else None,
            "wing_area": round(spec.wing.wing_area, 4) if spec else None,
            "wingspan": round(spec.wing.wing_span, 4) if spec else None,
            "aspect_ratio": round(spec.wing.aspect_ratio, 2) if spec else None,
            "root_chord": round(spec.wing.root_chord, 4) if spec else None,
            "tail_config": spec.tail.tail_configuration if spec else None,
            "V_h": spec.tail.horizontal_volume_coefficient if spec else None,
            "V_v": spec.tail.vertical_volume_coefficient if spec else None,
            "tail_area": round(spec.tail.horizontal_tail_area_m2 + spec.tail.vertical_tail_area_m2, 4) if spec else None,
            "tail_s_h": spec.tail.horizontal_tail_area_m2 if spec else None,
            "tail_s_v": spec.tail.vertical_tail_area_m2 if spec else None,
            "tail_arm": spec.tail.tail_arm_m if spec else None,
            "cg_x": round(spec.cg.cg_position[0] if isinstance(spec.cg.cg_position, (list, tuple)) else spec.cg.cg_position, 4) if spec else None,
            "static_margin": round(spec.cg.static_margin, 2) if spec else None,
            "stall_speed": round(spec.performance.stall_speed_kmh, 2) if spec else None,
            "cruise_speed": round(spec.performance.cruise_speed_kmh, 2) if spec else None,
            "endurance_min": round(spec.performance.endurance_min, 2) if spec else None,
            "range_km": round(spec.performance.range_km, 2) if spec else None,
            "score": spec.tail.optimization_score if spec else None,
        }
        print(f"[{name}] success={res.success} MTOW={results[name]['mtow']} tail={results[name]['tail_config']} Vh={results[name]['V_h']} Vv={results[name]['V_v']} Sh={results[name]['tail_s_h']} Sv={results[name]['tail_s_v']} arm={results[name]['tail_arm']} score={results[name]['score']}")
    
    with open("scratch/baseline_representative_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Baseline saved to scratch/baseline_representative_results.json")
    return results

if __name__ == "__main__":
    run_representative_cases()

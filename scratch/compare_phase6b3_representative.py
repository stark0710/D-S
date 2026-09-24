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

def run_comparison():
    pipeline = FixedWingDesignPipeline()
    results = {}
    for name, req in CASES:
        res = pipeline.execute(req)
        spec = res.final_specification
        results[name] = {
            "success": res.success,
            "status": res.status.name,
            "iterations": res.iterations,
            "mtow_kg": round(spec.mass_properties.maximum_takeoff_weight_kg, 3) if spec else None,
            "battery_name": getattr(spec.propulsion, "battery_name", None),
            "battery_capacity_mah": getattr(spec.propulsion, "battery_capacity_mah", None),
            "battery_weight_g": getattr(spec.propulsion, "battery_weight_g", None),
            "battery_energy_wh": getattr(spec.propulsion, "battery_energy_wh", None),
            "required_energy_wh": getattr(spec.propulsion, "required_energy_wh", None),
            "battery_cell_count": getattr(spec.propulsion, "cell_count_s", None),
            "battery_voltage_v": getattr(spec.propulsion, "operating_voltage_v", None),
            "battery_chemistry": getattr(spec.propulsion, "battery_chemistry", None),
            "battery_c_rating": getattr(spec.propulsion, "battery_c_rating", None),
            "cruise_power_w": round(spec.propulsion.cruise_power_w, 1) if spec else None,
            "endurance_min": round(spec.performance.endurance_min, 1) if spec else None,
            "range_km": round(spec.performance.range_km, 1) if spec else None,
            "wing_area_m2": round(spec.wing.wing_area, 4) if spec else None,
            "wingspan_m": round(spec.wing.wing_span, 4) if spec else None,
            "cg_x": round(spec.cg.cg_position[0] if isinstance(spec.cg.cg_position, (list, tuple)) else spec.cg.cg_position, 3) if spec else None,
            "static_margin": round(spec.cg.static_margin, 3) if spec else None,
            "stall_speed_kmh": round(spec.performance.stall_speed_kmh, 1) if spec else None,
            "motor_name": getattr(spec.propulsion, "motor_name", None),
            "propeller_name": getattr(spec.propulsion, "propeller_name", None),
            "esc_name": getattr(spec.propulsion, "esc_name", None),
            "tail_config": getattr(spec.tail, "tail_configuration", None),
            "v_h": getattr(spec.tail, "horizontal_volume_coefficient", None),
            "v_v": getattr(spec.tail, "vertical_volume_coefficient", None),
        }
        print(f"[{name}] success={res.success} MTOW={results[name]['mtow_kg']}kg Batt={results[name]['battery_name']} ({results[name]['battery_capacity_mah']}mAh, {results[name]['battery_weight_g']}g) Endur={results[name]['endurance_min']}min P_cr={results[name]['cruise_power_w']}W iter={res.iterations}")

    with open("scratch/phase6b3_representative_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved to scratch/phase6b3_representative_results.json")

if __name__ == "__main__":
    run_comparison()

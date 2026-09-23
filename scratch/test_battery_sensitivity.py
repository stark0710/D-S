from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

def inspect_propulsion_candidates_sensitivity():
    # Test Survey 0.5kg with 20min vs 45min vs 80min
    times = [20.0, 30.0, 45.0, 60.0, 80.0]
    pipeline = FixedWingDesignPipeline()
    for t in times:
        req = RequirementModel(
            mission_type=MissionType.SURVEY,
            payload_weight_kg=0.5,
            target_flight_time_min=t,
            target_range_km=30.0,
            cruise_speed_kmh=70.0,
            takeoff_type=TakeoffType.RUNWAY,
            landing_type=LandingType.RUNWAY,
            environment=OperatingEnvironment.RURAL,
            optimization_priority=OptimizationPriority.BALANCED
        )
        res = pipeline.execute(req)
        spec = res.final_specification
        batt_name = getattr(spec.propulsion, "battery_name", None)
        batt_cap = getattr(spec.propulsion, "battery_capacity_mah", None)
        batt_w = getattr(spec.propulsion, "battery_weight_g", None)
        endurance = getattr(spec.performance, "endurance_min", None)
        mtow = getattr(spec.mass_properties, "maximum_takeoff_weight_kg", None)
        p_cruise = getattr(spec.propulsion, "cruise_power_w", None)
        print(f"Target: {t:4.1f} min | MTOW: {mtow:5.3f} kg | Batt: {batt_name} ({batt_cap} mAh, {batt_w} g) | Achieved Endur: {endurance:5.1f} min | P_cruise: {p_cruise} W")

if __name__ == "__main__":
    inspect_propulsion_candidates_sensitivity()

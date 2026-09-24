from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

req = RequirementModel(
    mission_type=MissionType.SURVEY,
    payload_weight_kg=0.5,
    target_flight_time_min=45.0,
    target_range_km=30.0,
    cruise_speed_kmh=70.0,
    takeoff_type=TakeoffType.RUNWAY,
    landing_type=LandingType.RUNWAY,
    environment=OperatingEnvironment.RURAL,
    optimization_priority=OptimizationPriority.BALANCED
)
res = FixedWingDesignPipeline().execute(req)
spec = res.final_specification
p = spec.propulsion
print(f"Motor: {p.motor_name}")
print(f"Propeller: {p.propeller_name}")
print(f"ESC: {p.esc_name}")
print(f"Battery: {p.battery_name}")
print(f"Capacity: {p.battery_capacity_mah} mAh, Weight: {p.battery_weight_g} g")
print(f"Cruise power: {p.cruise_power_w} W, Cruise current: {p.cruise_current_a} A")
print(f"Estimated flight time: {p.estimated_flight_time_min} min")
print(f"MTOW: {spec.mass_properties.maximum_takeoff_weight_kg} kg")

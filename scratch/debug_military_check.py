import sys
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

req = RequirementModel(
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
)

import backend.design.fixed_wing.propulsion.optimization.constraints as c_mod
orig_check = c_mod.check_mission_energy_sufficiency

def debug_check(candidate, context):
    passed, reason = orig_check(candidate, context)
    ft = candidate.derived_variables.get("estimated_flight_time_min", 0.0)
    p_cr = candidate.derived_variables.get("cruise_power_w", 0.0)
    batt = candidate.design_variables["battery"]["name"]
    print(f"Cand batt={batt:35} | P_cr={p_cr:5.1f}W | ft={ft:5.1f}min | passed={passed}")
    return passed, reason

c_mod.check_mission_energy_sufficiency = debug_check

pipeline = FixedWingDesignPipeline()
pipeline.execute(req)

import sys, os
sys.path.insert(0, os.path.abspath("."))
import math
from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.common.requirements.aircraft_type import AircraftType
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

cases = [
    ('Survey 0.5kg', MissionType.SURVEY, 0.5, 45.0, 30.0, 70.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL),
    ('Survey 1.0kg', MissionType.SURVEY, 1.0, 45.0, 30.0, 70.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL),
    ('Agriculture 2.0kg', MissionType.AGRICULTURE, 2.0, 35.0, 25.0, 65.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL),
    ('Security 0.5kg', MissionType.SECURITY, 0.5, 60.0, 40.0, 75.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL),
    ('Inspection 0.5kg', MissionType.INSPECTION, 0.5, 40.0, 25.0, 60.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL),
    ('Delivery 1.0kg (Twin)', MissionType.DELIVERY, 1.0, 45.0, 40.0, 80.0, TakeoffType.RUNWAY, LandingType.RUNWAY, OperatingEnvironment.RURAL),
]

pipeline = FixedWingDesignPipeline()
for name, m_type, payload, f_time, rng, spd, to, ld, env in cases:
    req = RequirementModel(
        mission_type=m_type,
        payload_weight_kg=payload,
        target_flight_time_min=f_time,
        target_range_km=rng,
        cruise_speed_kmh=spd,
        takeoff_type=to,
        landing_type=ld,
        environment=env,
        optimization_priority=OptimizationPriority.BALANCED,
        design_mode=DesignMode.ENGINEERING_ADVISOR,
        aircraft_type=AircraftType.FIXED_WING,
    )
    res = pipeline.execute(req)
    wb = res.mass_properties_result.weight_breakdown
    pa = res.propulsion_result.power_analysis
    ec = pa.metadata.get('engine_count', 1)
    comps = res.mass_properties_result.component_masses
    sum_comps = sum(c.mass_kg for c in comps)
    mass_spec = res.subsystem_specifications.get('MassPropertiesSpecification') if hasattr(res, 'subsystem_specifications') else None
    mtow_spec = getattr(mass_spec, 'maximum_takeoff_weight_kg', sum_comps)
    print(f"=== {name} ===")
    print(f"Status: {res.status}")
    print(f"MTOW: {sum_comps:.3f} kg")
    print(f"Engine Count: {ec}")
    static_thrust = res.propulsion_result.thrust_analysis.estimated_static_thrust_n
    print(f"Static Thrust: {static_thrust:.2f} N")
    print(f"Cruise Power: {pa.required_cruise_power_w:.1f} W")
    print(f"Battery Mass: {wb.battery_fuel_weight_kg:.3f} kg")
    print(f"Propulsion Mass: {wb.propulsion_weight_kg:.3f} kg")
    diff = abs(sum_comps - mtow_spec)
    print(f"Mass Conservation: sum={sum_comps:.3f} kg, MTOW_spec={mtow_spec:.3f} kg, diff={diff:.4f}")
    assert diff < 0.005, f"Mass conservation failed: diff={diff}"
    print(f"TW Ratio: {res.propulsion_result.thrust_analysis.thrust_to_weight_ratio:.3f}")

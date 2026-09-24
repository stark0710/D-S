import sys
import os
sys.path.insert(0, os.getcwd())

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline

from scripts.run_fixed_wing_pipeline import audit_mass_accounting

def run_case(p_wt=0.5, t_min=45.0, r_km=30.0, budget=15000.0):
    req = RequirementModel(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=p_wt,
        target_flight_time_min=t_min,
        target_range_km=r_km,
        cruise_speed_kmh=70.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
        budget=budget
    )
    res = FixedWingDesignPipeline().execute(req)
    if not res.success:
        return {
            "success": False,
            "status": str(res.status),
            "mtow": 0.0,
            "span": 0.0,
            "area": 0.0,
            "bat_mass": 0.0,
            "struct_mass": 0.0,
            "power": 0.0,
            "endurance": 0.0,
            "actual_range": 0.0,
            "motor": "N/A",
            "error": res.errors[0] if res.errors else "Unknown"
        }

    audit = audit_mass_accounting(res)
    mtow = audit["reported_mtow_kg"]
    bat_mass = audit["battery_mass_kg"]
    struct_mass = audit["structural_mass_kg"]
    span = 0.0
    area = 0.0
    pwr = 0.0
    endur = 0.0
    actual_range = 0.0
    motor = "N/A"

    if res.wing_result:
        wg = getattr(res.wing_result, "wing_geometry", res.wing_result)
        span = getattr(wg, "span_m", 0.0)
        area = getattr(wg, "reference_area_m2", getattr(wg, "area_m2", 0.0))
    if res.propulsion_result:
        pr = res.propulsion_result
        motor = getattr(pr, "selected_motor_or_engine", getattr(pr, "selected_motor", "N/A"))
        pa = getattr(pr, "power_analysis", None)
        if pa:
            pwr = getattr(pa, "required_cruise_power_w", 0.0)
    if res.performance_result:
        pf = res.performance_result
        if hasattr(pf, "endurance_analysis"):
            endur = getattr(pf.endurance_analysis, "cruise_endurance_min", 0.0)
        if hasattr(pf, "range_analysis"):
            actual_range = getattr(pf.range_analysis, "cruise_range_km", 0.0)

    return {
        "success": res.success,
        "status": str(res.status),
        "mtow": round(mtow, 4),
        "span": round(span, 3),
        "area": round(area, 4),
        "bat_mass": round(bat_mass, 4),
        "struct_mass": round(struct_mass, 4),
        "power": round(pwr, 1),
        "endurance": round(endur, 1),
        "actual_range": round(actual_range, 1),
        "motor": str(motor),
    }

print("=== STEP 10A: RANGE SENSITIVITY (WITH MATCHED FLIGHT TIME) ===")
range_cases = [
    (20.0, 30.0),
    (30.0, 45.0),
    (50.0, 60.0),
    (70.0, 75.0),
    (80.0, 80.0),
]
for r, t in range_cases:
    out = run_case(r_km=r, t_min=t)
    print(f"Range: {r:>2.0f}km (t={t:>2.0f}m) | MTOW: {out['mtow']:>5.3f}kg | Bat: {out['bat_mass']:>5.3f}kg | Area: {out['area']:>6.4f}m2 | Pwr: {out['power']:>5.1f}W | Act R: {out['actual_range']:>5.1f}km | Act Endur: {out['endurance']:>5.1f}m")

print("\n=== STEP 10B: ENDURANCE SENSITIVITY (FIXED RANGE = 25 km) ===")
times = [30.0, 45.0, 60.0, 90.0]
for t in times:
    out = run_case(t_min=t, r_km=25.0)
    print(f"Target Time: {t:>3.0f} min | MTOW: {out['mtow']:>5.3f}kg | Bat: {out['bat_mass']:>5.3f}kg | Area: {out['area']:>6.4f}m2 | Pwr: {out['power']:>5.1f}W | Act Endur: {out['endurance']:>5.1f}min")

print("\n=== STEP 11: BUDGET SENSITIVITY (500, 2000, 15000, 50000 USD) ===")
budgets = [500.0, 2000.0, 15000.0, 50000.0]
for b in budgets:
    out = run_case(budget=b, r_km=30.0, t_min=45.0)
    print(f"Budget: {b:>7.0f} USD | MTOW: {out['mtow']:>5.3f}kg | Motor: {out['motor']} | Pwr: {out['power']:>5.1f}W")

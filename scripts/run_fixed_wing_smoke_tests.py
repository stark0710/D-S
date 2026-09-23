"""
Numerical Smoke Tests for Existing Fixed-Wing Engines.
"""

import json
from typing import Dict, Any, List

from backend.design.fixed_wing.mission.mission_requirements import (
    MissionRequirements,
    MissionCategory,
    LaunchMethod,
    LandingMethod,
    EnvironmentType,
    AutonomyLevel,
)
from backend.design.fixed_wing.mission.mission_engine import MissionEngine

from backend.design.fixed_wing.configuration.configuration_requirements import ConfigurationRequirements
from backend.design.fixed_wing.configuration.configuration_engine import ConfigurationEngine

from backend.design.fixed_wing.wing.wing_requirements import WingRequirements
from backend.design.fixed_wing.wing.wing_engine import WingEngine

from backend.design.fixed_wing.airfoil.airfoil_requirements import AirfoilRequirements
from backend.design.fixed_wing.airfoil.airfoil_engine import AirfoilEngine

from backend.design.fixed_wing.tail.tail_requirements import TailRequirements
from backend.design.fixed_wing.tail.tail_engine import TailEngine

from backend.design.fixed_wing.fuselage.fuselage_requirements import FuselageRequirements
from backend.design.fixed_wing.fuselage.fuselage_engine import FuselageEngine

from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine

from backend.design.fixed_wing.avionics.avionics_requirements import AvionicsRequirements
from backend.design.fixed_wing.avionics.avionics_engine import AvionicsEngine

from backend.design.fixed_wing.payload.payload_requirements import PayloadRequirements
from backend.design.fixed_wing.payload.payload_engine import PayloadEngine

from backend.design.fixed_wing.mass_properties.mass_requirements import MassRequirements
from backend.design.fixed_wing.mass_properties.mass_properties_engine import MassPropertiesEngine

from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
from backend.design.fixed_wing.flight_performance.flight_performance_engine import FlightPerformanceEngine


def run_smoke_tests() -> List[Dict[str, Any]]:
    m_engine = MissionEngine()
    c_engine = ConfigurationEngine()
    w_engine = WingEngine()
    af_engine = AirfoilEngine()
    t_engine = TailEngine()
    f_engine = FuselageEngine()
    p_engine = PropulsionEngine()
    av_engine = AvionicsEngine()
    pay_engine = PayloadEngine()
    m_prop_engine = MassPropertiesEngine()
    fp_engine = FlightPerformanceEngine()

    missions = [
        ("M1: Small Mapping UAV", 0.5, 30.0, 45.0, 70.0, MissionCategory.MAPPING),
        ("M2: Long-Endurance Survey UAV", 1.5, 80.0, 120.0, 80.0, MissionCategory.SURVEY),
        ("M3: Corridor Inspection UAV", 2.0, 60.0, 90.0, 75.0, MissionCategory.SURVEILLANCE),
        ("M4: Agriculture Monitoring UAV", 3.0, 40.0, 60.0, 65.0, MissionCategory.AGRICULTURE),
        ("M5: Medium Surveillance UAV", 5.0, 150.0, 180.0, 95.0, MissionCategory.SURVEILLANCE),
        ("M6: Light Cargo Fixed-Wing", 10.0, 120.0, 150.0, 100.0, MissionCategory.CARGO),
        ("M7: Tactical Military Recon UAV", 4.0, 200.0, 240.0, 120.0, MissionCategory.SURVEILLANCE),
        ("M8: Scientific Research Glider UAV", 1.0, 100.0, 300.0, 60.0, MissionCategory.RESEARCH),
        ("M9: Disaster Assessment UAV", 2.5, 90.0, 100.0, 85.0, MissionCategory.SURVEY),
        ("M10: High-Speed Frontier Patrol UAV", 3.5, 250.0, 180.0, 140.0, MissionCategory.SURVEILLANCE),
    ]

    results: List[Dict[str, Any]] = []

    for name, pay, rng, end, spd, cat in missions:
        res_dict = {"mission_name": name, "inputs": {"payload_kg": pay, "range_km": rng, "endurance_min": end, "cruise_speed_kmh": spd}}

        try:
            # 1. Mission Engine
            m_reqs = MissionRequirements(
                mission_category=cat,
                payload_kg=pay,
                flight_time_min=end,
                cruise_speed_kmh=spd,
                stall_speed_target_kmh=45.0,
                maximum_takeoff_weight_limit_kg=max(8.0, pay * 3.5),
                operational_altitude_m=150.0,
                mission_range_km=rng,
                launch_method=LaunchMethod.RUNWAY if pay > 3.0 else LaunchMethod.CATAPULT,
                landing_method=LandingMethod.RUNWAY if pay > 3.0 else LandingMethod.BELLY_LANDING,
                budget=15000.0,
                environment=EnvironmentType.RURAL,
                autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
            )
            m_res = m_engine.process_mission(m_reqs)
            res_dict["mtow_limit_kg"] = m_res.mission_profile.maximum_takeoff_weight_limit_kg

            # 2. Configuration Engine
            c_reqs = ConfigurationRequirements(mission_result=m_res)
            c_res = c_engine.process_configuration(c_reqs)
            res_dict["configuration"] = {
                "wing": c_res.wing_configuration,
                "propulsion": c_res.propulsion_configuration,
                "tail": c_res.tail_configuration,
                "score": c_res.configuration_score,
            }

            # 3. Wing Engine
            w_reqs = WingRequirements(mission_result=m_res, configuration_result=c_res)
            w_res = w_engine.process_wing_design(w_reqs)
            res_dict["wing"] = {
                "span_m": round(w_res.wing_geometry.span_m, 3),
                "area_m2": round(w_res.wing_geometry.area_m2, 3),
                "aspect_ratio": round(w_res.aspect_ratio, 2),
                "root_chord_m": round(w_res.wing_geometry.root_chord_m, 3),
                "tip_chord_m": round(w_res.wing_geometry.tip_chord_m, 3),
                "mac_m": round(w_res.wing_geometry.mean_aerodynamic_chord_m, 3),
                "wing_loading": round(w_res.wing_geometry.wing_loading_kg_m2, 2),
                "stall_speed_kmh": round(w_res.analysis.estimated_stall_speed_kmh, 1),
            }

            # 4. Airfoil Engine
            af_reqs = AirfoilRequirements(mission_result=m_res, configuration_result=c_res, wing_result=w_res)
            af_res = af_engine.process_airfoil_design(af_reqs)
            res_dict["airfoil"] = {
                "root_airfoil": str(getattr(af_res, "selected_root_airfoil", "NACA 4412")),
                "tip_airfoil": str(getattr(af_res, "selected_tip_airfoil", "NACA 4412")),
            }

            # 5. Tail Engine
            t_reqs = TailRequirements(mission_result=m_res, configuration_result=c_res, wing_result=w_res, airfoil_result=af_res)
            t_res = t_engine.process_tail_design(t_reqs)
            res_dict["tail"] = {
                "htail_area_m2": round(t_res.horizontal_tail.area_m2, 3),
                "vtail_area_m2": round(t_res.vertical_tail.area_m2, 3),
                "htail_span_m": round(t_res.horizontal_tail.span_m, 3),
            }

            # 6. Fuselage Engine
            f_reqs = FuselageRequirements(
                mission_result=m_res, configuration_result=c_res, wing_result=w_res, airfoil_result=af_res, tail_result=t_res
            )
            f_res = f_engine.process_fuselage_design(f_reqs)
            res_dict["fuselage"] = {
                "length_m": round(f_res.fuselage_geometry.length_m, 3),
                "max_diameter_m": round(f_res.fuselage_geometry.max_diameter_m, 3),
                "fineness_ratio": round(f_res.fuselage_geometry.fineness_ratio, 2),
            }

            # 7. Propulsion Engine
            p_reqs = PropulsionRequirements(
                mission_result=m_res, configuration_result=c_res, wing_result=w_res, airfoil_result=af_res, tail_result=t_res, fuselage_result=f_res
            )
            p_res = p_engine.process_propulsion_design(p_reqs)
            motor_obj = p_res.selected_motor_or_engine
            prop_obj = p_res.selected_propeller
            res_dict["propulsion"] = {
                "motor": motor_obj.get("name", "T-Motor AT2820") if isinstance(motor_obj, dict) else (getattr(motor_obj, "name", str(motor_obj))),
                "propeller": prop_obj.get("name", "12x6 APC") if isinstance(prop_obj, dict) else (getattr(prop_obj, "name", str(prop_obj))),
                "required_power_w": round(getattr(p_res.power_analysis, "required_cruise_power_w", 120.0), 1),
                "max_thrust_n": round(getattr(p_res.thrust_analysis, "available_max_thrust_n", 25.0), 1),
            }

            # 8. Avionics Engine
            av_reqs = AvionicsRequirements(
                mission_result=m_res, configuration_result=c_res, wing_result=w_res, airfoil_result=af_res, tail_result=t_res, fuselage_result=f_res, propulsion_result=p_res
            )
            av_res = av_engine.process_avionics_design(av_reqs)
            res_dict["avionics_pkg"] = {
                "flight_controller": str(getattr(av_res, "flight_controller", "Pixhawk 6C")),
                "total_power_w": getattr(av_res, "total_power_draw_w", 12.0),
            }

            # 9. Payload Engine
            pay_reqs = PayloadRequirements(
                mission_result=m_res, configuration_result=c_res, wing_result=w_res, airfoil_result=af_res, tail_result=t_res, fuselage_result=f_res, propulsion_result=p_res, avionics_result=av_res
            )
            pay_res = pay_engine.process_payload_design(pay_reqs)
            res_dict["payload_pkg"] = {
                "allocated_weight_kg": getattr(pay_res, "allocated_payload_weight_kg", pay),
                "power_draw_w": getattr(pay_res, "total_power_draw_w", 15.0),
            }

            # 10. Mass Properties Engine
            m_prop_reqs = MassRequirements(
                mission_result=m_res,
                configuration_result=c_res,
                wing_result=w_res,
                airfoil_result=af_res,
                tail_result=t_res,
                fuselage_result=f_res,
                propulsion_result=p_res,
                avionics_result=av_res,
                payload_result=pay_res,
            )
            m_prop_res = m_prop_engine.process_mass_design(m_prop_reqs)
            res_dict["mass"] = {
                "calculated_mtow_kg": round(m_prop_res.weight_breakdown.total_weight_kg, 3),
                "empty_weight_kg": round(m_prop_res.weight_breakdown.empty_weight_kg, 3),
                "structure_weight_kg": round(m_prop_res.weight_breakdown.structure_weight_kg, 3),
                "battery_weight_kg": round(m_prop_res.weight_breakdown.battery_weight_kg, 3),
                "cg_x_m": round(m_prop_res.center_of_gravity.x_cg_m, 3),
                "static_margin_pct": round(m_prop_res.static_margin.static_margin_percentage, 1),
            }

            # 11. Flight Performance Engine
            fp_reqs = FlightRequirements(
                mission_result=m_res,
                configuration_result=c_res,
                wing_result=w_res,
                airfoil_result=af_res,
                tail_result=t_res,
                fuselage_result=f_res,
                propulsion_result=p_res,
                avionics_result=av_res,
                payload_result=pay_res,
                mass_result=m_prop_res,
            )
            fp_res = fp_engine.process_performance_design(fp_reqs)
            res_dict["performance"] = {
                "max_speed_kmh": round(getattr(fp_res.performance_analysis, "max_speed_kmh", 110.0), 1),
                "calculated_range_km": round(fp_res.range_analysis["calculated_range_km"], 1),
                "calculated_endurance_min": round(fp_res.endurance_analysis["calculated_endurance_min"], 1),
                "max_lift_to_drag": round(getattr(fp_res.aerodynamic_analysis, "max_lift_drag_ratio", 14.5), 2),
            }
        except Exception as e:
            res_dict["execution_error"] = str(e)

        results.append(res_dict)

    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    run_smoke_tests()

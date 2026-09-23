"""
Fixed-Wing Flight Performance Sizing Engine Subsystem

Purpose:
    Defines the `FlightPerformanceEngine` class, which serves as the orchestrator for the Performance Sizing Framework.

Role in Architecture:
    `FlightPerformanceEngine` coordinates environmental models, lift/drag polars, climb rates,
    takeoff/landing rolls, glide ranges, and stability margins, running validations.
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime
import math

from backend.design.fixed_wing.flight_performance.flight_requirements import FlightRequirements
from backend.design.fixed_wing.flight_performance.flight_profile import FlightProfile
from backend.design.fixed_wing.flight_performance.flight_constraints import FlightConstraints
from backend.design.fixed_wing.flight_performance.flight_result import FlightResult
from backend.design.fixed_wing.flight_performance.flight_validator import FlightValidator
from backend.design.fixed_wing.flight_performance.flight_registry import FlightStrategyRegistry
from backend.design.fixed_wing.flight_performance.environment_model import EnvironmentModel
from backend.design.fixed_wing.flight_performance.aerodynamic_analysis import AerodynamicAnalysis
from backend.design.fixed_wing.flight_performance.performance_analysis import PerformanceAnalysis
from backend.design.fixed_wing.flight_performance.takeoff_analysis import TakeoffAnalysis
from backend.design.fixed_wing.flight_performance.landing_analysis import LandingAnalysis
from backend.design.fixed_wing.flight_performance.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.flight_performance.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.flight_performance.descent_analysis import DescentAnalysis
from backend.design.fixed_wing.flight_performance.stall_analysis import StallAnalysis
from backend.design.fixed_wing.flight_performance.glide_analysis import GlideAnalysis
from backend.design.fixed_wing.flight_performance.turn_performance import TurnAnalysis
from backend.design.fixed_wing.flight_performance.range_analysis import RangeAnalysis
from backend.design.fixed_wing.flight_performance.endurance_analysis import EnduranceAnalysis
from backend.design.fixed_wing.flight_performance.ceiling_analysis import CeilingAnalysis
from backend.design.fixed_wing.flight_performance.stability_analysis import StabilityAnalysis
from backend.design.fixed_wing.flight_performance.maneuver_analysis import ManeuverAnalysis
from backend.design.fixed_wing.flight_performance.mission_performance import MissionPerformance


class FlightPerformanceEngine:
    """
    Orchestrator driving the fixed-wing flight performance predictions and validation audits.
    """

    def __init__(
        self,
        env_model: EnvironmentModel | None = None,
        validator: FlightValidator | None = None,
    ) -> None:
        self._env_model = env_model if env_model else EnvironmentModel()
        self._validator = validator if validator else FlightValidator()

    def process_performance_design(
        self,
        requirements: FlightRequirements,
        profile: FlightProfile | None = None,
        validate: bool = True,
    ) -> FlightResult:
        """
        Calculates and validates standard flight performance.

        Args:
            requirements (FlightRequirements): Sizing requirements context.
            profile (FlightProfile | None): references and ground constants.

        Returns:
            FlightResult: Speeds, rolls, glide efficiency, ranges, and mission scores.
        """
        if profile is None:
            profile = FlightProfile()

        g = profile.gravity_m_s2
        m_profile = requirements.mission_result.mission_profile
        category = m_profile.mission_category
        wing_geom = requirements.wing_result.wing_geometry
        mass_result = requirements.mass_result
        prop_result = requirements.propulsion_result
        av_result = requirements.avionics_result
        pay_result = requirements.payload_result

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = FlightStrategyRegistry.get(strategy_name)

        # target margins
        min_climb_target, cruise_margin = strategy.get_performance_margins()
        stall_margin = strategy.get_stall_speed_margin_pct()

        # Define constraints
        constraints = FlightConstraints(
            min_range_km=m_profile.mission_range_km,
            min_endurance_min=m_profile.flight_time_min,
            max_takeoff_distance_m=100.0,
            max_landing_distance_m=100.0,
            min_rate_of_climb_m_s=min_climb_target,
        )

        # Total MTOW and Wing parameters
        mtow = mass_result.weight_breakdown.useful_load_kg + mass_result.weight_breakdown.structural_weight_kg + mass_result.weight_breakdown.propulsion_weight_kg + mass_result.weight_breakdown.avionics_weight_kg
        weight_n = mtow * g
        wing_area = wing_geom.reference_area_m2
        aspect_ratio = wing_geom.aspect_ratio

        # 2. ISA Atmospheric calculations
        altitude = m_profile.operational_altitude_m
        rho, pressure, temp = self._env_model.get_atmospheric_properties(altitude)

        # 3. Sizing Aerodynamic polars
        # Parasite drag coefficient Cd0 (clean balsa/EPO glider baseline)
        cd0 = 0.023
        # Oswald efficiency factor e
        oswald = 0.82
        induced_drag_factor = 1.0 / (math.pi * aspect_ratio * oswald)

        v_cruise_m_s = m_profile.cruise_speed_kmh / 3.6
        q_cruise = 0.5 * rho * (v_cruise_m_s ** 2)
        cl_cruise = weight_n / max(0.1, q_cruise * wing_area)
        cl_cruise = max(0.1, min(1.2, cl_cruise))

        cd_cruise = cd0 + induced_drag_factor * (cl_cruise ** 2)
        l_d_cruise = cl_cruise / cd_cruise

        aerodynamic = AerodynamicAnalysis(
            cruise_lift_coefficient=round(cl_cruise, 3),
            cruise_drag_coefficient=round(cd_cruise, 4),
            lift_to_drag_ratio=round(l_d_cruise, 2),
            zero_lift_drag_coefficient=cd0,
            induced_drag_factor=round(induced_drag_factor, 4),
        )

        # 4. Sizing stall boundaries
        cl_max = max(1.2, requirements.airfoil_result.polar_data.max_lift_coeff)
        cl_max_landing = cl_max + 0.35  # full flaps deflection adds lift
        
        v_stall_m_s = math.sqrt((2.0 * weight_n) / max(0.1, rho * wing_area * cl_max))
        v_stall_landing_m_s = math.sqrt((2.0 * weight_n) / max(0.1, rho * wing_area * cl_max_landing))

        stall = StallAnalysis(
            stall_speed_clean_kmh=round(v_stall_m_s * 3.6, 1),
            stall_speed_landing_kmh=round(v_stall_landing_m_s * 3.6, 1),
            stall_angle_of_attack_deg=requirements.airfoil_result.polar_data.stall_angle_deg,
            stall_characteristics_warning="docile nose drop" if requirements.airfoil_result.polar_data.stall_angle_deg >= 12.0 else "Aggressive tip stall risk",
        )

        # Minimum controllable airspeed
        v_mc_m_s = 1.15 * v_stall_m_s

        # Maximum top speed at full throttle
        # P_max_shaft * eta = Drag * V_max = 0.5 * rho * V_max^3 * S * Cd0
        p_max_shaft = prop_result.power_analysis.maximum_power_w
        eta_prop = prop_result.efficiency_analysis.propeller_efficiency
        v_max_m_s = ((2.0 * p_max_shaft * eta_prop) / max(0.01, rho * wing_area * cd0)) ** (1.0 / 3.0)

        # 5. Takeoff performance
        # S_takeoff = 2.0 * (W/S) / ( rho * (T/W) * CL_takeoff )
        t_to_w = prop_result.thrust_analysis.thrust_to_weight_ratio
        cl_takeoff = cl_max * 0.8
        takeoff_dist = (2.0 * wing_geom.wing_loading_kg_m2) / max(0.01, rho * t_to_w * cl_takeoff)
        
        v_rotation = 1.25 * v_stall_m_s
        accel_to = v_rotation / max(0.1, (t_to_w * g) - (profile.ground_friction_coefficient * g))

        takeoff = TakeoffAnalysis(
            takeoff_distance_m=round(takeoff_dist, 2),
            rotation_speed_m_s=round(v_rotation, 2),
            ground_acceleration_m_s2=round(v_rotation / accel_to, 2),
            takeoff_duration_s=round(accel_to, 2),
        )

        # 6. Landing performance
        # S_landing = 0.48 * (W/S) / ( rho * CL_max * braking_coeff )
        braking_coeff = getattr(profile, "braking_coefficient", 0.4)
        landing_dist = (0.48 * wing_geom.wing_loading_kg_m2) / max(0.01, rho * cl_max_landing * braking_coeff)
        v_approach = 1.30 * v_stall_landing_m_s
        accel_land = v_approach / 4.5  # standard landing ground roll run time: 4.5s

        landing = LandingAnalysis(
            landing_distance_m=round(landing_dist, 2),
            approach_speed_m_s=round(v_approach, 2),
            braking_deceleration_m_s2=round(v_approach / accel_land, 2),
            landing_duration_s=round(accel_land, 2),
        )

        # 7. Sizing climbs and descents
        # ROC = Excess Power / Weight = (P_shaft * eta_total - Drag * V) / W
        eta_total = prop_result.efficiency_analysis.total_system_efficiency
        drag_cruise_n = cd_cruise * q_cruise * wing_area
        climb_speed_m_s = 1.15 * v_stall_m_s
        
        p_excess = (p_max_shaft * eta_total) - (drag_cruise_n * climb_speed_m_s)
        p_excess = max(40.0, p_excess)
        roc = p_excess / weight_n
        climb_angle = math.degrees(math.asin(max(-0.9, min(0.9, roc / climb_speed_m_s))))

        climb = ClimbAnalysis(
            rate_of_climb_m_s=round(roc, 2),
            climb_angle_deg=round(climb_angle, 1),
            climb_speed_m_s=round(climb_speed_m_s, 2),
            time_to_altitude_min=round(altitude / (roc * 60.0), 2),
        )

        # Rate of descent (glide slope)
        rod = v_cruise_m_s / max(1.0, l_d_cruise)
        descent_angle = math.degrees(math.asin(rod / v_cruise_m_s))
        descent = DescentAnalysis(
            rate_of_descent_m_s=round(rod, 2),
            descent_angle_deg=round(descent_angle, 1),
            descent_speed_m_s=round(v_cruise_m_s, 2),
        )

        # 8. Cruise required parameters
        cruise = CruiseAnalysis(
            cruise_speed_kmh=m_profile.cruise_speed_kmh,
            thrust_required_n=round(drag_cruise_n, 2),
            power_required_w=round(prop_result.power_analysis.required_cruise_power_w, 1),
            throttle_setting_pct=round(prop_result.cruise_analysis.throttle_setting_pct, 1),
            cruise_lift_coefficient=round(cl_cruise, 3),
        )

        # 9. Gliding performance
        best_l_d = 1.0 / (2.0 * math.sqrt(cd0 * induced_drag_factor))
        glide_angle = math.degrees(math.atan(1.0 / best_l_d))
        sink_min = v_cruise_m_s * math.sin(math.radians(glide_angle))

        glide = GlideAnalysis(
            glide_ratio=round(best_l_d, 2),
            minimum_glide_angle_deg=round(glide_angle, 1),
            sink_rate_min_m_s=round(sink_min, 2),
        )

        # 10. Turning performance
        bank_angle = 30.0
        load_factor = 1.0 / math.cos(math.radians(bank_angle))
        turn_r = (v_cruise_m_s ** 2) / (g * math.sqrt(load_factor**2 - 1.0))
        turn_rate = math.degrees(g * math.sqrt(load_factor**2 - 1.0) / v_cruise_m_s)

        turn = TurnAnalysis(
            turn_radius_m=round(turn_r, 2),
            load_factor=round(load_factor, 2),
            bank_angle_deg=bank_angle,
            turn_rate_deg_s=round(turn_rate, 2),
        )

        # 11. Sizing range and endurance
        # Sized battery capacity: energy = battery_weight * 200.0 Wh/kg
        batt_mass = mass_result.weight_breakdown.battery_fuel_weight_kg
        battery_energy_wh = batt_mass * 200.0

        # continuous power draw: cruise power + avionics power + payload power
        p_av = av_result.power_analysis.continuous_power_w
        p_pay = pay_result.payload_analysis.power_consumption_w
        p_continuous = prop_result.power_analysis.required_cruise_power_w + p_av + p_pay

        # Max endurance minutes
        endurance_min = (battery_energy_wh / max(1.0, p_continuous)) * 60.0
        # Cruise range km
        range_km = (endurance_min / 60.0) * m_profile.cruise_speed_kmh

        range_anal = RangeAnalysis(
            maximum_range_km=round(range_km, 2),
            cruise_range_km=round(range_km * 0.85, 2),  # 15% battery safety margin reserve
            energy_consumption_rate_wh_km=round(p_continuous / m_profile.cruise_speed_kmh, 2),
        )

        endurance = EnduranceAnalysis(
            maximum_endurance_min=round(endurance_min, 2),
            cruise_endurance_min=round(endurance_min * 0.85, 2),
            average_power_draw_w=round(p_continuous, 1),
        )

        # 12. Absolute and Service Ceilings
        # Ceiling estimation: ROC decreases linearly with altitude density loss
        ceiling_alt = altitude + (roc / 0.00078)
        service_alt = ceiling_alt - 300.0

        ceiling = CeilingAnalysis(
            absolute_ceiling_m=round(ceiling_alt, 0),
            service_ceiling_m=round(service_alt, 0),
            density_altitude_limit_m=round(ceiling_alt, 0),
        )

        wing_x = getattr(requirements.fuselage_result.fuselage_geometry, 'wing_attachment_x_m', 0.35 * requirements.fuselage_result.fuselage_geometry.length_m)
        tail_config = requirements.tail_result.tail_configuration if requirements.tail_result else None
        np_pct = 0.42 if tail_config == "Conventional" else (0.25 if tail_config == "Tailless" else 0.38)
        neutral_point_x_m = wing_x + wing_geom.quarter_chord_x_m + np_pct * wing_geom.mean_aerodynamic_chord_m

        stability = StabilityAnalysis(
            static_margin=round(mass_result.static_margin, 3),
            pitch_stability_level="Stable" if mass_result.static_margin >= 0.08 else "Marginal",
            yaw_stability_level="Stable",
            roll_stability_level="Stable",
            neutral_point_x_m=round(neutral_point_x_m, 3),
        )

        # 14. maneuvering structural limits
        maneuver = ManeuverAnalysis(
            max_load_factor=2.5,  # standard utility fixed wing G-limit
            maneuvering_speed_kmh=round(v_stall_m_s * math.sqrt(2.5) * 3.6, 1),
            max_bank_angle_deg=60.0,
        )

        # 15. Mission performance probabilities
        prob = 95.0
        # If range or endurance is close to constraint limits, decrease score
        if range_km < m_profile.mission_range_km:
            prob -= 30.0
        if endurance_min < m_profile.flight_time_min:
            prob -= 20.0

        mission = MissionPerformance(
            mission_completion_probability=round(prob, 1),
            critical_phase_suitability="Fully Compliant" if prob >= 80.0 else "Critical Range Warning",
            energy_margin_pct=round(((range_km - m_profile.mission_range_km) / max(0.1, range_km)) * 100.0, 1),
        )

        # Sizing summary scores
        perf_anal = PerformanceAnalysis(
            maximum_speed_kmh=round(v_max_m_s * 3.6, 1),
            cruise_speed_kmh=m_profile.cruise_speed_kmh,
            minimum_controllable_speed_kmh=round(v_mc_m_s * 3.6, 1),
            best_glide_ratio=round(best_l_d, 2),
            max_rate_of_climb_m_s=round(roc, 2),
        )

        # 16. Validate sized performance
        warnings = []
        if validate:
            warnings = self._validator.validate(
                requirements=requirements,
                constraints=constraints,
                profile=profile,
                perf=perf_anal,
                to_anal=takeoff,
                land_anal=landing,
                cl_anal=climb,
                r_anal=range_anal,
                ed_anal=endurance,
                stab_anal=stability,
                stall_margin_pct=stall_margin,
                stall=stall,
            )

        # 17. Compile notes and recommendations
        engineering_notes = [
            f"Flight strategy applied: {strategy.name}.",
            f"takeoff distance: {takeoff.takeoff_distance_m:.1f} m, landing braking distance: {landing.landing_distance_m:.1f} m.",
            f"maximum range: {range_anal.maximum_range_km:.1f} km, flight time endurance: {endurance.maximum_endurance_min:.1f} minutes.",
            f"maximum rate of climb: {climb.rate_of_climb_m_s:.2f} m/s, best glide L/D: {glide.glide_ratio:.1f}.",
            f"aerodynamic efficiency score: {aerodynamic.lift_to_drag_ratio:.1f} L/D.",
        ]
        
        recommendations = strategy.get_recommendations()

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
        }

        # 18. Return compiled FlightResult
        return FlightResult(
            aerodynamic_analysis=aerodynamic,
            performance_analysis=perf_anal,
            takeoff_analysis=takeoff,
            landing_analysis=landing,
            climb_analysis=climb,
            cruise_analysis=cruise,
            descent_analysis=descent,
            stall_analysis=stall,
            glide_analysis=glide,
            turn_analysis=turn,
            range_analysis=range_anal,
            endurance_analysis=endurance,
            ceiling_analysis=ceiling,
            stability_analysis=stability,
            mission_performance=mission,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )

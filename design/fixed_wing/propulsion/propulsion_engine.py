"""
Fixed-Wing Propulsion Engine Subsystem

Purpose:
    Defines the `PropulsionEngine` class, which serves as the orchestrator for the Propulsion Engineering Framework.

Role in Architecture:
    `PropulsionEngine` coordinates sizers, selectors, moment balances, dynamic analyses,
    and validation rules to size motor/engine systems and propellers.
"""

from typing import List, Dict, Any
from datetime import datetime
import math

from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements, PropulsionType, PropulsionLayout
from backend.design.fixed_wing.propulsion.propulsion_profile import PropulsionProfile
from backend.design.fixed_wing.propulsion.propulsion_constraints import PropulsionConstraints
from backend.design.fixed_wing.propulsion.propulsion_result import PropulsionResult
from backend.design.fixed_wing.propulsion.propulsion_validator import PropulsionValidator
from backend.design.fixed_wing.propulsion.propulsion_registry import PropulsionStrategyRegistry
from backend.design.fixed_wing.propulsion.motor_selector import MotorSelector
from backend.design.fixed_wing.propulsion.engine_selector import EngineSelector
from backend.design.fixed_wing.propulsion.propeller_selector import PropellerSelector
from backend.design.fixed_wing.propulsion.thrust_analysis import ThrustAnalysis
from backend.design.fixed_wing.propulsion.power_analysis import PowerAnalysis
from backend.design.fixed_wing.propulsion.efficiency_analysis import EfficiencyAnalysis
from backend.design.fixed_wing.propulsion.cruise_analysis import CruiseAnalysis
from backend.design.fixed_wing.propulsion.climb_analysis import ClimbAnalysis
from backend.design.fixed_wing.propulsion.takeoff_analysis import TakeoffAnalysis


class PropulsionEngine:
    """
    Facade class managing the aircraft propulsion sizing and flight performance loop.
    """

    def __init__(
        self,
        motor_selector: MotorSelector | None = None,
        engine_selector: EngineSelector | None = None,
        prop_selector: PropellerSelector | None = None,
        validator: PropulsionValidator | None = None,
    ) -> None:
        self._motor_selector = motor_selector if motor_selector else MotorSelector()
        self._engine_selector = engine_selector if engine_selector else EngineSelector()
        self._prop_selector = prop_selector if prop_selector else PropellerSelector()
        self._validator = validator if validator else PropulsionValidator()

    def process_propulsion_design(
        self,
        requirements: PropulsionRequirements,
        profile: PropulsionProfile | None = None,
    ) -> PropulsionResult:
        """
        Sizes and validates the motor/engine, propeller, and flight performance parameters.

        Args:
            requirements (PropulsionRequirements): Sizing requirements context.
            profile (PropulsionProfile | None): Safety configurations.

        Returns:
            PropulsionResult: Sized motor, propeller, and performance analyses.
        """
        if profile is None:
            profile = PropulsionProfile()

        g = 9.80665
        m_profile = requirements.mission_result.mission_profile
        wing_geom = requirements.wing_result.wing_geometry
        category = m_profile.mission_category
        wl = getattr(wing_geom, "wing_loading_kg_m2", None) if wing_geom else None
        wa = getattr(wing_geom, "area_m2", None) if wing_geom else None
        if isinstance(wl, (int, float)) and isinstance(wa, (int, float)):
            mtow = float(wl * wa)
        elif isinstance(getattr(m_profile, "maximum_takeoff_weight_limit_kg", None), (int, float)):
            mtow = float(m_profile.maximum_takeoff_weight_limit_kg)
        elif getattr(requirements.mission_result, "constraints", None) and isinstance(getattr(requirements.mission_result.constraints, "maximum_takeoff_weight_kg", None), (int, float)):
            mtow = float(requirements.mission_result.constraints.maximum_takeoff_weight_kg)
        else:
            pay = getattr(m_profile, "payload_kg", 2.0)
            pay_val = float(pay) if isinstance(pay, (int, float)) else 2.0
            mtow = pay_val / 0.25
        weight_n = mtow * g

        # 1. Fetch matching strategy from registry
        strategy_name = category.value if hasattr(category, 'value') else str(category)
        strategy = PropulsionStrategyRegistry.get(strategy_name)

        # 2. Define Propulsion Constraints
        launch_m = getattr(m_profile, "launch_method", None)
        is_runway = launch_m is not None and ("RUNWAY" in str(launch_m).upper())
        min_tw = 0.30 if is_runway else strategy.get_thrust_to_weight_ratio()
        
        fuse_geom = getattr(getattr(requirements, "fuselage_result", None), "fuselage_geometry", None)
        fuse_h = getattr(fuse_geom, "height_m", 0.15) if fuse_geom else 0.15
        fuse_h_val = float(fuse_h) if isinstance(fuse_h, (int, float)) else 0.15
        constraints = PropulsionConstraints(
            allowed_types=[PropulsionType.ELECTRIC, PropulsionType.ICE],
            max_prop_diameter_m=max(0.28, fuse_h_val * 2.0),
            min_thrust_to_weight=min_tw,
        )

        # 3. Select type and layout using strategy
        prop_type = strategy.select_propulsion_type(requirements)
        prop_layout = strategy.select_propulsion_layout(requirements)

        # Extract authoritative engine_count from configuration result or layout
        engine_count = 1
        cfg_res = getattr(requirements, "configuration_result", None)
        if cfg_res and hasattr(cfg_res, "selected_configuration") and isinstance(cfg_res.selected_configuration, dict):
            raw_ec = cfg_res.selected_configuration.get("engine_count")
            if raw_ec is not None:
                try:
                    engine_count = int(raw_ec)
                except (ValueError, TypeError):
                    engine_count = 1
            elif "twin" in str(cfg_res.selected_configuration.get("propulsion_layout", "")).lower() or "twin" in str(cfg_res.selected_configuration.get("architecture", "")).lower():
                engine_count = 2
        elif hasattr(requirements, "preferred_layout") and requirements.preferred_layout and "twin" in str(requirements.preferred_layout).lower():
            engine_count = 2
        elif prop_layout and "twin" in str(prop_layout).lower():
            engine_count = 2
        engine_count = max(1, engine_count)

        # 4. Sizing thrust targets
        # Sized cruise aerodynamic glide L/D (typically around 12 to 18 for UAVs)
        estimated_LD = requirements.wing_result.analysis.aerodynamic_efficiency_score * 0.18
        estimated_LD = max(6.0, min(20.0, estimated_LD))
        
        # Distinguish estimated L/D from the final calculated aerodynamic L/D (BUG-08)
        if (requirements.flight_performance_result is not None and 
            getattr(requirements.flight_performance_result, "aerodynamic_analysis", None) is not None):
            final_calculated_LD = requirements.flight_performance_result.aerodynamic_analysis.lift_to_drag_ratio
            l_d = final_calculated_LD
        else:
            l_d = estimated_LD
            
        cruise_drag_total_n = weight_n / l_d

        # Required Takeoff thrust target
        t_to_w_target = 0.35 if is_runway else strategy.get_thrust_to_weight_ratio()
        takeoff_thrust_total_n = t_to_w_target * weight_n

        # Sizing targets per propulsion unit
        cruise_drag_n = cruise_drag_total_n / engine_count
        takeoff_thrust_n = takeoff_thrust_total_n / engine_count

        # 5. Sizing power targets
        v_cruise_m_s = m_profile.cruise_speed_kmh / 3.6
        eta_total = profile.default_motor_efficiency * profile.default_prop_efficiency

        # Sized Cruise Power per unit: P_cruise = (Thrust_unit * V_flight) / eta
        cruise_power_w = (cruise_drag_n * v_cruise_m_s) / eta_total
        cruise_power_total_w = cruise_power_w * engine_count

        # Sized Climb Power per unit: assume climb speed is 1.3 * V_stall, ROC = 3.5 m/s
        v_stall_m_s = requirements.wing_result.analysis.estimated_stall_speed_kmh / 3.6
        climb_speed_m_s = 1.3 * v_stall_m_s
        roc_target = 3.5  # standard climb rate target in m/s
        climb_power_total_w = ((weight_n * roc_target) + (cruise_drag_total_n * climb_speed_m_s)) / eta_total
        climb_power_w = climb_power_total_w / engine_count

        # Maximum takeoff/shaft power target per unit
        prop_area_est = (math.pi / 4.0) * (constraints.max_prop_diameter_m ** 2)
        takeoff_power_w = (math.sqrt((takeoff_thrust_n ** 3) / max(0.001, m_profile.air_density_kg_m3 * prop_area_est))) / eta_total
        max_power_target_w = max(takeoff_power_w, climb_power_w, cruise_power_w * 2.0) * 1.25

        # 6 & 7. Joint Selector for Motor and Propeller
        selected_component_name = "SunnySky X2820"
        max_component_power = 600.0
        weight_g = 140.0
        voltage_v = 14.8
        prop = self._prop_selector._props[1]  # fallback default

        from backend.design.fixed_wing.propulsion.propulsion_validator import PropulsionValidationError

        if prop_type == PropulsionType.ELECTRIC:
            motors = self._motor_selector._motors
            props = self._prop_selector._props
            
            valid_pairs = []
            for motor in motors:
                for propeller in props:
                    # check prop diameter clearance limit
                    if propeller.diameter_m > constraints.max_prop_diameter_m:
                        continue
                    
                    # static thrust and power margin calculations for a single unit
                    prop_area_val = (math.pi / 4.0) * (propeller.diameter_m ** 2)
                    shaft_max_power = motor.max_power_w * profile.default_motor_efficiency
                    unit_static_thrust_n = (m_profile.air_density_kg_m3 * prop_area_val * (shaft_max_power ** 2)) ** (1.0 / 3.0)
                    total_static_thrust_cand_n = unit_static_thrust_n * engine_count
                    t_w_ratio = total_static_thrust_cand_n / weight_n
                    
                    # Hard constraints:
                    if t_w_ratio < constraints.min_thrust_to_weight:
                        continue
                    if motor.max_power_w < climb_power_w:
                        continue
                    
                    climb_excess_power_unit = (motor.max_power_w * profile.default_motor_efficiency * profile.default_prop_efficiency) - (cruise_drag_n * climb_speed_m_s)
                    climb_excess_power_total = climb_excess_power_unit * engine_count
                    roc_val = climb_excess_power_total / weight_n
                    if roc_val < 0.5:
                        continue
                        
                    # Deterministic ranking metrics
                    thrust_margin = unit_static_thrust_n - takeoff_thrust_n
                    power_margin = motor.max_power_w - climb_power_w
                    cruise_current = cruise_power_w / motor.nominal_voltage_v if motor.nominal_voltage_v > 0.0 else 9999.0
                    motor_weight = motor.weight_g
                    
                    valid_pairs.append({
                        "motor": motor,
                        "prop": propeller,
                        "static_thrust_n": unit_static_thrust_n,
                        "t_w_ratio": t_w_ratio,
                        "roc": roc_val,
                        "thrust_margin": thrust_margin,
                        "power_margin": power_margin,
                        "cruise_current": cruise_current,
                        "motor_weight": motor_weight
                    })
            
            if valid_pairs:
                # Rank combinations:
                # 1. satisfy every hard constraint (already filtered)
                # 2. lower propulsion mass (lower motor weight first)
                # 3. lower electrical demand (lower cruise current draw first)
                # 4. adequate thrust margin (higher thrust margin first)
                # 5. adequate power margin (higher power margin first)
                valid_pairs.sort(key=lambda x: (
                    x["motor_weight"],
                    x["cruise_current"],
                    -x["thrust_margin"],
                    -x["power_margin"]
                ))
                best_pair = valid_pairs[0]
                
                selected_component_name = best_pair["motor"].name
                max_component_power = best_pair["motor"].max_power_w
                weight_g = best_pair["motor"].weight_g
                voltage_v = best_pair["motor"].nominal_voltage_v
                prop = best_pair["prop"]
            else:
                # If no valid combinations exist, identify if it's a catalog limit or thrust limit
                if max_power_target_w > 3400.0:
                    raise PropulsionValidationError(
                        errors=[f"PROPULSION_POWER_LIMIT: Sized power target of {max_power_target_w:.1f} W exceeds maximum catalog motor power limit of 3400.0 W."]
                    )
                else:
                    raise PropulsionValidationError(
                        errors=[f"PROPULSION_THRUST_LIMIT: Sized takeoff thrust target of {takeoff_thrust_n:.1f} N cannot be met within propeller diameter clearance limit of {constraints.max_prop_diameter_m:.3f} m."]
                    )

        elif prop_type == PropulsionType.ICE:
            engine = self._engine_selector.select_best_engine(max_power_target_w)
            selected_component_name = engine.name
            max_component_power = engine.max_power_w
            weight_g = engine.weight_g
            voltage_v = 0.0
            prop = self._prop_selector.select_propeller(
                target_thrust_n=takeoff_thrust_n,
                shaft_power_w=max_component_power * profile.default_motor_efficiency,
                air_density=m_profile.air_density_kg_m3,
                max_diameter_m=constraints.max_prop_diameter_m,
            )

        # 8. Sizing analyses
        # Est static thrust per unit: T = (rho * Area * (Power_shaft)^2)^(1/3)
        prop_area = (math.pi / 4.0) * (prop.diameter_m ** 2)
        shaft_max_power = max_component_power * profile.default_motor_efficiency
        unit_static_thrust_n = (m_profile.air_density_kg_m3 * prop_area * (shaft_max_power ** 2)) ** (1.0 / 3.0)
        total_static_thrust_n = unit_static_thrust_n * engine_count
        max_power_total_w = max_component_power * engine_count

        t_anal = ThrustAnalysis(
            required_cruise_thrust_n=round(cruise_drag_total_n, 2),
            required_takeoff_thrust_n=round(takeoff_thrust_total_n, 2),
            estimated_static_thrust_n=round(total_static_thrust_n, 2),
            thrust_to_weight_ratio=round(total_static_thrust_n / weight_n, 2),
            power_loading_w_kg=round(max_power_total_w / mtow, 2),
        )

        p_anal = PowerAnalysis(
            required_cruise_power_w=round(cruise_power_total_w, 1),
            required_climb_power_w=round(climb_power_total_w, 1),
            maximum_power_w=round(max_power_total_w, 1),
            current_draw_cruise_a=round(cruise_power_total_w / voltage_v, 2) if voltage_v > 0.0 else 0.0,
            metadata={
                "voltage_v": voltage_v,
                "motor_weight_g": weight_g,
                "engine_count": engine_count,
                "per_motor_static_thrust_n": round(unit_static_thrust_n, 2),
                "per_motor_max_power_w": round(max_component_power, 1),
                "per_motor_cruise_power_w": round(cruise_power_w, 1),
                "per_motor_cruise_current_a": round(cruise_power_w / voltage_v, 2) if voltage_v > 0.0 else 0.0,
            },
        )

        # Wh/km = Wh draw per hour / speed_kmh = Watts / speed_kmh
        energy_rate = cruise_power_total_w / m_profile.cruise_speed_kmh
        ef_anal = EfficiencyAnalysis(
            motor_efficiency=profile.default_motor_efficiency,
            propeller_efficiency=profile.default_prop_efficiency,
            total_system_efficiency=round(eta_total, 3),
            energy_consumption_per_km_wh=round(energy_rate, 2),
        )

        # Cruise RPM
        # RPM approx V_flight / pitch
        cruise_rpm = (v_cruise_m_s / prop.pitch_m) * 60.0
        c_anal = CruiseAnalysis(
            cruise_speed_kmh=m_profile.cruise_speed_kmh,
            required_cruise_thrust_n=round(cruise_drag_total_n, 2),
            prop_rpm_cruise=round(cruise_rpm, 0),
            throttle_setting_pct=round((cruise_power_w / max_component_power) * 100.0, 1),
        )

        # Climb rate: ROC = (P_excess) / W = (T - D) * V / W
        climb_excess_power = (max_power_total_w * profile.default_motor_efficiency * profile.default_prop_efficiency) - (cruise_drag_total_n * climb_speed_m_s)
        climb_excess_power = max(50.0, climb_excess_power)
        roc = climb_excess_power / weight_n
        climb_angle = math.degrees(math.asin(max(-0.9, min(0.9, roc / climb_speed_m_s))))
        
        # Time to operational altitude
        time_to_alt = m_profile.operational_altitude_m / (roc * 60.0)

        cl_anal = ClimbAnalysis(
            rate_of_climb_m_s=round(roc, 2),
            climb_angle_deg=round(climb_angle, 1),
            excess_power_w=round(climb_excess_power, 1),
            time_to_altitude_min=round(time_to_alt, 2),
        )

        # Takeoff roll distance (correct SI units including density rho):
        cl_to = 1.1  # typical flap takeoff lift coefficient
        t_to_w_actual = total_static_thrust_n / weight_n
        wl = wing_geom.wing_loading_kg_m2
        rho = m_profile.air_density_kg_m3
        to_dist = (2.0 * wl) / max(0.1, rho * t_to_w_actual * cl_to)
        
        # Takeoff rotation speed
        to_vel = 1.2 * v_stall_m_s
        to_accel = to_vel / max(0.1, (total_static_thrust_n - cruise_drag_total_n) / mtow)

        to_anal = TakeoffAnalysis(
            takeoff_distance_m=round(to_dist, 2),
            takeoff_velocity_m_s=round(to_vel, 2),
            acceleration_force_n=round(total_static_thrust_n - cruise_drag_total_n, 2),
            takeoff_time_s=round(to_accel, 2),
        )

        # 9. Validate sized geometry
        warnings = self._validator.validate(
            requirements=requirements,
            constraints=constraints,
            prop_type=prop_type,
            t_anal=t_anal,
            p_anal=p_anal,
            c_anal=c_anal,
            cl_anal=cl_anal,
            to_anal=to_anal,
        )

        # 10. Compile notes and recommendations
        unit_label = f"{engine_count}x {selected_component_name}" if engine_count > 1 else selected_component_name
        prop_label = f"{engine_count}x {prop.name}" if engine_count > 1 else prop.name
        engineering_notes = [
            f"Propulsion architecture: {prop_type.value}.",
            f"Propulsion layout: {prop_layout.value}.",
            f"Engine count: {engine_count}.",
            f"Selected power unit: {unit_label} (per-motor max power: {max_component_power:.1f} W, total max power: {max_power_total_w:.1f} W).",
            f"Sized propeller: {prop_label} (diameter: {prop.diameter_in:.1f} in, pitch: {prop.pitch_in:.1f} in).",
            f"Total static thrust: {total_static_thrust_n:.2f} N (per-motor: {unit_static_thrust_n:.2f} N, T/W: {t_to_w_actual:.2f}).",
            f"Estimated takeoff distance: {to_dist:.1f} m, rate of climb: {roc:.2f} m/s.",
            f"Energy consumption: {energy_rate:.2f} Wh/km.",
        ]
        
        recommendations = strategy.get_recommendations(t_to_w_actual)

        metadata = {
            "engine_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "strategy_applied": strategy.name,
            "engine_count": engine_count,
        }

        # 11. Return compiled PropulsionResult
        return PropulsionResult(
            selected_motor_or_engine=selected_component_name,
            selected_propeller=prop.name,
            propulsion_layout=prop_layout.value,
            thrust_analysis=t_anal,
            power_analysis=p_anal,
            efficiency_analysis=ef_anal,
            cruise_analysis=c_anal,
            climb_analysis=cl_anal,
            takeoff_analysis=to_anal,
            engineering_notes=engineering_notes,
            recommendations=recommendations,
            warnings=warnings,
            metadata=metadata,
        )

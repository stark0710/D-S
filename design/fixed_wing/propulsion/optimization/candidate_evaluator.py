"""
Fixed-Wing Propulsion Candidate Evaluator

Evaluates candidate propulsion systems by running them through the existing
PropulsionEngine engineering calculation backend.
"""

import copy
from backend.design.fixed_wing.propulsion.motor_selector import MotorSelector, MotorRecord
from backend.design.fixed_wing.propulsion.propeller_selector import PropellerSelector, PropellerRecord
from backend.design.fixed_wing.propulsion.propulsion_engine import PropulsionEngine
from backend.design.fixed_wing.propulsion.propulsion_requirements import PropulsionRequirements
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate


class CustomMotorSelector(MotorSelector):
    """Overrides motor selection to force a specific candidate motor."""

    def __init__(self, motor_record: MotorRecord) -> None:
        super().__init__()
        self._motors = [motor_record]

    def select_best_motor(self, target_power_w: float, mission_category: str) -> MotorRecord:
        return self._motors[0]


class CustomPropellerSelector(PropellerSelector):
    """Overrides propeller selection to force a specific candidate propeller."""

    def __init__(self, prop_record: PropellerRecord) -> None:
        super().__init__()
        self._props = [prop_record, prop_record]

    def select_propeller(
        self,
        target_thrust_n: float,
        shaft_power_w: float,
        air_density: float,
        max_diameter_m: float | None = None,
    ) -> PropellerRecord:
        return self._props[0]


class CandidateEvaluator:
    """Evaluates candidates using the existing PropulsionEngine."""

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """Evaluates the candidate motor, propeller, ESC, and battery combination."""
        dv = candidate.design_variables
        motor = dv["motor"]
        propeller = dv["propeller"]
        esc = dv["esc"]
        battery = dv["battery"]

        # Adapt requirements for consistent optimized geometry
        orig_reqs = context.requirements
        reqs = copy.deepcopy(orig_reqs)

        # Apply previous optimizer spec values to ensure consistent geometry
        fuse_spec = context.previous_specifications.get("FuselageOptimizer")
        wing_spec = context.previous_specifications.get("WingPlanformOptimizer")
        tail_spec = context.previous_specifications.get("TailOptimizer")

        if fuse_spec:
            if hasattr(reqs.fuselage_result, "fuselage_geometry") and reqs.fuselage_result.fuselage_geometry:
                reqs.fuselage_result.fuselage_geometry.height_m = getattr(fuse_spec, "height", reqs.fuselage_result.fuselage_geometry.height_m)
                reqs.fuselage_result.fuselage_geometry.length_m = getattr(fuse_spec, "overall_length", reqs.fuselage_result.fuselage_geometry.length_m)
        if wing_spec:
            if hasattr(reqs.wing_result, "wing_geometry") and reqs.wing_result.wing_geometry:
                reqs.wing_result.wing_geometry.span_m = getattr(wing_spec, "wing_span", getattr(wing_spec, "span_m", reqs.wing_result.wing_geometry.span_m))
                reqs.wing_result.wing_geometry.area_m2 = getattr(wing_spec, "wing_area", getattr(wing_spec, "area_m2", reqs.wing_result.wing_geometry.area_m2))
                reqs.wing_result.wing_geometry.aspect_ratio = getattr(wing_spec, "aspect_ratio", reqs.wing_result.wing_geometry.aspect_ratio)
                reqs.wing_result.wing_geometry.wing_loading_kg_m2 = getattr(wing_spec, "wing_loading", reqs.wing_result.wing_geometry.wing_loading_kg_m2)
        if tail_spec:
            if hasattr(reqs, "tail_result") and reqs.tail_result:
                reqs.tail_result.tail_configuration = getattr(tail_spec, "tail_configuration", reqs.tail_result.tail_configuration)

        # Create records to inject
        motor_rec = MotorRecord(
            name=motor["name"],
            kv=motor["kv"],
            weight_g=motor["weight_g"],
            max_power_w=motor["max_power_w"],
            nominal_voltage_v=motor["nominal_voltage_v"]
        )
        prop_rec = PropellerRecord(
            diameter_in=propeller["diameter_in"],
            pitch_in=propeller["pitch_in"]
        )

        engine = PropulsionEngine(
            motor_selector=CustomMotorSelector(motor_rec),
            prop_selector=CustomPropellerSelector(prop_rec)
        )

        try:
            result = engine.process_propulsion_design(reqs)
        except Exception as e:
            candidate.status = "FAILED"
            candidate.constraints_passed = False
            candidate.derived_variables["evaluation_error"] = str(e)
            return

        # Succeeded: Extract performance metrics
        # Extract engine_count
        engine_count = 1
        cfg_res = getattr(reqs, "configuration_result", None)
        if cfg_res and hasattr(cfg_res, "selected_configuration") and isinstance(cfg_res.selected_configuration, dict):
            raw_ec = cfg_res.selected_configuration.get("engine_count")
            if raw_ec is not None:
                try:
                    engine_count = int(raw_ec)
                except (ValueError, TypeError):
                    engine_count = 1
            elif "twin" in str(cfg_res.selected_configuration.get("propulsion_layout", "")).lower() or "twin" in str(cfg_res.selected_configuration.get("architecture", "")).lower():
                engine_count = 2
        elif hasattr(reqs, "preferred_layout") and reqs.preferred_layout and "twin" in str(reqs.preferred_layout).lower():
            engine_count = 2
        engine_count = max(1, engine_count)

        derived = candidate.derived_variables
        derived["engine_count"] = engine_count
        derived["cruise_power_w"] = result.power_analysis.required_cruise_power_w
        derived["climb_power_w"] = result.power_analysis.required_climb_power_w
        derived["takeoff_power_w"] = result.power_analysis.maximum_power_w

        derived["static_thrust_n"] = result.thrust_analysis.estimated_static_thrust_n
        derived["cruise_thrust_n"] = result.thrust_analysis.required_cruise_thrust_n
        derived["takeoff_thrust_n"] = result.thrust_analysis.required_takeoff_thrust_n
        derived["thrust_to_weight"] = result.thrust_analysis.thrust_to_weight_ratio

        # Per-motor power and thrust metrics
        derived["per_motor_cruise_power_w"] = derived["cruise_power_w"] / engine_count
        derived["per_motor_climb_power_w"] = derived["climb_power_w"] / engine_count
        derived["per_motor_static_thrust_n"] = derived["static_thrust_n"] / engine_count

        derived["motor_efficiency"] = result.efficiency_analysis.motor_efficiency
        derived["propeller_efficiency"] = result.efficiency_analysis.propeller_efficiency
        derived["total_efficiency"] = result.efficiency_analysis.total_system_efficiency

        derived["rate_of_climb_m_s"] = result.climb_analysis.rate_of_climb_m_s
        derived["climb_angle_deg"] = result.climb_analysis.climb_angle_deg

        # Voltage and Current analysis
        voltage_v = battery["nominal_voltage_v"]
        derived["cruise_current_a"] = derived["cruise_power_w"] / voltage_v
        derived["climb_current_a"] = derived["climb_power_w"] / voltage_v
        derived["per_motor_cruise_current_a"] = derived["cruise_current_a"] / engine_count
        derived["per_motor_climb_current_a"] = derived["climb_current_a"] / engine_count

        capacity_ah = battery["capacity_mah"] / 1000.0
        derived["estimated_flight_time_min"] = (capacity_ah * 0.80) / derived["cruise_current_a"] * 60.0
        derived["climb_c_rate"] = derived["climb_current_a"] / capacity_ah
        derived["total_propulsion_weight_g"] = engine_count * (motor["weight_g"] + esc["weight_g"]) + battery["weight_g"]

        # Target-aware flight performance and energy metrics
        m_prof = getattr(getattr(reqs, "mission_result", None), "mission_profile", None)
        v_cruise_kmh = getattr(m_prof, "cruise_speed_kmh", 70.0) if m_prof else 70.0
        t_target = getattr(m_prof, "flight_time_min", 45.0) if m_prof else 45.0
        r_target = getattr(m_prof, "mission_range_km", 30.0) if m_prof else 30.0

        controlling_target_min = t_target
        if v_cruise_kmh > 0 and r_target > 0:
            t_range = (r_target / v_cruise_kmh) * 60.0
            controlling_target_min = max(controlling_target_min, t_range)

        derived["estimated_range_km"] = (derived["estimated_flight_time_min"] / 60.0) * v_cruise_kmh
        battery_nominal_energy_wh = (voltage_v * battery["capacity_mah"]) / 1000.0
        derived["battery_nominal_energy_wh"] = battery_nominal_energy_wh
        derived["battery_usable_energy_wh"] = battery_nominal_energy_wh * 0.80
        derived["controlling_target_min"] = controlling_target_min

        # Required cruise propulsion energy for the controlling mission duration
        p_cruise = derived["cruise_power_w"]
        derived["required_energy_wh"] = p_cruise * (controlling_target_min / 60.0)
        req_energy = max(0.1, derived["required_energy_wh"])
        derived["energy_margin_pct"] = ((derived["battery_usable_energy_wh"] - req_energy) / req_energy) * 100.0

        derived["required_c_rating"] = derived["climb_current_a"] / max(0.1, capacity_ah)

        derived["engine_recommendations"] = result.recommendations
        derived["engine_warnings"] = result.warnings
        derived["propulsion_result"] = result
        candidate.status = "EVALUATED"

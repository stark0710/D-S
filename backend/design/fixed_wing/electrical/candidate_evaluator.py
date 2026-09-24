"""
Electrical System Candidate Evaluator

Performs all engineering calculations for the candidate layout.
"""

from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.components.component_category import ComponentCategory
from backend.design.components.component_repository import ComponentRepository
from backend.design.fixed_wing.electrical.candidate_generator import build_electrical_repository


class CandidateEvaluator:
    """
    Evaluates candidate layouts against engineering models.
    """

    def __init__(self, repository: ComponentRepository | None = None) -> None:
        self.repository = repository if repository else build_electrical_repository()

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        """
        Computes the derived variables of the electrical candidate.
        """
        dv = candidate.design_variables
        fc = dv["flight_controller"]
        gps = dv["gps"]
        telemetry = dv["telemetry"]
        receiver = dv["receiver"]
        servo = dv["servo"]
        servo_count = dv["servo_count"]
        bec = dv["bec"]
        pm = dv["power_module"]
        payload = dv["mission_equipment"]
        layout = dv["power_distribution_layout"]

        # Context metrics
        profile = context.requirements.mission_result.mission_profile
        mtow = (
            getattr(profile, "maximum_takeoff_weight_limit_kg", None)
            or getattr(profile, "current_iteration_mtow_kg", None)
            or getattr(profile, "initial_mtow_seed_kg", None)
            or 10.0
        )
        v_cruise = profile.cruise_speed_kmh
        range_km = profile.mission_range_km

        # Propulsion context
        prop_spec = context.previous_specifications.get("PropulsionOptimizer")
        prop_cells = 6
        prop_cruise_current = 15.0
        prop_climb_current = 40.0
        if prop_spec:
            prop_cells = getattr(prop_spec, "battery_cell_count", 6)
            prop_cruise_current = getattr(prop_spec, "cruise_current_a", 15.0)
            prop_climb_current = getattr(prop_spec, "max_climb_current_a", 40.0)

        main_battery_voltage = prop_cells * 3.7

        # 1. Required Servo Torque
        # Rule of thumb: dynamic torque scales with aircraft mass and cruise velocity squared
        # required_torque = mtow * (v_cruise / 50.0) * 0.5
        required_servo_torque_kgcm = round(mtow * (v_cruise / 50.0) * 0.5, 2)

        # 2. Power Budget Calculations
        fc_power = fc["current_draw_a"] * fc["voltage_v"]
        gps_power = gps["current_draw_a"] * gps["voltage_v"]
        telemetry_power = telemetry["power_w"]
        receiver_power = receiver["current_draw_a"] * receiver["voltage_v"]
        payload_power = payload["power_w"]
        
        # Standard sensors (MS5611 Baro + Airspeed + Compass)
        sensors = self.repository.get_components_by_category(ComponentCategory.SENSOR)
        sensor_power = sum(s["power_w"] for s in sensors)

        # Servos load (Peak servo draw is continuous x count, or peak x count x factor)
        servo_voltage = servo["voltage_v"]
        servo_cont_current = servo["continuous_current_a"] * servo_count
        servo_peak_current = servo["peak_current_a"] * servo_count * 0.6
        
        servo_cont_power = servo_cont_current * servo_voltage
        servo_peak_power = servo_peak_current * servo_voltage

        # Total continuous and peak avionics power (W)
        continuous_avionics_power_w = fc_power + gps_power + telemetry_power + receiver_power + payload_power + sensor_power
        
        # Total continuous and peak system power (W)
        total_continuous_power_w = continuous_avionics_power_w + servo_cont_power
        total_peak_power_w = continuous_avionics_power_w + servo_peak_power

        # Main battery current draw
        bec_efficiency = 0.85
        aux_cont_current_draw_a = total_continuous_power_w / (main_battery_voltage * bec_efficiency)
        aux_peak_current_draw_a = total_peak_power_w / (main_battery_voltage * bec_efficiency)

        total_continuous_current_a = prop_cruise_current + aux_cont_current_draw_a
        total_peak_current_a = prop_climb_current + aux_peak_current_draw_a

        # 3. Size Wires & Connectors
        wires = [w for w in self.repository.get_components_by_category(ComponentCategory.CUSTOM) if w["category"] == "Wire"]
        # Sort wires from thinnest to thickest
        wires = sorted(wires, key=lambda w: w["awg"], reverse=True)
        selected_wire = None
        wire_length_m = 0.5
        for w in wires:
            if w["max_continuous_current_a"] >= total_peak_current_a:
                # Check voltage drop
                v_drop = 2.0 * (w["resistance_mohm_per_m"] / 1000.0) * wire_length_m * total_peak_current_a
                v_drop_percent = (v_drop / main_battery_voltage) * 100.0
                if v_drop_percent <= 2.0:
                    selected_wire = w
                    break
        if not selected_wire:
            selected_wire = wires[-1] # fallback thickest

        connectors = [c for c in self.repository.get_components_by_category(ComponentCategory.CUSTOM) if c["category"] == "Connector"]
        connectors = sorted(connectors, key=lambda c: c["max_continuous_current_a"])
        selected_connector = None
        for c in connectors:
            if c["max_continuous_current_a"] >= total_peak_current_a:
                selected_connector = c
                break
        if not selected_connector:
            selected_connector = connectors[-1]

        # 4. Total Electrical Mass
        sensors_weight = sum(s["weight_g"] for s in sensors)
        wire_weight = selected_wire["weight_g_per_m"] * wire_length_m
        connector_weight = selected_connector["weight_g"]
        
        cabling_and_connectors_weight_g = wire_weight + connector_weight
        # Add layout redundancy penalty
        layout_weight_modifier = 45.0 if layout == "Dual Redundant Bus" else 0.0

        estimated_electrical_mass_g = (
            fc["weight_g"]
            + gps["weight_g"]
            + telemetry["weight_g"]
            + receiver["weight_g"]
            + (servo["weight_g"] * servo_count)
            + bec["weight_g"]
            + pm["weight_g"]
            + payload["weight_g"]
            + sensors_weight
            + cabling_and_connectors_weight_g
            + layout_weight_modifier
        )

        # Margins
        bec_continuous_margin = bec["max_continuous_current_a"] - servo_cont_current
        bec_peak_margin = bec["max_peak_current_a"] - servo_peak_current
        pm_continuous_margin = pm["max_continuous_current_a"] - total_continuous_current_a

        # Redundancy level: FC redundancy + (1 if dual power layout else 0)
        redundancy_level = 1
        if fc["triple_redundant"]:
            redundancy_level += 2
        if layout == "Dual Redundant Bus":
            redundancy_level += 1

        # Populate derived variables
        candidate.derived_variables.update({
            "required_servo_torque_kgcm": required_servo_torque_kgcm,
            "continuous_avionics_power_w": round(continuous_avionics_power_w, 2),
            "total_continuous_power_w": round(total_continuous_power_w, 2),
            "total_peak_power_w": round(total_peak_power_w, 2),
            "total_continuous_current_a": round(total_continuous_current_a, 2),
            "total_peak_current_a": round(total_peak_current_a, 2),
            "servo_cont_current_a": round(servo_cont_current, 2),
            "servo_peak_current_a": round(servo_peak_current, 2),
            "bec_continuous_margin_a": round(bec_continuous_margin, 2),
            "bec_peak_margin_a": round(bec_peak_margin, 2),
            "pm_continuous_margin_a": round(pm_continuous_margin, 2),
            "wire_gauge_awg": selected_wire["awg"],
            "wire_name": selected_wire["name"],
            "connector_name": selected_connector["name"],
            "estimated_electrical_mass_g": round(estimated_electrical_mass_g, 1),
            "redundancy_level": redundancy_level,
            "battery_voltage_v": main_battery_voltage,
            "voltage_drop_percent": round((2.0 * (selected_wire["resistance_mohm_per_m"] / 1000.0) * wire_length_m * total_peak_current_a / main_battery_voltage) * 100.0, 2),
        })
        candidate.status = "EVALUATED"

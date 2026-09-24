"""
Fixed-Wing Center of Gravity (CG) Optimization Candidate Evaluator
"""

from typing import List, Dict, Any, Tuple
from backend.design.common.optimization.optimization_context import OptimizationContext
from backend.design.common.optimization.optimization_candidate import OptimizationCandidate
from backend.design.fixed_wing.mass_properties.component_mass import ComponentMass
from backend.design.fixed_wing.mass_properties.cg_calculator import CGCalculator
from backend.design.fixed_wing.mass_properties.stability_margin import StabilityMarginCalculator


class CGCandidateEvaluator:
    """
    Service placing movable and fixed items inside the fuselage cabin envelope,
    running CG calculations, and verifying longitudinal static stability.
    """
    def __init__(self) -> None:
        self.cg_calc = CGCalculator()
        self.stability_calc = StabilityMarginCalculator()

    def evaluate(self, candidate: OptimizationCandidate, context: OptimizationContext) -> None:
        dv = candidate.design_variables
        bf = dv["battery_pos_fraction"]
        pf = dv["payload_pos_fraction"]
        af = dv["avionics_pos_fraction"]

        # Retrieve geometry and preceding results
        f_geom = context.requirements.fuselage_result.fuselage_geometry
        wing_geom = context.requirements.wing_result.wing_geometry
        tail_res = context.requirements.tail_result
        layout = context.requirements.configuration_result

        # Retrieve preceding mass properties spec or use context
        mass_spec = context.previous_specifications.get("MassPropertiesOptimizer")
        prop_spec = context.previous_specifications.get("PropulsionOptimizer")
        elec_spec = context.previous_specifications.get("ElectricalOptimizer")

        # Get weights from mass spec if available, otherwise default
        if mass_spec:
            breakdown = mass_spec.weight_breakdown
        else:
            breakdown = {
                "wing": wing_geom.reference_area_m2 * 2.8,
                "fuselage": f_geom.length_m * 1.35,
                "horizontal_tail": tail_res.horizontal_tail.area_m2 * 2.2,
                "vertical_tail": tail_res.vertical_tail.area_m2 * 2.2,
                "landing_gear": 0.35,
                "motor": 0.310, "propeller": 0.065, "esc": 0.080,
                "battery": 1.200, "flight_controller": 0.080,
                "gps": 0.050, "receiver": 0.010, "telemetry": 0.030,
                "power_module": 0.025, "bec": 0.015, "servos": 0.112,
                "mission_equipment": 0.500, "payload": 1.5,
                "fasteners": 0.05, "wiring": 0.120, "paint_finish": 0.02,
                "safety_margin": 0.3,
            }

        # Fuselage interior envelopes
        total_len = getattr(f_geom, "length_m", 1.4)
        nose_len = getattr(f_geom, "nose_length_m", 0.25)
        tail_cone_len = getattr(f_geom, "tail_cone_length_m", 0.70)

        # Scale parameters to ensure cabin_len is realistic, positive, and bounds-safe
        nose_len = min(nose_len, total_len * 0.25)
        tail_cone_len = min(tail_cone_len, total_len * 0.50)
        cabin_len = total_len - nose_len - tail_cone_len

        # 1. Movable Component Placement (nose-relative X-coordinate)
        cabin_start_x = nose_len
        battery_x = cabin_start_x + bf * cabin_len
        payload_x = cabin_start_x + pf * cabin_len
        avionics_x = cabin_start_x + af * cabin_len

        # Side components linked to avionics/payload trays
        mission_equip_x = payload_x
        gps_x = avionics_x - 0.05
        receiver_x = avionics_x + 0.05
        telemetry_x = avionics_x + 0.08
        pm_x = avionics_x - 0.08
        bec_x = avionics_x - 0.10

        # 2. Fixed Component positions
        w_x = getattr(f_geom, 'wing_attachment_x_m', 0.35 * total_len) + wing_geom.quarter_chord_x_m
        h_tail_x = total_len - 0.12
        v_tail_x = total_len - 0.12
        lg_x = total_len * 0.45
        fuse_shell_x = total_len * 0.46

        # Propulsion Configuration relative coordinates
        is_pusher = "pusher" in getattr(layout, "propulsion_configuration", "Tractor").lower()
        is_twin = False
        if layout:
            prop_cfg = getattr(layout, "propulsion_configuration", "")
            sel_cfg = getattr(layout, "selected_configuration", {})
            ec = sel_cfg.get("engine_count", "1") if isinstance(sel_cfg, dict) else "1"
            if "twin" in prop_cfg.lower() or str(ec) == "2":
                is_twin = True

        if is_pusher:
            motor_x = total_len - 0.06
        elif is_twin:
            wing_attach_x = getattr(f_geom, 'wing_attachment_x_m', 0.35 * total_len)
            motor_x = max(0.06, wing_attach_x - 0.05)
        else:
            motor_x = 0.06

        propeller_x = motor_x - 0.02 if is_pusher else motor_x + 0.02
        esc_x = motor_x + 0.05 if is_pusher else motor_x - 0.05

        # Standard layout centers for secondary mass items
        fasteners_x = total_len * 0.5
        wiring_x = total_len * 0.45
        paint_x = total_len * 0.5
        safety_margin_x = total_len * 0.5

        # 3. Assemble ComponentMass list
        components = [
            # Structural
            ComponentMass("Wing Structure", breakdown["wing"], round(w_x, 3), 0.0, 0.0),
            ComponentMass("Fuselage Shell", breakdown["fuselage"], round(fuse_shell_x, 3), 0.0, -0.02),
            ComponentMass("Horizontal Tail", breakdown["horizontal_tail"], round(h_tail_x, 3), 0.0, 0.05),
            ComponentMass("Vertical Tail", breakdown["vertical_tail"], round(v_tail_x, 3), 0.0, 0.10),
            ComponentMass("Landing Gear", breakdown["landing_gear"], round(lg_x, 3), 0.0, -0.15),
            # Propulsion hardware
            ComponentMass("Motor", breakdown["motor"], round(motor_x, 3), 0.0, 0.0),
            ComponentMass("Propeller", breakdown["propeller"], round(propeller_x, 3), 0.0, 0.0),
            ComponentMass("ESC", breakdown["esc"], round(esc_x, 3), 0.0, 0.0),
            # Sized Battery
            ComponentMass("Energy Battery", breakdown["battery"], round(battery_x, 3), 0.0, -0.04),
            # Avionics
            ComponentMass("Flight Controller", breakdown["flight_controller"], round(avionics_x, 3), 0.0, 0.02),
            ComponentMass("GPS", breakdown["gps"], round(gps_x, 3), 0.0, 0.04),
            ComponentMass("Receiver", breakdown["receiver"], round(receiver_x, 3), 0.0, 0.01),
            ComponentMass("Telemetry", breakdown["telemetry"], round(telemetry_x, 3), 0.0, 0.03),
            ComponentMass("Power Module", breakdown["power_module"], round(pm_x, 3), 0.0, -0.01),
            ComponentMass("BEC", breakdown["bec"], round(bec_x, 3), 0.0, 0.0),
            ComponentMass("Servos", breakdown["servos"], round(w_x, 3), 0.0, 0.0),
            # Payload
            ComponentMass("Payload", breakdown["payload"], round(payload_x, 3), 0.0, -0.05),
            *(
                [ComponentMass("Mission Equipment", breakdown["mission_equipment"], round(mission_equip_x, 3), 0.0, -0.05)]
                if breakdown.get("mission_equipment", 0.0) > 0.0 else []
            ),
            # Structural/mfg items
            ComponentMass("Fasteners", breakdown["fasteners"], round(fasteners_x, 3), 0.0, 0.0),
            ComponentMass("Wiring", breakdown["wiring"], round(wiring_x, 3), 0.0, 0.0),
            ComponentMass("Paint / Finish", breakdown["paint_finish"], round(paint_x, 3), 0.0, 0.0),
            ComponentMass("Safety Margin", breakdown["safety_margin"], round(safety_margin_x, 3), 0.0, 0.0),
        ]

        # 4. Solve for overall CG coordinate X/Y/Z
        cg_x, cg_y, cg_z = self.cg_calc.calculate_cg(components)

        # 5. Evaluate Longitudinal Static Stability Margin
        wing_attach_x = getattr(f_geom, 'wing_attachment_x_m', 0.35 * total_len)
        np_pct = 0.42 if tail_res.tail_configuration == "Conventional" else 0.38
        
        # Calculate neutral point coordinate X from nose
        mac = wing_geom.mean_aerodynamic_chord_m
        quarter_chord_x = wing_geom.quarter_chord_x_m
        neutral_point_x = wing_attach_x + quarter_chord_x + (np_pct * mac)

        static_margin = self.stability_calc.calculate_static_margin(
            cg_x=cg_x,
            wing_geom=wing_geom,
            tail_result=tail_res,
            neutral_point_override_pct=np_pct,
            wing_attachment_x_m=wing_attach_x,
        )

        # Calculate component positioning coordinate dictionary
        pos_dict = {
            "battery": (round(battery_x, 3), 0.0, -0.04),
            "payload": (round(payload_x, 3), 0.0, -0.05),
            "mission_equipment": (round(mission_equip_x, 3), 0.0, -0.05),
            "avionics_tray": (round(avionics_x, 3), 0.0, 0.02),
            "gps": (round(gps_x, 3), 0.0, 0.04),
            "receiver": (round(receiver_x, 3), 0.0, 0.01),
            "telemetry": (round(telemetry_x, 3), 0.0, 0.03),
            "power_module": (round(pm_x, 3), 0.0, -0.01),
            "bec": (round(bec_x, 3), 0.0, 0.0),
        }

        # Moment breakdown (moment = mass * arms relative to nose)
        moment_dict = {c.name: round(c.mass_kg * c.x_m, 4) for c in components}

        # 6. loading conditions CG envelopes
        # Empty CG envelope (no battery, no payload/equipment)
        empty_comps = [c for c in components if "Battery" not in c.name and "Payload" not in c.name and "Mission Equipment" not in c.name]
        em_x, em_y, em_z = self.cg_calc.calculate_cg(empty_comps)

        # Operating CG envelope (battery included, no payload)
        op_comps = [c for c in components if "Payload" not in c.name and "Mission Equipment" not in c.name]
        op_x, op_y, op_z = self.cg_calc.calculate_cg(op_comps)

        cg_envelope = {
            "Empty Airframe": (round(em_x, 3), round(em_y, 3), round(em_z, 3)),
            "Operational Empty": (round(op_x, 3), round(op_y, 3), round(op_z, 3)),
            "Maximum Takeoff Weight": (round(cg_x, 3), round(cg_y, 3), round(cg_z, 3)),
        }

        # Populate candidate variables
        candidate.derived_variables["components"] = components
        candidate.derived_variables["cg_position"] = (round(cg_x, 3), round(cg_y, 3), round(cg_z, 3))
        candidate.derived_variables["neutral_point"] = round(neutral_point_x, 3)
        candidate.derived_variables["static_margin"] = round(static_margin, 3)
        candidate.derived_variables["component_positions"] = pos_dict
        candidate.derived_variables["moment_summary"] = moment_dict
        candidate.derived_variables["cg_envelope"] = cg_envelope

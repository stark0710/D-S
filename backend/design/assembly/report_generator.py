"""
Report Generator and Deterministic Serializer Subsystem for Phase 13.

Provides deterministic JSON export and structured Markdown engineering report generation
for FinalAircraftDesign contracts across all aircraft classes.
"""

import os
import json
import math
import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional


def to_dict_deterministic(obj: Any, seen: Optional[set] = None) -> Any:
    """
    Recursively converts dataclasses, enums, dicts, lists, and primitives
    into deterministic, JSON-serializable structures.
    Rounds floats to 4 decimal places for stable serialization.
    """
    if seen is None:
        seen = set()

    if obj is None:
        return None
    if isinstance(obj, (int, str, bool)):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, 4)
    if isinstance(obj, Enum):
        return obj.value

    obj_id = id(obj)
    if obj_id in seen:
        return None
    seen.add(obj_id)

    if dataclasses.is_dataclass(obj):
        res = {}
        for f in dataclasses.fields(obj):
            try:
                val = getattr(obj, f.name, None)
                res[f.name] = to_dict_deterministic(val, seen)
            except Exception:
                res[f.name] = None
        return res

    if hasattr(obj, "__slots__"):
        res = {}
        all_slots = set()
        for cls in obj.__class__.__mro__:
            for s in getattr(cls, "__slots__", ()):
                all_slots.add(s)
        for s in all_slots:
            if not s.startswith("_"):
                try:
                    res[s] = to_dict_deterministic(getattr(obj, s), seen)
                except Exception:
                    pass
        return res

    if isinstance(obj, dict):
        # Sort keys to ensure deterministic ordering
        return {str(k): to_dict_deterministic(obj[k], seen) for k in sorted(obj.keys())}

    if isinstance(obj, (list, tuple, set)):
        return [to_dict_deterministic(x, seen) for x in obj]

    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        try:
            return to_dict_deterministic(obj.to_dict(), seen)
        except Exception:
            pass

    if hasattr(obj, "__dict__"):
        res = {}
        for k in sorted(obj.__dict__.keys()):
            if not k.startswith("_"):
                res[k] = to_dict_deterministic(obj.__dict__[k], seen)
        return res

    return str(obj)


def export_design_json(design: Any, filepath: str) -> None:
    """Exports FinalAircraftDesign to deterministic JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    data = to_dict_deterministic(design)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def generate_markdown_report(design: Any) -> str:
    """Generates comprehensive human-readable Markdown engineering design report."""
    d = design
    geom = d.geometry
    wing = geom.wing
    fuse = geom.fuselage
    tail = geom.tail
    booms = geom.booms
    aero = d.aerodynamics
    prop = d.propulsion
    mass = d.mass_properties
    stab = d.stability
    ctrl = d.controls
    perf = d.performance
    trans = d.transition
    bat = d.battery
    energy = d.energy
    avionics = d.avionics
    elec = d.electrical

    lines = []
    lines.append(f"# Torq Wings Final Aircraft Design Specification: {d.design_id}\n")
    lines.append(f"**Aircraft Class**: `{d.aircraft_class.value if isinstance(d.aircraft_class, Enum) else d.aircraft_class}`  ")
    lines.append(f"**Configuration**: `{d.configuration}`  ")
    lines.append(f"**Design Status**: `{d.design_status.value if isinstance(d.design_status, Enum) else d.design_status}`  ")
    lines.append(f"**Flight Validation Status**: `{d.validation_status.status}` (Flight Validated: `{d.validation_status.flight_validated}`)  ")
    lines.append(f"> [!IMPORTANT]\n> {d.validation_status.flight_status_note}\n")

    lines.append("## 1. Executive Summary & Mission Requirements\n")
    lines.append("| Parameter | Requirement | Sized / Achieved | Margin / Delta |")
    lines.append("|:---|:---|:---|:---|")
    for item in d.requirement_traceability:
        lim_str = f" [{item.limit}]" if item.limit else ""
        margin_str = f"{item.margin:+.2f} {item.unit}" if item.margin is not None else "N/A"
        lines.append(f"| {item.requirement} | {item.required_value} {item.unit}{lim_str} | {item.design_value} {item.unit} | {margin_str} (`{item.status}`) |")
    lines.append("")

    lines.append("## 2. Mass Properties & Center of Gravity\n")
    lines.append(f"- **Maximum Takeoff Weight (MTOW)**: `{mass.mtow_kg:.3f} kg`")
    lines.append(f"- **Empty Mass**: `{mass.empty_mass_kg:.3f} kg`")
    lines.append(f"- **Payload Mass**: `{mass.payload_mass_kg:.3f} kg`")
    lines.append(f"- **Battery Mass**: `{mass.battery_mass_kg:.3f} kg`")
    lines.append(f"- **Center of Gravity (CG)**: `[{mass.cg_x_m:.4f}, {mass.cg_y_m:.4f}, {mass.cg_z_m:.4f}] m`")
    lines.append(f"- **Allowable CG Travel Range**: `[{mass.forward_cg_limit_x_m:.4f} m .. {mass.aft_cg_limit_x_m:.4f} m]` (Margin: `{mass.cg_margin_m:.4f} m`)")
    lines.append(f"- **Inertia Tensor Status**: `{mass.inertia.status.value if isinstance(mass.inertia.status, Enum) else mass.inertia.status}` ({mass.inertia.reason})\n")

    lines.append("### Major Component Mass Breakdown\n")
    lines.append("| Component | Category | Mass (kg) | X_CG (m) | Y_CG (m) | Z_CG (m) | Provenance |")
    lines.append("|:---|:---|:---|:---|:---|:---|:---|")
    for c in mass.component_breakdown:
        p_val = c.provenance.value if isinstance(c.provenance, Enum) else c.provenance
        lines.append(f"| {c.name} | {c.category} | {c.mass_kg:.3f} | {c.x_cg_m:.3f} | {c.y_cg_m:.3f} | {c.z_cg_m:.3f} | `{p_val}` |")
    lines.append("")

    lines.append("## 3. Aerodynamics & Wing Geometry\n")
    lines.append(f"- **Wingspan (b)**: `{wing.span_m:.3f} m`")
    lines.append(f"- **Wing Reference Area (S)**: `{wing.area_m2:.4f} m²`")
    lines.append(f"- **Aspect Ratio (AR)**: `{wing.aspect_ratio:.2f}`")
    lines.append(f"- **Mean Aerodynamic Chord (MAC)**: `{wing.mac_m:.4f} m` (LE: `{wing.mac_le_x_m:.4f} m`)")
    lines.append(f"- **Root / Tip Chords**: `{wing.root_chord_m:.4f} m` / `{wing.tip_chord_m:.4f} m` (Taper: `{wing.taper_ratio:.2f}`)")
    lines.append(f"- **Airfoils**: Root: `{wing.airfoil_root}`, Tip: `{wing.airfoil_tip}`")
    lines.append(f"- **Cruise Lift Coefficient ($C_L$)**: `{aero.cl_cruise:.3f}`")
    lines.append(f"- **Zero-Lift Drag Coefficient ($C_{{D0}}$)**: `{aero.cd0:.4f}`")
    lines.append(f"- **Cruise Lift-to-Drag ($L/D$)**: `{aero.lift_to_drag_cruise:.2f}` (Max $L/D$: `{aero.lift_to_drag_max:.2f}`)\n")

    lines.append("## 4. Fuselage, Booms & Empennage\n")
    lines.append(f"- **Fuselage Dimensions (L x W x H)**: `{fuse.length_m:.3f} m x {fuse.max_width_m:.3f} m x {fuse.max_height_m:.3f} m`")
    lines.append(f"- **Fineness Ratio**: `{fuse.fineness_ratio:.2f}`")
    if booms.boom_count > 0:
        lines.append(f"- **Twin Booms**: `{booms.boom_count} booms`, Length: `{booms.length_m:.3f} m`, Spacing: `{booms.spacing_m:.3f} m`")
    lines.append(f"- **Empennage Type**: `{tail.tail_type}`")
    lines.append(f"- **Tail Area**: `{tail.total_area_m2:.4f} m²`")
    if tail.v_tail_angle_deg is not None:
        lines.append(f"- **V-Tail Dihedral**: `{tail.v_tail_angle_deg:.1f}°`")
        lines.append(f"- **Projected Areas**: Horizontal = `{tail.projected_horizontal_area_m2:.4f} m²`, Vertical = `{tail.projected_vertical_area_m2:.4f} m²`\n")

    lines.append("## 5. Propulsion System Architecture\n")
    cr_prop = prop.cruise_propulsion
    lines.append("### Cruise Propulsion")
    lines.append(f"- **Motor**: `{cr_prop.motor_model}` ({cr_prop.motor_count}x)")
    lines.append(f"- **Propeller**: `{cr_prop.propeller_model}` (Dia: `{cr_prop.propeller_diameter_in:.1f}\"`, Pitch: `{cr_prop.propeller_pitch_in:.1f}\"`)")
    lines.append(f"- **Cruise ESC**: `{cr_prop.esc_model}` (`{cr_prop.esc_rating_a:.0f}A`)")
    lines.append(f"- **Cruise Electrical Power**: `{cr_prop.cruise_power_electrical_w:.1f} W` (Thrust: `{cr_prop.cruise_thrust_per_motor_n:.2f} N`)\n")

    lift_prop = prop.lift_propulsion
    if lift_prop.motor_count > 0:
        lines.append("### VTOL Lift Propulsion")
        lines.append(f"- **Lift Motors**: `{lift_prop.motor_model}` ({lift_prop.motor_count}x)")
        lines.append(f"- **Lift Propellers**: `{lift_prop.propeller_model}` (Dia: `{lift_prop.propeller_diameter_in:.1f}\"`)")
        lines.append(f"- **Lift ESC**: `{lift_prop.esc_model}` (`{lift_prop.esc_rating_a:.0f}A`)")
        lines.append(f"- **Thrust-to-Weight (T/W)**: `{lift_prop.thrust_to_weight_ratio:.2f}` (Total Hover Thrust: `{lift_prop.total_hover_thrust_required_n:.1f} N`)")
        lines.append(f"- **Hover Electrical Power**: `{lift_prop.hover_power_electrical_w:.1f} W` (Disk Loading: `{lift_prop.disk_loading_kg_m2:.1f} kg/m²`)\n")

    if trans.status == "VALID" or trans.safe_transition_speed_mps > 0:
        lines.append("### VTOL Transition Dynamics")
        lines.append(f"- **Stall Speed ($V_{{stall}}$)**: `{trans.stall_speed_mps:.2f} m/s`")
        lines.append(f"- **Safe Transition Speed ($V_{{trans}}$)**: `{trans.safe_transition_speed_mps:.2f} m/s`")
        lines.append(f"- **Transition Duration**: `{trans.transition_duration_s:.1f} s`")
        lines.append(f"- **Transition Energy**: `{trans.transition_energy_wh:.2f} Wh`\n")

    lines.append("## 6. Energy Storage & Electrical Architecture\n")
    lines.append(f"- **Battery**: `{bat.pack_model}` ({bat.cell_series_count}S {bat.chemistry}, `{bat.voltage_nominal_v:.1f} V`)")
    lines.append(f"- **Capacity / Energy**: `{bat.capacity_mah:.0f} mAh` / `{bat.energy_wh:.1f} Wh`")
    lines.append(f"- **Mission Energy Required**: `{energy.energy_required_mission_wh:.1f} Wh`")
    lines.append(f"- **Battery Reserve**: `{energy.energy_reserve_pct:.1f}%`\n")

    lines.append("## 7. Stability, Control & Trim\n")
    lines.append(f"- **Neutral Point ($x_{{NP}}$)**: `{stab.neutral_point_x_m:.4f} m` ({stab.neutral_point_mac_pct:.1f}% MAC)")
    lines.append(f"- **Static Margin**: `{stab.static_margin_mac_pct:.2f}% MAC` (`{stab.static_margin_m:.4f} m`)")
    lines.append(f"- **Longitudinal Stability ($C_{{m\\alpha}}$)**: `{stab.c_m_alpha_per_rad:.4f} 1/rad` (Stable: `{stab.is_longitudinally_stable}`)")
    lines.append(f"- **Directional Stability ($C_{{n\\beta}}$)**: `{stab.c_n_beta_per_rad:.4f} 1/rad` (Stable: `{stab.is_directionally_stable}`)")
    lines.append(f"- **Lateral Stability ($C_{{l\\beta}}$)**: `{stab.c_l_beta_per_rad:.4f} 1/rad` (Stable: `{stab.is_laterally_stable}`)")
    lines.append(f"- **Elevator Control Power ($C_{{m\\delta_e}}$)**: `{ctrl.c_m_delta_e_per_rad:.4f} 1/rad`")
    lines.append(f"- **Trim Status**: Feasible (`{ctrl.trim_feasible}`), Trim Elevator: `{ctrl.trim_elevator_cruise_deg:.2f}°`\n")

    lines.append("## 8. Commercial Hardware Bill of Materials (BOM)\n")
    lines.append("| Category | Role | Component | Part Number | Qty | Unit Mass | Total Mass | Status |")
    lines.append("|:---|:---|:---|:---|:---|:---|:---|:---|")
    for item in d.commercial_components:
        pn = item.part_number or "N/A"
        lines.append(f"| {item.category} | {item.role} | {item.manufacturer} {item.model} | {pn} | {item.quantity} | {item.mass_per_unit_kg:.3f} kg | {item.total_mass_kg:.3f} kg | `{item.verification_status}` |")
    lines.append("")

    lines.append("## 9. CAD Handover Specification\n")
    cad = d.cad_handover
    lines.append(f"- **Reference Datum**: `{cad.reference_datum}`")
    lines.append(f"- **Aircraft Origin**: `X=0, Y=0, Z=0`")
    lines.append(f"- **CG Location**: `[{cad.cg_location_m[0]:.4f}, {cad.cg_location_m[1]:.4f}, {cad.cg_location_m[2]:.4f}] m`")
    lines.append(f"- **Airfoils**: {', '.join(cad.wing_airfoils)}")
    lines.append("- **Mounting Coordinates Resolved**:")
    for k, v in cad.mounting_coordinates.items():
        coords_str = f"[{v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}] m" if len(v) >= 3 else str(v)
        lines.append(f"  - `{k}`: `{coords_str}`")
    lines.append("")

    lines.append("## 10. Simulation Handover Specification\n")
    sim = d.simulation_handover
    lines.append(f"- **MTOW**: `{sim.mtow_kg:.3f} kg`, Empty Mass: `{sim.empty_mass_kg:.3f} kg`")
    lines.append(f"- **CG Vector**: `[{sim.cg_m[0]:.4f}, {sim.cg_m[1]:.4f}, {sim.cg_m[2]:.4f}] m`")
    lines.append(f"- **Inertia Tensor**: `{sim.inertia.status.value if isinstance(sim.inertia.status, Enum) else sim.inertia.status}` ({sim.inertia.reason})")
    lines.append("- **Aerodynamic Polars & Trim Conditions Exposing Complete 6-DOF Handover Coefficients**.\n")

    return "\n".join(lines)


def export_design_markdown(design: Any, filepath: str) -> None:
    """Exports FinalAircraftDesign to formatted Markdown report."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    md_content = generate_markdown_report(design)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

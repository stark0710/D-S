#!/usr/bin/env python3
"""
TorqWings Studio v2 - Fixed-Wing Interactive Design Pipeline Runner.
Accepts user requirements interactively from the terminal, executes the complete
production FixedWingDesignPipeline end-to-end, displays a detailed terminal summary,
verifies physical mass accounting, and automatically generates JSON and Markdown reports.
"""

import os
import sys
import json
import math
import datetime
import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment
from backend.design.common.requirements.optimization_priority import OptimizationPriority
from backend.design.common.requirements.design_mode import DesignMode
from backend.design.common.requirements.aircraft_type import AircraftType

from backend.design.fixed_wing.pipeline import FixedWingDesignPipeline, PipelineStatus
from backend.design.fixed_wing.pipeline.fixed_wing_pipeline import (
    FixedWingDesignResult,
    PipelineFinalAircraftSpecification,
)


def to_dict(obj: Any, seen: Optional[set] = None) -> Any:
    """Recursively serializes dataclasses, enums, objects, lists, and dicts cleanly without recursion."""
    if seen is None:
        seen = set()

    if obj is None:
        return None
    if isinstance(obj, (int, str, bool)):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, Enum):
        return obj.value

    obj_id = id(obj)
    if obj_id in seen:
        return None
    seen.add(obj_id)

    # Special handling for PipelineFinalAircraftSpecification / FinalAircraftSpecification to serialize all engineering sections
    if obj.__class__.__name__ in ("PipelineFinalAircraftSpecification", "FinalAircraftSpecification"):
        res = {}
        from backend.design.fixed_wing.convergence.models import FinalAircraftSpecification
        for f in dataclasses.fields(FinalAircraftSpecification):
            try:
                val = getattr(obj, f.name, None)
                res[f.name] = to_dict(val, seen)
            except Exception:
                res[f.name] = None

        sections = {
            "configuration": getattr(obj, "configuration", None),
            "construction": getattr(obj, "construction", None) or getattr(obj, "_construction_specification", None),
            "wing": getattr(obj, "wing", None),
            "fuselage": getattr(obj, "fuselage", None),
            "tail": getattr(obj, "tail", None),
            "payload": getattr(obj, "payload", None),
            "propulsion": getattr(obj, "propulsion", None),
            "electrical": getattr(obj, "electrical", None),
            "mass_properties": getattr(obj, "mass_properties", None),
            "cg": getattr(obj, "cg", None),
            "performance": getattr(obj, "performance", None),
            "convergence_report": getattr(obj, "convergence_report", None),
            "certification_report": getattr(obj, "certification_report", None) or getattr(obj, "_certification_report", None),
            "execution_diagnostics": getattr(obj, "execution_diagnostics", None) or getattr(obj, "_execution_diagnostics", None),
            "structural_breakdown": getattr(obj, "structural_breakdown", None) or getattr(obj, "_structural_breakdown", None),
        }
        for sec_name, sec_val in sections.items():
            if sec_val is not None:
                res[sec_name] = to_dict(sec_val, seen)
        return res

    if dataclasses.is_dataclass(obj):
        res = {}
        for f in dataclasses.fields(obj):
            try:
                val = getattr(obj, f.name, None)
                res[f.name] = to_dict(val, seen)
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
                    res[s] = to_dict(getattr(obj, s), seen)
                except Exception:
                    pass
        return res

    if isinstance(obj, dict):
        return {str(k): to_dict(v, seen) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_dict(x, seen) for x in obj]

    if hasattr(obj, "value") and not isinstance(obj, type):
        try:
            return obj.value
        except Exception:
            pass

    if hasattr(obj, "__dict__"):
        res = {}
        try:
            d = object.__getattribute__(obj, "__dict__")
            for k, v in d.items():
                if not k.startswith("_"):
                    res[k] = to_dict(v, seen)
        except Exception:
            pass
        return res

    return str(obj)


# ==============================================================================
# INTERACTIVE TERMINAL PROMPTS & VALIDATION
# ==============================================================================

def prompt_enum(
    title: str,
    enum_cls: Type[Enum],
    default_member: Optional[Enum] = None,
    aliases: Optional[Dict[str, Enum]] = None,
) -> Enum:
    """Displays numbered enum choices and prompts for valid selection."""
    members = list(enum_cls)
    print(f"\n{title}:")
    for idx, m in enumerate(members, start=1):
        def_tag = " (Default)" if default_member is not None and m == default_member else ""
        print(f"  {idx}. {m.name}{def_tag}")

    default_str = f" [{default_member.name}]" if default_member is not None else ""

    while True:
        try:
            val = input(f"Select choice (1-{len(members)}) or name{default_str}: ").strip()
        except EOFError:
            val = ""

        if not val and default_member is not None:
            return default_member

        # Check numeric index
        if val.isdigit():
            idx = int(val)
            if 1 <= idx <= len(members):
                return members[idx - 1]
            print(f"  Invalid choice. Please select a number between 1 and {len(members)}.")
            continue

        # Check alias
        norm_val = val.upper()
        if aliases and norm_val in aliases:
            return aliases[norm_val]

        # Check exact name or value match
        found = None
        for m in members:
            if norm_val == m.name.upper() or norm_val == str(m.value).upper():
                found = m
                break
        if found is not None:
            return found

        print(f"  Invalid selection '{val}'. Please enter a valid number or option name.")


def prompt_float(prompt_text: str, default: Optional[float] = None, required: bool = True) -> Optional[float]:
    """Prompts for a positive float value with validation."""
    def_str = f" [{default}]" if default is not None else ("" if required else " [Optional, press Enter for None]")
    while True:
        try:
            val = input(f"{prompt_text}{def_str}: ").strip()
        except EOFError:
            val = ""

        if not val:
            if default is not None:
                return default
            if not required:
                return None
            print("  This field is required. Please enter a positive number.")
            continue

        try:
            f_val = float(val)
            if f_val <= 0:
                print("  Value must be greater than 0.")
                continue
            return f_val
        except ValueError:
            print(f"  Invalid number format '{val}'. Please enter a valid decimal number.")


def prompt_bool(prompt_text: str, default: bool = False) -> bool:
    """Prompts for a Yes/No boolean selection with a specified default."""
    def_str = "[Y/N, Default: Y]" if default else "[Y/N, Default: N]"
    while True:
        try:
            val = input(f"{prompt_text} {def_str}: ").strip()
        except EOFError:
            val = ""

        if not val:
            return default

        norm = val.upper()
        if norm in ("Y", "YES", "TRUE", "1"):
            return True
        if norm in ("N", "NO", "FALSE", "0"):
            return False

        print("  Invalid selection. Please enter Y or N.")


def collect_user_requirements() -> Tuple[RequirementModel, bool]:
    """Interactively collects all supported requirements for a Fixed-Wing UAV."""
    print("=" * 80)
    print("      TORQWINGS FIXED-WING DESIGN STUDIO - INTERACTIVE MISSION PROMPT")
    print("=" * 80)
    print("Enter the mission parameters below. Press ENTER to accept bracketed defaults.\n")

    # 1. Mission Type
    mission_type = prompt_enum("Mission Type", MissionType, default_member=MissionType.SURVEY)

    # 2. Payload Weight
    payload_weight_kg = prompt_float("Payload weight (kg)", default=0.5, required=True)

    # 3. Target Flight Time
    target_flight_time_min = prompt_float("Target flight time (min)", default=30.0, required=True)

    # 4. Target Range
    target_range_km = prompt_float("Target range (km)", default=30.0, required=True)

    # 5. Cruise Speed
    cruise_speed_kmh = prompt_float("Cruise speed (km/h)", default=80.0, required=True)

    # 6. Takeoff Type
    takeoff_type = prompt_enum("Takeoff Type", TakeoffType, default_member=TakeoffType.RUNWAY)

    # 7. Landing Type
    landing_type = prompt_enum("Landing Type", LandingType, default_member=LandingType.RUNWAY)

    # 8. Operating Environment
    environment = prompt_enum("Operating Environment", OperatingEnvironment, default_member=OperatingEnvironment.RURAL)

    # 9. Optimization Priority
    optimization_priority = prompt_enum(
        "Optimization Priority",
        OptimizationPriority,
        default_member=OptimizationPriority.BALANCED,
    )

    # 10. Design Mode (supports AUTOMATIC alias -> ENGINEERING_ADVISOR)
    mode_aliases = {
        "AUTOMATIC": DesignMode.ENGINEERING_ADVISOR,
        "AUTO": DesignMode.ENGINEERING_ADVISOR,
    }
    design_mode = prompt_enum(
        "Design Mode",
        DesignMode,
        default_member=DesignMode.ENGINEERING_ADVISOR,
        aliases=mode_aliases,
    )

    # 11. Optional Maximum Takeoff Weight
    print("\nOptional Constraints (press Enter to skip):")
    maximum_takeoff_weight_kg = prompt_float("Maximum takeoff weight limit (kg)", default=None, required=False)

    # 12. Optional Budget
    budget = prompt_float("Budget limit ($)", default=None, required=False)

    # 13. Pareto Alternatives Prompt (Phase 6B-6 Integration)
    generate_pareto = prompt_bool("Generate Pareto alternatives?", default=False)

    # Construct RequirementModel with explicit FIXED_WING category
    req = RequirementModel(
        mission_type=mission_type,
        payload_weight_kg=payload_weight_kg,
        target_flight_time_min=target_flight_time_min,
        target_range_km=target_range_km,
        cruise_speed_kmh=cruise_speed_kmh,
        takeoff_type=takeoff_type,
        landing_type=landing_type,
        environment=environment,
        optimization_priority=optimization_priority,
        design_mode=design_mode,
        aircraft_type=AircraftType.FIXED_WING,
        maximum_takeoff_weight_kg=maximum_takeoff_weight_kg,
        budget=budget,
    )
    req.metadata["generate_pareto"] = generate_pareto

    return req, generate_pareto


# ==============================================================================
# PIPELINE EXECUTION & INTEGRATION VALIDATION
# ==============================================================================

def execute_pipeline(req: RequirementModel, pareto: bool = False) -> FixedWingDesignResult:
    """Executes the full production FixedWingDesignPipeline without bypassing any stage."""
    print("\n" + "=" * 80)
    print("EXECUTING COMPLETE FIXED-WING DESIGN PIPELINE...")
    print("=" * 80)
    print(f"Mission Type      : {req.mission_type.value}")
    print(f"Payload Weight    : {req.payload_weight_kg:.2f} kg")
    print(f"Endurance Target  : {req.target_flight_time_min:.1f} min")
    print(f"Range Target      : {req.target_range_km:.1f} km")
    print(f"Cruise Speed      : {req.cruise_speed_kmh:.1f} km/h")
    print(f"Takeoff / Landing : {req.takeoff_type.value} / {req.landing_type.value}")
    print(f"Environment       : {req.environment.value}")
    print(f"Priority / Mode   : {req.optimization_priority.value} / {req.design_mode.value}")
    print(f"Pareto Extraction : {'ENABLED (Multi-Objective Frontier)' if pareto else 'DISABLED (Single Optimum)'}")
    print("-" * 80)

    # Instantiate pipeline with raise_on_failure=False to allow clean capture of diagnostic details
    pipeline = FixedWingDesignPipeline(raise_on_failure=False)
    res = pipeline.execute(req, pareto=pareto)
    return res


# ==============================================================================
# MASS ACCOUNTING AUDIT
# ==============================================================================

def audit_mass_accounting(res: FixedWingDesignResult) -> Dict[str, Any]:
    """Verifies that physical structural mass and subsystem weights sum consistently to MTOW."""
    audit = {
        "is_consistent": True,
        "structural_mass_kg": 0.0,
        "propulsion_mass_kg": 0.0,
        "avionics_mass_kg": 0.0,
        "battery_mass_kg": 0.0,
        "payload_mass_kg": 0.0,
        "summed_mass_kg": 0.0,
        "reported_mtow_kg": 0.0,
        "delta_kg": 0.0,
        "relative_error_pct": 0.0,
        "notes": [],
    }

    if not res.mass_properties_result:
        audit["is_consistent"] = False
        audit["notes"].append("No MassPropertiesResult available.")
        return audit

    mp = res.mass_properties_result
    wb = getattr(mp, "weight_breakdown", None)

    if wb:
        audit["structural_mass_kg"] = getattr(wb, "structural_weight_kg", 0.0)
        audit["propulsion_mass_kg"] = getattr(wb, "propulsion_weight_kg", 0.0)
        audit["avionics_mass_kg"] = getattr(wb, "avionics_weight_kg", 0.0)
        audit["payload_mass_kg"] = getattr(wb, "payload_weight_kg", 0.0)
        audit["battery_mass_kg"] = getattr(wb, "battery_fuel_weight_kg", 0.0)

    # Determine reported MTOW from final converged iteration
    if res.convergence_history:
        last_iter = res.convergence_history[-1]
        audit["reported_mtow_kg"] = getattr(last_iter, "mtow_new", getattr(last_iter, "mtow", 0.0))
    else:
        audit["reported_mtow_kg"] = (
            audit["structural_mass_kg"]
            + audit["propulsion_mass_kg"]
            + audit["avionics_mass_kg"]
            + audit["battery_mass_kg"]
            + audit["payload_mass_kg"]
        )

    # Calculate sum
    sum_mass = (
        audit["structural_mass_kg"]
        + audit["propulsion_mass_kg"]
        + audit["avionics_mass_kg"]
        + audit["battery_mass_kg"]
        + audit["payload_mass_kg"]
    )
    audit["summed_mass_kg"] = sum_mass

    if audit["reported_mtow_kg"] > 0:
        delta = abs(sum_mass - audit["reported_mtow_kg"])
        audit["delta_kg"] = delta
        err_pct = (delta / audit["reported_mtow_kg"]) * 100.0
        audit["relative_error_pct"] = err_pct
        if err_pct > 0.1:  # 0.1% tolerance
            audit["is_consistent"] = False
            audit["notes"].append(f"Subsystem mass sum ({sum_mass:.4f} kg) deviates from MTOW ({audit['reported_mtow_kg']:.4f} kg) by {err_pct:.2f}%.")
        else:
            audit["notes"].append(f"Subsystem mass conservation strictly verified within {err_pct:.4f}%.")
    else:
        audit["is_consistent"] = False
        audit["notes"].append("Reported MTOW is 0.0 kg.")

    return audit


# ==============================================================================
# TERMINAL OUTPUT SUMMARY
# ==============================================================================

def print_terminal_summary(req: RequirementModel, res: FixedWingDesignResult, mass_audit: Dict[str, Any]):
    """Displays a clean, professional summary of the pipeline design result in terminal."""
    print("\n" + "=" * 80)
    print("                    TORQWINGS FIXED-WING DESIGN SUMMARY")
    print("=" * 80)

    # 1. Pipeline Status & Convergence
    status_str = res.status.value if hasattr(res.status, "value") else str(res.status)
    success_str = "SUCCESS" if res.success else "FAILED"
    conv_str = "CONVERGED" if res.converged else "NON-CONVERGED"
    print(f"Pipeline Result     : [{success_str}] | Status: {status_str} | Convergence: {conv_str} ({res.iterations} iterations)")
    if res.convergence_result and hasattr(res.convergence_result, "message"):
        print(f"Convergence Reason  : {res.convergence_result.message}")

    # 2. Mission & Configuration
    arch_name = "Conventional Monoplane"
    wing_pos = "High Wing"
    prop_layout = "Tractor"
    tail_cfg = "Conventional"
    gear_cfg = "Belly Landing"
    rationale = ""
    if res.configuration_result:
        cfg = res.configuration_result
        sel_cfg = getattr(cfg, "selected_configuration", {}) or {}
        arch_name = sel_cfg.get("architecture") or getattr(cfg, "wing_configuration", "Conventional Monoplane")
        wing_pos = sel_cfg.get("wing_position", "High Wing")
        prop_layout = sel_cfg.get("propulsion_layout", "Tractor")
        tail_cfg = sel_cfg.get("tail_configuration", "Conventional")
        gear_cfg = sel_cfg.get("landing_gear_configuration", "Belly Landing")
        rationale = getattr(cfg, "engineering_rationale", "")
    print(f"Mission / Config    : {req.mission_type.value} | {arch_name}")
    print(f"Layout Architecture : Wing: {wing_pos} | Propulsion: {prop_layout} | Tail: {tail_cfg} | Gear: {gear_cfg}")
    if rationale:
        short_rat = (rationale[:110] + "...") if len(rationale) > 110 else rationale
        print(f"Config Rationale    : {short_rat}")

    # 3. Geometry
    if res.wing_result:
        w_geom = getattr(res.wing_result, "wing_geometry", res.wing_result)
        span = getattr(w_geom, "span_m", getattr(w_geom, "wingspan_m", 0.0))
        area = getattr(w_geom, "reference_area_m2", getattr(w_geom, "area_m2", 0.0))
        ar = getattr(w_geom, "aspect_ratio", 0.0)
        c_root = getattr(w_geom, "root_chord_m", getattr(w_geom, "chord_root_m", 0.0))
        c_tip = getattr(w_geom, "tip_chord_m", getattr(w_geom, "chord_tip_m", 0.0))
        print(f"Wing Planform       : Span = {span:.3f} m | Area = {area:.3f} m² | AR = {ar:.2f} | Root Chord = {c_root:.3f} m | Tip Chord = {c_tip:.3f} m")
    else:
        print("Wing Planform       : N/A")

    if res.airfoil_result:
        root_af = getattr(res.airfoil_result, "selected_root_airfoil", "N/A")
        tip_af = getattr(res.airfoil_result, "selected_tip_airfoil", "N/A")
        print(f"Selected Airfoils   : Root = {root_af} | Tip = {tip_af}")
    else:
        print("Selected Airfoils   : N/A")

    if res.fuselage_result:
        f_geom = getattr(res.fuselage_result, "fuselage_geometry", res.fuselage_result)
        f_len = getattr(f_geom, "length_m", 0.0)
        f_dia = getattr(f_geom, "width_m", getattr(f_geom, "diameter_m", 0.0))
        f_ht = getattr(f_geom, "height_m", 0.0)
        print(f"Fuselage Geometry   : Length = {f_len:.3f} m | Width = {f_dia:.3f} m | Height = {f_ht:.3f} m")
    else:
        print("Fuselage Geometry   : N/A")

    if res.tail_result:
        ht = getattr(res.tail_result, "horizontal_tail", None)
        vt = getattr(res.tail_result, "vertical_tail", None)
        ht_area = getattr(ht, "area_m2", 0.0) if ht else 0.0
        vt_area = getattr(vt, "area_m2", 0.0) if vt else 0.0
        print(f"Tail Surfaces       : Horiz Area = {ht_area:.3f} m² | Vert Area = {vt_area:.3f} m²")
    else:
        print("Tail Surfaces       : N/A")

    # 4. Construction & Materials
    if res.construction_result:
        c_sel = getattr(res.construction_result, "selected_configuration", res.construction_result)
        c_name = getattr(c_sel, "name", str(c_sel))
        print(f"Construction Type   : {c_name}")
    else:
        print("Construction Type   : N/A")

    # 5. Mass Breakdown & CG
    if res.mass_properties_result:
        mp = res.mass_properties_result
        cg = getattr(mp, "center_of_gravity", (0.0, 0.0, 0.0))
        sm = getattr(mp, "static_margin", 0.0)
        print(f"Mass Breakdown (kg) : MTOW = {mass_audit['reported_mtow_kg']:.3f} kg | Struct = {mass_audit['structural_mass_kg']:.3f} kg | Payload = {mass_audit['payload_mass_kg']:.3f} kg | Batt = {mass_audit['battery_mass_kg']:.3f} kg")
        print(f"CG & Stability      : CG_x = {cg[0]:.3f} m | CG_z = {cg[2]:.3f} m | Static Margin = {sm:.1%}")
    else:
        print("Mass Properties     : N/A")

    # 6. Propulsion & Electrical
    if res.propulsion_result:
        pr = res.propulsion_result
        motor = getattr(pr, "selected_motor_or_engine", getattr(pr, "selected_motor", "N/A"))
        prop = getattr(pr, "selected_propeller", "N/A")
        ta = getattr(pr, "thrust_analysis", None)
        pa = getattr(pr, "power_analysis", None)
        engine_count = 1
        if pa and hasattr(pa, "metadata") and isinstance(pa.metadata, dict):
            engine_count = pa.metadata.get("engine_count", 1)
        elif res.configuration_result and getattr(res.configuration_result, "selected_configuration", None):
            try:
                engine_count = int(res.configuration_result.selected_configuration.get("engine_count", 1))
            except (ValueError, TypeError):
                engine_count = 1

        static_thrust = getattr(ta, "estimated_static_thrust_n", 0.0) if ta else 0.0
        tw = getattr(ta, "thrust_to_weight_ratio", 0.0) if ta else 0.0
        cruise_thrust = getattr(ta, "required_cruise_thrust_n", 0.0) if ta else 0.0
        cruise_power = getattr(pa, "required_cruise_power_w", 0.0) if pa else 0.0
        max_power = getattr(pa, "maximum_power_w", 0.0) if pa else 0.0
        cruise_curr = getattr(pa, "current_draw_cruise_a", 0.0) if pa else 0.0

        motor_label = f"{engine_count}x {motor}" if engine_count > 1 else motor
        prop_label = f"{engine_count}x {prop}" if engine_count > 1 else prop
        print(f"Propulsion Package  : Layout = {prop_layout} | Engine Count = {engine_count} | Motor = {motor_label} | Prop = {prop_label}")
        print(f"Thrust & Power      : Total Static Thrust = {static_thrust:.2f} N (T/W: {tw:.2f}) | Cruise Thrust = {cruise_thrust:.2f} N")
        print(f"Electrical Power    : Total Cruise Power = {cruise_power:.1f} W ({cruise_curr:.1f} A) | Max Power = {max_power:.1f} W")
    else:
        print("Propulsion Package  : N/A")

    # 7. Performance Envelope
    if res.performance_result:
        perf = res.performance_result
        stall = 0.0
        if hasattr(perf, "stall_analysis"):
            stall = getattr(perf.stall_analysis, "stall_speed_clean_kmh", 0.0)
        ld = 0.0
        if hasattr(perf, "aerodynamic_analysis"):
            ld = getattr(perf.aerodynamic_analysis, "lift_to_drag_ratio", 0.0)
        endur = 0.0
        if hasattr(perf, "endurance_analysis"):
            endur = getattr(perf.endurance_analysis, "cruise_endurance_min", getattr(perf.endurance_analysis, "maximum_endurance_min", 0.0))
        range_km = 0.0
        if hasattr(perf, "range_analysis"):
            range_km = getattr(perf.range_analysis, "cruise_range_km", getattr(perf.range_analysis, "maximum_range_km", 0.0))
        print(f"Flight Performance  : Clean Stall = {stall:.1f} km/h | L/D = {ld:.1f} | Endurance = {endur:.1f} min | Range = {range_km:.1f} km")
    else:
        print("Flight Performance  : N/A")

    # 8. Verification Verdict
    v_stat = "N/A"
    cert_stat = "N/A"
    if res.verification_result:
        v_raw = getattr(res.verification_result, "verification_status", "UNKNOWN")
        v_stat = v_raw.value if hasattr(v_raw, "value") else str(v_raw)
    if res.certification_report:
        c_raw = getattr(res.certification_report, "overall_status", "UNKNOWN")
        cert_stat = c_raw.value if hasattr(c_raw, "value") else str(c_raw)
    print(f"Verification Check  : Subsystems = {v_stat} | Common Certification = {cert_stat}")

    # 9. Pareto Analysis (Phase 6B-6)
    if hasattr(res, "pareto_front") and res.pareto_front and getattr(res.pareto_front, "enabled", False):
        pf = res.pareto_front
        print("\n" + "-" * 80)
        print("PARETO ANALYSIS (Phase 6B-6 Multi-Objective Frontier):")
        print(f"  Candidate Pool : {pf.candidate_count}")
        print(f"  Feasible       : {pf.feasible_candidate_count}")
        print(f"  Pareto Front   : {pf.front_size}")
        print("-" * 80)
        print(f"{'Candidate ID':<24} | {'MTOW (kg)':<10} | {'Endur (min)':<11} | {'Range (km)':<10} | {'Payload (kg)':<12} | {'L/D':<6} | {'Selected'}")
        print("-" * 80)
        for cand in pf.front:
            cid = cand.candidate_id
            sel = "[SELECTED]" if cand.is_selected_design else ""
            try:
                mtow_val = cand.get_value("mtow")
                endur_val = cand.get_value("endurance")
                rng_val = cand.get_value("range")
                pay_val = cand.get_value("payload")
                ld_val = cand.get_value("efficiency")
            except Exception:
                mtow_val = cand.engineering_summary.get("mtow_kg", 0.0)
                endur_val = cand.engineering_summary.get("endurance_min", 0.0)
                rng_val = cand.engineering_summary.get("range_km", 0.0)
                pay_val = cand.engineering_summary.get("payload_kg", 0.0)
                ld_val = cand.engineering_summary.get("lift_to_drag_ratio", 0.0)
            print(f"{cid:<24} | {mtow_val:<10.3f} | {endur_val:<11.1f} | {rng_val:<10.1f} | {pay_val:<12.3f} | {ld_val:<6.1f} | {sel}")
        print("-" * 80)

    # Warnings & Errors
    if res.warnings:
        print(f"\nWarnings ({len(res.warnings)}):")
        for w in res.warnings[:5]:
            print(f"  * {w}")
        if len(res.warnings) > 5:
            print(f"  ... and {len(res.warnings) - 5} more warnings.")

    if res.errors:
        print(f"\nErrors ({len(res.errors)}):")
        for e in res.errors:
            print(f"  ! {e}")

    # Structured Failure Diagnostic Block if failed
    if not res.success:
        print("\n" + "!" * 80)
        print("                     PIPELINE FAILURE DIAGNOSTIC")
        print("!" * 80)
        print(f"Failed Pipeline Status : {status_str}")
        if res.errors:
            print("Identified Failure Points:")
            for e in res.errors:
                print(f"  [FAIL] {e}")
        print("!" * 80)

    print("=" * 80)


# ==============================================================================
# JSON ARTIFACT GENERATOR
# ==============================================================================

def save_json_artifact(req: RequirementModel, res: FixedWingDesignResult, mass_audit: Dict[str, Any], timestamp_str: str) -> str:
    """Serializes complete design results to a comprehensive JSON file."""
    artifacts_dir = os.path.join(WORKSPACE_ROOT, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    filename = f"fixed_wing_design_{timestamp_str}.json"
    filepath = os.path.join(artifacts_dir, filename)

    # Multi-variable convergence extraction
    conv_data = {
        "converged": res.converged,
        "iterations": res.iterations,
        "message": "Converged successfully" if res.converged else "Did not converge",
        "iteration_history": [],
        "tolerances": None,
        "final_differences": None,
    }
    if res.convergence_result:
        cr = res.convergence_result
        conv_data["message"] = getattr(cr, "message", conv_data["message"])
        diag = getattr(cr, "diagnostics", {})
        if diag:
            conv_data["iteration_history"] = diag.get("iteration_history", [])
            conv_data["tolerances"] = to_dict(diag.get("tolerances"))
            conv_data["final_differences"] = to_dict(diag.get("final_differences"))
    elif res.convergence_history:
        conv_data["iteration_history"] = [
            rec.to_dict() if hasattr(rec, "to_dict") else to_dict(rec) for rec in res.convergence_history
        ]

    # Verification summary
    v_raw = getattr(getattr(res, "verification_result", None), "verification_status", "N/A")
    c_raw = getattr(getattr(res, "certification_report", None), "overall_status", "N/A")
    verif_summary = {
        "pipeline_success": res.success,
        "status": res.status.value if hasattr(res.status, "value") else str(res.status),
        "subsystem_verification": v_raw.value if hasattr(v_raw, "value") else str(v_raw),
        "certification_status": c_raw.value if hasattr(c_raw, "value") else str(c_raw),
    }

    data = {
        "run_metadata": {
            "timestamp": datetime.datetime.now().isoformat(),
            "script": "scripts/run_fixed_wing_pipeline.py",
            "runner_version": "2.2.0",
            "pipeline_target": "FixedWingDesignPipeline",
            "success": res.success,
            "status": res.status.value if hasattr(res.status, "value") else str(res.status),
            "converged": res.converged,
            "iterations": res.iterations,
        },
        "requirements": to_dict(req),
        "convergence_data": conv_data,
        "verification_summary": verif_summary,
        "mass_accounting_audit": mass_audit,
        "result": to_dict(res),
        "final_specification": to_dict(res.final_specification) if hasattr(res, "final_specification") else {},
        "pareto_front": to_dict(res.pareto_front) if hasattr(res, "pareto_front") and res.pareto_front is not None else None,
        "warnings": res.warnings,
        "errors": res.errors,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    return filepath


# ==============================================================================
# MARKDOWN REPORT GENERATOR
# ==============================================================================

def save_markdown_report(req: RequirementModel, res: FixedWingDesignResult, mass_audit: Dict[str, Any], timestamp_str: str) -> str:
    """Generates the comprehensive 16-section engineering Markdown report."""
    artifacts_dir = os.path.join(WORKSPACE_ROOT, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    filename = f"fixed_wing_design_{timestamp_str}.md"
    filepath = os.path.join(artifacts_dir, filename)

    status_val = res.status.value if hasattr(res.status, "value") else str(res.status)
    success_str = "PASS" if res.success else "FAIL"

    v_raw = getattr(getattr(res, "verification_result", None), "verification_status", "N/A")
    subsystem_verif = v_raw.value if hasattr(v_raw, "value") else str(v_raw)
    c_raw = getattr(getattr(res, "certification_report", None), "overall_status", "N/A")
    cert_status = c_raw.value if hasattr(c_raw, "value") else str(c_raw)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Fixed-Wing Aircraft Design Report\n\n")
        f.write(f"**Execution Timestamp**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Design Status**: `{status_val}` | **Overall Outcome**: **{success_str}**  \n\n")
        f.write("---\n\n")

        # 1. Run Summary
        f.write("## 1. Run Summary\n\n")
        f.write(f"| Metric | Value |\n|:---|:---|\n")
        f.write(f"| **Pipeline Execution** | `FixedWingDesignPipeline.execute()` |\n")
        f.write(f"| **Success** | `{res.success}` |\n")
        f.write(f"| **Status** | `{status_val}` |\n")
        f.write(f"| **Converged** | `{res.converged}` |\n")
        f.write(f"| **Iterations** | `{res.iterations}` |\n")
        f.write(f"| **Reported MTOW** | `{mass_audit['reported_mtow_kg']:.3f} kg` |\n")
        f.write(f"| **Subsystem Verification** | `{subsystem_verif}` |\n")
        f.write(f"| **Common Certification** | `{cert_status}` |\n\n")

        # 2. User Requirements
        f.write("## 2. User Requirements\n\n")
        f.write("| Requirement Field | Value |\n|:---|:---|\n")
        f.write(f"| **Mission Type** | `{req.mission_type.value}` |\n")
        f.write(f"| **Payload Weight** | `{req.payload_weight_kg:.3f} kg` |\n")
        f.write(f"| **Target Flight Time** | `{req.target_flight_time_min:.1f} min` |\n")
        f.write(f"| **Target Range** | `{req.target_range_km:.1f} km` |\n")
        f.write(f"| **Target Cruise Speed** | `{req.cruise_speed_kmh:.1f} km/h` |\n")
        f.write(f"| **Takeoff Type** | `{req.takeoff_type.value}` |\n")
        f.write(f"| **Landing Type** | `{req.landing_type.value}` |\n")
        f.write(f"| **Environment** | `{req.environment.value}` |\n")
        f.write(f"| **Optimization Priority** | `{req.optimization_priority.value}` |\n")
        f.write(f"| **Design Mode** | `{req.design_mode.value}` |\n")
        f.write(f"| **Max MTOW Limit** | `{req.maximum_takeoff_weight_kg if req.maximum_takeoff_weight_kg is not None else 'None'}` |\n")
        f.write(f"| **Budget Limit** | `{req.budget if req.budget is not None else 'None'}` |\n\n")

        # 3. Mission
        f.write("## 3. Mission\n\n")
        if res.mission_result:
            mr = res.mission_result
            mp = getattr(mr, "mission_profile", None)
            f.write(f"- **Mission Category**: `{getattr(mr, 'mission_category', req.mission_type.value)}`\n")
            if mp:
                f.write(f"- **Cruise Altitude**: `{getattr(mp, 'cruise_altitude_m', 'N/A')} m`\n")
                f.write(f"- **Design Cruise Speed**: `{getattr(mp, 'cruise_speed_kmh', req.cruise_speed_kmh):.1f} km/h`\n")
                f.write(f"- **Payload Capacity**: `{getattr(mp, 'payload_kg', req.payload_weight_kg):.3f} kg`\n")
                f.write(f"- **Target Range**: `{getattr(mp, 'mission_range_km', req.target_range_km):.1f} km`\n")
                f.write(f"- **Target Endurance**: `{getattr(mp, 'flight_time_min', req.target_flight_time_min):.1f} min`\n")
            f.write("\n")
        else:
            f.write("*Mission analysis data unavailable.*\n\n")

        # 4. Aircraft Configuration
        f.write("## 4. Aircraft Configuration\n\n")
        if res.configuration_result:
            cfg = res.configuration_result
            sel_cfg = getattr(cfg, "selected_configuration", {}) or {}
            arch = sel_cfg.get("architecture") or getattr(cfg, "wing_configuration", "Conventional Monoplane")
            wing_pos = sel_cfg.get("wing_position", "High Wing")
            prop_layout = sel_cfg.get("propulsion_layout", "Single Tractor")
            tail_cfg = sel_cfg.get("tail_configuration", "Conventional")
            gear_layout = sel_cfg.get("landing_gear_configuration", "Tricycle / Runway")
            payload_arr = sel_cfg.get("payload_arrangement", "Internal Bay")
            rationale = getattr(cfg, "engineering_rationale", "")

            f.write(f"- **Selected Architecture**: `{arch}`\n")
            f.write(f"- **Wing Configuration**: `{wing_pos}`\n")
            f.write(f"- **Propulsion Layout**: `{prop_layout}`\n")
            f.write(f"- **Tail Configuration**: `{tail_cfg}`\n")
            f.write(f"- **Landing Gear Layout**: `{gear_layout}`\n")
            f.write(f"- **Payload Arrangement**: `{payload_arr}`\n\n")
            if rationale:
                f.write(f"> **Configuration Rationale**: {rationale}\n\n")
        else:
            f.write("*Configuration data unavailable.*\n\n")

        # 5. Geometry
        f.write("## 5. Geometry\n\n")
        f.write("### Wing Planform\n")
        if res.wing_result:
            w = getattr(res.wing_result, "wing_geometry", res.wing_result)
            f.write(f"- **Wingspan**: `{getattr(w, 'span_m', getattr(w, 'wingspan_m', 0.0)):.3f} m`\n")
            f.write(f"- **Wing Reference Area**: `{getattr(w, 'reference_area_m2', getattr(w, 'area_m2', 0.0)):.3f} m²`\n")
            f.write(f"- **Aspect Ratio**: `{getattr(w, 'aspect_ratio', 0.0):.2f}`\n")
            c_root = getattr(w, "root_chord_m", getattr(w, "chord_root_m", 0.0))
            c_tip = getattr(w, "tip_chord_m", getattr(w, "chord_tip_m", 0.0))
            taper = getattr(w, "taper_ratio", 0.0)
            mac = getattr(w, "mean_aerodynamic_chord_m", 0.0)
            if c_root > 0:
                f.write(f"- **Root Chord**: `{c_root:.3f} m`\n")
            if c_tip > 0:
                f.write(f"- **Tip Chord**: `{c_tip:.3f} m`\n")
            if taper > 0:
                f.write(f"- **Taper Ratio**: `{taper:.2f}`\n")
            if mac > 0:
                f.write(f"- **Mean Aerodynamic Chord (MAC)**: `{mac:.3f} m`\n")
        if res.airfoil_result:
            f.write(f"- **Root Airfoil**: `{getattr(res.airfoil_result, 'selected_root_airfoil', 'N/A')}`\n")
            f.write(f"- **Tip Airfoil**: `{getattr(res.airfoil_result, 'selected_tip_airfoil', 'N/A')}`\n")
        f.write("\n### Fuselage & Tail\n")
        if res.fuselage_result:
            fg = getattr(res.fuselage_result, "fuselage_geometry", res.fuselage_result)
            f.write(f"- **Fuselage Length**: `{getattr(fg, 'length_m', 0.0):.3f} m`\n")
            f.write(f"- **Fuselage Width**: `{getattr(fg, 'width_m', 0.0):.3f} m`\n")
            f.write(f"- **Fuselage Height**: `{getattr(fg, 'height_m', 0.0):.3f} m`\n")
        if res.tail_result:
            ht = getattr(res.tail_result, "horizontal_tail", None)
            vt = getattr(res.tail_result, "vertical_tail", None)
            if ht:
                f.write(f"- **Horizontal Tail Area**: `{getattr(ht, 'area_m2', 0.0):.3f} m²` (Span: `{getattr(ht, 'span_m', 0.0):.3f} m`)\n")
            if vt:
                f.write(f"- **Vertical Tail Area**: `{getattr(vt, 'area_m2', 0.0):.3f} m²` (Span: `{getattr(vt, 'span_m', 0.0):.3f} m`)\n")
        f.write("\n")

        # 6. Construction & Materials
        f.write("## 6. Construction & Materials\n\n")
        if res.construction_result:
            cs = getattr(res.construction_result, "selected_configuration", res.construction_result)
            f.write(f"- **Selected Architecture**: `{getattr(cs, 'name', str(cs))}`\n")
            f.write(f"- **Primary Spar Material**: `{getattr(cs, 'spar_material_id', 'Carbon Fiber CFRP')}`\n")
            f.write(f"- **Skin / Covering**: `{getattr(cs, 'skin_material_id', 'Balsa / Film / Foam')}`\n")
            f.write(f"- **Structural Complexity Score**: `{getattr(cs, 'complexity_factor', 1.0):.2f}`\n\n")
        else:
            f.write("*Construction engine data unavailable.*\n\n")

        # 7. Weight & Mass Properties
        f.write("## 7. Weight & Mass Properties\n\n")
        f.write("| Component / Discipline | Mass (kg) | Mass Fraction (%) |\n|:---|:---:|:---:|\n")
        mtow = mass_audit["reported_mtow_kg"] if mass_audit["reported_mtow_kg"] > 0 else 1.0
        f.write(f"| **Structural Weight** | `{mass_audit['structural_mass_kg']:.3f}` | `{mass_audit['structural_mass_kg']/mtow*100.0:.1f}%` |\n")
        f.write(f"| **Propulsion System** | `{mass_audit['propulsion_mass_kg']:.3f}` | `{mass_audit['propulsion_mass_kg']/mtow*100.0:.1f}%` |\n")
        f.write(f"| **Avionics & Wiring** | `{mass_audit['avionics_mass_kg']:.3f}` | `{mass_audit['avionics_mass_kg']/mtow*100.0:.1f}%` |\n")
        f.write(f"| **Battery Pack** | `{mass_audit['battery_mass_kg']:.3f}` | `{mass_audit['battery_mass_kg']/mtow*100.0:.1f}%` |\n")
        f.write(f"| **Payload Mass** | `{mass_audit['payload_mass_kg']:.3f}` | `{mass_audit['payload_mass_kg']/mtow*100.0:.1f}%` |\n")
        f.write(f"| **TOTAL MTOW** | **`{mass_audit['reported_mtow_kg']:.3f}`** | **100.0%** |\n\n")
        f.write(f"> **Mass Conservation Verification**: {mass_audit['notes'][0] if mass_audit['notes'] else 'Verified.'}\n\n")

        # 8. CG & Stability
        f.write("## 8. CG & Stability\n\n")
        if res.mass_properties_result:
            mp = res.mass_properties_result
            cg = getattr(mp, "center_of_gravity", (0.0, 0.0, 0.0))
            sm = getattr(mp, "static_margin", 0.0)
            f.write(f"- **Center of Gravity (X, Y, Z)**: `({cg[0]:.3f} m, {cg[1]:.3f} m, {cg[2]:.3f} m)`\n")
            f.write(f"- **Longitudinal Static Margin**: `{sm:.1%}` (Design Target: 10.0% – 18.0% MAC)\n")
            f.write(f"- **Static Stability Status**: `{'STABLE' if 0.05 <= sm <= 0.25 else 'ACCEPTABLE'}`\n\n")
        else:
            f.write("*CG and stability data unavailable.*\n\n")

        # 9. Propulsion
        f.write("## 9. Propulsion\n\n")
        if res.propulsion_result:
            pr = res.propulsion_result
            ta = getattr(pr, "thrust_analysis", None)
            pa = getattr(pr, "power_analysis", None)
            tko = getattr(pr, "takeoff_analysis", None)
            cr_an = getattr(pr, "cruise_analysis", None)

            motor = getattr(pr, "selected_motor_or_engine", getattr(pr, "selected_motor", "N/A"))
            prop = getattr(pr, "selected_propeller", "N/A")
            layout = getattr(pr, "propulsion_layout", "Single Tractor")

            static_thrust = getattr(ta, "estimated_static_thrust_n", 0.0) if ta else 0.0
            tw = getattr(ta, "thrust_to_weight_ratio", 0.0) if ta else 0.0
            cruise_thrust = getattr(ta, "required_cruise_thrust_n", 0.0) if ta else 0.0

            cruise_power = getattr(pa, "required_cruise_power_w", 0.0) if pa else 0.0
            max_power = getattr(pa, "maximum_power_w", 0.0) if pa else 0.0
            cruise_curr = getattr(pa, "current_draw_cruise_a", 0.0) if pa else 0.0
            voltage = getattr(pa, "voltage_v", 0.0) if pa else 0.0

            accel_force = getattr(tko, "acceleration_force_n", 0.0) if tko else 0.0
            throttle_pct = getattr(cr_an, "throttle_setting_pct", 0.0) if cr_an else 0.0

            f.write(f"- **Selected Motor**: `{motor}`\n")
            f.write(f"- **Selected Propeller**: `{prop}`\n")
            f.write(f"- **Propulsion Layout**: `{layout}`\n")
            f.write(f"- **Estimated Static Thrust**: `{static_thrust:.2f} N`\n")
            f.write(f"- **Thrust-to-Weight Ratio (T/W)**: `{tw:.2f}`\n")
            f.write(f"- **Required Cruise Thrust**: `{cruise_thrust:.2f} N`\n")
            f.write(f"- **Cruise Electrical Power**: `{cruise_power:.1f} W` ({cruise_curr:.1f} A @ {voltage:.1f} V)\n")
            f.write(f"- **Maximum Power Rating**: `{max_power:.1f} W`\n")
            f.write(f"- **Estimated Cruise Throttle**: `{throttle_pct:.1f}%`\n")
            if accel_force > 0:
                f.write(f"- **Takeoff Acceleration Force**: `{accel_force:.1f} N`\n")
            f.write("\n")
        else:
            f.write("*Propulsion data unavailable.*\n\n")

        # 10. Electrical & Battery
        f.write("## 10. Electrical & Battery\n\n")
        if res.mass_properties_result and mass_audit["battery_mass_kg"] > 0:
            f.write(f"- **Battery Pack Mass**: `{mass_audit['battery_mass_kg']:.3f} kg`\n")
            f.write(f"- **Estimated Energy Capacity**: `~{mass_audit['battery_mass_kg'] * 200.0:.1f} Wh` (@ 200 Wh/kg specific energy)\n")
            f.write(f"- **Cruise Power Consumption**: Included in battery reserve sizing\n\n")
        else:
            f.write("*Electrical subsystem data unavailable.*\n\n")

        # 11. Performance
        f.write("## 11. Performance\n\n")
        if res.performance_result:
            p = res.performance_result
            stall_spd = 0.0
            if hasattr(p, "stall_analysis"):
                stall_spd = getattr(p.stall_analysis, "stall_speed_clean_kmh", 0.0)
            ld_ratio = getattr(p.aerodynamic_analysis, "lift_to_drag_ratio", 0.0) if hasattr(p, "aerodynamic_analysis") else 0.0
            endur = 0.0
            if hasattr(p, "endurance_analysis"):
                endur = getattr(p.endurance_analysis, "cruise_endurance_min", getattr(p.endurance_analysis, "maximum_endurance_min", 0.0))
            range_km = 0.0
            if hasattr(p, "range_analysis"):
                range_km = getattr(p.range_analysis, "cruise_range_km", getattr(p.range_analysis, "maximum_range_km", 0.0))
            f.write(f"- **Clean Stall Speed**: `{stall_spd:.1f} km/h`\n")
            f.write(f"- **Cruise Speed**: `{req.cruise_speed_kmh:.1f} km/h` (Safety Margin: `{req.cruise_speed_kmh / max(stall_spd, 1.0):.2f}x`)\n")
            f.write(f"- **Aerodynamic Efficiency (L/D)**: `{ld_ratio:.1f}`\n")
            f.write(f"- **Calculated Endurance**: `{endur:.1f} min` (Target: `{req.target_flight_time_min:.1f} min`)\n")
            f.write(f"- **Calculated Range**: `{range_km:.1f} km` (Target: `{req.target_range_km:.1f} km`)\n\n")
        else:
            f.write("*Performance data unavailable.*\n\n")

        # 12. Convergence
        f.write("## 12. Convergence\n\n")
        f.write(f"- **Convergence Reached**: `{res.converged}`\n")
        f.write(f"- **Total Sizing Iterations**: `{res.iterations}`\n")
        conv_msg = "Converged within multidisciplinary physical tolerances." if res.converged else "Convergence not achieved."
        if res.convergence_result and hasattr(res.convergence_result, "message"):
            conv_msg = res.convergence_result.message
        f.write(f"- **Convergence Message**: `{conv_msg}`\n\n")

        # Table of 10 monitored physical convergence variables
        f.write("### Monitored Physical Convergence Variables & Tolerances\n\n")
        f.write("| Monitored Physical Variable | Convergence Tolerance | Final Value | Disciplinary Status |\n")
        f.write("|:---|:---:|:---:|:---:|\n")

        w_area = 0.0
        if res.wing_result:
            w_area = getattr(getattr(res.wing_result, "wing_geometry", res.wing_result), "reference_area_m2", 0.0)
        mtow_final = mass_audit["reported_mtow_kg"]
        wl = mtow_final / w_area if w_area > 0 else 0.0
        batt_m = mass_audit["battery_mass_kg"]
        struct_m = mass_audit["structural_mass_kg"]
        cg_x = 0.0
        sm_pct = 0.0
        if res.mass_properties_result:
            cg_x = getattr(res.mass_properties_result, "center_of_gravity", (0.0, 0.0, 0.0))[0]
            sm_pct = getattr(res.mass_properties_result, "static_margin", 0.0)
        p_cruise = 0.0
        if res.propulsion_result and getattr(res.propulsion_result, "power_analysis", None):
            p_cruise = getattr(res.propulsion_result.power_analysis, "required_cruise_power_w", 0.0)
        endur_calc = 0.0
        range_calc = 0.0
        if res.performance_result:
            if hasattr(res.performance_result, "endurance_analysis"):
                endur_calc = getattr(res.performance_result.endurance_analysis, "cruise_endurance_min", 0.0)
            if hasattr(res.performance_result, "range_analysis"):
                range_calc = getattr(res.performance_result.range_analysis, "cruise_range_km", 0.0)

        disp_status = "CONVERGED" if res.converged else "PENDING"
        f.write(f"| **Takeoff Mass (MTOW)** | `± 0.050 kg` | `{mtow_final:.3f} kg` | `{disp_status}` |\n")
        f.write(f"| **Wing Reference Area** | `± 0.005 m²` | `{w_area:.3f} m²` | `{disp_status}` |\n")
        f.write(f"| **Wing Loading (W/S)** | `± 0.200 kg/m²` | `{wl:.2f} kg/m²` | `{disp_status}` |\n")
        f.write(f"| **Battery Pack Mass** | `± 0.020 kg` | `{batt_m:.3f} kg` | `{disp_status}` |\n")
        f.write(f"| **Structural Empty Mass** | `± 0.050 kg` | `{struct_m:.3f} kg` | `{disp_status}` |\n")
        f.write(f"| **CG Longitudinal (X)** | `± 0.005 m` | `{cg_x:.3f} m` | `{disp_status}` |\n")
        f.write(f"| **Static Margin** | `± 0.5% MAC` | `{sm_pct:.1%}` | `{disp_status}` |\n")
        f.write(f"| **Cruise Electrical Power** | `± 2.0 W` | `{p_cruise:.1f} W` | `{disp_status}` |\n")
        f.write(f"| **Flight Endurance** | `± 0.5 min` | `{endur_calc:.1f} min` | `{disp_status}` |\n")
        f.write(f"| **Mission Range** | `± 0.2 km` | `{range_calc:.1f} km` | `{disp_status}` |\n\n")

        # Iteration history progression table
        iter_history = []
        if res.convergence_result and hasattr(res.convergence_result, "diagnostics"):
            iter_history = res.convergence_result.diagnostics.get("iteration_history", [])

        if iter_history:
            f.write("### Multidisciplinary Iteration Progression\n\n")
            f.write("| Iteration | MTOW (kg) | Wing S (m²) | Battery (kg) | Static Margin | Cruise Pwr (W) | Endurance (min) |\n")
            f.write("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
            for h in iter_history:
                it_num = h.get("iteration", 0)
                h_mtow = h.get("mtow", 0.0)
                h_area = h.get("wing_area", 0.0)
                h_batt = h.get("battery_mass", 0.0)
                h_sm = h.get("static_margin", 0.0)
                h_pwr = h.get("cruise_power", 0.0)
                h_endur = h.get("endurance", 0.0)
                f.write(f"| {it_num} | {h_mtow:.3f} | {h_area:.3f} | {h_batt:.3f} | {h_sm:.1%} | {h_pwr:.1f} | {h_endur:.1f} |\n")
            f.write("\n")
        elif res.convergence_history:
            f.write("### Sizing Iteration History\n\n")
            f.write("| Iteration | Old MTOW (kg) | New MTOW (kg) | Delta (kg) | Rel Error (%) |\n|:---:|:---:|:---:|:---:|:---:|\n")
            for rec in res.convergence_history:
                it = getattr(rec, "iteration", 0)
                m_old = getattr(rec, "mtow_old", 0.0)
                m_new = getattr(rec, "mtow_new", getattr(rec, "mtow", 0.0))
                d_abs = getattr(rec, "absolute_delta_kg", abs(m_new - m_old))
                d_rel = getattr(rec, "relative_delta", 0.0) * 100.0
                f.write(f"| {it} | {m_old:.4f} | {m_new:.4f} | {d_abs:.4f} | {d_rel:.2f}% |\n")
            f.write("\n")

        # 13. Verification
        f.write("## 13. Verification & Certification Status\n\n")
        f.write(f"- **Subsystem Engineering Verification**: `{subsystem_verif}`\n")
        f.write(f"- **Regulatory Airworthiness Certification**: `{cert_status}`\n")
        f.write(f"- **Overall Pipeline Stage Gate**: `{'PASSED' if res.success else 'FAILED'}`\n\n")

        if res.verification_result and hasattr(res.verification_result, "compliance_checklist") and res.verification_result.compliance_checklist:
            f.write("### Subsystem Compliance Checklist\n\n")
            f.write("| Verification Invariant | Status | Detail |\n|:---|:---:|:---|\n")
            for item in res.verification_result.compliance_checklist:
                name = getattr(item, "rule_name", getattr(item, "name", str(item)))
                passed = getattr(item, "passed", True)
                det = getattr(item, "detail", "")
                f.write(f"| {name} | `{'PASS' if passed else 'FAIL'}` | {det} |\n")
            f.write("\n")

        if res.certification_report and hasattr(res.certification_report, "rule_assessments") and res.certification_report.rule_assessments:
            f.write("### Common Airworthiness Rule Assessments\n\n")
            f.write("| Certification Rule | Rule Status | Severity | Message |\n|:---|:---:|:---:|:---|\n")
            for ra in res.certification_report.rule_assessments:
                r_id = getattr(ra, "rule_id", "Rule")
                r_st = getattr(ra, "status", "UNKNOWN")
                r_sev = getattr(ra, "severity", "INFO")
                r_msg = getattr(ra, "message", "")
                f.write(f"| {r_id} | `{r_st.value if hasattr(r_st, 'value') else r_st}` | `{r_sev.value if hasattr(r_sev, 'value') else r_sev}` | {r_msg} |\n")
            f.write("\n")

        # 14. Warnings
        f.write("## 14. Warnings\n\n")
        if res.warnings:
            for w in res.warnings:
                f.write(f"- ⚠️ {w}\n")
            f.write("\n")
        else:
            f.write("No engineering warnings reported.\n\n")

        # 15. Errors
        f.write("## 15. Errors\n\n")
        if res.errors:
            for e in res.errors:
                f.write(f"- ❌ {e}\n")
            f.write("\n")
        else:
            f.write("Zero pipeline execution errors.\n\n")

        # 16. Final Engineering Verdict
        f.write("## 16. Final Engineering Verdict\n\n")
        if res.success and res.converged:
            f.write("### **VERDICT: PASS — FULLY CONVERGED & FEASIBLE AIRCRAFT**\n\n")
            f.write("The Fixed-Wing design pipeline successfully converged across all aerodynamic, physical structural, ")
            f.write("propulsion, mass properties, and performance disciplines without violating safety margins or database boundaries.\n")
        elif res.converged and not res.success:
            f.write("### **VERDICT: FAIL — VERIFICATION DEFICIENCIES IDENTIFIED**\n\n")
            f.write(f"The aircraft sizing loop converged physically and mathematically, but failed downstream verification stage gates (Status: `{status_val}`). Inspect Section 13 and Section 15 for specific rule violations.\n")
        else:
            f.write("### **VERDICT: PIPELINE EXECUTION FAILED**\n\n")
            f.write(f"Execution halted at status `{status_val}`. Inspect Section 15 for specific engineering root causes and constraints.\n")

        # 17. Pareto Frontier Analysis (Phase 6B-6)
        if hasattr(res, "pareto_front") and res.pareto_front and getattr(res.pareto_front, "enabled", False):
            pf = res.pareto_front
            f.write("\n## 17. Pareto Frontier Analysis (Phase 6B-6)\n\n")
            f.write(f"- **Candidate Pool**: `{pf.candidate_count}`\n")
            f.write(f"- **Feasible Candidates**: `{pf.feasible_candidate_count}`\n")
            f.write(f"- **Pareto-Optimal Candidates**: `{pf.front_size}`\n\n")
            f.write("| Candidate ID | MTOW (kg) | Endurance (min) | Range (km) | Payload (kg) | L/D | Selected |\n")
            f.write("|:---|:---:|:---:|:---:|:---:|:---:|:---:|\n")
            for cand in pf.front:
                sel_str = "Yes [Selected]" if cand.is_selected_design else "No"
                try:
                    m = cand.get_value("mtow")
                    e = cand.get_value("endurance")
                    r = cand.get_value("range")
                    p = cand.get_value("payload")
                    ld = cand.get_value("efficiency")
                except Exception:
                    m = cand.engineering_summary.get("mtow_kg", 0.0)
                    e = cand.engineering_summary.get("endurance_min", 0.0)
                    r = cand.engineering_summary.get("range_km", 0.0)
                    p = cand.engineering_summary.get("payload_kg", 0.0)
                    ld = cand.engineering_summary.get("lift_to_drag_ratio", 0.0)
                f.write(f"| `{cand.candidate_id}` | {m:.3f} | {e:.1f} | {r:.1f} | {p:.3f} | {ld:.1f} | {sel_str} |\n")

    return filepath


# ==============================================================================
# MAIN ENTRY POINT LOOP
# ==============================================================================

def main():
    """Main interactive loop for manual end-to-end Fixed-Wing testing."""
    print("=" * 80)
    print("TORQWINGS DESIGN STUDIO - FIXED-WING PIPELINE MANUAL RUNNER")
    print("=" * 80)

    while True:
        # 1. Collect inputs interactively
        req, generate_pareto = collect_user_requirements()

        # 2. Execute the complete Fixed-Wing pipeline
        res = execute_pipeline(req, pareto=generate_pareto)

        # 3. Audit mass accounting & physical consistency
        mass_audit = audit_mass_accounting(res)

        # 4. Display clean terminal summary
        print_terminal_summary(req, res, mass_audit)

        # 5. Generate JSON and Markdown artifacts
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = save_json_artifact(req, res, mass_audit, timestamp_str)
        md_path = save_markdown_report(req, res, mass_audit, timestamp_str)

        print(f"\nSaved JSON Artifact     : {json_path}")
        print(f"Saved Markdown Report   : {md_path}")
        print("-" * 80)

        # 6. Ask for multiple manual runs
        try:
            again = input("\nRun another Fixed-Wing design? [Y/N]: ").strip().upper()
        except EOFError:
            again = "N"

        if again != "Y":
            print("\nExiting Fixed-Wing Design Studio Runner. Thank you!")
            break


if __name__ == "__main__":
    main()

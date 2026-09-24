"""
TEST-02 Validation Script
Executes all 6 configurations (C1-C6) and runs full engineering audits.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
import json
import math

from backend.design.common.requirements.requirement_model import RequirementModel
from backend.design.common.requirements.mission_type import MissionType
from backend.design.common.requirements.takeoff_type import TakeoffType
from backend.design.common.requirements.landing_type import LandingType
from backend.design.common.requirements.operating_environment import OperatingEnvironment

from backend.design.fixed_wing.pipeline.fixed_wing_pipeline import FixedWingDesignPipeline
from backend.design.fixed_wing.construction.construction_types import (
    ConstructionConfigurationId,
    ConstructionCatalog,
)
from backend.design.fixed_wing.construction.construction_engine import (
    ConstructionConfigurationSelectionEngine,
)
from backend.design.fixed_wing.mass_properties.structural_weight_engine import (
    StructuralWeightEngine,
)
from backend.design.fixed_wing.materials.material_database import PhysicalMaterialDatabase
from backend.design.fixed_wing.materials.component_database import StructuralComponentDatabase


class ControlledRequirementModel(RequirementModel):
    preferred_construction_configuration: any = None


def run_test02():
    print("================================================================================")
    print("STARTING TEST-02: FIXED-WING CONSTRUCTION + WEIGHT ENGINE ENGINEERING VALIDATION")
    print("================================================================================")

    # Base mission parameters
    base_kwargs = dict(
        mission_type=MissionType.SURVEY,
        payload_weight_kg=0.50,
        target_flight_time_min=30.0,
        target_range_km=30.0,
        cruise_speed_kmh=80.0,
        takeoff_type=TakeoffType.RUNWAY,
        landing_type=LandingType.RUNWAY,
        environment=OperatingEnvironment.RURAL,
    )

    # 1. Engineering Advisor Run
    print("\n--- 1. Running Engineering Advisor Mode ---")
    req_advisor = RequirementModel(**base_kwargs)
    pipeline_advisor = FixedWingDesignPipeline(raise_on_failure=False)
    res_advisor = pipeline_advisor.execute(req_advisor)
    print(f"Advisor Run: success={res_advisor.success}, status={res_advisor.status}")

    advisor_engine = ConstructionConfigurationSelectionEngine()
    advisor_selection = advisor_engine.select_configuration(
        mission_requirements=req_advisor,
        wing_geometry=res_advisor.wing_result.wing_geometry if res_advisor.wing_result else None,
        fuselage_geometry=res_advisor.fuselage_result.fuselage_geometry if res_advisor.fuselage_result else None,
        manual_config_id=None
    )
    print(f"Advisor Selected: {advisor_selection.selected_configuration.configuration_id.value}")
    print(f"Advisor Rationale: {advisor_selection.engineering_rationale}")

    # 2. Manual Mode Runs for C1 through C6
    configs = [
        ("C1", ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE),
        ("C2", ConstructionConfigurationId.C2_BALSA_SKELETON_COMPOSITE),
        ("C3", ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM),
        ("C4", ConstructionConfigurationId.C4_FOAM_DEPRON_FILM),
        ("C5", ConstructionConfigurationId.C5_FOLDED_FOAM_MONOCOQUE),
        ("C6", ConstructionConfigurationId.C6_WOOD_SKELETON_FILM),
    ]

    manual_results = {}
    for code, config_id in configs:
        print(f"\n--- Running Manual Mode: {code} ({config_id.value}) ---")
        req_manual = ControlledRequirementModel(**base_kwargs)
        req_manual.preferred_construction_configuration = config_id

        pipeline = FixedWingDesignPipeline(raise_on_failure=False)
        res = pipeline.execute(req_manual)
        print(f"  {code} Result: success={res.success}, status={res.status}, iterations={res.iterations}")

        # Extract specifications and breakdown
        struct_bd = getattr(res.final_specification, "_structural_breakdown", None)
        if not struct_bd and res.mass_properties_result and hasattr(res.mass_properties_result, "metadata"):
            struct_bd = res.mass_properties_result.metadata.get("structural_breakdown")

        manual_results[code] = {
            "code": code,
            "config_id": config_id.value,
            "pipeline_result": res,
            "structural_breakdown": struct_bd,
        }

    # 3. Sensitivity Testing
    print("\n--- 3. Running Material Sensitivity Tests ---")
    struct_eng = StructuralWeightEngine()
    # Baseline geometry from C1
    ref_res = manual_results["C1"]["pipeline_result"]
    wing_g = ref_res.wing_result.wing_geometry
    fuse_g = ref_res.fuselage_result.fuselage_geometry
    tail_r = ref_res.tail_result

    # S1: XPS vs Depron in C1
    c1_spec = ConstructionCatalog.get(ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE)
    bd_c1_xps = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c1_spec, landing_gear_config="Tricycle")
    
    c1_spec_depron = ConstructionCatalog.get(ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE)
    c1_spec_depron.default_core_material = "FOAM_DEPRON"
    bd_c1_depron = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c1_spec_depron, landing_gear_config="Tricycle")

    # S2: Balsa Standard vs Balsa Light in C2
    c2_spec = ConstructionCatalog.get(ConstructionConfigurationId.C2_BALSA_SKELETON_COMPOSITE)
    bd_c2_std = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c2_spec, landing_gear_config="Tricycle")

    c2_spec_light = ConstructionCatalog.get(ConstructionConfigurationId.C2_BALSA_SKELETON_COMPOSITE)
    c2_spec_light.default_rib_material = "WOOD_BALSA_LIGHT"
    c2_spec_light.default_sheeting_material = "WOOD_BALSA_LIGHT"
    bd_c2_light = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c2_spec_light, landing_gear_config="Tricycle")

    # S3: Carbon fabric 120 vs 200 g/m2 in C1
    c1_spec_c120 = ConstructionCatalog.get(ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE)
    c1_spec_c120.default_skin_material = "FABRIC_CARBON_120"
    bd_c1_c120 = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c1_spec_c120, landing_gear_config="Tricycle")

    c1_spec_c200 = ConstructionCatalog.get(ConstructionConfigurationId.C1_FOAM_CORE_COMPOSITE)
    c1_spec_c200.default_skin_material = "FABRIC_CARBON_200"
    bd_c1_c200 = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c1_spec_c200, landing_gear_config="Tricycle")

    # S4: Carbon tube 8mm vs 12mm spar in C3
    c3_spec_8mm = ConstructionCatalog.get(ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM)
    c3_spec_8mm.default_spar_type = "CARBON_TUBE_8MM"
    bd_c3_8mm = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c3_spec_8mm, landing_gear_config="Tricycle")

    c3_spec_12mm = ConstructionCatalog.get(ConstructionConfigurationId.C3_BALSA_CARBON_SKELETON_FILM)
    c3_spec_12mm.default_spar_type = "CARBON_TUBE_12MM"
    bd_c3_12mm = struct_eng.calculate_structural_mass(wing_geometry=wing_g, fuselage_geometry=fuse_g, tail_result=tail_r, construction_config=c3_spec_12mm, landing_gear_config="Tricycle")

    sensitivity_results = {
        "xps_vs_depron_core": (bd_c1_xps.wing_structural_mass_kg, bd_c1_depron.wing_structural_mass_kg),
        "balsa_std_vs_light_ribs_sheeting": (bd_c2_std.wing_structural_mass_kg, bd_c2_light.wing_structural_mass_kg),
        "carbon_120_vs_200_skin": (bd_c1_c120.wing_structural_mass_kg, bd_c1_c200.wing_structural_mass_kg),
        "carbon_tube_8mm_vs_12mm_spar": (bd_c3_8mm.wing_structural_mass_kg, bd_c3_12mm.wing_structural_mass_kg),
    }

    # Save summary json
    output_data = {
        "advisor_selection": {
            "selected": advisor_selection.selected_configuration.configuration_id.value,
            "scores": advisor_selection.scores,
            "ranking": [(cfg.configuration_id.value, score, r) for cfg, score, r in advisor_selection.ranked_configurations],
            "rejected": [(cfg.configuration_id.value, reason) for cfg, reason in advisor_selection.rejected_configurations],
            "rationale": advisor_selection.engineering_rationale,
        },
        "manual_configurations": {},
        "sensitivities": sensitivity_results
    }

    for code, data in manual_results.items():
        res = data["pipeline_result"]
        bd = data["structural_breakdown"]
        final_spec = res.final_specification

        cg_pos = res.mass_properties_result.center_of_gravity if res.mass_properties_result else (0,0,0)
        sm = res.mass_properties_result.static_margin if res.mass_properties_result else 0
        perf = res.performance_result
        prop = res.propulsion_result
        wb = res.mass_properties_result.weight_breakdown if res.mass_properties_result else None

        output_data["manual_configurations"][code] = {
            "success": res.success,
            "status": str(res.status),
            "iterations": res.iterations,
            "mtow_kg": round(wb.useful_load_kg + wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg, 4) if wb else None,
            "empty_weight_kg": round(wb.structural_weight_kg + wb.propulsion_weight_kg + wb.avionics_weight_kg, 4) if wb else None,
            "structural_mass_kg": round(wb.structural_weight_kg, 4) if wb else None,
            "propulsion_weight_kg": round(wb.propulsion_weight_kg, 4) if wb else None,
            "avionics_weight_kg": round(wb.avionics_weight_kg, 4) if wb else None,
            "payload_weight_kg": round(wb.payload_weight_kg, 4) if wb else None,
            "battery_weight_kg": round(wb.battery_fuel_weight_kg, 4) if wb else None,
            "useful_load_kg": round(wb.useful_load_kg, 4) if wb else None,
            "cg": [round(c, 4) for c in cg_pos],
            "static_margin": round(sm, 4),
            "wing": {
                "span_m": round(res.wing_result.wing_geometry.span_m, 4),
                "area_m2": round(res.wing_result.wing_geometry.area_m2, 4),
                "aspect_ratio": round(res.wing_result.wing_geometry.aspect_ratio, 2),
                "root_chord_m": round(res.wing_result.wing_geometry.root_chord_m, 4),
                "tip_chord_m": round(res.wing_result.wing_geometry.tip_chord_m, 4),
                "mac_m": round(res.wing_result.wing_geometry.mean_aerodynamic_chord_m, 4),
            } if res.wing_result else {},
            "fuselage": {
                "length_m": round(res.fuselage_result.fuselage_geometry.length_m, 4),
                "width_m": round(res.fuselage_result.fuselage_geometry.width_m, 4),
                "height_m": round(res.fuselage_result.fuselage_geometry.height_m, 4),
            } if res.fuselage_result else {},
            "tail": {
                "horizontal_area_m2": round(res.tail_result.horizontal_tail.area_m2, 4),
                "vertical_area_m2": round(res.tail_result.vertical_tail.area_m2, 4),
            } if res.tail_result else {},
            "performance": {
                "stall_speed_kmh": round(perf.stall_analysis.stall_speed_clean_kmh, 2) if perf and hasattr(perf, "stall_analysis") else None,
                "cruise_speed_kmh": round(perf.cruise_analysis.cruise_speed_kmh, 2) if perf and hasattr(perf, "cruise_analysis") else None,
                "rate_of_climb_m_s": round(perf.climb_analysis.rate_of_climb_m_s, 2) if perf and hasattr(perf, "climb_analysis") else None,
                "range_km": round(perf.range_analysis.maximum_range_km, 2) if perf and hasattr(perf, "range_analysis") else None,
                "endurance_min": round(perf.endurance_analysis.maximum_endurance_min, 2) if perf and hasattr(perf, "endurance_analysis") else None,
                "takeoff_distance_m": round(perf.takeoff_analysis.takeoff_distance_m, 2) if perf and hasattr(perf, "takeoff_analysis") else None,
                "landing_distance_m": round(perf.landing_analysis.landing_distance_m, 2) if perf and hasattr(perf, "landing_analysis") else None,
            },
            "propulsion": {
                "motor": prop.selected_motor_or_engine if prop else None,
                "propeller": prop.selected_propeller if prop else None,
                "thrust_to_weight": round(prop.thrust_analysis.thrust_to_weight_ratio, 2) if prop and hasattr(prop, "thrust_analysis") else None,
                "cruise_power_w": round(prop.power_analysis.required_cruise_power_w, 1) if prop and hasattr(prop, "power_analysis") else None,
                "climb_power_w": round(prop.power_analysis.required_climb_power_w, 1) if prop and hasattr(prop, "power_analysis") else None,
                "max_power_w": round(prop.power_analysis.maximum_power_w, 1) if prop and hasattr(prop, "power_analysis") else None,
            },
            "breakdown": bd if isinstance(bd, dict) else (bd.to_dict() if hasattr(bd, "to_dict") else str(bd)),
            "convergence_history": [r.to_dict() if hasattr(r, "to_dict") else str(r) for r in res.convergence_history],
        }

    out_path = "reports/fixed_wing_TEST02_result.json"
    os.makedirs("reports", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nAll results saved to {out_path}")


if __name__ == "__main__":
    run_test02()
